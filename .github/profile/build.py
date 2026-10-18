#!/usr/bin/env python3
"""Renders README.md and every SVG in img/ from profile.toml.

    pip install fonttools brotli
    python3 .github/profile/build.py            # fetches GitHub + Spotify data when it can
    python3 .github/profile/build.py --offline  # uses the last values saved in cache.json

Each SVG embeds a subset of the fonts it uses, so the type renders the same
everywhere GitHub shows the image. Light and dark variants are written to
img/light and img/dark and picked by <picture> in the README.
"""

import base64
import html
import json
import math
import os
import sys
import tomllib
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CACHE = HERE / "cache.json"
W = 840

SERIF = "'New York', 'Iowan Old Style', Georgia, serif"
MONO = "ui-monospace, 'SF Mono', Menlo, monospace"
FONTS = {
    # key: (file, fallback stack, style, weight)
    "display": ("Newsreader-LightItalic.ttf", SERIF, "italic", 300),
    "serif": ("Newsreader-Regular.ttf", SERIF, "normal", 400),
    "italic": ("Newsreader-Italic.ttf", SERIF, "italic", 400),
    "mono": ("DMMono-Regular.ttf", MONO, "normal", 400),
    "mono-md": ("DMMono-Medium.ttf", MONO, "normal", 500),
}

THEMES = {
    "dark": {
        "ink": "#ECE7DF",
        "muted": "#8E8A83",
        "faint": "#30363D",
        "accent": "#FF6B3D",
        "vinyl": "#050608",
        "groove": 0.055,
        "sheen": 0.016,
        "rim": 0.12,
    },
    "light": {
        "ink": "#1C1B19",
        "muted": "#6B6761",
        "faint": "#DAD6CF",
        "accent": "#E5482A",
        "vinyl": "#111111",
        "groove": 0.07,
        "sheen": 0.011,
        "rim": 0.0,
    },
}
LABEL_INK = "#1A0D07"


def esc(s):
    return html.escape(str(s), quote=True)


def num(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


# ── type ─────────────────────────────────────────────────────────────────────


class Face:
    def __init__(self, key):
        file, self.stack, self.style, self.weight = FONTS[key]
        self.path = HERE / "fonts" / file
        font = TTFont(self.path, lazy=True)
        self.cmap = font.getBestCmap()
        self.advance = {g: a for g, (a, _) in font["hmtx"].metrics.items()}
        self.upm = font["head"].unitsPerEm

    def width(self, text, size, tracking=0.0):
        units = sum(
            self.advance[self.cmap[ord(c)]] if ord(c) in self.cmap else self.upm * 0.55
            for c in text
        )
        return units * size / self.upm + tracking * len(text)

    def fit(self, text, size, max_width, tracking=0.0):
        if self.width(text, size, tracking) <= max_width:
            return text
        while text and self.width(text + "…", size, tracking) > max_width:
            text = text[:-1]
        return text.rstrip(" ,.;:—-") + "…"

    def wrap(self, text, size, max_width):
        lines, line = [], ""
        for word in text.split():
            trial = f"{line} {word}".strip()
            if line and self.width(trial, size) > max_width:
                lines.append(line)
                line = word
            else:
                line = trial
        return lines + [line] if line else lines


FACES = {key: Face(key) for key in FONTS}


@lru_cache(maxsize=None)
def font_face(key, chars):
    face = FACES[key]
    options = subset.Options()
    options.flavor = "woff2"
    options.hinting = False
    options.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk"]
    font = TTFont(face.path, recalcTimestamp=False)
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=chars)
    subsetter.subset(font)
    buffer = BytesIO()
    subset.save_font(font, buffer, options)
    data = base64.b64encode(buffer.getvalue()).decode()
    return (
        f"@font-face{{font-family:'rr-{key}';src:url(data:font/woff2;base64,{data}) format('woff2');"
        f"font-style:{face.style};font-weight:{face.weight}}}"
        f".f-{key}{{font-family:'rr-{key}',{face.stack};font-style:{face.style};font-weight:{face.weight}}}"
    )


# ── canvas ───────────────────────────────────────────────────────────────────


class SVG:
    def __init__(self, theme, height, label):
        self.theme = theme
        self.t = THEMES[theme]
        self.height = height
        self.label = label
        self.parts, self.css, self.chars = [], [], {}

    def add(self, markup):
        self.parts.append(markup)

    def use(self, font, text):
        self.chars.setdefault(font, set()).update(text)

    def text(self, x, y, s, font, size, fill, tracking=0, anchor="start"):
        if not s:
            return
        if anchor == "end":
            x -= FACES[font].width(s, size, tracking)
        self.use(font, s)
        spacing = f' letter-spacing="{num(tracking)}"' if tracking else ""
        self.add(
            f'<text x="{num(x)}" y="{num(y)}" class="f-{font}" font-size="{num(size)}" '
            f'fill="{fill}"{spacing}>{esc(s)}</text>'
        )

    def rule(self, y):
        self.add(f'<line x1="0" y1="{num(y)}" x2="{W}" y2="{num(y)}" stroke="{self.t["faint"]}" stroke-width="1"/>')

    def leaders(self, x0, x1, y):
        if x1 - x0 < 12:
            return
        self.add(
            f'<line x1="{num(x0)}" y1="{num(y)}" x2="{num(x1)}" y2="{num(y)}" stroke="{self.t["muted"]}" '
            f'stroke-opacity=".55" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="0 6.5"/>'
        )

    def render(self):
        fonts = "".join(font_face(k, "".join(sorted(v))) for k, v in sorted(self.chars.items()))
        css = (
            fonts
            + "text{font-kerning:normal;text-rendering:geometricPrecision}"
            + "".join(self.css)
            + "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{self.height}" '
            f'viewBox="0 0 {W} {self.height}" role="img" aria-label="{esc(self.label)}">'
            f"<title>{esc(self.label)}</title><style>{css}</style>"
            + "".join(self.parts)
            + "</svg>\n"
        )


def circle_path(cx, cy, r):
    return f"M{num(cx - r)} {num(cy)}a{num(r)} {num(r)} 0 1 0 {num(2 * r)} 0a{num(r)} {num(r)} 0 1 0 {num(-2 * r)} 0Z"


def sector(cx, cy, r0, r1, a0, a1):
    def point(r, a):
        return f"{num(cx + r * math.cos(math.radians(a)))} {num(cy + r * math.sin(math.radians(a)))}"

    return (
        f"M{point(r1, a0)}A{num(r1)} {num(r1)} 0 0 1 {point(r1, a1)}"
        f"L{point(r0, a1)}A{num(r0)} {num(r0)} 0 0 0 {point(r0, a0)}Z"
    )


# ── pieces ───────────────────────────────────────────────────────────────────


def record(svg, cx, cy, r, words):
    t = svg.t
    label_r, hole_r = 58, 4.2
    svg.css.append(
        f".spin{{transform-origin:{cx}px {cy}px;animation:spin 16s linear infinite}}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
    )
    parts = [
        '<g class="spin">',
        f'<path d="{circle_path(cx, cy, r)}{circle_path(cx, cy, hole_r)}" fill="{t["vinyl"]}" fill-rule="evenodd"/>',
    ]
    groove = label_r + 8
    i = 0
    while groove < r - 5:
        opacity = t["groove"] * (1.8 if i % 7 == 0 else 1)
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{num(groove)}" fill="none" stroke="#fff" '
            f'stroke-opacity="{num(opacity)}" stroke-width=".6"/>'
        )
        groove += 2.6
        i += 1
    for gap in (r * 0.56, r * 0.71, r * 0.85):
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{num(gap)}" fill="none" stroke="{t["vinyl"]}" stroke-width="2.6"/>'
        )
    parts.append(
        f'<path d="{circle_path(cx, cy, label_r)}{circle_path(cx, cy, hole_r)}" fill="{t["accent"]}" fill-rule="evenodd"/>'
    )
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{label_r - 3}" fill="none" stroke="{LABEL_INK}" '
        f'stroke-opacity=".22" stroke-width=".6"/>'
    )
    ring = 46
    size = 7.4
    tracking = (2 * math.pi * ring - FACES["mono-md"].width(words, size)) / len(words)
    svg.use("mono-md", words)
    parts.append(
        f'<path id="ring" d="M{cx - ring} {cy}a{ring} {ring} 0 1 1 {2 * ring} 0a{ring} {ring} 0 1 1 {-2 * ring} 0" fill="none"/>'
        f'<text class="f-mono-md" font-size="{size}" letter-spacing="{num(tracking)}" fill="{LABEL_INK}" '
        f'fill-opacity=".78"><textPath href="#ring">{esc(words)}</textPath></text>'
    )
    svg.use("display", "A")
    parts.append(
        f'<text x="{cx}" y="{cy + 33}" text-anchor="middle" class="f-display" font-size="24" '
        f'fill="{LABEL_INK}" fill-opacity=".85">A</text>'
    )
    parts.append("</g>")
    # Light catching the grooves; it stays put while the disc turns.
    for base in (-58, 122):
        for spread in (34, 27, 21, 15, 10, 5):
            parts.append(
                f'<path d="{sector(cx, cy, label_r + 6, r - 2, base - spread, base + spread)}" '
                f'fill="#fff" fill-opacity="{t["sheen"]}"/>'
            )
    if t["rim"]:
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r - 0.5}" fill="none" stroke="#fff" '
            f'stroke-opacity="{t["rim"]}" stroke-width="1"/>'
        )
    svg.add("".join(parts))


def hero(theme, p):
    me = p["me"]
    label = f'{me["name"]}. {me["statement"]} {me["aside"]}'
    svg = SVG(theme, 478, label)
    t = svg.t
    cx, cy, r = 776, 192, 170
    record(svg, cx, cy, r, me["record"])

    def room(y, size):
        # Space to the left of the record at this baseline, with breathing room.
        dy = min(abs(y - cy), abs(y - size * 0.7 - cy))
        return cx - math.sqrt(max(r * r - dy * dy, 0)) - 34

    svg.text(0, 30, me["kicker"].upper(), "mono", 11.5, t["muted"], tracking=2.3)
    svg.text(-5, 172, me["name"], "display", 132, t["ink"])

    y, size = 236, 24
    for text, font, color in ((me["statement"], "serif", t["ink"]), (me["aside"], "italic", t["accent"])):
        for line in FACES[font].wrap(text, size, room(y, size)):
            svg.text(0, y, line, font, size, color)
            y += 34

    svg.rule(394)
    facts = me.get("facts", [])
    col = W / max(len(facts), 1)
    for i, fact in enumerate(facts):
        x = i * col
        svg.text(x, 430, fact["label"].upper(), "mono", 10.5, t["muted"], tracking=1.9)
        value = FACES["serif"].fit(fact["value"], 19, col - 24)
        svg.text(x, 460, value, "serif", 19, t["ink"])
    return svg


def section(theme, kicker, title, right, label):
    svg = SVG(theme, 150, label)
    t = svg.t
    svg.text(0, 78, kicker.upper(), "mono-md", 11, t["accent"], tracking=2.4)
    svg.text(-2, 122, title, "display", 42, t["ink"])
    svg.text(W, 122, right.upper(), "mono", 10.5, t["muted"], tracking=1.9, anchor="end")
    svg.rule(146)
    return svg


def track(svg, y, index, title, note, meta):
    t = svg.t
    svg.text(0, y, index, "mono", 12, t["muted"], tracking=1)
    meta = meta.upper()
    meta_w = FACES["mono"].width(meta, 11, 1.7)
    title = FACES["serif"].fit(title, 26, W - 52 - meta_w - 60)
    title_w = FACES["serif"].width(title, 26)
    svg.text(52, y, title, "serif", 26, t["ink"])
    svg.leaders(52 + title_w + 16, W - meta_w - 16, y - 1)
    svg.text(W - meta_w, y, meta, "mono", 11, t["muted"], tracking=1.7)
    if note:
        svg.text(52, y + 29, FACES["italic"].fit(note, 17.5, W - 52 - 20), "italic", 17.5, t["muted"])


def project_row(theme, index, project):
    note = project["note"]
    label = f'{project["name"]}{": " + note if note else ""}'
    svg = SVG(theme, 92 if note else 64, label)
    meta = project["language"] or ""
    stars = project["stars"]
    if stars:
        meta = f'{meta} · {stars} {"star" if stars == 1 else "stars"}'.strip(" ·")
    track(svg, 42, index, project["name"], note, meta)
    return svg


def highlights(theme, items):
    label = " ".join(f'{i["title"]}: {i["note"]}' for i in items)
    svg = SVG(theme, 18 + 92 * len(items), label)
    for n, item in enumerate(items):
        track(svg, 42 + n * 92, f"B{n + 1}", item["title"], item["note"], item.get("tag", ""))
    return svg


def rotation(theme, title, tracks):
    label = "On rotation: " + "; ".join(f'{x["name"]} by {x["artist"]}' for x in tracks)
    svg = SVG(theme, 172 + 50 * len(tracks), label)
    t = svg.t
    svg.text(0, 78, "ON ROTATION", "mono-md", 11, t["accent"], tracking=2.4)
    x = FACES["mono-md"].width("ON ROTATION", 11, 2.4) + 10
    svg.css.append(
        ".eq rect{transform-box:fill-box;transform-origin:50% 100%;animation:eq .9s ease-in-out infinite alternate}"
        "@keyframes eq{from{transform:scaleY(.25)}}"
    )
    bars = "".join(
        f'<rect x="{num(x + i * 4.5)}" y="68" width="2.4" height="10" rx=".6" fill="{t["accent"]}" '
        f'style="animation-delay:{num(-0.27 * i * (i + 1))}s"/>'
        for i in range(3)
    )
    svg.add(f'<g class="eq">{bars}</g>')
    svg.text(-2, 122, title, "display", 42, t["ink"])
    svg.text(W, 122, "VIA SPOTIFY", "mono", 10.5, t["muted"], tracking=1.9, anchor="end")
    svg.rule(146)
    for n, item in enumerate(tracks):
        y = 192 + n * 50
        minutes, seconds = divmod(round(item["ms"] / 1000), 60)
        duration = f"{minutes}:{seconds:02d}"
        dur_w = FACES["mono"].width(duration, 12, 1)
        room = W - 52 - dur_w - 56
        name = FACES["serif"].fit(item["name"], 22, room * 0.62)
        name_w = FACES["serif"].width(name, 22) + 9
        artist = FACES["italic"].fit(f'— {item["artist"]}', 18, room - name_w)
        artist_w = FACES["italic"].width(artist, 18)
        svg.text(0, y, f"{n + 1:02d}", "mono", 12, t["muted"], tracking=1)
        svg.text(52, y, name, "serif", 22, t["ink"])
        svg.text(52 + name_w, y, artist, "italic", 18, t["muted"])
        svg.leaders(52 + name_w + artist_w + 16, W - dur_w - 16, y - 1)
        svg.text(W - dur_w, y, duration, "mono", 12, t["muted"], tracking=1)
    return svg


def credits(theme, title, items):
    label = "Credits. " + "; ".join(f'{i["label"]}: {i["value"]}' for i in items)
    rows = math.ceil(len(items) / 2)
    svg = SVG(theme, 196 + 70 * rows, label)
    t = svg.t
    svg.text(0, 78, "CREDITS", "mono-md", 11, t["accent"], tracking=2.4)
    svg.text(-2, 122, title, "display", 42, t["ink"])
    svg.rule(146)
    col = W / 2 + 10
    for n, item in enumerate(items):
        x = (n % 2) * col
        y = 192 + (n // 2) * 70
        svg.text(x, y, item["label"].upper(), "mono", 10.5, t["muted"], tracking=1.9)
        svg.text(x, y + 29, FACES["serif"].fit(item["value"], 21, col - 30), "serif", 21, t["ink"])
    return svg


def colophon(theme, left, right):
    svg = SVG(theme, 96, f"{left}. {right}")
    t = svg.t
    svg.rule(40)
    svg.text(0, 74, left.upper(), "mono", 10, t["muted"], tracking=1.9)
    svg.text(W, 74, right.upper(), "mono", 10, t["muted"], tracking=1.9, anchor="end")
    return svg


# ── data ─────────────────────────────────────────────────────────────────────


def fetch_json(url, headers=None, data=None):
    request = urllib.request.Request(url, data=data, headers={"User-Agent": "robyrew-profile", **(headers or {})})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def github_data(p, cache):
    data = cache.setdefault("github", {"user": {}, "repos": {}})
    headers = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f'Bearer {os.environ["GITHUB_TOKEN"]}'
    login = p["me"]["github"]
    try:
        user = fetch_json(f"https://api.github.com/users/{login}", headers)
        data["user"] = {"public_repos": user["public_repos"], "created_at": user["created_at"]}
    except Exception as error:
        print(f"github: keeping cached user ({error})", file=sys.stderr)
    for project in p["work"]["projects"]:
        name = project["repo"]
        try:
            repo = fetch_json(f"https://api.github.com/repos/{login}/{name}", headers)
        except Exception as error:
            print(f"github: keeping cached {name} ({error})", file=sys.stderr)
            continue
        if repo.get("private"):
            data["repos"].pop(name, None)
            continue
        data["repos"][name] = {
            "description": repo.get("description") or "",
            "language": repo.get("language") or "",
            "stars": repo.get("stargazers_count", 0),
            "url": repo.get("html_url") or f"https://github.com/{login}/{name}",
        }


def spotify_data(p, cache):
    keys = ("SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "SPOTIFY_REFRESH_TOKEN")
    client_id, secret, refresh = (os.environ.get(k) for k in keys)
    if not (client_id and secret and refresh):
        return
    limit = int(p.get("listening", {}).get("tracks", 5))
    try:
        auth = base64.b64encode(f"{client_id}:{secret}".encode()).decode()
        token = fetch_json(
            "https://accounts.spotify.com/api/token",
            {"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"},
            urllib.parse.urlencode({"grant_type": "refresh_token", "refresh_token": refresh}).encode(),
        )["access_token"]
        bearer = {"Authorization": f"Bearer {token}"}
        items = fetch_json(
            f"https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit={limit}", bearer
        )["items"]
        if not items:
            recent = fetch_json("https://api.spotify.com/v1/me/player/recently-played?limit=50", bearer)["items"]
            seen = {}
            for play in recent:
                seen.setdefault(play["track"]["id"], play["track"])
            items = list(seen.values())[:limit]
    except Exception as error:
        print(f"spotify: keeping cached tracks ({error})", file=sys.stderr)
        return
    if items:
        cache["spotify"] = [
            {
                "name": item["name"],
                "artist": ", ".join(a["name"] for a in item["artists"]),
                "ms": item["duration_ms"],
            }
            for item in items
        ]


# ── assembly ─────────────────────────────────────────────────────────────────


def main():
    offline = "--offline" in sys.argv
    p = tomllib.loads((ROOT / "profile.toml").read_text(encoding="utf-8"))
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    if not offline:
        github_data(p, cache)
        spotify_data(p, cache)

    gh = cache.get("github", {})
    user = gh.get("user", {})
    joined = user.get("created_at", "")
    since = joined[:4] if joined else ""
    years = ""
    if joined:
        start = datetime.fromisoformat(joined.replace("Z", "+00:00"))
        years = str(int((datetime.now(timezone.utc) - start).days // 365.25))
    values = {"{repos}": str(user.get("public_repos", "")), "{since}": since, "{years}": years}

    def fill(obj):
        if isinstance(obj, str):
            for key, value in values.items():
                obj = obj.replace(key, value)
            return obj
        if isinstance(obj, list):
            return [fill(x) for x in obj]
        if isinstance(obj, dict):
            return {k: fill(v) for k, v in obj.items()}
        return obj

    p = fill(p)

    projects = []
    for entry in p["work"]["projects"]:
        repo = gh.get("repos", {}).get(entry["repo"])
        if repo is None:
            continue
        projects.append(
            {
                "name": entry["repo"],
                "note": entry.get("note") or repo["description"],
                "language": repo["language"],
                "stars": repo["stars"],
                "url": repo["url"],
            }
        )
    tracks = cache.get("spotify") or []
    year = datetime.now(timezone.utc).year

    files = {}  # name -> (builder, alt, href)
    blocks = []

    def add(name, build, href=None):
        files[name] = build
        blocks.append((name, href))

    add("hero", lambda th: hero(th, p))
    count = f"{len(projects):02d} tracks"
    add("side-a", lambda th: section(th, "Side A", p["work"]["title"], count, f'Side A: {p["work"]["title"]}'))
    for i, project in enumerate(projects):
        add(f"a{i + 1}", lambda th, i=i, pr=project: project_row(th, f"A{i + 1}", pr), project["url"])
    items = p.get("highlights", {}).get("items", [])
    if items:
        title = p["highlights"]["title"]
        add("side-b", lambda th: section(th, "Side B", title, f"{len(items):02d} tracks", f"Side B: {title}"))
        add("highlights", lambda th: highlights(th, items))
    if tracks:
        listening = p.get("listening", {})
        add("rotation", lambda th: rotation(th, listening.get("title", "On rotation"), tracks), listening.get("profile") or None)
    if p.get("credits", {}).get("items"):
        add("credits", lambda th: credits(th, p["credits"]["title"], p["credits"]["items"]))
    add("colophon", lambda th: colophon(th, "Set in Newsreader & DM Mono", f"© {year} {p['me']['name']}"))

    written = set()
    for theme in THEMES:
        folder = ROOT / "img" / theme
        folder.mkdir(parents=True, exist_ok=True)
        for name, build in files.items():
            path = folder / f"{name}.svg"
            out = build(theme).render()
            if not path.exists() or path.read_text(encoding="utf-8") != out:
                path.write_text(out, encoding="utf-8")
            written.add(path)
        for stale in folder.glob("*.svg"):
            if stale not in written:
                stale.unlink()

    alts = {name: files[name]("dark").label for name in files}
    lines = [
        "<!-- Generated by .github/profile/build.py from profile.toml. Edit that file, not this one. -->",
        "<div>",
    ]
    for name, href in blocks:
        picture = (
            f'<picture><source media="(prefers-color-scheme: dark)" srcset="img/dark/{name}.svg">'
            f'<img src="img/light/{name}.svg" width="100%" alt="{esc(alts[name])}"></picture>'
        )
        if name == "colophon":
            links = " &nbsp;·&nbsp; ".join(f'<a href="{esc(l["url"])}">{esc(l["label"])}</a>' for l in p.get("links", []))
            lines.append(f"<p>{links}</p>")
        lines.append(f'<a href="{esc(href)}">{picture}</a>' if href else picture)
    lines.append("</div>")
    readme = "\n".join(lines) + "\n"
    (ROOT / "README.md").write_text(readme, encoding="utf-8")

    CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"built {len(files)} images × {len(THEMES)} themes, {len(projects)} projects, {len(tracks)} tracks")


if __name__ == "__main__":
    main()
