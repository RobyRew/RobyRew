#!/usr/bin/env python3
"""Renders README.md and every SVG in img/ from profile.toml.

    pip install fonttools brotli
    python3 .github/profile/build.py              # fetches GitHub + music data when it can
    python3 .github/profile/build.py --offline    # uses the last values saved in cache.json
    python3 .github/profile/build.py --live _site # only the hero with what is playing now, for GitHub Pages

Each SVG embeds a subset of the fonts it uses, so the type renders the same
everywhere GitHub shows the image. Light and dark variants are written to
img/light and img/dark and picked by <picture> in the README.
"""

import base64
import hashlib
import html
import json
import math
import os
import sys
import tomllib
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CACHE = HERE / "cache.json"
W = 840  # every full-width image
PAD = 14  # cards sit this far in from the image edge
CW = W - 2 * PAD
HALF = 420  # half-width images, shown at 49% side by side
HP = 6
GAP = 14  # transparent space under every card

SANS = "-apple-system, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', Menlo, monospace"
FONTS = {
    # key: (file, fallback stack, weight)
    "display": ("BricolageGrotesque-ExtraBold.ttf", SANS, 800),
    "semi": ("BricolageGrotesque-SemiBold.ttf", SANS, 600),
    "text": ("BricolageGrotesque-Regular.ttf", SANS, 400),
    "mono": ("GeistMono-Regular.ttf", MONO, 400),
    "mono-md": ("GeistMono-Medium.ttf", MONO, 500),
}

HUES = {
    "ember": ("#FF6A2B", "#D62F4B", "#FFB347"),
    "teal": ("#14B8A6", "#0EA5E9", "#5EEAD4"),
    "blue": ("#3B82F6", "#0EA5E9", "#1D4ED8"),
    "rose": ("#F43F5E", "#FB923C", "#BE123C"),
    "green": ("#22C55E", "#14B8A6", "#A3E635"),
    "graphite": ("#64748B", "#334155", "#94A3B8"),
}
HUE_ORDER = ("ember", "teal", "blue", "rose", "green")

THEMES = {
    "dark": {
        "base": "#121014",
        "ink": "#F7F4EF",
        "dim": ("#FFFFFF", 0.7),
        "faint": ("#FFFFFF", 0.48),
        "glass": ("#FFFFFF", 0.08),
        "edge": ("#FFFFFF", 0.12),
        "blob": 0.8,
        "grain": 0.09,
        "veil": 0.55,
        "head": "#F0F6FC",
        "muted": "#8B949E",
        "accent": "#FF8A5B",
        "aside": "#FFC4A3",
        "window": "#1B1A1F",
        "heat": ("#FFFFFF", 0.07),
        "panel": ("#0B0A0D", 0.42),
    },
    "light": {
        "base": "#FFFBF7",
        "ink": "#17151A",
        "dim": ("#000000", 0.64),
        "faint": ("#000000", 0.46),
        "glass": ("#FFFFFF", 0.62),
        "edge": ("#000000", 0.08),
        "blob": 0.42,
        "grain": 0.06,
        "veil": 0.6,
        "head": "#1F2328",
        "muted": "#656D76",
        "accent": "#E8590C",
        "aside": "#C2410C",
        "window": "#FFFFFF",
        "heat": ("#000000", 0.06),
        "panel": ("#FFFFFF", 0.7),
    },
}

LANGUAGES = {
    "Swift": "#F05138",
    "TypeScript": "#3178C6",
    "JavaScript": "#F1E05A",
    "Python": "#3572A5",
    "HTML": "#E34C26",
    "CSS": "#663399",
    "Shell": "#89E051",
}

PLATFORMS = {
    "Spotify": "#1ED760",
    "Last.fm": "#D51007",
    "YouTube Music": "#FF0033",
    "Apple Music": "#FA2D48",
}

# 24×24 line icons.
ICONS = {
    "presentation": '<rect x="2.5" y="3.5" width="19" height="13" rx="2.5"/><path d="M12 16.5V20M8 20.5h8M10 7.5l4.5 2.5-4.5 2.5z"/>',
    "map": '<path d="M12 21.5s-7-6.1-7-11.6a7 7 0 0 1 14 0c0 5.5-7 11.6-7 11.6Z"/><circle cx="12" cy="9.8" r="2.6"/>',
    "chat": '<path d="M4.5 4.5h10A2.5 2.5 0 0 1 17 7v5.5a2.5 2.5 0 0 1-2.5 2.5h-5L6 18v-3H4.5A2.5 2.5 0 0 1 2 12.5V7a2.5 2.5 0 0 1 2.5-2.5Z"/><path d="M17 9h2.5A2.5 2.5 0 0 1 22 11.5V17a2.5 2.5 0 0 1-2.5 2.5H19V22l-3.5-2.5H12a2.5 2.5 0 0 1-2-1"/>',
    "pdf": '<path d="M14 2.5H6.5A2.5 2.5 0 0 0 4 5v14a2.5 2.5 0 0 0 2.5 2.5h11A2.5 2.5 0 0 0 20 19V8.5Z"/><path d="M14 2.5v6h6M12 11.5v6M9 14.8l3 3 3-3"/>',
    "layers": '<path d="M12 2.5 2.5 7.5 12 12.5l9.5-5Z"/><path d="m2.5 12 9.5 5 9.5-5M2.5 16.5l9.5 5 9.5-5"/>',
    "code": '<path d="m8 7-5 5 5 5M16 7l5 5-5 5M13.5 4l-3 16"/>',
    "briefcase": '<rect x="2.5" y="7" width="19" height="13.5" rx="2.5"/><path d="M8.5 7V5a2 2 0 0 1 2-2h3a2 2 0 0 1 2 2v2M2.5 12.5h19"/>',
    "pin": '<path d="M12 21.5s-7-6.1-7-11.6a7 7 0 0 1 14 0c0 5.5-7 11.6-7 11.6Z"/><circle cx="12" cy="9.8" r="2.6"/>',
    "arrow": '<path d="M7 17 17 7M8.5 7H17v8.5"/>',
    "spark": '<path d="M12 3v5M12 16v5M3 12h5M16 12h5"/>',
    "globe": '<circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19M12 2.5c2.6 2.8 3.9 6 3.9 9.5s-1.3 6.7-3.9 9.5c-2.6-2.8-3.9-6-3.9-9.5s1.3-6.7 3.9-9.5Z"/>',
    "send": '<path d="M21.5 3.5 2.8 10.7c-.9.4-.9 1.6.1 1.9l4.6 1.5 1.8 5.6c.3.8 1.3 1 1.9.4l2.6-2.5 4.8 3.5c.7.5 1.6.1 1.8-.7l3.3-15.3c.2-1-.8-1.8-1.7-1.4Z"/><path d="m7.6 14.1 9.4-6.6"/>',
    "music": '<path d="M9 18V5.5l11-2V16"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="17.5" cy="16" r="2.5"/>',
    "laptop": '<rect x="4" y="5" width="16" height="11" rx="1.8"/><path d="M2 19.5h20"/>',
    "phone": '<rect x="6.5" y="2.5" width="11" height="19" rx="2.5"/><path d="M11 18.5h2"/>',
    "speaker": '<rect x="5" y="2.5" width="14" height="19" rx="2.5"/><circle cx="12" cy="14" r="3.5"/><circle cx="12" cy="7" r="1"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.2-4 4.3-6 8-6s6.8 2 8 6"/>',
    "list": '<path d="M8 6h13M8 12h13M8 18h8M3.5 6h.01M3.5 12h.01M3.5 18h.01"/>',
}
STAR = "M12 2.8l2.8 5.8 6.4.9-4.6 4.5 1.1 6.3L12 17.3l-5.7 3 1.1-6.3-4.6-4.5 6.4-.9Z"
DEVICE_ICONS = {"computer": "laptop", "smartphone": "phone", "tablet": "phone"}

OFFLINE = False


def esc(s):
    return html.escape(str(s), quote=True)


def num(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def paint(color, attr="fill"):
    if isinstance(color, tuple):
        return f'{attr}="{color[0]}" {attr}-opacity="{num(color[1])}"'
    return f'{attr}="{color}"'


def compact(n):
    if n >= 10000:
        return f"{n / 1000:.0f}k"
    if n >= 1000:
        return f"{n / 1000:.1f}k".replace(".0k", "k")
    return str(n)


# ── type ─────────────────────────────────────────────────────────────────────


class Face:
    def __init__(self, key):
        file, self.stack, self.weight = FONTS[key]
        self.path = HERE / "fonts" / file
        font = TTFont(self.path, lazy=True)
        self.cmap = font.getBestCmap()
        self.advance = {g: a for g, (a, _) in font["hmtx"].metrics.items()}
        self.upm = font["head"].unitsPerEm

    def width(self, text, size, tracking=0.0):
        units = sum(
            self.advance[self.cmap[ord(c)]] if ord(c) in self.cmap else self.upm * 0.55
            for c in text
        )
        return units * size / self.upm + tracking * len(text)

    def fit(self, text, size, max_width, tracking=0.0):
        if self.width(text, size, tracking) <= max_width:
            return text
        while text and self.width(text + "…", size, tracking) > max_width:
            text = text[:-1]
        return text.rstrip(" ,.;:—-·") + "…"

    def wrap(self, text, size, max_width, max_lines=99):
        lines, line = [], ""
        words = text.split()
        for i, word in enumerate(words):
            trial = f"{line} {word}".strip()
            if line and self.width(trial, size) > max_width:
                lines.append(line)
                line = word
                if len(lines) == max_lines:
                    lines[-1] = self.fit(" ".join([lines[-1]] + words[i:]), size, max_width)
                    return lines
            else:
                line = trial
        return lines + [line] if line else lines


FACES = {key: Face(key) for key in FONTS}


@lru_cache(maxsize=None)
def font_face(key, chars):
    face = FACES[key]
    options = subset.Options()
    options.flavor = "woff2"
    options.hinting = False
    options.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk"]
    font = TTFont(face.path, recalcTimestamp=False)
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=chars)
    subsetter.subset(font)
    buffer = BytesIO()
    subset.save_font(font, buffer, options)
    data = base64.b64encode(buffer.getvalue()).decode()
    return (
        f"@font-face{{font-family:'rr-{key}';src:url(data:font/woff2;base64,{data}) format('woff2');"
        f"font-weight:{face.weight}}}"
        f".f-{key}{{font-family:'rr-{key}',{face.stack};font-weight:{face.weight}}}"
    )


# ── canvas ───────────────────────────────────────────────────────────────────


class SVG:
    def __init__(self, theme, width, height, label):
        self.theme = theme
        self.t = THEMES[theme]
        self.width, self.height = width, height
        self.label = label
        self.parts, self.defs, self.css, self.chars = [], [], [], {}
        self.ids = 0
        self.grain = False

    def uid(self, prefix):
        self.ids += 1
        return f"{prefix}{self.ids}"

    def add(self, markup):
        self.parts.append(markup)

    def use(self, font, text):
        self.chars.setdefault(font, set()).update(text)

    def text(self, x, y, s, font, size, color, tracking=0, anchor="start", extra=""):
        if not s:
            return 0
        width = FACES[font].width(s, size, tracking)
        if anchor == "end":
            x -= width
        elif anchor == "middle":
            x -= width / 2
        self.use(font, s)
        spacing = f' letter-spacing="{num(tracking)}"' if tracking else ""
        self.add(
            f'<text x="{num(x)}" y="{num(y)}" class="f-{font}" font-size="{num(size)}" '
            f'{paint(color)}{spacing}{extra}>{esc(s)}</text>'
        )
        return width

    def icon(self, name, x, y, size, color, stroke=1.8):
        self.add(
            f'<g transform="translate({num(x)} {num(y)}) scale({num(size / 24)})" fill="none" '
            f'{paint(color, "stroke")} stroke-width="{num(stroke * 24 / size)}" stroke-linecap="round" '
            f'stroke-linejoin="round">{ICONS.get(name, ICONS["spark"])}</g>'
        )

    def glass(self, x, y, w, h, r, fill=None):
        self.add(
            f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" rx="{num(r)}" '
            f'{paint(fill or self.t["glass"])} {paint(self.t["edge"], "stroke")} stroke-width="1"/>'
        )

    def chip(self, x, y, label, h=28, size=13.5, dot=None, icon=None, star=False):
        pad = 12
        inner = (15 if dot else 0) + (21 if icon or star else 0)
        width = pad * 2 + inner + FACES["semi"].width(label, size)
        self.glass(x, y, width, h, h / 2)
        cx = x + pad
        if dot:
            self.add(f'<circle cx="{num(cx + 4)}" cy="{num(y + h / 2)}" r="4" fill="{dot}"/>')
            cx += 15
        if icon:
            self.icon(icon, cx, y + h / 2 - 7, 14, self.t["ink"])
            cx += 21
        if star:
            self.add(
                f'<path d="{STAR}" fill="#FFC53D" transform="translate({num(cx)} {num(y + h / 2 - 7)}) scale({num(14 / 24)})"/>'
            )
            cx += 21
        self.text(cx, y + h / 2 + size * 0.35, label, "semi", size, self.t["ink"])
        return width

    def card(self, x, y, w, h, r, hue, blobs, drift=False):
        t = self.t
        clip = self.uid("clip")
        self.defs.append(
            f'<clipPath id="{clip}"><rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" rx="{num(r)}"/></clipPath>'
        )
        parts = [f'<g clip-path="url(#{clip})">', f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" fill="{t["base"]}"/>']
        colors = HUES.get(hue, HUES["ember"])
        for fx, fy, fr, ci, strength in blobs:
            grad = self.uid("blob")
            color = colors[ci]
            self.defs.append(
                f'<radialGradient id="{grad}"><stop offset="0" stop-color="{color}" stop-opacity="{num(t["blob"] * strength)}"/>'
                f'<stop offset=".55" stop-color="{color}" stop-opacity="{num(t["blob"] * strength * 0.45)}"/>'
                f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>'
            )
            klass = ' class="drift"' if drift else ""
            parts.append(
                f'<circle{klass} cx="{num(x + fx * w)}" cy="{num(y + fy * h)}" r="{num(fr * max(w, h))}" fill="url(#{grad})"/>'
            )
        if not self.grain:
            self.defs.append(
                '<filter id="grain" x="0" y="0" width="100%" height="100%">'
                '<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" stitchTiles="stitch"/>'
                '<feColorMatrix type="saturate" values="0"/></filter>'
            )
            self.grain = True
        parts.append(
            f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" filter="url(#grain)" '
            f'opacity="{num(t["grain"])}" style="mix-blend-mode:overlay"/>'
        )
        parts.append("</g>")
        parts.append(
            f'<rect x="{num(x + 0.5)}" y="{num(y + 0.5)}" width="{num(w - 1)}" height="{num(h - 1)}" rx="{num(r)}" '
            f'fill="none" {paint(t["edge"], "stroke")} stroke-width="1"/>'
        )
        self.add("".join(parts))

    def heading(self, x, y, kicker, title, right=""):
        t = self.t
        self.text(x, y, kicker.upper(), "mono-md", 11, t["ink"], tracking=2.2)
        self.text(x - 2, y + 40, title, "display", 30, t["ink"], tracking=-0.8)
        if right:
            self.text(self.width - x, y, right.upper(), "mono", 10.5, t["faint"], tracking=1.6, anchor="end")

    def render(self):
        fonts = "".join(font_face(k, "".join(sorted(v))) for k, v in sorted(self.chars.items()))
        css = (
            fonts
            + "text{font-kerning:normal;text-rendering:geometricPrecision}"
            + "".join(self.css)
            + "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}" role="img" aria-label="{esc(self.label)}">'
            f"<title>{esc(self.label)}</title><style>{css}</style><defs>{''.join(self.defs)}</defs>"
            + "".join(self.parts)
            + "</svg>\n"
        )


def circle_path(cx, cy, r):
    return f"M{num(cx - r)} {num(cy)}a{num(r)} {num(r)} 0 1 0 {num(2 * r)} 0a{num(r)} {num(r)} 0 1 0 {num(-2 * r)} 0Z"


def sector(cx, cy, r0, r1, a0, a1):
    def point(r, a):
        return f"{num(cx + r * math.cos(math.radians(a)))} {num(cy + r * math.sin(math.radians(a)))}"

    return (
        f"M{point(r1, a0)}A{num(r1)} {num(r1)} 0 0 1 {point(r1, a1)}"
        f"L{point(r0, a1)}A{num(r0)} {num(r0)} 0 0 0 {point(r0, a0)}Z"
    )


def blobs_for(index):
    layouts = (
        [(0.95, 1.05, 0.7, 0, 1), (0.05, 1.2, 0.55, 1, 0.75), (0.9, -0.15, 0.4, 2, 0.7)],
        [(0.1, -0.1, 0.65, 0, 0.95), (1.0, 1.1, 0.6, 1, 0.8), (0.6, 1.3, 0.4, 2, 0.6)],
        [(1.05, 0.2, 0.7, 0, 1), (0.0, 1.1, 0.5, 2, 0.7), (0.4, -0.3, 0.45, 1, 0.6)],
    )
    return layouts[index % len(layouts)]


@lru_cache(maxsize=None)
def image_data(url):
    if not url or OFFLINE:
        return None
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "robyrew-profile"})
        with urllib.request.urlopen(request, timeout=15) as response:
            kind = response.headers.get_content_type()
            return f"data:{kind};base64,{base64.b64encode(response.read()).decode()}"
    except Exception as error:
        print(f"image: skipped ({error})", file=sys.stderr)
        return None


def artwork(svg, x, y, size, url, seed, r=9):
    clip = svg.uid("art")
    svg.defs.append(f'<clipPath id="{clip}"><rect x="{num(x)}" y="{num(y)}" width="{size}" height="{size}" rx="{r}"/></clipPath>')
    data = image_data(url)
    if data:
        svg.add(
            f'<image href="{data}" x="{num(x)}" y="{num(y)}" width="{size}" height="{size}" '
            f'clip-path="url(#{clip})" preserveAspectRatio="xMidYMid slice"/>'
        )
        return
    colors = HUES[HUE_ORDER[sum(map(ord, seed or "x")) % len(HUE_ORDER)]]
    grad = svg.uid("artg")
    svg.defs.append(
        f'<linearGradient id="{grad}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{colors[0]}"/>'
        f'<stop offset="1" stop-color="{colors[1]}"/></linearGradient>'
    )
    svg.add(f'<rect x="{num(x)}" y="{num(y)}" width="{size}" height="{size}" rx="{r}" fill="url(#{grad})"/>')
    svg.icon("music", x + size / 2 - size * 0.22, y + size / 2 - size * 0.22, size * 0.44, "#FFFFFF")


# ── hero: the deck ───────────────────────────────────────────────────────────


def record(svg, cx, cy, r, words, spinning):
    label_r, hole_r = 0.38 * r, 4
    disc, label, shadow = svg.uid("disc"), svg.uid("label"), svg.uid("shadow")
    svg.defs.append(
        f'<radialGradient id="{disc}"><stop offset="0" stop-color="#2A2A2E"/><stop offset=".5" stop-color="#121214"/>'
        f'<stop offset="1" stop-color="#050506"/></radialGradient>'
        f'<radialGradient id="{label}" cx=".35" cy=".3"><stop offset="0" stop-color="#FFB37A"/>'
        f'<stop offset=".6" stop-color="#FF6A2B"/><stop offset="1" stop-color="#D9381E"/></radialGradient>'
        f'<filter id="{shadow}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter>'
    )
    if spinning:
        svg.css.append(
            f".spin{{transform-origin:{num(cx)}px {num(cy)}px;animation:spin 2.4s linear infinite}}"
            "@keyframes spin{to{transform:rotate(360deg)}}"
        )
    parts = [
        f'<circle cx="{num(cx + 6)}" cy="{num(cy + 16)}" r="{num(r)}" fill="#000" opacity=".55" filter="url(#{shadow})"/>',
        '<g class="spin">' if spinning else "<g>",
        f'<path d="{circle_path(cx, cy, r)}{circle_path(cx, cy, hole_r)}" fill="url(#{disc})" fill-rule="evenodd"/>',
    ]
    groove, i = label_r + 7, 0
    while groove < r - 5:
        opacity = 0.075 if i % 2 else 0.04
        parts.append(
            f'<circle cx="{num(cx)}" cy="{num(cy)}" r="{num(groove)}" fill="none" stroke="#fff" '
            f'stroke-opacity="{opacity}" stroke-width=".6"/>'
        )
        groove += 2.2
        i += 1
    for gap in (r * 0.6, r * 0.74, r * 0.87):
        parts.append(f'<circle cx="{num(cx)}" cy="{num(cy)}" r="{num(gap)}" fill="none" stroke="#000" stroke-opacity=".7" stroke-width="2.4"/>')
    parts.append(
        f'<path d="{circle_path(cx, cy, label_r)}{circle_path(cx, cy, hole_r)}" fill="url(#{label})" fill-rule="evenodd"/>'
    )
    ring = label_r - 12
    size = 6.2
    tracking = (2 * math.pi * ring - FACES["mono-md"].width(words, size)) / len(words)
    svg.use("mono-md", words)
    ring_id = svg.uid("ring")
    parts.append(
        f'<path id="{ring_id}" d="M{num(cx - ring)} {num(cy)}a{num(ring)} {num(ring)} 0 1 1 {num(2 * ring)} 0'
        f'a{num(ring)} {num(ring)} 0 1 1 {num(-2 * ring)} 0" fill="none"/>'
        f'<text class="f-mono-md" font-size="{size}" letter-spacing="{num(tracking)}" fill="#2A0E04" fill-opacity=".72">'
        f'<textPath href="#{ring_id}">{esc(words)}</textPath></text>'
    )
    svg.use("display", "RobyRew")
    parts.append(
        f'<text x="{num(cx)}" y="{num(cy - 10)}" text-anchor="middle" class="f-display" font-size="13" '
        f'letter-spacing="-.4" fill="#2A0E04" fill-opacity=".86">RobyRew</text>'
    )
    svg.use("mono-md", "SIDE A")
    parts.append(
        f'<text x="{num(cx)}" y="{num(cy + 18)}" text-anchor="middle" class="f-mono-md" font-size="6.5" '
        f'letter-spacing="1.6" fill="#2A0E04" fill-opacity=".7">SIDE A</text>'
    )
    parts.append("</g>")
    # Light catching the grooves; it stays put while the disc turns.
    for base in (-50, 130):
        for spread in (30, 22, 15, 9, 4):
            parts.append(
                f'<path d="{sector(cx, cy, label_r + 4, r - 1, base - spread, base + spread)}" fill="#fff" fill-opacity=".022"/>'
            )
    parts.append(
        f'<circle cx="{num(cx)}" cy="{num(cy)}" r="{num(r - 0.6)}" fill="none" stroke="#fff" stroke-opacity=".16" stroke-width="1.2"/>'
    )
    svg.add("".join(parts))


def tonearm(svg, px, py, points, rest=None):
    metal = svg.uid("metal")
    svg.defs.append(
        f'<linearGradient id="{metal}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F4F4F6"/>'
        f'<stop offset=".5" stop-color="#A9A9B2"/><stop offset="1" stop-color="#6B6B74"/></linearGradient>'
    )
    if rest:
        rx, ry = rest
        svg.add(
            f'<rect x="{num(rx - 7)}" y="{num(ry - 2)}" width="14" height="22" rx="4" fill="#2B2B30"/>'
            f'<rect x="{num(rx - 7)}" y="{num(ry - 2)}" width="14" height="22" rx="4" fill="none" stroke="#fff" stroke-opacity=".15"/>'
        )
    path = "M" + " L".join(f"{num(x)} {num(y)}" for x, y in [(px, py)] + points)
    hx, hy = points[-1]
    ax, ay = points[-2] if len(points) > 1 else (px, py)
    angle = math.degrees(math.atan2(hy - ay, hx - ax))
    svg.add(
        f'<path d="{path}" fill="none" stroke="#000" stroke-opacity=".35" stroke-width="9" stroke-linecap="round" '
        f'stroke-linejoin="round" transform="translate(4 7)"/>'
        f'<path d="{path}" fill="none" stroke="url(#{metal})" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="{path}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="1.2" stroke-linecap="round" '
        f'stroke-linejoin="round" transform="translate(-1.2 -1)"/>'
        f'<g transform="translate({num(hx)} {num(hy)}) rotate({num(angle)})">'
        f'<rect x="-6" y="-8" width="24" height="16" rx="3.5" fill="url(#{metal})"/>'
        f'<rect x="12" y="-3" width="7" height="6" rx="1.5" fill="#2B2B30"/></g>'
        f'<rect x="{num(px - 9)}" y="{num(py - 46)}" width="18" height="26" rx="5" fill="url(#{metal})"/>'
        f'<circle cx="{num(px)}" cy="{num(py)}" r="19" fill="url(#{metal})"/>'
        f'<circle cx="{num(px)}" cy="{num(py)}" r="19" fill="none" stroke="#000" stroke-opacity=".25"/>'
        f'<circle cx="{num(px)}" cy="{num(py)}" r="7.5" fill="#2B2B30"/>'
    )


def now_panel(svg, x, y, w, h, now):
    t = svg.t
    svg.glass(x, y, w, h, 20, fill=t["panel"])
    playing = bool(now and now.get("playing"))
    if playing:
        status = "NOW PLAYING"
    elif now and now.get("paused"):
        status = "PAUSED"
    else:
        status = "LAST PLAYED" if now else "OFF AIR"
    dot = "#30D158" if playing else "#8E8E93"
    if playing:
        svg.add(f'<circle cx="{num(x + 22)}" cy="{num(y + 24)}" r="8" fill="#30D158" fill-opacity=".22"/>')
        svg.add(f'<circle class="pulse" cx="{num(x + 22)}" cy="{num(y + 24)}" r="4.2" fill="{dot}"/>')
    else:
        svg.add(f'<circle cx="{num(x + 22)}" cy="{num(y + 24)}" r="4.2" fill="{dot}"/>')
    svg.text(x + 34, y + 28, status, "mono-md", 10.5, t["ink"], tracking=1.8)
    if not now:
        svg.text(x + 18, y + 62, "Nothing on the deck right now.", "semi", 16, t["ink"])
        svg.text(x + 18, y + 84, "Music is usually on. Check back soon.", "text", 13.5, t["dim"])
        return
    platform = now.get("platform", "")
    if platform:
        tag = f'{platform} · @{now["user"]}' if now.get("user") else platform
        tag = FACES["mono-md"].fit(tag.upper(), 10, w - 150, 1.4)
        width = FACES["mono-md"].width(tag, 10, 1.4)
        svg.add(f'<circle cx="{num(x + w - 22 - width - 8)}" cy="{num(y + 24)}" r="4" fill="{PLATFORMS.get(platform, "#9CA3AF")}"/>')
        svg.text(x + w - 18, y + 28, tag, "mono-md", 10, t["dim"], tracking=1.4, anchor="end")
    art = 54
    artwork(svg, x + 16, y + 44, art, now.get("cover"), now.get("title", ""))
    tx = x + 16 + art + 14
    room = x + w - 16 - tx
    svg.text(tx, y + 66, FACES["semi"].fit(now.get("title", ""), 16.5, room), "semi", 16.5, t["ink"])
    svg.text(tx, y + 87, FACES["text"].fit(now.get("artist", ""), 13.5, room), "text", 13.5, t["dim"])
    meta = []
    if now.get("context"):
        meta.append(("list", now["context"]))
    if now.get("device"):
        meta.append((DEVICE_ICONS.get((now.get("device_type") or "").lower(), "speaker"), now["device"]))
    cx, cy = x + 16, y + h - 20
    for icon, value in meta:
        value = FACES["text"].fit(value, 12, 150)
        width = FACES["text"].width(value, 12) + 18
        if cx + width > x + w - 12:
            break
        svg.icon(icon, cx, cy - 10, 13, t["faint"], stroke=2)
        svg.text(cx + 17, cy, value, "text", 12, t["faint"])
        cx += width + 12


def hero(theme, p, now):
    me = p["me"]
    playing = bool(now and now.get("playing"))
    label = f'{me["name"]}. {me["statement"]} {me["aside"]}'
    if now:
        label += f' {"Now playing" if playing else "Last played"}: {now.get("title", "")} by {now.get("artist", "")}.'
    H = 548
    svg = SVG(theme, W, H + GAP, label)
    t = svg.t
    svg.css.append(
        ".drift{animation:drift 18s ease-in-out infinite alternate}"
        "@keyframes drift{to{transform:translate(-36px,22px)}}"
        ".pulse{animation:pulse 1.6s ease-in-out infinite alternate}@keyframes pulse{to{opacity:.3}}"
    )
    x0 = PAD
    svg.card(
        x0, 0, CW, H, 30, "ember",
        [(0.9, 1.0, 0.62, 0, 1), (0.08, 1.12, 0.5, 1, 0.9), (0.98, -0.08, 0.42, 2, 0.85), (0.45, -0.2, 0.36, 1, 0.5)],
        drift=True,
    )
    veil = svg.uid("veil")
    svg.defs.append(
        f'<linearGradient id="{veil}"><stop offset="0" stop-color="{t["base"]}" stop-opacity="{t["veil"]}"/>'
        f'<stop offset=".62" stop-color="{t["base"]}" stop-opacity="0"/></linearGradient>'
    )
    svg.add(f'<rect x="{x0}" width="{CW}" height="{H}" rx="30" fill="url(#{veil})"/>')

    facts = me.get("facts", [])
    left = x0 + 36
    if facts:
        pill = f'{facts[0]["label"]} · {facts[0]["value"]}'.upper()
        width = FACES["mono-md"].width(pill, 11, 1.4) + 44
        svg.glass(left, 36, width, 32, 16)
        svg.add(f'<circle cx="{left + 18}" cy="52" r="8" fill="#FFB347" fill-opacity=".22"/>')
        svg.add(f'<circle cx="{left + 18}" cy="52" r="4.5" fill="#FFB347"/>')
        svg.text(left + 32, 56, pill, "mono-md", 11, t["ink"], tracking=1.4)

    cx, cy, r = x0 + 626, 210, 146
    size = 108
    while size > 60 and FACES["display"].width(me["name"], size, -size * 0.04) > cx - r - left - 36:
        size -= 2
    svg.text(left - 4, 204, me["name"], "display", size, t["ink"], tracking=-size * 0.04)
    y = 252
    for line in FACES["text"].wrap(me["statement"], 21, 410):
        svg.text(left, y, line, "text", 21, t["dim"])
        y += 29
    y += 4
    for line in FACES["semi"].wrap(me["aside"], 21, 410):
        svg.text(left, y, line, "semi", 21, t["aside"])
        y += 29

    x = left
    for fact in facts[1:]:
        x += svg.chip(x, H - 36 - 34, fact["value"], h=34, size=14, icon=fact.get("icon", "spark")) + 10

    record(svg, cx, cy, r, me["record"], playing)
    px, py = cx + 150, 72
    if playing:
        tonearm(svg, px, py, [(px + 8, cy + 22), (cx + 102, cy + 72)])
    else:
        tonearm(svg, px, py, [(px + 8, cy + 104), (px + 9, cy + 118)], rest=(px + 9, cy + 122))
    now_panel(svg, cx - 150, 382, 300 + 8, 130, now)
    return svg


# ── sections ─────────────────────────────────────────────────────────────────


def section(theme, kicker, title, right, label):
    svg = SVG(theme, W, 104, label)
    t = svg.t
    svg.text(PAD + 4, 58, kicker.upper(), "mono-md", 11, t["accent"], tracking=2.2)
    svg.text(PAD + 2, 92, title, "display", 32, t["head"], tracking=-0.8)
    svg.text(W - PAD - 4, 92, right.upper(), "mono", 11, t["muted"], tracking=1.6, anchor="end")
    return svg


def link_button(theme, link, index):
    hue = link.get("hue") or ("ember", "blue", "green", "rose")[index % 4]
    label = link["label"]
    icon = link.get("icon", "globe")
    width = 54 + FACES["semi"].width(label, 16) + 44
    svg = SVG(theme, math.ceil(width) + 12, 64, f'{label}: {link["url"]}')
    colors = HUES[hue]
    grad = svg.uid("btn")
    svg.defs.append(
        f'<linearGradient id="{grad}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{colors[0]}"/>'
        f'<stop offset="1" stop-color="{colors[1]}"/></linearGradient>'
    )
    w = svg.width - 12
    svg.add(
        f'<rect x="6" y="8" width="{num(w)}" height="48" rx="24" fill="#000" opacity=".25" transform="translate(0 3)"/>'
        f'<rect x="6" y="6" width="{num(w)}" height="48" rx="24" fill="url(#{grad})"/>'
        f'<rect x="6.5" y="6.5" width="{num(w - 1)}" height="47" rx="23.5" fill="none" stroke="#fff" stroke-opacity=".25"/>'
        f'<circle cx="31" cy="30" r="17" fill="#fff" fill-opacity=".2"/>'
    )
    svg.icon(icon, 22, 21, 18, "#FFFFFF", stroke=2)
    svg.text(56, 35.5, label, "semi", 16, "#FFFFFF")
    svg.icon("arrow", w - 22, 23, 14, ("#FFFFFF", 0.85), stroke=2.2)
    return svg


def window_mock(svg, x, y, w, h, hue):
    t = svg.t
    colors = HUES.get(hue, HUES["ember"])
    shadow, slide = svg.uid("wshadow"), svg.uid("slide")
    svg.defs.append(
        f'<filter id="{shadow}" x="-20%" y="-20%" width="140%" height="160%"><feGaussianBlur stdDeviation="12"/></filter>'
        f'<linearGradient id="{slide}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{colors[1]}"/>'
        f'<stop offset="1" stop-color="#140A0A"/></linearGradient>'
    )
    svg.add(
        f'<rect x="{num(x + 6)}" y="{num(y + 16)}" width="{num(w - 12)}" height="{num(h)}" rx="14" fill="#000" '
        f'opacity=".45" filter="url(#{shadow})"/>'
        f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" rx="12" fill="{t["window"]}"/>'
        f'<rect x="{num(x + 0.5)}" y="{num(y + 0.5)}" width="{num(w - 1)}" height="{num(h - 1)}" rx="12" fill="none" '
        f'{paint(t["edge"], "stroke")}/>'
    )
    for i, color in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        svg.add(f'<circle cx="{num(x + 16 + i * 15)}" cy="{num(y + 14)}" r="4.6" fill="{color}"/>')
    sx, sy, sw, sh = x + 10, y + 28, w - 20, h - 74
    svg.add(f'<rect x="{num(sx)}" y="{num(sy)}" width="{num(sw)}" height="{num(sh)}" rx="7" fill="url(#{slide})"/>')
    for width, height, dy, opacity in ((0.56, 9, 0.38, 0.92), (0.74, 5, 0.56, 0.6), (0.48, 5, 0.67, 0.6)):
        svg.add(
            f'<rect x="{num(sx + sw * (1 - width) / 2)}" y="{num(sy + sh * dy)}" width="{num(sw * width)}" '
            f'height="{height}" rx="{height / 2}" fill="#fff" fill-opacity="{opacity}"/>'
        )
    svg.add(f'<rect x="{num(sx + 10)}" y="{num(sy + 9)}" width="34" height="13" rx="6.5" fill="#FF3B30"/>')
    svg.text(sx + 27, sy + 18.6, "LIVE", "mono-md", 7.5, "#FFFFFF", tracking=1, anchor="middle")
    thumb_w = (sw - 3 * 8) / 4
    for i in range(4):
        tx = sx + i * (thumb_w + 8)
        svg.add(
            f'<rect x="{num(tx)}" y="{num(y + h - 38)}" width="{num(thumb_w)}" height="28" rx="5" '
            f'fill="{colors[i % 3]}" fill-opacity="{num(0.55 if i else 0.9)}"'
            + (f' stroke="{t["ink"]}" stroke-width="1.5"' if i == 0 else "")
            + "/>"
        )


def meta_chips(svg, x, y, project, h=28, size=13.5):
    if project["language"]:
        x += svg.chip(x, y, project["language"], h=h, size=size, dot=LANGUAGES.get(project["language"], "#9CA3AF")) + 8
    if project["stars"]:
        svg.chip(x, y, str(project["stars"]), h=h, size=size, star=True)


def project_card(theme, project, index, wide):
    t = THEMES[theme]
    note = project["note"]
    label = f'{project["name"]}{": " + note if note else ""}'
    hue = project["hue"]
    if wide:
        H = 266
        svg = SVG(theme, W, H + GAP, label)
        x0 = PAD
        svg.card(x0, 0, CW, H, 26, hue, blobs_for(index))
        svg.glass(x0 + 32, 32, 58, 58, 17)
        svg.icon(project["icon"], x0 + 46, 46, 30, t["ink"])
        illustrated = project["icon"] == "presentation"
        text_w = 400 if illustrated else CW - 64
        svg.text(x0 + 30, 138, FACES["display"].fit(project["name"], 38, text_w, -1), "display", 38, t["ink"], tracking=-1)
        y = 167
        for line in FACES["text"].wrap(note, 16.5, text_w, 2):
            svg.text(x0 + 32, y, line, "text", 16.5, t["dim"])
            y += 23
        meta_chips(svg, x0 + 32, H - 32 - 28, project)
        if illustrated:
            window_mock(svg, x0 + 470, 40, 262, 190, hue)
        svg.glass(x0 + CW - 32 - 34, 32, 34, 34, 17)
        svg.icon("arrow", x0 + CW - 32 - 26, 40, 18, t["ink"])
        return svg
    H = 228
    w = HALF - 2 * HP
    svg = SVG(theme, HALF, H + GAP, label)
    svg.card(HP, 0, w, H, 24, hue, blobs_for(index))
    x0 = HP
    svg.glass(x0 + 24, 24, 48, 48, 14)
    svg.icon(project["icon"], x0 + 36, 36, 24, t["ink"])
    svg.glass(x0 + w - 24 - 30, 24, 30, 30, 15)
    svg.icon("arrow", x0 + w - 24 - 23, 31, 16, t["ink"])
    svg.text(x0 + 22, 110, FACES["display"].fit(project["name"], 24, w - 48, -0.6), "display", 24, t["ink"], tracking=-0.6)
    y = 135
    for line in FACES["text"].wrap(note, 14.5, w - 48, 2):
        svg.text(x0 + 24, y, line, "text", 14.5, t["dim"])
        y += 20
    meta_chips(svg, x0 + 24, H - 24 - 26, project, h=26, size=13)
    return svg


def recent_row(theme, repo, index):
    t = THEMES[theme]
    label = f'{repo["name"]}: {repo["description"]}'.strip(": ")
    H = 76
    svg = SVG(theme, W, H + 10, label)
    x0 = PAD
    svg.card(x0, 0, CW, H, 20, "graphite", [(0.02, 0.5, 0.3, 0, 0.8), (1.0, 0.5, 0.25, 2, 0.5)])
    svg.glass(x0 + 18, 16, 44, 44, 13)
    svg.text(x0 + 40, 45, f"{index:02d}", "mono-md", 13, t["ink"], tracking=0.5, anchor="middle")
    right = x0 + CW - 20
    pushed = repo.get("pushed", "")
    if pushed:
        stamp = datetime.fromisoformat(pushed.replace("Z", "+00:00")).strftime("%b %Y").upper()
        right -= svg.text(right, 43, stamp, "mono", 11, t["faint"], tracking=1.2, anchor="end") + 16
    chips_w = 0
    if repo.get("stars"):
        chips_w += 24 + 21 + FACES["semi"].width(str(repo["stars"]), 12.5) + 8
    if repo.get("language"):
        chips_w += 24 + 15 + FACES["semi"].width(repo["language"], 12.5) + 8
    cx = right - chips_w
    meta_chips(svg, cx, 25, {"language": repo.get("language"), "stars": repo.get("stars")}, h=26, size=12.5)
    room = cx - (x0 + 78) - 20
    svg.text(x0 + 78, 34, FACES["semi"].fit(repo["name"], 17.5, room), "semi", 17.5, t["ink"])
    svg.text(x0 + 78, 55, FACES["text"].fit(repo.get("description") or "No description yet.", 13.5, room), "text", 13.5, t["dim"])
    return svg


def hexdump(svg, x, y, w, h, seed):
    digest = hashlib.sha256(seed.encode()).hexdigest() * 8
    rows = int(h // 15)
    cols = int(w // 22)
    for i in range(rows):
        chunk = digest[i * cols * 2:(i + 1) * cols * 2]
        line = " ".join(chunk[j:j + 2] for j in range(0, len(chunk), 2)).upper()
        svg.text(x, y + i * 15, line, "mono", 10, (svg.t["ink"], 0.06), tracking=0.4)


def highlights(theme, items):
    label = " ".join(f'{i["value"]} {i["title"]}: {i["note"]}' for i in items)
    H = 180
    svg = SVG(theme, W, H + GAP, label)
    t = svg.t
    n = max(len(items), 1)
    gap = 16
    tile = (CW - gap * (n - 1)) / n
    for i, item in enumerate(items):
        x = PAD + i * (tile + gap)
        svg.card(x, 0, tile, H, 22, item.get("hue", HUE_ORDER[i % len(HUE_ORDER)]), blobs_for(i + 1))
        if item.get("texture") == "hex":
            clip = svg.uid("hex")
            svg.defs.append(f'<clipPath id="{clip}"><rect x="{num(x)}" y="0" width="{num(tile)}" height="{H}" rx="22"/></clipPath>')
            svg.add(f'<g clip-path="url(#{clip})">')
            hexdump(svg, x + 14, 22, tile - 20, H - 20, item["title"])
            svg.add("</g>")
        tag = f"B{i + 1}"
        tag_w = FACES["mono-md"].width(tag, 10, 1) + 18
        svg.glass(x + tile - 20 - tag_w, 20, tag_w, 22, 11)
        svg.text(x + tile - 20 - tag_w / 2, 35, tag, "mono-md", 10, t["ink"], tracking=1, anchor="middle")
        value = FACES["display"].fit(item["value"], 46, tile - 90, -1.5)
        svg.text(x + 20, 72, value, "display", 46, t["ink"], tracking=-1.5)
        svg.text(x + 22, 106, FACES["semi"].fit(item["title"], 16.5, tile - 44), "semi", 16.5, t["ink"])
        y = 130
        for line in FACES["text"].wrap(item["note"], 13.5, tile - 44, 2):
            svg.text(x + 22, y, line, "text", 13.5, t["dim"])
            y += 19
    return svg


def heat_colors(theme):
    # Index 0 is the empty cell, drawn with the theme's "heat" colour instead.
    if theme == "dark":
        return (None, "#7A2E14", "#C2410C", "#FF7A3D", "#FFC08A")
    return (None, "#FFC6A3", "#FF9A61", "#F0631F", "#B8410C")


def activity(theme, stats):
    cal = stats["calendar"]
    total = stats["contributions"]
    label = f"{total} contributions in the last year. Current streak {stats['streak']} days, longest {stats['longest']} days."
    H = 384
    svg = SVG(theme, W, H + GAP, label)
    t = svg.t
    x0 = PAD
    svg.card(x0, 0, CW, H, 26, "blue", [(0.0, 0.0, 0.5, 2, 0.8), (1.0, 1.0, 0.5, 0, 0.75), (0.7, -0.2, 0.3, 1, 0.5)])
    svg.text(x0 + 32, 46, "ACTIVITY", "mono-md", 11, t["ink"], tracking=2.2)
    svg.text(x0 + 30, 86, f"{total:,} contributions", "display", 30, t["ink"], tracking=-0.8)
    svg.text(x0 + CW - 32, 46, "LAST 12 MONTHS · GITHUB", "mono", 10.5, t["faint"], tracking=1.6, anchor="end")
    blocks = [
        ("Commits", stats["commits"]),
        ("Pull requests", stats["prs"]),
        ("Issues", stats["issues"]),
        ("Reviews", stats["reviews"]),
        ("Current streak", f'{stats["streak"]}d'),
        ("Longest streak", f'{stats["longest"]}d'),
    ]
    bw = (CW - 64 - 5 * 10) / 6
    for i, (name, value) in enumerate(blocks):
        bx = x0 + 32 + i * (bw + 10)
        svg.glass(bx, 108, bw, 66, 14)
        svg.text(bx + 14, 142, compact(value) if isinstance(value, int) else value, "display", 24, t["ink"], tracking=-0.6)
        svg.text(bx + 14, 162, FACES["mono"].fit(name.upper(), 9, bw - 24, 1), "mono", 9, t["faint"], tracking=1)
    colors = heat_colors(theme)
    cell, step = 10, 13
    weeks = cal[-53:]
    gx = x0 + 32 + 28 + (CW - 64 - 28 - len(weeks) * step) / 2
    gy = 214
    peak = max([d for week in weeks for _, d in week] + [1])
    last_month = None
    for wi, week in enumerate(weeks):
        for day, count in week:
            weekday = date.fromisoformat(day).isoweekday() % 7
            if count == 0:
                fill = paint(t["heat"])
            else:
                fill = f'fill="{colors[max(1, min(4, math.ceil(4 * count / peak)))]}"'
            svg.add(f'<rect x="{num(gx + wi * step)}" y="{num(gy + weekday * step)}" width="{cell}" height="{cell}" rx="2.5" {fill}/>')
        month = date.fromisoformat(week[0][0]).strftime("%b")
        if month != last_month:
            if wi and wi < len(weeks) - 2:
                svg.text(gx + wi * step, gy - 8, month.upper(), "mono", 9, t["faint"], tracking=0.8)
            last_month = month
    for wd, name in ((1, "MON"), (3, "WED"), (5, "FRI")):
        svg.text(x0 + 32, gy + wd * step + 9, name, "mono", 8.5, t["faint"], tracking=0.6)
    lx = x0 + CW - 32 - 5 * step - 34
    ly = gy + 7 * step + 22
    svg.text(lx - 8, ly + 9, "LESS", "mono", 9, t["faint"], tracking=0.8, anchor="end")
    for i in range(5):
        fill = paint(t["heat"]) if i == 0 else f'fill="{colors[i]}"'
        svg.add(f'<rect x="{num(lx + i * step)}" y="{num(ly)}" width="{cell}" height="{cell}" rx="2.5" {fill}/>')
    svg.text(lx + 5 * step + 4, ly + 9, "MORE", "mono", 9, t["faint"], tracking=0.8)
    svg.text(x0 + 32, ly + 9, f'{stats["active_days"]} ACTIVE DAYS · {stats["repos_contributed"]} REPOS', "mono", 9, t["faint"], tracking=0.8)
    return svg


def popularity(theme, stats):
    langs = stats["languages"]
    label = (
        f'{stats["stars"]} stars, {stats["followers"]} followers, {stats["forks"]} forks, {stats["original"]} original repos. '
        + "Languages: " + ", ".join(f'{n} {p:.0f}%' for n, p, _ in langs)
    )
    H = 236
    svg = SVG(theme, W, H + GAP, label)
    t = svg.t
    cw = (CW - 16) / 2
    lx = PAD
    svg.card(lx, 0, cw, H, 24, "rose", blobs_for(0))
    svg.text(lx + 26, 42, "POPULARITY", "mono-md", 11, t["ink"], tracking=2.2)
    cells = [("Stars earned", stats["stars"], True), ("Followers", stats["followers"], False),
             ("Forks", stats["forks"], False), ("Original repos", stats["original"], False)]
    for i, (name, value, star) in enumerate(cells):
        cx = lx + 26 + (i % 2) * (cw / 2 - 10)
        cy = 66 + (i // 2) * 80
        width = svg.text(cx, cy + 40, compact(value), "display", 40, t["ink"], tracking=-1.2)
        if star:
            svg.add(f'<path d="{STAR}" fill="#FFC53D" transform="translate({num(cx + width + 8)} {num(cy + 16)}) scale(.9)"/>')
        svg.text(cx + 2, cy + 62, name.upper(), "mono", 9.5, t["faint"], tracking=1.2)
    rx = PAD + cw + 16
    svg.card(rx, 0, cw, H, 24, "teal", blobs_for(1))
    svg.text(rx + 26, 42, "LANGUAGES", "mono-md", 11, t["ink"], tracking=2.2)
    bar_w = cw - 52
    bx = rx + 26
    clip = svg.uid("bar")
    svg.defs.append(f'<clipPath id="{clip}"><rect x="{num(bx)}" y="66" width="{num(bar_w)}" height="14" rx="7"/></clipPath>')
    svg.add(f'<g clip-path="url(#{clip})">')
    svg.add(f'<rect x="{num(bx)}" y="66" width="{num(bar_w)}" height="14" {paint(t["heat"])}/>')
    offset = 0
    for _, share, color in langs:
        width = bar_w * share / 100
        svg.add(f'<rect x="{num(bx + offset)}" y="66" width="{num(width + 0.5)}" height="14" fill="{color}"/>')
        offset += width
    svg.add("</g>")
    for i, (name, share, color) in enumerate(langs[:8]):
        cx = bx + (i % 2) * (bar_w / 2)
        cy = 112 + (i // 2) * 30
        svg.add(f'<circle cx="{num(cx + 5)}" cy="{num(cy - 4)}" r="5" fill="{color}"/>')
        svg.text(cx + 18, cy, FACES["semi"].fit(name, 14.5, bar_w / 2 - 70), "semi", 14.5, t["ink"])
        svg.text(cx + bar_w / 2 - 14, cy, f"{share:.1f}%", "mono", 11.5, t["faint"], anchor="end")
    return svg


def rotation(theme, title, tracks):
    label = "On rotation: " + "; ".join(f'{x["name"]} by {x["artist"]}' for x in tracks)
    H = 128 + 60 * len(tracks)
    svg = SVG(theme, W, H + GAP, label)
    t = svg.t
    x0 = PAD
    svg.card(x0, 0, CW, H, 26, "green", [(1.0, -0.1, 0.6, 0, 0.9), (0.0, 1.1, 0.5, 1, 0.7), (0.7, 1.2, 0.35, 2, 0.5)])
    svg.text(x0 + 32, 46, "ON ROTATION", "mono-md", 11, t["ink"], tracking=2.2)
    x = x0 + 32 + FACES["mono-md"].width("ON ROTATION", 11, 2.2) + 10
    svg.css.append(
        ".eq rect{transform-box:fill-box;transform-origin:50% 100%;animation:eq .9s ease-in-out infinite alternate}"
        "@keyframes eq{from{transform:scaleY(.3)}}"
    )
    bars = "".join(
        f'<rect x="{num(x + i * 5)}" y="35" width="3" height="12" rx="1" fill="#30D158" '
        f'style="animation-delay:{num(-0.27 * i * (i + 1))}s"/>'
        for i in range(4)
    )
    svg.add(f'<g class="eq">{bars}</g>')
    svg.text(x0 + 30, 86, title, "display", 30, t["ink"], tracking=-0.8)
    svg.text(x0 + CW - 32, 46, "TOP TRACKS · SPOTIFY", "mono", 10.5, t["faint"], tracking=1.6, anchor="end")
    for n, item in enumerate(tracks):
        y = 112 + n * 60
        if n:
            svg.add(f'<line x1="{x0 + 32}" y1="{y - 8}" x2="{x0 + CW - 32}" y2="{y - 8}" {paint(t["edge"], "stroke")}/>')
        artwork(svg, x0 + 32, y, 44, item.get("cover"), item["name"])
        minutes, seconds = divmod(round(item["ms"] / 1000), 60)
        svg.text(x0 + CW - 32, y + 27, f"{minutes}:{seconds:02d}", "mono", 12, t["faint"], tracking=0.5, anchor="end")
        room = CW - 92 - 32 - 60
        svg.text(x0 + 92, y + 19, FACES["semi"].fit(item["name"], 16.5, room), "semi", 16.5, t["ink"])
        svg.text(x0 + 92, y + 39, FACES["text"].fit(item["artist"], 14, room), "text", 14, t["dim"])
    return svg


def credits(theme, title, items):
    label = "Credits. " + "; ".join(f'{i["label"]}: {i["value"]}' for i in items)
    rows = math.ceil(len(items) / 2)
    H = 116 + 74 * rows
    svg = SVG(theme, W, H + GAP, label)
    t = svg.t
    x0 = PAD
    svg.card(x0, 0, CW, H, 26, "graphite", [(0.0, 0.0, 0.55, 0, 0.7), (1.0, 1.0, 0.55, 2, 0.6)])
    svg.text(x0 + 32, 46, "CREDITS", "mono-md", 11, t["ink"], tracking=2.2)
    svg.text(x0 + 30, 86, title, "display", 30, t["ink"], tracking=-0.8)
    col = (CW - 64) / 2
    for n, item in enumerate(items):
        x = x0 + 32 + (n % 2) * (col + 16)
        y = 124 + (n // 2) * 74
        svg.text(x, y, item["label"].upper(), "mono", 10.5, t["faint"], tracking=1.6)
        cx = x
        for value in (v.strip() for v in item["value"].split(",")):
            width = FACES["semi"].width(value, 13.5) + 24
            if cx + width > x + col:
                break
            cx += svg.chip(cx, y + 12, value, h=30, size=13.5) + 8
    return svg


def colophon(theme, left, right):
    svg = SVG(theme, W, 58, f"{left}. {right}")
    t = svg.t
    svg.text(PAD + 4, 36, left.upper(), "mono", 10, t["muted"], tracking=1.6)
    svg.text(W - PAD - 4, 36, right.upper(), "mono", 10, t["muted"], tracking=1.6, anchor="end")
    return svg


# ── data ─────────────────────────────────────────────────────────────────────


def fetch(url, headers=None, data=None):
    request = urllib.request.Request(url, data=data, headers={"User-Agent": "robyrew-profile", **(headers or {})})
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read()
    return json.loads(body) if body else None


def github_headers():
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GH_STATS_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def github_data(p, cache):
    data = cache.setdefault("github", {"user": {}, "repos": {}})
    headers = github_headers()
    login = p["me"]["github"]
    try:
        user = fetch(f"https://api.github.com/users/{login}", headers)
        data["user"] = {"public_repos": user["public_repos"], "created_at": user["created_at"]}
    except Exception as error:
        print(f"github: keeping cached user ({error})", file=sys.stderr)
    for project in p["work"]["projects"]:
        name = project["repo"]
        try:
            repo = fetch(f"https://api.github.com/repos/{login}/{name}", headers)
        except Exception as error:
            print(f"github: keeping cached {name} ({error})", file=sys.stderr)
            continue
        if repo.get("private"):
            data["repos"].pop(name, None)
            continue
        data["repos"][name] = {
            "description": repo.get("description") or "",
            "language": repo.get("language") or "",
            "stars": repo.get("stargazers_count", 0),
            "url": repo.get("html_url") or f"https://github.com/{login}/{name}",
        }
    repository = os.environ.get("GITHUB_REPOSITORY", f"{login}/{login}")
    try:
        pages = fetch(f"https://api.github.com/repos/{repository}/pages", headers)
        if pages and pages.get("html_url"):
            cache["pages_url"] = pages["html_url"].rstrip("/") + "/"
    except Exception as error:
        print(f"github: no pages site ({error})", file=sys.stderr)


STATS_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!, $after: String) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100, after: $after,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        name description url stargazerCount forkCount pushedAt isArchived
        primaryLanguage { name }
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } }
      }
    }
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions totalPullRequestContributions totalIssueContributions
      totalPullRequestReviewContributions totalRepositoriesWithContributedCommits restrictedContributionsCount
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
  }
}
"""


def stats_data(p, cache):
    headers = github_headers()
    if "Authorization" not in headers:
        return
    login = p["me"]["github"]
    now = datetime.now(timezone.utc)
    variables = {"login": login, "from": (now - timedelta(days=365)).isoformat(), "to": now.isoformat(), "after": None}
    repos, user = [], None
    try:
        while True:
            body = json.dumps({"query": STATS_QUERY, "variables": variables}).encode()
            result = fetch("https://api.github.com/graphql", {**headers, "Content-Type": "application/json"}, body)
            if result.get("errors"):
                raise RuntimeError(result["errors"][0].get("message"))
            user = result["data"]["user"]
            page = user["repositories"]
            repos += page["nodes"]
            if not page["pageInfo"]["hasNextPage"]:
                break
            variables["after"] = page["pageInfo"]["endCursor"]
    except Exception as error:
        print(f"github: keeping cached stats ({error})", file=sys.stderr)
        return
    collection = user["contributionsCollection"]
    calendar = [
        [(d["date"], d["contributionCount"]) for d in week["contributionDays"]]
        for week in collection["contributionCalendar"]["weeks"]
    ]
    days = [count for week in calendar for _, count in week]
    longest = run = 0
    for count in days:
        run = run + 1 if count else 0
        longest = max(longest, run)
    streak = 0
    for i, count in enumerate(reversed(days)):
        if count:
            streak += 1
        elif i:  # today may still be empty
            break
    sizes = {}
    colors = {}
    for repo in repos:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            sizes[name] = sizes.get(name, 0) + edge["size"]
            colors[name] = edge["node"]["color"] or "#9CA3AF"
    total = sum(sizes.values()) or 1
    ranked = sorted(sizes.items(), key=lambda kv: -kv[1])
    languages = [[name, round(100 * size / total, 1), colors[name]] for name, size in ranked[:7]]
    rest = 100 - sum(share for _, share, _ in languages)
    if len(ranked) > 7 and rest > 0.05:
        languages.append(["Other", round(rest, 1), "#8B949E"])
    cache["stats"] = {
        "contributions": collection["contributionCalendar"]["totalContributions"],
        "commits": collection["totalCommitContributions"],
        "prs": collection["totalPullRequestContributions"],
        "issues": collection["totalIssueContributions"],
        "reviews": collection["totalPullRequestReviewContributions"],
        "repos_contributed": collection["totalRepositoriesWithContributedCommits"],
        "active_days": sum(1 for count in days if count),
        "streak": streak,
        "longest": longest,
        "calendar": calendar,
        "stars": sum(r["stargazerCount"] for r in repos),
        "forks": sum(r["forkCount"] for r in repos),
        "followers": user["followers"]["totalCount"],
        "original": user["repositories"]["totalCount"],
        "languages": languages,
    }
    cache["recent"] = [
        {
            "name": r["name"],
            "description": r["description"] or "",
            "url": r["url"],
            "stars": r["stargazerCount"],
            "language": (r["primaryLanguage"] or {}).get("name", ""),
            "pushed": r["pushedAt"],
        }
        for r in repos
        if not r["isArchived"]
    ][:20]


def spotify_token():
    keys = ("SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "SPOTIFY_REFRESH_TOKEN")
    client_id, secret, refresh = (os.environ.get(k) for k in keys)
    if not (client_id and secret and refresh):
        return None
    auth = base64.b64encode(f"{client_id}:{secret}".encode()).decode()
    return fetch(
        "https://accounts.spotify.com/api/token",
        {"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"},
        urllib.parse.urlencode({"grant_type": "refresh_token", "refresh_token": refresh}).encode(),
    )["access_token"]


def smallest_image(images, minimum=64):
    images = [i for i in images or [] if i.get("url")]
    if not images:
        return ""
    fitting = [i for i in images if (i.get("width") or 0) >= minimum]
    return min(fitting or images, key=lambda i: i.get("width") or 0)["url"]


def spotify_top(p, cache, token):
    limit = int(p.get("listening", {}).get("tracks", 5))
    bearer = {"Authorization": f"Bearer {token}"}
    try:
        items = fetch(f"https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit={limit}", bearer)["items"]
    except Exception as error:
        print(f"spotify: keeping cached top tracks ({error})", file=sys.stderr)
        return
    if items:
        cache["spotify"] = [
            {
                "name": item["name"],
                "artist": ", ".join(a["name"] for a in item["artists"]),
                "ms": item["duration_ms"],
                "cover": smallest_image(item.get("album", {}).get("images")),
            }
            for item in items
        ]


def spotify_context(context, item, bearer):
    if not context:
        return ""
    kind = context.get("type")
    if kind == "playlist":
        try:
            playlist = fetch(f'https://api.spotify.com/v1/playlists/{context["uri"].split(":")[-1]}?fields=name', bearer)
            return playlist["name"]
        except Exception:
            return "A playlist"
    if kind == "album":
        return item.get("album", {}).get("name", "")
    if kind == "artist":
        return f'{item["artists"][0]["name"]} radio' if item.get("artists") else ""
    if kind == "collection":
        return "Liked Songs"
    return ""


def spotify_now(token):
    bearer = {"Authorization": f"Bearer {token}"}
    me = fetch("https://api.spotify.com/v1/me", bearer) or {}
    user = me.get("display_name") or me.get("id") or ""
    player = fetch("https://api.spotify.com/v1/me/player?additional_types=track,episode", bearer)
    if player and player.get("item"):
        item = player["item"]
        device = player.get("device") or {}
        return {
            "playing": bool(player.get("is_playing")),
            "paused": not player.get("is_playing"),
            "title": item.get("name", ""),
            "artist": ", ".join(a["name"] for a in item.get("artists", [])) or item.get("show", {}).get("name", ""),
            "cover": smallest_image(item.get("album", {}).get("images") or item.get("images")),
            "context": spotify_context(player.get("context"), item, bearer),
            "device": device.get("name", ""),
            "device_type": device.get("type", ""),
            "user": user,
            "platform": "Spotify",
            "when": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        }
    recent = fetch("https://api.spotify.com/v1/me/player/recently-played?limit=1", bearer)
    if recent and recent.get("items"):
        play = recent["items"][0]
        item = play["track"]
        return {
            "playing": False,
            "title": item["name"],
            "artist": ", ".join(a["name"] for a in item["artists"]),
            "cover": smallest_image(item.get("album", {}).get("images")),
            "context": spotify_context(play.get("context"), item, bearer),
            "device": "",
            "device_type": "",
            "user": user,
            "platform": "Spotify",
            "when": play.get("played_at", ""),
        }
    return None


def lastfm_now(p):
    key = os.environ.get("LASTFM_API_KEY")
    listening = p.get("listening", {})
    user = listening.get("lastfm_user")
    if not (key and user):
        return None
    query = urllib.parse.urlencode(
        {"method": "user.getrecenttracks", "user": user, "api_key": key, "format": "json", "limit": 1}
    )
    tracks = fetch(f"https://ws.audioscrobbler.com/2.0/?{query}")["recenttracks"]["track"]
    if isinstance(tracks, dict):
        tracks = [tracks]
    if not tracks:
        return None
    track = tracks[0]
    images = {i.get("size"): i.get("#text") for i in track.get("image", [])}
    playing = track.get("@attr", {}).get("nowplaying") == "true"
    when = ""
    if not playing and track.get("date", {}).get("uts"):
        when = datetime.fromtimestamp(int(track["date"]["uts"]), timezone.utc).isoformat(timespec="minutes")
    return {
        "playing": playing,
        "title": track.get("name", ""),
        "artist": track.get("artist", {}).get("#text", ""),
        "cover": images.get("medium") or images.get("large") or "",
        "context": track.get("album", {}).get("#text", ""),
        "device": "",
        "device_type": "",
        "user": user,
        "platform": listening.get("lastfm_platform") or "Last.fm",
        "when": when,
    }


def now_data(p, cache, token):
    spotify = lastfm = None
    if token:
        try:
            spotify = spotify_now(token)
        except Exception as error:
            print(f"spotify: no playback state ({error})", file=sys.stderr)
    try:
        lastfm = lastfm_now(p)
    except Exception as error:
        print(f"last.fm: no recent tracks ({error})", file=sys.stderr)
    if spotify and lastfm and (lastfm["title"], lastfm["artist"]) == (spotify["title"], spotify["artist"]):
        lastfm = None  # Spotify scrobbles to Last.fm too; that's the same play
    candidates = [c for c in (spotify, lastfm) if c]
    if not candidates:
        return cache.get("now")
    playing = [c for c in candidates if c["playing"]]
    if playing:
        return playing[0]
    return max(candidates, key=lambda c: c.get("when") or "")


def now_key(now):
    if not now:
        return "off"
    return "|".join(str(now.get(k, "")) for k in ("playing", "paused", "title", "artist", "context", "device", "platform"))


# ── assembly ─────────────────────────────────────────────────────────────────


def picture(base, name, alt, width="100%", href=None):
    size = f' width="{width}"' if width else ""
    tag = (
        f'<picture><source media="(prefers-color-scheme: dark)" srcset="{base}dark/{name}.svg">'
        f'<img src="{base}light/{name}.svg"{size} alt="{esc(alt)}"></picture>'
    )
    return f'<a href="{esc(href)}">{tag}</a>' if href else tag


def fill_placeholders(p, cache):
    user = cache.get("github", {}).get("user", {})
    joined = user.get("created_at", "")
    since = joined[:4] if joined else ""
    years = ""
    if joined:
        start = datetime.fromisoformat(joined.replace("Z", "+00:00"))
        years = str(int((datetime.now(timezone.utc) - start).days // 365.25))
    values = {"{repos}": str(user.get("public_repos", "")), "{since}": since, "{years}": years}

    def fill(obj):
        if isinstance(obj, str):
            for key, value in values.items():
                obj = obj.replace(key, value)
            return obj
        if isinstance(obj, list):
            return [fill(x) for x in obj]
        if isinstance(obj, dict):
            return {k: fill(v) for k, v in obj.items()}
        return obj

    return fill(p)


def live(out):
    """Renders only the hero with what is playing right now, for the GitHub Pages site."""
    p = tomllib.loads((ROOT / "profile.toml").read_text(encoding="utf-8"))
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    p = fill_placeholders(p, cache)
    token = None
    try:
        token = spotify_token()
    except Exception as error:
        print(f"spotify: no token ({error})", file=sys.stderr)
    now = now_data(p, {}, token) or cache.get("now")
    key = now_key(now)
    out = Path(out)
    previous = None
    base = os.environ.get("PAGES_URL", cache.get("pages_url", ""))
    if base:
        try:
            previous = fetch(base.rstrip("/") + "/now.json").get("key")
        except Exception as error:
            print(f"live: no previous state ({error})", file=sys.stderr)
    changed = previous != key or "--force" in sys.argv
    for theme in THEMES:
        (out / theme).mkdir(parents=True, exist_ok=True)
        (out / theme / "hero.svg").write_text(hero(theme, p, now).render(), encoding="utf-8")
    (out / "now.json").write_text(json.dumps({"key": key, "now": now}, ensure_ascii=False, indent=2), encoding="utf-8")
    profile = f'https://github.com/{p["me"]["github"]}'
    (out / "index.html").write_text(f'<!doctype html><meta http-equiv="refresh" content="0; url={profile}">', encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as handle:
            handle.write(f"changed={'true' if changed else 'false'}\n")
    print(f"live: {key} ({'changed' if changed else 'unchanged'})")


def main():
    global OFFLINE
    if "--live" in sys.argv:
        live(sys.argv[sys.argv.index("--live") + 1])
        return
    OFFLINE = "--offline" in sys.argv
    p = tomllib.loads((ROOT / "profile.toml").read_text(encoding="utf-8"))
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    if not OFFLINE:
        github_data(p, cache)
        stats_data(p, cache)
        token = None
        try:
            token = spotify_token()
        except Exception as error:
            print(f"spotify: no token ({error})", file=sys.stderr)
        if token:
            spotify_top(p, cache, token)
        now = now_data(p, cache, token)
        if now:
            cache["now"] = {**now, "playing": False, "paused": False}
        if os.environ.get("LIVE") in ("true", "false"):
            cache["live"] = os.environ["LIVE"] == "true"
    p = fill_placeholders(p, cache)
    gh = cache.get("github", {})

    projects = []
    for i, entry in enumerate(p["work"]["projects"]):
        repo = gh.get("repos", {}).get(entry["repo"])
        if repo is None:
            continue
        projects.append(
            {
                "name": entry["repo"],
                "note": entry.get("note") or repo["description"],
                "language": repo["language"],
                "stars": repo["stars"],
                "url": repo["url"],
                "hue": entry.get("hue") or HUE_ORDER[i % len(HUE_ORDER)],
                "icon": entry.get("icon") or "code",
            }
        )
    featured = {pr["name"].lower() for pr in projects} | {p["me"]["github"].lower()}
    bsides = p.get("bsides", {})
    recent = [r for r in cache.get("recent", []) if r["name"].lower() not in featured][: int(bsides.get("count", 4))]
    stats = cache.get("stats")
    tracks = cache.get("spotify") or []
    year = datetime.now(timezone.utc).year

    files = {}
    rows = []  # each row is a list of (name, href, width)

    def add(name, build, href=None, width="100%", row=None):
        files[name] = build
        if row is None:
            rows.append([(name, href, width)])
        else:
            row.append((name, href, width))

    add("hero", lambda th: hero(th, p, cache.get("now")))
    links = p.get("links", [])
    if links:
        row = []
        rows.append(row)
        for i, link in enumerate(links):
            add(f"link-{i + 1}", lambda th, i=i, link=link: link_button(th, link, i), link["url"], "", row)
    add("side-a", lambda th: section(th, "Side A", p["work"]["title"], f"{len(projects):02d} tracks", f'Side A: {p["work"]["title"]}'))
    grid = projects[1:]
    for i, project in enumerate(projects):
        wide = i == 0 or (i == len(projects) - 1 and len(grid) % 2 == 1)
        if wide:
            add(f"a{i + 1}", lambda th, i=i, pr=project: project_card(th, pr, i, True), project["url"])
            continue
        if (i - 1) % 2 == 0:
            row = []
            rows.append(row)
        add(f"a{i + 1}", lambda th, i=i, pr=project: project_card(th, pr, i, False), project["url"], "49%", row)
    if recent:
        bs_title = bsides.get("title", "Fresh from the studio")
        add("b-sides", lambda th: section(th, "B-sides", bs_title, "auto · latest pushes", f"B-sides: {bs_title}"))
        for i, repo in enumerate(recent):
            add(f"b{i + 1}", lambda th, i=i, repo=repo: recent_row(th, repo, i + 1), repo["url"])
    items = p.get("highlights", {}).get("items", [])
    if items:
        title = p["highlights"]["title"]
        add("side-b", lambda th: section(th, "Side B", title, f"{len(items):02d} tracks", f"Side B: {title}"))
        add("highlights", lambda th: highlights(th, items))
    if stats:
        add("stats-head", lambda th: section(th, "Charts", "Activity & popularity", "updated daily", "Charts: activity and popularity"))
        add("activity", lambda th: activity(th, stats))
        add("popularity", lambda th: popularity(th, stats))
    if tracks:
        listening = p.get("listening", {})
        add("rotation", lambda th: rotation(th, listening.get("title", "On rotation"), tracks), listening.get("profile") or None)
    if p.get("credits", {}).get("items"):
        add("credits", lambda th: credits(th, p["credits"]["title"], p["credits"]["items"]))
    add("colophon", lambda th: colophon(th, "Set in Bricolage Grotesque & Geist Mono", f"© {year} {p['me']['name']}"))

    written = set()
    for theme in THEMES:
        folder = ROOT / "img" / theme
        folder.mkdir(parents=True, exist_ok=True)
        for name, build in files.items():
            path = folder / f"{name}.svg"
            out = build(theme).render()
            if not path.exists() or path.read_text(encoding="utf-8") != out:
                path.write_text(out, encoding="utf-8")
            written.add(path)
        for stale in folder.glob("*.svg"):
            if stale not in written:
                stale.unlink()

    alts = {name: files[name]("dark").label for name in files}
    live_base = cache.get("pages_url") if cache.get("live") else None
    lines = [
        "<!-- Generated by .github/profile/build.py from profile.toml. Edit that file, not this one. -->",
        '<div align="center">',
    ]
    for row in rows:
        parts = []
        for name, href, width in row:
            base = live_base if (name == "hero" and live_base) else "img/"
            parts.append(picture(base, name, alts[name], width, href))
        lines.append(("&nbsp;" if row and row[0][0].startswith("link-") else "").join(parts))
    lines.append("</div>")
    (ROOT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"built {len(files)} images × {len(THEMES)} themes, {len(projects)} projects, {len(recent)} b-sides, "
        f"{'stats' if stats else 'no stats'}, {len(tracks)} tracks, now: {now_key(cache.get('now'))}"
    )


if __name__ == "__main__":
    main()
