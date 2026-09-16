"""Render self-contained profile cards using only the Python standard library."""

import argparse
import base64
from datetime import datetime, timedelta, timezone
from html import escape, unescape
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

OWNER = "RobyRew"
SPOTIFY_USER = "gwiw7i4a2ha0a8dbldyn94vwl"
SPOTIFY_URL = "https://spotify-github-profile.kittinanx.com/api/view?" + urlencode({
    "uid": SPOTIFY_USER, "theme": "novatorem", "cover_image": "true",
    "show_offline": "true", "interchange": "false",
})
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"


def fetch(url, *, github=False):
    headers = {"User-Agent": "RobyRew-profile"}
    if github:
        headers["Accept"] = "application/vnd.github+json"
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, headers=headers), timeout=20) as response:
        payload = response.read(2_000_001)
        if len(payload) > 2_000_000:
            raise ValueError("Response exceeds the card size limit")
        return payload


def public_projects():
    repos = []
    page = 1
    while True:
        batch = json.loads(fetch(
            f"https://api.github.com/users/{OWNER}/repos?type=owner&per_page=100&page={page}",
            github=True,
        ))
        if not isinstance(batch, list):
            raise ValueError("GitHub did not return a repository list")
        repos.extend(repo for repo in batch if not repo["fork"]
                     and not repo["private"] and repo["name"].lower() != OWNER.lower())
        if len(batch) < 100:
            return repos
        page += 1


def text(x, y, value, size=16, color="#f4f1eb", **attrs):
    options = " ".join(f'{key.replace("_", "-")}="{escape(str(value), quote=True)}"'
                       for key, value in attrs.items())
    return (f'<text x="{x}" y="{y}" fill="{color}" font-family="{FONT}" '
            f'font-size="{size}" {options}>{escape(str(value))}</text>')


def card(title, content, height):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="{height}" '
            f'viewBox="0 0 600 {height}" role="img" aria-labelledby="title">\n'
            f'<title id="title">{escape(title)}</title>\n'
            f'<rect x="0.5" y="0.5" width="599" height="{height-1}" rx="10" '
            'fill="#171c21" stroke="#343b43"/>\n' + "\n".join(content) + "\n</svg>\n")


def stats_svg(repos, now):
    recent = sum(now - timedelta(days=90) <= datetime.fromisoformat(
        repo["pushed_at"].replace("Z", "+00:00")) <= now for repo in repos if repo.get("pushed_at"))
    metrics = [(len(repos), "public projects"),
               (sum(repo["stargazers_count"] for repo in repos), "stars earned"),
               (recent, "updated in 90 days")]
    content = [text(24, 30, "ON GITHUB", 12, "#ee9972", letter_spacing=1.5),
               text(576, 30, now.strftime("%d %b %Y"), 12, "#b8bec5", text_anchor="end")]
    for x, (value, label) in zip((24, 210, 396), metrics):
        content += [text(x, 84, value, 38, font_weight=600),
                    text(x, 111, label, 16, "#b8bec5")]
    content += ['<path d="M24 132h552" stroke="#343b43"/>',
                text(24, 157, "Public, non-fork repositories. This profile is excluded.", 12, "#b8bec5")]
    return card("GitHub: " + ", ".join(f"{v} {label}" for v, label in metrics), content, 178)


def parse_spotify(payload):
    # Never publish upstream markup, scripts or remote image references.
    if b"<!DOCTYPE" in payload.upper() or b"<!ENTITY" in payload.upper():
        raise ValueError("Unexpected XML declarations")
    root = ET.fromstring(payload)
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("Spotify returned a page instead of an SVG")
    fields = {}
    cover = None
    for element in root.iter():
        classes = element.get("class", "").split()
        for field in ("song", "artist"):
            if field in classes and field not in fields:
                fields[field] = unescape("".join(element.itertext()).strip())
        if "cover" in classes:
            source = element.get("src", "")
            if source.startswith(("data:image/png;base64,", "data:image/jpeg;base64,")):
                prefix, encoded = source.split(",", 1)
                encoded = "".join(encoded.split())
                base64.b64decode(encoded, validate=True)
                cover = prefix + "," + encoded
    if not fields.get("song") or not fields.get("artist"):
        raise ValueError("Spotify song or artist fields are missing")
    if fields["artist"] == "Offline":
        return None
    return fields["song"], fields["artist"], cover


def shorten(value, limit):
    return value if len(value) <= limit else value[:limit - 1].rstrip() + "…"


def spotify_svg(track, now):
    content = [text(124, 30, "SPOTIFY", 12, "#1ed760", font_weight=600, letter_spacing=1.5)]
    if track:
        song, artist, cover = track
        content += [text(124, 67, shorten(song, 33), 22, font_weight=600),
                    text(124, 94, shorten(artist, 45), 16, "#b8bec5"),
                    text(124, 130, now.strftime("Captured %d %b %Y · %H:%M UTC"), 12, "#b8bec5")]
        title = f"Spotify listening snapshot: {song} by {artist}. Captured {now:%d %b %Y %H:%M UTC}."
    else:
        cover = None
        content += [text(124, 67, "Find me on Spotify", 22, font_weight=600),
                    text(124, 94, "The music behind the commits.", 16, "#b8bec5"),
                    text(124, 130, "Open profile ↗", 14, "#1ed760")]
        title = "RobyRew on Spotify. Playback is unavailable; open the Spotify profile."
    if cover:
        content += ['<defs><clipPath id="cover"><rect x="24" y="35" width="80" height="80" rx="6"/></clipPath></defs>',
                    f'<image x="24" y="35" width="80" height="80" clip-path="url(#cover)" href="{escape(cover, quote=True)}"/>']
    else:
        content += ['<rect x="24" y="35" width="80" height="80" rx="8" fill="#20372a"/>',
                    '<circle cx="64" cy="75" r="24" fill="#1ed760"/>',
                    '<g fill="none" stroke="#171c21" stroke-linecap="round">',
                    '<path d="M48 68q17-8 33 2" stroke-width="4"/>',
                    '<path d="M50 76q14-7 28 2" stroke-width="3.5"/>',
                    '<path d="M52 84q12-5 23 1" stroke-width="3"/></g>']
    return card(title, content, 154)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("build/profile"))
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    # A GitHub outage fails the run before either published asset can change.
    stats = stats_svg(public_projects(), now)
    try:
        track = parse_spotify(fetch(SPOTIFY_URL))
    except (OSError, ValueError, ET.ParseError):
        print("::warning::Spotify playback unavailable. Using the profile card. "
              "If authorization expired, reconnect at https://spotify-github-profile.kittinanx.com/api/login")
        track = None
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "stats.svg").write_text(stats, encoding="utf-8")
    (args.output / "spotify.svg").write_text(spotify_svg(track, now), encoding="utf-8")
    print(f"Rendered profile cards in {args.output}")


if __name__ == "__main__":
    main()
