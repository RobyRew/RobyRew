import urllib.request
import json
import re
import os
import html

token = os.environ.get("GITHUB_TOKEN", "")
username = "RobyRew"

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


def fetch_repo(name):
    url = f"https://api.github.com/repos/{username}/{name}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"Skipping {name}: {e}")
        return None


LANG_COLORS = {
    "Swift": "#F05138",
    "TypeScript": "#3178C6",
    "JavaScript": "#F7DF1E",
    "Python": "#3572A5",
    "HTML": "#E34C26",
    "CSS": "#563D7C",
    "Shell": "#89E051",
    "Dockerfile": "#384D54",
}

STAR_ICON = (
    '<path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 '
    ".416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 "
    "1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.872 6.374a.75.75 0 0 1 .416-1.28l"
    '4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"/>'
)
FORK_ICON = (
    '<path d="M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a'
    "2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 "
    "2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 "
    '1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 '
    '1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z"/>'
)


def make_svg(repo: dict) -> str:
    name = html.escape(repo["name"])
    desc = html.escape(repo.get("description") or "No description provided.")
    if len(desc) > 70:
        desc = desc[:67] + "…"
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    lang = repo.get("language") or ""
    lang_color = LANG_COLORS.get(lang, "#858585")
    lang_escaped = html.escape(lang)

    lang_block = ""
    if lang:
        lang_block = f"""
    <circle cx="15" cy="131" r="6" fill="{lang_color}"/>
    <text x="26" y="136" fill="#a9b1d6" font-size="12" font-family="'Segoe UI',sans-serif">{lang_escaped}</text>"""

    return f"""<svg width="400" height="155" viewBox="0 0 400 155"
     xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="GitHub repo: {name}">
  <rect width="400" height="155" rx="10" fill="#0d1117" stroke="#2d0a6e" stroke-width="1.5"/>

  <!-- repo icon -->
  <svg x="15" y="15" width="16" height="16" viewBox="0 0 16 16" fill="#a78bfa">
    <path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75
     0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714
     1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1
     1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8Z"/>
  </svg>

  <text x="38" y="28" fill="#a78bfa" font-size="14" font-weight="600"
        font-family="'Segoe UI',sans-serif">{name}</text>

  <text x="15" y="68" fill="#8b949e" font-size="12"
        font-family="'Segoe UI',sans-serif" width="370">{desc}</text>

  {lang_block}

  <!-- stars -->
  <svg x="{"120" if lang else "15"}" y="122" width="16" height="16" viewBox="0 0 16 16" fill="#8b949e">
    {STAR_ICON}
  </svg>
  <text x="{"140" if lang else "35"}" y="136" fill="#a9b1d6" font-size="12"
        font-family="'Segoe UI',sans-serif">{stars}</text>

  <!-- forks -->
  <svg x="{"170" if lang else "65"}" y="122" width="16" height="16" viewBox="0 0 16 16" fill="#8b949e">
    {FORK_ICON}
  </svg>
  <text x="{"190" if lang else "85"}" y="136" fill="#a9b1d6" font-size="12"
        font-family="'Segoe UI',sans-serif">{forks}</text>
</svg>"""


os.makedirs("img/pins", exist_ok=True)

repos = []
for name in FEATURED:
    data = fetch_repo(name)
    if data and not data.get("private"):
        repos.append(data)
        svg = make_svg(data)
        path = f"img/pins/{name}.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"Generated {path}")

# Build README section using local SVG files
lines = ['<div align="center">\n\n']
for i in range(0, len(repos), 2):
    left = repos[i]
    right = repos[i + 1] if i + 1 < len(repos) else None
    lname = left["name"]
    left_card = (
        f'<a href="https://github.com/{username}/{lname}">'
        f'<img width="49%" src="img/pins/{lname}.svg"/></a>'
    )
    if right:
        rname = right["name"]
        right_card = (
            f'<a href="https://github.com/{username}/{rname}">'
            f'<img width="49%" src="img/pins/{rname}.svg"/></a>'
        )
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

print(f"Done — {len(repos)} cards generated.")
