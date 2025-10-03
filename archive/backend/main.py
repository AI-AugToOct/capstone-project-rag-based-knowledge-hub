from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from backend.rag_workflow import RAGWorkflow
from backend.notion_api import fetch_tasks  # Import the Notion API logic
import os

# Initialize FastAPI app and RAGWorkflow
app = FastAPI()
rag = RAGWorkflow()

UPLOAD_DIR = "backend/document_store/"  # Directory where uploaded files are stored

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# -------------------------------
# Notion Tasks
# -------------------------------
@app.get("/notion-tasks")
async def get_notion_tasks():
    try:
        tasks = fetch_tasks()
        return tasks
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# Startup event
# -------------------------------
@app.on_event("startup")
async def setup_knowledge_base():
    print("Setting up knowledge base...")
    rag.setup_knowledge_base()

# -------------------------------
# Query models
# -------------------------------
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    answer: str

# -------------------------------
# Query endpoint
# -------------------------------
@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    user_query = request.query
    answer = rag.answer_query(user_query)
    return {"query": user_query, "answer": answer}

# -------------------------------
# Upload documents
# -------------------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        return {"filename": file.filename, "status": "uploaded"}
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# List documents
# -------------------------------
@app.get("/documents")
async def list_documents():
    try:
        files = os.listdir(UPLOAD_DIR)
        return files
    except Exception as e:
        return {"error": str(e)}
