import httpx
from fastapi import FastAPI, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi_users import FastAPIUsers
from typing import List, Optional
import json
import os
import requests

from backend.prompt_engine import generate_prompt
from backend.rag_engine import load_and_embed, search_docs
from backend.persona_storage import log_interaction, export_persona_data
from backend.users.auth import auth_backend
from backend.users.manager import get_user_manager
from backend.users.models import User, Persona, get_async_session
from backend.users.schemas import UserRead, UserCreate, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Create FastAPI Users instance
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# Create FastAPI app
app = FastAPI()

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

# Get current user dependency
current_active_user = fastapi_users.current_user(active=True)

# Upload document endpoint
@app.post("/upload_doc/")
async def upload_doc(
    name: str, 
    file: UploadFile = File(...),
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # Check if persona exists and belongs to the current user
        result = await session.execute(
            select(Persona).where(
                Persona.name == name,
                Persona.user_id == current_user.id
            )
        )
        persona = result.scalars().first()
        
        if not persona:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Persona {name} not found or doesn't belong to you"
            )
            
        # Create directory if it doesn't exist
        os.makedirs(f"backend/persona_docs/{name}", exist_ok=True)
        
        # Save the uploaded file
        file_path = f"backend/persona_docs/{name}/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        # Process the document for RAG
        load_and_embed(file_path=file_path, persona_name=name, user_id=str(current_user.id))
        
        return {"message": f"Document {file.filename} uploaded and processed for persona {name}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {str(e)}"
        )

# Persona model
from pydantic import BaseModel

class PersonaCreate(BaseModel):
    name: str
    tone: str
    domain: str
    goals: List[str]
    response_style: str

@app.post("/persona/")
async def create_persona(
    persona: PersonaCreate,
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # Check if persona already exists for this user
        result = await session.execute(
            select(Persona).where(
                Persona.name == persona.name,
                Persona.user_id == current_user.id
            )
        )
        existing_persona = result.scalars().first()
        
        if existing_persona:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Persona {persona.name} already exists"
            )
            
        # Create new persona
        db_persona = Persona(
            name=persona.name,
            tone=persona.tone,
            domain=persona.domain,
            goals=json.dumps(persona.goals),
            response_style=persona.response_style,
            user_id=current_user.id
        )
        
        session.add(db_persona)
        await session.commit()
        await session.refresh(db_persona)
        
        # Save persona to file
        persona_dict = {
            "name": persona.name,
            "tone": persona.tone,
            "domain": persona.domain,
            "goals": persona.goals,
            "response_style": persona.response_style,
            "user_id": current_user.id
        }
        save_persona_to_file(persona_dict)
        
        return {"message": f"Persona {persona.name} created successfully"}
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating persona: {str(e)}"
        )

# Helper function to save persona to file
def save_persona_to_file(persona_dict):
    os.makedirs("backend/persona_profiles", exist_ok=True)
    file_path = f"backend/persona_profiles/{persona_dict['name']}.json"
    
    with open(file_path, "w") as f:
        json.dump(persona_dict, f, indent=2)
    
    # Create directory for persona documents
    os.makedirs(f"backend/persona_docs/{persona_dict['name']}", exist_ok=True)

@app.get("/personas/")
async def list_personas(
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        result = await session.execute(
            select(Persona).where(Persona.user_id == current_user.id)
        )
        personas = result.scalars().all()
        
        return [{"name": p.name, "tone": p.tone, "domain": p.domain} for p in personas]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing personas: {str(e)}"
        )

class QueryInput(BaseModel):
    name: str
    user_input: str
    model: str = "gemma3"

@app.post("/ask_persona/")
async def ask_persona(
    input: QueryInput,
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # Check if persona exists and belongs to the current user
        result = await session.execute(
            select(Persona).where(
                Persona.name == input.name,
                Persona.user_id == current_user.id
            )
        )
        db_persona = result.scalars().first() # Renamed to avoid conflict with persona_data
        
        if not db_persona:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Persona {input.name} not found or doesn't belong to you"
            )
            
        # Load persona from file
        persona_file_path = f"backend/persona_profiles/{input.name}.json"
        try:
            with open(persona_file_path, "r") as f:
                persona_data = json.load(f)
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Persona profile file {persona_file_path} not found"
            )
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error decoding JSON from {persona_file_path}"
            )
            
        print(f"[ask_persona] Incoming payload: name={input.name}, model={input.model}, user_input={input.user_input}")

        # Search for relevant documents (if RAG is intended here)
        # relevant_docs = search_docs(input.name, input.user_input) # Assuming search_docs is defined and async if needed
        
        # Search for relevant documents from RAG
        print(f"[ask_persona] Searching documents for persona: {input.name}, query: {input.user_input}, user_id: {current_user.id}")
        retrieved_context = ""
        try:
            # Note: search_docs is synchronous. For high-load, consider running in a threadpool.
            retrieved_context = search_docs(
                persona_name=input.name, 
                query=input.user_input, 
                user_id=str(current_user.id)
            )
            print(f"[ask_persona] Retrieved context (first 200 chars): {retrieved_context[:200]}...")
        except Exception as e_search:
            print(f"[ask_persona] Error during document search: {e_search}")
            # Optionally, inform the user or proceed without context
            pass # Proceed without context if search fails

        enhanced_user_input = input.user_input
        if retrieved_context and "No relevant documents found." not in retrieved_context and "Error retrieving relevant documents." not in retrieved_context:
            enhanced_user_input = (
                f"Based on the following context from your documents:\n---CONTEXT BEGIN---\n{retrieved_context}\n---CONTEXT END---\n\n"
                f"Please answer this question: {input.user_input}"
            )
            print(f"[ask_persona] Enhanced user input with context for prompt generation.")
        else:
            print(f"[ask_persona] No relevant context found or error in retrieval. Using original user input for prompt.")
        
        # Generate prompt
        prompt = generate_prompt(persona_data, enhanced_user_input)
        
        # Call LLM API
        llm_payload = {
            "model": input.model,
            "prompt": prompt,
            "stream": True # Explicitly ask for stream, as we are parsing it that way
        }
        print(f"[ask_persona] Sending to LLM API: {llm_payload}")
        
        full_response_content = ""
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                async with client.stream("POST", "http://localhost:11434/api/generate", json=llm_payload) as llm_response_stream:
                    llm_response_stream.raise_for_status() # Check for HTTP errors before streaming
                    print(f"[ask_persona] LLM API status: {llm_response_stream.status_code}, attempting to stream response.")
                    async for line_bytes in llm_response_stream.aiter_lines():
                        line = line_bytes.strip()
                        if not line:
                            continue
                        # print(f"[ask_persona] Stream line: {line}") # Very verbose, uncomment if needed
                        try:
                            json_data_line = json.loads(line)
                            if "response" in json_data_line:
                                full_response_content += json_data_line["response"]
                            if json_data_line.get("done", False):
                                print(f"[ask_persona] 'done: true' received in stream. Full content accumulated so far: '{full_response_content}'")
                                break 
                        except json.JSONDecodeError:
                            print(f"[ask_persona] Malformed JSON in stream line: {line}")
                            continue # Skip malformed lines
            except httpx.ReadTimeout:
                raise HTTPException(status_code=504, detail="LLM API request timed out")
            except httpx.RequestError as e:
                print(f"[ask_persona] LLM API request failed: {e}")
                raise HTTPException(status_code=503, detail=f"LLM API request failed: {str(e)}")
            except Exception as e_stream: # Catch other errors during streaming
                print(f"[ask_persona] Error during LLM response streaming: {e_stream}")
                raise HTTPException(status_code=500, detail=f"Error processing LLM stream: {str(e_stream)}")

        if not full_response_content:
            print("[ask_persona] Warning: full_response_content is empty after attempting to stream and parse.")
            # This could happen if the stream was empty, all json was malformed, or no 'response' keys were found.

        # Log the interaction
        try:
            # Assuming log_interaction is synchronous. If it's async, it should be awaited.
            # Also assuming it takes user_id, persona_name, user_input, llm_response_content
            log_interaction(name=input.name, user_input=input.user_input, response=full_response_content, user_id=str(current_user.id))
        except Exception as log_e:
            print(f"Warning: Failed to log interaction: {log_e}")

        print(f"[ask_persona] Final assembled response before returning to UI: '{full_response_content}'")
        
        return {"response": full_response_content}

    except HTTPException:
        raise # Re-raise HTTPException to let FastAPI handle it
    except Exception as e:
        print(f"Error in /ask_persona endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error in /ask_persona: {str(e)}")

@app.get("/export/{name}")
async def export_persona(
    name: str,
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # Check if persona exists and belongs to the current user
        result = await session.execute(
            select(Persona).where(
                Persona.name == name,
                Persona.user_id == current_user.id
            )
        )
        persona = result.scalars().first()
        
        if not persona:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Persona {name} not found or doesn't belong to you"
            )
            
        # Export persona data
        export_file = export_persona_data(name)
        
        if not export_file:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error exporting persona {name}"
            )
            
        return FileResponse(
            path=export_file,
            filename=f"{name}_export.zip",
            media_type="application/zip"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting persona: {str(e)}"
        )

class PersonaChatInput(BaseModel):
    name1: str
    name2: str
    starter: str
    rounds: int = 5
    model: str = "gemma3"

@app.post("/persona_chat/")
async def persona_to_persona(
    input: PersonaChatInput,
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # Check if both personas exist and belong to the current user
        result1 = await session.execute(
            select(Persona).where(
                Persona.name == input.name1,
                Persona.user_id == current_user.id
            )
        )
        persona1 = result1.scalars().first()
        
        result2 = await session.execute(
            select(Persona).where(
                Persona.name == input.name2,
                Persona.user_id == current_user.id
            )
        )
        persona2 = result2.scalars().first()
        
        if not persona1 or not persona2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"One or both personas not found or don't belong to you"
            )
            
        # Load persona data
        try:
            with open(f"backend/persona_profiles/{input.name1}.json", "r") as f:
                persona1_data = json.load(f)
                
            with open(f"backend/persona_profiles/{input.name2}.json", "r") as f:
                persona2_data = json.load(f)
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Persona profile not found"
            )
            
        # Initialize conversation
        conversation = [{"role": "system", "content": f"This is a conversation starter: {input.starter}"}]
        
        # Run conversation for specified rounds
        current_speaker = input.name1
        other_speaker = input.name2
        
        for _ in range(input.rounds):
            # Get current speaker's persona data
            if current_speaker == input.name1:
                current_persona = persona1_data
            else:
                current_persona = persona2_data
                
            # Generate prompt for current speaker
            conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])
            prompt = generate_prompt(current_persona, conversation_history)
            
            # Call LLM API (using httpx for async streaming)
            llm_payload = {
                "model": input.model,
                "prompt": prompt,
                "stream": True  # Explicitly request streaming
            }
            # Optional: print(f"[persona_to_persona] Sending to LLM API for {current_speaker}: {llm_payload}")

            llm_response_content_for_round = ""
            async with httpx.AsyncClient(timeout=60.0) as client:
                try:
                    async with client.stream("POST", "http://localhost:11434/api/generate", json=llm_payload) as llm_response_stream:
                        llm_response_stream.raise_for_status() # Check for HTTP errors
                        # Optional: print(f"[persona_to_persona] LLM API status: {llm_response_stream.status_code} for {current_speaker}")

                        async for line_bytes in llm_response_stream.aiter_lines():
                            line = line_bytes.strip()
                            if not line:
                                continue
                            try:
                                json_data_line = json.loads(line)
                                if "response" in json_data_line:
                                    llm_response_content_for_round += json_data_line["response"]
                                if json_data_line.get("done", False):
                                    # Optional: print(f"[persona_to_persona] 'done: true' received for {current_speaker}. Content: '{llm_response_content_for_round}'")
                                    break 
                            except json.JSONDecodeError:
                                # Optional: print(f"[persona_to_persona] Malformed JSON in stream line for {current_speaker}: {line}")
                                continue # Skip malformed lines
                except httpx.ReadTimeout:
                    raise HTTPException(status_code=504, detail=f"LLM API request timed out for {current_speaker}")
                except httpx.RequestError as e_req:
                    # Optional: print(f"[persona_to_persona] LLM API request failed for {current_speaker}: {e_req}")
                    raise HTTPException(status_code=503, detail=f"LLM API request failed for {current_speaker}: {str(e_req)}")
                except Exception as e_stream_processing: # Catch other errors during streaming/processing
                    # Optional: print(f"[persona_to_persona] Error during LLM response streaming/processing for {current_speaker}: {e_stream_processing}")
                    raise HTTPException(status_code=500, detail=f"Error processing LLM stream for {current_speaker}: {str(e_stream_processing)}")
            
            if not llm_response_content_for_round:
                # Optional: print(f"[persona_to_persona] Warning: llm_response_content_for_round is empty for {current_speaker} after streaming.")
                pass # Allow empty response to be added to conversation history

            llm_response = llm_response_content_for_round
            
            # Add response to conversation
            conversation.append({"role": current_speaker, "content": llm_response})
            
            # Switch speakers
            current_speaker, other_speaker = other_speaker, current_speaker
            
        return {"conversation": conversation}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in persona chat: {str(e)}"
        )

# Initialize database
@app.on_event("startup")
async def on_startup():
    from backend.users.models import Base, engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
