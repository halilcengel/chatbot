from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import get_settings
from app.vector_store import VectorStore
from app.tools.web_search import get_brave_search_tool
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
import logging
from typing import Optional, List
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

settings = get_settings()

def get_retriever_tool(retriever):
    def retrieve_with_metadata(q):
        docs = retriever.get_relevant_documents(q)
        results = []
        for doc in docs:
            # doc.metadata might include 'filename'
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        return results
    return Tool(
        name="Document Retriever",
        func=retrieve_with_metadata,
        description="Useful for answering questions based on uploaded documents and internal knowledge. Input should be a question."
    )

class ChatResponse(BaseModel):
    response: str
    document_names: Optional[List[str]] = None

class RAGChain:
    def __init__(self):
        self.vector_store = VectorStore()
        self.llm = ChatOpenAI(
            model_name=settings.model_name,
            temperature=0.7,
            openai_api_key=settings.openai_api_key
        )
        self.retriever = self.vector_store.vector_store.as_retriever()
        self.tools = [
            get_retriever_tool(self.retriever),
            get_brave_search_tool()
        ]
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False
        )

    def query(self, question: str) -> str:
        """Query the agent with a question. The agent decides which tool(s) to use."""
        result = self.agent.run(question)
        return result

    def query_with_metadata(self, question: str):
        docs = self.retriever.get_relevant_documents(question)
        context = "\n".join([doc.page_content for doc in docs])
        prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        answer = self.llm(prompt)
        doc_names = [doc.metadata.get("filename") for doc in docs if "filename" in doc.metadata]
        return {"response": answer, "document_names": doc_names}

    def add_documents(self, text: str, metadata: dict = None):
        """Add a document to the vector store."""
        logger.debug(f"Adding document with metadata: {metadata}")
        logger.debug(f"Text type: {type(text)}")
        logger.debug(f"Text length: {len(text) if isinstance(text, str) else 'N/A'}")
        # Ensure text is a string
        if not isinstance(text, str):
            raise ValueError(f"Expected string, got {type(text)}")
        # Add to vector store
        self.vector_store.add_documents(text, metadata) 