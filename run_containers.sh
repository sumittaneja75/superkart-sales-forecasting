#!/bin/bash
# Create a Docker network shared by the two containers (ignore the error if it already exists)
docker network create superkart-net 2>/dev/null || true

# Build the backend and frontend images
docker build -t superkart-backend ./backend_files
docker build -t superkart-frontend ./frontend_files

# Remove old containers, if any, then start the backend (port 7860) and the frontend (port 8501)
docker rm -f superkart-backend superkart-frontend 2>/dev/null || true
docker run -d --name superkart-backend --network superkart-net -p 7860:7860 superkart-backend
docker run -d --name superkart-frontend --network superkart-net -p 8501:8501 \
  -e BACKEND_URL=http://superkart-backend:7860 superkart-frontend

docker ps
