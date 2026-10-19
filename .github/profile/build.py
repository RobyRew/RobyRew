#!/usr/bin/env python3
"""Renders README.md and every SVG in img/ from profile.toml.

    pip install fonttools brotli
    python3 .github/profile/build.py            # fetches GitHub + Spotify data when it can
    python3 .github/profile/build.py --offline  # uses the last values saved in cache.json

Each SVG embeds a subset of the fonts it uses, so the type renders the same
everywhere GitHub shows the image. Light and dark variants are written to
img/light and img/dark and picked by <picture> in the README.
"""

import base64
import html
import json
import math
import os
import sys
import tomllib
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CACHE = HERE / "cache.json"
W = 840
HALF = 412
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
}
STAR = "M12 2.8l2.8 5.8 6.4.9-4.6 4.5 1.1 6.3L12 17.3l-5.7 3 1.1-6.3-4.6-4.5 6.4-.9Z"


def esc(s):
    return html.escape(str(s), quote=True)


def num(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def paint(color, attr="fill"):
    if isinstance(color, tuple):
        return f'{attr}="{color[0]}" {attr}-opacity="{num(color[1])}"'
    return f'{attr}="{color}"'


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
        return text.rstrip(" ,.;:—-") + "…"

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

    def glass(self, x, y, w, h, r):
        self.add(
            f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" rx="{num(r)}" '
            f'{paint(self.t["glass"])} {paint(self.t["edge"], "stroke")} stroke-width="1"/>'
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


# ── pieces ───────────────────────────────────────────────────────────────────


def record(svg, cx, cy, r, words):
    label_r, hole_r = 0.38 * r, 4
    disc, label, shadow = svg.uid("disc"), svg.uid("label"), svg.uid("shadow")
    svg.defs.append(
        f'<radialGradient id="{disc}"><stop offset="0" stop-color="#2A2A2E"/><stop offset=".5" stop-color="#121214"/>'
        f'<stop offset="1" stop-color="#050506"/></radialGradient>'
        f'<radialGradient id="{label}" cx=".35" cy=".3"><stop offset="0" stop-color="#FFB37A"/>'
        f'<stop offset=".6" stop-color="#FF6A2B"/><stop offset="1" stop-color="#D9381E"/></radialGradient>'
        f'<filter id="{shadow}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter>'
    )
    svg.css.append(
        f".spin{{transform-origin:{num(cx)}px {num(cy)}px;animation:spin 14s linear infinite}}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
    )
    parts = [
        f'<circle cx="{num(cx + 6)}" cy="{num(cy + 16)}" r="{num(r)}" fill="#000" opacity=".55" filter="url(#{shadow})"/>',
        '<g class="spin">',
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
    ring = label_r - 13
    size = 6.6
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
        f'<text x="{num(cx)}" y="{num(cy - 11)}" text-anchor="middle" class="f-display" font-size="14" '
        f'letter-spacing="-.4" fill="#2A0E04" fill-opacity=".86">RobyRew</text>'
    )
    svg.use("mono-md", "SIDE A")
    parts.append(
        f'<text x="{num(cx)}" y="{num(cy + 19)}" text-anchor="middle" class="f-mono-md" font-size="7" '
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


def tonearm(svg, px, py, points):
    metal = svg.uid("metal")
    svg.defs.append(
        f'<linearGradient id="{metal}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F4F4F6"/>'
        f'<stop offset=".5" stop-color="#A9A9B2"/><stop offset="1" stop-color="#6B6B74"/></linearGradient>'
    )
    path = "M" + " L".join(f"{num(x)} {num(y)}" for x, y in [(px, py)] + points)
    hx, hy = points[-1]
    ax, ay = points[-2]
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
        f'<circle cx="{num(px)}" cy="{num(py)}" r="20" fill="url(#{metal})"/>'
        f'<circle cx="{num(px)}" cy="{num(py)}" r="20" fill="none" stroke="#000" stroke-opacity=".25"/>'
        f'<circle cx="{num(px)}" cy="{num(py)}" r="8" fill="#2B2B30"/>'
    )


def hero(theme, p):
    me = p["me"]
    label = f'{me["name"]}. {me["statement"]} {me["aside"]}'
    H = 448
    svg = SVG(theme, W, H + GAP, label)
    t = svg.t
    svg.css.append(
        ".drift{animation:drift 18s ease-in-out infinite alternate}"
        "@keyframes drift{to{transform:translate(-36px,22px)}}"
        ".pulse{animation:pulse 1.6s ease-in-out infinite alternate}@keyframes pulse{to{opacity:.3}}"
    )
    svg.card(
        0, 0, W, H, 30, "ember",
        [(0.9, 1.0, 0.62, 0, 1), (0.08, 1.12, 0.5, 1, 0.9), (0.98, -0.08, 0.42, 2, 0.85), (0.45, -0.2, 0.36, 1, 0.5)],
        drift=True,
    )
    veil = svg.uid("veil")
    svg.defs.append(
        f'<linearGradient id="{veil}"><stop offset="0" stop-color="{t["base"]}" stop-opacity="{t["veil"]}"/>'
        f'<stop offset=".62" stop-color="{t["base"]}" stop-opacity="0"/></linearGradient>'
    )
    svg.add(f'<rect width="{W}" height="{H}" rx="30" fill="url(#{veil})"/>')

    facts = me.get("facts", [])
    if facts:
        pill = f'{facts[0]["label"]} · {facts[0]["value"]}'.upper()
        width = FACES["mono-md"].width(pill, 11, 1.4) + 44
        svg.glass(36, 36, width, 32, 16)
        svg.add('<circle class="pulse" cx="54" cy="52" r="4.5" fill="#30D158"/>')
        svg.add('<circle cx="54" cy="52" r="8" fill="#30D158" fill-opacity=".22"/>')
        svg.text(68, 56, pill, "mono-md", 11, t["ink"], tracking=1.4)

    cx, cy, r = 650, 226, 160
    size = 112
    while size > 60 and FACES["display"].width(me["name"], size, -size * 0.04) > cx - r - 32 - 40:
        size -= 2
    svg.text(32, 186, me["name"], "display", size, t["ink"], tracking=-size * 0.04)
    y = 232
    for line in FACES["text"].wrap(me["statement"], 21, 430):
        svg.text(36, y, line, "text", 21, t["dim"])
        y += 29
    y += 4
    for line in FACES["semi"].wrap(me["aside"], 21, 430):
        svg.text(36, y, line, "semi", 21, t["aside"])
        y += 29

    x = 36
    for fact in facts[1:]:
        x += svg.chip(x, 372, fact["value"], h=34, size=14, icon=fact.get("icon", "spark")) + 10

    record(svg, cx, cy, r, me["record"])
    tonearm(svg, cx + 158, 70, [(cx + 166, 252), (cx + 112, 300)])
    return svg


def section(theme, kicker, title, right, label):
    svg = SVG(theme, W, 104, label)
    t = svg.t
    svg.text(4, 58, kicker.upper(), "mono-md", 11, t["accent"], tracking=2.2)
    svg.text(2, 92, title, "display", 32, t["head"], tracking=-0.8)
    svg.text(W - 4, 92, right.upper(), "mono", 11, t["muted"], tracking=1.6, anchor="end")
    return svg


def blobs_for(index):
    layouts = (
        [(0.95, 1.05, 0.7, 0, 1), (0.05, 1.2, 0.55, 1, 0.75), (0.9, -0.15, 0.4, 2, 0.7)],
        [(0.1, -0.1, 0.65, 0, 0.95), (1.0, 1.1, 0.6, 1, 0.8), (0.6, 1.3, 0.4, 2, 0.6)],
        [(1.05, 0.2, 0.7, 0, 1), (0.0, 1.1, 0.5, 2, 0.7), (0.4, -0.3, 0.45, 1, 0.6)],
    )
    return layouts[index % len(layouts)]


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
        svg.card(0, 0, W, H, 26, hue, blobs_for(index))
        svg.glass(32, 32, 58, 58, 17)
        svg.icon(project["icon"], 46, 46, 30, t["ink"])
        illustrated = project["icon"] == "presentation"
        text_w = 410 if illustrated else W - 64
        svg.text(30, 138, FACES["display"].fit(project["name"], 38, text_w, -1), "display", 38, t["ink"], tracking=-1)
        y = 167
        for line in FACES["text"].wrap(note, 16.5, text_w, 2):
            svg.text(32, y, line, "text", 16.5, t["dim"])
            y += 23
        meta_chips(svg, 32, H - 32 - 28, project)
        if illustrated:
            window_mock(svg, 488, 40, 268, 190, hue)
        svg.glass(W - 32 - 34, 32, 34, 34, 17)
        svg.icon("arrow", W - 32 - 26, 40, 18, t["ink"])
        return svg
    H = 228
    svg = SVG(theme, HALF, H + GAP, label)
    svg.card(0, 0, HALF, H, 24, hue, blobs_for(index))
    svg.glass(24, 24, 48, 48, 14)
    svg.icon(project["icon"], 36, 36, 24, t["ink"])
    svg.glass(HALF - 24 - 30, 24, 30, 30, 15)
    svg.icon("arrow", HALF - 24 - 23, 31, 16, t["ink"])
    svg.text(22, 110, FACES["display"].fit(project["name"], 24, HALF - 48, -0.6), "display", 24, t["ink"], tracking=-0.6)
    y = 135
    for line in FACES["text"].wrap(note, 14.5, HALF - 48, 2):
        svg.text(24, y, line, "text", 14.5, t["dim"])
        y += 20
    meta_chips(svg, 24, H - 24 - 26, project, h=26, size=13)
    return svg


def highlights(theme, items):
    label = " ".join(f'{i["value"]} {i["title"]}: {i["note"]}' for i in items)
    H = 180
    svg = SVG(theme, W, H + GAP, label)
    t = svg.t
    n = max(len(items), 1)
    gap = 16
    tile = (W - gap * (n - 1)) / n
    for i, item in enumerate(items):
        x = i * (tile + gap)
        svg.card(x, 0, tile, H, 22, item.get("hue", HUE_ORDER[i % len(HUE_ORDER)]), blobs_for(i + 1))
        tag = f"B{i + 1}"
        tag_w = FACES["mono-md"].width(tag, 10, 1) + 18
        svg.glass(x + tile - 20 - tag_w, 20, tag_w, 22, 11)
        svg.text(x + tile - 20 - tag_w / 2, 35, tag, "mono-md", 10, t["ink"], tracking=1, anchor="middle")
        value = FACES["display"].fit(item["value"], 46, tile - 100, -1.5)
        svg.text(x + 20, 72, value, "display", 46, t["ink"], tracking=-1.5)
        svg.text(x + 22, 106, FACES["semi"].fit(item["title"], 16.5, tile - 44), "semi", 16.5, t["ink"])
        y = 130
        for line in FACES["text"].wrap(item["note"], 13.5, tile - 44, 2):
            svg.text(x + 22, y, line, "text", 13.5, t["dim"])
            y += 19
    return svg


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
        print(f"cover: skipped ({error})", file=sys.stderr)
        return None


def rotation(theme, title, tracks):
    label = "On rotation: " + "; ".join(f'{x["name"]} by {x["artist"]}' for x in tracks)
    H = 128 + 60 * len(tracks)
    svg = SVG(theme, W, H + GAP, label)
    t = svg.t
    svg.card(0, 0, W, H, 26, "green", [(1.0, -0.1, 0.6, 0, 0.9), (0.0, 1.1, 0.5, 1, 0.7), (0.7, 1.2, 0.35, 2, 0.5)])
    svg.text(32, 46, "ON ROTATION", "mono-md", 11, t["ink"], tracking=2.2)
    x = 32 + FACES["mono-md"].width("ON ROTATION", 11, 2.2) + 10
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
    svg.text(30, 86, title, "display", 30, t["ink"], tracking=-0.8)
    svg.text(W - 32, 46, "VIA SPOTIFY", "mono", 10.5, t["faint"], tracking=1.6, anchor="end")
    for n, item in enumerate(tracks):
        y = 112 + n * 60
        if n:
            svg.add(f'<line x1="32" y1="{y - 8}" x2="{W - 32}" y2="{y - 8}" {paint(t["edge"], "stroke")}/>')
        clip = svg.uid("cover")
        svg.defs.append(f'<clipPath id="{clip}"><rect x="32" y="{y}" width="44" height="44" rx="9"/></clipPath>')
        cover = image_data(item.get("cover"))
        if cover:
            svg.add(f'<image href="{cover}" x="32" y="{y}" width="44" height="44" clip-path="url(#{clip})" preserveAspectRatio="xMidYMid slice"/>')
        else:
            colors = HUES[HUE_ORDER[n % len(HUE_ORDER)]]
            grad = svg.uid("art")
            svg.defs.append(
                f'<linearGradient id="{grad}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{colors[0]}"/>'
                f'<stop offset="1" stop-color="{colors[1]}"/></linearGradient>'
            )
            svg.add(f'<rect x="32" y="{y}" width="44" height="44" rx="9" fill="url(#{grad})"/>')
            svg.text(54, y + 29, item["name"][:1].upper(), "display", 18, "#FFFFFF", anchor="middle")
        minutes, seconds = divmod(round(item["ms"] / 1000), 60)
        duration = f"{minutes}:{seconds:02d}"
        svg.text(W - 32, y + 27, duration, "mono", 12, t["faint"], tracking=0.5, anchor="end")
        room = W - 92 - 32 - 60
        svg.text(92, y + 19, FACES["semi"].fit(item["name"], 16.5, room), "semi", 16.5, t["ink"])
        svg.text(92, y + 39, FACES["text"].fit(item["artist"], 14, room), "text", 14, t["dim"])
    return svg


def credits(theme, title, items):
    label = "Credits. " + "; ".join(f'{i["label"]}: {i["value"]}' for i in items)
    rows = math.ceil(len(items) / 2)
    H = 116 + 74 * rows
    svg = SVG(theme, W, H + GAP, label)
    t = svg.t
    svg.card(0, 0, W, H, 26, "graphite", [(0.0, 0.0, 0.55, 0, 0.7), (1.0, 1.0, 0.55, 2, 0.6)])
    svg.text(32, 46, "CREDITS", "mono-md", 11, t["ink"], tracking=2.2)
    svg.text(30, 86, title, "display", 30, t["ink"], tracking=-0.8)
    col = (W - 64) / 2
    for n, item in enumerate(items):
        x = 32 + (n % 2) * (col + 16)
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
    svg.text(4, 36, left.upper(), "mono", 10, t["muted"], tracking=1.6)
    svg.text(W - 4, 36, right.upper(), "mono", 10, t["muted"], tracking=1.6, anchor="end")
    return svg


# ── data ─────────────────────────────────────────────────────────────────────


OFFLINE = False


def fetch_json(url, headers=None, data=None):
    request = urllib.request.Request(url, data=data, headers={"User-Agent": "robyrew-profile", **(headers or {})})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def github_data(p, cache):
    data = cache.setdefault("github", {"user": {}, "repos": {}})
    headers = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f'Bearer {os.environ["GITHUB_TOKEN"]}'
    login = p["me"]["github"]
    try:
        user = fetch_json(f"https://api.github.com/users/{login}", headers)
        data["user"] = {"public_repos": user["public_repos"], "created_at": user["created_at"]}
    except Exception as error:
        print(f"github: keeping cached user ({error})", file=sys.stderr)
    for project in p["work"]["projects"]:
        name = project["repo"]
        try:
            repo = fetch_json(f"https://api.github.com/repos/{login}/{name}", headers)
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


def spotify_data(p, cache):
    keys = ("SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "SPOTIFY_REFRESH_TOKEN")
    client_id, secret, refresh = (os.environ.get(k) for k in keys)
    if not (client_id and secret and refresh):
        return
    limit = int(p.get("listening", {}).get("tracks", 5))
    try:
        auth = base64.b64encode(f"{client_id}:{secret}".encode()).decode()
        token = fetch_json(
            "https://accounts.spotify.com/api/token",
            {"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"},
            urllib.parse.urlencode({"grant_type": "refresh_token", "refresh_token": refresh}).encode(),
        )["access_token"]
        bearer = {"Authorization": f"Bearer {token}"}
        items = fetch_json(
            f"https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit={limit}", bearer
        )["items"]
        if not items:
            recent = fetch_json("https://api.spotify.com/v1/me/player/recently-played?limit=50", bearer)["items"]
            seen = {}
            for play in recent:
                seen.setdefault(play["track"]["id"], play["track"])
            items = list(seen.values())[:limit]
    except Exception as error:
        print(f"spotify: keeping cached tracks ({error})", file=sys.stderr)
        return
    if items:
        cache["spotify"] = [
            {
                "name": item["name"],
                "artist": ", ".join(a["name"] for a in item["artists"]),
                "ms": item["duration_ms"],
                "cover": min(item["album"]["images"], key=lambda i: i.get("width") or 0)["url"]
                if item.get("album", {}).get("images")
                else "",
            }
            for item in items
        ]


# ── assembly ─────────────────────────────────────────────────────────────────


def main():
    global OFFLINE
    OFFLINE = "--offline" in sys.argv
    p = tomllib.loads((ROOT / "profile.toml").read_text(encoding="utf-8"))
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    if not OFFLINE:
        github_data(p, cache)
        spotify_data(p, cache)

    gh = cache.get("github", {})
    user = gh.get("user", {})
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

    p = fill(p)

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
    tracks = cache.get("spotify") or []
    year = datetime.now(timezone.utc).year

    files = {}
    blocks = []  # (name, href, layout) where layout is "full", "left" or "right"

    def add(name, build, href=None, layout="full"):
        files[name] = build
        blocks.append((name, href, layout))

    add("hero", lambda th: hero(th, p))
    count = f"{len(projects):02d} tracks"
    add("side-a", lambda th: section(th, "Side A", p["work"]["title"], count, f'Side A: {p["work"]["title"]}'))
    rest = projects[1:]
    for i, project in enumerate(projects):
        wide = i == 0 or (i == len(projects) - 1 and len(rest) % 2 == 1)
        layout = "full" if wide else ("left" if (i - 1) % 2 == 0 else "right")
        add(f"a{i + 1}", lambda th, i=i, pr=project, wide=wide: project_card(th, pr, i, wide), project["url"], layout)
    items = p.get("highlights", {}).get("items", [])
    if items:
        title = p["highlights"]["title"]
        add("side-b", lambda th: section(th, "Side B", title, f"{len(items):02d} tracks", f"Side B: {title}"))
        add("highlights", lambda th: highlights(th, items))
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
    lines = [
        "<!-- Generated by .github/profile/build.py from profile.toml. Edit that file, not this one. -->",
        "<div>",
    ]
    for name, href, layout in blocks:
        width = "100%" if layout == "full" else "49%"
        align = "" if layout == "full" else f' align="{layout}"'
        picture = (
            f'<picture><source media="(prefers-color-scheme: dark)" srcset="img/dark/{name}.svg">'
            f'<img src="img/light/{name}.svg" width="{width}"{align} alt="{esc(alts[name])}"></picture>'
        )
        if name == "colophon":
            links = " &nbsp;·&nbsp; ".join(f'<a href="{esc(l["url"])}">{esc(l["label"])}</a>' for l in p.get("links", []))
            lines.append(f"<p>{links}</p>")
        lines.append(f'<a href="{esc(href)}">{picture}</a>' if href else picture)
    lines.append("</div>")
    (ROOT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"built {len(files)} images × {len(THEMES)} themes, {len(projects)} projects, {len(tracks)} tracks")


if __name__ == "__main__":
    main()
