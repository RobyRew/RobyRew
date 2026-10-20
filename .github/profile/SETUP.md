# How this profile is built

`README.md` and everything in `img/` are generated. Don't edit them by hand.

- **Content** lives in [`profile.toml`](../../profile.toml) at the repo root. Change the text, push to `main`, and the
  *Refresh profile* workflow rebuilds the page. It also runs every morning to pick up new stars, repos,
  contribution stats and listening data.
- **Rendering:** [`layout.py`](layout.py) draws the page, [`canvas.py`](canvas.py) has the shared drawing
  pieces (fonts, colours, icons, the record) and [`data.py`](data.py) reads GitHub, Spotify and Last.fm.
  [`build.py`](build.py) puts it together. Every SVG embeds a small subset of Bricolage Grotesque and Geist Mono
  (licence in [`fonts/OFL.txt`](fonts/OFL.txt)).
- **Last known data** (repos, stats, tracks) is saved in [`cache.json`](cache.json), so a failed API call
  never blanks the page.

### How the page is put together

GitHub strips CSS and clickable areas inside images from READMEs, so an image can carry only one link. That is why the
page is a grid of glass tiles, one image per link: a project, its stars, downloads and latest release, each chart
number, each track and artist. Tiles of one group share a tint laid across all of them.

No tile touches the edge of its image: wherever two images meet there is clear space, half a gap from each side.
When an image lands between two device pixels (at 110 % or 125 % zoom, or on most phones), browsers blend its edge
with the page, so two images painted flush on one colour always show a hairline where they meet. In clear space
there is nothing to blend, so no zoom level or screen can show a cut. `align="top"` on every image stops GitHub
leaving a gap under each row, and `layout.py` refuses rows under 40 units, which GitHub would pad to a line of
text (24 px).

The tiles are frosted glass with a faint tint, sized like GitHub's own interface, and drawn without filters so
they stay quick to paint. Images are linked straight to `raw.githubusercontent.com`; a relative link would cost
every image a redirect through github.com first.

- Every tile comes as `img/dark` and `img/light` for computers and `img/m` for phones (half the width, same
  type size, so nothing gets tiny). The phone file holds both themes and switches by itself: GitHub's page script
  rewrites any `<picture>` source that mentions dark or light mode to follow the viewer's GitHub theme, and in
  doing so drops a width condition, so the phone source asks for width only.
- Every link has a hover tooltip.
- The top row is two tiles. Yours has your name, with a slow aurora behind it, a sweep of colour through the name,
  a glitch and some sparkle now and then, and a blinking cursor (all CSS, no filters, and still for anyone who
  asks their system for reduced motion); it links to the project you're building. The turntable shows the album
  cover as the record's label and what's playing beside the record (under it on phones), and plays the song.
  The record stays in one image: cut across two, its halves would turn out of step.
- "Fresh from the studio" lists your other public repositories, latest push first, two to a row, and ends with a
  tile to all of them. `[bsides]` in `profile.toml` sets how many, which to leave out and your own descriptions.
- Numbers that are zero or missing are left out, and the rest fill their rows evenly.
- The fonts carry no kerning table: the kerning is worked out at build time and written into each line of text,
  which makes every image lighter.
- The contribution calendar is also saved as a 3D model, [`img/contributions.stl`](../../img/contributions.stl),
  which GitHub shows in its own 3D viewer. The activity tile links to it, so the profile itself doesn't load
  the viewer.

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

3. Tell the workflows your Last.fm usernames, in priority order, each with the label to show
   (Last.fm can't tell which app played a song):

   ```sh
   gh variable set LASTFM_USERS --body "yourname:Spotify"
   gh variable set LASTFM_USERS --body "yourname:Spotify, second:YouTube Music, third:Apple Music"   # several
   ```

   The `[[listening.lastfm]]` blocks in `profile.toml` work too; the variable is checked first.

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

## 2. Live record player

The README is only rebuilt once a day, so on its own the record always shows "last played" with the needle parked.
To make it live, a second workflow publishes the record player to GitHub Pages every five minutes (the shortest
schedule GitHub allows), whenever the music has changed. Nothing is committed and no branch is created. GitHub
caches README images for up to about ten minutes on top of that, so the card trails the music by a few minutes;
a README can't run scripts, so it can't update while the page is open.

Their links follow the music too: they point at small redirect pages on the same site (`go/play/`, `go/song/`,
`go/artist/`, `go/context/`, `go/user/`), rewritten every time the song changes. A push that changes the code
or `profile.toml` redeploys the site straight away.

```sh
gh api -X POST repos/RobyRew/RobyRew/pages -f build_type=workflow || gh api -X PUT repos/RobyRew/RobyRew/pages -f build_type=workflow
gh variable set LIVE_NOW_PLAYING --body true
gh workflow run now-playing.yml
gh workflow run refresh.yml
```

The first run publishes the record player; the second switches the README over to it. Expect it to lag the music
by roughly 5 to 15 minutes, since GitHub's scheduler and image cache both add delay.

## 3. Optional: an instant record player (Cloudflare Worker)

With a free Cloudflare Worker, the deck is drawn on every visit, so it shows what's playing right now instead of a
few minutes ago. Its answers tell GitHub's image proxy not to keep them. It fills in the templates that step 2
publishes (`kit.json` on Pages), and if anything goes wrong it hands over the Pages copy, so keep step 2 running.

1. Make a free account at <https://dash.cloudflare.com> and open **Workers & Pages** once; it asks you to pick
   your `workers.dev` subdomain.
2. Create an API token: **My Profile → API Tokens → Create Token**, template **Edit Cloudflare Workers**. Copy your
   **Account ID** from the Workers & Pages overview.
3. Save both and deploy:

   ```sh
   gh secret set CLOUDFLARE_API_TOKEN
   gh secret set CLOUDFLARE_ACCOUNT_ID
   gh workflow run worker.yml
   ```

   The run's log shows the Worker's address, like `https://robyrew-now.<you>.workers.dev`. Open
   `<address>/now.json` to check it sees your music.
4. Put that address in `profile.toml` as `worker` under `[listening]`, and push. The README switches over on the
   next build.

The Worker reuses `LASTFM_API_KEY` and the Spotify secrets (`worker.yml` copies them over on each deploy). To go
back, empty `worker` again.

## 4. Optional: richer stats

The activity and popularity cards use the workflow's own token, which sees public activity. To count private
contributions too, create a fine-grained token with read-only access and save it:

```sh
gh secret set PROFILE_TOKEN
```
