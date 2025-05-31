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

def export_persona_data(name: str, user_id: str = None):
    persona = load_persona(name, user_id)
    
    # Use user-specific log file if user_id is provided
    if user_id:
        log_file = os.path.join(LOG_DIR, f"{user_id}_{name.lower().replace(' ', '_')}.log.jsonl")
    else:
        log_file = os.path.join(LOG_DIR, f"{name.lower().replace(' ', '_')}.log.jsonl")
    
    logs = []
    if os.path.exists(log_file):
        with open(log_file) as f:
            logs = [json.loads(line) for line in f]
    
    return {
        "persona": persona,
        "logs": logs
    }
