FROM python:3.10-slim

# Avoid Python buffering issues
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# System deps for pdfplumber
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app
COPY streamlit_ui ./streamlit_ui
COPY start.sh .

EXPOSE 8000
EXPOSE 8501

CMD ["bash", "start.sh"]
