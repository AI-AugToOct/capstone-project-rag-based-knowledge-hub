from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import upload, docs
from app.db.client import init_db_pool, close_db_pool


app = FastAPI(title="RAG Knowledge Hub API", version="1.0.0")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def on_startup():
    await init_db_pool()


@app.on_event("shutdown")
async def on_shutdown():
    await close_db_pool()
    
    
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(docs.router, prefix="/api", tags=["Docs"])



