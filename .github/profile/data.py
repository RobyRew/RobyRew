"""Everything the profile reads from the outside world: GitHub, Spotify and Last.fm."""

import asyncio
import importlib.util
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

from canvas import LANGUAGES


def fetch(url, headers=None, data=None):
    request = urllib.request.Request(url, data=data, headers={"User-Agent": "robyrew-profile", **(headers or {})})
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read()
    return json.loads(body) if body else None


def github_headers():
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GH_STATS_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def github_data(p, cache):
    """My account, and every public repository I own (forks aside) with its release downloads and newest tag."""
    data = cache.setdefault("github", {})
    data.setdefault("user", {})
    headers = github_headers()
    login = p["me"]["github"]
    try:
        user = fetch(f"https://api.github.com/users/{login}", headers)
        data["user"] = {"public_repos": user["public_repos"], "created_at": user["created_at"]}
    except Exception as error:
        print(f"github: keeping cached user ({error})", file=sys.stderr)
    nodes = None
    if "Authorization" in headers:
        try:
            nodes = repos_graphql(login, headers)
        except Exception as error:
            print(f"github: repositories via GraphQL unavailable ({error})", file=sys.stderr)
    if nodes is None:
        try:
            nodes = repos_rest(login, headers)
        except Exception as error:
            print(f"github: keeping cached repositories ({error})", file=sys.stderr)
    if nodes is not None:
        old = data.get("repos", {})
        repos = {}
        for node in nodes:
            name = node["name"]
            previous = old.get(name, {})
            language = node.get("primaryLanguage") or {}
            repo = {
                "description": node.get("description") or "",
                "language": language.get("name") or "",
                "language_color": language.get("color") or "",
                "stars": node.get("stargazerCount", 0),
                "forks": node.get("forkCount", 0),
                "url": node.get("url") or f"https://github.com/{login}/{name}",
                "homepage": node.get("homepageUrl") or "",
                "pushed": node.get("pushedAt") or "",
                "archived": bool(node.get("isArchived")),
                "downloads": previous.get("downloads", 0),
                "version": previous.get("version", ""),
            }
            # GraphQL says how many releases there are; the REST fallback doesn't (None), so it asks every repo.
            if node.get("releases") == 0:
                repo["downloads"], repo["version"] = 0, ""
            else:
                try:
                    repo["downloads"], repo["version"] = releases(login, name, headers)
                except Exception as error:
                    print(f"github: keeping cached releases for {name} ({error})", file=sys.stderr)
            repos[name] = repo
        data["repos"] = repos
    # The Pages address needs the workflow's own token; PROFILE_TOKEN has no access to repo settings.
    repository = os.environ.get("GITHUB_REPOSITORY", f"{login}/{login}")
    own = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        own["Authorization"] = f'Bearer {os.environ["GITHUB_TOKEN"]}'
    try:
        pages = fetch(f"https://api.github.com/repos/{repository}/pages", own)
        if pages and pages.get("html_url"):
            cache["pages_url"] = pages["html_url"].rstrip("/") + "/"
    except Exception as error:
        print(f"github: pages address not readable ({error})", file=sys.stderr)
        if not cache.get("pages_url") and "/" in repository:
            owner, name = repository.split("/", 1)
            cache["pages_url"] = f"https://{owner.lower()}.github.io/{name}/"


REPOS_QUERY = """
query($login: String!, $after: String) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100, after: $after,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name description url homepageUrl stargazerCount forkCount pushedAt isArchived
        primaryLanguage { name color }
        releases { totalCount }
      }
    }
  }
}
"""

YEAR_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) { contributionsCollection(from: $from, to: $to) { contributionCalendar { totalContributions } } }
}
"""

LANGUAGE_COLORS = {
    **LANGUAGES, "Kotlin": "#A97BFF", "Java": "#B07219", "C": "#555555", "C++": "#F34B7D", "C#": "#178600",
    "Go": "#00ADD8", "Rust": "#DEA584", "Ruby": "#701516", "PHP": "#4F5D95", "Objective-C": "#438EFF",
    "Objective-C++": "#6866FB", "Dockerfile": "#384D54", "Vue": "#41B883", "SCSS": "#C6538C", "Makefile": "#427819",
    "Lua": "#000080", "Dart": "#00B4AB", "Jupyter Notebook": "#DA5B0B", "PowerShell": "#012456", "Batchfile": "#C1F12E",
    "Assembly": "#6E4C13", "Perl": "#0298C3", "AppleScript": "#101F1F", "Metal": "#8F14E9", "MDX": "#FCB32C",
    "Svelte": "#FF3E00", "Astro": "#FF5A03", "Nix": "#7E7EFF", "Zig": "#EC915C", "Haskell": "#5E5086",
}


def graphql(query, variables, headers):
    body = json.dumps({"query": query, "variables": variables}).encode()
    result = fetch("https://api.github.com/graphql", {**headers, "Content-Type": "application/json"}, body)
    if result.get("errors"):
        raise RuntimeError(result["errors"][0].get("message"))
    return result["data"]


def github_get(path, headers):
    return fetch(f"https://api.github.com{path}", headers)


def repos_graphql(login, headers):
    nodes, after = [], None
    while True:
        page = graphql(REPOS_QUERY, {"login": login, "after": after}, headers)["user"]["repositories"]
        for node in page["nodes"]:
            nodes.append({**node, "releases": (node.get("releases") or {}).get("totalCount")})
        if not page["pageInfo"]["hasNextPage"]:
            return nodes
        after = page["pageInfo"]["endCursor"]


def repos_rest(login, headers):
    """The same shape as repos_graphql, from the REST API (which doesn't count releases)."""
    found, page = [], 1
    while True:
        batch = github_get(f"/users/{login}/repos?type=owner&sort=pushed&per_page=100&page={page}", headers) or []
        found += batch
        if len(batch) < 100:
            break
        page += 1
    return [
        {
            "name": r["name"],
            "description": r.get("description"),
            "url": r["html_url"],
            "homepageUrl": r.get("homepage"),
            "stargazerCount": r.get("stargazers_count", 0),
            "forkCount": r.get("forks_count", 0),
            "pushedAt": r.get("pushed_at"),
            "isArchived": r.get("archived", False),
            "primaryLanguage": {"name": r["language"], "color": LANGUAGE_COLORS.get(r["language"])} if r.get("language") else None,
            "releases": None,
        }
        for r in found
        if not r.get("fork") and not r.get("private")
    ]


def releases(login, name, headers):
    """Downloads across a repository's published releases, and its newest stable tag."""
    found, page = [], 1
    while True:
        batch = github_get(f"/repos/{login}/{name}/releases?per_page=100&page={page}", headers) or []
        found += batch
        if len(batch) < 100:
            break
        page += 1
    published = [r for r in found if not r.get("draft")]
    stable = [r for r in published if not r.get("prerelease")]
    downloads = sum(a.get("download_count", 0) for r in published for a in r.get("assets", []))
    return downloads, ((stable or published)[0]["tag_name"] if published else "")


def calendar_page(login):
    """The "contributions in the last year" count on my public profile, when the API won't give it."""
    request = urllib.request.Request(f"https://github.com/users/{login}/contributions",
                                     headers={"User-Agent": "Mozilla/5.0 (profile builder)", "Accept": "text/html"})
    with urllib.request.urlopen(request, timeout=20) as response:
        page = response.read().decode("utf-8", "replace")
    total = re.search(r"([\d,]+)\s+contributions?\s+in\s+the\s+last\s+year", page)
    if not total:
        raise RuntimeError("no count on the page")
    return int(total.group(1).replace(",", ""))


def stats_data(p, cache):
    """The numbers on the page that aren't per repository: stars on my own repos, contributions in the last year."""
    headers = github_headers()
    login = p["me"]["github"]
    now = datetime.now(timezone.utc)
    stats = {key: value for key, value in cache.get("stats", {}).items() if key in ("stars", "contributions")}
    repos = cache.get("github", {}).get("repos")
    if repos:
        stats["stars"] = sum(repo.get("stars", 0) for repo in repos.values())
    total = None
    if "Authorization" in headers:
        try:
            window = {"login": login, "from": (now - timedelta(days=365)).isoformat(), "to": now.isoformat()}
            total = graphql(YEAR_QUERY, window, headers)["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
        except Exception as error:
            print(f"github: contributions via GraphQL unavailable ({error})", file=sys.stderr)
    if total is None:
        try:
            total = calendar_page(login)
        except Exception as error:
            print(f"github: keeping cached contributions ({error})", file=sys.stderr)
    if total is not None:
        stats["contributions"] = total
    cache["stats"] = stats


# Spotify, through SpotAPI (https://github.com/Aran404/SpotAPI): each account's own web session, read from its
# Spotify Connect state, the way the web player sees it. Read only: SpotAPI observes the account's players and sends
# no playback commands. Last.fm accounts are numbered from 10, so Spotify takes slots 1 to 9.
SPOTIFY_SLOTS = 9
SPOTIFY_TIMEOUT = 15  # seconds for each step of an account's Connect handshake


def spotify_accounts(p):
    """The Spotify accounts to watch, in priority order: (slot, cookie, label).

    The cookie is the account's web session, saved as the secret SPOTIFY_COOKIE_<slot>: a Cookie header copied from
    open.spotify.com, or just the value of its sp_dc cookie. `[[listening.spotify]]` blocks in profile.toml can give
    the accounts a name for the deck, in the same order."""
    labels = [entry.get("label", "") for entry in p.get("listening", {}).get("spotify", [])]
    accounts = []
    for n in range(1, SPOTIFY_SLOTS + 1):
        cookie = (os.environ.get(f"SPOTIFY_COOKIE_{n}") or (os.environ.get("SPOTIFY_COOKIE", "") if n == 1 else "")).strip()
        if not cookie:
            continue
        accounts.append((n, cookie if "=" in cookie else f"sp_dc={cookie}", labels[n - 1] if n <= len(labels) else ""))
    return accounts


PLAY_SEARCH = {
    "Spotify": "https://open.spotify.com/search/{q}",
    "YouTube Music": "https://music.youtube.com/search?q={q}",
    "Apple Music": "https://music.apple.com/search?term={q}",
    "Last.fm": "https://www.last.fm/search?q={q}",
}


def play_url(platform, title, artist):
    """Where "play this" goes: a search for the song in the app it was played on."""
    template = PLAY_SEARCH.get(platform, PLAY_SEARCH["Last.fm"])
    return template.format(q=urllib.parse.quote(f"{title} {artist}".strip()))


def lastfm_music_url(*parts):
    return "https://www.last.fm/music/" + "/".join(urllib.parse.quote_plus(part) for part in parts)


def open_url(uri):
    """A Spotify URI as an open.spotify.com address: spotify:track:ID becomes /track/ID, Liked Songs /collection."""
    parts = (uri or "").split(":")
    if len(parts) == 3 and parts[0] == "spotify":
        return f"https://open.spotify.com/{parts[1]}/{parts[2]}"
    if len(parts) >= 4 and parts[0] == "spotify" and parts[1] == "user" and parts[3] == "collection":
        return "https://open.spotify.com/collection/tracks"
    return ""


CONTEXT_KINDS = {"album": "Album", "playlist": "Playlist", "artist": "Radio", "collection": "Library", "show": "Podcast"}


def spotify_context(uri, album):
    """What the song plays from, as (kind, name, url). SpotAPI's snapshot names the album; other contexts get a kind."""
    parts = (uri or "").split(":")
    kind = "collection" if "collection" in parts else (parts[1] if len(parts) >= 3 else "")
    if kind in ("", "album"):
        return ("Album", album, open_url(uri)) if album else ("", "", "")
    names = {"collection": "Liked Songs", "playlist": "A playlist", "artist": "Artist radio", "show": "A podcast"}
    return CONTEXT_KINDS.get(kind, ""), names.get(kind, ""), open_url(uri)


def details_fields(details):
    """Title, artists, album and a cover from SpotAPI's TrackDetails, for when the Connect event leaves them out."""
    album = getattr(details, "album_of_track", None)
    sources = getattr(getattr(album, "cover_art", None), "sources", None) or []
    sized = sorted((s for s in sources if getattr(s, "url", "")), key=lambda s: abs((getattr(s, "width", 0) or 0) - 300))
    artists = []
    for group in (getattr(details, "first_artist", None), getattr(details, "other_artists", None)):
        for item in getattr(group, "items", None) or []:
            name = getattr(getattr(item, "profile", None), "name", "")
            if name:
                artists.append(name)
    return getattr(details, "name", ""), ", ".join(artists), getattr(album, "name", "") or "", sized[0].url if sized else ""


def when_from(stamp):
    """A Connect timestamp (milliseconds since 1970) as the ISO minute the deck shows."""
    if not stamp:
        return datetime.now(timezone.utc).isoformat(timespec="minutes")
    seconds = stamp / 1000 if stamp > 10**11 else stamp
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat(timespec="minutes")


class SpotifyStep(Exception):
    """Which step of an account's check failed (sign-in, connect, track details), with the error it raised."""

    def __init__(self, step, error):
        super().__init__(step)
        self.step, self.error = step, error


def safe_message(error):
    """An error and its causes in one line, safe for a public log: web addresses cut to their host, anything long
    enough to be a token or a cookie replaced by an ellipsis."""
    parts, seen = [], set()
    while error is not None and id(error) not in seen and len(parts) < 4:
        seen.add(id(error))
        text = " ".join(str(error).split())
        text = re.sub(r"(?:wss?|https?)://([^/\s?#]+)\S*", r"\1/…", text)
        text = re.sub(r"[A-Za-z0-9_\-.%+/=]{28,}", "…", text)
        status = getattr(error, "status_code", None) or getattr(error, "status", None)
        parts.append(f"{type(error).__name__}{f' {status}' if isinstance(status, int) else ''}{f': {text[:140]}' if text else ''}")
        error = error.__cause__ or error.__context__
    return " <- ".join(parts)


async def spotify_observe(n, cookie, label, known):
    """One account: sign in with its cookie, open a read-only Connect observer and take the snapshot of its players.
    Returns the deck's fields, or None when the account has nothing on its players."""
    from spotapi import Account, AsyncClient, Player

    step = "sign-in"
    try:
        async with await AsyncClient.from_cookies(cookie) as client:
            step = "connect"
            player = Player(client)
            async with player.connect(timeout=SPOTIFY_TIMEOUT):
                state = player.state
                track = state.track if state else None
                if track is None:
                    return None
                title, artist, album, cover = track.name, track.artist, track.album, track.image_url or ""
                if not (title and artist):
                    step = "track details"
                    details = await player.current_track_details()
                    if details is not None and details.uri == track.uri:
                        title, artist, album, cover = (new or old for new, old in zip(details_fields(details), (title, artist, album, cover)))
                device = next((d for d in player.devices if d.id == state.active_device_id), None)
            username = (known or {}).get("username", "")
            if not username:
                try:
                    username = (await Account(client).get_profile()).username
                except Exception as error:
                    print(f"spotify {n}: no profile name ({safe_message(error)})", file=sys.stderr)
    except Exception as error:
        raise SpotifyStep(step, error) from error
    if not title:
        return None
    playing = bool(state.is_playing and not state.is_paused)
    kind, name, context_url = spotify_context(state.context_uri, album)
    song = open_url(track.uri)
    return {
        "playing": playing,
        "paused": bool(state.is_paused),
        "title": title,
        "artist": artist,
        "cover": cover,
        "context": name,
        "context_kind": kind,
        "device": device.name if device else "",
        "device_type": (device.type or "").lower() if device else "",
        "user": label or username,
        "username": username,
        "platform": "Spotify",
        "when": when_from(state.timestamp),
        "song_url": song,
        "artist_url": "",
        "context_url": context_url,
        "user_url": f"https://open.spotify.com/user/{urllib.parse.quote(username)}" if username else "",
        "play_url": song or play_url("Spotify", title, artist),
    }


def spotify_now(accounts, users):
    """Every account at once, each bounded in time. A list in account order: the account's fields, or None.

    Only error types and HTTP statuses are logged: a SpotAPI message or URL can carry a token or a cookie."""
    if not accounts:
        return []
    if importlib.util.find_spec("spotapi") is None:  # a local build without it still works
        print("spotify: SpotAPI isn't installed (pip install spotapi), skipping the Spotify accounts", file=sys.stderr)
        return [None] * len(accounts)

    async def one(n, cookie, label):
        try:
            return await asyncio.wait_for(spotify_observe(n, cookie, label, users.get(str(n))), SPOTIFY_TIMEOUT * 4)
        except SpotifyStep as failure:
            hint = {"LoginExpired": f" (sign in again and update SPOTIFY_COOKIE_{n})",
                    "TimeoutError": " (no player snapshot: no device signed in?)"}.get(type(failure.error).__name__, "")
            print(f"spotify {n}: no playback state at {failure.step}{hint}: {safe_message(failure.error)}", file=sys.stderr)
        except Exception as error:
            print(f"spotify {n}: no playback state: {safe_message(error)}", file=sys.stderr)
        return None

    async def everyone():
        return await asyncio.gather(*(one(*account) for account in accounts))

    return asyncio.run(everyone())


def spotify_best(results):
    """The account to show: the first one playing, else the latest play."""
    found = [r for r in results if r]
    playing = [r for r in found if r["playing"]]
    if playing:
        return playing[0]
    return max(found, key=lambda r: r.get("when") or "") if found else None


LASTFM_BLANK = "2a96cbd8b46e442fc41c2b86b821562f"  # Last.fm's grey star placeholder


def lastfm(method, **params):
    key = os.environ.get("LASTFM_API_KEY")
    if not key:
        return None
    query = urllib.parse.urlencode({"method": method, "api_key": key, "format": "json", **params})
    return fetch(f"https://ws.audioscrobbler.com/2.0/?{query}")


def lastfm_users(p):
    """Last.fm accounts in priority order, checked after the Spotify ones."""
    listening = p.get("listening", {})
    users = []
    # The LASTFM_USERS repository variable comes first: "name:Platform, other:YouTube Music".
    for item in (os.environ.get("LASTFM_USERS") or "").split(","):
        name, _, platform = item.strip().partition(":")
        if name.strip():
            users.append({"user": name.strip(), "platform": platform.strip()})
    users += [dict(u) for u in listening.get("lastfm", []) if u.get("user")]
    if listening.get("lastfm_user"):
        users.append({"user": listening["lastfm_user"], "platform": listening.get("lastfm_platform", "")})
    seen, unique = set(), []
    for entry in users:
        if entry["user"].lower() not in seen:
            seen.add(entry["user"].lower())
            unique.append(entry)
    return unique[:5]


def lastfm_image(images, size="large"):
    by_size = {i.get("size"): i.get("#text") for i in images or []}
    url = by_size.get(size) or by_size.get("large") or by_size.get("medium") or by_size.get("extralarge") or ""
    return "" if LASTFM_BLANK in url else url


def as_jpeg(url):
    """Last.fm sends a cover as JPEG when its name ends in .jpg: about a fifth of the PNG's weight."""
    return url[:-4] + ".jpg" if url.endswith(".png") and ".fastly.net/" in url else url


def lastfm_now(entry, account):
    data = lastfm("user.getrecenttracks", user=entry["user"], limit=1, extended=1)
    if not data:
        return None
    tracks = data["recenttracks"]["track"]
    if isinstance(tracks, dict):
        tracks = [tracks]
    if not tracks:
        return None
    track = tracks[0]
    playing = track.get("@attr", {}).get("nowplaying") == "true"
    when = ""
    if not playing and track.get("date", {}).get("uts"):
        when = datetime.fromtimestamp(int(track["date"]["uts"]), timezone.utc).isoformat(timespec="minutes")
    artist = track.get("artist", {})
    artist_name = artist.get("name") or artist.get("#text", "")
    album = track.get("album", {}).get("#text", "")
    title = track.get("name", "")
    platform = entry.get("platform") or "Last.fm"
    return {
        "playing": playing,
        "paused": False,
        "title": title,
        "artist": artist_name,
        "cover": as_jpeg(lastfm_image(track.get("image"))),  # 174 px, the record's label
        "context": album,
        "context_kind": "Album" if album else "",
        "device": "",
        "device_type": "",
        "user": entry["user"],
        "platform": platform,
        "when": when,
        "account": account,
        "song_url": track.get("url") or lastfm_music_url(artist_name, "_", title),
        "artist_url": artist.get("url") or lastfm_music_url(artist_name),
        "context_url": lastfm_music_url(artist_name, album) if album else "",
        "user_url": f"https://www.last.fm/user/{urllib.parse.quote(entry['user'])}",
        "play_url": play_url(platform, title, artist_name),
    }


def lastfm_top(p, cache):
    users = lastfm_users(p)
    if not users or not os.environ.get("LASTFM_API_KEY"):
        return
    limit = int(p.get("listening", {}).get("tracks", 5))
    try:
        user = users[0]["user"]
        items = lastfm("user.gettoptracks", user=user, period="1month", limit=limit)["toptracks"]["track"]
        info = lastfm("user.getinfo", user=user)["user"]
        cache.setdefault("extra", {})["scrobbles"] = int(info.get("playcount") or 0)
        cache["extra"]["lastfm_url"] = f"https://www.last.fm/user/{urllib.parse.quote(user)}"
    except Exception as error:
        print(f"last.fm: keeping cached top tracks ({error})", file=sys.stderr)
        return
    tracks = []
    for item in items[:limit]:
        artist = item.get("artist", {})
        artist_name = artist.get("name", "")
        cover = lastfm_image(item.get("image"), "medium")
        if not cover:
            try:
                album = lastfm("track.getInfo", artist=artist_name, track=item["name"])["track"].get("album", {})
                cover = lastfm_image(album.get("image"), "medium")
            except Exception:
                pass
        tracks.append({
            "name": item["name"],
            "artist": artist_name,
            "ms": int(item.get("duration") or 0) * 1000,
            "plays": int(item.get("playcount") or 0),
            "cover": cover,
            "source": "Last.fm",
            "url": item.get("url") or lastfm_music_url(artist_name, "_", item["name"]),
            "artist_url": artist.get("url") or lastfm_music_url(artist_name),
            "plays_url": f"https://www.last.fm/user/{urllib.parse.quote(user)}/library/music/"
                         f"{urllib.parse.quote_plus(artist_name)}/_/{urllib.parse.quote_plus(item['name'])}",
        })
    if tracks:
        cache["top_tracks"] = tracks


def now_data(p, cache, accounts, spotify=None):
    """Spotify accounts, then Last.fm accounts: the first one playing wins, else the most recent play anywhere.
    `spotify` is spotify_now()'s result when the caller has already asked."""
    users = cache.setdefault("spotify_users", {})
    if spotify is None:
        spotify = spotify_now(accounts, users)
    heard = []
    for (n, _, _), result in zip(accounts, spotify):
        if not result:
            continue
        result = dict(result, account=n)
        username = result.pop("username", "")
        if username:
            users[str(n)] = {"username": username, "url": result["user_url"]}
        if result["playing"]:
            return result
        heard.append(result)
    scrobbled = []
    for i, entry in enumerate(lastfm_users(p)):
        try:
            result = lastfm_now(entry, 10 + i)
        except Exception as error:
            print(f"last.fm {entry['user']}: no recent tracks ({error})", file=sys.stderr)
            continue
        if not result:
            continue
        if any((result["title"], result["artist"]) == (c["title"], c["artist"]) for c in heard):
            continue  # Spotify scrobbles to Last.fm too; that's the same play
        if result["playing"]:
            return result
        scrobbled.append(result)
    candidates = heard + scrobbled
    if not candidates:
        return cache.get("now")
    return max(candidates, key=lambda c: (c.get("when") or "", -c.get("account", 9)))


def now_key(now):
    if not now:
        return "off"
    return "|".join(str(now.get(k, "")) for k in ("playing", "paused", "title", "artist", "context", "device", "platform"))
