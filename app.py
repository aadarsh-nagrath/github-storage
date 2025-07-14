import streamlit as st
from git import Repo, GitCommandError
import os
from PIL import Image
import shutil

# Path to the local git repo (assume cloned in /app/repo)
REPO_PATH = os.getenv('REPO_PATH', './repo')
STORAGE_DIR = os.path.join(REPO_PATH, 'storage')

# --- Custom CSS for modern look with enhanced animations and detailing ---
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #e0e7ff 0%, #f5f7fa 100%);
        animation: gradientFade 15s ease infinite;
    }
    @keyframes gradientFade {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .main {
        background: transparent !important;
    }
    .bucket-card {
        background: #fff;
        border-radius: 20px;
        box-shadow: 0 6px 24px rgba(30,60,114,0.1);
        padding: 1.5em;
        margin-bottom: 1.5em;
        transition: all 0.3s ease;
        border: 2px solid #e0e7ff;
        position: relative;
        overflow: hidden;
    }
    .bucket-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, rgba(99,102,241,0.1), rgba(30,60,114,0.05));
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .bucket-card:hover::before {
        opacity: 1;
    }
    .bucket-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(30,60,114,0.2);
        border: 2px solid #6366f1;
    }
    .current-badge {
        background: linear-gradient(90deg, #6366f1 0%, #1e3c72 100%);
        color: #fff;
        border-radius: 10px;
        padding: 0.3em 0.8em;
        font-size: 0.95em;
        margin-left: 0.8em;
        font-weight: 600;
        letter-spacing: 0.5px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .image-card {
        background: #fff;
        border-radius: 20px;
        box-shadow: 0 4px 16px rgba(30,60,114,0.12);
        padding: 1.2em;
        margin-bottom: 1.5em;
        text-align: center;
        transition: all 0.3s ease;
        border: 2px solid #e0e7ff;
        position: relative;
        overflow: hidden;
    }
    .image-card:hover {
        transform: scale(1.03);
        box-shadow: 0 12px 40px rgba(30,60,114,0.2);
        border: 2px solid #6366f1;
    }
    .image-card::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(99,102,241,0.1), transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .image-card:hover::after {
        opacity: 1;
    }
    .image-link {
        font-size: 0.95em;
        color: #6366f1;
        margin: 0 0.3em;
        text-decoration: none;
        transition: all 0.2s ease;
    }
    .image-link:hover {
        color: #1e3c72;
        text-decoration: underline;
        transform: translateY(-2px);
    }
    .footer {
        text-align: center;
        color: #6366f1;
        margin-top: 2.5em;
        font-size: 1.2em;
        opacity: 0.9;
        animation: fadeInUp 1s ease-out;
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 0.9; transform: translateY(0); }
    }
    .stButton>button {
        color: white;
        background: linear-gradient(90deg, #6366f1 0%, #1e3c72 100%);
        border-radius: 10px;
        padding: 0.6em 1.8em;
        font-weight: bold;
        font-size: 1.15em;
        margin: 0.3em 0.6em 0.3em 0;
        border: none;
        box-shadow: 0 4px 12px rgba(30,60,114,0.15);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #1e3c72 0%, #6366f1 100%);
        color: #ffd700;
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(30,60,114,0.25);
    }
    .stButton>button::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: 0.5s;
    }
    .stButton>button:hover::after {
        left: 100%;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #6366f1;
        padding: 0.6em;
        transition: all 0.2s ease;
    }
    .stTextInput>div>div>input:focus {
        box-shadow: 0 0 8px rgba(99,102,241,0.3);
        border-color: #1e3c72;
    }
    .stFileUploader>div>div {
        border-radius: 10px;
        border: 2px solid #6366f1;
        background: #f5f7fa;
        transition: all 0.2s ease;
    }
    .stFileUploader:hover {
        box-shadow: 0 0 8px rgba(99,102,241,0.3);
    }
    .stAlert {
        border-radius: 10px;
        animation: slideIn 0.5s ease-out;
    }
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    .st-expander {
        border-radius: 12px;
        border: 2px solid #e0e7ff;
        transition: all 0.3s ease;
    }
    .st-expander:hover {
        border-color: #6366f1;
        box-shadow: 0 4px 16px rgba(30,60,114,0.1);
    }
    .sidebar .stImage {
        transition: transform 0.3s ease;
    }
    .sidebar .stImage:hover {
        transform: rotate(360deg);
    }
    .stButton > button[kind="secondary"] {
        background: #ff4b4b !important;
        color: #fff !important;
        border-radius: 10px;
        font-weight: bold;
        font-size: 1.1em;
        box-shadow: 0 4px 12px rgba(255,75,75,0.15);
        transition: all 0.3s ease;
    }
    .stButton > button[kind="secondary"]:hover {
        background: #d90429 !important;
        color: #fff !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(255,75,75,0.25);
    }
    #delete_selected_bucket {
        background: #ff4b4b !important;
        color: #fff !important;
        border-radius: 10px;
        font-weight: bold;
        font-size: 1.1em;
        box-shadow: 0 4px 12px rgba(255,75,75,0.15);
        transition: all 0.3s ease;
    }
    #delete_selected_bucket:hover {
        background: #d90429 !important;
        color: #fff !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(255,75,75,0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar ---
st.sidebar.image("https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png", width=70)
st.sidebar.markdown("<h2 style='color:#1e3c72; animation: fadeIn 1s ease-out;'>GitHub Image Storage</h2>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style='font-size:1.1em; animation: fadeInUp 1s ease-out;'>
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
    # List remote branches for existence check
    repo.git.fetch('--all')
    remote_branches = []
    for ref in repo.git.branch('-r').splitlines():
        ref = ref.strip()
        if '->' in ref or ref == 'origin/main':
            continue
        if ref.startswith('origin/'):
            remote_branches.append(ref.replace('origin/', ''))
    if bucket:
        if bucket in remote_branches:
            try:
                if bucket not in [b.name for b in repo.branches]:
                    repo.git.checkout('-b', bucket, f'origin/{bucket}')
                else:
                    repo.git.checkout(bucket)
                st.sidebar.success(f"Switched to bucket: {bucket}")
                st.rerun()
            except GitCommandError as e:
                st.sidebar.error(f"Error switching branch: {e}")
        else:
            try:
                new_branch = repo.create_head(bucket, 'origin/main')
                repo.git.checkout(bucket)
                # Push new branch to origin so it appears in dropdown
                repo.git.push('--set-upstream', 'origin', bucket)
                st.sidebar.success(f"Created and switched to new bucket: {bucket}")
                st.rerun()
            except GitCommandError as e:
                st.sidebar.error(f"Error creating/switching branch: {e}")
    else:
        st.sidebar.info('Please enter a bucket name to continue.')
st.sidebar.markdown("---")
st.sidebar.markdown("<div style='font-size:1em; color:#6366f1; animation: fadeInUp 1s ease-out;'>Built with ❤️ using Streamlit, GitPython, and GitHub</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='font-size:0.95em;'><a href='https://github.com/aadarsh-nagrath/github-storage' target='_blank'>View Source on GitHub</a></div>", unsafe_allow_html=True)

# Always refresh repo and branches before rendering
repo = Repo(REPO_PATH)
all_branches = [b.name for b in repo.branches if b.name != 'main']
current_branch = repo.active_branch.name if repo.head.is_valid() else None

# --- Ensure all remote branches are available locally (except main) ---
repo = Repo(REPO_PATH)
repo.git.fetch('--all')
for ref in repo.git.branch('-r').splitlines():
    ref = ref.strip()
    if '->' in ref:
        continue  # skip symbolic refs
    if ref.startswith('origin/') and ref != 'origin/main':
        branch_name = ref.replace('origin/', '')
        if branch_name not in repo.branches:
            repo.git.checkout('-b', branch_name, ref)

# --- List all remote branches (buckets) ---
repo = Repo(REPO_PATH)
repo.git.fetch('--all')
remote_branches = []
for ref in repo.git.branch('-r').splitlines():
    ref = ref.strip()
    if '->' in ref or ref == 'origin/main':
        continue
    if ref.startswith('origin/'):
        remote_branches.append(ref.replace('origin/', ''))

current_branch = repo.active_branch.name if repo.head.is_valid() else None

# --- Bucket selection ---
if remote_branches:
    bucket_col1, bucket_col2 = st.columns([4, 1])
    selected_bucket = bucket_col1.selectbox(
        'Select a bucket to view images:',
        options=remote_branches,
        index=remote_branches.index(current_branch) if current_branch in remote_branches else 0,
        key='bucket_select',
    )
    # Red delete button for selected bucket
    delete_btn = bucket_col2.button('🗑️ Delete Bucket', key='delete_selected_bucket', help='Delete this bucket', use_container_width=True)
    if delete_btn:
        try:
            # If the selected bucket is checked out, switch to main first
            if selected_bucket == current_branch:
                repo.git.checkout('main')
            # Remove local branch if exists
            if selected_bucket in [b.name for b in repo.branches]:
                repo.git.branch('-D', selected_bucket)
            # Remove remote branch
            repo.git.push('origin', '--delete', selected_bucket)
            st.success(f"Deleted bucket: {selected_bucket}")
            st.rerun()
        except GitCommandError as e:
            st.error(f"Error deleting bucket: {e}")
else:
    selected_bucket = None

st.markdown("<h1 style='text-align:center; color:#1e3c72; margin-bottom:0.5em; animation: fadeInDown 1s ease-out;'>🗂️ GitHub Image Storage <span style='color:#6366f1;'>Buckets</span> UI</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#6366f1; font-size:1.2em; margin-bottom:2em; animation: fadeInUp 1s ease-out;'>Manage your image buckets with style!</div>", unsafe_allow_html=True)

# --- List all branches (buckets) ---
st.markdown("### 🪣 <span style='color:#6366f1; animation: fadeIn 0.8s ease-out;'>Your Buckets</span>", unsafe_allow_html=True)
if remote_branches:
    for branch in remote_branches:
        with st.container():
            branch_icon = '🔵' if branch == current_branch else '⚪️'
            current_label = "<span class='current-badge'>Current</span>" if branch == current_branch else ""
            branch_html = f"<span style='font-size:1.1em;'>{branch_icon} <b>{branch}</b> {current_label}</span>"
            st.markdown(branch_html, unsafe_allow_html=True)
else:
    st.info('No buckets (branches) found.')

# --- Always show image operations for selected bucket ---
if selected_bucket:
    # Save the current branch to switch back after operation
    original_branch = repo.active_branch.name if repo.head.is_valid() else None
    # Check out the selected branch locally if not already
    if selected_bucket not in [b.name for b in repo.branches]:
        repo.git.checkout('-b', selected_bucket, f'origin/{selected_bucket}')
    else:
        repo.git.checkout(selected_bucket)
    os.makedirs(STORAGE_DIR, exist_ok=True)
    st.markdown(f"<h3 style='color:#6366f1; animation: fadeIn 0.8s ease-out;'>🖼️ Images in <b>{selected_bucket}</b></h3>", unsafe_allow_html=True)
    # --- Image Upload (now for any bucket) ---
    with st.expander("📤 <b>Upload an image</b>", expanded=True):
        uploaded_file = st.file_uploader(f"Upload an image to {selected_bucket}", type=["png", "jpg", "jpeg", "gif"], key=f"uploader_{selected_bucket}")
        if uploaded_file is not None:
            image_path = os.path.join(STORAGE_DIR, uploaded_file.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            # Show the image immediately
            st.image(image_path, caption=f"Just uploaded: {uploaded_file.name}", width=220)
            # Add, commit, and push
            repo.git.add(image_path)
            repo.index.commit(f"Add image {uploaded_file.name} to bucket {selected_bucket}")
            try:
                repo.git.pull('origin', selected_bucket, '--rebase')
                repo.git.push('origin', selected_bucket)
                st.success(f"Uploaded and pushed {uploaded_file.name}")
                # Add to images list for immediate gallery display
                images = [f for f in os.listdir(STORAGE_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
                if uploaded_file.name not in images:
                    images.append(uploaded_file.name)
                # Switch back to original branch if needed
                if original_branch and original_branch != selected_bucket:
                    repo.git.checkout(original_branch)
                st.rerun()
            except GitCommandError as e:
                st.error(f"Push failed: {e}")
                if original_branch and original_branch != selected_bucket:
                    repo.git.checkout(original_branch)
    # --- List Images ---
    images = [f for f in os.listdir(STORAGE_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
    if images:
        st.markdown("#### <span style='color:#6366f1; animation: fadeIn 0.8s ease-out;'>🖼️ Gallery</span>", unsafe_allow_html=True)
        # Grid layout for images
        cols = st.columns(3)
        for idx, img_name in enumerate(images):
            with cols[idx % 3]:
                st.markdown(f"<div class='image-card'>", unsafe_allow_html=True)
                img_path = os.path.join(STORAGE_DIR, img_name)
                st.image(img_path, caption=img_name, width=220)
                github_url = f"https://github.com/aadarsh-nagrath/github-storage/blob/{selected_bucket}/storage/{img_name}"
                raw_url = f"https://raw.githubusercontent.com/aadarsh-nagrath/github-storage/refs/heads/{selected_bucket}/storage/{img_name}"
                st.markdown(f"<a class='image-link' href='{github_url}' target='_blank' title='View on GitHub'>🌐 GitHub</a> | <a class='image-link' href='{raw_url}' target='_blank' title='Direct Image Link'>🖼️ Raw</a>", unsafe_allow_html=True)
                if st.button(f"🗑️", key=f"del_{selected_bucket}_{img_name}", help="Delete this image"):
                    os.remove(img_path)
                    repo.git.add(img_path)
                    repo.index.commit(f"Delete image {img_name} from bucket {selected_bucket}")
                    try:
                        repo.git.pull('origin', selected_bucket, '--rebase')
                        repo.git.push('origin', selected_bucket)
                        st.success(f"Deleted and pushed {img_name}")
                        st.toast(f"Deleted {img_name}", icon="🗑️")
                        # Switch back to original branch if needed
                        if original_branch and original_branch != selected_bucket:
                            repo.git.checkout(original_branch)
                        st.rerun()
                    except GitCommandError as e:
                        st.error(f"Push failed: {e}")
                        if original_branch and original_branch != selected_bucket:
                            repo.git.checkout(original_branch)
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No images found in this bucket.")
    # Switch back to original branch after listing images
    if original_branch and original_branch != selected_bucket:
        repo.git.checkout(original_branch)
else:
    st.info('No bucket selected. Use the sidebar to create or switch buckets.')

# --- Footer ---
st.markdown("<div class='footer'>Made with <span style='color:#ffd700;'>★</span> by <a href='https://github.com/aadarsh-nagrath' target='_blank'>aadarsh-nagrath</a> | <a href='https://github.com/aadarsh-nagrath/github-storage' target='_blank'>GitHub Storage Repo</a></div>", unsafe_allow_html=True)