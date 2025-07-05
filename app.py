import streamlit as st
import os
import requests

# 📁 Create folder if not exists
base_folder = "downloaded_files"
os.makedirs(base_folder, exist_ok=True)

# ── Streamlit Page Setup ─────────────────────────────────
st.set_page_config(page_title="GitHub Repo Crawler", layout="centered")
st.title("🔍 GitHub Repo Crawler")
st.write("Enter a public GitHub repo URL to download all `.py` files from it.")

# ── Input Section ────────────────────────────────────────
repo_url = st.text_input("🔗 Enter GitHub Repository URL:", "")

if repo_url:
    if st.button("🚀 Download .py Files"):
        with st.spinner("Crawling and downloading files..."):
            try:
                def get_github_api_url(repo_url):
                    parts = repo_url.strip("/").split("/")
                    owner, repo = parts[-2], parts[-1]
                    return f"https://api.github.com/repos/{owner}/{repo}/contents", owner, repo

                def fetch_files(api_url, current_path=""):
                    full_url = f"{api_url}/{current_path}" if current_path else api_url
                    response = requests.get(full_url)
                    if response.status_code != 200:
                        st.error(f"❌ Failed to access {current_path}")
                        return 0
                    
                    items = response.json()
                    count = 0

                    for item in items:
                        if item["type"] == "file" and item["name"].endswith(".py"):
                            rel_path = os.path.join(base_folder, item["path"])
                            os.makedirs(os.path.dirname(rel_path), exist_ok=True)
                            content = requests.get(item["download_url"]).text
                            with open(rel_path, "w", encoding="utf-8") as f:
                                f.write(content)
                            count += 1
                        elif item["type"] == "dir":
                            count += fetch_files(api_url, item["path"])
                    return count

                api_url, owner, repo = get_github_api_url(repo_url)
                total_files = fetch_files(api_url)
                st.success(f"✅ Downloaded {total_files} .py files from `{owner}/{repo}`!")
                                # ── Create File List Table ───────────────
                file_paths = []
                for root, _, files in os.walk(base_folder):
                    for name in files:
                        if name.endswith(".py"):
                            rel_path = os.path.relpath(os.path.join(root, name), base_folder)
                            file_paths.append({"S.No.": len(file_paths)+1, "File Path": rel_path})

                # ── Display in Table ──────────────────────
                st.markdown("### 📜 Downloaded Python Files")
                st.dataframe(file_paths, use_container_width=True)

                # ── Export to CSV ─────────────────────────
                import pandas as pd
                df = pd.DataFrame(file_paths)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download File List CSV",
                    data=csv,
                    file_name="downloaded_files.csv",
                    mime="text/csv",
                )


            except Exception as e:
                st.error(f"💥 Error: {str(e)}")
import zipfile

# ── Create ZIP File ──────────────────────────────
zip_filename = "downloaded_repo.zip"
zip_path = os.path.join(".", zip_filename)

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(base_folder):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, base_folder)
            zipf.write(full_path, arcname)

# ── Provide Download Button ──────────────────────
with open(zip_path, "rb") as f:
    st.download_button(
        label="📦 Download All Files as ZIP",
        data=f,
        file_name=zip_filename,
        mime="application/zip",
    )
           