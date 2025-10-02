import os

# Notion API Configuration
NOTION_API_KEY      = os.getenv("NOTION_API_KEY", "XXXXXXXXXXXXXXXXX")  
NOTION_DATABASE_ID  = os.getenv("NOTION_DATABASE_ID", "XXXXXXXXXXXXXXXXX")


# Google Gemini API Configuration
GOOGLE_API_KEY  = os.getenv("GOOGLE_API_KEY", "XXXXXXXXXXXXXXXXX") 

# Embeddings Configuration
EMBEDDINGS_ON = True
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # Model for generating embeddings

# Vector Database Configuration
VECTOR_DB_PATH = "backend/vector_store/faiss_index"

# filepath: [config.py](http://_vscodecontentref_/3)
DOCUMENT_STORE_PATH = "backend/document_store/"