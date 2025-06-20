<div align="center">
  <img src="logo/personaforgelogo.png" alt="PersonaForge Logo" width="300">
</div>

# 🚀 PersonaForge

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Gradio](https://img.shields.io/badge/UI-Gradio-orange?logo=gradio)](https://gradio.app/)
[![FastAPI Users](https://img.shields.io/badge/Auth-FastAPI%20Users-blue?logo=fastapi)](https://fastapi-users.github.io/fastapi-users/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ManiaSacha/PersonaForge)

---

> **PersonaForge** is a modular platform for building, managing, and running AI personas with Retrieval-Augmented Generation (RAG), LLMs, and multi-persona orchestration. Perfect for research, prototyping, and production AI applications. Now with multi-user support and secure authentication!

---

## 📸 Preview

<div align="center">
  <img src="logo/PersonaForge.gif" alt="PersonaForge Demo" width="700">
</div>

---

## ✨ Features

- ⚡ **FastAPI Backend** — blazing fast, modern Python API
- 🖥️ **Gradio UI** — clean, interactive frontend for creating and interacting with personas
- 🔐 **User Authentication** — secure multi-user support with JWT tokens via FastAPI Users
- 🔒 **Access Control** — user-specific persona isolation and data protection
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

---

## 🛠️ Technologies Used

- **Python 3.10+** — core programming language
- **FastAPI** — modern, async web framework for the backend API
- **Uvicorn** — lightning-fast ASGI server for FastAPI
- **Gradio** — interactive web UI for persona management and chat
- **FastAPI Users** — authentication and user management (JWT, registration, login)
- **SQLAlchemy** — ORM for database models (with async and sync support)
- **SQLite** — lightweight relational database (with aiosqlite for async)
- **LangChain** — orchestration and chaining of LLMs and RAG workflows
- **OpenAI** — LLM API integration (supports multiple models)
- **Chroma** — vector store for document embeddings (RAG)
- **FAISS** — vector similarity search for embeddings
- **HuggingFace Embeddings** — for local embedding generation
- **Pydantic** — data validation and settings management
- **email-validator** — email validation for user registration
- **python-multipart** — file upload support in FastAPI
- **python-dotenv** — environment variable management
- **Requests** — HTTP requests to APIs and LLM endpoints
- **NumPy & Pandas** — data processing and manipulation
- **tqdm** — progress bars for long-running operations
- **Docker** — containerization for deployment
- **Docker Compose** — multi-service orchestration and volume mounts
- **Shell Scripts** — startup automation (start.sh)
- **JWT** — secure token-based authentication
- **CORS Middleware** — API access control
- **JSON/JSONL** — persona and chat log storage

---

## 📂 Project Structure & Architecture

### System Architecture

```plaintext
┌───────────────────────────────────────────────────────────────────────────────┐
│                              PersonaForge Architecture                        │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────┐                ┌─────────────────────────────┐  │
│  │       User 1            │                │         User 2              │  │
│  └──────────┬──────────────┘                └───────────┬─────────────────┘  │
│             │                                            │                    │
│             ▼                                            ▼                    │
│  ┌───────────────────────────────────────────────────────────────────────┐    │
│  │                        Docker Container                               │    │
│  │                                                                       │    │
│  │  ┌─────────────────────────────┐      ┌───────────────────────────┐  │    │
│  │  │      Gradio UI              │      │     FastAPI Backend       │  │    │
│  │  │    (Port 7860)              │      │      (Port 8100)          │  │    │
│  │  │                             │      │                           │  │    │
│  │  │  ┌─────────────────────┐    │      │  ┌─────────────────────┐  │  │    │
│  │  │  │   User Interface    │    │      │  │  Authentication     │  │  │    │
│  │  │  └─────────┬───────────┘    │      │  │  (FastAPI Users)    │  │  │    │
│  │  │            │                │      │  └─────────┬───────────┘  │  │    │
│  │  │  ┌─────────▼───────────┐    │      │            │              │  │    │
│  │  │  │  Login/Register     ├───────────►            │              │  │    │
│  │  │  └─────────────────────┘    │      │            ▼              │  │    │
│  │  │                             │      │  ┌─────────────────────┐  │  │    │
│  │  │  ┌─────────────────────┐    │      │  │   FastAPI Endpoints │  │  │    │
│  │  │  │  Export             ├───────────►  └─────────┬───────────┘  │  │    │
│  │  │  ├─────────────────────┤    │      │            │              │  │    │
│  │  │  │  AI-to-AI Chat      ├───────────►            │              │  │    │
│  │  │  ├─────────────────────┤    │      │            ▼              │  │    │
│  │  │  │  Document Upload    ├───────────►  ┌─────────────────────┐  │  │    │
│  │  │  ├─────────────────────┤    │      │  │      RAG Engine    │  │  │    │
│  │  │  │  Chat Interface     ├───────────►  └─────────┬───────────┘  │  │    │
│  │  │  ├─────────────────────┤    │      │            │              │  │    │
│  │  │  │  Create Persona     ├───────────►  ┌─────────▼───────────┐  │  │    │
│  │  │  └─────────────────────┘    │      │  │   Persona Manager   │  │  │    │
│  │  │                             │      │  └─────────┬───────────┘  │  │    │
│  │  └─────────────────────────────┘      │            │              │  │    │
│  │                                       │            ▼              │  │    │
│  │                                       │  ┌─────────────────────┐  │  │    │
│  │                                       │  │   LLM Integration   ├───────┐  │
│  │                                       │  └─────────────────────┘  │    │  │
│  │  ┌───────────────────────────────────────────────────────────┐    │    │  │
│  │  │                Persistent Storage (Volume Mounts)         │    │    │  │
│  │  │                                                           │    │    │  │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐  │    │    │  │
│  │  │  │  SQLite     │  │  Personas   │  │  Knowledge        │  │    │    │  │
│  │  │  │  Database   │  │  (JSON)     │  │  (Vector Store)   │  │    │    │  │
│  │  │  └──────┬──────┘  └──────┬──────┘  └────────┬──────────┘  │    │    │  │
│  │  │         │                │                  │             │    │    │  │
│  │  └─────────┼────────────────┼──────────────────┼─────────────┘    │    │  │
│  │            │                │                  │                  │    │  │
│  │            │                ▼                  │                  │    │  │
│  │            │    ┌─────────────────────┐        │                  │    │  │
│  │            └───►│    Uploads           │◄───────┘                  │    │  │
│  │                 │    (Documents)      │                           │    │  │
│  │                 └─────────────────────┘                           │    │  │
│  │                                                                   │    │  │
│  └───────────────────────────────────────────────────────────────────┘    │  │
│                                                                            │  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    External LLM API (Ollama)                          │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
PersonaForge/
├── backend/
│   ├── main.py               # FastAPI entry point
│   ├── persona_profiles/     # Persona JSON definitions
│   ├── logs/                # Chat history logs (JSONL)
│   ├── prompt_engine.py      # Prompt generation utility
│   ├── persona_storage.py    # Persona versioning and logs
│   ├── rag_engine.py         # RAG functionality
│   └── users/               # User authentication modules
│       ├── models.py         # User and Persona database models
│       ├── schemas.py        # Pydantic schemas for users
│       └── auth.py           # Authentication setup
├── rag_db/                   # Vector database for RAG
├── ui_fastapi_users.py      # Gradio UI with authentication
├── query_db.py              # Database management utility
├── personaforge.db          # SQLite database for users and personas
├── requirements.txt
├── .env
└── README.md
```

## 🚀 Quickstart

### Option 1: Local Setup

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
   python ui_fastapi_users.py
   ```
6. **Access the UI:**
   - Visit [http://127.0.0.1:7860](http://127.0.0.1:7860) for the Gradio UI
   - Visit [http://localhost:8100/docs](http://localhost:8100/docs) for the API docs

### Option 2: Docker Setup (Recommended)

1. **Clone the repo:**
   ```bash
   git clone https://github.com/ManiaSacha/PersonaForge.git
   cd PersonaForge
   ```

2. **Build and run with Docker Compose:**
   ```bash
   docker compose build
   docker compose up
   ```

3. **Access the UI:**
   - Visit [http://localhost:7860](http://localhost:7860) for the Gradio UI
   - Visit [http://localhost:8100/docs](http://localhost:8100/docs) for the API docs

4. **To stop the container:**
   ```bash
   docker compose down
   ```

### First-time setup (both options):
   - Register a new user account through the Authentication tab
   - Login with your credentials
   - Create personas and start using the system

## 🛠️ Usage

### Using the Gradio UI

- **Authentication:**
  - Go to the "Authentication" tab
  - Register a new account with email and password
  - Login with your credentials
  - All your personas and data will be isolated from other users

- **Create a Persona:**
  - Go to the "Create Persona" tab
  - Fill in the name, tone, domain, goals, and response style
  - Click "Create Persona"
  - The persona will be associated with your user account

- **Ask a Persona:**
  - Go to the "Chat with Persona" tab
  - Select a persona from the dropdown (only your personas will appear)
  - Enter your question
  - Select a model (llava, gemma3, llama3.2, gemma:2b, tinyllama)
  - Click "Ask" to get a response

- **Upload Knowledge:**
  - Go to the "Upload Knowledge" tab
  - Select a persona from the dropdown
  - Upload PDF, TXT, or MD files
  - Click "Upload & Embed" to add knowledge to the persona
  - Documents are stored in user-specific collections

- **AI-to-AI Chat:**
  - Go to the "AI-to-AI Chat" tab
  - Select two of your personas, an opening message, and select rounds
  - Click "Start Conversation" to watch them talk to each other

- **Export Persona:**
  - Go to the "Export" tab
  - Select a persona from the dropdown
  - Click "Download Export"
  - Get a JSON file with the persona config and chat history

### Using the API

#### Authentication

- **Register:**
  - Use `POST /auth/register` to create a new user account
- **Login:**
  - Use `POST /auth/jwt/login` to get a JWT token
  - Include the token in the `Authorization: Bearer <token>` header for all requests

#### Persona Management

- **Create a Persona:**
  - Use `POST /persona/` to save a new persona (requires authentication)
- **List Personas:**
  - Use `GET /personas/` to get all personas for the current user
- **Ask a Persona:**
  - Use `POST /ask_persona/` with name, question, and model (requires authentication)
- **Upload Documents:**
  - Use `POST /upload_doc/` to add knowledge to a persona (requires authentication)
- **AI-to-AI Chat:**
  - Use `POST /persona_chat/` to start a conversation between personas (requires authentication)
- **Export Persona Data:**
  - Use `GET /export_persona/{name}` to download persona data (requires authentication)

All API endpoints require authentication and will only allow access to personas owned by the authenticated user.

## 🌟 Example Persona JSON
```json
{
  "name": "TechAdvisor",
  "tone": "Friendly but professional",
  "domain": "Technology",
  "goals": [
    "Explain complex tech concepts simply",
    "Provide balanced product recommendations",
    "Help troubleshoot common tech issues"
  ],
  "response_style": "Clear, concise, with examples",
  "user_id": "1"
}
```

## 💡 Why PersonaForge?

PersonaForge is ideal for:

* 🧪 **Researchers** building multi-agent AI systems
* 💼 **AI engineers** developing domain-specific LLM personas
* 🛡️ **Teams** needing secure user access and RAG integration
* 🏫 **Educators** teaching modular LLM design with memory and prompt engineering
* 🏢 **Businesses** creating specialized AI assistants for different departments

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

## 🌐 More Projects

For more exciting projects, check out my portfolio: [https://mania-sacha.netlify.app/](https://mania-sacha.netlify.app/)

> Made with ❤️ by [ManiaSacha](https://github.com/ManiaSacha)
