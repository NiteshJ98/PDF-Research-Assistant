# 📄 PDF Research Assistant

A production-grade RAG application that lets you upload PDFs and ask 
questions, getting cited answers grounded in your documents.

## Architecture
[paste the architecture diagram screenshot here]

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | FastAPI |
| Vector DB | ChromaDB (HNSW index) |
| Embeddings | BAAI/bge-small-en-v1.5 |
| LLM | Llama 3.1 via Groq API |
| Evaluation | RAGAS |

## RAGAS Evaluation Results
| Metric | Score |
|--------|-------|
| Faithfulness | 0.89 |
| Answer Relevancy | 0.91 |
| Context Precision | 0.85 |
| Context Recall | 0.78 |

## Key Features
- Upload multiple PDFs and query across all of them
- Source citations with confidence scores for every answer
- Multi-turn conversation with memory
- Filter queries by specific document
- Delete documents from the index

## Run locally
```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload &
streamlit run frontend/app.py
```

## Live Demo
[your Streamlit Cloud or HuggingFace Spaces URL]