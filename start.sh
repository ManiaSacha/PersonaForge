#!/bin/bash

# Initialize the database
python init_fastapi_users_db.py

# Start the FastAPI backend
uvicorn backend.main_fastapi_users:app --host 0.0.0.0 --port 8100 &

# Start the Gradio UI
python ui_fastapi_users.py --server_name=0.0.0.0

# Keep container running
wait
