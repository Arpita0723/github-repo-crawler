# 🔎 GitHub Repo Crawler

A simple Streamlit-based tool that allows you to fetch and download all `.py` files from any public GitHub repository — directly from a user-friendly web interface!

---

## ✨ Features

- ✅ Enter any public GitHub repo URL
- 📁 Recursively fetches all Python files in subfolders
- 💾 Saves files locally, preserving directory structure
- 🌐 Clean, Streamlit-powered UI

---

## 🛠 Tech Stack

- Python 3.10+
- Streamlit
- GitHub REST API
- `requests`, `os`, `json`, `urllib.parse`

---

## 🚀 How to Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/Arpita0723/github-repo-crawler.git
cd github-repo-crawler

# 2. Create virtual environment (optional but recommended)
python -m venv .venv
.\.venv\Scripts\activate        # On Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
