#!/bin/bash

# Authenticate with GitHub CLI using token
if [ -n "$GH_TOKEN" ]; then
  echo "$GH_TOKEN" | gh auth login --hostname github.com --git-protocol https --with-token
else
  echo "Warning: GH_TOKEN not set. gh auth login will be skipped."
fi

# Start Streamlit app
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0 