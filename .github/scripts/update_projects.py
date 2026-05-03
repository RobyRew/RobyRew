import urllib.request
import json
import re
import os

token = os.environ.get("GITHUB_TOKEN", "")
username = "RobyRew"

headers = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "readme-updater",
}
if token:
    headers["Authorization"] = f"Bearer {token}"

url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=20&type=public"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as resp:
    repos = json.loads(resp.read().decode())

# Drop forks, sort by stars desc then last updated
repos = [r for r in repos if not r["fork"]]
repos.sort(key=lambda r: (-r["stargazers_count"], r["pushed_at"]), reverse=False)
repos.sort(key=lambda r: -r["stargazers_count"])
repos = repos[:6]

BASE = "https://github-readme-stats.vercel.app/api/pin/"
STYLE = "bg_color=0d1117&title_color=a78bfa&icon_color=a78bfa&text_color=c9d1d9&border_color=2d0a6e"

lines = ['<div align="center">\n\n']
for i in range(0, len(repos), 2):
    left = repos[i]
    right = repos[i + 1] if i + 1 < len(repos) else None
    left_url = f"{BASE}?username={username}&repo={left['name']}&{STYLE}"
    left_card = f'<a href="{left["html_url"]}"><img width="49%" src="{left_url}"/></a>'
    if right:
        right_url = f"{BASE}?username={username}&repo={right['name']}&{STYLE}"
        right_card = f'<a href="{right["html_url"]}"><img width="49%" src="{right_url}"/></a>'
        lines.append(f"{left_card}\n{right_card}\n\n")
    else:
        lines.append(f"{left_card}\n\n")

lines.append("</div>")
new_content = "".join(lines)

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

pattern = r"<!-- PROJECTS:START -->.*?<!-- PROJECTS:END -->"
replacement = f"<!-- PROJECTS:START -->\n{new_content}\n<!-- PROJECTS:END -->"
readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)

print("README updated successfully")
