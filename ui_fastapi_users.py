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
    try:
        response = requests.post(
            f"{BASE_URL}/auth/jwt/login",
            data={"username": email, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            token_data = response.json()
            save_token(token_data["access_token"])
            return "Login successful! You can now use the app."
        else:
            return f"Login failed: Status {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error connecting to server: {str(e)}"

def register(email, password, confirm_password):
    if password != confirm_password:
        return "Passwords don't match!"
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={"email": email, "password": password},
            timeout=10
        )
        if response.status_code == 201:  # FastAPI Users returns 201 Created
            return "Registration successful! You can now login."
        else:
            return f"Registration failed: Status {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error connecting to server: {str(e)}"

# Persona functions
def submit_persona(name, tone, domain, goals, style):
    headers = get_auth_headers()
    if not headers:
        return "Please login first!"
    
    if not name or not tone or not domain or not goals or not style:
        return "All fields are required!"
    
    try:
        goals_list = [goal.strip() for goal in goals.split(",") if goal.strip()]
        if not goals_list:
            return "Please provide at least one goal!"
        
        print(f"Creating persona with name: {name}, tone: {tone}, domain: {domain}, goals: {goals_list}, style: {style}")
        
        response = requests.post(
            f"{BASE_URL}/persona/",
            headers=headers,
            json={
                "name": name,
                "tone": tone,
                "domain": domain,
                "goals": goals_list,
                "response_style": style
            },
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            return f"Persona '{name}' created successfully!"
        else:
            error_msg = f"Error creating persona: Status {response.status_code}"
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    error_msg += f" - {error_data['detail']}"
                elif 'msg' in error_data:
                    error_msg += f" - {error_data['msg']}"
                else:
                    error_msg += f" - {response.text}"
            except:
                error_msg += f" - {response.text}"
            return error_msg
    except Exception as e:
        return f"Error creating persona: {str(e)}"

def get_personas():
    headers = get_auth_headers()
    if not headers:
        return []
    
    try:
        response = requests.get(f"{BASE_URL}/personas/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # Handle the response format - the API returns a list of persona objects
            if isinstance(data, list):
                return [p["name"] for p in data]
            else:
                # Fallback for potential future API changes
                personas = data.get('personas', [])
                return [p["name"] for p in personas]
        else:
            print(f"Error fetching personas: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Exception in get_personas: {str(e)}")
        return []

def ask_question(persona, question, model):
    headers = get_auth_headers()
    if not headers:
        return "Please login first!"
    
    if not persona:
        return "Please select a persona!"
    
    if not question:
        return "Please enter a question!"
    
    try:
        print(f"Asking question to persona: {persona}, model: {model}, question: {question}")
        
        response = requests.post(
            f"{BASE_URL}/ask_persona/",
            headers=headers,
            json={
                "name": persona,
                "user_input": question,
                "model": model
            },
            timeout=30  # Increased timeout for model inference
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text[:100]}..." if len(response.text) > 100 else f"Response text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if "response" in data:
                return data["response"]
            elif "error" in data:
                return f"Error: {data['error']}"
            else:
                return f"Unexpected response format: {data}"
        else:
            try:
                error_data = response.json()
                if "detail" in error_data:
                    return f"Error: {error_data['detail']}"
                elif "error" in error_data:
                    return f"Error: {error_data['error']}"
                else:
                    return f"Error: Status {response.status_code} - {response.text}"
            except:
                return f"Error: Status {response.status_code} - {response.text}"
    except Exception as e:
        print(f"Exception in ask_question: {str(e)}")
        return f"Error: {str(e)}"

def upload_document(persona, file):
    headers = get_auth_headers()
    if not headers:
        return "Please login first!"
    
    if not file:
        return "Please select a file to upload!"
    
    files = {"file": (os.path.basename(file.name), open(file.name, "rb"), "application/octet-stream")}
    response = requests.post(
        f"{BASE_URL}/upload_doc/?name={persona}",
        headers=headers,
        files=files
    )
    
    if response.status_code == 200:
        return f"Document uploaded and processed for {persona}!"
    else:
        return f"Error uploading document: {response.text}"

def export_persona_data(persona):
    headers = get_auth_headers()
    if not headers:
        return "Please login first!"
    
    response = requests.get(
        f"{BASE_URL}/export/{persona}",
        headers=headers
    )
    
    if response.status_code == 200:
        with open(f"{persona}_export.zip", "wb") as f:
            f.write(response.content)
        return f"Persona data exported to {persona}_export.zip!"
    else:
        return f"Error exporting persona data: {response.text}"

def persona_chat(persona1, persona2, starter, rounds, model):
    headers = get_auth_headers()
    if not headers:
        return "Please login first!"
    
    response = requests.post(
        f"{BASE_URL}/persona_chat/",
        headers=headers,
        json={
            "name1": persona1,
            "name2": persona2,
            "starter": starter,
            "rounds": rounds,
            "model": model
        }
    )
    
    if response.status_code == 200:
        conversation = response.json()["conversation"]
        chat_text = ""
        for msg in conversation:
            if msg["role"] == "system":
                chat_text += f"[System] {msg['content']}\n\n"
            else:
                chat_text += f"[{msg['role']}] {msg['content']}\n\n"
        return chat_text
    else:
        return f"Error in persona chat: {response.text}"

# Create Gradio interface
import base64

def get_base64_image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img_base64 = get_base64_image("logo/personaforgelogo.png")

with gr.Blocks(title="PersonaForge", theme=gr.themes.Base(primary_hue="pink", secondary_hue="purple")) as app:
    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML(f'<img src="data:image/png;base64,{img_base64}" style="height:130px;">')
        with gr.Column(scale=3):
            gr.Markdown("# PersonaForge")
            gr.Markdown("Create, chat with, and manage AI personas with RAG capabilities")
    
    # Authentication tab
    with gr.Tab("Authentication"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("## Register")
                register_email = gr.Textbox(label="Email")
                register_password = gr.Textbox(label="Password", type="password")
                register_confirm = gr.Textbox(label="Confirm Password", type="password")
                register_btn = gr.Button("Register")
                register_result = gr.Textbox(label="Result")
                
                register_btn.click(
                    register,
                    inputs=[register_email, register_password, register_confirm],
                    outputs=register_result
                )
                
            with gr.Column():
                gr.Markdown("## Login")
                login_email = gr.Textbox(label="Email")
                login_password = gr.Textbox(label="Password", type="password")
                login_btn = gr.Button("Login")
                login_result = gr.Textbox(label="Result")
                
                login_btn.click(
                    login,
                    inputs=[login_email, login_password],
                    outputs=login_result
                )
    
    # Create Persona tab
    with gr.Tab("Create Persona"):
        persona_name = gr.Textbox(label="Name")
        persona_tone = gr.Textbox(label="Tone (e.g., friendly, professional)")
        persona_domain = gr.Textbox(label="Domain/Expertise")
        persona_goals = gr.Textbox(label="Goals (comma separated)")
        persona_style = gr.Textbox(label="Response Style")
        create_btn = gr.Button("Create Persona")
        create_result = gr.Textbox(label="Result")
        
        create_btn.click(
            submit_persona,
            inputs=[persona_name, persona_tone, persona_domain, persona_goals, persona_style],
            outputs=create_result
        )
    
    # Chat tab
    with gr.Tab("Chat with Persona"):
        chat_persona = gr.Dropdown(label="Select Persona", choices=get_personas())
        refresh_btn = gr.Button("Refresh Personas")
        chat_model = gr.Dropdown(
            label="Model", 
            choices=["gemma3", "llama3.2", "llava", "gemma:2b", "tinyllama"],
            value="gemma3"
        )
        chat_question = gr.Textbox(label="Your Question")
        chat_btn = gr.Button("Ask")
        chat_response = gr.Textbox(label="Response")
        
        refresh_btn.click(lambda: gr.update(choices=get_personas()), outputs=chat_persona)
        chat_btn.click(
            ask_question,
            inputs=[chat_persona, chat_question, chat_model],
            outputs=chat_response
        )
    
    # Upload Knowledge tab
    with gr.Tab("Upload Knowledge"):
        upload_persona = gr.Dropdown(label="Select Persona", choices=get_personas())
        upload_refresh_btn = gr.Button("Refresh Personas")
        upload_file = gr.File(label="Document")
        upload_btn = gr.Button("Upload")
        upload_result = gr.Textbox(label="Result")
        
        upload_refresh_btn.click(lambda: gr.update(choices=get_personas()), outputs=upload_persona)
        upload_btn.click(
            upload_document,
            inputs=[upload_persona, upload_file],
            outputs=upload_result
        )
    
    # Persona-to-Persona Chat tab
    with gr.Tab("AI-to-AI Chat"):
        p2p_persona1 = gr.Dropdown(label="Persona 1", choices=get_personas())
        p2p_persona2 = gr.Dropdown(label="Persona 2", choices=get_personas())
        p2p_refresh_btn = gr.Button("Refresh Personas")
        p2p_starter = gr.Textbox(label="Conversation Starter")
        p2p_rounds = gr.Slider(label="Conversation Rounds", minimum=1, maximum=10, step=1, value=5)
        p2p_model = gr.Dropdown(
            label="Model", 
            choices=["gemma3", "llama3.2", "llava", "gemma:2b", "tinyllama"],
            value="gemma3"
        )
        p2p_btn = gr.Button("Start Conversation")
        p2p_result = gr.Textbox(label="Conversation")
        
        p2p_refresh_btn.click(lambda: [gr.update(choices=get_personas()), gr.update(choices=get_personas())], outputs=[p2p_persona1, p2p_persona2])
        p2p_btn.click(
            persona_chat,
            inputs=[p2p_persona1, p2p_persona2, p2p_starter, p2p_rounds, p2p_model],
            outputs=p2p_result
        )
    
    # Export tab
    with gr.Tab("Export"):
        export_persona = gr.Dropdown(label="Select Persona", choices=get_personas())
        export_refresh_btn = gr.Button("Refresh Personas")
        export_btn = gr.Button("Export Persona Data")
        export_result = gr.Textbox(label="Result")
        
        export_refresh_btn.click(lambda: gr.update(choices=get_personas()), outputs=export_persona)
        export_btn.click(
            export_persona_data,
            inputs=export_persona,
            outputs=export_result
        )

# Launch the app
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='PersonaForge UI')
    parser.add_argument('--server_name', type=str, default="127.0.0.1", help='Server name')
    parser.add_argument('--server_port', type=int, default=7860, help='Server port')
    args = parser.parse_args()
    
    app.launch(server_name=args.server_name, server_port=args.server_port)
