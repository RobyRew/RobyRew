# Profile maintenance

Edit `README.md` for copy and project links, and `img/header.svg` for the banner.
The README is curated; automation never rewrites it.

## Generated cards

`profile.yml` renders cards hourly (at minute 17), on relevant main-branch changes,
or via **Actions → Profile cards → Run workflow**. Scheduled runs can be delayed.
Python's standard library is the only dependency.

Images live on the **profile-assets** branch, which contains generated data only.
This keeps routine image refreshes separate from reviewed changes to `main`.
The branch must exist before the publishing job runs; it is seeded as part of
this profile revision. Keep code changes on `main` subject to the normal review.

Stats use GitHub's public repository endpoint, with pagination. They exclude
forks, private repositories and this profile repository. Stars are summed across
those projects, including archived ones. “Updated in 90 days” counts repositories
with a push in that rolling period; it is not a commit or contribution count.
A failed GitHub request fails the workflow without changing published cards.

Spotify uses the existing `spotify-github-profile` connection. The renderer
extracts song, artist and embedded album art, then draws a matching card. It does
not copy upstream HTML or make visitors load third-party widgets. A capture time
identifies the card as a snapshot, not live playback. Hourly refreshes and GitHub
image caching mean a change may take time to appear.

Offline playback, invalid authorization or a service outage produces a clean
Spotify profile link instead of a broken image or a stale “now playing” claim.
To restore track snapshots, reconnect the same Spotify account at
<https://spotify-github-profile.kittinanx.com/api/login>, then run the workflow.
Never put Spotify tokens in this repository or in GitHub issue/PR comments.

## Local checks

```sh
python3 -m unittest discover -s .github/scripts -p 'test_*.py' -v
python3 .github/scripts/update_profile.py
```

The second command requires network access and writes to ignored `build/profile/`.
No publishing occurs when running the Python script locally.
