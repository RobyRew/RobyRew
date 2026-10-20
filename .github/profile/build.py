#!/usr/bin/env python3
"""Builds README.md and img/ from profile.toml, and the live record player for GitHub Pages.

    python3 .github/profile/build.py            fetch fresh data, then build
    python3 .github/profile/build.py --offline  build from cache.json only
    python3 .github/profile/build.py --live DIR write the live parts and their link redirects to DIR
"""

import hashlib
import html
import json
import os
import re
import sys
import tomllib
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import canvas
from canvas import CACHE, HUE_ORDER, LANGUAGES, ROOT, THEMES, esc
from data import (LANGUAGE_COLORS, fetch, github_data, lastfm_music_url, lastfm_top, now_data, now_key, play_url,
                  spotify_accounts, spotify_token, spotify_top, stats_data, views_data)
from layout import Row, page, render, render_phone, skyline

HERE = Path(__file__).resolve().parent
LIVE_KEYS = ("play", "song", "artist", "context", "user")


def load():
    p = tomllib.loads((ROOT / "profile.toml").read_text(encoding="utf-8"))
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    return p, cache


def fill_placeholders(p, cache):
    user = cache.get("github", {}).get("user", {})
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

    return fill(p)


def version():
    """Changes whenever the code or the profile does, so the live deck is redeployed to match the README."""
    digest = hashlib.sha256()
    for path in sorted(HERE.glob("*.py")) + [ROOT / "profile.toml"]:
        digest.update(path.read_bytes())
    return digest.hexdigest()[:12]


# ── data for the page ────────────────────────────────────────────────────────


def collect(p, cache):
    gh = cache.get("github", {})
    login = p["me"]["github"]
    projects = []
    for i, entry in enumerate(p["work"]["projects"]):
        repo = gh.get("repos", {}).get(entry["repo"])
        if repo is None:
            continue
        language = repo.get("language", "")
        projects.append({
            "name": entry["repo"],
            "note": entry.get("note") or repo["description"],
            "language": language,
            "language_color": LANGUAGE_COLORS.get(language) or LANGUAGES.get(language) or "#9CA3AF",
            "stars": repo.get("stars", 0),
            "forks": repo.get("forks", 0),
            "downloads": repo.get("downloads", 0),
            "version": repo.get("version", ""),
            "url": repo["url"],
            "hue": entry.get("hue") or HUE_ORDER[i % len(HUE_ORDER)],
            "icon": entry.get("icon") or "code",
        })
    featured = {pr["name"].lower() for pr in projects} | {login.lower()}
    count = int(p.get("bsides", {}).get("count", 4))
    others = [
        {**r, "language_color": LANGUAGE_COLORS.get(r.get("language") or "", "#9CA3AF")}
        for r in cache.get("recent", []) if r["name"].lower() not in featured
    ]
    stats = cache.get("stats")
    if stats:
        stats = {**stats, **cache.get("extra", {})}
    tracks = cache.get("top_tracks") or []
    return {
        "projects": projects,
        "recent": others[:count],
        "more": others[count:],
        "stats": stats,
        "tracks": tracks,
        "now": cache.get("now"),
        "since": str(gh.get("user", {}).get("created_at", ""))[:4],
        "repo_count": gh.get("user", {}).get("public_repos"),
        "scrobbles": cache.get("extra", {}).get("scrobbles") if tracks and tracks[0].get("source") == "Last.fm" else None,
        "lastfm_url": cache.get("extra", {}).get("lastfm_url"),
    }


def now_links(now, fallback):
    """Where each part of the record player links to, for whatever is on it."""
    now = now or {}
    title, artist = now.get("title", ""), now.get("artist", "")
    if not title:
        return {key: fallback for key in LIVE_KEYS}
    platform = now.get("platform") or "Last.fm"
    song = now.get("song_url") or lastfm_music_url(artist, "_", title)
    artist_url = now.get("artist_url") or (lastfm_music_url(artist) if artist else song)
    context = now.get("context_url")
    if not context and now.get("context") and now.get("context_kind", "Album") == "Album" and artist:
        context = lastfm_music_url(artist, now["context"])
    user = now.get("user_url")
    if not user and now.get("user"):
        user = f'https://www.last.fm/user/{urllib.parse.quote(now["user"])}'
    return {
        "play": now.get("play_url") or play_url(platform, title, artist),
        "song": song,
        "artist": artist_url,
        "context": context or artist_url,
        "user": user or fallback,
    }


def repository(p):
    return os.environ.get("GITHUB_REPOSITORY") or f'{p["me"]["github"]}/{p["me"]["github"]}'


def raw_base(p):
    """Images are linked straight to the raw file host. A relative link costs a redirect through github.com each."""
    return f"https://raw.githubusercontent.com/{repository(p)}/main/img/"


def live_links(base):
    return {key: f"{base}go/{key}/" for key in LIVE_KEYS}


def fallback_link(cache, p):
    return cache.get("extra", {}).get("lastfm_url") or p.get("listening", {}).get("profile") or f'https://github.com/{p["me"]["github"]}'


# ── output ───────────────────────────────────────────────────────────────────


# Desktop images in a dark and a light version; phone images hold both themes in one file.
FOLDERS = {**{theme: theme for theme in THEMES}, "phone": "m"}


def rows_of(items):
    for item in items:
        if isinstance(item, Row):
            yield item
        elif isinstance(item, tuple) and item[0] == "details":
            yield item[1]


def write_images(rows, root, only_live=False):
    written = set()
    for row in rows:
        for cell in row.cells:
            if only_live and not cell.live:
                continue
            for theme, folder in FOLDERS.items():
                path = root / folder / f"{cell.file}.svg"
                path.parent.mkdir(parents=True, exist_ok=True)
                out = render_phone(row, cell) if theme == "phone" else render(row, cell, theme, "d")
                if not path.exists() or path.read_text(encoding="utf-8") != out:
                    path.write_text(out, encoding="utf-8")
                written.add(path)
    return written


def picture(row, cell, base):
    """One image, three files. align="top" stops GitHub leaving a gap under each row of images.

    GitHub's page script rewrites any source that mentions prefers-color-scheme to follow the theme chosen in the
    viewer's settings, and drops whatever else the query said. So the phone source asks for width only, and its
    image switches theme by itself.
    """

    def src(folder):
        return f"{base}{folder}/{cell.file}.svg"

    pct = row.percent(cell)
    return (
        f'<picture><source media="(max-width: 600px)" srcset="{src("m")}">'
        f'<source media="(prefers-color-scheme: dark)" srcset="{src("dark")}">'
        f'<img src="{src("light")}" width="{pct:g}%" align="top" alt="{esc(cell.alt)}" title="{esc(cell.title)}"></picture>'
    )


def row_html(row, live_base, static_base):
    parts = []
    for cell in row.cells:
        base = f"{live_base}img/" if (cell.live and live_base) else static_base
        tag = picture(row, cell, base)
        parts.append(f'<a href="{esc(cell.href)}" title="{esc(cell.title)}">{tag}</a>' if cell.href else tag)
    return "".join(parts)


def markdown_text(text):
    """Plain text that Markdown won't turn into anything."""
    return re.sub(r"([\\`*_{}\[\]<>#|~])", r"\\\1", html.unescape(text))


def more_list(more, login, total):
    lines = []
    for repo in more:
        description = " ".join((repo.get("description") or "").split())
        if len(description) > 110:
            description = description[:108].rsplit(" ", 1)[0].rstrip(",.;:—-") + "…"
        extra = f" · {markdown_text(description)}" if description else ""
        language = f" `{repo['language']}`" if repo.get("language") else ""
        lines.append(f'- [**{markdown_text(repo["name"])}**]({repo["url"]}){language}{extra}')
    label = f"All {total} repositories" if total else "All repositories"
    lines += ["", f"[**{label} →**](https://github.com/{login}?tab=repositories)"]
    return "\n".join(lines)


def readme(items, p, live_base, repo_count, static_base):
    login = p["me"]["github"]
    views = f'<img src="https://komarev.com/ghpvc/?username={login}&amp;style=flat" width="1" height="1" alt="">'
    lines = [
        "<!-- Generated by .github/profile/build.py from profile.toml. Edit that file, not this one. -->",
        '<a name="top"></a>',
        '<div align="center">',
    ]
    anchor = ""
    for item in items:
        if isinstance(item, tuple) and item[0] == "anchor":
            anchor += f'<a name="{item[1]}"></a>'
        elif isinstance(item, tuple) and item[0] == "details":
            # Outside the centred block, so the list inside can be real Markdown.
            row, more = item[1], item[2]
            lines += ["</div>", "", f"<details>\n<summary>{anchor}{row_html(row, None, static_base)}</summary>", "",
                      more_list(more, login, repo_count), "", "</details>", "", '<div align="center">']
            anchor = ""
        elif isinstance(item, Row):
            lines.append(anchor + row_html(item, live_base, static_base))
            anchor = ""
    lines.append(views)
    lines.append("</div>")
    return "\n".join(lines) + "\n"


# ── the live record player (GitHub Pages) ────────────────────────────────────


def redirect_page(url):
    target = esc(url)
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="robots" content="noindex">'
        f'<meta http-equiv="refresh" content="0; url={target}"><title>Opening…</title>'
        f"<script>location.replace({json.dumps(url)})</script>"
        f'<p style="font:16px system-ui;margin:2rem">Opening <a href="{target}">{target}</a>…</p></html>\n'
    )


def live(out):
    """Renders the parts of the record player that change with the music, plus a redirect for each link."""
    p, cache = load()
    p = fill_placeholders(p, cache)
    now = now_data(p, dict(cache), spotify_accounts()) or cache.get("now")
    base = os.environ.get("PAGES_URL") or cache.get("pages_url", "")
    base = base.rstrip("/") + "/" if base else ""
    key = f"{now_key(now)}|{version()}"
    out = Path(out)
    previous = None
    if base:
        try:
            previous = fetch(base + "now.json").get("key")
        except Exception as error:
            print(f"live: no previous state ({error})", file=sys.stderr)
    changed = previous != key or "--force" in sys.argv
    data = collect(p, cache)
    data["now"] = now
    write_images(rows_of(page(p, data, live_links(base))), out / "img", only_live=True)
    links = now_links(now, fallback_link(cache, p))
    for name, url in links.items():
        folder = out / "go" / name
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "index.html").write_text(redirect_page(url), encoding="utf-8")
    (out / "now.json").write_text(json.dumps({"key": key, "now": now, "links": links}, ensure_ascii=False, indent=2),
                                  encoding="utf-8")
    (out / "index.html").write_text(redirect_page(f'https://github.com/{p["me"]["github"]}'), encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as handle:
            handle.write(f"changed={'true' if changed else 'false'}\n")
    print(f"live: {key} ({'changed' if changed else 'unchanged'})")


# ── the daily build ──────────────────────────────────────────────────────────


def refresh(p, cache):
    github_data(p, cache)
    stats_data(p, cache)
    accounts = spotify_accounts()
    topped = False
    if accounts:
        try:
            topped = spotify_top(p, cache, spotify_token(*accounts[0][1:]))
        except Exception as error:
            print(f"spotify: no top tracks ({error})", file=sys.stderr)
    if not topped:
        lastfm_top(p, cache)
    views_data(p, cache)
    now = now_data(p, cache, accounts)
    if now:
        cache["now"] = {**now, "playing": False, "paused": False}
    if os.environ.get("LIVE") in ("true", "false"):
        cache["live"] = os.environ["LIVE"] == "true"


def main():
    if "--live" in sys.argv:
        live(sys.argv[sys.argv.index("--live") + 1])
        return
    canvas.OFFLINE = "--offline" in sys.argv
    p, cache = load()
    if not canvas.OFFLINE:
        refresh(p, cache)
    p = fill_placeholders(p, cache)
    data = collect(p, cache)
    live_base = cache.get("pages_url") if cache.get("live") else None
    hrefs = live_links(live_base) if live_base else now_links(data["now"], fallback_link(cache, p))
    folder = ROOT / "img"
    folder.mkdir(exist_ok=True)
    # The contribution calendar in 3D, as a file GitHub shows in its own 3D viewer (linked from the activity card).
    model = folder / "contributions.stl"
    skyline_url = None
    if (data["stats"] or {}).get("calendar"):
        stl = skyline(data["stats"]["calendar"])
        if not model.exists() or model.read_text(encoding="utf-8") != stl:
            model.write_text(stl, encoding="utf-8")
        skyline_url = f"https://github.com/{repository(p)}/blob/main/img/contributions.stl"
    elif model.exists():
        model.unlink()
    items = page(p, data, hrefs, skyline_url)
    rows = list(rows_of(items))

    written = write_images(rows, folder)
    for stale in folder.rglob("*.svg"):
        if stale not in written:
            stale.unlink()
    for empty in sorted(folder.iterdir()):
        if empty.is_dir() and not any(empty.iterdir()):
            empty.rmdir()

    (ROOT / "README.md").write_text(readme(items, p, live_base, data["repo_count"], raw_base(p)), encoding="utf-8")
    CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    cells = sum(len(row.cells) for row in rows)
    print(
        f"built {cells} linked images × {len(FOLDERS)} versions, {len(data['projects'])} projects, "
        f"{len(data['recent'])} b-sides, {'stats' if data['stats'] else 'no stats'}, {len(data['tracks'])} tracks, "
        f"now: {now_key(data['now'])}"
    )


if __name__ == "__main__":
    main()
