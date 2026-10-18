#!/usr/bin/env python3
"""One-time helper that prints the Spotify refresh token the workflow needs.

1. Create an app at https://developer.spotify.com/dashboard
   - Redirect URI: http://127.0.0.1:8888/callback
   - API: Web API
2. Run on your own machine:  python3 .github/profile/spotify_auth.py
3. Add the three values it prints as repository secrets
   (Settings → Secrets and variables → Actions).
"""

import base64
import getpass
import http.server
import json
import secrets
import sys
import urllib.parse
import urllib.request
import webbrowser

REDIRECT = "http://127.0.0.1:8888/callback"
SCOPES = "user-top-read user-read-recently-played"


def main():
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

    print("Add these as repository secrets:\n")
    print(f"SPOTIFY_CLIENT_ID      {client_id}")
    print(f"SPOTIFY_CLIENT_SECRET  {client_secret}")
    print(f"SPOTIFY_REFRESH_TOKEN  {token['refresh_token']}")


if __name__ == "__main__":
    main()
