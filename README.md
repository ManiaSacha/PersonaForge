# PersonaForge 🚀

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ManiaSacha/PersonaForge)

---

> **PersonaForge** is a modular platform for building, managing, and running AI personas with Retrieval-Augmented Generation (RAG), LLMs, and multi-persona orchestration. Perfect for research, prototyping, and production AI applications.

---

## ✨ Features

- ⚡ **FastAPI Backend** — blazing fast, modern Python API
- 🧠 **Persona Profiles** — define, save, and load persona JSON schemas
- 📝 **Prompt Engine** — generate persona-customized prompts for LLMs
- 💾 **Disk Persistence** — all personas are saved as JSON for easy sharing
- 🔌 **RAG & Vector DB Ready** — designed for easy integration with embeddings and RAG pipelines
- 🔒 **Extensible** — add new persona types, prompt templates, and LLMs easily

## 📂 Project Structure

```
PersonaForge/
├── backend/
│   ├── main.py               # FastAPI entry point
│   ├── persona_profiles/     # Persona JSON definitions
│   └── prompt_engine.py      # Prompt generation utility
├── data/                     # Documents for RAG
├── models/                   # Fine-tuned models or checkpoints
├── requirements.txt
├── .env
├── README.md
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
4. **Run the FastAPI server:**
   ```bash
   uvicorn backend.main:app --reload --port 8100
   ```
5. **Open Swagger UI:**
   - Visit [http://localhost:8100/docs](http://localhost:8100/docs)

## 🛠️ Usage

- **Create a Persona:**
  - Use `POST /persona/` in Swagger UI to save a new persona.
- **List Personas:**
  - Use `GET /personas/` to see all saved personas.
- **Generate Persona Prompt:**
  - Use `POST /generate_prompt/` with a persona name and user query to get a custom prompt for LLMs.

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
