"""Everything the profile reads from the outside world: GitHub, Spotify, Last.fm and the view counter."""

import base64
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

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
    data = cache.setdefault("github", {"user": {}, "repos": {}})
    headers = github_headers()
    login = p["me"]["github"]
    try:
        user = fetch(f"https://api.github.com/users/{login}", headers)
        data["user"] = {"public_repos": user["public_repos"], "created_at": user["created_at"]}
    except Exception as error:
        print(f"github: keeping cached user ({error})", file=sys.stderr)
    for project in p["work"]["projects"]:
        name = project["repo"]
        try:
            repo = fetch(f"https://api.github.com/repos/{login}/{name}", headers)
        except Exception as error:
            print(f"github: keeping cached {name} ({error})", file=sys.stderr)
            continue
        if repo.get("private"):
            data["repos"].pop(name, None)
            continue
        previous = data["repos"].get(name, {})
        data["repos"][name] = {
            "description": repo.get("description") or "",
            "language": repo.get("language") or "",
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "url": repo.get("html_url") or f"https://github.com/{login}/{name}",
            "downloads": previous.get("downloads", 0),
            "version": previous.get("version", ""),
        }
        try:
            releases = fetch(f"https://api.github.com/repos/{login}/{name}/releases?per_page=100", headers) or []
            published = [r for r in releases if not r.get("draft")]
            stable = [r for r in published if not r.get("prerelease")]
            data["repos"][name]["downloads"] = sum(a.get("download_count", 0) for r in published for a in r.get("assets", []))
            data["repos"][name]["version"] = (stable or published)[0]["tag_name"] if published else ""
        except Exception as error:
            print(f"github: keeping cached releases for {name} ({error})", file=sys.stderr)
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
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        name description url stargazerCount forkCount pushedAt isArchived
        primaryLanguage { name }
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } }
      }
    }
  }
}
"""

CALENDAR_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions totalPullRequestContributions totalIssueContributions
      totalPullRequestReviewContributions totalRepositoriesWithContributedCommits
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
  }
}
"""

YEAR_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) { contributionsCollection(from: $from, to: $to) { contributionCalendar { totalContributions } } }
}
"""

# One small query each, so a field the token can't see doesn't sink the rest.
EXTRA_FIELDS = {
    "merged_prs": "pullRequests(states: MERGED) { totalCount }",
    "issues_all": "issues { totalCount }",
    "contributed_to": "repositoriesContributedTo(contributionTypes: [COMMIT, PULL_REQUEST, ISSUE], includeUserRepositories: false) { totalCount }",
}

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


def views_data(p, cache):
    """Reads the profile view counter (komarev.com). Reading it counts as one view."""
    login = p["me"]["github"]
    try:
        request = urllib.request.Request(f"https://komarev.com/ghpvc/?username={urllib.parse.quote(login)}",
                                         headers={"User-Agent": "robyrew-profile"})
        with urllib.request.urlopen(request, timeout=15) as response:
            svg = response.read().decode("utf-8", "replace")
        numbers = [m.replace(",", "") for m in re.findall(r">([\d,]+)<", svg)]
        if numbers:
            cache.setdefault("extra", {})["views"] = int(numbers[-1])
    except Exception as error:
        print(f"views: keeping cached count ({error})", file=sys.stderr)


def github_get(path, headers):
    return fetch(f"https://api.github.com{path}", headers)


def search_count(kind, query, headers):
    return github_get(f"/search/{kind}?q={urllib.parse.quote(query)}&per_page=1", headers)["total_count"]


def repos_rest(login, headers):
    """The same shape as REPOS_QUERY's nodes, from the REST API."""
    found, page = [], 1
    while True:
        batch = github_get(f"/users/{login}/repos?type=owner&sort=pushed&per_page=100&page={page}", headers) or []
        found += batch
        if len(batch) < 100:
            break
        page += 1
    repos = []
    for r in found:
        if r.get("fork") or r.get("private"):
            continue
        try:
            sizes = github_get(f"/repos/{login}/{r['name']}/languages", headers) or {}
        except Exception:
            sizes = {}
        repos.append({
            "name": r["name"],
            "description": r.get("description"),
            "url": r["html_url"],
            "stargazerCount": r.get("stargazers_count", 0),
            "forkCount": r.get("forks_count", 0),
            "pushedAt": r.get("pushed_at"),
            "isArchived": r.get("archived", False),
            "primaryLanguage": {"name": r["language"]} if r.get("language") else None,
            "languages": {"edges": [{"size": size, "node": {"name": name, "color": None}} for name, size in sizes.items()]},
        })
    return repos


def calendar_page(login, start=None, end=None):
    """Reads the public contribution calendar on github.com when the API won't give it."""
    url = f"https://github.com/users/{login}/contributions"
    if start:
        url += f"?from={start}&to={end}"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (profile builder)", "Accept": "text/html"})
    with urllib.request.urlopen(request, timeout=20) as response:
        page = response.read().decode("utf-8", "replace")
    counts = {}
    for tip in re.finditer(r'<tool-tip[^>]*\bfor="([^"]+)"[^>]*>\s*([^<]*?)\s*</tool-tip>', page):
        match = re.match(r"(No|\d[\d,]*)\s+contribution", tip.group(2))
        if match:
            counts[tip.group(1)] = 0 if match.group(1) == "No" else int(match.group(1).replace(",", ""))
    days = {}
    for cell in re.finditer(r"<td\b[^>]*>", page):
        tag = cell.group(0)
        day = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', tag)
        if not day:
            continue
        ident = re.search(r'\bid="([^"]+)"', tag)
        level = re.search(r'data-level="(\d)"', tag)
        count = counts.get(ident.group(1)) if ident else None
        days[day.group(1)] = count if count is not None else (int(level.group(1)) if level else 0)
    total = re.search(r"([\d,]+)\s+contributions?\s+in\s+(?:the\s+last\s+year|\d{4})", page)
    if not days and not total:
        raise RuntimeError("no calendar on the page")
    return (int(total.group(1).replace(",", "")) if total else sum(days.values())), days


def as_weeks(days):
    weeks, week = [], []
    for day in sorted(days):
        if week and date.fromisoformat(day).isoweekday() % 7 == 0:
            weeks.append(week)
            week = []
        week.append((day, days[day]))
    return weeks + [week] if week else weeks


def stats_data(p, cache):
    """Activity and popularity numbers. Each piece is optional and falls back to the REST API or the public page."""
    headers = github_headers()
    authed = "Authorization" in headers
    login = p["me"]["github"]
    now = datetime.now(timezone.utc)
    year_ago = now - timedelta(days=365)
    stats = dict(cache.get("stats", {}))

    def attempt(label, fn):
        try:
            return fn()
        except Exception as error:
            print(f"github: {label} unavailable ({error})", file=sys.stderr)
            return None

    def graphql_repos():
        repos, after = [], None
        while True:
            page = graphql(REPOS_QUERY, {"login": login, "after": after}, headers)["user"]["repositories"]
            repos += page["nodes"]
            if not page["pageInfo"]["hasNextPage"]:
                return repos
            after = page["pageInfo"]["endCursor"]

    repos = attempt("repositories via GraphQL", graphql_repos) if authed else None
    if repos is None:
        repos = attempt("repositories via REST", lambda: repos_rest(login, headers))
    if repos is not None:
        sizes, colors = {}, {}
        for repo in repos:
            for edge in repo["languages"]["edges"]:
                name = edge["node"]["name"]
                sizes[name] = sizes.get(name, 0) + edge["size"]
                colors[name] = edge["node"].get("color") or LANGUAGE_COLORS.get(name) or "#9CA3AF"
        total = sum(sizes.values()) or 1
        ranked = sorted(sizes.items(), key=lambda kv: -kv[1])
        languages = [[name, round(100 * size / total, 1), colors[name]] for name, size in ranked[:7]]
        rest = 100 - sum(share for _, share, _ in languages)
        if len(ranked) > 7 and rest > 0.05:
            languages.append(["Other", round(rest, 1), "#8B949E"])
        stats.update({
            "languages": languages,
            "stars": sum(r["stargazerCount"] for r in repos),
            "forks": sum(r["forkCount"] for r in repos),
            "original": len(repos),
        })
        cache["recent"] = [
            {
                "name": r["name"],
                "description": r["description"] or "",
                "url": r["url"],
                "stars": r["stargazerCount"],
                "language": (r["primaryLanguage"] or {}).get("name", ""),
                "pushed": r["pushedAt"],
            }
            for r in sorted(repos, key=lambda r: r["pushedAt"] or "", reverse=True)
            if not r["isArchived"]
        ][:100]

    variables = {"login": login, "from": year_ago.isoformat(), "to": now.isoformat()}
    collection = attempt("contributions via GraphQL", lambda: graphql(CALENDAR_QUERY, variables, headers)["user"]["contributionsCollection"]) if authed else None
    if collection:
        stats["contributions"] = collection["contributionCalendar"]["totalContributions"]
        stats["calendar"] = [
            [(d["date"], d["contributionCount"]) for d in week["contributionDays"]]
            for week in collection["contributionCalendar"]["weeks"]
        ]
        stats.update({
            "commits": collection["totalCommitContributions"],
            "prs": collection["totalPullRequestContributions"],
            "issues": collection["totalIssueContributions"],
            "reviews": collection["totalPullRequestReviewContributions"],
            "repos_contributed": collection["totalRepositoriesWithContributedCommits"],
        })
    else:
        scraped = attempt("contribution calendar page", lambda: calendar_page(login))
        if scraped:
            stats["contributions"], days = scraped
            stats["calendar"] = as_weeks(days)
        start = year_ago.date().isoformat()
        for key, kind, query in (
            ("commits", "commits", f"author:{login} committer-date:>={start}"),
            ("prs", "issues", f"author:{login} type:pr created:>={start}"),
            ("issues", "issues", f"author:{login} type:issue created:>={start}"),
            ("reviews", "issues", f"reviewed-by:{login} type:pr created:>={start}"),
        ):
            value = attempt(f"{key} count", lambda kind=kind, query=query: search_count(kind, query, headers))
            if value is not None:
                stats[key] = value

    if stats.get("calendar"):
        days = [count for week in stats["calendar"] for _, count in week]
        longest = run = 0
        for count in days:
            run = run + 1 if count else 0
            longest = max(longest, run)
        streak = 0
        for i, count in enumerate(reversed(days)):
            if count:
                streak += 1
            elif i:  # today may still be empty
                break
        weekdays = [0] * 7
        best = ("", 0)
        for week in stats["calendar"]:
            for day, count in week:
                weekdays[date.fromisoformat(day).weekday()] += count
                if count > best[1]:
                    best = (day, count)
        stats.update({
            "active_days": sum(1 for count in days if count),
            "streak": streak,
            "longest": longest,
            "busiest": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][weekdays.index(max(weekdays))],
            "best_day": best[0],
            "best_count": best[1],
        })

    for key, fragment in EXTRA_FIELDS.items():
        query = f"query($login: String!) {{ user(login: $login) {{ x: {fragment} }} }}"
        value = attempt(key, lambda query=query: graphql(query, {"login": login}, headers)["user"]["x"]["totalCount"]) if authed else None
        if value is not None:
            stats[key] = value
    for key, query in (("merged_prs", f"author:{login} type:pr is:merged"), ("issues_all", f"author:{login} type:issue")):
        if key not in stats:
            value = attempt(key, lambda query=query: search_count("issues", query, headers))
            if value is not None:
                stats[key] = value

    user = attempt("user", lambda: github_get(f"/users/{login}", headers)) or {}
    if user:
        stats.update({"followers": user.get("followers", 0), "gists": user.get("public_gists", 0), "joined": user.get("created_at", "")})
    orgs = attempt("organizations", lambda: github_get(f"/users/{login}/orgs", headers))
    if orgs is not None:
        stats["orgs"] = len(orgs)

    joined = stats.get("joined")
    if joined:
        use_graphql = authed

        def yearly():
            nonlocal use_graphql
            total = 0
            for year in range(int(joined[:4]), now.year + 1):
                start, end = f"{year}-01-01", f"{year}-12-31"
                if use_graphql:
                    try:
                        window = {"login": login, "from": f"{start}T00:00:00Z",
                                  "to": f"{end}T23:59:59Z" if year < now.year else now.isoformat()}
                        total += graphql(YEAR_QUERY, window, headers)["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
                        continue
                    except Exception:
                        use_graphql = False
                total += calendar_page(login, start, end)[0]
            return total

        value = attempt("all-time contributions", yearly)
        if value is not None:
            stats["all_time"] = value
    if stats:
        cache["stats"] = stats


def spotify_accounts():
    """Up to five Spotify accounts, in priority order. They can share one app (client ID and secret)."""
    shared_id, shared_secret = os.environ.get("SPOTIFY_CLIENT_ID"), os.environ.get("SPOTIFY_CLIENT_SECRET")
    accounts = []
    for n in range(1, 6):
        refresh = os.environ.get(f"SPOTIFY_REFRESH_TOKEN_{n}") or (os.environ.get("SPOTIFY_REFRESH_TOKEN") if n == 1 else None)
        client_id = os.environ.get(f"SPOTIFY_CLIENT_ID_{n}") or shared_id
        secret = os.environ.get(f"SPOTIFY_CLIENT_SECRET_{n}") or shared_secret
        if refresh and client_id and secret:
            accounts.append((n, client_id, secret, refresh))
    return accounts


def spotify_token(client_id, secret, refresh):
    auth = base64.b64encode(f"{client_id}:{secret}".encode()).decode()
    return fetch(
        "https://accounts.spotify.com/api/token",
        {"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"},
        urllib.parse.urlencode({"grant_type": "refresh_token", "refresh_token": refresh}).encode(),
    )["access_token"]


def smallest_image(images, minimum=64):
    images = [i for i in images or [] if i.get("url")]
    if not images:
        return ""
    fitting = [i for i in images if (i.get("width") or 0) >= minimum]
    return min(fitting or images, key=lambda i: i.get("width") or 0)["url"]


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


def spotify_top(p, cache, token):
    limit = int(p.get("listening", {}).get("tracks", 5))
    bearer = {"Authorization": f"Bearer {token}"}
    try:
        items = fetch(f"https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit={limit}", bearer)["items"]
    except Exception as error:
        print(f"spotify: keeping cached top tracks ({error})", file=sys.stderr)
        return
    if items:
        cache["top_tracks"] = [
            {
                "name": item["name"],
                "artist": ", ".join(a["name"] for a in item["artists"]),
                "ms": item["duration_ms"],
                "cover": smallest_image(item.get("album", {}).get("images")),
                "source": "Spotify",
                "url": item.get("external_urls", {}).get("spotify", ""),
                "artist_url": (item["artists"][0].get("external_urls", {}).get("spotify", "") if item["artists"] else ""),
                "plays_url": item.get("external_urls", {}).get("spotify", ""),
            }
            for item in items
        ]
        return True


def spotify_context(context, item, bearer):
    """What the song is playing from: (kind, name, url)."""
    if not context:
        album = item.get("album") or {}
        return ("Album", album.get("name", ""), album.get("external_urls", {}).get("spotify", "")) if album else ("", "", "")
    kind = context.get("type")
    url = context.get("external_urls", {}).get("spotify", "")
    if kind == "playlist":
        try:
            playlist = fetch(f'https://api.spotify.com/v1/playlists/{context["uri"].split(":")[-1]}?fields=name', bearer)
            return "Playlist", playlist["name"], url
        except Exception:
            return "Playlist", "A playlist", url
    if kind == "album":
        return "Album", item.get("album", {}).get("name", ""), url
    if kind == "artist":
        return "Radio", f'{item["artists"][0]["name"]} radio' if item.get("artists") else "Artist radio", url
    if kind == "collection":
        return "Library", "Liked Songs", "https://open.spotify.com/collection/tracks"
    return "", "", url


def spotify_item(item, context, bearer, user, playing, paused, device, when):
    kind, name, url = spotify_context(context, item, bearer)
    artists = item.get("artists") or []
    song = item.get("external_urls", {}).get("spotify", "")
    return {
        "playing": playing,
        "paused": paused,
        "title": item.get("name", ""),
        "artist": ", ".join(a["name"] for a in artists) or item.get("show", {}).get("name", ""),
        "cover": smallest_image(item.get("album", {}).get("images") or item.get("images")),
        "context": name,
        "context_kind": kind,
        "device": device.get("name", ""),
        "device_type": device.get("type", ""),
        "user": user.get("name", ""),
        "platform": "Spotify",
        "when": when,
        "song_url": song,
        "artist_url": artists[0].get("external_urls", {}).get("spotify", "") if artists else "",
        "context_url": url,
        "user_url": user.get("url", ""),
        "play_url": song,
    }


def spotify_now(token, user=None):
    bearer = {"Authorization": f"Bearer {token}"}
    if not isinstance(user, dict) or not user.get("name"):
        me = fetch("https://api.spotify.com/v1/me", bearer) or {}
        user = {"name": me.get("display_name") or me.get("id") or "", "url": me.get("external_urls", {}).get("spotify", "")}
    player = fetch("https://api.spotify.com/v1/me/player?additional_types=track,episode", bearer)
    if player and player.get("item"):
        playing = bool(player.get("is_playing"))
        return spotify_item(player["item"], player.get("context"), bearer, user, playing, not playing,
                            player.get("device") or {}, datetime.now(timezone.utc).isoformat(timespec="minutes"))
    recent = fetch("https://api.spotify.com/v1/me/player/recently-played?limit=1", bearer)
    if recent and recent.get("items"):
        play = recent["items"][0]
        return spotify_item(play["track"], play.get("context"), bearer, user, False, False, {}, play.get("played_at", ""))
    return None


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
        "cover": lastfm_image(track.get("image")),
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


def now_data(p, cache, accounts):
    """Spotify accounts, then Last.fm accounts: the first one playing wins, else the most recent play anywhere."""
    users = cache.setdefault("spotify_users", {})
    spotify = []
    for n, client_id, secret, refresh in accounts:
        try:
            result = spotify_now(spotify_token(client_id, secret, refresh), users.get(str(n)))
        except Exception as error:
            print(f"spotify {n}: no playback state ({error})", file=sys.stderr)
            continue
        if not result:
            continue
        users[str(n)] = {"name": result["user"], "url": result["user_url"]}
        result["account"] = n
        if result["playing"]:
            return result
        spotify.append(result)
    scrobbled = []
    for i, entry in enumerate(lastfm_users(p)):
        try:
            result = lastfm_now(entry, 10 + i)
        except Exception as error:
            print(f"last.fm {entry['user']}: no recent tracks ({error})", file=sys.stderr)
            continue
        if not result:
            continue
        if any((result["title"], result["artist"]) == (c["title"], c["artist"]) for c in spotify):
            continue  # Spotify scrobbles to Last.fm too; that's the same play
        if result["playing"]:
            return result
        scrobbled.append(result)
    candidates = spotify + scrobbled
    if not candidates:
        return cache.get("now")
    return max(candidates, key=lambda c: (c.get("when") or "", -c.get("account", 9)))


def now_key(now):
    if not now:
        return "off"
    return "|".join(str(now.get(k, "")) for k in ("playing", "paused", "title", "artist", "context", "device", "platform"))
