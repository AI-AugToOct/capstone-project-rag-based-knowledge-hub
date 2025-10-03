import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
import docx
import pdfplumber

def load_documents_from_store(document_store_path):
    documents = []
    for filename in os.listdir(document_store_path):
        filepath = os.path.join(document_store_path, filename)
        ext = os.path.splitext(filename)[1].lower()

        text = ""
        if ext == ".txt":
            with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
                text = file.read()
        elif ext == ".pdf":
            try:
                with pdfplumber.open(filepath) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
            except Exception as e:
                print(f"⚠️ Error reading PDF {filename}: {e}")
        elif ext == ".docx":
            try:
                doc = docx.Document(filepath)
                text = "\n".join([p.text for p in doc.paragraphs])
            except Exception as e:
                print(f"⚠️ Error reading DOCX {filename}: {e}")
        else:
            print(f"⏭ Skipping unsupported file type: {filename}")
            continue

        if text.strip():
            documents.append({"filename": filename, "content": text})

    return documents

def split_documents(documents, chunk_size=500, chunk_overlap=50):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = []
    for doc in documents:
        for chunk in text_splitter.split_text(doc["content"]):
            chunks.append({"filename": doc["filename"], "content": chunk})
    return chunks
