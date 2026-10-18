# How this profile is built

`README.md` and everything in `img/` are generated. Don't edit them by hand.

- **Content** lives in [`profile.toml`](../../profile.toml) at the repo root. Change the text, push to `main`, and the
  *Refresh profile* workflow rebuilds the page. It also runs every morning to pick up new stars,
  repo counts and listening data.
- **Rendering** is [`build.py`](build.py). It writes every section as an SVG, in a light and a dark version,
  and embeds a small subset of Newsreader and DM Mono in each one (licence in [`fonts/OFL.txt`](fonts/OFL.txt)).
- **Last known data** (repo languages, stars, tracks) is saved in [`cache.json`](cache.json), so a failed API call
  never blanks the page.

Build locally:

```sh
pip install fonttools==4.67.0 brotli==1.2.0
python3 .github/profile/build.py            # live data
python3 .github/profile/build.py --offline  # cached data only
```

## Turning on "On rotation" (Spotify)

The card lists your top tracks from the last four weeks. It stays hidden until these three secrets exist:

1. Create an app at <https://developer.spotify.com/dashboard>. Use `http://127.0.0.1:8888/callback` as the
   redirect URI and pick **Web API**.
2. On your own machine, run `python3 .github/profile/spotify_auth.py`, paste the client ID and secret, and approve
   access in the browser.
3. In this repo, open **Settings → Secrets and variables → Actions** and add the three values it prints:
   `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` and `SPOTIFY_REFRESH_TOKEN`.
4. Run the *Refresh profile* workflow from the **Actions** tab, or wait for the next morning run.
