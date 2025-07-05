# 🕸️ GitHub Repo Crawler

A Streamlit app to crawl any public GitHub repository and **download all `.py` files** recursively. Get a clean zipped copy of all the Python files in seconds!

---

## 🚀 Live App

🔗 [Click here to use the app](https://yourname-yourrepo.streamlit.app)  
_(Replace with your actual Streamlit app link)_

---

## 📦 Features

- 🔍 Enter any public GitHub repo URL
- 🐍 Recursively finds all `.py` files (in folders/subfolders)
- 💾 Saves the files locally
- 📥 Provides CSV report of filenames
- 📦 One-click ZIP download of all files

---

## 🛠️ Technologies Used

- **Python**
- **Streamlit** – for building the UI
- **Requests** – for GitHub API calls
- **Pandas** – for tabular reporting
- **Zipfile / OS** – for file handling and compression

---

## 🧪 How It Works

1. Paste the URL of a public GitHub repository
2. The app fetches the repo contents via the GitHub API
3. Recursively crawls through folders to find `.py` files
4. Saves them locally inside a `downloaded_files/` folder
5. Zips the folder and lets you download it

---

## 🧰 Installation (Run Locally)

```bash
git clone https://github.com/yourusername/github-repo-crawler.git
cd github-repo-crawler
python -m venv .venv
.\.venv\Scripts\activate   # On Windows
pip install -r requirements.txt
streamlit run app.py
