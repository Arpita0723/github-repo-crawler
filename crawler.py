import requests
import os
import csv

# Step 1: Set the repo URL and base folder to save files
repo_url = "https://github.com/psf/requests"  
base_folder = "downloaded_files"

#  Step 2: Track saved file paths
saved_files = []

# Step 3: Convert GitHub URL to API URL
def get_github_api_url(repo_url):
    parts = repo_url.strip("/").split("/")
    owner, repo = parts[-2], parts[-1]
    return f"https://api.github.com/repos/{owner}/{repo}/contents", owner, repo

# Step 4: Recursive fetcher function
def fetch_files(api_url, path=""):
    full_url = f"{api_url}/{path}" if path else api_url
    response = requests.get(full_url)

    if response.status_code != 200:
        print(f"❌ Failed to access {full_url}")
        return

    items = response.json()

    for item in items:
        if item["type"] == "file" and item["name"].endswith(".py"):
            rel_path = os.path.join(base_folder, item["path"])
            os.makedirs(os.path.dirname(rel_path), exist_ok=True)
            content = requests.get(item["download_url"]).text

            with open(rel_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f" Saved: {item['path']}")
            saved_files.append(rel_path)

        elif item["type"] == "dir":
            fetch_files(api_url, item["path"])

# Step 5: Run the script and export to CSV
if __name__ == "__main__":
    print(" Crawling GitHub repo...\n")

    api_url, owner, repo = get_github_api_url(repo_url)
    fetch_files(api_url)

    # Save results to CSV
    with open("downloaded_files.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Filename"])
        for path in saved_files:
            writer.writerow([path])

    print("\n All .py files saved inside:", base_folder)
    print("📄 CSV report generated: downloaded_files.csv")

