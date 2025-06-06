from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json, os
from datetime import timedelta
from sqlalchemy.orm import Session

from backend.prompt_engine import generate_prompt
from backend.rag_engine import load_and_embed, search_docs
from backend.persona_storage import log_interaction, export_persona_data
from fastapi.responses import FileResponse
from fastapi import UploadFile, File
import requests

from backend.database import get_db
from backend.models import User, Persona
from backend.auth import (
    authenticate_user, 
    create_access_token, 
    get_current_active_user,
    create_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Token endpoint
class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/auth/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# User registration
class UserCreate(BaseModel):
    email: str
    password: str

@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user already exists
        db_user = db.query(User).filter(User.email == user_data.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        # Create new user
        user = create_user(db, user_data.email, user_data.password)
        return {"msg": f"User {user.email} created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration error: {str(e)}"
        )

# Upload document endpoint
@app.post("/upload_doc/")
def upload_doc(
    name: str, 
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Check if persona belongs to user
    persona = db.query(Persona).filter(
        Persona.name == name,
        Persona.owner_id == current_user.id
    ).first()
    
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found or not owned by you"
        )
    
    filepath = f"temp_{file.filename}"
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    try:
        load_and_embed(filepath, name)
        os.remove(filepath)
        return {"msg": f"{file.filename} embedded for {name}!"}
    except Exception as e:
        return {"error": str(e)}

# Persona model
class PersonaCreate(BaseModel):
    name: str
    tone: str
    domain: str
    goals: List[str]
    response_style: str

@app.post("/persona/")
def create_persona(
    persona: PersonaCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Check if persona with this name already exists for this user
    existing_persona = db.query(Persona).filter(
        Persona.name == persona.name,
        Persona.owner_id == current_user.id
    ).first()
    
    if existing_persona:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Persona '{persona.name}' already exists"
        )
    
    # Create new persona
    db_persona = Persona.from_dict(persona.dict(), current_user.id)
    db.add(db_persona)
    db.commit()
    db.refresh(db_persona)
    
    # Also save to file system for backward compatibility
    persona_dict = persona.dict()
    persona_dict["owner_id"] = current_user.id
    save_persona_to_file(persona_dict)
    
    return {"msg": f"Persona '{persona.name}' saved!"}

# Helper function to save persona to file
def save_persona_to_file(persona_dict):
    PERSONA_DIR = "backend/persona_profiles"
    if not os.path.exists(PERSONA_DIR):
        os.makedirs(PERSONA_DIR)
    
    filename = f"{PERSONA_DIR}/{persona_dict['name'].lower().replace(' ', '_')}.json"
    
    # Create backup if file exists
    if os.path.exists(filename):
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{filename.rsplit('.', 1)[0]}_{timestamp}.bak.json"
        os.rename(filename, backup_filename)
    
    with open(filename, "w") as f:
        json.dump(persona_dict, f, indent=2)

@app.get("/personas/")
def list_personas(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Get personas from database
    personas = db.query(Persona).filter(Persona.owner_id == current_user.id).all()
    return {"personas": [p.to_dict() for p in personas]}

class QueryInput(BaseModel):
    name: str
    user_input: str
    model: str = "gemma3"  # Default model, other options include: llava, llama3.2, gemma:2b, tinyllama

@app.post("/ask_persona/")
def ask_persona(
    input: QueryInput,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Check if persona belongs to user
    persona = db.query(Persona).filter(
        Persona.name == input.name,
        Persona.owner_id == current_user.id
    ).first()
    
    if not persona:
        return {"error": "Persona not found or not owned by you"}
    
    # Convert DB persona to dict format for prompt engine
    persona_dict = persona.to_dict()
    
    prompt = generate_prompt(persona_dict, input.user_input)
    try:
        context = search_docs(input.name, input.user_input)
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
        log_interaction(input.name, input.user_input, answer)
        return {"response": answer}
    except Exception as e:
        return {"error": str(e)}

@app.get("/export_persona/{name}")
def export_persona(
    name: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Check if persona belongs to user
    persona = db.query(Persona).filter(
        Persona.name == name,
        Persona.owner_id == current_user.id
    ).first()
    
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found or not owned by you"
        )
    
    data = export_persona_data(name)
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
def persona_to_persona(
    input: PersonaChatInput,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Check if both personas belong to user
    p1 = db.query(Persona).filter(
        Persona.name == input.name1,
        Persona.owner_id == current_user.id
    ).first()
    
    p2 = db.query(Persona).filter(
        Persona.name == input.name2,
        Persona.owner_id == current_user.id
    ).first()
    
    if not p1 or not p2:
        return {"error": "One or both personas not found or not owned by you"}
    
    # Convert DB personas to dict format
    p1_dict = p1.to_dict()
    p2_dict = p2.to_dict()
    
    convo = []
    current_msg = input.starter
    current_speaker = input.name1
    current_speaker_dict = p1_dict

    for i in range(input.rounds):
        prompt = generate_prompt(current_speaker_dict, current_msg)
        context = search_docs(current_speaker, current_msg)
        full_prompt = prompt + f"\n\nRelevant context:\n{context}"

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": input.model, "prompt": full_prompt, "stream": False}
        )
        reply = response.json().get("response", "")
        convo.append(f"🗣 **{current_speaker}**: {current_msg}\n🤖 **Reply**: {reply}\n")

        log_interaction(current_speaker, current_msg, reply)

        # Prepare for next round
        current_msg = reply
        if current_speaker == input.name1:
            current_speaker = input.name2
            current_speaker_dict = p2_dict
        else:
            current_speaker = input.name1
            current_speaker_dict = p1_dict

    return {"conversation": "\n---\n".join(convo)}
