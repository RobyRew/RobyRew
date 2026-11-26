# How this profile is built

`README.md` and everything in `img/` are generated. Don't edit them by hand.

- **Content** lives in [`profile.toml`](../../profile.toml) at the repo root: who I am, the projects and their copy,
  the archive, music and contact links. Change it, push to `main`, and the *Refresh profile* workflow rebuilds the
  page. It also runs every morning to pick up new stars, downloads, releases and listening data.
- **Rendering:** [`layout.py`](layout.py) draws the page, [`canvas.py`](canvas.py) has the shared drawing
  pieces (fonts, colours, icons, the record) and [`data.py`](data.py) reads GitHub, Spotify and Last.fm.
  [`build.py`](build.py) puts it together. Every SVG embeds a small subset of Inter and JetBrains Mono, the type of
  cosmincalin.es (licence and how the files were cut in [`fonts/OFL.txt`](fonts/OFL.txt)).
- **Project icons** are in [`icons/`](icons): each project's own app icon or favicon, named in `profile.toml`
  (`icon = "mapswitch.png"`). PNGs are 112 px with the transparent margin of macOS icons cropped off, so every
  icon reads at the same size. A project without one gets a line icon on a glass square (`icon = "terminal"`).
- **Last known data** (repos, numbers, tracks) is saved in [`cache.json`](cache.json), so a failed API call
  never blanks the page.

### How the page is put together

GitHub strips CSS and clickable areas inside images from READMEs, so an image can carry only one link. That is why the
page is a grid of cards, one image per link. The cards use the palette of the RobyRew sites (`@robyrew/ui`): neutral
greys, one blue accent, a see-through fill that sits on any GitHub theme, and a faint tint in the colour of each
project's icon.

No card touches the edge of its image: wherever two images meet there is clear space, half a gap from each side.
When an image lands between two device pixels (at 110 % or 125 % zoom, or on most phones), browsers blend its edge
with the page, so two images painted flush on one colour always show a hairline where they meet. In clear space
there is nothing to blend, so no zoom level or screen can show a cut. `align="top"` on every image stops GitHub
leaving a gap under each row, and `layout.py` refuses rows under 40 units, which GitHub would pad to a line of
text (24 px). Images are linked straight to `raw.githubusercontent.com`; a relative link would cost every image a
redirect through github.com first.

- Every card comes as `img/dark` and `img/light` for computers and `img/m` for phones (half the width, same
  type size, so nothing gets tiny). The phone file holds both themes and switches by itself: GitHub's page script
  rewrites any `<picture>` source that mentions dark or light mode to follow the viewer's GitHub theme, and in
  doing so drops a width condition, so the phone source asks for width only.
- Every link has a hover tooltip and every image a full-sentence `alt`.
- Top to bottom:
  - **Two tiles.** Mine has my name over a slow aurora, with a sweep of the accent through it now and then, and what I
    do. `statement`, `aside` (with a blinking cursor) and `facts` in `profile.toml` add lines under it, and the line
    over the name is `now`, or my latest push among the projects on the page unless `latest_push = false`. It links
    to my website. The turntable shows the album cover as the record's label and what's playing beside it (under it
    on phones), and plays the song. The record stays in one image: cut across two, its halves would turn out of step.
  - **The numbers:** release downloads and stars across my own repositories (forks left out), public repositories,
    and contributions in the last year.
  - **Projects** (`[work]`): two to a row, all the same size: the icon, the name and `note`, one short line.
  - **More projects** (`[more]`), **Archive** (`[archive]`) and the top tracks (`tracks` above 0 under
    `[listening]`) show only when `profile.toml` asks for them. Then the contact links and the footer.
- Numbers that are zero or missing are left out, and copy that doesn't fit is cut with an ellipsis rather than
  overflowing; the font metrics are read at build time, so `build.py` knows exactly where each line ends.
- The fonts carry no kerning table: the kerning is worked out at build time and written into each line of text,
  which makes every image lighter.
- Everything that moves is CSS inside the SVG, with no filters, and stays still for anyone who asks their system
  for reduced motion.

Build locally:

```sh
pip install fonttools==4.67.0 brotli==1.2.0
python3 .github/profile/build.py --offline  # cached data only
GH_STATS_TOKEN=$(gh auth token) python3 .github/profile/build.py  # fresh GitHub data
```

Every command below runs on your Mac from the repo folder, with the GitHub CLI (`gh`) logged in.

## 1. Music

The deck reads up to 9 Spotify accounts and up to 5 Last.fm accounts. Spotify accounts come first, then the Last.fm
ones in the order they appear in `profile.toml`; the first one that is playing wins, else the latest play anywhere.

### Spotify accounts (SpotAPI)

[SpotAPI](https://github.com/Aran404/SpotAPI) reads an account the way Spotify's web player does. The account's web
session (the `sp_dc` cookie open.spotify.com keeps after you log in) is exchanged for a short-lived token, and a
read-only Spotify Connect observer takes a snapshot of the account's players: the song, playing or paused, and on
which device. No developer app and no Premium are needed, and SpotAPI sends no playback commands. The now service
(below) keeps the accounts connected all the time; the daily build reads them here only when the service doesn't
answer, all the accounts at once.

Add each account, on your own computer from the repo folder (repeat with 2, 3 … up to 9):

```sh
pip install spotapi==2.1.3
python3 .github/profile/spotify_login.py 1
```

It walks you through it: log in to the account in a private window, copy the `sp_dc` cookie from the developer
tools, paste it (it isn't shown), close the window without logging out. It checks the session with Spotify, tells
you whose account it is, and saves it as the secret `SPOTIFY_COOKIE_1`. To show names on the deck instead of
usernames, add `[[listening.spotify]]` blocks with a `label` to `profile.toml`, one per account, in order.

Worth knowing:

- A session is a full login for that account: whoever has the cookie can act as it. It lives only in the repo's
  secrets, and the workflows log error types and HTTP statuses, never cookies, tokens or URLs.
- It lasts until that session is logged out (or the password changes). The deck then carries on with the other
  accounts and Last.fm, and the run log names the account to add again.
- SpotAPI uses Spotify's unofficial web-player endpoints, which Spotify can change. It's pinned
  (`spotapi==2.1.3`, `wreq==0.12.3` in the workflows), so an update only arrives when you move the pin. It's
  GPL-3.0, installed at run time and not copied into this repo.
- Spotify may treat an automated session as unusual: each run opens one observer per account for a few seconds.

### Last.fm (free, works for everything)

Last.fm also covers YouTube Music and Apple Music, and any Spotify account that scrobbles to it.

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

The first Last.fm account also supplies the top tracks (when `tracks` is above 0) and the scrobble count.

## 2. Live record player

The README is rebuilt once a day (and on every push of the profile), so its own image of the deck shows the last play
that build saw. The deck you see on the profile is drawn by a Cloudflare Worker instead (step 3), on every visit:
GitHub's image proxy asks again on each page view because the Worker's answers say not to keep them. The Worker asks
the now service for the Spotify accounts and Last.fm for the rest, each time, so a song change shows on the next page
load, within a couple of seconds. A README can't run scripts, so it can't update while the page stays open.

The Worker's templates (fonts, layout numbers, the deck's looks) are `img/kit.json`, built by the daily workflow and
read from the repo. It holds no song, so it only changes when the code or `profile.toml` does. The links on the deck
(`go/play/`, `go/song/`, `go/artist/`, `go/context/`, `go/user/`) are answered by the Worker too.

Until 2026-11-26 a "Now playing" workflow republished the deck to GitHub Pages every five minutes; it's gone, since
GitHub's artifact listing kept failing its deploys and the Worker no longer needs it.

## 3. Optional: an instant record player (Cloudflare Worker)

With a free Cloudflare Worker, the deck is drawn on every visit. Its answers tell GitHub's image proxy not to keep
them. It fills in the templates from `img/kit.json` (`KIT_URL` in `.github/worker/wrangler.toml`): the now service and
Last.fm are asked live, on each visit, and one lookup is reused for at most 2 seconds. If anything goes wrong it hands
over the image the daily build made (`STATIC_URL`).

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

The Worker reuses `LASTFM_API_KEY` (`worker.yml` copies it over on each deploy) and needs no Spotify secret. With
`worker` empty, the README shows the image the daily build made.

### The now service (always-on Spotify)

[RobyRew/now](https://github.com/RobyRew/now), at `now.spotify.robyrew.com`, keeps one read-only SpotAPI observer per
Spotify account connected all the time and answers `GET /api/now` with the record player's fields. Accounts are added
on its `/admin` page (sign in with RobyRew ID, paste each account's `sp_dc`), and their deck names are set there too.

- The Worker asks it on each visit (`NOW_API` in `.github/worker/wrangler.toml`), so the Spotify side changes with the
  music instead of every few minutes.
- The workflows ask it first (`now_api` under `[listening]` in `profile.toml`). While it answers and watches at least
  one account, they sign in to no Spotify account themselves.
- When it doesn't answer or watches no account, the daily build falls back to the `SPOTIFY_COOKIE_<n>` secrets and
  the Worker to Last.fm. Keep those secrets for that fallback.

## 4. Optional: private contributions

The numbers use the workflow's own token, which sees public activity. To count private contributions in the
"contributions, past year" figure too, create a fine-grained token with read-only access and save it:

```sh
gh secret set PROFILE_TOKEN
```
