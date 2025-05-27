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
        model_choice = gr.Dropdown(["llava", "gemma3", "llama3.2"], value="gemma3", label="Model")
        ask_button = gr.Button("Ask")
        reply = gr.Textbox(label="Persona's Answer")
        ask_button.click(ask_persona, [ask_name, query, model_choice], reply)

    with gr.Tab("Upload Knowledge"):
        up_name = gr.Textbox(label="Persona Name")
        file = gr.File(label="Upload PDF, TXT or MD")
        model_choice2 = gr.Dropdown(["llava", "gemma3", "llama3.2"], value="gemma3", label="Model (for future use)")
        up_button = gr.Button("Upload & Embed")
        up_result = gr.Textbox(label="Status")
        up_button.click(upload_file, [up_name, file, model_choice2], up_result)

demo.launch()
