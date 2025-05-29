# PersonaForge 🚀

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![Gradio](https://img.shields.io/badge/Gradio-5.0+-orange?logo=gradio)](https://gradio.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ManiaSacha/PersonaForge)

---

> **PersonaForge** is a modular platform for building, managing, and running AI personas with Retrieval-Augmented Generation (RAG), LLMs, and multi-persona orchestration. Perfect for research, prototyping, and production AI applications.

---

## ✨ Features

- ⚡ **FastAPI Backend** — blazing fast, modern Python API
- 🖥️ **Gradio UI** — clean, interactive frontend for creating and interacting with personas
- 🧠 **Persona Profiles** — define, save, and load persona JSON schemas
- 📝 **Prompt Engine** — generate persona-customized prompts for LLMs
- 💾 **Disk Persistence** — all personas are saved as JSON for easy sharing
- 🔌 **RAG & Vector DB Ready** — upload and embed documents for context-aware responses
- 🤖 **AI-to-AI Chat** — let two personas have conversations with each other
- 📊 **Persona Versioning** — track changes to personas with automatic backups
- 📜 **Memory Logs** — save all interactions with timestamps for analysis
- 📦 **Export Feature** — download persona configs and chat logs as JSON
- 🔄 **Multiple LLM Support** — use llava, gemma3, llama3.2, gemma:2b, tinyllama, and more
- 🔒 **Extensible** — add new persona types, prompt templates, and LLMs easily

## 📂 Project Structure

```
PersonaForge/
├── backend/
│   ├── main.py               # FastAPI entry point
│   ├── persona_profiles/     # Persona JSON definitions
│   ├── logs/                # Chat history logs (JSONL)
│   ├── prompt_engine.py      # Prompt generation utility
│   └── persona_storage.py    # Persona versioning and logs
├── rag_db/                   # Vector database for RAG
├── ui.py                     # Gradio UI frontend
├── requirements.txt
├── .env
└── README.md
```

## 🚀 Quickstart

1. **Clone the repo:**
   ```bash
   git clone https://github.com/ManiaSacha/PersonaForge.git
   cd PersonaForge
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the FastAPI backend server:**
   ```bash
   uvicorn backend.main:app --reload --port 8100
   ```
5. **Run the Gradio UI frontend** (in a separate terminal):
   ```bash
   python ui.py
   ```
6. **Access the UI:**
   - Visit [http://127.0.0.1:7860](http://127.0.0.1:7860) for the Gradio UI
   - Visit [http://localhost:8100/docs](http://localhost:8100/docs) for the API docs

## 🛠️ Usage

### Using the Gradio UI

- **Create a Persona:**
  - Go to the "Create Persona" tab
  - Fill in the name, tone, domain, goals, and response style
  - Click "Create Persona"

- **Ask a Persona:**
  - Go to the "Ask Persona" tab
  - Enter the persona name and your question
  - Select a model (llava, gemma3, llama3.2, gemma:2b, tinyllama)
  - Click "Ask" to get a response

- **Upload Knowledge:**
  - Go to the "Upload Knowledge" tab
  - Enter the persona name and upload PDF, TXT, or MD files
  - Click "Upload & Embed" to add knowledge to the persona

- **AI-to-AI Chat:**
  - Go to the "AI-to-AI Chat" tab
  - Enter two persona names, an opening message, and select rounds
  - Click "Start Conversation" to watch them talk to each other

- **Export Persona:**
  - Go to the "Export Persona" tab
  - Enter the persona name and click "Download Export"
  - Get a JSON file with the persona config and chat history

### Using the API

- **Create a Persona:**
  - Use `POST /persona/` to save a new persona
- **Ask a Persona:**
  - Use `POST /ask_persona/` with name, question, and model
- **Upload Documents:**
  - Use `POST /upload_doc/` to add knowledge to a persona
- **AI-to-AI Chat:**
  - Use `POST /persona_chat/` to start a conversation between personas
- **Export Persona Data:**
  - Use `GET /export_persona/{name}` to download persona data

## 🌟 Example Persona JSON
```json
{
  "name": "LegalAdvisorGPT",
  "tone": "Formal",
  "domain": "Corporate Law",
  "goals": [
    "Review contracts",
    "Identify legal risks",
    "Summarize compliance requirements"
  ],
  "response_style": "Legal, structured, bullet-pointed"
}
```

## 🤝 Contributing

Contributions are welcome! Please open issues and pull requests for improvements or new features.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

> Made with ❤️ by [ManiaSacha](https://github.com/ManiaSacha)
