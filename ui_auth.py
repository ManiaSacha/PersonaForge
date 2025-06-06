import gradio as gr
import requests
import json
import os

BASE_URL = "http://localhost:8100"

# Token management
def save_token(token):
    with open("auth_token.json", "w") as f:
        json.dump({"token": token}, f)

def load_token():
    try:
        with open("auth_token.json", "r") as f:
            data = json.load(f)
            return data.get("token")
    except:
        return None

def get_auth_headers():
    token = load_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

# Authentication functions
def login(email, password):
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data={"username": email, "password": password}
    )
    if response.status_code == 200:
        token_data = response.json()
        save_token(token_data["access_token"])
        return "Login successful! You can now use the app."
    else:
        return f"Login failed: {response.text}"

def register(email, password, confirm_password):
    if password != confirm_password:
        return "Passwords don't match!"
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={"email": email, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            return "Registration successful! You can now login."
        else:
            return f"Registration failed: Status {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error connecting to server: {str(e)}"

# Persona functions
def submit_persona(name, tone, domain, goals, style):
    payload = {
        "name": name,
        "tone": tone,
        "domain": domain,
        "goals": goals.split(','),
        "response_style": style
    }
    headers = get_auth_headers()
    r = requests.post(f"{BASE_URL}/persona/", json=payload, headers=headers)
    return r.json()

def ask_persona(name, message, model):
    payload = {"name": name, "user_input": message, "model": model}
    headers = get_auth_headers()
    r = requests.post(f"{BASE_URL}/ask_persona/", json=payload, headers=headers)
    try:
        return r.json().get("response")
    except:
        return r.text

def upload_file(name, file, model):
    files = {"file": (file.name, file)}
    headers = get_auth_headers()
    # Model is not used in upload_doc, but included for consistency
    r = requests.post(f"{BASE_URL}/upload_doc/?name={name}", files=files, headers=headers)
    return r.json().get("msg", str(r.content))

def export_persona(name):
    fname = f"{name.lower().replace(' ', '_')}_export.json"
    headers = get_auth_headers()
    r = requests.get(f"{BASE_URL}/export_persona/{name}", headers=headers)
    with open(fname, "wb") as f:
        f.write(r.content)
    return f"Exported to {fname}"

def start_convo(p1, p2, starter, rounds, model):
    payload = {"name1": p1, "name2": p2, "starter": starter, "rounds": int(rounds), "model": model}
    headers = get_auth_headers()
    r = requests.post(f"{BASE_URL}/persona_chat/", json=payload, headers=headers)
    return r.json().get("conversation", "Error: " + str(r.text))

# Create the UI
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 PersonaForge – Your Custom AI Persona Builder")
    
    # Check if user is logged in
    is_logged_in = load_token() is not None
    
    with gr.Tab("Authentication"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Login")
                login_email = gr.Textbox(label="Email")
                login_password = gr.Textbox(label="Password", type="password")
                login_btn = gr.Button("Login")
                login_result = gr.Textbox(label="Result")
                login_btn.click(login, [login_email, login_password], login_result)
            
            with gr.Column():
                gr.Markdown("### Register")
                reg_email = gr.Textbox(label="Email")
                reg_password = gr.Textbox(label="Password", type="password")
                reg_confirm = gr.Textbox(label="Confirm Password", type="password")
                reg_btn = gr.Button("Register")
                reg_result = gr.Textbox(label="Result")
                reg_btn.click(register, [reg_email, reg_password, reg_confirm], reg_result)
    
    with gr.Tab("Create Persona"):
        name = gr.Textbox(label="Name")
        tone = gr.Textbox(label="Tone (e.g., friendly, formal)")
        domain = gr.Textbox(label="Domain (e.g., law, HR, finance)")
        goals = gr.Textbox(label="Goals (comma-separated)")
        style = gr.Textbox(label="Response Style (e.g., concise, elaborate)")
        submit = gr.Button("Create Persona")
        result = gr.Textbox(label="Result")
        submit.click(submit_persona, [name, tone, domain, goals, style], result)

    with gr.Tab("Ask Persona"):
        ask_name = gr.Textbox(label="Persona Name")
        query = gr.Textbox(label="Your Question")
        model_choice = gr.Dropdown(["llava", "gemma3", "llama3.2", "gemma:2b", "tinyllama"], value="gemma3", label="Model")
        ask_button = gr.Button("Ask")
        reply = gr.Textbox(label="Persona's Answer")
        ask_button.click(ask_persona, [ask_name, query, model_choice], reply)

    with gr.Tab("Upload Knowledge"):
        up_name = gr.Textbox(label="Persona Name")
        file = gr.File(label="Upload PDF, TXT or MD")
        model_choice2 = gr.Dropdown(["llava", "gemma3", "llama3.2", "gemma:2b", "tinyllama"], value="gemma3", label="Model (for future use)")
        up_button = gr.Button("Upload & Embed")
        up_result = gr.Textbox(label="Status")
        up_button.click(upload_file, [up_name, file, model_choice2], up_result)

    with gr.Tab("Export Persona"):
        exp_name = gr.Textbox(label="Persona Name")
        exp_btn = gr.Button("Download Export")
        exp_result = gr.Textbox(label="Export Status")
        exp_btn.click(export_persona, exp_name, exp_result)
        
    with gr.Tab("AI-to-AI Chat"):
        gr.Markdown("### 🤖 Let Two Personas Talk to Each Other")
        persona1 = gr.Textbox(label="Persona 1 Name")
        persona2 = gr.Textbox(label="Persona 2 Name")
        starter = gr.Textbox(label="Opening Message")
        rounds = gr.Slider(label="Rounds", minimum=1, maximum=10, value=5, step=1)
        chat_model = gr.Dropdown(["llava", "gemma3", "llama3.2", "gemma:2b", "tinyllama"], value="gemma3", label="Model")
        start_btn = gr.Button("Start Conversation")
        output = gr.Textbox(lines=20, label="Conversation", interactive=False)
        start_btn.click(start_convo, [persona1, persona2, starter, rounds, chat_model], output)

demo.launch()
