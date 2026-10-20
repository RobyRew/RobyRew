"""The page as rows of linked slices.

GitHub strips CSS and image maps from READMEs, so a card can't carry links. Instead every card is drawn whole and
cut into one image per link. Images side by side meet flush, and `align="top"` on each image removes the gap
GitHub would otherwise leave between rows, so the cuts don't show: a card looks like one piece.

Every image also has a phone version, drawn at half the width with about the same type sizes. Both share the
README's `width="…%"`, so a row is split the same way on phones and computers; only the heights differ.

Sizes follow GitHub's own interface: titles around 20 px, text 13–14 px, labels 8–9 px.
"""

import math
import urllib.parse
from datetime import date, datetime, timedelta, timezone

from canvas import (FACES, HUES, PLATFORMS, STAR, SVG, artwork, blobs_for, compact, heat_colors, hexdump, num,
                    paint, record, render_pair, tonearm, window_mock)


WIDTH = {"d": 840, "m": 420}  # desktop and phone canvases
OUTER = {"d": 16, "m": 13}  # corner radius of a card
GUTTER = {"d": 12, "m": 8}  # space between cards that share a row
SPACE = {"d": 14, "m": 12}  # room under the last row of a card, before the next one
RULE = {"d": 18, "m": 12}  # how far the line between two rows of a card stays from its edges
# A row of images can't be shorter than a line of text (24 px), or GitHub pads it and a seam shows. These keep every
# row above that down to a 600 px window for the desktop images and a 340 px phone for the phone ones.
MIN_HEIGHT = {"d": 40, "m": 40}


# ── the slicing system ───────────────────────────────────────────────────────


class Card:
    """One rounded shape, possibly over several rows. Its tint is placed on the whole card."""

    def __init__(self, hue="graphite", style="glass", blobs=None):
        self.hue, self.style = hue, style
        self.blobs = blobs or blobs_for(0)
        self.rows = []


class Cell:
    """One linked image: a part of a row."""

    def __init__(self, card, span, href, title, alt, draw, live=False, key=None, whole=False):
        self.card, self.span, self.href, self.title, self.alt = card, span, href, title, alt
        self.draw, self.live, self.key = draw, live, key
        self.whole = whole  # draws in the card's coordinates, across all its rows; the image shows its own band
        self.file = ""
        self.f0 = self.f1 = 0.0


class Row:
    """Cells side by side. Consecutive cells of the same card share one shape."""

    def __init__(self, name, d, m, cells, space=False, width=100, lines=True, rule=True):
        self.name, self.h, self.cells, self.space, self.width = name, {"d": d, "m": m}, cells, space, width
        self.lines = lines  # thin lines between the cells
        self.rule = rule  # a thin line above, when the row continues a card
        for v, minimum in MIN_HEIGHT.items():
            if self.h[v] < minimum:
                raise ValueError(f"row {name} is {self.h[v]} high on {v}; GitHub would show a seam under {minimum}")
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
        self.panels = []
        for cell in cells:
            if self.panels and self.panels[-1][0] is cell.card:
                self.panels[-1][1].append(cell)
            else:
                self.panels.append((cell.card, [cell]))
        for card, _ in self.panels:
            card.rows.append(self)

    def height(self, v):
        return self.h[v] + (SPACE[v] if self.space else 0)

    def panel_box(self, i, v):
        _, cells = self.panels[i]
        x0, x1 = cells[0].f0 * WIDTH[v], cells[-1].f1 * WIDTH[v]
        if i:
            x0 += GUTTER[v] / 2
        if i < len(self.panels) - 1:
            x1 -= GUTTER[v] / 2
        return x0, x1

    def percent(self, cell):
        """The README width of a cell, rounded down so a row never spills onto a second line."""
        return math.floor((cell.f1 - cell.f0) * self.width * 1000 + 1e-6) / 1000


class Ctx:
    """What a cell's drawing function gets: the canvas and the cell's box on it.

    For a `whole` cell, y is measured from the top of the card, `h` is the card's height and the image only shows
    the band from `top` to `bottom`.
    """

    def __init__(self, svg, v, x, w, h, top=0, bottom=None):
        self.svg, self.t, self.v, self.m = svg, svg.t, v, v == "m"
        self.x, self.w, self.h = x, w, h
        self.top, self.bottom = top, h if bottom is None else bottom

    def pick(self, desktop, phone):
        return phone if self.m else desktop

    def shows(self, y0, y1):
        return y1 >= self.top - 1 and y0 <= self.bottom + 1


def outline(x, y, w, h, top, bottom, closed_top, closed_bottom):
    """The visible edge of one row of a card: both sides, plus the top or bottom where the card ends."""
    t, b = min(top, w / 2, h / 2), min(bottom, w / 2, h / 2)
    if closed_bottom:
        path = f"M{num(x + w - b)} {num(y + h)}H{num(x + b)}A{num(b)} {num(b)} 0 0 1 {num(x)} {num(y + h - b)}"
    else:
        path = f"M{num(x)} {num(y + h)}"
    if closed_top:
        path += (f"V{num(y + t)}A{num(t)} {num(t)} 0 0 1 {num(x + t)} {num(y)}H{num(x + w - t)}"
                 f"A{num(t)} {num(t)} 0 0 1 {num(x + w)} {num(y + t)}")
    else:
        path += f"V{num(y)}M{num(x + w)} {num(y)}"
    if closed_bottom:
        path += f"V{num(y + h - b)}A{num(b)} {num(b)} 0 0 1 {num(x + w - b)} {num(y + h)}"
    else:
        path += f"V{num(y + h)}"
    return path


def rounded(x, y, w, h, top, bottom):
    t, b = min(top, w / 2, h / 2), min(bottom, w / 2, h / 2)
    return (
        f"M{num(x + t)} {num(y)}H{num(x + w - t)}A{num(t)} {num(t)} 0 0 1 {num(x + w)} {num(y + t)}"
        f"V{num(y + h - b)}A{num(b)} {num(b)} 0 0 1 {num(x + w - b)} {num(y + h)}"
        f"H{num(x + b)}A{num(b)} {num(b)} 0 0 1 {num(x)} {num(y + h - b)}V{num(y + t)}"
        f"A{num(t)} {num(t)} 0 0 1 {num(x + t)} {num(y)}Z"
    )


def card_frame(card, row, v):
    """How far down the card this row starts, and the card's full height."""
    total, mine = 0, 0
    for r in card.rows:
        if r is row:
            mine = total
        total += r.h[v]
    return mine, total


def radii(card, row, v):
    return (OUTER[v] if card.rows[0] is row else 0), (OUTER[v] if card.rows[-1] is row else 0)


def vertical(svg, x, y0, y1, stops):
    """A top-to-bottom gradient in canvas coordinates, so it carries on across rows."""
    grad = svg.uid("lin")
    svg.defs.append(
        f'<linearGradient id="{grad}" gradientUnits="userSpaceOnUse" x1="{num(x)}" y1="{num(y0)}" x2="{num(x)}" '
        f'y2="{num(y1)}">' + "".join(f'<stop offset="{num(o)}" stop-color="{c}" stop-opacity="{num(a)}"/>' for o, c, a in stops)
        + "</linearGradient>"
    )
    return f"url(#{grad})"


def background(svg, card, row, x0, x1, v):
    """Frosted glass: a see-through fill, a faint tint, a sheen at the top and a light rim."""
    if card.style == "none":
        return
    t = svg.t
    h, w = row.h[v], x1 - x0
    top, bottom = radii(card, row, v)
    shape = rounded(x0, 0, w, h, top, bottom)
    first, last = card.rows[0] is row, card.rows[-1] is row
    edge = outline(x0 + 0.5, 0.5 if first else 0, w - 1, h - (0.5 if first else 0) - (0.5 if last else 0),
                   max(top - 0.5, 0), max(bottom - 0.5, 0), first, last)
    offset, full = card_frame(card, row, v)
    colors = HUES.get(card.hue, HUES["graphite"])
    clip = svg.uid("seg")
    svg.defs.append(f'<clipPath id="{clip}"><path d="{shape}"/></clipPath>')
    parts = [f'<g clip-path="url(#{clip})">', f'<rect x="{num(x0)}" y="0" width="{num(w)}" height="{num(h)}" {paint(t["card"])}/>']
    tint = t["blob"] * (1.6 if card.style == "tinted" else 1)
    for fx, fy, fr, ci, strength in card.blobs:
        cx, cy, r = x0 + fx * w, fy * full - offset, fr * max(w, full)
        if cy + r < 0 or cy - r > h:
            continue
        grad = svg.uid("blob")
        color = colors[ci]
        alpha = min(tint * strength, 0.9)
        svg.defs.append(
            f'<radialGradient id="{grad}" gradientUnits="userSpaceOnUse" cx="{num(cx)}" cy="{num(cy)}" r="{num(r)}">'
            f'<stop offset="0" stop-color="{color}" stop-opacity="{num(alpha)}"/>'
            f'<stop offset=".6" stop-color="{color}" stop-opacity="{num(alpha * 0.35)}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>'
        )
        parts.append(f'<rect x="{num(x0)}" y="0" width="{num(w)}" height="{num(h)}" fill="url(#{grad})"/>')
    sheen_end = min(full * 0.45, 140)
    if offset < sheen_end:
        color, alpha = t["sheen"]
        fill = vertical(svg, x0, -offset, sheen_end - offset, [(0, color, alpha), (1, color, 0)])
        parts.append(f'<rect x="{num(x0)}" y="0" width="{num(w)}" height="{num(min(h, sheen_end - offset))}" fill="{fill}"/>')
    parts.append("</g>")
    color, at_top, at_bottom = t["rim"]
    rim = vertical(svg, x0, -offset, full - offset, [(0, color, at_top), (0.5, color, (at_top + at_bottom) / 2), (1, color, at_bottom)])
    parts.append(f'<path d="{edge}" fill="none" stroke="{rim}"/>')
    if last and row.space and t["shadow"]:
        # A soft shadow under the card, in the room left before the next one.
        fill = vertical(svg, x0, h, h + SPACE[v] * 0.7, [(0, "#000000", t["shadow"]), (1, "#000000", 0)])
        parts.append(f'<rect x="{num(x0 + bottom)}" y="{num(h)}" width="{num(w - 2 * bottom)}" height="{num(SPACE[v] * 0.7)}" fill="{fill}"/>')
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
    box = (x0, x1)
    for i, (card, cells) in enumerate(row.panels):
        px0, px1 = row.panel_box(i, v)
        if cell in cells:
            box = (max(x0, px0), min(x1, px1))
        if px1 <= x0 or px0 >= x1:
            continue
        background(svg, card, row, px0, px1, v)
        if card.style == "none":
            continue
        if row.lines:
            inset = min(12, row.h[v] * 0.24)
            for other in cells[1:]:
                sx = other.f0 * W + 0.5
                if x0 <= sx <= x1:
                    svg.add(
                        f'<line x1="{num(sx)}" y1="{num(inset)}" x2="{num(sx)}" y2="{num(row.h[v] - inset)}" '
                        f'{paint(svg.t["edge"], "stroke")}/>'
                    )
        if row.rule and card.rows[0] is not row:
            svg.add(f'<line x1="{num(px0 + RULE[v])}" y1=".5" x2="{num(px1 - RULE[v])}" y2=".5" {paint(svg.t["edge"], "stroke")}/>')
    if cell.whole:
        top, full = card_frame(cell.card, row, v)
        svg.add(f'<g transform="translate(0 {num(-top)})">')
        cell.draw(Ctx(svg, v, box[0], box[1] - box[0], full, top, top + row.h[v]))
        svg.add("</g>")
    else:
        cell.draw(Ctx(svg, v, box[0], box[1] - box[0], row.h[v]))
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

# The record player card, in three rows: the spinning record with who I am beside it (like an artist page), a slim
# now-playing bar across the card (each part of it its own link), and the buttons.
HERO = {
    "d": {"rows": (172, 48, 46), "cx": 100, "cy": 88, "r": 64, "bar": 20},
    "m": {"rows": (132, 48, 44), "cx": 50, "cy": 66, "r": 38, "bar": 12},
}
SPLIT = 0.27  # the record's column, on the left; wide enough for the parked tonearm on phones too
NOW = (0.34, 0.22, 0.22, 0.22)  # song, artist, album or playlist, listener


def identity(c, me):
    """What I'm doing, my name, bio and facts, next to the record."""
    svg, t = c.svg, c.t
    left = c.x + c.pick(8, 4)
    facts = me.get("facts", [])
    chips = max((24 + 21 + FACES["semi"].width(f["value"], 11.5) for f in facts[1:]), default=0)
    room = c.x + c.w - left - (c.pick(chips + 40, 12) if chips else c.pick(22, 12))
    if facts:
        size = c.pick(8.5, 7.5)
        y = c.pick(40, 30)
        text = facts[0]["value"] if c.m else f'{facts[0]["label"]} · {facts[0]["value"]}'
        svg.add(f'<circle cx="{num(left + 3)}" cy="{num(y - size * 0.35)}" r="5.5" fill="#F2A65A" fill-opacity=".2"/>')
        svg.add(f'<circle cx="{num(left + 3)}" cy="{num(y - size * 0.35)}" r="2.6" fill="#F2A65A"/>')
        svg.text(left + 13, y, fit(text.upper(), "mono", size, room - 13, 1.4), "mono", size, t["dim"], tracking=1.4)
    size = c.pick(38, 26)
    while size > 20 and FACES["display"].width(me["name"], size, -size * 0.035) > room:
        size -= 1
    base = c.pick(78, 58)
    svg.text(left - size * 0.03, base, me["name"], "display", size, t["ink"], tracking=-size * 0.035)
    fs, lh = c.pick(14, 11.5), c.pick(19, 14.5)
    y = base + c.pick(24, 18)
    for line in FACES["text"].wrap(me["statement"], fs, room, 2):
        svg.text(left, y, line, "text", fs, t["dim"])
        y += lh
    y += c.pick(1, 2)
    for line in FACES["semi"].wrap(me["aside"], fs, room, 2):
        svg.text(left, y, line, "semi", fs, t["aside"])
        y += lh
    rest = facts[1:]
    if not rest:
        return
    if c.m:
        line = fit(" · ".join(f["value"] for f in rest), "semi", 10, room)
        svg.text(left, y + 6, line, "semi", 10, t["faint"])
        return
    # Day job and city on the right, stacked, so the row is balanced.
    right = c.x + c.w - 20
    y = (c.h - len(rest) * 24 - (len(rest) - 1) * 8) / 2
    for fact in rest:
        width = 24 + 21 + FACES["semi"].width(fact["value"], 11.5)
        svg.chip(right - width, y, fact["value"], h=24, size=11.5, icon=fact.get("icon", "spark"))
        y += 32


def deck(c, me, now):
    svg = c.svg
    g = HERO[c.v]
    playing = bool(now and now.get("playing"))
    svg.add(f'<g transform="translate({num(g["cx"])} {num(g["cy"])}) scale({num(g["r"] / 146)})">')
    record(svg, 0, 0, 146, me["record"], playing)
    if playing:
        tonearm(svg, 150, -138, [(158, 22), (102, 72)])
    else:
        tonearm(svg, 150, -138, [(158, 104), (159, 118)], rest=(159, 122))
    svg.add("</g>")


def status_text(now):
    if not now:
        return "OFF AIR"
    if now.get("playing"):
        return "NOW PLAYING"
    if now.get("paused"):
        return "PAUSED"
    stamp = when_label(now.get("when"))
    return f"LAST PLAYED · {stamp}" if stamp else "LAST PLAYED"


def now_bar(c, first):
    """The glass bar the now-playing parts sit in. Every part draws all of it; each image shows its own piece."""
    svg, t = c.svg, c.t
    inset = HERO[c.v]["bar"]
    x0, x1 = inset, WIDTH[c.v] - inset
    y, h = 5, c.h - 10
    svg.add(f'<rect x="{num(x0)}" y="{y}" width="{num(x1 - x0)}" height="{num(h)}" rx="{num(h / 2)}" '
            f'{paint(t["panel"])} {paint(t["edge"], "stroke")}/>')
    if not first:
        svg.add(f'<line x1="{num(c.x + 0.5)}" y1="{y + 11}" x2="{num(c.x + 0.5)}" y2="{num(y + h - 11)}" {paint(t["edge"], "stroke")}/>')
    left = max(c.x, x0) + c.pick(12, 8)
    right = min(c.x + c.w, x1) - c.pick(12, 7)
    return left, right, y + h / 2


def now_song(c, now):
    svg, t = c.svg, c.t
    left, right, mid = now_bar(c, True)
    playing = bool(now and now.get("playing"))
    art = c.pick(28, 26)
    ax = left - c.pick(5, 3)
    if now:
        artwork(svg, ax, mid - art / 2, art, now.get("cover"), now.get("title", ""), r=art / 2)
        svg.add(f'<circle cx="{num(ax + art / 2)}" cy="{num(mid)}" r="2.2" fill="#000" fill-opacity=".55"/>')
    else:
        svg.glass(ax, mid - art / 2, art, art, art / 2)
        svg.icon("disc", ax + art * 0.25, mid - art * 0.25, art * 0.5, t["faint"])
    tx = ax + art + c.pick(10, 7)
    room = right - tx
    dot = "#30D158" if playing else "#8E8E93"
    title = now.get("title", "") if now else "Nothing on the deck"
    if playing:
        svg.css.append(".pulse{animation:pulse 1.6s ease-in-out infinite alternate}@keyframes pulse{to{opacity:.3}}")
    pulse = ' class="pulse"' if playing else ""
    if c.m:
        svg.add(f'<circle{pulse} cx="{num(tx + 2.5)}" cy="{num(mid - 1)}" r="2.5" fill="{dot}"/>')
        size, title = shrink(title, "semi", 11, room - 9, 0.88)
        svg.text(tx + 9, mid + size * 0.35, title, "semi", size, t["ink"])
        return
    sy = mid - 3.5
    svg.add(f'<circle{pulse} cx="{num(tx + 2.5)}" cy="{num(sy - 2.6)}" r="2.5" fill="{dot}"/>')
    end = tx + 9 + svg.text(tx + 9, sy, fit(status_text(now), "mono", 7.5, room - 30, 1.2), "mono", 7.5, t["faint"], tracking=1.2)
    if playing:
        equalizer(svg, end + 6, sy + 0.5, 7)
    svg.text(tx, mid + 10, fit(title, "semi", 12.5, room), "semi", 12.5, t["ink"])


def now_part(c, value, icon=None, dot=None):
    """The artist, the album or playlist, or who is listening where."""
    svg, t = c.svg, c.t
    left, right, mid = now_bar(c, False)
    size = c.pick(11, 9.5)
    if dot:
        svg.add(f'<circle cx="{num(left + size * 0.4)}" cy="{num(mid)}" r="{num(size * 0.3)}" fill="{dot}"/>')
    else:
        svg.icon(icon, left, mid - size / 2, size, t["faint"], stroke=2)
    tx = left + size + c.pick(7, 5)
    text_size, value = shrink(value or "—", "semi", c.pick(12, 10.5), right - tx, 0.88)
    svg.text(tx, mid + text_size * 0.36, value, "semi", text_size, t["ink"])


def link_cell(c, link, left_pad, right_pad):
    """A website or chat button: glass with a touch of the link's colour."""
    svg, t = c.svg, c.t
    colors = HUES.get(link.get("hue") or "ember", HUES["ember"])
    h = c.pick(28, 26)
    x0, x1 = c.x + left_pad, c.x + c.w - right_pad
    y = (c.h - h) / 2 - 2
    tint = svg.uid("tint")
    svg.defs.append(
        f'<linearGradient id="{tint}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{colors[0]}" stop-opacity=".2"/>'
        f'<stop offset="1" stop-color="{colors[1]}" stop-opacity=".08"/></linearGradient>'
    )
    svg.add(
        f'<rect x="{num(x0)}" y="{num(y)}" width="{num(x1 - x0)}" height="{h}" rx="{h / 2}" fill="url(#{tint})"/>'
        f'<rect x="{num(x0 + 0.5)}" y="{num(y + 0.5)}" width="{num(x1 - x0 - 1)}" height="{h - 1}" rx="{(h - 1) / 2}" fill="none" '
        f'stroke="{colors[0]}" stroke-opacity=".32"/>'
    )
    dot = h - 8
    size = c.pick(12, 10)
    room = x1 - x0 - dot - c.pick(20, 12)
    label = link["label"]
    if FACES["semi"].width(label, size) > room and link.get("short"):
        label = link["short"]
    size, label = shrink(label, "semi", size, room, 0.86)
    width = dot + 6 + FACES["semi"].width(label, size)
    x = x0 + (x1 - x0 - width) / 2
    svg.add(f'<circle cx="{num(x + dot / 2)}" cy="{num(y + h / 2)}" r="{num(dot / 2)}" fill="{colors[0]}" fill-opacity=".9"/>')
    svg.icon(link.get("icon", "globe"), x + dot * 0.22, y + h / 2 - dot * 0.28, dot * 0.56, "#FFFFFF", stroke=2.2)
    svg.text(x + dot + 6, y + h / 2 + size * 0.36, label, "semi", size, t["ink"])


def nav_cell(c, icon, label, first, last):
    """One button of the jump bar; together they make one glass strip."""
    svg, t = c.svg, c.t
    h = c.pick(28, 26)
    y = (c.h - h) / 2 - 2
    x0 = c.x + (4 if first else 0)
    x1 = c.x + c.w - (HERO[c.v]["bar"] if last else 0)
    r = h / 2
    left_r, right_r = (r if first else 0), (r if last else 0)
    shape = (f"M{num(x0 + left_r)} {num(y)}H{num(x1 - right_r)}"
             + (f"A{num(r)} {num(r)} 0 0 1 {num(x1 - right_r)} {num(y + h)}" if last else f"V{num(y + h)}")
             + f"H{num(x0 + left_r)}"
             + (f"A{num(r)} {num(r)} 0 0 1 {num(x0 + left_r)} {num(y)}" if first else f"V{num(y)}") + "Z")
    svg.add(f'<path d="{shape}" {paint(t["glass"])}/>')
    svg.add(f'<path d="M{num(x0 + left_r)} {num(y + 0.5)}H{num(x1 - right_r)}M{num(x0 + left_r)} {num(y + h - 0.5)}H{num(x1 - right_r)}" '
            f'{paint(t["edge"], "stroke")}/>')
    if first:
        svg.add(f'<path d="M{num(x0 + r)} {num(y + 0.5)}A{num(r - 0.5)} {num(r - 0.5)} 0 0 0 {num(x0 + r)} {num(y + h - 0.5)}" '
                f'fill="none" {paint(t["edge"], "stroke")}/>')
    else:
        svg.add(f'<line x1="{num(x0 + 0.5)}" y1="{num(y + 7)}" x2="{num(x0 + 0.5)}" y2="{num(y + h - 7)}" {paint(t["edge"], "stroke")}/>')
    if last:
        svg.add(f'<path d="M{num(x1 - r)} {num(y + 0.5)}A{num(r - 0.5)} {num(r - 0.5)} 0 0 1 {num(x1 - r)} {num(y + h - 0.5)}" '
                f'fill="none" {paint(t["edge"], "stroke")}/>')
    size = c.pick(11.5, 9.5)
    icon_w = 0 if c.m else 17
    size, label = shrink(label, "semi", size, x1 - x0 - icon_w - 6, 0.85)
    width = icon_w + FACES["semi"].width(label, size)
    x = x0 + (x1 - x0 - width) / 2
    if icon_w:
        svg.icon(icon, x, y + h / 2 - 6, 12, t["dim"], stroke=2)
    svg.text(x + icon_w, y + h / 2 + size * 0.36, label, "semi", size, t["ink"])


def hero_rows(p, now, hrefs, sections):
    """The record player card. `hrefs` says where its live parts link to (Pages redirects, or the song itself)."""
    me = p["me"]
    links = p.get("links", [])[:2]
    card = Card("ember", blobs=[(0.06, 0.25, 0.45, 0, 0.9), (0.96, 0.85, 0.5, 1, 0.7), (0.55, -0.2, 0.4, 2, 0.5)])
    info = now or {}
    platform = info.get("platform") or "Last.fm"
    home = links[0]["url"] if links else f'https://github.com/{me["github"]}'
    bio = f'{me["name"]}. {me["statement"]} {me["aside"]}'
    d, m = HERO["d"]["rows"], HERO["m"]["rows"]
    kind = info.get("context_kind") or ("Album" if info.get("context") else "From")
    rows = [
        Row("hero", d[0], m[0], [
            Cell(card, SPLIT, hrefs["play"], f"Play it on {platform}", "The record player: it spins while I'm listening",
                 lambda c: deck(c, me, now), live=True, key="deck"),
            Cell(card, 1 - SPLIT, home, f"Visit {links[0]['label']}" if links else "My GitHub", bio,
                 lambda c: identity(c, me), key="me"),
        ], lines=False, rule=False),
        Row("hero-now", d[1], m[1], [
            Cell(card, NOW[0], hrefs["song"], "The song on my record player", "What I'm listening to",
                 lambda c: now_song(c, now), live=True, key="song"),
            Cell(card, NOW[1], hrefs["artist"], "The artist", "Artist",
                 lambda c: now_part(c, info.get("artist") or "—", icon="mic"), live=True, key="artist"),
            Cell(card, NOW[2], hrefs["context"], f"The {kind.lower()}" if kind != "From" else "Where it's playing from", kind,
                 lambda c: now_part(c, info.get("context") or info.get("device") or "Library",
                                    icon="list" if kind == "Playlist" else "disc"), live=True, key="context"),
            Cell(card, NOW[3], hrefs["user"], f"My {platform} profile", "Listening profile",
                 lambda c: now_part(c, f'@{info["user"]}' if info.get("user") else platform,
                                    dot=PLATFORMS.get(platform, "#9CA3AF")), live=True, key="user"),
        ], lines=False, rule=False),
    ]
    buttons = []
    for i, link in enumerate(links):
        buttons.append(Cell(card, 0.5 / len(links), link["url"], f'Open {link["label"]}', link["label"],
                            lambda c, link=link, i=i: link_cell(c, link, HERO[c.v]["bar"] if i == 0 else 4, 4),
                            key=f"link{i + 1}"))
    if not buttons:
        buttons.append(Cell(card, 0.5, home, "My GitHub", "", lambda c: None, key="links"))
    for i, (anchor, label, icon) in enumerate(sections):
        buttons.append(Cell(card, 0.5 / len(sections), f"#{anchor}", f"Jump to {label}", label,
                            lambda c, icon=icon, label=label, i=i: nav_cell(c, icon, label, i == 0, i == len(sections) - 1),
                            key=anchor))
    rows.append(Row("hero-buttons", d[2], m[2], buttons, lines=False, rule=False, space=True))
    return rows


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
    return Row(name, 60, 56, [
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


def bside_main(c, repo, n):
    svg, t = c.svg, c.t
    badge = c.pick(28, 24)
    bx = c.x + c.pick(16, 10)
    svg.glass(bx, (c.h - badge) / 2, badge, badge, badge * 0.3)
    svg.text(bx + badge / 2, c.h / 2 + c.pick(3.5, 3.2), f"{n:02d}", "mono", c.pick(9.5, 8.5), t["dim"], tracking=0.4, anchor="middle")
    tx = bx + badge + c.pick(12, 9)
    room = c.x + c.w - tx - c.pick(14, 8)
    description = repo.get("description") or "No description yet."
    size, name = shrink(repo["name"], "semi", c.pick(13.5, 12.5), room)
    if c.m:
        svg.text(tx, 23, name, "semi", size, t["ink"])
        y = 39
        for line in FACES["text"].wrap(description, 11, room, 2):
            svg.text(tx, y, line, "text", 11, t["dim"])
            y += 13.5
        return
    svg.text(tx, c.h / 2 - 2, name, "semi", size, t["ink"])
    svg.text(tx, c.h / 2 + 13, fit(description, "text", 11.5, room), "text", 11.5, t["dim"])


def bside_rows(recent):
    rows = []
    card = Card("graphite", blobs=[(0.02, 0.1, 0.45, 0, 0.8), (1.0, 0.9, 0.4, 2, 0.6), (0.6, 0.5, 0.3, 1, 0.35)])
    for n, repo in enumerate(recent, 1):
        url = repo["url"]
        stars = repo.get("stars", 0)
        language = repo.get("language") or "Code"
        updated = when_label(repo.get("pushed")) or "—"
        rows.append(Row(f"bside-{n}", 48, 58, [
            Cell(card, 0.6, url, f'Open {repo["name"]} on GitHub', f'{repo["name"]}: {repo.get("description") or ""}'.strip(": "),
                 lambda c, repo=repo, n=n: bside_main(c, repo, n), key="repo"),
            Cell(card, 0.2, f"{url}/stargazers", f'Who starred {repo["name"]}', f"{stars} stars, {language}",
                 lambda c, stars=stars, language=language, color=repo.get("language_color"):
                 meta_stat(c, compact(stars), language, star=True) if stars else
                 meta_stat(c, language, "Language", dot=color or "#9CA3AF"), key="stars"),
            Cell(card, 0.2, f"{url}/commits", f'Latest commits in {repo["name"]}', f"Updated {updated}",
                 lambda c, updated=updated: meta_stat(c, updated, "Updated", icon="clock"), key="updated"),
        ], space=n == len(recent)))
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
                        f'rx="{OUTER[c.v]}"/></clipPath>')
        svg.add(f'<g clip-path="url(#{clip})">')
        disasm(svg, c.x + c.pick(14, 9), c.pick(18, 14), c.w - c.pick(20, 12), c.h - 10, c.pick(7.5, 6.5))
        svg.add("</g>")
    elif item.get("texture") == "hex":
        clip = svg.uid("hex")
        svg.defs.append(f'<clipPath id="{clip}"><rect x="{num(c.x)}" y="0" width="{num(c.w)}" height="{num(c.h)}" '
                        f'rx="{OUTER[c.v]}"/></clipPath>')
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


def languages_head(c, stats):
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


def language_cell(c, name, share, color):
    svg, t = c.svg, c.t
    if c.m:
        x = c.x + 12
        svg.add(f'<circle cx="{num(x + 3.5)}" cy="21.5" r="3.5" fill="{color}"/>')
        svg.text(x + 11, 25.5, fit(name, "semi", 11.5, c.w - 28), "semi", 11.5, t["ink"])
        svg.text(x + 11, 39, f"{share:.1f}%", "mono", 8.5, t["faint"])
        return
    x = c.x + 18
    svg.add(f'<circle cx="{num(x + 4)}" cy="{num(c.h / 2 - 0.5)}" r="4" fill="{color}"/>')
    svg.text(c.x + c.w - 16, c.h / 2 + 3.2, f"{share:.1f}%", "mono", 9, t["faint"], anchor="end")
    svg.text(x + 14, c.h / 2 + 4, fit(name, "semi", 12.5, c.w - 90), "semi", 12.5, t["ink"])


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
        groups = [
            [
                ("Commits", "Commits", stats.get("commits"), "commit", search(f"author:{login} committer-date:>{year_ago}", "commits"), "My commits this year"),
                ("Pull requests", "PRs", stats.get("prs"), "merge", search(f"author:{login} type:pr created:>{year_ago}", "pullrequests"), "My pull requests this year"),
                ("Issues", "Issues", stats.get("issues"), "issue", search(f"author:{login} type:issue created:>{year_ago}", "issues"), "Issues I opened this year"),
                ("Reviews", "Reviews", stats.get("reviews"), "eye", search(f"reviewed-by:{login} type:pr created:>{year_ago}", "pullrequests"), "Pull requests I reviewed"),
            ],
            [
                ("Current streak", "Streak", f'{stats.get("streak", 0)}d', "flame", f"{profile}?tab=overview", "Days in a row with a contribution"),
                ("Longest streak", "Longest", f'{stats.get("longest", 0)}d', "flame", f"{profile}?tab=overview", "Longest run this year"),
                ("Active days", "Active", stats.get("active_days"), "calendar", f"{profile}?tab=overview", "Days with at least one contribution"),
                (f"Best day · {best_label}" if best_label else "Best day", f"Best · {best_label}" if best_label else "Best day",
                 stats.get("best_count"), "spark",
                 f"{profile}?tab=overview&from={best}&to={best}" if best else f"{profile}?tab=overview", "My busiest day this year"),
            ],
        ]
        for gi, group in enumerate(groups):
            cells = []
            for label, short, value, icon, url, tip in group:
                shown = compact(value) if isinstance(value, int) else (value if value is not None else "—")
                cells.append(Cell(card, 1, url, tip, f"{label}: {shown}",
                                  lambda c, shown=shown, label=label, short=short, icon=icon:
                                  big_stat(c, shown, c.pick(label, short), icon=icon), key=short.split(" ")[0].lower()))
            rows.append(Row(f"activity-{gi + 1}", 54, 56, cells, space=gi == len(groups) - 1))

    joined = stats.get("joined") or ""
    years = ""
    if joined:
        start = datetime.fromisoformat(joined.replace("Z", "+00:00"))
        years = str(int((datetime.now(timezone.utc) - start).days // 365.25))
    popularity = [
        [
            ("Profile views", "Views", stats.get("views"), "eye", profile, "This page's view counter"),
            ("Stars earned", "Stars", stats.get("stars"), "star", f"{profile}?tab=repositories&sort=stargazers", "My repositories by stars"),
            ("Followers", "Followers", stats.get("followers"), "users", f"{profile}?tab=followers", "Who follows me"),
        ],
        [
            ("Merged PRs", "Merged PRs", stats.get("merged_prs"), "merge", search(f"author:{login} type:pr is:merged", "pullrequests"), "My merged pull requests"),
            ("Forks of my repos", "Forks", stats.get("forks"), "fork", f"{profile}?tab=repositories", "My repositories"),
            ("Contributed to", "Contributed", stats.get("contributed_to"), "repo", search(f"author:{login} -user:{login} type:pr", "pullrequests"), "Pull requests to other people's projects"),
        ],
        [
            ("Years on GitHub", f"Since {since}" if since else "On GitHub", f"{years} yrs" if years else None, "clock", profile, f"On GitHub since {since}"),
            ("All-time contributions", "All-time", stats.get("all_time"), "chart", f"{profile}?tab=overview", "Every contribution since I joined"),
            ("Busiest day of the week", "Busiest day", stats.get("busiest"), "calendar", f"{profile}?tab=overview", "The weekday I code the most"),
        ],
    ]
    popularity = [[cell for cell in group if cell[2] is not None] for group in popularity]
    popularity = [group for group in popularity if group]
    if popularity:
        card = Card("rose", blobs=[(0.95, 0.05, 0.5, 0, 0.9), (0.05, 0.95, 0.5, 1, 0.7), (0.5, 0.5, 0.3, 2, 0.35)])
        for gi, group in enumerate(popularity):
            cells = []
            for label, short, value, icon, url, tip in group:
                shown = compact(value) if isinstance(value, int) else value
                cells.append(Cell(card, 1, url, tip, f"{label}: {shown}",
                                  lambda c, shown=shown, label=label, short=short, icon=icon:
                                  big_stat(c, shown, c.pick(label, short), icon=None if icon == "star" else icon,
                                           star=icon == "star", size=c.pick(21, 17)),
                                  key=short.split(" ")[0].lower()))
            rows.append(Row(f"popularity-{gi + 1}", 58, 58, cells, space=gi == len(popularity) - 1))

    langs = stats.get("languages") or []
    if langs:
        card = Card("teal", blobs=[(0.05, 0.0, 0.5, 0, 0.9), (1.0, 1.0, 0.45, 1, 0.75), (0.6, 0.3, 0.3, 2, 0.4)])
        rows.append(Row("languages", 58, 56, [Cell(card, 1, f"{profile}?tab=repositories", "All my repositories",
                                                    "Languages: " + ", ".join(f"{n} {s:.0f}%" for n, s, _ in langs),
                                                    lambda c: languages_head(c, stats))]))
        shown = langs[:8]
        for gi in range(0, len(shown), 4):
            group = shown[gi:gi + 4]
            cells = []
            for name, share, color in group:
                url = f"{profile}?tab=repositories" + ("" if name == "Other" else f"&language={urllib.parse.quote(name.lower())}")
                tip = f"My {name} repositories" if name != "Other" else "All my repositories"
                cells.append(Cell(card, 1, url, tip, f"{name} {share:.1f}%",
                                  lambda c, name=name, share=share, color=color: language_cell(c, name, share, color)))
            while len(cells) < 4:
                cells.append(Cell(card, 1, f"{profile}?tab=repositories", "All my repositories", "", lambda c: None))
            rows.append(Row(f"languages-{gi // 4 + 1}", 42, 50, cells, space=gi + 4 >= len(shown)))
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


def track_cell(c, track, n):
    svg, t = c.svg, c.t
    art = c.pick(30, 32)
    if c.m:
        ax = c.x + 10
    else:
        svg.text(c.x + 18, c.h / 2 + 3.2, f"{n:02d}", "mono", 9, t["faint"], tracking=0.4)
        ax = c.x + 42
    artwork(svg, ax, (c.h - art) / 2, art, track.get("cover"), track["name"], r=6)
    tx = ax + art + c.pick(12, 9)
    room = c.x + c.w - tx - c.pick(14, 8)
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
            Cell(card, 0.58, url, f'{track["name"]} by {track["artist"]}', f'{n}. {track["name"]}',
                 lambda c, track=track, n=n: track_cell(c, track, n), key="track"),
            Cell(card, 0.27, artist_url, f'More from {track["artist"]}', track["artist"],
                 lambda c, name=track["artist"]: artist_cell(c, name), key="artist"),
            Cell(card, 0.15, track.get("plays_url") or url, "My plays of this track", f"{value} {label.lower()}",
                 lambda c, value=value, label=label: meta_stat(c, value, label, icon="music" if label == "Plays" else None),
                 key="plays"),
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


def catalogue_cell(c, repo):
    svg, t = c.svg, c.t
    pad = c.pick(18, 11)
    room = c.w - 2 * pad
    language = repo.get("language") or ""
    stars = repo.get("stars", 0)
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


def catalogue_all(c, total):
    svg, t = c.svg, c.t
    label = f"Browse all {total} repositories" if total else "Browse all repositories"
    size, label = shrink(label, "semi", c.pick(12.5, 11.5), c.w - 50, 0.85)
    width = FACES["semi"].width(label, size) + 18
    x = c.x + (c.w - width) / 2
    svg.text(x, c.h / 2 + size * 0.36, label, "semi", size, t["ink"])
    svg.icon("arrow", x + width - 11, c.h / 2 - 5.5, 11, t["dim"], stroke=2.2)


def catalogue_rows(more, login, total, limit=9):
    """The projects not shown above, two to a row, ending with a way to every repository."""
    card = Card("graphite", blobs=[(0.0, 0.0, 0.55, 0, 0.6), (1.0, 1.0, 0.5, 2, 0.5), (0.5, 0.5, 0.35, 1, 0.3)])
    everything = f"https://github.com/{login}?tab=repositories"
    cells = [
        Cell(card, 1, repo["url"], f'Open {repo["name"]} on GitHub', f'{repo["name"]}: {repo.get("description") or ""}'.strip(": "),
             lambda c, repo=repo: catalogue_cell(c, repo), key=repo["name"].lower()[:40])
        for repo in more[:limit]
    ]
    cells.append(Cell(card, 1, everything, "All my repositories", "Browse all repositories",
                      lambda c: catalogue_all(c, total), key="all"))
    rows = []
    for n, i in enumerate(range(0, len(cells), 2), 1):
        pair = cells[i:i + 2]
        rows.append(Row(f"catalogue-{n}", 54 if len(pair) == 2 else 44, 62 if len(pair) == 2 else 44, pair,
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
    projects, recent, more, stats, tracks = data["projects"], data["recent"], data["more"], data["stats"], data["tracks"]
    since = data.get("since", "")
    items = []

    sections = []
    if projects:
        sections.append(("work", "Work", "code"))
    if stats:
        sections.append(("charts", "Charts", "chart"))
    if tracks:
        sections.append(("music", "Music", "music"))
    if p.get("credits", {}).get("items"):
        sections.append(("credits", "Credits", "layers"))

    items += hero_rows(p, data["now"], hrefs, sections)

    if projects:
        items.append(("anchor", "work"))
        repos = data.get("repo_count")
        items.append(header_row("side-a", "Side A", p["work"]["title"], f"All {repos} repos" if repos else "All repos",
                                f"{profile}?tab=repositories", "work"))
        items += project_rows(projects, login)
    if recent:
        title = p.get("bsides", {}).get("title", "Fresh from the studio")
        items.append(header_row("b-sides", "B-sides", title, "Latest pushes", f"{profile}?tab=repositories&sort=updated", "work"))
        items += bside_rows(recent)
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
        items.append(("anchor", "charts"))
        items.append(header_row("charts", "Charts", "Activity & popularity", "Updated daily", f"{profile}?tab=overview", "charts"))
        items += chart_rows(stats, login, since, skyline_url)

    if tracks:
        listening = p.get("listening", {})
        items.append(("anchor", "music"))
        scrobbles = data.get("scrobbles")
        lastfm_url = data.get("lastfm_url") or listening.get("profile") or None
        side = f"{compact(scrobbles)} scrobbles" if scrobbles else f'Top tracks · {tracks[0].get("source", "Spotify")}'
        items.append(header_row("rotation", "On rotation", listening.get("title", "On rotation"), side, lastfm_url, "music", bars=True))
        items += rotation_rows(tracks)

    credits = p.get("credits", {})
    if credits.get("items"):
        items.append(("anchor", "credits"))
        items.append(header_row("liner-notes", "Credits", credits.get("title", "Liner notes"), "Stack & tools", None, "credits"))
        items += credit_rows(credits["items"], credits.get("urls"), "#credits")

    if more:
        repos = data.get("repo_count")
        items.append(header_row("catalogue", "More", "Back catalogue", f"All {repos} repos" if repos else "All repos",
                                f"{profile}?tab=repositories", "work"))
        items += catalogue_rows(more, login, repos)
    items.append(Row("footer", 42, 42, [
        Cell(Card(style="none"), 1, "#top", "Back to the top", "Set in Bricolage Grotesque and Geist Mono",
             lambda c: footer(c, me["name"]), key="end"),
    ]))
    return items
