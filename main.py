from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from PyPDF2 import PdfReader
import chardet
import io
import logging
from langchain_community.chat_models import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from app.tools.web_search import brave_search, BraveSearchError
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from app.rag_chain import RAGChain
from app.config import get_settings

app = FastAPI(title="RAG Chatbot API")
settings = get_settings()

# Initialize RAG chain
rag_chain = RAGChain()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str 

class ChatResponse(BaseModel):
    response: str
    url: Optional[str] = None
    document_name: Optional[str] = None

class DocumentResponse(BaseModel):
    message: str
    document_count: int

class EmbeddingInfo(BaseModel):
    total_documents: int
    documents: List[Dict[str, Any]]
    collection_info: Dict[str, Any]

class DeleteResponse(BaseModel):
    message: str
    deleted_count: int

class WebSearchRequest(BaseModel):
    query: str
    num_results: Optional[int] = 3

class WebSearchResult(BaseModel):
    title: str
    url: str
    snippet: Optional[str] = None

class WebSearchResponse(BaseModel):
    results: List[WebSearchResult]

# In-memory session store: session_id -> list of messages
session_store: Dict[str, List[Dict[str, str]]] = {}

SESSIONS_DIR = "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

# Helper functions for session persistence
def save_session_to_disk(session_id: str, history: List[Dict[str, str]]):
    path = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_session_from_disk(session_id: str) -> List[Dict[str, str]]:
    path = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def read_file_content(file_path: str) -> str:
    """Read file content with proper encoding handling."""
    # Read the file in binary mode
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        
        # Try to detect the encoding
        result = chardet.detect(raw_data)
        detected_encoding = result['encoding']
        
        # If no encoding is detected, try common encodings
        if not detected_encoding:
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'windows-1252']:
                try:
                    return raw_data.decode(encoding)
                except UnicodeDecodeError:
                    continue
            raise ValueError("Could not decode the file with any supported encoding")
        
        # Try the detected encoding
        try:
            return raw_data.decode(detected_encoding)
        except UnicodeDecodeError:
            # If detected encoding fails, try common encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'windows-1252']:
                try:
                    return raw_data.decode(encoding)
                except UnicodeDecodeError:
                    continue
            raise ValueError("Could not decode the file with any supported encoding")

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF content."""
    try:
        # Create a BytesIO object from the file content
        pdf_file = io.BytesIO(file_content)
        
        # Create PDF reader object
        pdf_reader = PdfReader(pdf_file)
        
        # Extract text from each page
        text_content = []
        for page in pdf_reader.pages:
            try:
                text = page.extract_text()
                if text:  # Only add non-empty text
                    text_content.append(text)
            except Exception as e:
                logger.error(f"Error extracting text from page: {str(e)}")
                continue
        
        if not text_content:
            raise ValueError("No text could be extracted from the PDF")
            
        return "\n".join(text_content)
    except Exception as e:
        raise ValueError(f"Error processing PDF: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint that processes user messages and returns AI responses."""
    try:
        # Retrieve or create session history (load from disk if not in memory)
        history = session_store.get(request.session_id)
        if history is None:
            history = load_session_from_disk(request.session_id)
            session_store[request.session_id] = history
        # Append user message to history
        history.append({"role": "user", "content": request.message})
        # Optionally, pass history to RAGChain (if supported)
        # For now, just use the latest message as before
        response = rag_chain.query(request.message)
        url = None
        document_name = None
        
        import re
        url_match = re.search(r'(https?://\S+)', response)
        if url_match:
            url = url_match.group(1)
            
        if "Document:" in response:
            document_name = response.split("Document:")[1].strip()

        history.append({"role": "assistant", "content": response, "url": url, "document_name": document_name})
        # Save updated session to disk
        save_session_to_disk(request.session_id, history)
        return ChatResponse(response=response, url=url, document_name=document_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document."""
    try:
        # Read the file content
        content = await file.read()
        
        # Process the document based on file type
        if file.filename.lower().endswith('.pdf'):
            # Handle PDF files
            text_content = extract_text_from_pdf(content)
        else:
            # Handle text files
            # Save temporarily to process with encoding detection
            os.makedirs("uploads", exist_ok=True)
            temp_path = f"uploads/{file.filename}"
            try:
                with open(temp_path, "wb") as f:
                    f.write(content)
                text_content = read_file_content(temp_path)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        logger.debug(f"Extracted text type: {type(text_content)}")
        logger.debug(f"Extracted text length: {len(text_content)}")
        
        # Add the content to the RAG chain with metadata
        metadata = {
            "filename": file.filename,
            "content_type": file.content_type
        }
        
        # Ensure text_content is a string
        if not isinstance(text_content, str):
            raise ValueError(f"Expected string content, got {type(text_content)}")
            
        rag_chain.add_documents(text_content, metadata)
        
        return DocumentResponse(
            message="Document processed successfully",
            document_count=1
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/embeddings", response_model=EmbeddingInfo)
async def get_embeddings():
    """Get information about stored embeddings and documents."""
    try:
        # Get the collection from the vector store
        collection = rag_chain.vector_store.vector_store._collection
        
        # Get all documents from the collection
        results = collection.get()
        
        # Prepare document information
        documents = []
        for i, (text, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
            documents.append({
                "id": results['ids'][i],
                "text": text[:200] + "..." if len(text) > 200 else text,  # Truncate long texts
                "metadata": metadata,
                "embedding_dimension": len(results['embeddings'][i]) if results['embeddings'] else None
            })
        
        # Get collection information
        collection_info = {
            "name": collection.name,
            "count": collection.count(),
            "embedding_dimension": len(results['embeddings'][0]) if results['embeddings'] else None
        }
        
        return EmbeddingInfo(
            total_documents=len(documents),
            documents=documents,
            collection_info=collection_info
        )
    except Exception as e:
        logger.error(f"Error retrieving embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/embeddings", response_model=DeleteResponse)
async def delete_embeddings(
    document_ids: Optional[List[str]] = Query(None, description="List of document IDs to delete. If not provided, all documents will be deleted.")
):
    """Delete embeddings from the vector store."""
    try:
        collection = rag_chain.vector_store.vector_store._collection
        
        if document_ids:
            # Delete specific documents
            collection.delete(ids=document_ids)
            deleted_count = len(document_ids)
            message = f"Successfully deleted {deleted_count} documents"
        else:
            # Delete all documents
            collection.delete(where={})
            deleted_count = collection.count()
            message = "Successfully cleared all documents from the vector store"
        
        # Persist changes
        rag_chain.vector_store.vector_store.persist()
        
        return DeleteResponse(
            message=message,
            deleted_count=deleted_count
        )
    except Exception as e:
        logger.error(f"Error deleting embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/web_search", response_model=WebSearchResponse)
async def web_search_endpoint(request: WebSearchRequest):
    """Perform a web search using Brave Search API."""
    try:
        results = brave_search(request.query, request.num_results)
        return WebSearchResponse(results=[WebSearchResult(**r) for r in results])
    except BraveSearchError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}") 