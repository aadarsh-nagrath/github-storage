import streamlit as st
from git import Repo, GitCommandError
import os
from PIL import Image
import shutil

# Path to the local git repo (assume cloned in /app/repo)
REPO_PATH = os.getenv('REPO_PATH', './repo')
STORAGE_DIR = os.path.join(REPO_PATH, 'storage')

# --- Custom CSS for modern look ---
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #e0e7ff 0%, #f5f7fa 100%);
    }
    .main {
        background: transparent !important;
    }
    .bucket-card {
        background: #fff;
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(30,60,114,0.08);
        padding: 1.2em 1.5em 1.2em 1.5em;
        margin-bottom: 1.2em;
        transition: box-shadow 0.2s;
        border: 2px solid #e0e7ff;
    }
    .bucket-card:hover {
        box-shadow: 0 8px 32px rgba(30,60,114,0.18);
        border: 2px solid #6366f1;
    }
    .current-badge {
        background: linear-gradient(90deg, #6366f1 0%, #1e3c72 100%);
        color: #fff;
        border-radius: 8px;
        padding: 0.2em 0.7em;
        font-size: 0.95em;
        margin-left: 0.7em;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .image-card {
        background: #fff;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(30,60,114,0.10);
        padding: 1em;
        margin-bottom: 1.2em;
        text-align: center;
        transition: box-shadow 0.2s;
        border: 2px solid #e0e7ff;
    }
    .image-card:hover {
        box-shadow: 0 8px 32px rgba(30,60,114,0.18);
        border: 2px solid #6366f1;
    }
    .image-link {
        font-size: 0.95em;
        color: #6366f1;
        margin: 0 0.2em;
        text-decoration: none;
    }
    .image-link:hover {
        color: #1e3c72;
        text-decoration: underline;
    }
    .footer {
        text-align: center;
        color: #6366f1;
        margin-top: 2em;
        font-size: 1.1em;
        opacity: 0.8;
    }
    .stButton>button {
        color: white;
        background: linear-gradient(90deg, #6366f1 0%, #1e3c72 100%);
        border-radius: 8px;
        padding: 0.5em 1.5em;
        font-weight: bold;
        font-size: 1.1em;
        margin: 0.2em 0.5em 0.2em 0;
        border: none;
        box-shadow: 0 2px 8px rgba(30,60,114,0.1);
        transition: 0.2s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #1e3c72 0%, #6366f1 100%);
        color: #ffd700;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1.5px solid #6366f1;
        padding: 0.5em;
    }
    .stFileUploader>div>div {
        border-radius: 8px;
        border: 1.5px solid #6366f1;
        background: #f5f7fa;
    }
    .stAlert {
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar ---
st.sidebar.image("https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png", width=70)
st.sidebar.markdown("<h2 style='color:#1e3c72;'>GitHub Image Storage</h2>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style='font-size:1.1em;'>
Easily use <b>GitHub branches as buckets</b> for your images.<br>
Create, switch, or delete buckets.<br>
Upload, view, and share images.<br>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("### ➕ <span style='color:#6366f1;'>Create or Switch Bucket</span>", unsafe_allow_html=True)
bucket = st.sidebar.text_input('Bucket name (branch):', help="Type a new or existing branch name.")
if st.sidebar.button("Create/Switch", use_container_width=True):
    repo = Repo(REPO_PATH)
    branches = [b.name for b in repo.branches if b.name != 'main']
    if bucket:
        if bucket in branches:
            try:
                repo.git.checkout(bucket)
                st.sidebar.success(f"Switched to bucket: {bucket}")
                st.rerun()
            except GitCommandError as e:
                st.sidebar.error(f"Error switching branch: {e}")
        else:
            try:
                new_branch = repo.create_head(bucket)
                repo.git.checkout(bucket)
                st.sidebar.success(f"Created and switched to new bucket: {bucket}")
                st.rerun()
            except GitCommandError as e:
                st.sidebar.error(f"Error creating/switching branch: {e}")
    else:
        st.sidebar.info('Please enter a bucket name to continue.')
st.sidebar.markdown("---")
st.sidebar.markdown("<div style='font-size:1em; color:#6366f1;'>Built with ❤️ using Streamlit, GitPython, and GitHub</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='font-size:0.95em;'><a href='https://github.com/aadarsh-nagrath/github-storage' target='_blank'>View Source on GitHub</a></div>", unsafe_allow_html=True)

repo = Repo(REPO_PATH)
branches = [b.name for b in repo.branches if b.name != 'main']
current_branch = repo.active_branch.name if repo.head.is_valid() else None

st.markdown("<h1 style='text-align:center; color:#1e3c72; margin-bottom:0.5em;'>🗂️ GitHub Image Storage <span style='color:#6366f1;'>Buckets</span> UI</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#6366f1; font-size:1.2em; margin-bottom:2em;'>Manage your image buckets with style!</div>", unsafe_allow_html=True)

# --- List all branches (buckets) ---
st.markdown("### 🪣 <span style='color:#6366f1;'>Your Buckets</span>", unsafe_allow_html=True)
if branches:
    for branch in branches:
        with st.container():
            cols = st.columns([3, 1, 1])
            branch_icon = '🔵' if branch == current_branch else '⚪️'
            current_label = "<span class='current-badge'>Current</span>" if branch == current_branch else ""
            branch_html = f"<span style='font-size:1.1em;'>{branch_icon} <b>{branch}</b> {current_label}</span>"
            cols[0].markdown(branch_html, unsafe_allow_html=True)
            if branch != current_branch:
                if cols[1].button(f"🌈 Switch", key=f"switch_{branch}"):
                    try:
                        repo.git.checkout(branch)
                        st.success(f"Switched to bucket: {branch}")
                        st.rerun()
                    except GitCommandError as e:
                        st.error(f"Error switching branch: {e}")
                if cols[2].button(f"🗑️ Delete", key=f"delete_{branch}"):
                    try:
                        repo.git.branch('-D', branch)
                        repo.git.push('origin', '--delete', branch)
                        st.success(f"Deleted bucket: {branch}")
                        st.rerun()
                    except GitCommandError as e:
                        st.error(f"Error deleting branch: {e}")
else:
    st.info('No buckets (branches) found.')

# --- Always show image operations for current branch ---
if current_branch:
    os.makedirs(STORAGE_DIR, exist_ok=True)
    st.markdown(f"<h3 style='color:#6366f1;'>🖼️ Images in <b>{current_branch}</b></h3>", unsafe_allow_html=True)
    # --- Image Upload ---
    with st.expander("📤 <b>Upload an image</b>", expanded=True):
        uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "gif"])
        if uploaded_file is not None:
            image_path = os.path.join(STORAGE_DIR, uploaded_file.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            # Show the image immediately
            st.image(image_path, caption=f"Just uploaded: {uploaded_file.name}", width=220)
            # Add, commit, and push
            repo.git.add(image_path)
            repo.index.commit(f"Add image {uploaded_file.name} to bucket {current_branch}")
            try:
                repo.git.pull('origin', current_branch, '--rebase')
                repo.git.push('origin', current_branch)
                st.success(f"Uploaded and pushed {uploaded_file.name}")
                st.rerun()
            except GitCommandError as e:
                st.error(f"Push failed: {e}")
    # --- List Images ---
    images = [f for f in os.listdir(STORAGE_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
    if images:
        st.markdown("#### <span style='color:#6366f1;'>🖼️ Gallery</span>", unsafe_allow_html=True)
        # Grid layout for images
        cols = st.columns(3)
        for idx, img_name in enumerate(images):
            with cols[idx % 3]:
                st.markdown(f"<div class='image-card'>", unsafe_allow_html=True)
                img_path = os.path.join(STORAGE_DIR, img_name)
                st.image(img_path, caption=img_name, width=220)
                github_url = f"https://github.com/aadarsh-nagrath/github-storage/blob/{current_branch}/storage/{img_name}"
                raw_url = f"https://raw.githubusercontent.com/aadarsh-nagrath/github-storage/refs/heads/{current_branch}/storage/{img_name}"
                st.markdown(f"<a class='image-link' href='{github_url}' target='_blank' title='View on GitHub'>🌐 GitHub</a> | <a class='image-link' href='{raw_url}' target='_blank' title='Direct Image Link'>🖼️ Raw</a>", unsafe_allow_html=True)
                if st.button(f"🗑️", key=f"del_{img_name}", help="Delete this image"):
                    os.remove(img_path)
                    repo.git.add(img_path)
                    repo.index.commit(f"Delete image {img_name} from bucket {current_branch}")
                    try:
                        repo.git.pull('origin', current_branch, '--rebase')
                        repo.git.push('origin', current_branch)
                        st.success(f"Deleted and pushed {img_name}")
                        # Remove from UI immediately
                        st.toast(f"Deleted {img_name}", icon="🗑️")
                        st.rerun()
                    except GitCommandError as e:
                        st.error(f"Push failed: {e}")
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No images found in this bucket.")
else:
    st.info('No bucket selected. Use the sidebar to create or switch buckets.')

# --- Footer ---
st.markdown("<div class='footer'>Made with <span style='color:#ffd700;'>★</span> by <a href='https://github.com/aadarsh-nagrath' target='_blank'>aadarsh-nagrath</a> | <a href='https://github.com/aadarsh-nagrath/github-storage' target='_blank'>GitHub Storage Repo</a></div>", unsafe_allow_html=True) 