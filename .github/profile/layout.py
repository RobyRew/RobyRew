"""The page as a grid of tiles, one image per link.

GitHub strips CSS and image maps from READMEs, so an image can carry only one link. Every link gets its own tile.
A tile is a card in the palette of the RobyRew sites: a see-through fill, a faint tint in the colour of what it
shows, a sheen at the top and a light rim.

No tile ever touches the edge of its image: wherever two images meet there is clear space. That's on purpose.
When an image lands between two device pixels (at 110 % or 125 % zoom, or on most phones), browsers blend its edge
with the page, and two images painted side by side on one colour show a hairline where they meet. In clear space
there's nothing to blend, so nothing shows at any zoom. `align="top"` on each image removes the gap GitHub would
otherwise leave under each row.

The one exception is a joined card (the top of the page): one card drawn across several images that meet edge to
edge. Each image draws the whole card, fill, tint, sheen and rim, and shows its own part of it, so the card runs on
unbroken from one image to the next. The fill there is see-through and close to the page colour, which keeps a
blended edge at fractional zoom faint. Anything that belongs to one panel only (the aurora behind my name) fades out
before it reaches a seam, so nothing stops dead at the edge of an image.

Every image also has a phone version, drawn at half the width with about the same type sizes. Both share the
README's `width="…%"`, so a row is split the same way on phones and computers; only the heights differ.

Sizes follow GitHub's own interface: titles around 17–26 px, text 12–14 px, labels 7–9 px.
"""

import math
import urllib.parse
from datetime import datetime, timezone

from canvas import (FACES, HUES, PLATFORMS, STAR, SVG, blobs_for, compact, icon_markup, image_data, num, paint,
                    record, render_pair, tonearm, window_mock)


WIDTH = {"d": 840, "m": 420}  # desktop and phone canvases
OUTER = {"d": 16, "m": 13}  # corner radius of a big tile
SMALL = {"d": 12, "m": 10}  # corner radius of a small one
GAP = {"d": 10, "m": 8}  # clear space between two tiles, across or down
SPACE = {"d": 16, "m": 12}  # room under the last row of a group, before the next heading
INSET = 1  # how far tiles stay from the sides of the page, so their rims are never cut
# A row of images can't be shorter than a line of text (24 px), or GitHub pads it. These keep every row above that
# down to a 600 px window for the desktop images and a 340 px phone for the phone ones.
MIN_HEIGHT = {"d": 40, "m": 40}


# ── the tiles ────────────────────────────────────────────────────────────────


class Card:
    """A group of tiles in one colour. Its tint is laid across all of them. A joined card is one card drawn across
    several images: its tiles meet edge to edge, across and down, with nothing between them."""

    def __init__(self, hue="graphite", style="glass", blobs=None, joined=False):
        self.hue, self.style, self.joined = hue, style, joined
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
    """Cells side by side. A row of plain cells (headings, the footer) has no tiles and no gaps. `gap_above` and
    `gap_below` are False where the row carries on a joined card from the row above or into the row below."""

    def __init__(self, name, d, m, cells, space=False, width=100, gap_above=True, gap_below=True):
        self.name, self.h, self.cells, self.space, self.width = name, {"d": d, "m": m}, cells, space, width
        self.gap_above, self.gap_below = gap_above, gap_below
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

    def top(self, v):
        """Clear space above the tiles: half a gap, or none where the row carries on the card above."""
        return GAP[v] / 2 if self.tiled and self.gap_above else 0

    def height(self, v):
        below = SPACE[v] if self.space else (GAP[v] / 2 if self.tiled and self.gap_below else 0)
        return self.top(v) + self.h[v] + below

    def tile(self, cell, v):
        """A tile's left and right edges: half a gap in from each neighbour, so the images meet in clear space.
        Panels of a joined card meet edge to edge instead."""
        x0, x1 = cell.f0 * WIDTH[v], cell.f1 * WIDTH[v]
        if not self.tiled:
            return x0, x1
        inner = 0 if cell.card.joined else GAP[v] / 2
        return x0 + (inner if cell.f0 > 1e-9 else INSET), x1 - (inner if cell.f1 < 1 - 1e-9 else INSET)

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
    """What a cell's drawing function gets: the canvas, and its tile on it (y from the tile's top, corner radius r).
    `shape` is the outline to clip decorations to: the tile's own, or the whole joined card's. `open` names the
    sides where a joined card runs on into another image."""

    def __init__(self, svg, v, x, w, h, r, shape=None, open=()):
        self.svg, self.t, self.v, self.m = svg, svg.t, v, v == "m"
        self.x, self.w, self.h, self.r = x, w, h, r
        self.shape = shape or rounded(x, 0, w, h, r)
        self.open = set(open)

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
    gap = 0 if card.joined else GAP[v]
    total, mine = 0, 0
    for r in card.rows:
        if r is row:
            mine = total
        total += r.h[v] + gap
    return mine, total - gap


def card_outline(row, card, v):
    """A joined card's whole outline, as (x, y, w, h) with y from the top of this row's image."""
    gx0, gx1 = row.extent(card, v)
    offset, full = card_frame(card, row, v)
    return gx0, row.top(v) - offset, gx1 - gx0, full


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
    """The card: a see-through fill, the group's tint, a sheen at the top, a light rim and, in light mode, a soft
    shadow underneath. All of it stays inside the image, clear of its edges."""
    card = cell.card
    if card.style == "none":
        return
    if card.joined:
        joined_background(svg, row, cell, v)
        return
    t = svg.t
    x0, x1 = row.tile(cell, v)
    y0, w, h = row.top(v), x1 - x0, row.h[v]
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


def joined_background(svg, row, cell, v):
    """One panel of a joined card. The whole card is drawn and the image's frame shows this panel's part of it, so
    fill, tint, sheen and rim carry on into the neighbouring images with no seam drawn."""
    card, t = cell.card, svg.t
    x, y, w, h = card_outline(row, card, v)
    r = OUTER[v]
    colors = HUES.get(card.hue, HUES["graphite"])
    clip = svg.uid("card")
    svg.defs.append(f'<clipPath id="{clip}"><path d="{rounded(x, y, w, h, r)}"/></clipPath>')
    box = f'x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}"'
    parts = [f'<g clip-path="url(#{clip})">', f'<rect {box} {paint(t["card"])}/>']
    for fx, fy, fr, ci, strength in card.blobs:
        grad = svg.uid("blob")
        alpha = min(t["blob"] * strength, 0.9)
        svg.defs.append(
            f'<radialGradient id="{grad}" gradientUnits="userSpaceOnUse" cx="{num(x + fx * w)}" cy="{num(y + fy * h)}" '
            f'r="{num(fr * max(w, h))}"><stop offset="0" stop-color="{colors[ci]}" stop-opacity="{num(alpha)}"/>'
            f'<stop offset=".6" stop-color="{colors[ci]}" stop-opacity="{num(alpha * 0.35)}"/>'
            f'<stop offset="1" stop-color="{colors[ci]}" stop-opacity="0"/></radialGradient>'
        )
        parts.append(f'<rect {box} fill="url(#{grad})"/>')
    sheen = min(h * 0.5, 100)
    color, alpha = t["sheen"]
    fill = vertical(svg, x, y, y + sheen, [(0, color, alpha), (1, color, 0)])
    parts.append(f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(sheen)}" fill="{fill}"/>')
    bottom = row.top(v) + row.h[v]
    parts.append("</g>")
    color, at_top, at_bottom = t["rim"]
    rim = vertical(svg, x, y, y + h, [(0, color, at_top), (0.5, color, (at_top + at_bottom) / 2), (1, color, at_bottom)])
    parts.append(f'<path d="{rounded(x + 0.5, y + 0.5, w - 1, h - 1, r - 0.5)}" fill="none" stroke="{rim}"/>')
    below = row.height(v) - bottom
    if t["shadow"] and card.rows[-1] is row and below > 2:
        depth = min(below - 1.5, SPACE[v] * 0.7)
        fill = vertical(svg, x, bottom, bottom + depth, [(0, "#000000", t["shadow"]), (1, "#000000", 0)])
        parts.append(f'<rect x="{num(x + r * 0.7)}" y="{num(bottom)}" width="{num(w - 1.4 * r)}" height="{num(depth)}" fill="{fill}"/>')
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
    pad = row.top(v)
    shape, open = None, []
    if cell.card.joined:
        x, y, w, h = card_outline(row, cell.card, v)
        shape = rounded(x, y - pad, w, h, OUTER[v])
        open = [side for side, runs_on in (("left", cell.f0 > 1e-9), ("right", cell.f1 < 1 - 1e-9),
                                            ("top", cell.card.rows[0] is not row), ("bottom", cell.card.rows[-1] is not row))
                if runs_on]
    if pad:
        svg.add(f'<g transform="translate(0 {num(pad)})">')
    cell.draw(Ctx(svg, v, tx0, tx1 - tx0, row.h[v], row.radius(v), shape, open))
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


def centered_block(h, first, gap, second):
    """Baselines for a big line over a small line, centred in a cell of height h."""
    block = first * 0.72 + gap + second * 0.72
    top = (h - block) / 2
    return top + first * 0.72, top + first * 0.72 + gap + second * 0.72


def when_label(stamp):
    if not stamp:
        return ""
    try:
        moment = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return ""
    return moment.strftime("%b %-d").upper()


def project_icon(c, project, x, y, size):
    """The project's own icon (icons/ in this folder) when it has one, else a line icon on a glass square."""
    if c.svg.picture(project.get("image"), x, y, size):
        return
    c.svg.glass(x, y, size, size, size * 0.26)
    c.svg.icon(project.get("glyph") or "code", x + size * 0.25, y + size * 0.25, size * 0.5, c.t["ink"])


def meta_line(c, x, y, room, items, dot=None, size=8, lines=1):
    """A project's facts in the label font, after its language's colour dot. With lines=2 they may wrap, and the
    first line moves up so the last one stays on `y`."""
    if not items:
        return
    offset = 0
    if dot:
        c.svg.add(f'<circle cx="{num(x + 3.2)}" cy="{num(y - size * 0.36)}" r="3.2" fill="{dot}"/>')
        offset = 12
    rows = [[]]
    for item in items:
        trial = " · ".join(rows[-1] + [item])
        if rows[-1] and FACES["mono"].width(trial, size, 0.6) > room - offset and len(rows) < lines:
            rows.append([item])
        else:
            rows[-1].append(item)
    for n, row in enumerate(rows):
        baseline = y - (len(rows) - 1 - n) * size * 1.6
        text = fit(" · ".join(row), "mono", size, room - offset, 0.6)
        c.svg.text(x + offset, baseline, text, "mono", size, c.t["faint"], tracking=0.6)


# ── the record player ────────────────────────────────────────────────────────

# One row of two tiles: who I am, and the record player with what's on it, beside the record on computers and under
# it on phones. The record must stay in one image: cut across two, its halves would turn out of step.
HERO = {
    # cx, cy: the record's centre from the tile's top left. info: where what's playing starts, and its right margin.
    "d": {"h": 236, "pad": 26, "cx": 108, "cy": 118, "r": 90, "info": (250, 18)},
    "m": {"h": 214, "pad": 13, "cx": 64, "cy": 64, "r": 50, "info": (13, 12)},
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


def fades(c, reach=0.38):
    """Masks that fade what's inside them out towards each side where the card runs on into another image, so a
    decoration of this panel never stops dead at a seam. Returns the opening and closing tags."""
    svg = c.svg
    opening, closing = "", ""
    for side in sorted(c.open):
        span = reach * (c.w if side in ("left", "right") else c.h)
        x1, y1, x2, y2 = {
            "right": (c.x + c.w - span, 0, c.x + c.w, 0),
            "left": (c.x + span, 0, c.x, 0),
            "bottom": (0, c.h - span, 0, c.h),
            "top": (0, span, 0, 0),
        }[side]
        grad, mask = svg.uid("fg"), svg.uid("fm")
        box = f'x="{num(c.x - 40)}" y="-40" width="{num(c.w + 80)}" height="{num(c.h + 80)}"'
        svg.defs.append(
            f'<linearGradient id="{grad}" gradientUnits="userSpaceOnUse" x1="{num(x1)}" y1="{num(y1)}" x2="{num(x2)}" '
            f'y2="{num(y2)}"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
            f'</linearGradient><mask id="{mask}" maskUnits="userSpaceOnUse" {box}><rect {box} fill="url(#{grad})"/></mask>'
        )
        opening += f'<g mask="url(#{mask})">'
        closing += "</g>"
    return opening, closing


def aurora(c):
    """Three soft lights in the accent's colours, drifting behind the text, slowly, for ever. On a joined card they
    fade out before the seams."""
    svg = c.svg
    clip = svg.uid("aur")
    svg.defs.append(f'<clipPath id="{clip}"><path d="{c.shape}"/></clipPath>')
    dark = svg.theme == "dark"
    strength = 0.26 if dark else 0.13
    colors = ("#7AA2FF", "#6366F1", "#22D3EE") if dark else ("#2563EB", "#7C3AED", "#0EA5E9")
    reach = c.pick(1, 0.55)
    svg.css.append(
        ".au{transform-box:fill-box;transform-origin:center}"
        f".a1{{animation:a1 19s ease-in-out infinite alternate}}@keyframes a1{{to{{transform:translate({num(70 * reach)}px,{num(16 * reach)}px) scale(1.3)}}}}"
        f".a2{{animation:a2 23s ease-in-out infinite alternate}}@keyframes a2{{to{{transform:translate({num(-60 * reach)}px,{num(-14 * reach)}px) scale(.8)}}}}"
        f".a3{{animation:a3 29s ease-in-out infinite alternate}}@keyframes a3{{to{{transform:translate({num(40 * reach)}px,{num(-22 * reach)}px) scale(1.2)}}}}"
    )
    opening, closing = fades(c)
    parts = [f'<g clip-path="url(#{clip})">{opening}']
    for n, (fx, fy, fr, color) in enumerate(((0.18, 0.2, 0.5, colors[0]), (0.85, 0.85, 0.45, colors[1]), (0.6, 0.05, 0.35, colors[2])), 1):
        grad = svg.uid("aug")
        svg.defs.append(f'<radialGradient id="{grad}"><stop offset="0" stop-color="{color}" stop-opacity="{num(strength)}"/>'
                        f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')
        r = fr * c.w
        parts.append(f'<circle class="au a{n}" cx="{num(c.x + fx * c.w)}" cy="{num(fy * c.h)}" r="{num(r)}" fill="url(#{grad})"/>')
    svg.add("".join(parts) + closing + "</g>")


def lively_name(c, x, y, name, size):
    """The name, with a sweep of the accent passing through it now and then."""
    svg, t = c.svg, c.t
    tracking = -size * 0.03
    main, width = svg.text_markup(x, y, name, "display", size, t["ink"], tracking)
    top, height = y - size * 0.78, size * 0.98
    letters, shine = svg.uid("letters"), svg.uid("shine")
    sweep = width * 0.45
    svg.defs.append(
        f'<clipPath id="{letters}">{main}</clipPath>'
        f'<linearGradient id="{shine}"><stop offset="0" stop-color="{t["aside"]}" stop-opacity="0"/>'
        f'<stop offset=".45" stop-color="{t["aside"]}" stop-opacity=".95"/><stop offset=".6" stop-color="{t["accent"]}" stop-opacity=".95"/>'
        f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></linearGradient>'
    )
    svg.css.append(
        f".sweep{{animation:sweep 7s cubic-bezier(.5,0,.3,1) infinite}}"
        f"@keyframes sweep{{0%,64%{{transform:translateX(0)}}100%{{transform:translateX({num(width + sweep)}px)}}}}"
    )
    svg.add(main + f'<g clip-path="url(#{letters})"><rect class="sweep" x="{num(x - sweep)}" y="{num(top - 4)}" '
            f'width="{num(sweep)}" height="{num(height + 8)}" fill="url(#{shine})"/></g>')
    return width


def pulse_text(me, pulse, phone):
    """The line over my name: what I set in profile.toml, or my latest push among the projects on the page."""
    if me.get("now"):
        return me["now"]
    if not pulse:
        return ""
    when = when_label(pulse.get("when"))
    parts = ("Latest push", when) if phone else ("Latest push", pulse.get("name", ""), when)
    return " · ".join(part for part in parts if part)


def identity(c, me, pulse):
    """Who I am: the name over a slow aurora with a sweep of light through it, what I do, and a cursor that's
    still typing."""
    svg, t = c.svg, c.t
    g = HERO[c.v]
    left = c.x + g["pad"]
    room = c.x + c.w - left - g["pad"]
    aurora(c)
    kick = c.pick(8.5, 7)
    size = c.pick(46, 30)
    while size > 20 and FACES["display"].width(me["name"], size, -size * 0.03) > room:
        size -= 1
    rs = c.pick(13.5, 10.5)
    fs, lh = c.pick(13.5, 10.5), c.pick(19, 13.8)
    role = " · ".join(part for part in (me.get("person"), me.get("role")) if part)
    roles = FACES["semi"].wrap(role, rs, room, c.pick(1, 2)) if role else []
    statement = FACES["text"].wrap(me.get("statement", ""), fs, room, c.pick(3, 5))
    aside = FACES["semi"].wrap(me["aside"], fs, room - 8, 2) if me.get("aside") else []
    facts = [] if c.m else me.get("facts", [])
    status = pulse_text(me, pulse, c.m)
    # Baselines laid out from 0, then the block is centred. Each gap runs from a baseline to the next cap height.
    y = kick * 0.72 if status else 0
    status_y = y
    name_y = (y + c.pick(18, 12) if status else 0) + size * 0.74
    y = name_y
    role_ys, text_ys, aside_ys = [], [], []
    for i in range(len(roles)):
        y += (c.pick(20, 13) + rs * 0.72) if i == 0 else rs * 1.32
        role_ys.append(y)
    for i in range(len(statement)):
        y += (c.pick(14, 10) + fs * 0.72) if i == 0 else lh
        text_ys.append(y)
    for i in range(len(aside)):
        y += lh + (1 if i == 0 else 0)
        aside_ys.append(y)
    facts_y = None
    if facts:
        y += c.pick(17, 12) + kick * 0.72
        facts_y = y
    shift = (c.h - y - fs * 0.22) / 2
    if status:
        y = shift + status_y
        cy = y - kick * 0.35
        svg.css.append(".ping{transform-box:fill-box;transform-origin:center;animation:ping 2.4s ease-out infinite}"
                       "@keyframes ping{from{transform:scale(1);opacity:.55}to{transform:scale(3.2);opacity:0}}")
        svg.add(f'<circle class="ping" cx="{num(left + 3)}" cy="{num(cy)}" r="2.6" fill="{t["live"]}"/>'
                f'<circle cx="{num(left + 3)}" cy="{num(cy)}" r="2.6" fill="{t["live"]}"/>')
        svg.text(left + 13, y, fit(status.upper(), "mono", kick, room - 13, 1.4), "mono", kick, t["dim"], tracking=1.4)
    name = fit(me["name"], "display", size, room, -size * 0.03)  # past the 20 px floor, cut rather than overflow
    lively_name(c, left - size * 0.03, shift + name_y, name, size)
    for line, y in zip(roles, role_ys):
        svg.text(left, shift + y, line, "semi", rs, t["ink"])
    for line, y in zip(statement, text_ys):
        svg.text(left, shift + y, line, "text", fs, t["dim"])
    end = last = None
    for line, y in zip(aside, aside_ys):
        end = left + svg.text(left, shift + y, line, "semi", fs, t["aside"])
        last = shift + y
    if end is not None:
        # A cursor after the last word, as if it were still being typed.
        svg.css.append(".caret{animation:caret 1.1s steps(1,end) infinite}@keyframes caret{50%{opacity:0}}")
        svg.add(f'<rect class="caret" x="{num(end + 3)}" y="{num(last - fs * 0.8)}" width="{c.pick(2, 1.6)}" '
                f'height="{num(fs * 0.98)}" rx=".6" {paint(t["aside"])}/>')
    if facts_y is not None:
        svg.text(left, shift + facts_y, fit(" · ".join(facts).upper(), "mono", kick, room, 1.2),
                 "mono", kick, t["faint"], tracking=1.2)


def deck(c, me, now):
    """The record, its arm, and what's on it."""
    svg = c.svg
    g = HERO[c.v]
    playing = bool(now and now.get("playing"))
    clip = svg.uid("deck")  # the card's shape, so the record's shadow stays inside it
    svg.defs.append(f'<clipPath id="{clip}"><path d="{c.shape}"/></clipPath>')
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


def hero_rows(p, now, hrefs, home, pulse=None, home_title="About me", totals=None, profile=""):
    """The top of the page as one card: me and the record player side by side, the numbers under them. `hrefs` says
    where the deck links to (the Worker, Pages redirects, or the song itself); `home` is where my own tile goes.

    build.kit() draws the deck from these same rows, so the live deck has the shape of the one in the README."""
    me = p["me"]
    card = Card("blue", blobs=[(0.96, 0.3, 0.5, 0, 0.9), (0.04, 0.9, 0.5, 1, 0.7), (0.45, -0.2, 0.4, 2, 0.5)], joined=True)
    role = " · ".join(part for part in (me.get("person"), me.get("role")) if part)
    bio = " ".join(f"{part.rstrip('.')}." for part in (me["name"], role, me.get("statement"), me.get("aside")) if part)
    items = stats_items(totals or {})
    rows = [Row("hero", HERO["d"]["h"], HERO["m"]["h"], [
        Cell(card, SPLIT, home, home_title, bio, lambda c: identity(c, me, pulse), key="me"),
        Cell(card, 1 - SPLIT, hrefs["play"], "Play what's on the deck", "The record player, with what I'm listening to",
             lambda c: deck(c, me, now), live=True, key="deck"),
    ], space=not items, gap_below=not items)]
    if items:
        alt = ", ".join(f"{value} {label.lower()}" for value, label, _, _ in items)
        rows.append(Row("stats", 84, 62 * (1 if len(items) <= 2 else 2), [
            Cell(card, 1, f"{profile}?tab=repositories&sort=stargazers", "My repositories, most starred first", alt,
                 lambda c: stats_cell(c, items), key="numbers"),
        ], space=True, gap_above=False))
    return rows


# ── numbers ──────────────────────────────────────────────────────────────────


def stats_cell(c, items):
    """Big numbers over their labels, side by side on computers and two by two on phones."""
    svg, t = c.svg, c.t
    cols = len(items) if not c.m else min(2, len(items))
    rows = math.ceil(len(items) / cols)
    cw, rh = c.w / cols, c.h / rows
    size, small = c.pick(24, 19), c.pick(8, 7)
    inset = c.pick(20, 12)
    for i in range(1, cols):
        x = c.x + i * cw
        svg.add(f'<path d="M{num(x)} {num(inset)}V{num(c.h - inset)}" fill="none" {paint(t["edge"], "stroke")}/>')
    for i in range(1, rows):
        svg.add(f'<path d="M{num(c.x + inset)} {num(i * rh)}H{num(c.x + c.w - inset)}" fill="none" {paint(t["edge"], "stroke")}/>')
    for i, (value, label, icon, star) in enumerate(items):
        col, row = i % cols, i // cols
        cx = c.x + (col + 0.5) * cw
        vy, ly = centered_block(rh, size, c.pick(11, 9), small)
        vy, ly = vy + row * rh, ly + row * rh
        mw = c.pick(15, 12) if (icon or star) else 0
        gap = c.pick(7, 5) if mw else 0
        vw = FACES["display"].width(value, size, -0.5)
        x = cx - (mw + gap + vw) / 2
        if mw:
            mark(c, x, vy - size * 0.12, mw, icon=icon, star=star, color=t["accent"])
        svg.text(x + mw + gap, vy, value, "display", size, t["ink"], tracking=-0.5)
        svg.text(cx, ly, fit(label.upper(), "mono", small, cw - 16, 1.2), "mono", small, t["faint"], tracking=1.2,
                 anchor="middle")


def stats_items(totals):
    """The numbers that are there: (value, label, icon, star)."""
    items = []
    if totals.get("downloads"):
        items.append((compact(totals["downloads"]), "Release downloads", "download", False))
    if totals.get("stars"):
        items.append((compact(totals["stars"]), "Stars earned", None, True))
    if totals.get("repos"):
        items.append((str(totals["repos"]), "Public repos", "repo", False))
    if totals.get("contributions"):
        items.append((compact(totals["contributions"]), "Contributions, past year", "commit", False))
    return items


# ── section headers ──────────────────────────────────────────────────────────


def header(c, kicker_text, title, side, arrow):
    t = c.t
    y = c.pick(26, 24)
    kicker(c, c.x + 2, y, kicker_text, t["accent"])
    base = c.pick(50, 45)
    size, title = shrink(title, "display", c.pick(20, 17), c.w * 0.62, 0.85, -0.4)
    c.svg.text(c.x + 1, base, title, "display", size, t["head"], tracking=-0.4)
    right = c.x + c.w - 2
    small = c.pick(9, 8)
    if arrow:
        c.svg.icon("arrow", right - 10, base - 9, 10, t["muted"], stroke=2.2)
        right -= 15
    if side:
        c.svg.text(right, base, fit(side.upper(), "mono", small, c.w * 0.34, 1.4), "mono", small, t["muted"],
                   tracking=1.4, anchor="end")


def header_row(name, kicker_text, title, side, side_href, anchor):
    return Row(name, 55, 52, [
        Cell(Card(style="none"), 1, side_href or f"#{anchor}", side if side_href else title, f"{kicker_text}: {title}",
             lambda c: header(c, kicker_text, title, side, bool(side_href)), key="head"),
    ])


# ── projects ─────────────────────────────────────────────────────────────────


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
        svg.text(x, y + i * step, fit(line, "mono", size, w), "mono", size, (svg.t["ink"], 0.06))


def project_card(c, pr, big):
    """A project: its icon with the name and what it is beside it, a line or two about it, and its facts at the
    bottom. The big card keeps its text in a column beside the icon and can carry a picture of the app."""
    svg, t = c.svg, c.t
    pad = c.pick(24, 14) if big else c.pick(18, 12)
    icon = c.pick(64, 46) if big else c.pick(44, 32)
    if pr.get("texture") == "disasm":
        # An arm64 listing in the top right, beside the name, fading out towards the text.
        x, top = c.x + c.w * 0.42, c.pick(22, 16)
        fade, mask = svg.uid("fade"), svg.uid("mask")
        svg.defs.append(
            f'<linearGradient id="{fade}"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset=".6" stop-color="#fff" stop-opacity="1"/></linearGradient>'
            f'<mask id="{mask}" maskUnits="userSpaceOnUse" x="{num(x)}" y="0" width="{num(c.w * 0.58)}" height="{num(c.h)}">'
            f'<rect x="{num(x)}" y="0" width="{num(c.w * 0.58 - 2)}" height="{num(c.h)}" fill="url(#{fade})"/></mask>'
        )
        svg.add(f'<g mask="url(#{mask})">')
        disasm(svg, x, top, c.w * 0.58 - 10, pad + icon + 4 - top, c.pick(7.5, 6.5))
        svg.add("</g>")
    x0 = c.x + pad
    project_icon(c, pr, x0, pad, icon)
    right = c.x + c.w - pad
    beside = big and not c.m
    if beside and pr.get("mock"):
        mw = min(236, c.w * 0.3)
        mx = right - mw
        window_mock(svg, mx, 20, mw, c.h - 40, pr["hue"])
        right = mx - 28
    if not big:
        arrow = c.pick(24, 20)
        arrow_button(c, right - arrow, pad, arrow)
    tx = x0 + icon + c.pick(18, 12)
    room = right - tx - (0 if big else c.pick(32, 26))
    gap = c.pick(9, 6)
    ts, title = shrink(pr["title"], "display", c.pick(26, 19) if big else c.pick(17, 14), room, 0.72, -0.5)
    ks = c.pick(13, 10.5) if big else c.pick(11.5, 9.5)
    kind = ""
    if pr.get("kind"):
        ks, kind = shrink(pr["kind"], "semi", ks, right - tx, 0.85)  # under the arrow, so the full width
    block = ts * 0.72 + (gap + ks * 0.72 if kind else 0)
    ty = pad + (icon - block) / 2 + ts * 0.72
    ky = ty + gap + ks * 0.72
    svg.text(tx - 1, ty, title, "display", ts, t["ink"], tracking=-0.5)
    if kind:
        svg.text(tx, ky, kind, "semi", ks, t["dim"])
    px = tx if beside else x0
    width = right - px
    fs = c.pick(13.5, 12) if big else c.pick(12.5, 11)
    lh = c.pick(19.5, 16) if big else c.pick(18, 14.5)
    lines = c.pick(3, 4) if big else c.pick(2, 5)
    y = (ky + c.pick(26, 20)) if beside else (pad + icon + c.pick(28, 22))
    for line in FACES["text"].wrap(pr["note"], fs, width, lines):
        svg.text(px, y, line, "text", fs, t["dim"])
        y += lh
    size = c.pick(8.5, 7.5) if big else c.pick(8, 7)
    bottom = c.h - (c.pick(22, 13) if big else c.pick(17, 12))
    meta_line(c, px, bottom, width, pr.get("meta"), pr.get("language_color"), size)


def project_cell(card, pr, big):
    alt = f'{pr["title"]}: ' + " ".join(f"{part.rstrip('.')}." for part in (pr.get("kind"), pr["note"]) if part)
    return Cell(card, 1, pr["url"], f'Open {pr["title"]} on GitHub', alt,
                lambda c, pr=pr: project_card(c, pr, big), key=pr["name"].lower()[:40])


def project_rows(projects):
    """The first project on a card of its own, the rest two to a row."""
    if not projects:
        return []
    first, rest = projects[0], projects[1:]
    rows = [Row("work-1", 182, 156, [project_cell(Card(first["hue"], blobs=blobs_for(0)), first, True)], space=True)]
    for n, i in enumerate(range(0, len(rest), 2), 2):
        pair = rest[i:i + 2]
        solo = len(pair) == 1
        cells = [project_cell(Card(pr["hue"], blobs=blobs_for(n + k)), pr, solo) for k, pr in enumerate(pair)]
        rows.append(Row(f"work-{n}", 182 if solo else 146, 156 if solo else 154, cells, space=True))
    return rows


def chip_cell(c, pr):
    """A smaller project: icon, name and a line about it, with what kind of thing it is on the right."""
    svg, t = c.svg, c.t
    pad = c.pick(14, 10)
    icon = c.pick(30, 22)
    project_icon(c, pr, c.x + pad, (c.h - icon) / 2 if not c.m else pad, icon)
    tx = c.x + pad + icon + c.pick(13, 8)
    right = c.x + c.w - pad
    if c.m:
        size, name = shrink(pr["title"], "semi", 12, right - tx, 0.85)
        svg.text(tx, pad + icon / 2 + size * 0.36, name, "semi", size, t["ink"])
        y = pad + icon + 16
        for line in FACES["text"].wrap(pr["note"], 10.5, c.w - 2 * pad, 2):
            svg.text(c.x + pad, y, line, "text", 10.5, t["dim"])
            y += 13.5
        return
    tag_w = 0
    if pr.get("tag"):
        tag = fit(pr["tag"].upper(), "mono", 7.5, (right - tx) * 0.42, 1.2)
        tag_w = svg.text(right, 26, tag, "mono", 7.5, t["faint"], tracking=1.2, anchor="end")
    size, name = shrink(pr["title"], "semi", 13, right - tx - tag_w - 10, 0.85)
    svg.text(tx, 26, name, "semi", size, t["ink"])
    svg.text(tx, 43, fit(pr["note"], "text", 11.5, right - tx), "text", 11.5, t["dim"])


def repo_all(c, total):
    svg, t = c.svg, c.t
    label = f"Browse all {total} repositories" if total else "Browse all repositories"
    size, label = shrink(label, "semi", c.pick(12.5, 11.5), c.w - 50, 0.85)
    width = FACES["semi"].width(label, size) + 18
    x = c.x + (c.w - width) / 2
    svg.text(x, c.h / 2 + size * 0.36, label, "semi", size, t["ink"])
    svg.icon("arrow", x + width - 11, c.h / 2 - 5.5, 11, t["dim"], stroke=2.2)


def more_rows(projects, profile, total):
    """More projects, two to a row, ending with a way to every repository."""
    card = Card("graphite", blobs=[(0.0, 0.0, 0.55, 0, 0.6), (1.0, 1.0, 0.5, 2, 0.5), (0.5, 0.5, 0.35, 1, 0.3)])
    cells = [
        Cell(card, 1, pr["url"], f'Open {pr["title"]} on GitHub', f'{pr["title"]}: {pr["note"]}',
             lambda c, pr=pr: chip_cell(c, pr), key=pr["name"].lower()[:40])
        for pr in projects
    ]
    cells.append(Cell(card, 1, f"{profile}?tab=repositories&sort=updated", "All my repositories, latest push first",
                      "Browse all repositories", lambda c: repo_all(c, total), key="all"))
    rows = []
    for n, i in enumerate(range(0, len(cells), 2), 1):
        pair = cells[i:i + 2]
        tall = len(pair) == 2
        rows.append(Row(f"more-{n}", 58 if tall else 44, 72 if tall else 44, pair, space=i + 2 >= len(cells)))
    return rows


def archive_card(c, item):
    """Older work that people still use: what it was, and what it adds up to."""
    svg, t = c.svg, c.t
    pad = c.pick(18, 12)
    icon = c.pick(38, 28)
    svg.glass(c.x + pad, pad, icon, icon, icon * 0.28)
    svg.icon(item.get("glyph") or "archive", c.x + pad + icon * 0.24, pad + icon * 0.24, icon * 0.52, t["ink"])
    right = c.x + c.w - pad
    arrow = c.pick(24, 20)
    arrow_button(c, right - arrow, pad, arrow)
    tx = c.x + pad + icon + c.pick(14, 10)
    room = right - tx - arrow - 8
    gap = c.pick(8, 6)
    ts, title = shrink(item["title"], "display", c.pick(16, 13), room, 0.75, -0.4)
    ks = c.pick(11, 9.5)
    subtitle = item.get("subtitle", "")
    block = ts * 0.72 + (gap + ks * 0.72 if subtitle else 0)
    ty = pad + (icon - block) / 2 + ts * 0.72
    if subtitle:
        clears = ty + gap > pad + arrow  # its cap height is below the arrow
        ks, subtitle = shrink(subtitle, "semi", ks, (right - tx) if clears else room, 0.85)
    svg.text(tx - 1, ty, title, "display", ts, t["ink"], tracking=-0.4)
    if subtitle:
        svg.text(tx, ty + gap + ks * 0.72, subtitle, "semi", ks, t["dim"])
    fs, lh = c.pick(12, 10.5), c.pick(17, 14)
    y = pad + icon + c.pick(24, 18)
    for line in FACES["text"].wrap(item["note"], fs, c.w - 2 * pad, c.pick(2, 5)):
        svg.text(c.x + pad, y, line, "text", fs, t["dim"])
        y += lh
    meta_line(c, c.x + pad, c.h - c.pick(17, 12), c.w - 2 * pad, item.get("meta"), None, c.pick(8, 7), c.pick(1, 2))


def archive_rows(items):
    rows = []
    for n, i in enumerate(range(0, len(items), 2), 1):
        pair = items[i:i + 2]
        cells = [
            Cell(Card(item.get("hue") or "graphite", blobs=blobs_for(i + k + 1)), 1, item["url"],
                 item.get("tip") or f'Open {item["title"]}', f'{item["title"]}: {item["note"]}',
                 lambda c, item=item: archive_card(c, item), key=str(i + k + 1))
            for k, item in enumerate(pair)
        ]
        rows.append(Row(f"archive-{n}", 132, 152, cells, space=True))
    return rows


# ── music ────────────────────────────────────────────────────────────────────


def plays_label(track):
    if track.get("plays"):
        return f'{track["plays"]} play' + ("s" if track["plays"] != 1 else "")
    if track.get("ms"):
        minutes, seconds = divmod(round(track["ms"] / 1000), 60)
        return f"{minutes}:{seconds:02d}"
    return ""


def rotation_cell(c, tracks):
    """My top tracks of the last weeks: in columns on computers, a list on phones."""
    svg, t = c.svg, c.t
    pad = c.pick(18, 14)
    edge = paint(t["edge"], "stroke")
    if c.m:
        row_h = (c.h - 2 * pad) / len(tracks)
        right = c.x + c.w - pad
        for n, track in enumerate(tracks, 1):
            top = pad + (n - 1) * row_h
            if n > 1:
                svg.add(f'<path d="M{num(c.x + pad)} {num(top)}H{num(right)}" fill="none" {edge}/>')
            title_y = top + row_h / 2 - 1.5
            artist_y = title_y + 13
            svg.text(c.x + pad, title_y, f"{n:02d}", "mono", 8, t["accent"], tracking=1)
            plays = fit(plays_label(track).upper(), "mono", 7, (right - c.x - pad) * 0.3, 1)
            pw = svg.text(right, title_y, plays, "mono", 7, t["faint"], tracking=1, anchor="end") if plays else 0
            tx = c.x + pad + 24
            svg.text(tx, title_y, fit(track["name"], "semi", 12, right - tx - pw - 8), "semi", 12, t["ink"])
            svg.text(tx, artist_y, fit(track["artist"], "text", 10.5, right - tx), "text", 10.5, t["dim"])
        return
    cw = (c.w - 2 * pad) / len(tracks)
    for i, track in enumerate(tracks):
        x = c.x + pad + i * cw
        if i:
            svg.add(f'<path d="M{num(x)} {num(20)}V{num(c.h - 20)}" fill="none" {edge}/>')
        inner = x + (16 if i else 0)
        room = cw - (32 if i else 16)
        svg.text(inner, 30, f"{i + 1:02d}", "mono", 8, t["accent"], tracking=1.2)
        y = 50
        for line in FACES["semi"].wrap(track["name"], 12.5, room, 2):
            svg.text(inner, y, line, "semi", 12.5, t["ink"])
            y += 15.5
        svg.text(inner, 86, fit(track["artist"], "text", 11, room), "text", 11, t["dim"])
        plays = fit(plays_label(track).upper(), "mono", 7.5, room, 1.2)
        if plays:
            svg.text(inner, c.h - 16, plays, "mono", 7.5, t["faint"], tracking=1.2)


def rotation_rows(tracks, href):
    card = Card("green", blobs=[(1.0, -0.05, 0.55, 0, 0.9), (0.0, 1.05, 0.5, 1, 0.7), (0.65, 0.6, 0.3, 2, 0.4)])
    alt = "; ".join(f'{n}. {track["name"]} by {track["artist"]}' for n, track in enumerate(tracks, 1))
    return [Row("rotation", 120, 28 + 34 * len(tracks), [
        Cell(card, 1, href, "Everything I listen to", alt, lambda c: rotation_cell(c, tracks), key="tracks"),
    ], space=True)]


# ── the end ──────────────────────────────────────────────────────────────────


def contact_cell(c, item):
    svg, t = c.svg, c.t
    if c.m:
        size = 26
        svg.glass(c.x + 10, 10, size, size, size / 2)
        svg.icon(item.get("icon") or "globe", c.x + 10 + 6.5, 16.5, 13, t["ink"])
        svg.text(c.x + 10, 52, fit(item["label"].upper(), "mono", 6.5, c.w - 20, 1), "mono", 6.5, t["faint"], tracking=1)
        size, value = shrink(item["value"], "semi", 10.5, c.w - 20, 0.8)
        svg.text(c.x + 10, 66, value, "semi", size, t["ink"])
        return
    size = 34
    y0 = (c.h - size) / 2
    svg.glass(c.x + 16, y0, size, size, size / 2)
    svg.icon(item.get("icon") or "globe", c.x + 16 + 9, y0 + 9, 16, t["ink"])
    tx = c.x + 16 + size + 12
    room = c.x + c.w - 16 - 16 - tx
    svg.text(tx, c.h / 2 - 4, fit(item["label"].upper(), "mono", 7.5, room, 1.2), "mono", 7.5, t["faint"], tracking=1.2)
    size, value = shrink(item["value"], "semi", 13, room, 0.8)
    svg.text(tx, c.h / 2 + 12, value, "semi", size, t["ink"])
    svg.icon("arrow", c.x + c.w - 16 - 10, c.h / 2 - 5, 10, t["muted"], stroke=2.2)


def contact_row(items):
    card = Card("graphite", blobs=[(0.0, 0.0, 0.55, 0, 0.6), (1.0, 1.0, 0.5, 2, 0.5), (0.5, 0.5, 0.35, 1, 0.3)])
    cells = [
        Cell(card, 1, item["url"], item.get("tip") or f'{item["label"]}: {item["value"]}',
             f'{item["label"]}: {item["value"]}', lambda c, item=item: contact_cell(c, item), key=item["label"].lower())
        for item in items
    ]
    return [Row("contact", 66, 78, cells, space=True)]


def footer(c, name):
    t = c.t
    size = c.pick(8, 7.5)
    y = c.pick(26, 24)
    left = "SET IN INTER & JETBRAINS MONO" if not c.m else "INTER & JETBRAINS MONO"
    c.svg.text(c.x + 2, y, left, "mono", size, t["muted"], tracking=1.2)
    right = c.x + c.w - 2
    c.svg.icon("up", right - 9, y - 8, 9, t["muted"], stroke=2.2)
    text = f"© {datetime.now(timezone.utc).year} {name} · Back to top" if not c.m else "Top"
    c.svg.text(right - 13, y, text.upper(), "mono", size, t["muted"], tracking=1.2, anchor="end")


def page(p, data, hrefs):
    """Everything on the profile, top to bottom: rows of cells and the anchors between them."""
    me = p["me"]
    login = me["github"]
    profile = f"https://github.com/{login}"
    repos = data.get("repo_count")
    items = []

    home = me.get("website") or profile
    host = urllib.parse.urlsplit(home).netloc
    items += hero_rows(p, data["now"], hrefs, home, data.get("pulse"), f"More about me on {host}" if host else "About me",
                       data.get("totals"), profile)

    if data["projects"]:
        work = p.get("work", {})
        items.append(("anchor", "work"))
        items.append(header_row("work", work.get("kicker", "Work"), work.get("title", "Selected work"),
                                f"All {repos} repos" if repos else "All repos", f"{profile}?tab=repositories", "work"))
        items += project_rows(data["projects"])

    if data["more"]:
        more = p.get("more", {})
        items.append(("anchor", "more"))
        items.append(header_row("more", more.get("kicker", "More"), more.get("title", "More projects"),
                                more.get("side", ""), more.get("side_url"), "more"))
        items += more_rows(data["more"], profile, repos)

    if data["archive"]:
        archive = p.get("archive", {})
        items.append(("anchor", "archive"))
        items.append(header_row("archive", archive.get("kicker", "Archive"), archive.get("title", "Where it started"),
                                archive.get("side", ""), archive.get("side_url"), "archive"))
        items += archive_rows(data["archive"])

    tracks = data["tracks"]
    if tracks:
        listening = p.get("listening", {})
        scrobbles = data.get("scrobbles")
        lastfm_url = data.get("lastfm_url") or listening.get("profile") or None
        side = f"{compact(scrobbles)} scrobbles" if scrobbles else f'Top tracks · {tracks[0].get("source", "Spotify")}'
        items.append(("anchor", "music"))
        items.append(header_row("music", listening.get("kicker", "Music"), listening.get("title", "On rotation"), side,
                                lastfm_url, "music"))
        items += rotation_rows(tracks, lastfm_url or profile)

    if p.get("contact"):
        items += contact_row(p["contact"])

    items.append(Row("footer", 42, 42, [
        Cell(Card(style="none"), 1, "#top", "Back to the top", "Set in Inter and JetBrains Mono",
             lambda c: footer(c, me["name"]), key="end"),
    ]))
    return items
