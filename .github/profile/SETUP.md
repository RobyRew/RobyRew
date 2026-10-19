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

## 1. Spotify

Gives the deck under the record (song, artist, playlist, device, you) and the "On rotation" top tracks.

1. Create an app at <https://developer.spotify.com/dashboard>. Use `http://127.0.0.1:8888/callback` as the
   redirect URI and tick **Web API**.
2. Run `python3 .github/profile/spotify_auth.py`, paste the client ID and secret, and approve access in the browser.
3. Save the three values it prints:

   ```sh
   gh secret set SPOTIFY_CLIENT_ID
   gh secret set SPOTIFY_CLIENT_SECRET
   gh secret set SPOTIFY_REFRESH_TOKEN
   ```

   Each command asks you to paste the value.

## 2. YouTube Music and Apple Music (through Last.fm)

Neither has a public "now playing" API, so the deck reads them from Last.fm instead.

1. Make a free account at <https://www.last.fm> and connect what you listen on:
   - **Spotify:** Last.fm → Settings → Applications → Spotify scrobbling.
   - **YouTube Music:** the Web Scrobbler browser extension, or Pano Scrobbler on Android.
   - **Apple Music:** the Last.fm desktop scrobbler on the Mac. On iPhone, a scrobbler app.
2. Get an API key at <https://www.last.fm/api/account/create>.
3. Save the API key:

   ```sh
   gh secret set LASTFM_API_KEY
   ```

4. In `profile.toml`, set `lastfm_user` to your Last.fm username. Set `lastfm_platform` to the app that is not
   Spotify (Last.fm can't tell which app played a song).

Spotify wins when it is playing. Otherwise the deck shows whatever Last.fm says is playing or played last.

## 3. Live deck (spinning record)

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

## 4. Optional: richer stats

The activity and popularity cards use the workflow's own token, which sees public activity. To count private
contributions too, create a fine-grained token with read-only access and save it:

```sh
gh secret set PROFILE_TOKEN
```
