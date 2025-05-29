import gradio as gr
import requests
import json
import os

BASE_URL = "http://localhost:8100"

def submit_persona(name, tone, domain, goals, style):
    payload = {
        "name": name,
        "tone": tone,
        "domain": domain,
        "goals": goals.split(','),
        "response_style": style
    }
    r = requests.post(f"{BASE_URL}/persona/", json=payload)
    return r.json()

def ask_persona(name, message, model):
    payload = {"name": name, "user_input": message, "model": model}
    r = requests.post(f"{BASE_URL}/ask_persona/", json=payload)
    try:
        return r.json().get("response")
    except:
        return r.text

def upload_file(name, file, model):
    files = {"file": (file.name, file)}
    # Model is not used in upload_doc, but included for consistency
    r = requests.post(f"{BASE_URL}/upload_doc/?name={name}", files=files)
    return r.json().get("msg", str(r.content))

def export_persona(name):
    fname = f"{name.lower().replace(' ', '_')}_export.json"
    r = requests.get(f"{BASE_URL}/export_persona/{name}")
    with open(fname, "wb") as f:
        f.write(r.content)
    return f"Exported to {fname}"

with gr.Blocks() as demo:
    gr.Markdown("# 🤖 PersonaForge – Your Custom AI Persona Builder")

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
        
        def start_convo(p1, p2, starter, rounds, model):
            payload = {"name1": p1, "name2": p2, "starter": starter, "rounds": int(rounds), "model": model}
            r = requests.post(f"{BASE_URL}/persona_chat/", json=payload)
            return r.json().get("conversation", "Error: " + str(r.text))
            
        start_btn.click(start_convo, [persona1, persona2, starter, rounds, chat_model], output)

demo.launch()
