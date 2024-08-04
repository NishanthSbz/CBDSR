import streamlit as st
import requests
import base64

# GitHub configuration
# GITHUB_TOKEN = ''  Replace with your GitHub PAT
MAIN_REPO = 'NishanthSbz/Main_storage'  # Replace with your GitHub username and repository for main storage
BACKUP_REPO = 'NishanthSbz/Backup_repo'  # Replace with your GitHub username and repository for backup storage

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def upload_to_github(file, repo, path):
    try:
        url = f"https://api.github.com/repos/{repo}/contents/{path}/{file.name}"
        content = base64.b64encode(file.getvalue()).decode()
        data = {
            "message": f"Add {file.name}",
            "content": content
        }
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['content']['path']
    except Exception as e:
        st.error(f"Failed to upload to GitHub: {e}")
        return None

def list_files_in_github(repo, path):
    try:
        url = f"https://api.github.com/repos/{repo}/contents/{path}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        files = response.json()
        return [file['name'] for file in files if file['type'] == 'file']
    except Exception as e:
        st.error(f"Failed to list files in GitHub: {e}")
        return []

def delete_from_github(repo, path, file_name):
    try:
        url = f"https://api.github.com/repos/{repo}/contents/{path}/{file_name}"
        get_file_response = requests.get(url, headers=headers)
        get_file_response.raise_for_status()
        sha = get_file_response.json()['sha']
        data = {
            "message": f"Delete {file_name}",
            "sha": sha
        }
        delete_response = requests.delete(url, headers=headers, json=data)
        delete_response.raise_for_status()
    except Exception as e:
        st.error(f"Failed to delete file from GitHub: {e}")

# Streamlit UI
st.title("CLOUD-BASED DISASTER RECOVERY SYSTEM")

# Input GitHub repository paths for main and backup storage
main_repo_path = st.text_input("Main Repository Path:", MAIN_REPO)
backup_repo_path = st.text_input("Backup Repository Path:", BACKUP_REPO)

if main_repo_path and backup_repo_path:
    # File uploader
    uploaded_file = st.file_uploader("Choose a file to upload")

    if uploaded_file is not None:
        # Save file to main and backup GitHub repositories
        main_path = upload_to_github(uploaded_file, main_repo_path, 'main')
        backup_path = upload_to_github(uploaded_file, backup_repo_path, 'backup')

        if main_path and backup_path:
            st.success(f"File '{uploaded_file.name}' has been uploaded to both main and backup repositories.")

    # Display files in main repository
    st.subheader("Files in Main Repository")
    main_files = list_files_in_github(main_repo_path, 'main')
    for file_name in main_files:
        st.write(file_name)
        if st.button(f"Delete from Main Repository: {file_name}", key=f"delete_main_{file_name}"):
            delete_from_github(main_repo_path, 'main', file_name)
            st.warning(f"File '{file_name}' deleted from main repository but remains in backup repository.")

    # Display files in backup repository
    st.subheader("Files in Backup Repository")
    backup_files = list_files_in_github(backup_repo_path, 'backup')
    for file_name in backup_files:
        st.write(file_name)
else:
    st.error("Please provide both main and backup repository paths.")
