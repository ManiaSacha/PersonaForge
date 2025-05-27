import os, json, datetime

PERSONA_DIR = "backend/persona_profiles"
LOG_DIR = "backend/logs"
os.makedirs(PERSONA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def _persona_filename(name: str):
    return os.path.join(PERSONA_DIR, f"{name.lower().replace(' ', '_')}.json")

def save_persona(persona: dict):
    filename = _persona_filename(persona['name'])
    if os.path.exists(filename):
        # Save old version
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = filename.replace(".json", f"_{timestamp}.bak.json")
        os.rename(filename, backup)
    with open(filename, "w") as f:
        json.dump(persona, f, indent=2)

def load_persona(name: str) -> dict:
    filename = _persona_filename(name)
    if not os.path.exists(filename):
        return None
    with open(filename) as f:
        return json.load(f)

def log_interaction(name: str, user_input: str, response: str):
    log_file = os.path.join(LOG_DIR, f"{name.lower().replace(' ', '_')}.log.jsonl")
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "input": user_input,
        "response": response
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")

def export_persona_data(name: str):
    persona = load_persona(name)
    log_file = os.path.join(LOG_DIR, f"{name.lower().replace(' ', '_')}.log.jsonl")
    logs = []
    if os.path.exists(log_file):
        with open(log_file) as f:
            logs = [json.loads(line) for line in f]
    return {
        "persona": persona,
        "logs": logs
    }
