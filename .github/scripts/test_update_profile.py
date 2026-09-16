import contextlib
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError
import xml.etree.ElementTree as ET

import update_profile as profile

NOW = datetime(2026, 9, 16, 12, tzinfo=timezone.utc)


def repository(name="app", **changes):
    return {"name": name, "private": False, "fork": False,
            "stargazers_count": 4, "pushed_at": "2026-09-01T00:00:00Z", **changes}


def spotify(song="A song", artist="An artist", extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg"><foreignObject>'
            f'<div xmlns="http://www.w3.org/1999/xhtml">'
            f'<div class="artist">{artist}</div><div class="song scrolling">{song}</div>'
            f'{extra}</div></foreignObject></svg>').encode()


class ProfileTests(unittest.TestCase):
    def test_pagination_filters_private_fork_and_profile_repositories(self):
        first = [repository(f"repo-{i}") for i in range(97)] + [
            repository("private", private=True), repository("fork", fork=True),
            repository("robyrew")]
        second = [repository("last", archived=True)]
        with patch.object(profile, "fetch", side_effect=[json.dumps(first), json.dumps(second)]) as fetch:
            repos = profile.public_projects()
        self.assertEqual(len(repos), 98)
        self.assertEqual(repos[-1]["name"], "last")
        self.assertIn("page=2", fetch.call_args.args[0])

    def test_stats_use_push_dates_not_archived_status(self):
        repos = [repository(), repository("archived", archived=True),
                 repository("old", pushed_at="2020-01-01T00:00:00Z"),
                 repository("future", pushed_at="2030-01-01T00:00:00Z"),
                 repository("empty", pushed_at=None)]
        root = ET.fromstring(profile.stats_svg(repos, NOW))
        title = root.find("{http://www.w3.org/2000/svg}title").text
        self.assertIn("5 public projects, 20 stars earned, 2 updated in 90 days", title)

    def test_track_is_parsed_and_escaped_as_plain_text(self):
        track = profile.parse_spotify(spotify("Song &amp;amp; &amp;lt;title&amp;gt;", "Artist"))
        self.assertEqual(track[:2], ("Song & <title>", "Artist"))
        output = profile.spotify_svg(track, NOW)
        ET.fromstring(output)
        self.assertIn("Song &amp; &lt;title&gt;", output)
        self.assertNotIn("foreignObject", output)
        self.assertIn("Captured 16 Sep 2026 · 12:00 UTC", output)

    def test_offline_returns_profile_card(self):
        self.assertIsNone(profile.parse_spotify(spotify("Currently not playing on Spotify", "Offline")))
        self.assertIn("Find me on Spotify", profile.spotify_svg(None, NOW))

    def test_html_error_empty_svg_and_xml_entities_are_rejected(self):
        for payload in (b"Error: Invalid Spotify access_token", b"<html>Error</html>",
                        b'<svg xmlns="http://www.w3.org/2000/svg"/>',
                        b'<!DOCTYPE svg [<!ENTITY x "test">]><svg/>'):
            with self.subTest(payload=payload), self.assertRaises((ValueError, ET.ParseError)):
                profile.parse_spotify(payload)

    def test_remote_images_and_upstream_scripts_are_not_copied(self):
        track = profile.parse_spotify(spotify(extra='<img class="cover" src="https://example.com/art.png"/><script>alert(1)</script>'))
        self.assertIsNone(track[2])
        output = profile.spotify_svg(track, NOW)
        self.assertNotIn("example.com", output)
        self.assertNotIn("script", output)

    def test_embedded_cover_is_retained(self):
        source = "data:image/png;base64,iVBORw0KGgo="
        track = profile.parse_spotify(spotify(extra=f'<img class="cover" src="{source}"/>'))
        self.assertEqual(track[2], source)
        self.assertIn(source, profile.spotify_svg(track, NOW))

    def test_long_titles_do_not_break_the_svg(self):
        root = ET.fromstring(profile.spotify_svg(("<&" * 100, "Artist" * 30, None), NOW))
        self.assertTrue(any((element.text or "").endswith("…") for element in root.iter()))

    def test_github_failure_leaves_existing_assets_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            for name in ("stats.svg", "spotify.svg"):
                (output / name).write_text("previous")
            with patch("sys.argv", ["update_profile.py", "--output", directory]), \
                 patch.object(profile, "public_projects", side_effect=URLError("offline")), \
                 self.assertRaises(URLError):
                profile.main()
            self.assertTrue(all(path.read_text() == "previous" for path in output.iterdir()))

    def test_spotify_failure_still_generates_both_valid_cards(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("sys.argv", ["update_profile.py", "--output", directory]), \
                 patch.object(profile, "public_projects", return_value=[repository()]), \
                 patch.object(profile, "fetch", side_effect=URLError("offline")), \
                 contextlib.redirect_stdout(io.StringIO()) as log:
                profile.main()
            for path in Path(directory).iterdir():
                ET.parse(path)
            self.assertIn("Find me on Spotify", (Path(directory) / "spotify.svg").read_text())
            self.assertIn("::warning::Spotify", log.getvalue())


if __name__ == "__main__":
    unittest.main()
