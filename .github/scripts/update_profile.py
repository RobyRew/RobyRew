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


def text(x, y, value, size=16, color="#edf3f6", **attrs):
    options = " ".join(f'{key.replace("_", "-")}="{escape(str(value), quote=True)}"'
                       for key, value in attrs.items())
    return (f'<text x="{x}" y="{y}" fill="{color}" font-family="{FONT}" '
            f'font-size="{size}" {options}>{escape(str(value))}</text>')


def card(title, content, height, width=860, music=False):
    glow = "#6fc5a0" if music else "#91b1ca"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">\n'
            f'<title id="title">{escape(title)}</title>\n'
            '<defs>'
            '<linearGradient id="surface" x2="1" y2="1">'
            '<stop stop-color="#151d27"/><stop offset="1" stop-color="#0d121a"/></linearGradient>'
            f'<radialGradient id="glow" cx=".15" cy="0" r="1">'
            f'<stop stop-color="{glow}" stop-opacity=".10"/>'
            f'<stop offset="1" stop-color="{glow}" stop-opacity="0"/></radialGradient>'
            '<linearGradient id="edge" x2=".8" y2="1">'
            '<stop stop-color="#7a8b9a" stop-opacity=".45"/>'
            '<stop offset=".5" stop-color="#344353" stop-opacity=".4"/>'
            '<stop offset="1" stop-color="#7a8b9a" stop-opacity=".2"/></linearGradient>'
            '</defs>'
            f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="20" fill="url(#surface)"/>'
            f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="20" fill="url(#glow)" stroke="url(#edge)"/>\n'
            + "\n".join(content) + "\n</svg>\n")


def stats_svg(repos, now, compact=False):
    recent = sum(now - timedelta(days=90) <= datetime.fromisoformat(
        repo["pushed_at"].replace("Z", "+00:00")) <= now for repo in repos if repo.get("pushed_at"))
    metrics = [(len(repos), "public projects"),
               (sum(repo["stargazers_count"] for repo in repos), "stars earned"),
               (recent, "updated in 90 days")]
    width = 360 if compact else 860
    margin = 24 if compact else 34
    content = [text(margin, 31 if compact else 35, "PUBLIC WORK", 11, "#a8c5d4", letter_spacing=2),
               text(width - margin, 31 if compact else 35, now.strftime("%d %b %Y"), 11, "#8fa4b4", text_anchor="end")]
    labels = ("projects", "stars earned", "updated in 90d") if compact else tuple(label for _, label in metrics)
    columns = (24, 134, 244) if compact else (34, 316, 598)
    for x, (value, _), label in zip(columns, metrics, labels):
        content += [text(x, 88 if compact else 109, value, 38 if compact else 52, font_weight=400, letter_spacing=-1.5),
                    text(x, 114 if compact else 141, label, 11 if compact else 17, "#a8b8c7")]
    for x in ((119, 229) if compact else (281, 563)):
        content += [f'<path d="M{x} {60 if compact else 65}v{59 if compact else 86}" stroke="#b0c5d5" stroke-opacity=".12"/>']
    content += [text(margin, 155 if compact else 184,
                     "Public repos. Forks and this profile excluded." if compact else
                     "Original public repositories · forks and this profile excluded", 10 if compact else 12, "#8fa4b4")]
    return card("GitHub: " + ", ".join(f"{v} {label}" for v, label in metrics), content, 176 if compact else 206, width)


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


def spotify_svg(track, now, compact=False):
    width = 360 if compact else 860
    x = 120 if compact else 204
    content = [f'<defs><clipPath id="text"><rect x="{x}" y="17" width="{width-x-25}" height="112"/></clipPath></defs>',
               '<g clip-path="url(#text)">',
               text(x, 34 if compact else 42, "SPOTIFY", 11, "#7dd3ac", letter_spacing=2)]
    if track:
        song, artist, cover = track
        content += [text(x, 71 if compact else 89, shorten(song, 22 if compact else 39), 18 if compact else 30, font_weight=500, letter_spacing=-.5),
                    text(x, 99 if compact else 119, shorten(artist, 28 if compact else 55), 14 if compact else 18, "#a8b8c7"),
                    '</g>', text(24 if compact else x, 165 if compact else 175,
                                now.strftime("Captured %d %b %Y · %H:%M UTC"), 10 if compact else 12, "#8fa4b4")]
        title = f"Spotify listening snapshot: {song} by {artist}. Captured {now:%d %b %Y %H:%M UTC}."
    else:
        cover = None
        if compact:
            content += [text(x, 66, "Usually with", 22, font_weight=500, letter_spacing=-.5),
                        text(x, 96, "music on.", 22, font_weight=500, letter_spacing=-.5)]
        else:
            content += [text(x, 89, "Usually with music on.", 30, font_weight=500, letter_spacing=-.5),
                        text(x, 120, "Find me on Spotify", 18, "#a8b8c7")]
        content += ['</g>', text(24 if compact else x, 165 if compact else 175,
                                "Find me on Spotify ↗" if compact else "Open Spotify ↗", 13, "#7dd3ac")]
        title = "RobyRew on Spotify. Playback is unavailable; open the Spotify profile."
    # The embedded cover or locally drawn record never needs another network request.
    content += ['<g transform="translate(24 44) scale(.57)">' if compact else '<g transform="translate(34 36)">']
    if cover:
        content += ['<defs><clipPath id="cover"><rect width="132" height="132" rx="14"/></clipPath></defs>',
                    f'<image width="132" height="132" clip-path="url(#cover)" href="{escape(cover, quote=True)}"/>',
                    '<rect x=".5" y=".5" width="131" height="131" rx="14" fill="none" stroke="#d0e8ef" stroke-opacity=".2"/>']
    else:
        content += ['<defs><linearGradient id="vinyl" x2="1" y2="1">'
                    '<stop stop-color="#3b4b50"/><stop offset=".25" stop-color="#141e24"/>'
                    '<stop offset=".51" stop-color="#263c3b"/><stop offset=".76" stop-color="#111a22"/>'
                    '<stop offset="1" stop-color="#526664"/></linearGradient></defs>',
                    '<circle cx="66" cy="66" r="65" fill="url(#vinyl)" stroke="#7a9e96" stroke-opacity=".28"/>']
        for radius in (58, 52, 46, 40, 34):
            content += [f'<circle cx="66" cy="66" r="{radius}" fill="none" stroke="#b8d5cd" stroke-opacity=".11"/>']
        content += ['<circle cx="66" cy="66" r="25" fill="#7dd3ac"/>',
                    '<g fill="none" stroke="#12261f" stroke-linecap="round">',
                    '<path d="M50 59q17-8 33 2" stroke-width="4"/>',
                    '<path d="M52 67q14-7 28 2" stroke-width="3.5"/>',
                    '<path d="M54 75q12-5 23 1" stroke-width="3"/></g>']
    content += ['</g>']
    return card(title, content, 192 if compact else 210, width, music=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("build/profile"))
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    # A GitHub outage fails the run before either published asset can change.
    repos = public_projects()
    stats = stats_svg(repos, now)
    compact_stats = stats_svg(repos, now, compact=True)
    try:
        track = parse_spotify(fetch(SPOTIFY_URL))
    except (OSError, ValueError, ET.ParseError):
        print("::warning::Spotify playback unavailable. Using the profile card. "
              "If authorization expired, reconnect at https://spotify-github-profile.kittinanx.com/api/login")
        track = None
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "stats.svg").write_text(stats, encoding="utf-8")
    (args.output / "stats-compact.svg").write_text(compact_stats, encoding="utf-8")
    (args.output / "spotify.svg").write_text(spotify_svg(track, now), encoding="utf-8")
    (args.output / "spotify-compact.svg").write_text(spotify_svg(track, now, compact=True), encoding="utf-8")
    print(f"Rendered profile cards in {args.output}")


if __name__ == "__main__":
    main()
