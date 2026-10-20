"""Drawing basics for the profile cards: fonts, the SVG canvas, colours, icons and shared shapes."""

import base64
import hashlib
import html
import math
import sys
import urllib.parse
import urllib.request
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
    "mono": ("GeistMono-Medium.ttf", MONO, 500),
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

# Cards are frosted glass over the page: a see-through fill, a faint tint, a sheen at the top and a light rim.
THEMES = {
    "dark": {
        "page": "#0D1117",
        "card": ("#FFFFFF", 0.035),
        "ink": "#F0F3F6",
        "dim": ("#FFFFFF", 0.68),
        "faint": ("#FFFFFF", 0.46),
        "glass": ("#FFFFFF", 0.06),
        "edge": ("#FFFFFF", 0.09),
        "rim": ("#FFFFFF", 0.24, 0.05),  # colour, opacity at the top, opacity at the bottom
        "sheen": ("#FFFFFF", 0.06),
        "blob": 0.3,
        "shadow": 0,
        "head": "#F0F6FC",
        "muted": "#8B949E",
        "accent": "#F2A27E",
        "aside": "#F5B795",
        "window": "#161B22",
        "heat": ("#FFFFFF", 0.06),
        "panel": ("#FFFFFF", 0.045),
    },
    "light": {
        "page": "#FFFFFF",
        "card": ("#F2F4F7", 0.78),
        "ink": "#1F2328",
        "dim": ("#000000", 0.62),
        "faint": ("#000000", 0.45),
        "glass": ("#FFFFFF", 0.72),
        "edge": ("#000000", 0.07),
        "rim": ("#000000", 0.09, 0.11),
        "sheen": ("#FFFFFF", 0.7),
        "blob": 0.2,
        "shadow": 0.06,
        "head": "#1F2328",
        "muted": "#656D76",
        "accent": "#C4511F",
        "aside": "#B4461C",
        "window": "#FFFFFF",
        "heat": ("#000000", 0.05),
        "panel": ("#FFFFFF", 0.6),
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
    "download": '<path d="M12 3.5v11M7.5 10l4.5 4.5 4.5-4.5M4 19.5h16"/>',
    "tag": '<path d="M3 12V4h8l9.5 9.5-8 8Z"/><circle cx="7.5" cy="8" r="1.4"/>',
    "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
    "fork": '<circle cx="6" cy="5" r="2.2"/><circle cx="18" cy="5" r="2.2"/><circle cx="12" cy="19" r="2.2"/><path d="M6 7.2v1.3a3 3 0 0 0 3 3h6a3 3 0 0 0 3-3V7.2M12 11.5v5.3"/>',
    "merge": '<circle cx="6" cy="5" r="2.2"/><circle cx="6" cy="19" r="2.2"/><circle cx="18" cy="12" r="2.2"/><path d="M6 7.2v9.6M6 7.5c0 3 2.5 4.5 5.5 4.5h4.3"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.9-3.4 3.4-5.2 6.5-5.2s5.6 1.8 6.5 5.2"/><path d="M15.5 4.8a3.5 3.5 0 0 1 0 6.4M18 15c1.8.7 3 2.4 3.5 5"/>',
    "repo": '<path d="M5 4.5A2.5 2.5 0 0 1 7.5 2H19v16H7.5A2.5 2.5 0 0 0 5 20.5v-16ZM5 20.5A2.5 2.5 0 0 0 7.5 23H19v-5"/>',
    "chart": '<path d="M3 20.5h18M6.5 16.5v-5M11 16.5V6M15.5 16.5v-8M20 16.5v-3"/>',
    "chevron": '<path d="m6 9.5 6 6 6-6"/>',
    "play": '<path d="M8 4.8v14.4c0 .8.9 1.3 1.6.9l11.2-7.2c.6-.4.6-1.3 0-1.7L9.6 3.9C8.9 3.5 8 4 8 4.8Z"/>',
    "up": '<path d="M12 19.5v-15M6 10.5l6-6 6 6"/>',
    "mic": '<rect x="9" y="2.5" width="6" height="12" rx="3"/><path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v3.5"/>',
    "disc": '<circle cx="12" cy="12" r="9.5"/><circle cx="12" cy="12" r="2.5"/>',
    "flame": '<path d="M12 21.5c-4 0-7-2.8-7-6.6 0-3.4 2.4-5.4 4-7.9.4 2 1.6 3.2 2.8 3.6C11.6 7 13 4.4 15.5 2.5c-.3 3 3.5 5.7 3.5 11 0 4.6-3 8-7 8Z"/>',
    "calendar": '<rect x="3" y="4.5" width="18" height="16.5" rx="2.5"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/>',
    "commit": '<circle cx="12" cy="12" r="3.5"/><path d="M2 12h6.5M15.5 12H22"/>',
    "issue": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="1.6"/>',
    "clock": '<circle cx="12" cy="12" r="9.5"/><path d="M12 6.5V12l3.5 2"/>',
    "heart": '<path d="M12 20.5s-8.5-5-8.5-11A4.8 4.8 0 0 1 12 6.4a4.8 4.8 0 0 1 8.5 3.1c0 6-8.5 11-8.5 11Z"/>',
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
    # Just what the labels need: kerning, no names or ligature tables. Keeps every image small.
    options.layout_features = [] if key == "mono" else ["kern"]  # a monospace font has nothing to kern
    options.name_IDs = []
    options.name_legacy = False
    options.glyph_names = False
    options.notdef_outline = False
    options.drop_tables += ["GSUB", "GDEF", "STAT", "meta"] + (["GPOS"] if key == "mono" else [])
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
    def __init__(self, theme, width, height, label, ids=""):
        self.theme = theme
        self.t = THEMES[theme]
        self.width, self.height = width, height
        self.label = label
        self.parts, self.defs, self.css, self.chars = [], [], [], {}
        self.ids, self.id_prefix = 0, ids

    def uid(self, prefix):
        self.ids += 1
        return f"{self.id_prefix}{prefix}{self.ids}"

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

    def render(self, view=None):
        """The whole canvas, or only the (x, y, w, h) part of it given as `view`."""
        x, y, w, h = view or (0, 0, self.width, self.height)
        fonts = "".join(font_face(k, "".join(sorted(v))) for k, v in sorted(self.chars.items()))
        css = (
            fonts
            + "text{font-kerning:normal;text-rendering:geometricPrecision}"
            + "".join(self.css)
            + "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{num(w)}" height="{num(h)}" '
            f'viewBox="{num(x)} {num(y)} {num(w)} {num(h)}" role="img" aria-label="{esc(self.label)}">'
            f"<title>{esc(self.label)}</title><style>{css}</style><defs>{''.join(self.defs)}</defs>"
            + "".join(self.parts)
            + "</svg>\n"
        )


def render_pair(light, dark, view):
    """Both themes in one image, switched by the page's colour scheme. Used for phones, where GitHub's own theme
    switching can't be combined with a width condition."""
    x, y, w, h = view
    chars = {}
    for svg in (light, dark):
        for key, used in svg.chars.items():
            chars.setdefault(key, set()).update(used)
    fonts = "".join(font_face(k, "".join(sorted(v))) for k, v in sorted(chars.items()))
    extra = "".join(dict.fromkeys(light.css + dark.css))
    css = (
        fonts
        + "text{font-kerning:normal;text-rendering:geometricPrecision}"
        + extra
        + ".k{display:none}@media (prefers-color-scheme:dark){.l{display:none}.k{display:inline}}"
        + "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{num(w)}" height="{num(h)}" '
        f'viewBox="{num(x)} {num(y)} {num(w)} {num(h)}" role="img" aria-label="{esc(light.label)}">'
        f"<title>{esc(light.label)}</title><style>{css}</style><defs>{''.join(light.defs)}{''.join(dark.defs)}</defs>"
        f'<g class="l">{"".join(light.parts)}</g><g class="k">{"".join(dark.parts)}</g>'
        "</svg>\n"
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


# ── shared shapes ─────────────────────────────────────────────────────────────


def record(svg, cx, cy, r, words, spinning):
    label_r, hole_r = 0.38 * r, 4
    disc, label, shadow = svg.uid("disc"), svg.uid("label"), svg.uid("shadow")
    svg.defs.append(
        f'<radialGradient id="{disc}"><stop offset="0" stop-color="#2A2A2E"/><stop offset=".5" stop-color="#121214"/>'
        f'<stop offset="1" stop-color="#050506"/></radialGradient>'
        f'<radialGradient id="{label}" cx=".35" cy=".3"><stop offset="0" stop-color="#FFB37A"/>'
        f'<stop offset=".6" stop-color="#F0703A"/><stop offset="1" stop-color="#C9442A"/></radialGradient>'
        # A soft ring of shadow: a gradient rather than a blur, which would be redrawn on every frame of the spin.
        f'<radialGradient id="{shadow}"><stop offset=".84" stop-color="#000" stop-opacity=".42"/>'
        f'<stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>'
    )
    if spinning:
        # The disc's own box, so the spin stays centred however the image is cropped or scaled.
        svg.css.append(
            ".spin{transform-box:fill-box;transform-origin:center;animation:spin 2.4s linear infinite}"
            "@keyframes spin{to{transform:rotate(360deg)}}"
        )
    parts = [
        f'<circle cx="{num(cx + 4)}" cy="{num(cy + 12)}" r="{num(r * 1.16)}" fill="url(#{shadow})"/>',
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
    tracking = (2 * math.pi * ring - FACES["mono"].width(words, size)) / len(words)
    svg.use("mono", words)
    ring_id = svg.uid("ring")
    parts.append(
        f'<path id="{ring_id}" d="M{num(cx - ring)} {num(cy)}a{num(ring)} {num(ring)} 0 1 1 {num(2 * ring)} 0'
        f'a{num(ring)} {num(ring)} 0 1 1 {num(-2 * ring)} 0" fill="none"/>'
        f'<text class="f-mono" font-size="{size}" letter-spacing="{num(tracking)}" fill="#2A0E04" fill-opacity=".72">'
        f'<textPath href="#{ring_id}">{esc(words)}</textPath></text>'
    )
    svg.use("display", "RobyRew")
    parts.append(
        f'<text x="{num(cx)}" y="{num(cy - 10)}" text-anchor="middle" class="f-display" font-size="13" '
        f'letter-spacing="-.4" fill="#2A0E04" fill-opacity=".86">RobyRew</text>'
    )
    svg.use("mono", "SIDE A")
    parts.append(
        f'<text x="{num(cx)}" y="{num(cy + 18)}" text-anchor="middle" class="f-mono" font-size="6.5" '
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


def window_mock(svg, x, y, w, h, hue):
    t = svg.t
    colors = HUES.get(hue, HUES["ember"])
    slide = svg.uid("slide")
    svg.defs.append(
        f'<linearGradient id="{slide}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{colors[1]}" stop-opacity=".85"/>'
        f'<stop offset="1" stop-color="#140A0A"/></linearGradient>'
    )
    svg.add(
        f'<rect x="{num(x + 3)}" y="{num(y + 6)}" width="{num(w - 6)}" height="{num(h)}" rx="12" fill="#000" opacity=".18"/>'
        f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" rx="10" fill="{t["window"]}"/>'
        f'<rect x="{num(x + 0.5)}" y="{num(y + 0.5)}" width="{num(w - 1)}" height="{num(h - 1)}" rx="10" fill="none" '
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
    svg.text(sx + 27, sy + 18.6, "LIVE", "mono", 7.5, "#FFFFFF", tracking=1, anchor="middle")
    thumb_w = (sw - 3 * 8) / 4
    for i in range(4):
        tx = sx + i * (thumb_w + 8)
        svg.add(
            f'<rect x="{num(tx)}" y="{num(y + h - 38)}" width="{num(thumb_w)}" height="28" rx="5" '
            f'fill="{colors[i % 3]}" fill-opacity="{num(0.55 if i else 0.9)}"'
            + (f' stroke="{t["ink"]}" stroke-width="1.5"' if i == 0 else "")
            + "/>"
        )


def hexdump(svg, x, y, w, h, seed, size=10):
    digest = hashlib.sha256(seed.encode()).hexdigest() * 8
    step = size * 1.5
    rows = int(h // step)
    cols = int(w // (size * 2.2))
    for i in range(rows):
        chunk = digest[i * cols * 2:(i + 1) * cols * 2]
        line = " ".join(chunk[j:j + 2] for j in range(0, len(chunk), 2)).upper()
        svg.text(x, y + i * step, line, "mono", size, (svg.t["ink"], 0.05), tracking=0.4)


def heat_colors(theme):
    # Index 0 is the empty cell, drawn with the theme's "heat" colour instead.
    if theme == "dark":
        return (None, "#4A2A20", "#8C4128", "#D2693F", "#F5A57A")
    return (None, "#F9DCCB", "#F1B08C", "#E07F52", "#BF5A2E")
