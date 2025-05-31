from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json, os
from backend.prompt_engine import generate_prompt
from backend.rag_engine import load_and_embed, search_docs
from backend.persona_storage import save_persona, load_persona, log_interaction, export_persona_data
from fastapi.responses import FileResponse
from fastapi import UploadFile, File
from fastapi.staticfiles import StaticFiles
import requests

# Import FastAPI Users components
from backend.users.auth import auth_backend
from backend.users.manager import get_user_manager
from backend.users.models import User, Persona, get_async_session
from backend.users.schemas import UserRead, UserCreate, UserUpdate
from fastapi_users import FastAPIUsers

# Create FastAPI Users instance
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# Create FastAPI app
app = FastAPI(
    title="PersonaForge API",
    description="API for creating and managing AI personas with RAG capabilities",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include FastAPI Users routers
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Mount the logo directory
try:
    app.mount("/logo", StaticFiles(directory="logo"), name="logo")
except Exception as e:
    print(f"Warning: Could not mount logo directory: {e}")

# Get current user dependency
current_active_user = fastapi_users.current_user(active=True)

@app.post("/upload_doc/")
async def upload_doc(name: str, file: UploadFile = File(...), user: User = Depends(current_active_user)):
    filepath = f"temp_{file.filename}"
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    try:
        # Pass user ID to ensure documents are associated with the user
        load_and_embed(filepath, name, user_id=str(user.id))
        os.remove(filepath)
        return {"msg": f"{file.filename} embedded for {name}!"}
    except Exception as e:
        return {"error": str(e)}

PERSONA_DIR = "backend/persona_profiles"

if not os.path.exists(PERSONA_DIR):
    os.makedirs(PERSONA_DIR)

class PersonaCreate(BaseModel):
    name: str
    tone: str
    domain: str
    goals: List[str]
    response_style: str

@app.get("/", tags=["root"])
def read_root():
    return {
        "message": "Welcome to PersonaForge API",
        "description": "Create, chat with, and manage AI personas with RAG capabilities",
        "logo": "/logo/personaforgelogo.png",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.post("/persona/")
async def create_persona(persona: PersonaCreate, user: User = Depends(current_active_user)):
    try:
        # Create a persona with user ID
        persona_data = persona.dict()
        persona_data["user_id"] = str(user.id)
        save_persona(persona_data)
        
        # Create in database
        session = await anext(get_async_session())
        try:
            db_persona = Persona(
                name=persona.name, 
                tone=persona.tone,
                domain=persona.domain,
                goals=",".join(persona.goals),
                response_style=persona.response_style,
                user_id=user.id
            )
            session.add(db_persona)
            await session.commit()
            await session.refresh(db_persona)
        except Exception as db_error:
            await session.rollback()
            raise db_error
        finally:
            await session.close()
        
        return {"msg": f"Persona '{persona.name}' saved!"}
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error creating persona: {str(e)}\n{error_details}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to create persona: {str(e)}")

@app.get("/personas/")
async def list_personas(user: User = Depends(current_active_user)):
    # Only list personas belonging to the authenticated user
    persona_files = [f for f in os.listdir(PERSONA_DIR) if f.endswith(".json")]
    personas = []
    for file in persona_files:
        with open(os.path.join(PERSONA_DIR, file)) as f:
            data = json.load(f)
            # Only include personas that belong to this user
            if data.get("user_id") == str(user.id):
                personas.append(data)
    return {"personas": personas}

@app.post("/generate_prompt/")
async def get_persona_prompt(name: str, user_input: str, user: User = Depends(current_active_user)):
    filename = f"{PERSONA_DIR}/{name.lower().replace(' ', '_')}.json"
    if not os.path.exists(filename):
        return {"error": "Persona not found"}
    with open(filename) as f:
        persona = json.load(f)
    # Check if persona belongs to user
    if persona.get("user_id") != str(user.id):
        return {"error": "You do not have access to this persona"}
    prompt = generate_prompt(persona, user_input)
    return {"prompt": prompt}

class QueryInput(BaseModel):
    name: str
    user_input: str
    model: str = "gemma3"  # Default model, other options include: llava, llama3.2, gemma:2b, tinyllama

@app.post("/ask_persona/")
async def ask_persona(input: QueryInput, user: User = Depends(current_active_user)):
    try:
        # Load persona with user_id to ensure we get the right one
        persona = load_persona(input.name, user_id=str(user.id))
        if not persona:
            return {"error": "Persona not found"}
            
        # Check is redundant now but keeping for safety
        if persona.get("user_id") != str(user.id):
            return {"error": "You do not have access to this persona"}
            
        prompt = generate_prompt(persona, input.user_input)
        try:
            context = search_docs(input.name, input.user_input, user_id=str(user.id))
            full_prompt = prompt + f"\n\nRelevant context:\n{context}"
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": input.model,
                    "prompt": full_prompt,
                    "stream": False
                }
            )
            answer = response.json().get("response")
            log_interaction(input.name, input.user_input, answer, user_id=str(user.id))
            return {"response": answer}
        except Exception as e:
            return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to process request: {str(e)}"}

@app.get("/export_persona/{name}")
async def export_persona(name: str, user: User = Depends(current_active_user)):
    # Check if persona belongs to user
    persona = load_persona(name)
    if not persona:
        return {"error": "Persona not found"}
    if persona.get("user_id") != str(user.id):
        return {"error": "You do not have access to this persona"}
    
    data = export_persona_data(name, user_id=str(user.id))
    filename = f"{name.lower().replace(' ', '_')}_export.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    return FileResponse(filename, filename=filename, media_type="application/json")

class PersonaChatInput(BaseModel):
    name1: str
    name2: str
    starter: str
    rounds: int = 5
    model: str = "gemma3"  # Default model, other options include: llava, llama3.2, gemma:2b, tinyllama

@app.post("/persona_chat/")
async def persona_to_persona(input: PersonaChatInput, user: User = Depends(current_active_user)):
    p1 = load_persona(input.name1, user_id=str(user.id))
    p2 = load_persona(input.name2, user_id=str(user.id))
    if not p1 or not p2:
        return {"error": "One or both personas not found"}
    
    # Check if both personas belong to user
    if p1.get("user_id") != str(user.id) or p2.get("user_id") != str(user.id):
        return {"error": "You do not have access to one or both personas"}

    convo = []
    current_msg = input.starter
    current_speaker = input.name1

    for i in range(input.rounds):
        speaker = load_persona(current_speaker, user_id=str(user.id))
        prompt = generate_prompt(speaker, current_msg)
        context = search_docs(current_speaker, current_msg, user_id=str(user.id))
        full_prompt = prompt + f"\n\nRelevant context:\n{context}"

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": input.model, "prompt": full_prompt, "stream": False}
        )
        reply = response.json().get("response", "")
        convo.append(f"🗣 **{current_speaker}**: {current_msg}\n🤖 **Reply**: {reply}\n")

        log_interaction(current_speaker, current_msg, reply, user_id=str(user.id))

        # Prepare for next round
        current_msg = reply
        current_speaker = input.name2 if current_speaker == input.name1 else input.name1

    return {"conversation": "\n---\n".join(convo)}
