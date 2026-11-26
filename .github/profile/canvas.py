"""Drawing basics for the profile cards: fonts, the SVG canvas, colours, icons and shared shapes."""

import base64
import hashlib
import html
import math
import random
import sys
import urllib.request
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CACHE = HERE / "cache.json"
ICON_DIR = HERE / "icons"  # each project's own app icon or favicon, named in profile.toml
W = 840  # every full-width image
PAD = 14  # cards sit this far in from the image edge
CW = W - 2 * PAD
HALF = 420  # half-width images, shown at 49% side by side
HP = 6
GAP = 14  # transparent space under every card

SANS = "Inter, -apple-system, 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, monospace"
FONTS = {
    # key: (file, fallback stack, weight). The same type as cosmincalin.es: Inter, and JetBrains Mono for labels.
    "display": ("InterDisplay-Bold.ttf", SANS, 700),
    "semi": ("Inter-SemiBold.ttf", SANS, 600),
    "text": ("Inter-Regular.ttf", SANS, 400),
    "mono": ("JetBrainsMono-Medium.ttf", MONO, 500),
}

# A card's tint: three colours laid across it as soft light. Each project takes the hue of its own icon.
HUES = {
    "blue": ("#3B82F6", "#6366F1", "#60A5FA"),
    "violet": ("#8B5CF6", "#6366F1", "#C084FC"),
    "sky": ("#38BDF8", "#6366F1", "#7DD3FC"),
    "teal": ("#14B8A6", "#0EA5E9", "#5EEAD4"),
    "green": ("#22C55E", "#14B8A6", "#86EFAC"),
    "ember": ("#FF6A2B", "#F43F5E", "#FDBA74"),
    "rose": ("#F43F5E", "#A855F7", "#FB7185"),
    "graphite": ("#64748B", "#334155", "#94A3B8"),
}
HUE_ORDER = ("blue", "violet", "teal", "rose", "green", "sky")

# The palette of the RobyRew sites (@robyrew/ui): neutral greys and one blue accent. Cards stay see-through so they
# sit on any of GitHub's themes: a faint fill, the card's tint, a sheen at the top and a light rim.
THEMES = {
    "dark": {
        "page": "#0D1117",
        "card": ("#FFFFFF", 0.035),
        "ink": "#EDEDED",
        "dim": ("#FFFFFF", 0.66),
        "faint": ("#FFFFFF", 0.5),  # small labels: 5.2:1 on a card; WCAG asks 4.5:1 for small text
        "glass": ("#FFFFFF", 0.06),
        "edge": ("#FFFFFF", 0.1),
        "rim": ("#FFFFFF", 0.2, 0.05),  # colour, opacity at the top, opacity at the bottom
        "sheen": ("#FFFFFF", 0.05),
        "blob": 0.22,
        "shadow": 0,
        "head": "#F0F6FC",
        "muted": "#8B949E",
        "accent": "#7AA2FF",
        "aside": "#9DB9FF",
        "live": "#30D158",
        "window": "#161B22",
        "panel": ("#FFFFFF", 0.045),
    },
    "light": {
        "page": "#FFFFFF",
        "card": ("#F2F2F4", 0.8),
        "ink": "#1D1D1F",
        "dim": ("#000000", 0.64),
        "faint": ("#000000", 0.56),  # small labels: 4.8:1 on a card (0.46 gave 3.4:1)
        "glass": ("#FFFFFF", 0.75),
        "edge": ("#000000", 0.08),
        "rim": ("#000000", 0.08, 0.11),
        "sheen": ("#FFFFFF", 0.7),
        "blob": 0.15,
        "shadow": 0.05,
        "head": "#1F2328",
        "muted": "#656D76",
        "accent": "#2563EB",
        "aside": "#1D4ED8",
        "live": "#1A9E3F",
        "window": "#FFFFFF",
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
    "door": '<path d="M5.5 21.5V4A1.5 1.5 0 0 1 7 2.5h10A1.5 1.5 0 0 1 18.5 4v17.5M3 21.5h18"/><circle cx="15" cy="12.5" r="1.2"/>',
    "terminal": '<rect x="2.5" y="4" width="19" height="16" rx="2.5"/><path d="m7 9.5 3 2.5-3 2.5M12.5 15H17"/>',
    "archive": '<rect x="2.5" y="3.5" width="19" height="5" rx="1.5"/><path d="M4.5 8.5v10a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-10M10 12.5h4"/>',
    "wand": '<path d="m3.5 20.5 11-11M13 5.5l1.5 1.5M17.5 3v3M19 4.5h-3M20.5 10.5v3M22 12h-3M8.5 3v3M10 4.5H7"/>',
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
    """A count for a label: 14936 is "14.9k", never rounded up to "15k"."""
    if n >= 100000:
        return f"{n // 1000}k"
    if n >= 1000:
        return f"{math.floor(n / 100) / 10:.1f}k".replace(".0k", "k")
    return str(n)


# ── type ─────────────────────────────────────────────────────────────────────


def kerning_lookups(font):
    """The font's pair kerning, as lookups of subtables: (kind, first glyphs, data). Read here and written into the
    text as offsets, so the embedded fonts can leave out their kerning table, the biggest part of a small subset."""
    if "GPOS" not in font:
        return []
    table = font["GPOS"].table
    wanted = sorted({i for record in table.FeatureList.FeatureRecord if record.FeatureTag == "kern"
                     for i in record.Feature.LookupListIndex})
    lookups = []
    for index in wanted:
        lookup = table.LookupList.Lookup[index]
        subtables = []
        for sub in lookup.SubTable:
            if lookup.LookupType == 9:
                if sub.ExtensionLookupType != 2:
                    continue
                sub = sub.ExtSubTable
            elif lookup.LookupType != 2:
                continue
            first = sub.Coverage.glyphs
            if sub.Format == 1:
                pairs = {glyph: {r.SecondGlyph: getattr(r.Value1, "XAdvance", 0) or 0 for r in pair_set.PairValueRecord}
                         for glyph, pair_set in zip(first, sub.PairSet)}
                subtables.append((1, set(first), pairs))
            else:
                values = [[getattr(r.Value1, "XAdvance", 0) or 0 for r in c1.Class2Record] for c1 in sub.Class1Record]
                subtables.append((2, set(first), (sub.ClassDef1.classDefs, sub.ClassDef2.classDefs, values)))
        lookups.append(subtables)
    return lookups


class Face:
    def __init__(self, key):
        file, self.stack, self.weight = FONTS[key]
        self.path = HERE / "fonts" / file
        font = TTFont(self.path, lazy=True)
        self.cmap = font.getBestCmap()
        self.advance = {g: a for g, (a, _) in font["hmtx"].metrics.items()}
        self.upm = font["head"].unitsPerEm
        self.lookups = kerning_lookups(font)

    @lru_cache(maxsize=None)
    def pair(self, left, right):
        """Kerning between two characters, in font units: what the first subtable that covers them says, per lookup."""
        a, b = self.cmap.get(ord(left)), self.cmap.get(ord(right))
        if a is None or b is None:
            return 0
        total = 0
        for subtables in self.lookups:
            for kind, first, data in subtables:
                if a not in first:
                    continue
                if kind == 1:
                    if b in data[a]:
                        total += data[a][b]
                        break
                    continue
                classes1, classes2, values = data
                row = values[classes1.get(a, 0)]
                second = classes2.get(b, 0)
                if second < len(row):
                    total += row[second]
                    break
        return total

    def kerns(self, text):
        """The kerning before each character, in font units."""
        return [0] + [self.pair(a, b) for a, b in zip(text, text[1:])]

    def width(self, text, size, tracking=0.0, kern=True):
        units = sum(
            self.advance[self.cmap[ord(c)]] if ord(c) in self.cmap else self.upm * 0.55
            for c in text
        ) + (sum(self.kerns(text)) if kern else 0)
        return units * size / self.upm + tracking * len(text)

    def fit(self, text, size, max_width, tracking=0.0, kern=True):
        if self.width(text, size, tracking, kern) <= max_width:
            return text
        while text and self.width(text + "…", size, tracking, kern) > max_width:
            text = text[:-1]
        return text.rstrip(" ,.;:—-·") + "…"

    def wrap(self, text, size, max_width, max_lines=99, kern=True):
        lines, line = [], ""
        words = text.split()
        for i, word in enumerate(words):
            trial = f"{line} {word}".strip()
            if line and self.width(trial, size, 0, kern) > max_width:
                lines.append(line)
                line = word
                if len(lines) == max_lines:
                    lines[-1] = self.fit(" ".join([lines[-1]] + words[i:]), size, max_width, 0, kern)
                    return lines
            else:
                line = trial
        # A word wider than the line on its own was placed whole; cut any line that still doesn't fit.
        return [self.fit(each, size, max_width, 0, kern) for each in (lines + [line] if line else lines)]


FACES = {key: Face(key) for key in FONTS}


@lru_cache(maxsize=None)
def font_face(key, chars):
    face = FACES[key]
    options = subset.Options()
    options.flavor = "woff2"
    options.hinting = False
    # Just the outlines and metrics: no names, no layout tables. The kerning is already in the text (see SVG.text).
    options.layout_features = []
    options.name_IDs = []
    options.name_legacy = False
    options.glyph_names = False
    options.notdef_outline = False
    options.drop_tables += ["GSUB", "GPOS", "GDEF", "STAT", "meta", "kern"]
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


def icon_markup(name, x, y, size, stroke_paint, stroke=1.8):
    return (
        f'<g transform="translate({num(x)} {num(y)}) scale({num(size / 24)})" fill="none" '
        f'{stroke_paint} stroke-width="{num(stroke * 24 / size)}" stroke-linecap="round" '
        f'stroke-linejoin="round">{ICONS.get(name, ICONS["spark"])}</g>'
    )


@lru_cache(maxsize=None)
def icon_data(name):
    """A file from icons/ as a data URI, or None when there is no such file."""
    path = ICON_DIR / name if name else None
    if path is None or not path.is_file():
        return None
    kind = "image/svg+xml" if path.suffix.lower() == ".svg" else "image/png"
    return f"data:{kind};base64,{base64.b64encode(path.read_bytes()).decode()}"


class SVG:
    def __init__(self, theme, width, height, label, ids=""):
        self.theme = theme
        self.t = THEMES[theme]
        self.width, self.height = width, height
        self.label = label
        self.parts, self.defs, self.css, self.chars = [], [], [], {}
        self.ids, self.id_prefix = 0, ids
        self.slots = []  # parts the Worker draws on each visit, in a template (see layout.TEMPLATES)

    def uid(self, prefix):
        self.ids += 1
        return f"{self.id_prefix}{prefix}{self.ids}"

    def add(self, markup):
        self.parts.append(markup)

    def use(self, font, text):
        self.chars.setdefault(font, set()).update(text)

    def text(self, x, y, s, font, size, color, tracking=0, anchor="start", extra=""):
        markup, width = self.text_markup(x, y, s, font, size, color, tracking, anchor, extra)
        self.add(markup)
        return width

    def text_markup(self, x, y, s, font, size, color, tracking=0, anchor="start", extra="", kern=True):
        """A line of text and its width. Kerning goes in as `dx` offsets, so the fonts don't need to carry it."""
        if not s:
            return "", 0
        face = FACES[font]
        width = face.width(s, size, tracking, kern)
        if anchor == "end":
            x -= width
        elif anchor == "middle":
            x -= width / 2
        self.use(font, s)
        spacing = f' letter-spacing="{num(tracking)}"' if tracking else ""
        offsets = [num(k * size / face.upm) for k in face.kerns(s)] if kern else []
        while offsets and offsets[-1] in ("0", "-0"):
            offsets.pop()
        kerning = f' dx="{" ".join(offsets)}"' if offsets else ""
        markup = (
            f'<text x="{num(x)}" y="{num(y)}"{kerning} class="f-{font}" font-size="{num(size)}" '
            f'{paint(color)}{spacing}{extra}>{esc(s)}</text>'
        )
        return markup, width

    def icon(self, name, x, y, size, color, stroke=1.8):
        self.add(icon_markup(name, x, y, size, paint(color, "stroke"), stroke))

    def picture(self, name, x, y, size):
        """Draws icons/<name> in a size × size box. Returns False when there is no such file.

        The image is defined once under an id made from what it is and where, without the theme's id prefix: the
        phone file holds both themes, and the identical definitions collapse into one (see render_pair)."""
        data = icon_data(name)
        if not data:
            return False
        key = "pic" + hashlib.sha256(f"{name}|{x:.2f}|{y:.2f}|{size:.2f}".encode()).hexdigest()[:10]
        self.defs.append(f'<image id="{key}" href="{data}" x="{num(x)}" y="{num(y)}" width="{num(size)}" '
                         f'height="{num(size)}" preserveAspectRatio="xMidYMid meet"/>')
        self.add(f'<use href="#{key}"/>')
        return True

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
        """The whole canvas, or only the (x, y, w, h) part of it given as `view`.

        preserveAspectRatio="none": a browser lays an image out in fractions of a pixel, so a 420 × 241 image can get
        a 240.98 px tall box. With the default ("meet") WebKit then letterboxes the drawing and pulls it in by up to
        1.5 device pixels at each side, which shows as a step wherever two images have to line up (the joined card at
        the top). "none" fills the box exactly; the difference in scale is far too small to see."""
        x, y, w, h = view or (0, 0, self.width, self.height)
        fonts = "".join(font_face(k, "".join(sorted(v))) for k, v in sorted(self.chars.items()))
        css = (
            fonts
            + "text{font-kerning:none;text-rendering:geometricPrecision}"
            + "".join(self.css)
            + "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{num(w)}" height="{num(h)}" '
            f'viewBox="{num(x)} {num(y)} {num(w)} {num(h)}" preserveAspectRatio="none" role="img" '
            f'aria-label="{esc(self.label)}">'
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
        + "text{font-kerning:none;text-rendering:geometricPrecision}"
        + extra
        + ".k{display:none}@media (prefers-color-scheme:dark){.l{display:none}.k{display:inline}}"
        + "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{num(w)}" height="{num(h)}" '
        f'viewBox="{num(x)} {num(y)} {num(w)} {num(h)}" preserveAspectRatio="none" role="img" '
        f'aria-label="{esc(light.label)}">'
        f"<title>{esc(light.label)}</title><style>{css}</style><defs>{''.join(dict.fromkeys(light.defs + dark.defs))}</defs>"
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


# ── shared shapes ─────────────────────────────────────────────────────────────


def arc(cx, cy, radius, a0, a1):
    """A circular arc from angle a0 to a1 (degrees, clockwise), as path data."""
    def point(a):
        return f"{num(cx + radius * math.cos(math.radians(a)))} {num(cy + radius * math.sin(math.radians(a)))}"
    return f"M{point(a0)}A{num(radius)} {num(radius)} 0 {1 if (a1 - a0) % 360 > 180 else 0} 1 {point(a1)}"


def vinyl_marks(cx, cy, r, label_r):
    """What makes a real record's turning visible: grooves that catch the light unevenly, dust and a few hairline
    scratches. Scattered at random, from a fixed seed, so every build draws the same marks and the Worker's kit stays
    the same file."""
    rng = random.Random(146)
    marks = []
    for _ in range(11):  # uneven pressing: short runs of groove that shine a little more
        radius, start = rng.uniform(label_r + 9, r - 5), rng.uniform(0, 360)
        marks.append(f'<path d="{arc(cx, cy, radius, start, start + rng.uniform(16, 80))}" fill="none" stroke="#fff" '
                     f'stroke-opacity="{num(rng.uniform(0.05, 0.12))}" stroke-width="{num(rng.uniform(0.6, 1.5))}" '
                     'stroke-linecap="round"/>')
    for _ in range(4):  # hairline scratches, along the grooves
        radius, start = rng.uniform(label_r + 14, r - 8), rng.uniform(0, 360)
        marks.append(f'<path d="{arc(cx, cy, radius, start, start + rng.uniform(3, 10))}" fill="none" stroke="#fff" '
                     f'stroke-opacity="{num(rng.uniform(0.12, 0.2))}" stroke-width=".5" stroke-linecap="round"/>')
    for _ in range(8):  # dust
        angle, distance = rng.uniform(0, 2 * math.pi), rng.uniform(label_r + 5, r - 3)
        marks.append(f'<circle cx="{num(cx + distance * math.cos(angle))}" cy="{num(cy + distance * math.sin(angle))}" '
                     f'r="{num(rng.uniform(0.45, 1.1))}" fill="#fff" fill-opacity="{num(rng.uniform(0.16, 0.34))}"/>')
    return "".join(marks)


def record(svg, cx, cy, r, words, period, cover=None):
    """A vinyl record turning once every `period` seconds. With `cover` (an image as a data URI), the album art is
    its label; without, a label of my own.

    No record is quite flat: as it turns it rocks a little on the platter (`warp`, once a turn) and drifts a fraction
    out of true (`drift`, on a longer, unrelated period), so the motion never repeats exactly. The light on the grooves
    stays where the light is, but rides along with that rocking."""
    label_r, hole_r = 0.38 * r, 4
    disc, label, shadow = svg.uid("disc"), svg.uid("label"), svg.uid("shadow")
    svg.defs.append(
        f'<radialGradient id="{disc}"><stop offset="0" stop-color="#2A2A2E"/><stop offset=".5" stop-color="#121214"/>'
        f'<stop offset="1" stop-color="#050506"/></radialGradient>'
        f'<radialGradient id="{label}" cx=".35" cy=".3"><stop offset="0" stop-color="#C7D6FF"/>'
        f'<stop offset=".6" stop-color="#7AA2FF"/><stop offset="1" stop-color="#3F63D8"/></radialGradient>'
        # A soft ring of shadow: a gradient rather than a blur, which would be redrawn on every frame of the spin.
        f'<radialGradient id="{shadow}"><stop offset=".84" stop-color="#000" stop-opacity=".42"/>'
        f'<stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>'
    )
    # The disc's own box, so the spin stays centred however the image is cropped or scaled. Lengths are in the
    # record's own units (radius 146).
    svg.css.append(
        f".spin{{transform-box:fill-box;transform-origin:center;animation:spin {num(period)}s linear infinite}}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
        f".warp{{transform-box:fill-box;transform-origin:center;animation:warp {num(period)}s ease-in-out infinite}}"
        "@keyframes warp{0%,100%{transform:translate(0,0) skewX(0deg) scale(1,1)}"
        "25%{transform:translate(.9px,-.5px) skewX(.35deg) scale(1.004,.996)}"
        "50%{transform:translate(.2px,.8px) skewX(-.1deg) scale(.997,1.003)}"
        "75%{transform:translate(-.8px,-.2px) skewX(-.3deg) scale(1.003,.997)}}"
        f".drift{{transform-box:fill-box;transform-origin:center;animation:drift {num(period * 2.618)}s ease-in-out "
        "infinite alternate}@keyframes drift{0%{transform:translate(-.5px,.3px) rotate(-.3deg)}"
        "100%{transform:translate(.6px,-.4px) rotate(.35deg)}}"
    )
    parts = [
        f'<circle cx="{num(cx + 4)}" cy="{num(cy + 12)}" r="{num(r * 1.16)}" fill="url(#{shadow})"/>',
        '<g class="drift"><g class="warp"><g class="spin">',
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
    parts.append(vinyl_marks(cx, cy, r, label_r))
    if cover:
        # Defined once with a fixed id, so the phone image, which holds both themes, carries the picture only once.
        svg.defs.append(f'<image id="cover" href="{cover}" x="{num(cx - label_r)}" y="{num(cy - label_r)}" '
                        f'width="{num(2 * label_r)}" height="{num(2 * label_r)}" preserveAspectRatio="xMidYMid slice"/>')
        art = svg.uid("art")
        svg.defs.append(f'<clipPath id="{art}"><circle cx="{num(cx)}" cy="{num(cy)}" r="{num(label_r)}"/></clipPath>')
        parts.append(
            f'<g clip-path="url(#{art})"><use href="#cover"/></g>'
            f'<circle cx="{num(cx)}" cy="{num(cy)}" r="{num(label_r - 0.8)}" fill="none" stroke="#000" stroke-opacity=".35" '
            f'stroke-width="1.6"/>'
            f'<circle cx="{num(cx)}" cy="{num(cy)}" r="{num(hole_r + 3)}" fill="#0B0B0D" fill-opacity=".55"/>'
            f'<circle cx="{num(cx)}" cy="{num(cy)}" r="{num(hole_r)}" fill="#C9C9CF"/>'
            "</g>"
        )
        finish(svg, parts, cx, cy, r, label_r)
        return
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
        f'<text class="f-mono" font-size="{size}" letter-spacing="{num(tracking)}" fill="#0B1636" fill-opacity=".72">'
        f'<textPath href="#{ring_id}">{esc(words)}</textPath></text>'
    )
    parts.append(svg.text_markup(cx, cy - 10, "RobyRew", "display", 13, ("#0B1636", 0.86), tracking=-0.4, anchor="middle")[0])
    svg.use("mono", "33 RPM")
    parts.append(
        f'<text x="{num(cx)}" y="{num(cy + 18)}" text-anchor="middle" class="f-mono" font-size="6.5" '
        f'letter-spacing="1.6" fill="#0B1636" fill-opacity=".7">33 RPM</text>'
    )
    parts.append("</g>")
    finish(svg, parts, cx, cy, r, label_r)


def finish(svg, parts, cx, cy, r, label_r):
    # Light catching the grooves; it stays put while the disc turns.
    for base in (-50, 130):
        for spread in (30, 22, 15, 9, 4):
            parts.append(
                f'<path d="{sector(cx, cy, label_r + 4, r - 1, base - spread, base + spread)}" fill="#fff" fill-opacity=".022"/>'
            )
    parts.append(
        f'<circle cx="{num(cx)}" cy="{num(cy)}" r="{num(r - 0.6)}" fill="none" stroke="#fff" stroke-opacity=".16" stroke-width="1.2"/>'
        "</g></g>"  # the warp and the drift
    )
    svg.add("".join(parts))


# An S-shaped tonearm, like a Technics SL-1200's, drawn pointing down from its pivot at (0, 0): the tube bends one
# way and back, the headshell is angled in towards the spindle and the counterweight sits behind the pivot. It is
# one rigid shape; parked or playing, only its angle changes.
ARM_TUBE = "M0 0V26C0 60 13 84 12 112S-6 168-4 196"


# What the arm does while the needle is in the groove: it sways with the record's rocking (`ride`, once a turn) and
# now and then shivers for a moment (`buzz`, run twice on unrelated periods, so the shivers come at irregular times).
# An invisible square centred on the pivot gives each group a box centred there, so they turn about the pivot.
ARM_PIVOT_BOX = '<rect x="-300" y="-300" width="600" height="600" fill="none"/>'


def tonearm(svg, px, py, angle, rest, ride=None):
    """The arm at `angle` degrees about its pivot (positive swings it in over the record), and its rest at `rest`.
    With `ride` (the record's seconds per turn) the needle is playing, and the arm sways and shivers."""
    metal = svg.uid("metal")
    svg.defs.append(
        f'<linearGradient id="{metal}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F4F4F6"/>'
        f'<stop offset=".5" stop-color="#A9A9B2"/><stop offset="1" stop-color="#6B6B74"/></linearGradient>'
    )
    rx, ry = rest
    # The rest stays put on the plinth: a round post with a clip the tube lies in when parked.
    svg.add(
        f'<circle cx="{num(rx + 2)}" cy="{num(ry + 4)}" r="11" fill="#000" fill-opacity=".25"/>'
        f'<circle cx="{num(rx)}" cy="{num(ry)}" r="10" fill="#2B2B30"/>'
        f'<circle cx="{num(rx)}" cy="{num(ry)}" r="10" fill="none" stroke="#fff" stroke-opacity=".12"/>'
        f'<path d="M{num(rx - 7)} {num(ry - 3)}H{num(rx + 7)}M{num(rx - 7)} {num(ry + 3)}H{num(rx + 7)}" stroke="#55555C" '
        f'stroke-width="2.4" stroke-linecap="round"/>'
    )
    tube = (
        f'<path d="{ARM_TUBE}" fill="none" stroke="url(#{metal})" stroke-width="6" stroke-linecap="round"/>'
        f'<path d="{ARM_TUBE}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="1.2" stroke-linecap="round" '
        f'transform="translate(-1.2 -1)"/>'
    )
    headshell = (
        '<g transform="translate(-4 196) rotate(20)">'
        f'<path d="M7 6L17 1.5" stroke="url(#{metal})" stroke-width="3" stroke-linecap="round"/>'  # finger lift
        f'<rect x="-8" y="-2" width="16" height="32" rx="3.5" fill="url(#{metal})"/>'
        '<rect x="-6" y="22" width="12" height="13" rx="2" fill="#2B2B30"/>'  # cartridge
        '<rect x="-1" y="34" width="2" height="4" rx="1" fill="#C9C9CF"/>'  # stylus
        "</g>"
    )
    weight = (
        f'<rect x="-2.5" y="-36" width="5" height="36" fill="url(#{metal})"/>'
        f'<rect x="-12" y="-64" width="24" height="28" rx="5" fill="url(#{metal})"/>'
        '<path d="M-12 -57H12M-12 -50H12M-12 -43H12" stroke="#000" stroke-opacity=".18"/>'
    )
    shadow = f'<path d="{ARM_TUBE}" fill="none" stroke="#000" stroke-opacity=".3" stroke-width="9" stroke-linecap="round"/>'
    body = f"{weight}{tube}{headshell}"
    if ride:
        svg.css.append(
            f".ride{{transform-box:fill-box;transform-origin:center;animation:ride {num(ride)}s ease-in-out infinite}}"
            "@keyframes ride{0%,100%{transform:rotate(0deg)}25%{transform:rotate(.14deg)}50%{transform:rotate(-.05deg)}"
            "75%{transform:rotate(-.12deg)}}"
            ".buzz,.buzz2{transform-box:fill-box;transform-origin:center;animation:buzz 6.7s linear infinite}"
            ".buzz2{animation-duration:10.3s;animation-delay:-3.1s}"
            "@keyframes buzz{0%,57%,66%,86%,92%,100%{transform:rotate(0deg)}58%{transform:rotate(.32deg)}"
            "59.5%{transform:rotate(-.26deg)}61%{transform:rotate(.18deg)}62.5%{transform:rotate(-.11deg)}"
            "64%{transform:rotate(.05deg)}87.5%{transform:rotate(-.2deg)}89%{transform:rotate(.14deg)}"
            "90.5%{transform:rotate(-.06deg)}}"
        )

        def moving(markup):
            return f'<g class="ride"><g class="buzz"><g class="buzz2">{ARM_PIVOT_BOX}{markup}</g></g></g>'

        shadow, body = moving(shadow), moving(body)
    svg.add(
        f'<g transform="translate({num(px + 4)} {num(py + 7)}) rotate({num(angle)})">{shadow}</g>'
        f'<g transform="translate({num(px)} {num(py)}) rotate({num(angle)})">{body}</g>'
        f'<circle cx="{num(px)}" cy="{num(py)}" r="24" fill="#2B2B30" fill-opacity=".55"/>'
        f'<circle cx="{num(px)}" cy="{num(py)}" r="19" fill="url(#{metal})"/>'
        f'<circle cx="{num(px)}" cy="{num(py)}" r="19" fill="none" stroke="#000" stroke-opacity=".25"/>'
        f'<circle cx="{num(px)}" cy="{num(py)}" r="7.5" fill="#2B2B30"/>'
    )


def window_mock(svg, x, y, w, h, hue):
    """A presenter window: a sidebar of verses, the live slide with a verse on it, and the next slides below."""
    t = svg.t
    colors = HUES.get(hue, HUES["violet"])
    slide = svg.uid("slide")
    svg.defs.append(
        f'<linearGradient id="{slide}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{colors[0]}" stop-opacity=".9"/>'
        f'<stop offset="1" stop-color="#0E0B1F"/></linearGradient>'
    )
    svg.add(
        f'<rect x="{num(x + 3)}" y="{num(y + 6)}" width="{num(w - 6)}" height="{num(h)}" rx="12" fill="#000" opacity=".16"/>'
        f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" rx="10" fill="{t["window"]}"/>'
        f'<rect x="{num(x + 0.5)}" y="{num(y + 0.5)}" width="{num(w - 1)}" height="{num(h - 1)}" rx="10" fill="none" '
        f'{paint(t["edge"], "stroke")}/>'
    )
    for i, color in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        svg.add(f'<circle cx="{num(x + 14 + i * 13)}" cy="{num(y + 13)}" r="4" fill="{color}"/>')
    # Sidebar: the passage, one verse picked.
    side_w = w * 0.27
    sx, sy = x + 8, y + 26
    for i in range(5):
        row_y = sy + i * 14
        if i == 1:
            svg.add(f'<rect x="{num(sx - 2)}" y="{num(row_y - 3)}" width="{num(side_w - 4)}" height="12" rx="3.5" '
                    f'fill="{colors[0]}" fill-opacity=".85"/>')
        svg.add(f'<rect x="{num(sx + 2)}" y="{num(row_y + 1.5)}" width="{num((side_w - 14) * (0.9 - 0.12 * (i % 3)))}" height="3" '
                f'rx="1.5" {paint((t["ink"], 0.9 if i == 1 else 0.28))}/>')
    # The live slide.
    lx, ly = x + side_w + 8, y + 24
    lw, lh = w - side_w - 16, h - 64
    svg.add(f'<rect x="{num(lx)}" y="{num(ly)}" width="{num(lw)}" height="{num(lh)}" rx="7" fill="url(#{slide})"/>')
    for width, height, dy, opacity in ((0.72, 4.5, 0.36, 0.95), (0.8, 4.5, 0.5, 0.95), (0.58, 4.5, 0.64, 0.95)):
        svg.add(
            f'<rect x="{num(lx + lw * (1 - width) / 2)}" y="{num(ly + lh * dy)}" width="{num(lw * width)}" '
            f'height="{height}" rx="{height / 2}" fill="#fff" fill-opacity="{opacity}"/>'
        )
    svg.text(lx + lw / 2, ly + lh * 0.86, "JOHN 1:1", "mono", 6.5, ("#FFFFFF", 0.75), tracking=1.4, anchor="middle")
    svg.add(f'<rect x="{num(lx + 8)}" y="{num(ly + 8)}" width="30" height="12" rx="6" fill="#FF3B30"/>')
    svg.text(lx + 23, ly + 16.6, "LIVE", "mono", 7, "#FFFFFF", tracking=1, anchor="middle")
    # Next slides.
    thumb_w = (lw - 3 * 6) / 4
    for i in range(4):
        tx = lx + i * (thumb_w + 6)
        svg.add(
            f'<rect x="{num(tx)}" y="{num(y + h - 32)}" width="{num(thumb_w)}" height="22" rx="4" '
            f'fill="{colors[i % 3]}" fill-opacity="{num(0.75 if i == 0 else 0.35)}"'
            + (f' stroke="{t["ink"]}" stroke-width="1.2"' if i == 0 else "")
            + "/>"
        )
