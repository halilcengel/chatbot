# Agentic RAG Chatbot

A powerful Retrieval-Augmented Generation (RAG) chatbot service built with FastAPI and LangChain.

## Features

- Document ingestion and processing
- Vector-based semantic search
- Conversational memory
- RESTful API endpoints
- Document upload support
- Health check endpoint

## Prerequisites

- Python 3.12 or higher
- OpenAI API key

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd chatbot-v2
```

2. Create a virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

4. Create a `.env` file in the root directory with the following content:
```
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small
CHROMA_PERSIST_DIRECTORY=./data/chroma
```

## Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `POST /chat`: Send a message to the chatbot
  ```json
  {
    "message": "Your question here"
  }
  ```

- `POST /upload`: Upload a document for processing
  - Use multipart/form-data with a file field named "file"

- `GET /health`: Check the API health status

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
chatbot-v2/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── rag_chain.py
│   └── vector_store.py
├── data/
│   └── chroma/
├── uploads/
├── .env
├── pyproject.toml
└── README.md
```

## Contributing

Feel free to submit issues and enhancement requests! 

## Additional Changes

The following code block was added to the main.py file:

```
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def serve_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
``` 