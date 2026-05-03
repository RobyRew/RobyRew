import urllib.request
import json
import re
import os

token = os.environ.get("GITHUB_TOKEN", "")
username = "RobyRew"

# Pinned repos — shown in this order, always
FEATURED = [
    "TopPresenter",
    "calendar-event-generator",
    "bibletype",
    "kingdomskids",
    "powerpoint-extractor",
    "chat-converter",
]

headers = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "readme-updater",
}
if token:
    headers["Authorization"] = f"Bearer {token}"

# Verify each repo exists and isn't private
def repo_exists(name):
    url = f"https://api.github.com/repos/{username}/{name}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return not data.get("private", True)
    except Exception:
        return False

repos = [r for r in FEATURED if repo_exists(r)]

BASE = "https://github-readme-stats.vercel.app/api/pin/"
STYLE = "bg_color=0d1117&title_color=a78bfa&icon_color=a78bfa&text_color=c9d1d9&border_color=2d0a6e&cache_seconds=86400"

lines = ['<div align="center">\n\n']
for i in range(0, len(repos), 2):
    left = repos[i]
    right = repos[i + 1] if i + 1 < len(repos) else None
    left_url = f"{BASE}?username={username}&repo={left}&{STYLE}"
    left_card = f'<a href="https://github.com/{username}/{left}"><img width="49%" src="{left_url}"/></a>'
    if right:
        right_url = f"{BASE}?username={username}&repo={right}&{STYLE}"
        right_card = f'<a href="https://github.com/{username}/{right}"><img width="49%" src="{right_url}"/></a>'
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

print(f"README updated with {len(repos)} repos: {', '.join(repos)}")
