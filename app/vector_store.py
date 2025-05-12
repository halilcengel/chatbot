from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from typing import List, Optional, Union
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from app.config import get_settings

settings = get_settings()

class VectorStore:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Ensure the persist directory exists
        os.makedirs(settings.chroma_persist_directory, exist_ok=True)
        
        self.vector_store = Chroma(
            persist_directory=settings.chroma_persist_directory,
            embedding_function=self.embeddings
        )

    def add_documents(self, text: Union[str, List[str]], metadata: Optional[Union[dict, List[dict]]] = None):
        """Add documents to the vector store."""
        logger.debug(f"Input text type: {type(text)}")
        logger.debug(f"Input metadata type: {type(metadata)}")
        
        # Convert single text to list
        if isinstance(text, str):
            texts = [text]
        else:
            texts = text
            
        logger.debug(f"Number of texts to process: {len(texts)}")
        
        # Split texts into chunks
        chunks = []
        for text in texts:
            if not isinstance(text, str):
                raise ValueError(f"Expected string, got {type(text)}")
            chunks.extend(self.text_splitter.split_text(text))
        
        logger.debug(f"Number of chunks after splitting: {len(chunks)}")
        
        # Prepare metadata
        if metadata is None:
            metadatas = [{}] * len(chunks)
        elif isinstance(metadata, dict):
            metadatas = [metadata] * len(chunks)
        else:
            if len(metadata) == 1:
                metadatas = [metadata[0]] * len(chunks)
            else:
                metadatas = metadata
                
        logger.debug(f"Number of metadata entries: {len(metadatas)}")
        
        # Add to vector store
        self.vector_store.add_texts(chunks, metadatas=metadatas)
        self.vector_store.persist()
        
        logger.debug("Documents added successfully")

    def similarity_search(self, query: str, k: int = 4):
        """Search for similar documents."""
        return self.vector_store.similarity_search(query, k=k)

    def load_documents_from_directory(self, directory_path: str):
        """Load documents from a directory and add them to the vector store."""
        loader = DirectoryLoader(directory_path, glob="**/*.txt", loader_cls=TextLoader)
        documents = loader.load()
        texts = self.text_splitter.split_documents(documents)
        self.vector_store.add_documents(texts)
        self.vector_store.persist() 