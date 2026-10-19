#!/usr/bin/env python3
"""One-time helper that prints the Spotify refresh token the workflows need.

1. Create an app at https://developer.spotify.com/dashboard
   - Redirect URI: http://127.0.0.1:8888/callback
   - API: Web API
   - Settings → User Management: add the email of every Spotify account you connect (up to 5)
2. Run on your own machine, once per account, in priority order:
       python3 .github/profile/spotify_auth.py        # account 1
       python3 .github/profile/spotify_auth.py 2      # account 2 … up to 5
   Spotify asks which account to approve; use "Not you?" to switch.
3. It offers to save the secrets for you with gh, or prints them to add by hand.
"""

import base64
import getpass
import http.server
import json
import secrets
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
import webbrowser

REDIRECT = "http://127.0.0.1:8888/callback"
SCOPES = (
    "user-top-read user-read-recently-played user-read-currently-playing "
    "user-read-playback-state playlist-read-private"
)


def main():
    account = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    if not 1 <= account <= 5:
        sys.exit("Account number must be between 1 and 5.")
    client_id = input("Client ID: ").strip()
    client_secret = getpass.getpass("Client secret: ").strip()
    state = secrets.token_urlsafe(16)
    url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(
        {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": REDIRECT,
            "scope": SCOPES,
            "state": state,
            "show_dialog": "true",
        }
    )
    result = {}

    class Callback(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            result.update({key: values[0] for key, values in query.items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Done. You can close this tab and go back to the terminal.")

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 8888), Callback)
    print(f"\nOpening Spotify to approve access. If no browser opens, visit:\n{url}\n")
    webbrowser.open(url)
    while "code" not in result and "error" not in result:
        server.handle_request()
    server.server_close()

    if result.get("state") != state or "code" not in result:
        sys.exit(f"Authorization failed: {result.get('error', 'state mismatch')}")

    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    request = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=urllib.parse.urlencode(
            {"grant_type": "authorization_code", "code": result["code"], "redirect_uri": REDIRECT}
        ).encode(),
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        token = json.load(response)

    secrets_to_save = {}
    if account == 1:
        secrets_to_save["SPOTIFY_CLIENT_ID"] = client_id
        secrets_to_save["SPOTIFY_CLIENT_SECRET"] = client_secret
    name = "SPOTIFY_REFRESH_TOKEN" if account == 1 else f"SPOTIFY_REFRESH_TOKEN_{account}"
    secrets_to_save[name] = token["refresh_token"]

    print(f"Account {account} approved.")
    if shutil.which("gh") and input("Save to this repo's GitHub secrets with gh now? [Y/n] ").strip().lower() in ("", "y", "yes"):
        for key, value in secrets_to_save.items():
            # gh reads the value from stdin, so it never lands in your shell history.
            subprocess.run(["gh", "secret", "set", key], input=value, text=True, check=True)
        print("Saved.")
        return
    print("Add these as repository secrets (Settings → Secrets and variables → Actions):\n")
    for key, value in secrets_to_save.items():
        print(f"{key}  {value}")


if __name__ == "__main__":
    main()
