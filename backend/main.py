from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json, os
from backend.prompt_engine import generate_prompt
import requests

app = FastAPI()

PERSONA_DIR = "backend/persona_profiles"

if not os.path.exists(PERSONA_DIR):
    os.makedirs(PERSONA_DIR)

class Persona(BaseModel):
    name: str
    tone: str
    domain: str
    goals: List[str]
    response_style: str

@app.get("/")
def read_root():
    return {"msg": "PersonaForge API is live!"}

@app.post("/persona/")
def create_persona(persona: Persona):
    filename = f"{PERSONA_DIR}/{persona.name.lower().replace(' ', '_')}.json"
    with open(filename, "w") as f:
        json.dump(persona.dict(), f, indent=2)
    return {"msg": f"Persona '{persona.name}' saved!"}

@app.get("/personas/")
def list_personas():
    persona_files = [f for f in os.listdir(PERSONA_DIR) if f.endswith(".json")]
    personas = []
    for file in persona_files:
        with open(os.path.join(PERSONA_DIR, file)) as f:
            data = json.load(f)
            personas.append(data)
    return {"personas": personas}

@app.post("/generate_prompt/")
def get_persona_prompt(name: str, user_input: str):
    filename = f"{PERSONA_DIR}/{name.lower().replace(' ', '_')}.json"
    if not os.path.exists(filename):
        return {"error": "Persona not found"}
    with open(filename) as f:
        persona = json.load(f)
    prompt = generate_prompt(persona, user_input)
    return {"prompt": prompt}

@app.post("/ask_persona/")
def ask_persona(name: str, user_input: str, model: str = "mistral"):
    filename = f"{PERSONA_DIR}/{name.lower().replace(' ', '_')}.json"
    if not os.path.exists(filename):
        return {"error": "Persona not found"}
    with open(filename) as f:
        persona = json.load(f)
    prompt = generate_prompt(persona, user_input)
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,  # e.g., "mistral", "llama3", "gemma"
                "prompt": prompt,
                "stream": False
            }
        )
        data = response.json()
        return {"response": data.get("response")}
    except Exception as e:
        return {"error": str(e)}
