"""The page as a grid of glass tiles, one image per link.

GitHub strips CSS and image maps from READMEs, so an image can carry only one link. Every link gets its own tile,
and tiles of one group share a tint laid across all of them, so the colour flows from tile to tile.

No tile ever touches the edge of its image: wherever two images meet there is clear space. That's on purpose.
When an image lands between two device pixels (at 110 % or 125 % zoom, or on most phones), browsers blend its edge
with the page, and two images painted side by side on one colour show a hairline where they meet. In clear space
there's nothing to blend, so nothing shows at any zoom. `align="top"` on each image removes the gap GitHub would
otherwise leave under each row.

Every image also has a phone version, drawn at half the width with about the same type sizes. Both share the
README's `width="…%"`, so a row is split the same way on phones and computers; only the heights differ.

Sizes follow GitHub's own interface: titles around 20 px, text 13–14 px, labels 8–9 px.
"""

import math
import urllib.parse
from datetime import date, datetime, timedelta, timezone

from canvas import (FACES, HUES, PLATFORMS, STAR, SVG, artwork, blobs_for, compact, heat_colors, hexdump,
                    icon_markup, image_data, num, paint, record, render_pair, tonearm, window_mock)


WIDTH = {"d": 840, "m": 420}  # desktop and phone canvases
OUTER = {"d": 16, "m": 13}  # corner radius of a big tile
SMALL = {"d": 12, "m": 10}  # corner radius of a small one
GAP = {"d": 10, "m": 8}  # clear space between two tiles, across or down
SPACE = {"d": 14, "m": 12}  # room under the last row of a group, before the next heading
INSET = 1  # how far tiles stay from the sides of the page, so their rims are never cut
# A row of images can't be shorter than a line of text (24 px), or GitHub pads it. These keep every row above that
# down to a 600 px window for the desktop images and a 340 px phone for the phone ones.
MIN_HEIGHT = {"d": 40, "m": 40}


# ── the tiles ────────────────────────────────────────────────────────────────


class Card:
    """A group of tiles in one colour. Its tint is laid across all of them."""

    def __init__(self, hue="graphite", style="glass", blobs=None):
        self.hue, self.style = hue, style
        self.blobs = blobs or blobs_for(0)
        self.rows = []


class Cell:
    """One linked image, holding one tile."""

    def __init__(self, card, span, href, title, alt, draw, live=False, key=None):
        self.card, self.span, self.href, self.title, self.alt = card, span, href, title, alt
        self.draw, self.live, self.key = draw, live, key
        self.file = ""
        self.f0 = self.f1 = 0.0


class Row:
    """Cells side by side. A row of plain cells (headings, the footer) has no tiles and no gaps."""

    def __init__(self, name, d, m, cells, space=False, width=100):
        self.name, self.h, self.cells, self.space, self.width = name, {"d": d, "m": m}, cells, space, width
        self.tiled = any(cell.card.style != "none" for cell in cells)
        for v, minimum in MIN_HEIGHT.items():
            if self.height(v) < minimum:
                raise ValueError(f"row {name} is {self.height(v)} high on {v}; GitHub would pad it under {minimum}")
        total = sum(c.span for c in cells)
        start = 0.0
        seen = set()
        for i, cell in enumerate(cells):
            cell.file = f"{name}-{cell.key or i + 1}"
            if cell.file in seen:
                cell.file += f"-{i + 1}"
            seen.add(cell.file)
            cell.f0, start = start / total, start + cell.span
            cell.f1 = start / total
            if not cell.card.rows or cell.card.rows[-1] is not self:
                cell.card.rows.append(self)

    def pad(self, v):
        """Clear space above a tile, and below it unless the row ends a group."""
        return GAP[v] / 2 if self.tiled else 0

    def height(self, v):
        return self.pad(v) + self.h[v] + (SPACE[v] if self.space else self.pad(v))

    def tile(self, cell, v):
        """A tile's left and right edges: half a gap in from each neighbour, so the images meet in clear space."""
        x0, x1 = cell.f0 * WIDTH[v], cell.f1 * WIDTH[v]
        if not self.tiled:
            return x0, x1
        return x0 + (GAP[v] / 2 if cell.f0 > 1e-9 else INSET), x1 - (GAP[v] / 2 if cell.f1 < 1 - 1e-9 else INSET)

    def extent(self, card, v):
        """Where a group's tiles start and end on this row."""
        boxes = [self.tile(cell, v) for cell in self.cells if cell.card is card]
        return boxes[0][0], boxes[-1][1]

    def radius(self, v):
        return OUTER[v] if self.h[v] >= 80 else SMALL[v]

    def percent(self, cell):
        """The README width of a cell, rounded down so a row never spills onto a second line."""
        return math.floor((cell.f1 - cell.f0) * self.width * 1000 + 1e-6) / 1000


class Ctx:
    """What a cell's drawing function gets: the canvas, and its tile on it (y from the tile's top, corner radius r)."""

    def __init__(self, svg, v, x, w, h, r):
        self.svg, self.t, self.v, self.m = svg, svg.t, v, v == "m"
        self.x, self.w, self.h, self.r = x, w, h, r

    def pick(self, desktop, phone):
        return phone if self.m else desktop


def rounded(x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    return (
        f"M{num(x + r)} {num(y)}H{num(x + w - r)}A{num(r)} {num(r)} 0 0 1 {num(x + w)} {num(y + r)}"
        f"V{num(y + h - r)}A{num(r)} {num(r)} 0 0 1 {num(x + w - r)} {num(y + h)}"
        f"H{num(x + r)}A{num(r)} {num(r)} 0 0 1 {num(x)} {num(y + h - r)}V{num(y + r)}"
        f"A{num(r)} {num(r)} 0 0 1 {num(x + r)} {num(y)}Z"
    )


def card_frame(card, row, v):
    """How far down its group this row starts, and the group's full height, gaps included."""
    total, mine = 0, 0
    for r in card.rows:
        if r is row:
            mine = total
        total += r.h[v] + GAP[v]
    return mine, total


def vertical(svg, x, y0, y1, stops):
    """A top-to-bottom gradient in canvas coordinates."""
    grad = svg.uid("lin")
    svg.defs.append(
        f'<linearGradient id="{grad}" gradientUnits="userSpaceOnUse" x1="{num(x)}" y1="{num(y0)}" x2="{num(x)}" '
        f'y2="{num(y1)}">' + "".join(f'<stop offset="{num(o)}" stop-color="{c}" stop-opacity="{num(a)}"/>' for o, c, a in stops)
        + "</linearGradient>"
    )
    return f"url(#{grad})"


def background(svg, row, cell, v):
    """Frosted glass: a see-through fill, the group's tint, a sheen at the top, a light rim and, in light mode, a
    soft shadow underneath. All of it stays inside the image, clear of its edges."""
    card = cell.card
    if card.style == "none":
        return
    t = svg.t
    x0, x1 = row.tile(cell, v)
    y0, w, h = row.pad(v), x1 - x0, row.h[v]
    r = row.radius(v)
    offset, full = card_frame(card, row, v)
    gx0, gx1 = row.extent(card, v)
    colors = HUES.get(card.hue, HUES["graphite"])
    clip = svg.uid("tile")
    svg.defs.append(f'<clipPath id="{clip}"><path d="{rounded(x0, y0, w, h, r)}"/></clipPath>')
    parts = [f'<g clip-path="url(#{clip})">', f'<rect x="{num(x0)}" y="{num(y0)}" width="{num(w)}" height="{h}" {paint(t["card"])}/>']
    tint = t["blob"] * (1.6 if card.style == "tinted" else 1)
    for fx, fy, fr, ci, strength in card.blobs:
        # Placed on the whole group, so the colour carries on from one tile to the next.
        cx, cy, br = gx0 + fx * (gx1 - gx0), fy * full - offset, fr * max(gx1 - gx0, full)
        if cy + br < y0 or cy - br > y0 + h or cx + br < x0 or cx - br > x1:
            continue
        grad = svg.uid("blob")
        color = colors[ci]
        alpha = min(tint * strength, 0.9)
        svg.defs.append(
            f'<radialGradient id="{grad}" gradientUnits="userSpaceOnUse" cx="{num(cx)}" cy="{num(cy)}" r="{num(br)}">'
            f'<stop offset="0" stop-color="{color}" stop-opacity="{num(alpha)}"/>'
            f'<stop offset=".6" stop-color="{color}" stop-opacity="{num(alpha * 0.35)}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>'
        )
        parts.append(f'<rect x="{num(x0)}" y="{num(y0)}" width="{num(w)}" height="{h}" fill="url(#{grad})"/>')
    sheen = min(h * 0.5, 100)
    color, alpha = t["sheen"]
    fill = vertical(svg, x0, y0, y0 + sheen, [(0, color, alpha), (1, color, 0)])
    parts.append(f'<rect x="{num(x0)}" y="{num(y0)}" width="{num(w)}" height="{num(sheen)}" fill="{fill}"/>')
    parts.append("</g>")
    color, at_top, at_bottom = t["rim"]
    rim = vertical(svg, x0, y0, y0 + h, [(0, color, at_top), (0.5, color, (at_top + at_bottom) / 2), (1, color, at_bottom)])
    parts.append(f'<path d="{rounded(x0 + 0.5, y0 + 0.5, w - 1, h - 1, r - 0.5)}" fill="none" stroke="{rim}"/>')
    below = row.height(v) - y0 - h
    if t["shadow"] and below > 2:
        depth = min(below - 1.5, SPACE[v] * 0.7)
        fill = vertical(svg, x0, y0 + h, y0 + h + depth, [(0, "#000000", t["shadow"]), (1, "#000000", 0)])
        parts.append(f'<rect x="{num(x0 + r * 0.7)}" y="{num(y0 + h)}" width="{num(w - 1.4 * r)}" height="{num(depth)}" fill="{fill}"/>')
    svg.add("".join(parts))


def render(row, cell, theme, v):
    svg, view = draw(row, cell, theme, v)
    return svg.render(view=view)


def render_phone(row, cell):
    """The phone image: both themes in one file (see canvas.render_pair)."""
    light, view = draw(row, cell, "light", "m", "l")
    dark, _ = draw(row, cell, "dark", "m", "k")
    return render_pair(light, dark, view)


def draw(row, cell, theme, v, ids=""):
    W, H = WIDTH[v], row.height(v)
    x0, x1 = cell.f0 * W, cell.f1 * W
    svg = SVG(theme, W, H, cell.alt, ids)
    background(svg, row, cell, v)
    tx0, tx1 = row.tile(cell, v)
    pad = row.pad(v)
    if pad:
        svg.add(f'<g transform="translate(0 {num(pad)})">')
    cell.draw(Ctx(svg, v, tx0, tx1 - tx0, row.h[v], row.radius(v)))
    if pad:
        svg.add("</g>")
    return svg, (x0, 0, x1 - x0, H)


# ── small pieces ─────────────────────────────────────────────────────────────


def fit(text, font, size, room, tracking=0.0):
    return FACES[font].fit(str(text), size, max(room, 1), tracking)


def shrink(text, font, size, room, smallest=0.8, tracking=0.0):
    """Steps the size down (to `smallest` of it) before cutting the text short. Returns (size, text)."""
    floor = size * smallest
    while size > floor and FACES[font].width(str(text), size, tracking) > room:
        size -= 0.5
    return size, fit(text, font, size, room, tracking)


def kicker(c, x, y, text, color=None, size=None):
    size = size or c.pick(9, 8.5)
    return c.svg.text(x, y, fit(text.upper(), "mono", size, c.x + c.w - x - 8, 1.6), "mono", size,
                      color or c.t["faint"], tracking=1.6)


def arrow_button(c, x, y, size):
    c.svg.glass(x, y, size, size, size / 2)
    c.svg.icon("arrow", x + size * 0.25, y + size * 0.25, size * 0.5, c.t["dim"], stroke=2)


def mark(c, x, baseline, size, icon=None, star=False, dot=None, color=None):
    """A small icon, star or colour dot sitting on a text baseline. Returns its width."""
    if star:
        c.svg.add(f'<path d="{STAR}" fill="#F2B640" transform="translate({num(x)} {num(baseline - size * 0.86)}) '
                  f'scale({num(size / 24)})"/>')
        return size
    if dot:
        c.svg.add(f'<circle cx="{num(x + size * 0.32)}" cy="{num(baseline - size * 0.36)}" r="{num(size * 0.3)}" fill="{dot}"/>')
        return size * 0.64
    if icon:
        c.svg.icon(icon, x, baseline - size * 0.86, size, color or c.t["dim"], stroke=2)
        return size
    return 0


def equalizer(svg, x, baseline, height=10, color="#30D158"):
    svg.css.append(
        ".eq rect{transform-box:fill-box;transform-origin:50% 100%;animation:eq .9s ease-in-out infinite alternate}"
        "@keyframes eq{from{transform:scaleY(.3)}}"
    )
    bars = "".join(
        f'<rect x="{num(x + i * 4)}" y="{num(baseline - height)}" width="2.4" height="{num(height)}" rx=".8" fill="{color}" '
        f'style="animation-delay:{num(-0.27 * i * (i + 1))}s"/>'
        for i in range(4)
    )
    svg.add(f'<g class="eq">{bars}</g>')
    return 15


def centered_block(h, first, gap, second):
    """Baselines for a big line over a small line, centred in a cell of height h."""
    block = first * 0.72 + gap + second * 0.72
    top = (h - block) / 2
    return top + first * 0.72, top + first * 0.72 + gap + second * 0.72


def meta_stat(c, value, label, icon=None, star=False, dot=None):
    """Value with an icon, over a small label, centred. Used under projects and in side columns."""
    svg, t = c.svg, c.t
    size, small = c.pick(13, 12.5), 8
    vy, ly = centered_block(c.h, size, 9, small)
    iw = c.pick(16, 14) if (icon or star) else (c.pick(11, 10) if dot else 0)
    size, value = shrink(value, "semi", size, c.w - c.pick(16, 10) - iw)
    width = iw + FACES["semi"].width(value, size)
    x = c.x + (c.w - width) / 2
    mark(c, x, vy, c.pick(11.5, 11), icon=icon, star=star, dot=dot)
    svg.text(x + iw, vy, value, "semi", size, t["ink"])
    label = fit(label.upper(), "mono", small, c.w - 12, 1)
    svg.text(c.x + c.w / 2, ly, label, "mono", small, t["faint"], tracking=1, anchor="middle")


def big_stat(c, value, label, icon=None, star=False, size=None):
    """A number with a label under it, left aligned. Used for the charts."""
    svg, t = c.svg, c.t
    pad = c.pick(18, 12)
    size = size or c.pick(19, 16)
    small = 8
    vy, ly = centered_block(c.h, size, c.pick(9, 8), small)
    room = c.w - 2 * pad
    extra = c.pick(18, 14)
    if FACES["display"].width(value, size, -0.4) > room - extra:
        icon = star = None
    size, value = shrink(value, "display", size, room if not (icon or star) else room - extra, 0.82, -0.4)
    width = svg.text(c.x + pad - 1, vy, value, "display", size, t["ink"], tracking=-0.4)
    mark(c, c.x + pad + width + c.pick(5, 4), vy - size * 0.06, c.pick(12, 10.5), icon=icon, star=star, color=t["faint"])
    svg.text(c.x + pad, ly, fit(label.upper(), "mono", small, room + 4, 1), "mono", small, t["faint"], tracking=1)


def when_label(stamp):
    if not stamp:
        return ""
    try:
        moment = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return ""
    return moment.strftime("%b %-d").upper()


def search(query, kind):
    return f"https://github.com/search?q={urllib.parse.quote(query)}&type={kind}"


# ── the record player ────────────────────────────────────────────────────────

# One row of two tiles: who I am, and the record player with what's on it, beside the record on computers and under
# it on phones. The record must stay in one image: cut across two, its halves would turn out of step.
HERO = {
    # cx, cy: the record's centre from the tile's top left. info: where what's playing starts, and its right margin.
    "d": {"h": 216, "pad": 26, "cx": 106, "cy": 108, "r": 88, "info": (246, 18)},
    "m": {"h": 200, "pad": 14, "cx": 64, "cy": 62, "r": 50, "info": (13, 12)},
}
SPLIT = 0.5
# The arm, in the record's own units (radius 146): hinged at the top right, swung slightly out onto its rest when
# parked, or in by 24 degrees so the needle sits in the outer grooves.
ARM_PIVOT = (172, -100)
ARM_PARKED, ARM_PLAYING = -4, 24
ARM_REST = (186, 53)  # where the parked tube crosses, worked out from its curve
# Seconds per turn: always turning, a lazy idle, and a real 33 1/3 RPM while a song plays.
SPIN_IDLE, SPIN_PLAYING = 6, 1.8

# Set while build.py draws the templates the Worker fills in on each visit (see .github/worker/now.js): what's on the
# deck is left as a slot, with its measurements, and the record's cover as a placeholder.
TEMPLATES = False
COVER_SLOT = "{{cover}}"
# Every character a song, artist or album is likely to use: the templates carry these, the rest fall back to the
# system font.
INFO_CHARS = "".join(map(chr, range(0x20, 0x7F))) + "".join(map(chr, range(0xA0, 0x180))) + "‘’‚“”„–—…•·′″€™"
STATUS_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ·"


def status_text(now):
    if not now:
        return "OFF AIR"
    if now.get("playing"):
        return "NOW PLAYING"
    if now.get("paused"):
        return "PAUSED"
    stamp = when_label(now.get("when"))
    return f"LAST PLAYED · {stamp}" if stamp else "LAST PLAYED"


def info_items(now):
    """What's on the deck, ready to print."""
    if not now:
        return {"status": "OFF AIR", "title": "Nothing on the deck", "artist": "Music is usually on, check back soon",
                "album": "", "kind": "", "platform": "", "user": ""}
    return {"status": status_text(now), "title": now.get("title") or "Untitled", "artist": now.get("artist") or "",
            "album": now.get("context") or "", "kind": now.get("context_kind") or "",
            "platform": now.get("platform") or "Last.fm", "user": now.get("user") or ""}


def info_params(c, x, w, y0, y1):
    """Where what's playing goes and how it looks. The Worker gets the same numbers, so both draw it alike."""
    t = c.t
    return {
        "ids": c.svg.id_prefix, "x": x, "w": w, "y0": y0, "y1": y1, "phone": c.m,
        "status": c.pick(7.5, 7), "title": c.pick(17, 12.5), "lh": c.pick(20, 15), "lines": c.pick(2, 1),
        "artist": c.pick(12.5, 10), "album": c.pick(10.5, 9), "gaps": c.pick([12, 7, 7, 12], [8, 5, 5, 0]),
        "ink": t["ink"], "dim": t["dim"], "faint": t["faint"], "glass": t["glass"], "edge": t["edge"],
    }


def info_markup(svg, k, now):
    """Status, title, artist, album and where it played, stacked and centred in their space. Self-contained, with its
    own style, so the Worker can drop the same thing into a template. No kerning, like the Worker."""
    semi, mono = FACES["semi"], FACES["mono"]

    def text(x, y, s, font, size, color, tracking=0):
        return svg.text_markup(x, y, s, font, size, color, tracking, kern=False)[0]

    item = info_items(now)
    playing = bool(now and now.get("playing"))
    x, w, phone = k["x"], k["w"], k["phone"]
    gaps = k["gaps"]
    status = item["status"].split(" · ")[0] if phone else item["status"]
    titles = semi.wrap(item["title"], k["title"], w, k["lines"], kern=False) or [""]
    artist = item["artist"]
    album = item["album"]
    where = item["platform"] + (f' · @{item["user"]}' if item["user"] else "")
    if phone:
        artist = " · ".join(part for part in (artist, album) if part)
        album = ""
    # The block's height, from the top of the status line to the bottom of its last line, to centre it.
    cap = 0.72
    height = k["status"] * cap + gaps[0] + k["title"] * cap + (len(titles) - 1) * k["lh"]
    if artist:
        height += gaps[1] + k["artist"] * cap
    if album:
        height += gaps[2] + k["album"] * cap
    pill = 20 if not phone else 0
    if item["platform"]:
        height += gaps[3] + pill if not phone else gaps[2] + k["album"] * cap
    y = k["y0"] + (k["y1"] - k["y0"] - height) / 2 + k["status"] * cap
    out, style = [], []
    dot = "#30D158" if playing else "#8E8E93"
    if playing:
        style.append(".pulse{animation:pulse 1.6s ease-in-out infinite alternate}@keyframes pulse{to{opacity:.3}}")
    pulse = ' class="pulse"' if playing else ""
    out.append(f'<circle{pulse} cx="{num(x + 3)}" cy="{num(y - k["status"] * 0.36)}" r="3" fill="{dot}"/>')
    label = mono.fit(status, k["status"], w - 30, 1.2, kern=False)
    out.append(text(x + 11, y, label, "mono", k["status"], k["dim"], 1.2))
    if playing:
        # Bars bouncing to the music, after the status.
        bx = x + 11 + mono.width(label, k["status"], 1.2, kern=False) + 7
        style.append(".eq rect{transform-box:fill-box;transform-origin:50% 100%;animation:eq .9s ease-in-out infinite alternate}"
                     "@keyframes eq{from{transform:scaleY(.3)}}")
        bars = "".join(
            f'<rect x="{num(bx + i * 3.6)}" y="{num(y - 8)}" width="2.2" height="8" rx=".8" fill="#30D158" '
            f'style="animation-delay:{num(-0.27 * i * (i + 1))}s"/>'
            for i in range(4)
        )
        out.append(f'<g class="eq">{bars}</g>')
    y += gaps[0] + k["title"] * cap
    for i, line in enumerate(titles):
        out.append(text(x, y, line, "semi", k["title"], k["ink"], -0.2))
        if i < len(titles) - 1:
            y += k["lh"]
    if artist:
        y += gaps[1] + k["artist"] * cap
        out.append(text(x, y, semi.fit(artist, k["artist"], w, kern=False), "semi", k["artist"], k["dim"]))
    if album:
        y += gaps[2] + k["album"] * cap
        size = k["album"] + 1
        out.append(icon_markup("list" if item["kind"] == "Playlist" else "disc", x, y - size * 0.82, size, paint(k["faint"], "stroke"), 2))
        out.append(text(x + size + 5, y, semi.fit(album, k["album"], w - size - 5, kern=False), "semi", k["album"], k["faint"]))
    if item["platform"]:
        color = PLATFORMS.get(item["platform"], "#9CA3AF")
        if phone:
            y += gaps[2] + k["album"] * cap
            out.append(f'<circle cx="{num(x + 3)}" cy="{num(y - k["album"] * 0.34)}" r="2.6" fill="{color}"/>')
            out.append(text(x + 10, y, semi.fit(where, k["album"], w - 10, kern=False), "semi", k["album"], k["faint"]))
        else:
            y += gaps[3]
            size = 9.5
            label = semi.fit(where, size, w - 26, kern=False)
            width = semi.width(label, size, kern=False) + 26
            out.append(f'<rect x="{num(x)}" y="{num(y)}" width="{num(width)}" height="{pill}" rx="{pill / 2}" '
                       f'{paint(k["glass"])} {paint(k["edge"], "stroke")}/>')
            out.append(f'<circle cx="{num(x + 10)}" cy="{num(y + pill / 2)}" r="3" fill="{color}"/>')
            out.append(text(x + 18, y + pill / 2 + size * 0.36, label, "semi", size, k["dim"]))
    return (f"<style>{''.join(style)}</style>" if style else "") + "".join(out)


SPARKLE = "M0-1C.12-.12.12-.12 1 0C.12.12.12.12 0 1C-.12.12-.12.12-1 0C-.12-.12-.12-.12 0-1Z"


def aurora(c):
    """Three soft lights drifting behind the text, slowly, for ever."""
    svg = c.svg
    clip = svg.uid("aur")
    svg.defs.append(f'<clipPath id="{clip}"><rect x="{num(c.x)}" y="0" width="{num(c.w)}" height="{num(c.h)}" rx="{c.r}"/></clipPath>')
    strength = 0.3 if svg.theme == "dark" else 0.2
    reach = c.pick(1, 0.55)
    svg.css.append(
        ".au{transform-box:fill-box;transform-origin:center}"
        f".a1{{animation:a1 19s ease-in-out infinite alternate}}@keyframes a1{{to{{transform:translate({num(70 * reach)}px,{num(16 * reach)}px) scale(1.3)}}}}"
        f".a2{{animation:a2 23s ease-in-out infinite alternate}}@keyframes a2{{to{{transform:translate({num(-60 * reach)}px,{num(-14 * reach)}px) scale(.8)}}}}"
        f".a3{{animation:a3 29s ease-in-out infinite alternate}}@keyframes a3{{to{{transform:translate({num(40 * reach)}px,{num(-22 * reach)}px) scale(1.2)}}}}"
    )
    parts = [f'<g clip-path="url(#{clip})">']
    for n, (fx, fy, fr, color) in enumerate(((0.18, 0.2, 0.5, "#FF6A2B"), (0.85, 0.85, 0.45, "#D62F4B"), (0.6, 0.05, 0.35, "#FFB347")), 1):
        grad = svg.uid("aug")
        svg.defs.append(f'<radialGradient id="{grad}"><stop offset="0" stop-color="{color}" stop-opacity="{num(strength)}"/>'
                        f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')
        r = fr * c.w
        parts.append(f'<circle class="au a{n}" cx="{num(c.x + fx * c.w)}" cy="{num(fy * c.h)}" r="{num(r)}" fill="url(#{grad})"/>')
    svg.add("".join(parts) + "</g>")


def lively_name(c, x, y, name, size):
    """The name, with a sweep of colour through it now and then, and a short glitch every so often."""
    svg, t = c.svg, c.t
    tracking = -size * 0.035
    main, width = svg.text_markup(x, y, name, "display", size, t["ink"], tracking)
    top, height = y - size * 0.78, size * 0.98
    # The glitch: a red and a cyan copy, each cut to a band of the letters, knocked sideways for a moment.
    bands = []
    for n, (color, b0, b1) in enumerate((("#FF2D6F", 0.0, 0.46), ("#22D3EE", 0.52, 1.0)), 1):
        band = svg.uid("band")
        svg.defs.append(f'<clipPath id="{band}"><rect x="{num(x - 8)}" y="{num(top + b0 * height)}" width="{num(width + 16)}" '
                        f'height="{num((b1 - b0) * height)}"/></clipPath>')
        copy = svg.text_markup(x, y, name, "display", size, (color, 0.85), tracking)[0]
        bands.append(f'<g clip-path="url(#{band})"><g class="g{n}">{copy}</g></g>')
    svg.css.append(
        ".g1,.g2{opacity:0;animation:g1 9s steps(1,end) infinite}.g2{animation-name:g2}"
        "@keyframes g1{0%,90%{opacity:0;transform:none}91%{opacity:1;transform:translate(-4px,0)}92.4%{transform:translate(3px,0)}"
        "93.8%{transform:translate(-2px,0)}95%,100%{opacity:0;transform:none}}"
        "@keyframes g2{0%,90%{opacity:0;transform:none}91%{opacity:1;transform:translate(4px,0)}92.4%{transform:translate(-3px,0)}"
        "93.8%{transform:translate(2px,0)}95%,100%{opacity:0;transform:none}}"
        ".jolt{animation:jolt 9s steps(1,end) infinite}@keyframes jolt{0%,90.6%{transform:none}91.2%{transform:translate(1.5px,0)}"
        "92.6%{transform:translate(-1px,0)}94%,100%{transform:none}}"
    )
    # The sweep: a band of warm colour passing through the letters.
    letters, shine = svg.uid("letters"), svg.uid("shine")
    sweep = width * 0.45
    svg.defs.append(
        f'<clipPath id="{letters}">{main}</clipPath>'
        f'<linearGradient id="{shine}"><stop offset="0" stop-color="#FFB37A" stop-opacity="0"/>'
        f'<stop offset=".45" stop-color="#FFB37A" stop-opacity=".95"/><stop offset=".6" stop-color="#FF6A2B" stop-opacity=".95"/>'
        f'<stop offset="1" stop-color="#FF6A2B" stop-opacity="0"/></linearGradient>'
    )
    svg.css.append(
        f".sweep{{animation:sweep 6.5s cubic-bezier(.5,0,.3,1) infinite}}"
        f"@keyframes sweep{{0%,64%{{transform:translateX(0)}}100%{{transform:translateX({num(width + sweep)}px)}}}}"
    )
    svg.add("".join(bands) + f'<g class="jolt">{main}</g>'
            f'<g clip-path="url(#{letters})"><rect class="sweep" x="{num(x - sweep)}" y="{num(top - 4)}" width="{num(sweep)}" '
            f'height="{num(height + 8)}" fill="url(#{shine})"/></g>')
    return width


def sparkles(c, points):
    """Little stars that light up and fade, one after another."""
    color = "#FFD2A6" if c.svg.theme == "dark" else "#F06A2E"
    c.svg.css.append(
        ".tw{transform-box:fill-box;transform-origin:center;opacity:0;animation:tw 5.2s ease-in-out infinite}"
        "@keyframes tw{0%,60%,100%{opacity:0;transform:scale(.2) rotate(0)}72%{opacity:1;transform:scale(1) rotate(45deg)}"
        "86%{opacity:0;transform:scale(.3) rotate(90deg)}}"
    )
    for i, (x, y, size) in enumerate(points):
        c.svg.add(f'<path class="tw" d="{SPARKLE}" fill="{color}" transform="translate({num(x)} {num(y)}) scale({num(size)})" '
                  f'style="animation-delay:{num(i * 1.7)}s"/>')


def identity(c, me):
    """My name, what I do and where, with a little life in it: a slow aurora behind, a sweep of colour through the
    name, a glitch and some sparkle now and then, and a blinking cursor."""
    svg, t = c.svg, c.t
    g = HERO[c.v]
    left = c.x + g["pad"]
    room = c.x + c.w - left - g["pad"]
    aurora(c)
    facts = me.get("facts", [])
    kick = c.pick(8.5, 7.5)
    size = c.pick(40, 28)
    while size > 20 and FACES["display"].width(me["name"], size, -size * 0.035) > room:
        size -= 1
    fs, lh = c.pick(14, 11.5), c.pick(19, 14.5)
    statement = FACES["text"].wrap(me["statement"], fs, room, c.pick(2, 3))
    aside = FACES["semi"].wrap(me["aside"], fs, room - 8, 2)
    rest = facts[1:]
    # Lay the block out from 0, then centre it in the tile.
    name_y = (c.pick(16, 11) + size * 0.76) if facts else size * 0.76
    text_y = name_y + c.pick(26, 19)
    end_y = text_y + len(statement) * lh + c.pick(1, 2) + len(aside) * lh  # the line after the last one
    facts_y = end_y + c.pick(4, 3) if rest else end_y - lh
    shift = (c.h - facts_y - kick * 0.72) / 2 + kick * 0.72  # the kicker's baseline, so the block sits in the middle
    if facts:
        y = shift
        text = facts[0]["value"] if c.m else f'{facts[0]["label"]} · {facts[0]["value"]}'
        svg.css.append(".ping{transform-box:fill-box;transform-origin:center;animation:ping 2.4s ease-out infinite}"
                       "@keyframes ping{from{transform:scale(1);opacity:.55}to{transform:scale(3.2);opacity:0}}")
        cy = y - kick * 0.35
        svg.add(f'<circle class="ping" cx="{num(left + 3)}" cy="{num(cy)}" r="2.6" fill="#F2A65A"/>'
                f'<circle cx="{num(left + 3)}" cy="{num(cy)}" r="2.6" fill="#F2A65A"/>')
        svg.text(left + 13, y, fit(text.upper(), "mono", kick, room - 13, 1.4), "mono", kick, t["dim"], tracking=1.4)
    width = lively_name(c, left - size * 0.03, shift + name_y, me["name"], size)
    y = shift + text_y
    for line in statement:
        svg.text(left, y, line, "text", fs, t["dim"])
        y += lh
    y += c.pick(1, 2)
    end = left
    for line in aside:
        end = left + svg.text(left, y, line, "semi", fs, t["aside"])
        last = y
        y += lh
    if aside:
        # A cursor after the last word, as if it were still being typed.
        svg.css.append(".caret{animation:caret 1.1s steps(1,end) infinite}@keyframes caret{50%{opacity:0}}")
        svg.add(f'<rect class="caret" x="{num(end + 3)}" y="{num(last - fs * 0.8)}" width="{c.pick(2, 1.6)}" '
                f'height="{num(fs * 0.98)}" rx=".6" {paint(t["aside"])}/>')
    if rest:
        svg.text(left, shift + facts_y, fit(" · ".join(f["value"] for f in rest).upper(), "mono", kick, room, 1.2),
                 "mono", kick, t["faint"], tracking=1.2)
    name_x = left - size * 0.03
    sparkles(c, [(name_x + width + c.pick(10, 7), shift + name_y - size * 0.72, c.pick(5, 3.6)),
                 (name_x + width * 0.42, shift + name_y - size * 0.98, c.pick(3.5, 2.6)),
                 (c.x + c.w - c.pick(34, 18), c.pick(30, 20), c.pick(4.2, 3))])


def deck(c, me, now):
    """The record, its arm, and what's on it."""
    svg = c.svg
    g = HERO[c.v]
    playing = bool(now and now.get("playing"))
    clip = svg.uid("deck")  # the tile's own shape, so the record's shadow stays inside it
    svg.defs.append(f'<clipPath id="{clip}"><rect x="{num(c.x)}" y="0" width="{num(c.w)}" height="{num(c.h)}" rx="{c.r}"/></clipPath>')
    if TEMPLATES:
        cover = COVER_SLOT if (now or {}).get("cover") else None
    else:
        cover = image_data((now or {}).get("cover"))
    svg.add(f'<g clip-path="url(#{clip})"><g transform="translate({num(c.x + g["cx"])} {num(g["cy"])}) scale({num(g["r"] / 146)})">')
    record(svg, 0, 0, 146, me["record"], SPIN_PLAYING if playing else SPIN_IDLE, cover)
    tonearm(svg, *ARM_PIVOT, ARM_PLAYING if playing else ARM_PARKED, ARM_REST)
    svg.add("</g></g>")
    ix, right = g["info"]
    if c.m:
        y0, y1 = g["cy"] + g["r"] + 8, c.h - 8
    else:
        y0, y1 = 0, c.h
    params = info_params(c, c.x + ix, c.w - ix - right, y0, y1)
    if TEMPLATES:
        svg.slots.append(params)
        svg.add(f"<!--now:{params['ids']}-->")
        svg.use("semi", INFO_CHARS)
        svg.use("mono", STATUS_CHARS)
        return
    svg.add(info_markup(svg, params, now))


def hero_rows(p, now, hrefs, home):
    """The record player row. `hrefs` says where the deck links to (the Worker, Pages redirects, or the song itself);
    `home` is where my own tile goes."""
    me = p["me"]
    card = Card("ember", blobs=[(0.96, 0.4, 0.5, 0, 0.9), (0.04, 0.95, 0.5, 1, 0.7), (0.45, -0.25, 0.4, 2, 0.5)])
    bio = f'{me["name"]}. {me["statement"]} {me["aside"]}'
    facts = me.get("facts", [])
    return [Row("hero", HERO["d"]["h"], HERO["m"]["h"], [
        Cell(card, SPLIT, home, f'{facts[0]["label"]}: {facts[0]["value"]}' if facts else me["name"], bio,
             lambda c: identity(c, me), key="me"),
        Cell(card, 1 - SPLIT, hrefs["play"], "Play what's on the deck", "The record player, with what I'm listening to",
             lambda c: deck(c, me, now), live=True, key="deck"),
    ], space=True)]


# ── section headers ──────────────────────────────────────────────────────────


def header(c, kicker_text, title, side, arrow, bars=False):
    t = c.t
    y = c.pick(26, 24)
    width = kicker(c, c.x + 2, y, kicker_text, t["accent"])
    if bars:
        equalizer(c.svg, c.x + 2 + width + 8, y + 0.5, c.pick(9, 8))
    base = c.pick(50, 45)
    size, title = shrink(title, "display", c.pick(19, 16.5), c.w * 0.62, 0.85, -0.4)
    c.svg.text(c.x + 1, base, title, "display", size, t["head"], tracking=-0.4)
    right = c.x + c.w - 2
    small = c.pick(9, 8)
    if arrow:
        c.svg.icon("arrow", right - 10, base - 9, 10, t["muted"], stroke=2.2)
        right -= 15
    c.svg.text(right, base, fit(side.upper(), "mono", small, c.w * 0.34, 1.4), "mono", small, t["muted"], tracking=1.4, anchor="end")


def header_row(name, kicker_text, title, side, side_href, anchor, bars=False):
    return Row(name, 55, 52, [
        Cell(Card(style="none"), 1, side_href or f"#{anchor}", side if side_href else title, f"{kicker_text}: {title}",
             lambda c: header(c, kicker_text, title, side, bool(side_href), bars), key="head"),
    ])


# ── projects ─────────────────────────────────────────────────────────────────


def project_body(c, project, featured):
    svg, t = c.svg, c.t
    x0 = c.x
    illustrated = featured and project["icon"] == "presentation"
    pad = c.pick(22, 14) if featured else c.pick(18, 12)
    icon_box = c.pick(36, 30) if featured else c.pick(30, 26)
    svg.glass(x0 + pad, pad, icon_box, icon_box, icon_box * 0.3)
    svg.icon(project["icon"], x0 + pad + icon_box * 0.25, pad + icon_box * 0.25, icon_box * 0.5, t["ink"])
    text_w = c.w - 2 * pad
    if illustrated:
        mock_w, mock_h = c.pick(206, 124), c.pick(132, 98)
        mock_x = x0 + c.w - pad - mock_w
        window_mock(svg, mock_x, c.pick(20, 48), mock_w, mock_h, project["hue"])
        text_w = mock_x - x0 - pad - c.pick(28, 10)
    else:
        arrow = c.pick(24, 20)
        arrow_button(c, x0 + c.w - pad - arrow, pad, arrow)
    if featured:
        size, name = shrink(project["name"], "display", c.pick(24, 18), text_w, 0.75, -0.6)
        base, fs, lh, lines, y = c.pick(96, 72), c.pick(13.5, 12.5), c.pick(19, 16.5), c.pick(2, 4), c.pick(120, 92)
    else:
        size, name = shrink(project["name"], "display", c.pick(16.5, 14.5), text_w, 0.75, -0.4)
        base, fs, lh, lines, y = c.pick(76, 62), c.pick(12.5, 12), c.pick(17.5, 16), c.pick(3, 6), c.pick(97, 80)
    svg.text(x0 + pad - 1, base, name, "display", size, t["ink"], tracking=-0.5)
    for line in FACES["text"].wrap(project["note"], fs, text_w, lines):
        svg.text(x0 + pad, y, line, "text", fs, t["dim"])
        y += lh


def project_meta(project, featured, login):
    """The linked stats under a project card: (label, value, mark, url, tooltip)."""
    url = project["url"]
    name = project["name"]
    found = []
    if project.get("stars"):
        found.append(("Stars", compact(project["stars"]), {"star": True}, f"{url}/stargazers", f"Who starred {name}"))
    if project.get("downloads"):
        found.append(("Downloads", compact(project["downloads"]), {"icon": "download"}, f"{url}/releases", f"All {name} releases"))
    if project.get("version"):
        found.append(("Latest", project["version"], {"icon": "tag"}, f"{url}/releases/latest", f"Latest {name} release"))
    if project.get("forks"):
        found.append(("Forks", compact(project["forks"]), {"icon": "fork"}, f"{url}/forks", f"Forks of {name}"))
    if project.get("language"):
        language = project["language"]
        found.append(("Language", language, {"dot": project.get("language_color", "#9CA3AF")},
                      f"https://github.com/{login}?tab=repositories&language={urllib.parse.quote(language.lower())}",
                      f"My other {language} projects"))
    found.append(("Source", "Code", {"icon": "code"}, url, f"Browse the {name} source"))
    return found[: 4 if featured else 2]


def meta_cells(card, project, featured, login):
    stats = project_meta(project, featured, login)
    return [
        Cell(card, 1 / len(stats), url, tip, f"{label}: {value}",
             lambda c, label=label, value=value, extra=extra: meta_stat(c, value, label, **extra), key=label.lower())
        for label, value, extra, url, tip in stats
    ]


def project_rows(projects, login):
    rows = []
    if not projects:
        return rows
    first, rest = projects[0], projects[1:]
    card = Card(first["hue"], blobs=blobs_for(0))
    rows.append(Row("work-1", 166, 160, [Cell(card, 1, first["url"], f'Open {first["name"]} on GitHub',
                                              f'{first["name"]}: {first["note"]}', lambda c, pr=first: project_body(c, pr, True))]))
    rows.append(Row("work-1-meta", 50, 56, meta_cells(card, first, True, login), space=True))
    pairs = [rest[i:i + 2] for i in range(0, len(rest), 2)]
    for n, pair in enumerate(pairs, 2):
        solo = len(pair) == 1
        cards = [Card(pr["hue"], blobs=blobs_for(i + n)) for i, pr in enumerate(pair)]
        bodies = [
            Cell(card, 1, pr["url"], f'Open {pr["name"]} on GitHub', f'{pr["name"]}: {pr["note"]}',
                 lambda c, pr=pr: project_body(c, pr, solo))
            for card, pr in zip(cards, pair)
        ]
        rows.append(Row(f"work-{n}", 166 if solo else 128, 160 if solo else 138, bodies))
        metas = []
        for card, pr in zip(cards, pair):
            metas += meta_cells(card, pr, solo, login)
        rows.append(Row(f"work-{n}-meta", 50, 56, metas, space=True))
    return rows


# ── highlights ───────────────────────────────────────────────────────────────


# A real arm64 prologue and epilogue, as Ghidra would list it: address, bytes, instruction.
DISASM = (
    "100003f40  fd 7b bf a9  stp   x29, x30, [sp, #-0x10]!",
    "100003f44  fd 03 00 91  mov   x29, sp",
    "100003f48  00 00 00 90  adrp  x0, 0x100003000",
    "100003f4c  00 e0 3e 91  add   x0, x0, #0xfb8",
    "100003f50  05 00 00 94  bl    _puts",
    "100003f54  00 00 80 52  mov   w0, #0x0",
    "100003f58  fd 7b c1 a8  ldp   x29, x30, [sp], #0x10",
    "100003f5c  c0 03 5f d6  ret",
)


def disasm(svg, x, y, w, h, size):
    step = size * 1.55
    for i in range(int(h // step)):
        line = DISASM[i % len(DISASM)]
        svg.text(x, y + i * step, fit(line, "mono", size, w), "mono", size, (svg.t["ink"], 0.07))


def highlight(c, item, n):
    svg, t = c.svg, c.t
    if item.get("texture") == "disasm":
        clip = svg.uid("asm")
        svg.defs.append(f'<clipPath id="{clip}"><rect x="{num(c.x)}" y="0" width="{num(c.w)}" height="{num(c.h)}" '
                        f'rx="{c.r}"/></clipPath>')
        svg.add(f'<g clip-path="url(#{clip})">')
        disasm(svg, c.x + c.pick(14, 9), c.pick(18, 14), c.w - c.pick(20, 12), c.h - 10, c.pick(7.5, 6.5))
        svg.add("</g>")
    elif item.get("texture") == "hex":
        clip = svg.uid("hex")
        svg.defs.append(f'<clipPath id="{clip}"><rect x="{num(c.x)}" y="0" width="{num(c.w)}" height="{num(c.h)}" '
                        f'rx="{c.r}"/></clipPath>')
        svg.add(f'<g clip-path="url(#{clip})">')
        hexdump(svg, c.x + 10, 16, c.w - 14, c.h - 14, item["title"], size=c.pick(8, 7))
        svg.add("</g>")
    pad = c.pick(16, 11)
    face, track = ("mono", 0) if item["value"].lower().startswith("0x") else ("display", -0.6)
    if c.m:
        size, value = shrink(item["value"], face, 20 if face == "display" else 16, c.w - 2 * pad, 0.7, track)
        svg.text(c.x + pad - 1, 36, value, face, size, t["ink"], tracking=track)
        y = 56
        for line in FACES["semi"].wrap(item["title"], 11.5, c.w - 2 * pad, 2):
            svg.text(c.x + pad, y, line, "semi", 11.5, t["dim"])
            y += 14
        return
    tag = f"B{n}"
    tag_w = FACES["mono"].width(tag, 8, 1) + 14
    svg.glass(c.x + c.w - pad - tag_w, 14, tag_w, 18, 9)
    svg.text(c.x + c.w - pad - tag_w / 2, 26, tag, "mono", 8, t["dim"], tracking=1, anchor="middle")
    size, value = shrink(item["value"], face, 30 if face == "display" else 24, c.w - 2 * pad - tag_w - 6, 0.7,
                         -1 if face == "display" else 0)
    svg.text(c.x + pad - 1, 48, value, face, size, t["ink"], tracking=-1 if face == "display" else 0)
    svg.text(c.x + pad, 70, fit(item["title"], "semi", 13, c.w - 2 * pad), "semi", 13, t["ink"])
    y = 88
    for line in FACES["text"].wrap(item["note"], 11.5, c.w - 2 * pad, 2):
        svg.text(c.x + pad, y, line, "text", 11.5, t["dim"])
        y += 15


# ── charts ───────────────────────────────────────────────────────────────────


def activity_head(c, stats, three_d):
    svg, t = c.svg, c.t
    pad = c.pick(22, 14)
    total = stats.get("contributions", 0)
    y = c.pick(28, 25)
    kicker(c, c.x + pad, y, "Activity")
    weeks = stats["calendar"][-c.pick(53, 26):]
    right = c.pick("Last 12 months", "26 weeks") + (c.pick(" · View in 3D", " · 3D") if three_d else "")
    rx = c.x + c.w - pad
    if three_d:
        svg.icon("arrow", rx - 9, y - 8.5, 9, t["faint"], stroke=2.4)
        rx -= 13
    svg.text(rx, y, right.upper(), "mono", c.pick(8.5, 8), t["faint"], tracking=1.2, anchor="end")
    svg.text(c.x + pad - 1, c.pick(54, 50), f"{total:,} contributions", "display", c.pick(20, 17), t["ink"], tracking=-0.5)
    colors = heat_colors(svg.theme)
    cell, step = c.pick(9, 10), c.pick(11.6, 13)
    labels = c.pick(26, 22)
    gx = c.x + pad + labels + (c.w - 2 * pad - labels - len(weeks) * step) / 2
    gy = c.pick(84, 74)
    peak = max([n for week in weeks for _, n in week] + [1])
    last_month = None
    tiny = 7.5
    for wi, week in enumerate(weeks):
        for day, count in week:
            weekday = date.fromisoformat(day).isoweekday() % 7
            fill = paint(t["heat"]) if count == 0 else f'fill="{colors[max(1, min(4, math.ceil(4 * count / peak)))]}"'
            svg.add(f'<rect x="{num(gx + wi * step)}" y="{num(gy + weekday * step)}" width="{num(cell)}" '
                    f'height="{num(cell)}" rx="2" {fill}/>')
        month = date.fromisoformat(week[0][0]).strftime("%b")
        if month != last_month:
            if wi and wi < len(weeks) - 2:
                svg.text(gx + wi * step, gy - 7, month.upper(), "mono", tiny, t["faint"], tracking=0.6)
            last_month = month
    for wd, name in ((1, "MON"), (3, "WED"), (5, "FRI")):
        svg.text(c.x + pad, gy + wd * step + cell - 1.5, name, "mono", tiny, t["faint"], tracking=0.4)
    ly = gy + 7 * step + 8
    lx = c.x + c.w - pad - 5 * step - c.pick(28, 26)
    svg.text(lx - 6, ly + cell - 1.5, "LESS", "mono", tiny, t["faint"], tracking=0.6, anchor="end")
    for i in range(5):
        fill = paint(t["heat"]) if i == 0 else f'fill="{colors[i]}"'
        svg.add(f'<rect x="{num(lx + i * step)}" y="{num(ly)}" width="{num(cell)}" height="{num(cell)}" rx="2" {fill}/>')
    svg.text(lx + 5 * step + 3, ly + cell - 1.5, "MORE", "mono", tiny, t["faint"], tracking=0.6)
    footer_text = [f'{stats.get("active_days", 0)} ACTIVE DAYS']
    if stats.get("repos_contributed") is not None and not c.m:
        footer_text.append(f'{stats["repos_contributed"]} REPOS')
    svg.text(c.x + pad, ly + cell - 1.5, " · ".join(footer_text), "mono", tiny, t["faint"], tracking=0.6)


def languages(c, stats):
    """The language bar, with a legend of the top eight under it."""
    svg, t = c.svg, c.t
    pad = c.pick(22, 14)
    langs = stats.get("languages") or []
    kicker(c, c.x + pad, c.pick(26, 24), "Languages")
    if stats.get("original"):
        svg.text(c.x + c.w - pad, c.pick(26, 24), f'ACROSS {stats["original"]} REPOS', "mono", c.pick(8.5, 8),
                 t["faint"], tracking=1.2, anchor="end")
    bar_w = c.w - 2 * pad
    bx, by, bh = c.x + pad, c.pick(38, 36), 8
    clip = svg.uid("bar")
    svg.defs.append(f'<clipPath id="{clip}"><rect x="{num(bx)}" y="{by}" width="{num(bar_w)}" height="{bh}" rx="4"/></clipPath>')
    parts = [f'<g clip-path="url(#{clip})">', f'<rect x="{num(bx)}" y="{by}" width="{num(bar_w)}" height="{bh}" {paint(t["heat"])}/>']
    offset = 0
    for _, share, color in langs:
        width = bar_w * share / 100
        parts.append(f'<rect x="{num(bx + offset)}" y="{by}" width="{num(width + 0.5)}" height="{bh}" fill="{color}" fill-opacity=".85"/>')
        offset += width
    svg.add("".join(parts) + "</g>")
    columns = c.pick(4, 3)
    column = bar_w / columns
    size, small = c.pick(12.5, 11.5), c.pick(9, 8.5)
    for i, (name, share, color) in enumerate(langs[:8]):
        x = bx + (i % columns) * column
        y = by + bh + c.pick(26, 24) + (i // columns) * c.pick(24, 22)
        svg.add(f'<circle cx="{num(x + 4)}" cy="{num(y - size * 0.34)}" r="{c.pick(4, 3.5)}" fill="{color}"/>')
        share_text = f"{share:.1f}%"
        right = x + column - c.pick(18, 12)
        width = svg.text(right, y, share_text, "mono", small, t["faint"], anchor="end")
        svg.text(x + 14, y, fit(name, "semi", size, right - width - 8 - x - 14), "semi", size, t["ink"])


def stat_value(value, unit=""):
    """How a number reads on its tile, or None when there's nothing worth showing: it's missing, or zero."""
    if value in (None, "", 0):
        return None
    return (compact(value) if isinstance(value, int) else str(value)) + unit


def balanced(items, most):
    """Splits items into as few rows of at most `most` as possible, filled evenly: six by four become three and three."""
    if not items:
        return []
    count = math.ceil(len(items) / most)
    base, extra = divmod(len(items), count)
    rows, start = [], 0
    for i in range(count):
        size = base + (i < extra)
        rows.append(items[start:start + size])
        start += size
    return rows


def stat_rows(name, card, entries, most, d, m, size=None):
    """Tiles for the numbers that have something to show, in even rows. An entry is
    (label, short label, value, unit, icon, url, tooltip)."""
    shown = [(entry, stat_value(entry[2], entry[3])) for entry in entries]
    shown = [(entry, value) for entry, value in shown if value is not None]
    groups = balanced(shown, most)
    rows = []
    for gi, group in enumerate(groups):
        cells = []
        for (label, short, _, _, icon, url, tip), value in group:
            cells.append(Cell(card, 1, url, tip, f"{label}: {value}",
                              lambda c, value=value, label=label, short=short, icon=icon:
                              big_stat(c, value, c.pick(label, short), icon=None if icon == "star" else icon,
                                       star=icon == "star", size=size and c.pick(*size)),
                              key=short.split(" ")[0].lower()))
        rows.append(Row(f"{name}-{gi + 1}", d, m, cells, space=gi == len(groups) - 1))
    return rows


def chart_rows(stats, login, since, skyline_url):
    rows = []
    profile = f"https://github.com/{login}"
    year_ago = (date.today() - timedelta(days=365)).isoformat()
    if stats.get("calendar"):
        card = Card("blue", blobs=[(0.0, 0.0, 0.5, 2, 0.8), (1.0, 1.0, 0.5, 0, 0.75), (0.7, -0.1, 0.3, 1, 0.5)])
        rows.append(Row("activity", 188, 186, [Cell(card, 1, skyline_url or f"{profile}?tab=overview",
                                                     "Spin this year in 3D" if skyline_url else "My contribution graph",
                                                     f'{stats.get("contributions", 0)} contributions in the last year',
                                                     lambda c: activity_head(c, stats, bool(skyline_url)))]))
        best = stats.get("best_day") or ""
        best_label = date.fromisoformat(best).strftime("%b %-d") if best else ""
        activity = [
            ("Commits", "Commits", stats.get("commits"), "", "commit", search(f"author:{login} committer-date:>{year_ago}", "commits"), "My commits this year"),
            ("Pull requests", "PRs", stats.get("prs"), "", "merge", search(f"author:{login} type:pr created:>{year_ago}", "pullrequests"), "My pull requests this year"),
            ("Issues", "Issues", stats.get("issues"), "", "issue", search(f"author:{login} type:issue created:>{year_ago}", "issues"), "Issues I opened this year"),
            ("Reviews", "Reviews", stats.get("reviews"), "", "eye", search(f"reviewed-by:{login} type:pr created:>{year_ago}", "pullrequests"), "Pull requests I reviewed"),
            ("Current streak", "Streak", stats.get("streak"), "d", "flame", f"{profile}?tab=overview", "Days in a row with a contribution"),
            ("Longest streak", "Longest", stats.get("longest"), "d", "flame", f"{profile}?tab=overview", "Longest run this year"),
            ("Active days", "Active", stats.get("active_days"), "", "calendar", f"{profile}?tab=overview", "Days with at least one contribution"),
            (f"Best day · {best_label}" if best_label else "Best day", f"Best · {best_label}" if best_label else "Best day",
             stats.get("best_count"), "", "spark",
             f"{profile}?tab=overview&from={best}&to={best}" if best else f"{profile}?tab=overview", "My busiest day this year"),
        ]
        rows += stat_rows("activity", card, activity, 4, 54, 56)

    joined = stats.get("joined") or ""
    years = None
    if joined:
        start = datetime.fromisoformat(joined.replace("Z", "+00:00"))
        years = int((datetime.now(timezone.utc) - start).days // 365.25)
    popularity = [
        ("Profile views", "Views", stats.get("views"), "", "eye", profile, "This page's view counter"),
        ("Stars earned", "Stars", stats.get("stars"), "", "star", f"{profile}?tab=repositories&sort=stargazers", "My repositories by stars"),
        ("Followers", "Followers", stats.get("followers"), "", "users", f"{profile}?tab=followers", "Who follows me"),
        ("Merged PRs", "Merged PRs", stats.get("merged_prs"), "", "merge", search(f"author:{login} type:pr is:merged", "pullrequests"), "My merged pull requests"),
        ("Forks of my repos", "Forks", stats.get("forks"), "", "fork", f"{profile}?tab=repositories", "My repositories"),
        ("Contributed to", "Contributed", stats.get("contributed_to"), "", "repo", search(f"author:{login} -user:{login} type:pr", "pullrequests"), "Pull requests to other people's projects"),
        ("Years on GitHub", f"Since {since}" if since else "On GitHub", years, " yrs", "clock", profile, f"On GitHub since {since}"),
        ("All-time contributions", "All-time", stats.get("all_time"), "", "chart", f"{profile}?tab=overview", "Every contribution since I joined"),
        ("Busiest day of the week", "Busiest day", stats.get("busiest"), "", "calendar", f"{profile}?tab=overview", "The weekday I code the most"),
    ]
    card = Card("rose", blobs=[(0.95, 0.05, 0.5, 0, 0.9), (0.05, 0.95, 0.5, 1, 0.7), (0.5, 0.5, 0.3, 2, 0.35)])
    rows += stat_rows("popularity", card, popularity, 3, 58, 58, size=(21, 17))

    langs = stats.get("languages") or []
    if langs:
        card = Card("teal", blobs=[(0.05, 0.0, 0.5, 0, 0.9), (1.0, 1.0, 0.45, 1, 0.75), (0.6, 0.3, 0.3, 2, 0.4)])
        lines = {"d": math.ceil(min(len(langs), 8) / 4), "m": math.ceil(min(len(langs), 8) / 3)}
        rows.append(Row("languages", 64 + 24 * lines["d"], 62 + 22 * lines["m"], [
            Cell(card, 1, f"{profile}?tab=repositories", "All my repositories",
                 "Languages: " + ", ".join(f"{n} {s:.0f}%" for n, s, _ in langs), lambda c: languages(c, stats)),
        ], space=True))
    return rows


def skyline(calendar):
    """The contribution calendar as a 3D city: one tower per active day, on a base plate. ASCII STL."""
    weeks = calendar[-53:]
    peak = max([n for week in weeks for _, n in week] + [1])
    pitch, side = 10, 8
    facets = []

    def quad(a, b, c, d, normal):
        facets.append((normal, a, b, c))
        facets.append((normal, a, c, d))

    def box(x0, y0, z0, x1, y1, z1, bottom=False):
        quad((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1), (0, 0, 1))
        quad((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1), (0, -1, 0))
        quad((x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1), (1, 0, 0))
        quad((x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (0, 1, 0))
        quad((x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (-1, 0, 0))
        if bottom:
            quad((x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (0, 0, -1))

    box(-6, -6, -4, len(weeks) * pitch + 4, 7 * pitch + 4, 0, bottom=True)
    for wi, week in enumerate(weeks):
        for day, count in week:
            if not count:
                continue
            row = 6 - date.fromisoformat(day).isoweekday() % 7
            height = round(6 + 104 * (count / peak) ** 0.55)
            box(wi * pitch, row * pitch, 0, wi * pitch + side, row * pitch + side, height)

    def vertex(p):
        return "vertex " + " ".join(str(v) for v in p)

    body = "\n".join(
        f"facet normal {' '.join(map(str, n))}\nouter loop\n{vertex(a)}\n{vertex(b)}\n{vertex(c)}\nendloop\nendfacet"
        for n, a, b, c in facets
    )
    return f"solid contributions\n{body}\nendsolid contributions\n"


# ── music ────────────────────────────────────────────────────────────────────


def track_cell(c, track, n, value, label):
    """A track with its cover, and how often I played it on the right."""
    svg, t = c.svg, c.t
    art = c.pick(30, 32)
    if c.m:
        ax = c.x + 10
    else:
        svg.text(c.x + 18, c.h / 2 + 3.2, f"{n:02d}", "mono", 9, t["faint"], tracking=0.4)
        ax = c.x + 42
    artwork(svg, ax, (c.h - art) / 2, art, track.get("cover"), track["name"], r=6)
    tx = ax + art + c.pick(12, 9)
    right = c.x + c.w - c.pick(18, 11)
    size = c.pick(13.5, 12)
    svg.text(right, c.h / 2 - 1, value, "semi", size, t["ink"], anchor="end")
    svg.text(right, c.h / 2 + 12, label.upper(), "mono", 7.5, t["faint"], tracking=1, anchor="end")
    meta = max(FACES["semi"].width(value, size), FACES["mono"].width(label, 7.5, 1))
    room = right - meta - c.pick(18, 10) - tx
    if c.m:
        lines = FACES["semi"].wrap(track["name"], 12, room, 2)
        y = c.h / 2 + (4.3 if len(lines) == 1 else -3)
        for line in lines:
            svg.text(tx, y, line, "semi", 12, t["ink"])
            y += 14.5
        return
    sub = ""
    if track.get("ms"):
        minutes, seconds = divmod(round(track["ms"] / 1000), 60)
        sub = f"{minutes}:{seconds:02d}"
    if sub:
        svg.text(tx, c.h / 2 - 1.5, fit(track["name"], "semi", 13.5, room), "semi", 13.5, t["ink"])
        svg.text(tx, c.h / 2 + 12.5, sub, "mono", 8, t["faint"], tracking=0.8)
    else:
        svg.text(tx, c.h / 2 + 4.8, fit(track["name"], "semi", 13.5, room), "semi", 13.5, t["ink"])


def artist_cell(c, name):
    svg, t = c.svg, c.t
    pad = c.pick(16, 10)
    if c.m:
        svg.text(c.x + pad, 19, "ARTIST", "mono", 7.5, t["faint"], tracking=1)
        y = 34
        for line in FACES["semi"].wrap(name, 11.5, c.w - 2 * pad, 2):
            svg.text(c.x + pad, y, line, "semi", 11.5, t["ink"])
            y += 13.5
        return
    svg.text(c.x + pad, c.h / 2 - 3.5, "ARTIST", "mono", 7.5, t["faint"], tracking=1.2)
    svg.text(c.x + pad, c.h / 2 + 11, fit(name, "text", 12.5, c.w - 2 * pad), "text", 12.5, t["ink"])


def rotation_rows(tracks):
    rows = []
    card = Card("green", blobs=[(1.0, -0.05, 0.55, 0, 0.9), (0.0, 1.05, 0.5, 1, 0.7), (0.65, 0.6, 0.3, 2, 0.4)])
    for n, track in enumerate(tracks, 1):
        url = track.get("url") or track.get("plays_url") or ""
        artist_url = track.get("artist_url") or url
        plays = track.get("plays")
        if plays:
            value, label = str(plays), "Plays"
        elif track.get("ms"):
            minutes, seconds = divmod(round(track["ms"] / 1000), 60)
            value, label = f"{minutes}:{seconds:02d}", "Length"
        else:
            value, label = f"#{n}", "Rank"
        rows.append(Row(f"rotation-{n}", 46, 56, [
            Cell(card, 0.7, url, f'{track["name"]} by {track["artist"]}', f'{n}. {track["name"]}, {value} {label.lower()}',
                 lambda c, track=track, n=n, value=value, label=label: track_cell(c, track, n, value, label), key="track"),
            Cell(card, 0.3, artist_url, f'More from {track["artist"]}', track["artist"],
                 lambda c, name=track["artist"]: artist_cell(c, name), key="artist"),
        ], space=n == len(tracks)))
    return rows


# ── credits ──────────────────────────────────────────────────────────────────


TOOL_URLS = {
    "swift": "https://www.swift.org",
    "swiftui": "https://developer.apple.com/xcode/swiftui/",
    "appkit": "https://developer.apple.com/documentation/appkit",
    "uikit": "https://developer.apple.com/documentation/uikit",
    "swiftdata": "https://developer.apple.com/xcode/swiftdata/",
    "typescript": "https://www.typescriptlang.org",
    "javascript": "https://developer.mozilla.org/docs/Web/JavaScript",
    "react": "https://react.dev",
    "vite": "https://vite.dev",
    "tailwind": "https://tailwindcss.com",
    "docker": "https://www.docker.com",
    "nginx": "https://nginx.org",
    "ansible": "https://www.ansible.com",
    "xcode": "https://developer.apple.com/xcode/",
    "vs code": "https://code.visualstudio.com",
    "ghidra": "https://ghidra-sre.org",
    "ida pro": "https://hex-rays.com/ida-pro",
    "apple silicon": "https://www.apple.com/mac/",
    "arm64": "https://developer.arm.com/Architectures/A-Profile%20Architecture",
    "spotify": "https://open.spotify.com",
    "youtube music": "https://music.youtube.com",
    "apple music": "https://music.apple.com",
    "python": "https://www.python.org",
    "kotlin": "https://kotlinlang.org",
    "rust": "https://www.rust-lang.org",
    "go": "https://go.dev",
}


def credit_cell(c, label, values):
    svg, t = c.svg, c.t
    pad = c.pick(20, 12)
    room = c.w - 2 * pad
    if c.m:
        svg.text(c.x + pad, 20, fit(label.upper(), "mono", 7.5, room, 1.2), "mono", 7.5, t["faint"], tracking=1.2)
        y = 36
        for line in FACES["semi"].wrap(" · ".join(values), 11.5, room, 2):
            svg.text(c.x + pad, y, line, "semi", 11.5, t["ink"])
            y += 14
        return
    svg.text(c.x + pad, c.h / 2 - 4, fit(label.upper(), "mono", 8, room, 1.2), "mono", 8, t["faint"], tracking=1.2)
    svg.text(c.x + pad, c.h / 2 + 12, fit(" · ".join(values), "semi", 12.5, room), "semi", 12.5, t["ink"])


def credit_rows(items, urls, anchor):
    rows = []
    card = Card("graphite", blobs=[(0.0, 0.0, 0.55, 0, 0.7), (1.0, 1.0, 0.55, 2, 0.6), (0.7, 0.4, 0.3, 1, 0.35)])
    lookup = {**TOOL_URLS, **{k.lower(): v for k, v in (urls or {}).items()}}
    pairs = [items[i:i + 2] for i in range(0, len(items), 2)]
    for n, pair in enumerate(pairs, 1):
        cells = []
        for item in pair:
            values = [v.strip() for v in item["value"].split(",") if v.strip()]
            url = next((lookup[v.lower()] for v in values if v.lower() in lookup), None)
            text = f'{item["label"]}: {", ".join(values)}'
            cells.append(Cell(card, 1, url or anchor, text, text, lambda c, label=item["label"], values=values: credit_cell(c, label, values)))
        if len(cells) == 1:
            cells.append(Cell(card, 1, anchor, "", "", lambda c: None))
        rows.append(Row(f"credits-{n}", 50, 60, cells, space=n == len(pairs)))
    return rows


# ── the rest ─────────────────────────────────────────────────────────────────


def repo_cell(c, repo):
    """A repository: its name and description, with language, stars and last push on the right."""
    svg, t = c.svg, c.t
    pad = c.pick(18, 11)
    room = c.w - 2 * pad
    language = repo.get("language") or ""
    stars = repo.get("stars", 0)
    pushed = when_label(repo.get("pushed"))
    meta_w = 0
    if not c.m:
        x = c.x + c.w - pad
        if language:
            width = svg.text(x, 22, fit(language.upper(), "mono", 8, room * 0.3, 1), "mono", 8, t["faint"], tracking=1, anchor="end")
            svg.add(f'<circle cx="{num(x - width - 7)}" cy="19.2" r="3.2" fill="{repo.get("language_color", "#9CA3AF")}"/>')
            x -= width + 16
        if stars:
            width = svg.text(x, 22, str(stars), "mono", 8, t["faint"], anchor="end")
            mark(c, x - width - 12, 22.5, 10, star=True)
            x -= width + 18
        if pushed and x - (c.x + pad) > room * 0.55:
            width = svg.text(x, 22, pushed, "mono", 8, t["faint"], tracking=1, anchor="end")
            x -= width + 12
        meta_w = c.x + c.w - pad - x
    size, name = shrink(repo["name"], "semi", c.pick(13, 12), room - meta_w - 8, 0.85)
    svg.text(c.x + pad, c.pick(23, 21), name, "semi", size, t["ink"])
    description = " ".join((repo.get("description") or "No description yet.").split())
    if c.m:
        y = 36
        for line in FACES["text"].wrap(description, 10.5, room, 2):
            svg.text(c.x + pad, y, line, "text", 10.5, t["dim"])
            y += 13
        return
    svg.text(c.x + pad, 40, fit(description, "text", 11.5, room), "text", 11.5, t["dim"])


def repo_all(c, total):
    svg, t = c.svg, c.t
    label = f"Browse all {total} repositories" if total else "Browse all repositories"
    size, label = shrink(label, "semi", c.pick(12.5, 11.5), c.w - 50, 0.85)
    width = FACES["semi"].width(label, size) + 18
    x = c.x + (c.w - width) / 2
    svg.text(x, c.h / 2 + size * 0.36, label, "semi", size, t["ink"])
    svg.icon("arrow", x + width - 11, c.h / 2 - 5.5, 11, t["dim"], stroke=2.2)


def repo_rows(repos, login, total):
    """My other repositories, latest push first, two to a row, ending with a way to every repository."""
    card = Card("graphite", blobs=[(0.0, 0.0, 0.55, 0, 0.6), (1.0, 1.0, 0.5, 2, 0.5), (0.5, 0.5, 0.35, 1, 0.3)])
    everything = f"https://github.com/{login}?tab=repositories"
    cells = [
        Cell(card, 1, repo["url"], f'Open {repo["name"]} on GitHub', f'{repo["name"]}: {repo.get("description") or ""}'.strip(": "),
             lambda c, repo=repo: repo_cell(c, repo), key=repo["name"].lower()[:40])
        for repo in repos
    ]
    cells.append(Cell(card, 1, everything, "All my repositories", "Browse all repositories",
                      lambda c: repo_all(c, total), key="all"))
    rows = []
    for n, i in enumerate(range(0, len(cells), 2), 1):
        pair = cells[i:i + 2]
        rows.append(Row(f"repos-{n}", 54 if len(pair) == 2 else 44, 62 if len(pair) == 2 else 44, pair,
                        space=i + 2 >= len(cells)))
    return rows


def footer(c, name):
    t = c.t
    size = c.pick(8, 7.5)
    y = c.pick(26, 24)
    left = "SET IN BRICOLAGE GROTESQUE & GEIST MONO" if not c.m else "BRICOLAGE GROTESQUE & GEIST MONO"
    c.svg.text(c.x + 2, y, left, "mono", size, t["muted"], tracking=1.2)
    right = c.x + c.w - 2
    c.svg.icon("up", right - 9, y - 8, 9, t["muted"], stroke=2.2)
    text = f"© {datetime.now(timezone.utc).year} {name} · Back to top" if not c.m else "Top"
    c.svg.text(right - 13, y, text.upper(), "mono", size, t["muted"], tracking=1.2, anchor="end")


def page(p, data, hrefs, skyline_url=None):
    """Everything on the profile, top to bottom: rows of cells, anchors and the list of other projects."""
    me = p["me"]
    login = me["github"]
    profile = f"https://github.com/{login}"
    projects, recent, stats, tracks = data["projects"], data["recent"], data["stats"], data["tracks"]
    since = data.get("since", "")
    items = []

    home = projects[0]["url"] if projects else profile
    items += hero_rows(p, data["now"], hrefs, home)

    if projects:
        repos = data.get("repo_count")
        items.append(header_row("side-a", "Side A", p["work"]["title"], f"All {repos} repos" if repos else "All repos",
                                f"{profile}?tab=repositories", "work"))
        items += project_rows(projects, login)
    if recent:
        title = p.get("bsides", {}).get("title", "Fresh from the studio")
        items.append(header_row("b-sides", "B-sides", title, "Latest pushes", f"{profile}?tab=repositories&sort=updated", "work"))
        items += repo_rows(recent, login, data.get("repo_count"))
    highlights = p.get("highlights", {}).get("items", [])
    if highlights:
        items.append(header_row("side-b", "Side B", p["highlights"]["title"], f"{len(highlights):02d} tracks", None, "work"))
        cards = [Card(item.get("hue") or ("ember", "teal", "rose")[i % 3], style="tinted", blobs=blobs_for(i + 1))
                 for i, item in enumerate(highlights)]
        items.append(Row("highlights", 118, 96, [
            Cell(card, 1, item.get("url") or f"{profile}?tab=repositories", item.get("tip") or item["title"],
                 f'{item["value"]}. {item["title"]}: {item["note"]}', lambda c, item=item, n=n: highlight(c, item, n), key=str(n))
            for n, (card, item) in enumerate(zip(cards, highlights), 1)
        ], space=True))

    if stats:
        items.append(header_row("charts", "Charts", "Activity & popularity", "Updated daily", f"{profile}?tab=overview", "charts"))
        items += chart_rows(stats, login, since, skyline_url)

    if tracks:
        listening = p.get("listening", {})
        scrobbles = data.get("scrobbles")
        lastfm_url = data.get("lastfm_url") or listening.get("profile") or None
        side = f"{compact(scrobbles)} scrobbles" if scrobbles else f'Top tracks · {tracks[0].get("source", "Spotify")}'
        items.append(header_row("rotation", "On rotation", listening.get("title", "On rotation"), side, lastfm_url, "music", bars=True))
        items += rotation_rows(tracks)

    credits = p.get("credits", {})
    if credits.get("items"):
        items.append(header_row("liner-notes", "Credits", credits.get("title", "Liner notes"), "Stack & tools", None, "credits"))
        items += credit_rows(credits["items"], credits.get("urls"), "#credits")

    items.append(Row("footer", 42, 42, [
        Cell(Card(style="none"), 1, "#top", "Back to the top", "Set in Bricolage Grotesque and Geist Mono",
             lambda c: footer(c, me["name"]), key="end"),
    ]))
    return items
