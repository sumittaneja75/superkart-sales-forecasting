# Lightweight Python base image
FROM python:3.11-slim

# Working directory inside the container
WORKDIR /app

# Copy the API code, the model and the dependency list, then install the dependencies
COPY . .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Serve the Flask app with gunicorn on port 7860
EXPOSE 7860
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]
