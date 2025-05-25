# PersonaForge

A platform for building, managing, and running AI personas with RAG and LLM integration.

## Folder Structure

```
PersonaForge/
├── backend/
│   ├── main.py               ← FastAPI entry point
│   └── persona_profiles/     ← Persona definitions
├── data/                     ← Documents to embed for RAG
├── models/                   ← Any fine-tuned models or checkpoints
├── README.md
├── requirements.txt
├── .env
```

## Quickstart

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the FastAPI server:
   ```bash
   uvicorn backend.main:app --reload
   ```
3. Visit http://localhost:8000/docs to test the API.
