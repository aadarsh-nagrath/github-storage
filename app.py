import streamlit as st
from git import Repo, GitCommandError
import os
from PIL import Image
import shutil

# Path to the local git repo (assume cloned in /app/repo)
REPO_PATH = os.getenv('REPO_PATH', './repo')
STORAGE_DIR = os.path.join(REPO_PATH, 'storage')

st.title('GitHub Image Storage - Bucket (Branch) Interface')

# Prompt for bucket (branch) name
bucket = st.text_input('Enter bucket name (branch):')

if bucket:
    repo = Repo(REPO_PATH)
    # Check if branch exists
    if bucket in repo.branches:
        st.success(f"Switching to bucket: {bucket}")
        repo.git.checkout(bucket)
    else:
        try:
            new_branch = repo.create_head(bucket)
            repo.git.checkout(bucket)
            st.success(f"Created and switched to new bucket: {bucket}")
        except GitCommandError as e:
            st.error(f"Error creating/switching branch: {e}")

    # Ensure storage directory exists
    os.makedirs(STORAGE_DIR, exist_ok=True)

    st.header(f"Images in bucket: {bucket}")

    # --- Image Upload ---
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "gif"])
    if uploaded_file is not None:
        image_path = os.path.join(STORAGE_DIR, uploaded_file.name)
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        # Add, commit, and push
        repo.git.add(image_path)
        repo.index.commit(f"Add image {uploaded_file.name} to bucket {bucket}")
        try:
            repo.git.push('origin', bucket)
            st.success(f"Uploaded and pushed {uploaded_file.name}")
        except GitCommandError as e:
            st.error(f"Push failed: {e}")

    # --- List Images ---
    images = [f for f in os.listdir(STORAGE_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
    if images:
        for img_name in images:
            img_path = os.path.join(STORAGE_DIR, img_name)
            st.image(img_path, caption=img_name, width=200)
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button(f"Delete {img_name}", key=img_name):
                    os.remove(img_path)
                    repo.git.add(img_path)
                    repo.index.commit(f"Delete image {img_name} from bucket {bucket}")
                    try:
                        repo.git.push('origin', bucket)
                        st.success(f"Deleted and pushed {img_name}")
                    except GitCommandError as e:
                        st.error(f"Push failed: {e}")
                    st.experimental_rerun()
    else:
        st.info("No images found in this bucket.")
else:
    st.info('Please enter a bucket name to continue.') 