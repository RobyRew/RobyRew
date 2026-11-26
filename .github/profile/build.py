#!/usr/bin/env python3
"""Builds README.md and img/ from profile.toml, and the live record player for GitHub Pages.

    python3 .github/profile/build.py            fetch fresh data, then build
    python3 .github/profile/build.py --offline  build from cache.json only
    python3 .github/profile/build.py --live DIR write the live parts and their link redirects to DIR
"""

import hashlib
import json
import os
import re
import sys
import tomllib
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import canvas
import layout
from canvas import CACHE, FACES, HUE_ORDER, ICONS, PLATFORMS, ROOT, THEMES, compact, esc, render_pair
from data import (LANGUAGE_COLORS, PLAY_SEARCH, fetch, github_data, lastfm_music_url, lastfm_top, lastfm_users, now_data,
                  now_key, now_service, play_url, spotify_accounts, spotify_best, spotify_now, stats_data)
from layout import Row, draw, hero_rows, page, render, render_phone

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


def domain(url):
    """A web address the way a person would type it: no scheme, no trailing slash."""
    return re.sub(r"^https?://(www\.)?", "", url or "").rstrip("/")


def project(entry, repo, hue):
    """A repository from profile.toml, with what GitHub knows about it."""
    language = repo.get("language") or ""
    icon = entry.get("icon") or "code"
    image = icon if icon.lower().endswith((".png", ".svg")) else None
    meta = [language] if language else []
    if repo.get("version"):
        meta.append(repo["version"])
    if repo.get("downloads"):
        meta.append(f'{compact(repo["downloads"])} downloads')
    live = entry["live"] if "live" in entry else repo.get("homepage")  # live = "" hides the repo's homepage
    if live:
        meta.append(domain(live))
    return {
        "name": entry["repo"],
        "title": entry.get("title") or entry["repo"],
        "kind": entry.get("kind", ""),
        "tag": entry.get("tag", ""),
        "note": entry.get("note") or repo.get("description") or "",
        "image": image,
        "glyph": None if image else icon,
        "hue": entry.get("hue") or hue,
        "texture": entry.get("texture"),
        "mock": entry.get("mock"),
        "url": repo["url"],
        "meta": meta,
        "language_color": repo.get("language_color") or LANGUAGE_COLORS.get(language) or "#9CA3AF",
        "pushed": repo.get("pushed", ""),
    }


def projects_of(section, repos):
    found = []
    for i, entry in enumerate(section.get("projects", [])):
        repo = repos.get(entry["repo"])
        if repo is None:
            print(f"profile: {entry['repo']} isn't a public repository of mine, left out", file=sys.stderr)
            continue
        found.append(project(entry, repo, HUE_ORDER[i % len(HUE_ORDER)]))
    return found


def archive_items(p, repos, login):
    """Older work: one repository, or every repository whose name matches, added up."""
    items = []
    for entry in p.get("archive", {}).get("items", []):
        if entry.get("match"):
            pattern = re.compile(entry["match"], re.IGNORECASE)
            group = [repo for name, repo in repos.items() if pattern.search(name)]
            url = entry.get("url") or f"https://github.com/{login}?tab=repositories&q={urllib.parse.quote(entry['match'])}"
        else:
            group = [repos[entry["repo"]]] if entry.get("repo") in repos else []
            url = entry.get("url") or (group[0]["url"] if group else "")
        if not group:
            continue
        stars = sum(repo.get("stars", 0) for repo in group)
        downloads = sum(repo.get("downloads", 0) for repo in group)
        forks = sum(repo.get("forks", 0) for repo in group)
        meta = [f'{len(group)} {entry.get("unit", "repos")}'] if len(group) > 1 else []
        meta += [f"{compact(n)} {label}" for n, label in ((stars, "stars"), (downloads, "downloads"), (forks, "forks")) if n]
        items.append({
            "title": entry["title"], "subtitle": entry.get("subtitle", ""), "note": entry.get("note", ""),
            "glyph": entry.get("icon") or "archive", "hue": entry.get("hue"), "url": url, "tip": entry.get("tip"),
            "meta": meta,
        })
    return items


def collect(p, cache):
    gh = cache.get("github", {})
    login = p["me"]["github"]
    repos = gh.get("repos", {})
    user = gh.get("user", {})
    stats = cache.get("stats") or {}
    projects = projects_of(p.get("work", {}), repos)
    more = projects_of(p.get("more", {}), repos)
    listed = [pr for pr in projects + more if pr["pushed"]]
    latest = max(listed, key=lambda pr: pr["pushed"]) if listed else None
    tracks = (cache.get("top_tracks") or [])[: int(p.get("listening", {}).get("tracks", 5))]
    return {
        "projects": projects,
        "more": more,
        "archive": archive_items(p, repos, login),
        "totals": {
            # Downloads and stars add up my own repositories (the query leaves forks out); the repository count is
            # GitHub's public_repos, forks included, the number on the Repositories tab of the profile.
            "downloads": sum(repo.get("downloads", 0) for repo in repos.values()),
            "stars": stats.get("stars") or sum(repo.get("stars", 0) for repo in repos.values()),
            "repos": user.get("public_repos"),
            "contributions": stats.get("contributions"),
        },
        "pulse": {"name": latest["title"], "when": latest["pushed"]} if latest else None,
        "tracks": tracks,
        "now": cache.get("now"),
        "since": str(user.get("created_at", ""))[:4],
        "repo_count": user.get("public_repos"),
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


def readme(items, p, live_base, static_base):
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


def kit(p, cache, now, spotify=None):
    """Everything the Worker (.github/worker/now.js) needs to draw the deck on each visit: the deck in each of its
    looks (idle or playing, with a cover or without) with a slot for what's on it, the fonts they share, the numbers
    to measure text with, and whose music to look up."""
    templates, fonts = {}, {}
    totals = collect(p, cache)["totals"]  # the numbers under the deck shape its card, as in the README

    def shared_fonts(svg):
        # Each font is stored once and named by its hash; the templates only name it.
        def keep(match):
            key = hashlib.sha256(match.group(1).encode()).hexdigest()[:10]
            fonts[key] = match.group(1)
            return "{{font:" + key + "}}"
        return re.sub(r"(?<=data:font/woff2;base64,)([A-Za-z0-9+/=]+)", keep, svg)

    layout.TEMPLATES = True
    try:
        for playing in (False, True):
            for cover in (False, True):
                look = f'{"playing" if playing else "idle"}-{"cover" if cover else "label"}'
                row = hero_rows(p, {"playing": playing, "cover": "yes" if cover else ""}, {"play": ""}, "", totals=totals)[0]
                cell = next(c for c in row.cells if c.live)
                versions = {}
                for theme in THEMES:
                    svg, view = draw(row, cell, theme, "d")
                    versions[theme] = {"svg": shared_fonts(svg.render(view=view)), "slots": svg.slots}
                light, view = draw(row, cell, "light", "m", "l")
                dark, _ = draw(row, cell, "dark", "m", "k")
                versions["m"] = {"svg": shared_fonts(render_pair(light, dark, view)), "slots": light.slots + dark.slots}
                templates[look] = versions
    finally:
        layout.TEMPLATES = False

    def metrics(key, chars):
        face = FACES[key]
        return {"upm": face.upm, "advance": {ch: face.advance[face.cmap[ord(ch)]] for ch in chars if ord(ch) in face.cmap}}

    return {
        "version": version(),
        "file": next(c.file for c in hero_rows(p, now, {"play": ""}, "", totals=totals)[0].cells if c.live),
        "templates": templates,
        "fonts": fonts,
        "faces": {"semi": metrics("semi", layout.INFO_CHARS), "mono": metrics("mono", layout.STATUS_CHARS)},
        "icons": {name: ICONS[name] for name in ("disc", "list")},
        "platforms": PLATFORMS,
        "play_search": PLAY_SEARCH,
        "lastfm": lastfm_users(p),
        "now": now,
        # The Spotify accounts' best snapshot from this run (SpotAPI is Python, so the Worker reads it from here).
        "spotify": spotify,
        "fallback": fallback_link(cache, p),
        "profile": f'https://github.com/{p["me"]["github"]}',
    }


def live(out):
    """Renders the parts of the record player that change with the music, plus a redirect for each link."""
    p, cache = load()
    p = fill_placeholders(p, cache)
    accounts = spotify_accounts(p)
    service = now_service(p)
    if service is not None:
        # The now service watches the accounts all the time; its pick is the Spotify side of this run.
        best = dict(service["now"]) if service.get("now") else None
        now = now_data(p, dict(cache), accounts, heard=[best] if best else []) or cache.get("now")
    else:
        spotify = spotify_now(accounts, dict(cache.get("spotify_users", {})))
        now = now_data(p, dict(cache), accounts, spotify) or cache.get("now")
        best = spotify_best([dict(result, account=n) for (n, _, _), result in zip(accounts, spotify) if result])
        if best:
            best.pop("username", None)
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
    (out / "kit.json").write_text(json.dumps(kit(p, cache, now, best), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
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
    lastfm_top(p, cache)  # the "On rotation" card: Last.fm's top tracks of the last month
    service = now_service(p)
    heard = None if service is None else [service["now"]] if service.get("now") else []
    now = now_data(p, cache, spotify_accounts(p), heard=heard)
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
    # The deck comes from the Worker when there is one (drawn on each visit), else from Pages (redrawn every 5 minutes).
    worker = p.get("listening", {}).get("worker", "").strip()
    live_base = (worker.rstrip("/") + "/") if worker else (cache.get("pages_url") if cache.get("live") else None)
    hrefs = live_links(live_base) if live_base else now_links(data["now"], fallback_link(cache, p))
    folder = ROOT / "img"
    folder.mkdir(exist_ok=True)
    (folder / "contributions.stl").unlink(missing_ok=True)  # the 3D calendar of the previous design
    items = page(p, data, hrefs)
    rows = list(rows_of(items))

    written = write_images(rows, folder)
    for stale in folder.rglob("*.svg"):
        if stale not in written:
            stale.unlink()
    for empty in sorted(folder.iterdir()):
        if empty.is_dir() and not any(empty.iterdir()):
            empty.rmdir()

    (ROOT / "README.md").write_text(readme(items, p, live_base, raw_base(p)), encoding="utf-8")
    # Only what the page uses is kept; older designs cached more.
    cache.pop("recent", None)
    cache.get("extra", {}).pop("views", None)
    cache["stats"] = {key: value for key, value in (cache.get("stats") or {}).items() if key in ("stars", "contributions")}
    CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    cells = sum(len(row.cells) for row in rows)
    print(
        f"built {cells} linked images × {len(FOLDERS)} versions, {len(data['projects'])} projects, "
        f"{len(data['more'])} more, {len(data['archive'])} archive cards, {len(data['tracks'])} tracks, "
        f"now: {now_key(data['now'])}"
    )


if __name__ == "__main__":
    main()
