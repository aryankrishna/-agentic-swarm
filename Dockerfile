# ---- Base image ----
FROM python:3.11-slim

# ---- Set up workdir ----
WORKDIR /app

# ---- System deps for OCR ----
RUN apt-get update && \
    apt-get install -y --no-install-recommends tesseract-ocr && \
    rm -rf /var/lib/apt/lists/*

# ---- Copy project files ----
COPY . .

# ---- Install Python dependencies ----
RUN pip install --no-cache-dir -r requirements.txt

# ---- Expose Streamlit port ----
EXPOSE 8501

# ---- Run the app ----
CMD ["streamlit", "run", "apps/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]