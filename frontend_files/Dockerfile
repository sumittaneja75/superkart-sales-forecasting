# Lightweight Python base image
FROM python:3.11-slim

WORKDIR /app

# Copy the Streamlit app and install its dependencies
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Serve the Streamlit UI on port 8501
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false"]
