#!/usr/bin/env python3
"""Adds a Spotify account to the record player: checks its web session with SpotAPI and saves it as a secret.

    python3 .github/profile/spotify_login.py        account 1
    python3 .github/profile/spotify_login.py 2      account 2, and so on up to 9

Run it on your own computer from the repo folder. It needs SpotAPI (pip install spotapi==2.1.3) and the GitHub CLI
(gh), signed in to the account that owns this repo. The session is read without being shown, sent only to Spotify
(to check it) and to GitHub (as the secret SPOTIFY_COOKIE_<n>), and never written to disk.
"""

import asyncio
import getpass
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

STEPS = """
Spotify account {n}

1. Open a private window (Chrome or Safari: Cmd+Shift+N, Firefox: Cmd+Shift+P), go to https://open.spotify.com
   and log in to the account you want as number {n}.
2. Open the developer tools (Cmd+Option+I) and find the site's cookies:
     Chrome, Edge, Brave: Application -> Storage -> Cookies -> https://open.spotify.com
     Firefox:             Storage -> Cookies -> https://open.spotify.com
     Safari:              Storage -> Cookies (turn on Settings -> Advanced -> "Show features for web developers")
   Copy the value of the cookie named sp_dc.
3. Paste it here. Then close the private window without logging out: logging out ends that session, and the
   cookie stops working.
"""


async def username_of(cookie):
    """The account the session belongs to, so you can see it's the right one."""
    from spotapi import Account, AsyncClient

    async with await AsyncClient.from_cookies(cookie) as client:
        return (await Account(client).get_profile()).username


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 1
    if not 1 <= n <= 9:
        sys.exit("The account number goes from 1 to 9.")
    if importlib.util.find_spec("spotapi") is None:
        sys.exit("SpotAPI isn't installed here: pip install spotapi==2.1.3")
    print(STEPS.format(n=n))
    value = getpass.getpass("sp_dc (hidden): ").strip()
    if not value:
        sys.exit("Nothing pasted, nothing saved.")
    cookie = value if "=" in value else f"sp_dc={value}"
    try:
        username = asyncio.run(username_of(cookie))
    except Exception as error:
        # Only the error's type: a message can carry part of the request.
        sys.exit(f"Spotify didn't accept that session ({type(error).__name__}). Log in again in a private window, "
                 "copy sp_dc again and rerun this.")
    print(f"\nThat session belongs to the Spotify account: {username}")
    repo = subprocess.run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout.strip()
    # On stdin, so the value never appears in a command line or the shell history.
    subprocess.run(["gh", "secret", "set", f"SPOTIFY_COOKIE_{n}", "--repo", repo], input=cookie, text=True, check=True)
    print(f"Saved as SPOTIFY_COOKIE_{n} in {repo}.\n")
    print("The record player reads it on its next run (every 5 minutes). To run it now:")
    print("  gh workflow run now-playing.yml\n")
    print(f'To show a name on the deck instead of "{username}", put a block per account, in order, in profile.toml:')
    print('  [[listening.spotify]]\n  label = "Your name"')


if __name__ == "__main__":
    main()
