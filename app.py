import streamlit as st
from git import Repo, GitCommandError
import os
from PIL import Image
import shutil

# Path to the local git repo (assume cloned in /app/repo)
REPO_PATH = os.getenv('REPO_PATH', './repo')
STORAGE_DIR = os.path.join(REPO_PATH, 'storage')

# --- Custom CSS for background and button styling ---
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .stButton>button {
        color: white;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
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
        background: linear-gradient(90deg, #2a5298 0%, #1e3c72 100%);
        color: #ffd700;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1.5px solid #2a5298;
        padding: 0.5em;
    }
    .stFileUploader>div>div {
        border-radius: 8px;
        border: 1.5px solid #2a5298;
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
st.sidebar.image("https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png", width=60)
st.sidebar.title("GitHub Image Storage")
st.sidebar.markdown("""
**Buckets = Branches**
- Create, switch, or delete buckets
- Upload, view, and delete images
- All images are stored in the `storage/` folder of each branch
""")
st.sidebar.info("Built with ❤️ using Streamlit, GitPython, and GitHub")

repo = Repo(REPO_PATH)
branches = [b.name for b in repo.branches if b.name != 'main']
current_branch = repo.active_branch.name if repo.head.is_valid() else None

# --- Create/Switch Bucket in Sidebar ---
st.sidebar.markdown("---")
st.sidebar.markdown("### ➕ Create or Switch Bucket")
bucket = st.sidebar.text_input('Enter bucket name (branch):', help="Type a new or existing branch name.")
if st.sidebar.button("Create/Switch", use_container_width=True):
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

st.markdown("<h1 style='text-align:center; color:#1e3c72;'>🗂️ GitHub Image Storage <span style='color:#2a5298;'>Buckets</span> UI</h1>", unsafe_allow_html=True)

# --- List all branches (buckets) ---
st.markdown("### 🪣 Existing Buckets")
if branches:
    for branch in branches:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            branch_icon = '🔵' if branch == current_branch else '⚪️'
            current_label = "<span style='color:#ffd700;'>(current)</span>" if branch == current_branch else ""
            branch_html = f"<span style='font-size:1.1em;'>{branch_icon} <b>{branch}</b> {current_label}</span>"
            st.markdown(branch_html, unsafe_allow_html=True)
        with col2:
            if branch != current_branch and branch != 'main' and st.button(f"🌈 Switch", key=f"switch_{branch}"):
                try:
                    repo.git.checkout(branch)
                    st.success(f"Switched to bucket: {branch}")
                    st.rerun()
                except GitCommandError as e:
                    st.error(f"Error switching branch: {e}")
        with col3:
            if branch != current_branch and branch != 'main' and st.button(f"🗑️ Delete", key=f"delete_{branch}"):
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
    st.markdown(f"<h3 style='color:#2a5298;'>🖼️ Images in <b>{current_branch}</b></h3>", unsafe_allow_html=True)
    # --- Image Upload ---
    with st.expander("📤 Upload an image", expanded=True):
        uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "gif"])
        if uploaded_file is not None:
            image_path = os.path.join(STORAGE_DIR, uploaded_file.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            # Add, commit, and push
            repo.git.add(image_path)
            repo.index.commit(f"Add image {uploaded_file.name} to bucket {current_branch}")
            try:
                repo.git.push('origin', current_branch)
                st.success(f"Uploaded and pushed {uploaded_file.name}")
                st.rerun()
            except GitCommandError as e:
                st.error(f"Push failed: {e}")
    # --- List Images ---
    images = [f for f in os.listdir(STORAGE_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
    if images:
        st.markdown("#### 🖼️ Images:")
        for img_name in images:
            img_path = os.path.join(STORAGE_DIR, img_name)
            with st.container():
                img_col, btn_col = st.columns([4, 1])
                with img_col:
                    st.image(img_path, caption=img_name, width=250)
                    # Show GitHub and raw URLs
                    github_url = f"https://github.com/aadarsh-nagrath/github-storage/blob/{current_branch}/storage/{img_name}"
                    raw_url = f"https://raw.githubusercontent.com/aadarsh-nagrath/github-storage/refs/heads/{current_branch}/storage/{img_name}"
                    st.markdown(f"[🌐 View on GitHub]({github_url})  ", unsafe_allow_html=True)
                    st.markdown(f"[🖼️ Direct Image Link]({raw_url})", unsafe_allow_html=True)
                with btn_col:
                    if st.button(f"🗑️ Delete {img_name}", key=img_name):
                        os.remove(img_path)
                        repo.git.add(img_path)
                        repo.index.commit(f"Delete image {img_name} from bucket {current_branch}")
                        try:
                            repo.git.push('origin', current_branch)
                            st.success(f"Deleted and pushed {img_name}")
                            st.rerun()
                        except GitCommandError as e:
                            st.error(f"Push failed: {e}")
    else:
        st.info("No images found in this bucket.")
else:
    st.info('No bucket selected. Use the sidebar to create or switch buckets.') 