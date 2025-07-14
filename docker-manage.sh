#!/bin/bash

# Variables
IMAGE_NAME=github-storage-app
CONTAINER_NAME=github-storage-app-container
REPO_URL="https://github.com/aadarsh-nagrath/github-storage.git"
REPO_DIR="repo"
PORT=8501

# Build Docker image

echo "[1/4] Building Docker image..."
docker build --build-arg GH_TOKEN=${GH_TOKEN} -t $IMAGE_NAME . || { echo "Docker build failed"; exit 1; }

# Remove any existing container

echo "[2/4] Removing old container (if exists)..."
docker rm -f $CONTAINER_NAME 2>/dev/null || true

# Clone repo if not present
if [ ! -d "$REPO_DIR/.git" ]; then
  echo "[3/4] Cloning repo..."
  git clone $REPO_URL $REPO_DIR || { echo "Git clone failed"; exit 1; }
else
  echo "[3/4] Repo already present."
fi

# Run container with volume mount for repo and port mapping

echo "[4/4] Running Streamlit app in Docker..."
docker run --name $CONTAINER_NAME -p $PORT:8501 -v $(pwd)/$REPO_DIR:/app/repo -v $(pwd):/app -e REPO_PATH=/app/repo -e GH_TOKEN=${GH_TOKEN} $IMAGE_NAME streamlit run app.py 