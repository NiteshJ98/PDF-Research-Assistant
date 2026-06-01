# config.py
import os
from dotenv import load_dotenv
load_dotenv()

# LLM
LLM_API_KEY   = os.getenv("GROQ_API_KEY")          # or OPENAI_API_KEY
LLM_BASE_URL  = "https://api.groq.com/openai/v1"   # remove for OpenAI
LLM_MODEL     = "llama-3.1-8b-instant"             # or "gpt-4o-mini"
TEMPERATURE   = 0

# Embedding
EMBED_MODEL   = "BAAI/bge-small-en-v1.5"

# ChromaDB
DB_PATH       = "./chroma_db"
COLLECTION    = "pdf_research"

# Chunking
CHUNK_SIZE    = 500
CHUNK_OVERLAP = 50
BATCH_SIZE    = 64

# Retrieval
TOP_K         = 3

# Upload
UPLOAD_DIR    = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)