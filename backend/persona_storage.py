import os, json, datetime

PERSONA_DIR = "backend/persona_profiles"
LOG_DIR = "backend/logs"
os.makedirs(PERSONA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def _persona_filename(name: str, user_id: str = None):
    # If user_id is provided, include it in the filename to ensure uniqueness across users
    if user_id:
        return os.path.join(PERSONA_DIR, f"{user_id}_{name.lower().replace(' ', '_')}.json")
    else:
        return os.path.join(PERSONA_DIR, f"{name.lower().replace(' ', '_')}.json")

def save_persona(persona: dict):
    # Get user_id from persona dict if it exists
    user_id = persona.get('user_id')
    filename = _persona_filename(persona['name'], user_id)
    
    if os.path.exists(filename):
        # Save old version
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = filename.replace(".json", f"_{timestamp}.bak.json")
        os.rename(filename, backup)
    
    with open(filename, "w") as f:
        json.dump(persona, f, indent=2)

def load_persona(name: str, user_id: str = None) -> dict:
    # First try with user_id prefix
    filename = _persona_filename(name, user_id)
    print(f"Attempting to load persona from: {filename}")
    
    if os.path.exists(filename):
        try:
            with open(filename) as f:
                persona = json.load(f)
                # Ensure user_id is in the persona data
                if user_id and 'user_id' not in persona:
                    persona['user_id'] = user_id
                    # Save the updated persona
                    with open(filename, 'w') as f:
                        json.dump(persona, f, indent=2)
                return persona
        except Exception as e:
            print(f"Error loading persona from {filename}: {str(e)}")
            return None
    
    # If not found with user_id, try without (for backward compatibility)
    if user_id:
        filename = _persona_filename(name)
        print(f"Attempting to load persona from (legacy path): {filename}")
        
        if os.path.exists(filename):
            try:
                with open(filename) as f:
                    persona = json.load(f)
                    # Add user_id to the persona data
                    persona['user_id'] = user_id
                    # Save to the new filename with user_id
                    new_filename = _persona_filename(name, user_id)
                    with open(new_filename, 'w') as f:
                        json.dump(persona, f, indent=2)
                    print(f"Migrated persona from {filename} to {new_filename}")
                    return persona
            except Exception as e:
                print(f"Error loading/migrating persona from {filename}: {str(e)}")
                return None
    
    # List all persona files to help with debugging
    print(f"Persona not found. Available personas in {PERSONA_DIR}:")
    for f in os.listdir(PERSONA_DIR):
        if f.endswith('.json'):
            print(f"  - {f}")
    
    return None

def log_interaction(name: str, user_input: str, response: str, user_id: str = None):
    # Include user_id in log filename if provided
    if user_id:
        log_file = os.path.join(LOG_DIR, f"{user_id}_{name.lower().replace(' ', '_')}.log.jsonl")
    else:
        log_file = os.path.join(LOG_DIR, f"{name.lower().replace(' ', '_')}.log.jsonl")
        
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "input": user_input,
        "response": response,
        "user_id": user_id  # Store user_id in log entry
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")

import zipfile
import tempfile

def export_persona_data(name: str, user_id: str = None) -> str:
    persona_data = load_persona(name, user_id)
    if not persona_data:
        # This will be caught by FileNotFoundError in the endpoint if load_persona returns None
        # and the endpoint tries to use a None path. Or handle more explicitly here.
        raise FileNotFoundError(f"Persona '{name}' not found for user '{user_id}'.")

    log_filename_base = f"{user_id}_{name.lower().replace(' ', '_')}.log.jsonl" if user_id else f"{name.lower().replace(' ', '_')}.log.jsonl"
    log_file_path = os.path.join(LOG_DIR, log_filename_base)

    # Create a temporary directory for the ZIP file
    # temp_dir = tempfile.mkdtemp()
    # zip_filename = f"{user_id}_{name}_export.zip" if user_id else f"{name}_export.zip"
    # zip_file_path = os.path.join(temp_dir, zip_filename)
    
    # Using a named temporary file directly for the zip to simplify cleanup
    # The FileResponse will handle sending it and it should be cleaned up after.
    # For more robust cleanup, especially on errors, a try/finally with os.remove might be needed
    # if not using a context manager that handles deletion.
    temp_zip_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip', prefix=f"persona_export_{name}_")
    zip_file_path = temp_zip_file.name
    temp_zip_file.close() # Close it so zipfile can open and write to it

    try:
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add persona JSON data
            persona_json_str = json.dumps(persona_data, indent=2)
            zf.writestr(f"{name}_persona.json", persona_json_str)

            # Add logs if they exist
            if os.path.exists(log_file_path):
                zf.write(log_file_path, arcname=log_filename_base)
            else:
                # Optionally, create an empty log file in the zip or a note
                zf.writestr(log_filename_base, "# No logs found for this persona.\n")
            
            # Add RAG documents if they exist
            # The RAG DB itself (Chroma) is a directory structure, not a single file easily zipped.
            # For simplicity, we'll export the source documents if they are stored.
            persona_docs_dir_base = f"{user_id}_{name}" if user_id else name
            persona_docs_dir = os.path.join("backend", "persona_docs", persona_docs_dir_base) # Adjusted based on rag_engine DB_DIR structure
            
            if os.path.exists(persona_docs_dir) and os.path.isdir(persona_docs_dir):
                for doc_filename in os.listdir(persona_docs_dir):
                    doc_file_path = os.path.join(persona_docs_dir, doc_filename)
                    if os.path.isfile(doc_file_path):
                        zf.write(doc_file_path, arcname=f"documents/{doc_filename}")
            else:
                zf.writestr("documents/readme.txt", "# No uploaded documents found for this persona.\n")

    except Exception as e_zip:
        # If zipping fails, clean up the partially created temp zip file
        if os.path.exists(zip_file_path):
            os.remove(zip_file_path)
        raise IOError(f"Failed to create persona export zip: {str(e_zip)}")

    return zip_file_path
