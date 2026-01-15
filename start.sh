#!/bin/bash

echo "Starting FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

sleep 3

echo "Starting Streamlit..."
streamlit run streamlit_ui/ui.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true &

wait

