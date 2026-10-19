# How this profile is built

`README.md` and everything in `img/` are generated. Don't edit them by hand.

- **Content** lives in [`profile.toml`](../../profile.toml) at the repo root. Change the text, push to `main`, and the
  *Refresh profile* workflow rebuilds the page. It also runs every morning to pick up new stars, repos,
  contribution stats and listening data.
- **Rendering** is [`build.py`](build.py). It writes every section as an SVG, in a light and a dark version,
  and embeds a small subset of Bricolage Grotesque and Geist Mono in each one (licence in [`fonts/OFL.txt`](fonts/OFL.txt)).
- **Last known data** (repos, stats, tracks) is saved in [`cache.json`](cache.json), so a failed API call
  never blanks the page.

Build locally:

```sh
pip install fonttools==4.67.0 brotli==1.2.0
python3 .github/profile/build.py --offline  # cached data only
```

Every command below runs on your Mac from the repo folder, with the GitHub CLI (`gh`) logged in.

## 1. Music

The deck under the record can read up to 5 Spotify accounts and up to 5 Last.fm accounts. Spotify accounts come
first, then the Last.fm ones in the order they appear in `profile.toml`; the first one that is playing wins.

### Last.fm (free, works for everything)

Since February 2026 Spotify only lets **Premium** accounts create Web API apps, so Last.fm is the way in for free
accounts. It also covers YouTube Music and Apple Music.

1. Make a free account at <https://www.last.fm> for each music account you want on the deck (one Spotify
   account can scrobble to one Last.fm account), and connect them:
   - **Spotify (free or Premium):** Last.fm → Settings → Applications → Spotify scrobbling.
   - **YouTube Music:** the Web Scrobbler browser extension, or Pano Scrobbler on Android.
   - **Apple Music:** the Last.fm desktop scrobbler on the Mac. On iPhone, a scrobbler app.
2. Get one API key at <https://www.last.fm/api/account/create> and save it:

   ```sh
   gh secret set LASTFM_API_KEY
   ```

3. In `profile.toml`, fill in the `[[listening.lastfm]]` blocks in priority order: the username, and the
   `platform` label to show (Last.fm can't tell which app played a song).

The first Last.fm account also supplies the "On rotation" top tracks and the scrobble count when Spotify isn't set up.

### Spotify Web API (optional, needs Premium)

Adds the device and playlist to the deck. The account that **owns** the app must have Spotify Premium; up to
5 accounts can connect to it.

1. Create an app at <https://developer.spotify.com/dashboard> with a Premium account. Use
   `http://127.0.0.1:8888/callback` as the redirect URI and tick **Web API** (it is greyed out without Premium).
2. In the app, open **Settings → User Management** and add the name and email of every account you will connect.
3. Connect each account, in priority order. Spotify shows which account it is approving; use **Not you?** to switch.

   ```sh
   python3 .github/profile/spotify_auth.py      # account 1
   python3 .github/profile/spotify_auth.py 2    # account 2, and so on up to 5
   ```

   Each run asks for the app's client ID and secret, then offers to save the secrets with `gh` for you.

## 2. Live deck (spinning record)

The README is only rebuilt once a day, so on its own the record always shows "last played" with the needle parked.
To make it live, a second workflow publishes the hero card to GitHub Pages every ten minutes. Nothing is committed
and no branch is created.

```sh
gh api -X POST repos/RobyRew/RobyRew/pages -f build_type=workflow || gh api -X PUT repos/RobyRew/RobyRew/pages -f build_type=workflow
gh variable set LIVE_NOW_PLAYING --body true
gh workflow run now-playing.yml
gh workflow run refresh.yml
```

The first run publishes the deck; the second switches the README over to it. Expect the card to lag the music by
up to about 15 minutes, since GitHub's scheduler and image cache both add delay.

## 3. Optional: richer stats

The activity and popularity cards use the workflow's own token, which sees public activity. To count private
contributions too, create a fine-grained token with read-only access and save it:

```sh
gh secret set PROFILE_TOKEN
```
