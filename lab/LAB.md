# README lab

A test sheet for what a GitHub profile README can really do. Each test says what should happen.
Nothing here touches the profile; this file only lives in `lab/`.

<a name="top"></a>

**Jump to:** [Slices](#t01--card-cut-into-linked-slices) · [Tiles](#t04--tiles-with-no-gaps) · [Phone art](#t07--different-images-on-phones) · [Expand](#t08--tap-a-card-to-expand) · [Diagrams, maps, 3D](#t18--mermaid-diagram-with-links)

## T01 · Card cut into linked slices

Expected: looks like one card. Top opens the repo, each bottom chip opens its own page. Watch for a seam between top and bottom.

<div align="center">
<a href="https://github.com/RobyRew/TopPresenter"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-body-dark.svg"><img src="assets/card-body-light.svg" width="100%" alt="TopPresenter"></picture></a>
<a href="https://github.com/RobyRew/TopPresenter/stargazers"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-chip1-dark.svg"><img src="assets/card-chip1-light.svg" width="33.333%" alt="1 star"></picture></a><a href="https://github.com/RobyRew/TopPresenter/releases"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-chip2-dark.svg"><img src="assets/card-chip2-light.svg" width="33.333%" alt="88 downloads"></picture></a><a href="https://github.com/RobyRew/TopPresenter/releases/latest"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-chip3-dark.svg"><img src="assets/card-chip3-light.svg" width="33.333%" alt="v1.0.0"></picture></a>
</div>

## T02 · Same slices, stacked with `<br>`

Expected: the gap between top and bottom changes (or disappears).

<div align="center">
<a href="https://github.com/RobyRew/TopPresenter"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-body-dark.svg"><img src="assets/card-body-light.svg" width="100%" alt="TopPresenter"></picture></a><br><a href="https://github.com/RobyRew/TopPresenter/stargazers"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-chip1-dark.svg"><img src="assets/card-chip1-light.svg" width="33.333%" alt="1 star"></picture></a><a href="https://github.com/RobyRew/TopPresenter/releases"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-chip2-dark.svg"><img src="assets/card-chip2-light.svg" width="33.333%" alt="88 downloads"></picture></a><a href="https://github.com/RobyRew/TopPresenter/releases/latest"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-chip3-dark.svg"><img src="assets/card-chip3-light.svg" width="33.333%" alt="v1.0.0"></picture></a>
</div>

## T03 · Same slices, floated with `align="left"` and `<br clear="all">`

Expected: if floats work, the slices tile with no gap at all.

<a href="https://github.com/RobyRew/TopPresenter"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-body-dark.svg"><img src="assets/card-body-light.svg" width="100%" alt="TopPresenter" align="left"></picture></a>
<a href="https://github.com/RobyRew/TopPresenter/stargazers"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-chip1-dark.svg"><img src="assets/card-chip1-light.svg" width="33.333%" alt="1 star" align="left"></picture></a><a href="https://github.com/RobyRew/TopPresenter/releases"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-chip2-dark.svg"><img src="assets/card-chip2-light.svg" width="33.333%" alt="88 downloads" align="left"></picture></a><a href="https://github.com/RobyRew/TopPresenter/releases/latest"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-chip3-dark.svg"><img src="assets/card-chip3-light.svg" width="33.333%" alt="v1.0.0" align="left"></picture></a>
<br clear="all">

Control: the uncut card.

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-full-dark.svg"><img src="assets/card-full-light.svg" width="100%" alt="Whole card"></picture>

## T04 · Tiles with no gaps

Expected: a 4×2 grid, every tile its own link, no visible seams.

<div align="center">
<a href="https://github.com/RobyRew?tab=repositories&n=1"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tile1-dark.svg"><img src="assets/tile1-light.svg" width="25%" alt="Tile 1"></picture></a><a href="https://github.com/RobyRew?tab=repositories&n=2"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tile2-dark.svg"><img src="assets/tile2-light.svg" width="25%" alt="Tile 2"></picture></a><a href="https://github.com/RobyRew?tab=repositories&n=3"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tile3-dark.svg"><img src="assets/tile3-light.svg" width="25%" alt="Tile 3"></picture></a><a href="https://github.com/RobyRew?tab=repositories&n=4"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tile4-dark.svg"><img src="assets/tile4-light.svg" width="25%" alt="Tile 4"></picture></a>
<a href="https://github.com/RobyRew?tab=repositories&n=5"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tile5-dark.svg"><img src="assets/tile5-light.svg" width="25%" alt="Tile 5"></picture></a><a href="https://github.com/RobyRew?tab=repositories&n=6"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tile6-dark.svg"><img src="assets/tile6-light.svg" width="25%" alt="Tile 6"></picture></a><a href="https://github.com/RobyRew?tab=repositories&n=7"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tile7-dark.svg"><img src="assets/tile7-light.svg" width="25%" alt="Tile 7"></picture></a><a href="https://github.com/RobyRew?tab=repositories&n=8"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tile8-dark.svg"><img src="assets/tile8-light.svg" width="25%" alt="Tile 8"></picture></a>
</div>

## T05 · Spacing with `hspace` / `vspace`

Expected: the two buttons sit 24 px apart with space above and below.

<div align="center">
<a href="https://robyrew.com"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/button-dark.svg"><img src="assets/button-light.svg" alt="Button" hspace="12" vspace="16"></picture></a><a href="https://t.me/RobyRew"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/button-dark.svg"><img src="assets/button-light.svg" alt="Button" hspace="12" vspace="16"></picture></a>
</div>

## T06 · Hover tooltips

Expected: hovering the button shows "Opens robyrew.com". Hovering the abbreviation shows its meaning.

<div align="center">
<a href="https://robyrew.com" title="Opens robyrew.com"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/button-dark.svg"><img src="assets/button-light.svg" alt="Button" title="Opens robyrew.com"></picture></a>
</div>

I take apart binaries in <abbr title="Reverse engineering">RE</abbr> tools.

## T07 · Different images on phones

Expected: below 600 px wide (a phone) you see the green "Phone version"; on a computer the blue "Desktop version".

<picture>
<source media="(prefers-color-scheme: dark) and (max-width: 600px)" srcset="assets/narrow-dark.svg">
<source media="(max-width: 600px)" srcset="assets/narrow-light.svg">
<source media="(prefers-color-scheme: dark)" srcset="assets/wide-dark.svg">
<img src="assets/wide-light.svg" width="100%" alt="Responsive test">
</picture>

Width only, no theme:

<picture>
<source media="(max-width: 600px)" srcset="assets/narrow-dark.svg">
<img src="assets/wide-dark.svg" width="100%" alt="Responsive test, width only">
</picture>

## T08 · Tap a card to expand

Expected: tapping the card opens a list of real, clickable links underneath.

<details>
<summary><picture><source media="(prefers-color-scheme: dark)" srcset="assets/summary-dark.svg"><img src="assets/summary-light.svg" width="100%" alt="More projects"></picture></summary>

- [**pacetimer**](https://github.com/RobyRew/pacetimer) · Liquid-Glass menu-bar countdown for macOS
- [**split-stream**](https://github.com/RobyRew/split-stream) · Split one app's traffic through your own server
- [**retro-phone-tools**](https://github.com/RobyRew/retro-phone-tools) · Nokia DCT4 firmware tools in the browser

</details>

<details open>
<summary><b>Plain text summary, open by default</b></summary>

Content that starts expanded.

</details>

## T09 · Real-text buttons

Expected: links that look like keys.

<kbd><a href="https://robyrew.com">🌐 robyrew.com</a></kbd> <kbd><a href="https://t.me/RobyRew">✈️ Telegram</a></kbd> <kbd><a href="#top">↑ Top</a></kbd>

<sub>small print in &lt;sub&gt;</sub> · <sup>tiny in &lt;sup&gt;</sup> · <mark>highlighted</mark> · <ins>inserted</ins> · <del>deleted</del> · <samp>sample</samp>

## T10 · Coloured real text (math trick)

Expected: the words appear in orange, teal and pink, selectable as text.

$\color{#FF6A2B}\textsf{Native}$ $\color{#14B8A6}\textsf{apps}$ $\color{#F43F5E}\textsf{only}$

## T11 · Callouts

> [!TIP]
> Alerts render as coloured boxes with an icon.

> [!IMPORTANT]
> Another style.

## T12 · Things GitHub should strip

Expected: no red text, no clickable areas on the map image, no custom ids.

<div style="color:red" class="secret" id="custom">If this is red, inline styles survive.</div>

<img src="assets/tile1-dark.svg" width="210" usemap="#m" alt="Image map test">
<map name="m"><area shape="rect" coords="0,0,105,110" href="https://robyrew.com" alt="left half"></map>

<table border="0" cellpadding="0" cellspacing="0"><tr><td width="50%"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tile2-dark.svg"><img src="assets/tile2-light.svg" width="100%" alt="Table cell"></picture></td><td width="50%">Real text in a table cell next to an image. Borders show if GitHub keeps its table style.</td></tr></table>

## T13 · HTML and CSS inside an SVG (foreignObject)

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/foreign-dark.svg"><img src="assets/foreign-light.svg" width="100%" alt="foreignObject test"></picture>

## T14 · SMIL animation inside an SVG

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/smil-dark.svg"><img src="assets/smil-light.svg" width="100%" alt="SMIL test"></picture>

## T15 · Text wrapping beside a floated image

<img src="assets/tile3-dark.svg" width="40%" align="right" alt="Floated right">

Real text on the left of a picture that floats right. If floats survive, this paragraph wraps beside the image
instead of sitting under it. Links work: [TopPresenter](https://github.com/RobyRew/TopPresenter), [mapswitch](https://github.com/RobyRew/mapswitch).

<br clear="all">

## T16 · Footnotes and task list

Footnote at the end of this sentence.[^1]

- [x] Done item
- [ ] Open item

[^1]: Footnotes jump to the bottom and back.

## T17 · Anchor link

[Back to the top ↑](#top)

## T18 · Mermaid diagram with links

```mermaid
flowchart LR
    A[Profile README] --> B{{Refresh workflow}}
    B --> C[Cards as SVG]
    B --> D[Live deck on Pages]
    click A "https://github.com/RobyRew" "Open the profile"
    click D "https://robyrew.github.io/RobyRew/" "Open the live deck"
```

## T19 · Interactive map

```geojson
{
  "type": "FeatureCollection",
  "features": [
    {"type": "Feature", "properties": {"name": "Barcelona", "marker-color": "#FF6A2B"},
     "geometry": {"type": "Point", "coordinates": [2.1734, 41.3851]}}
  ]
}
```

## T20 · 3D model you can spin

```stl
solid record
facet normal 0 0 0
 outer loop
  vertex 3.50 0.00 2.00
  vertex 150.00 0.00 2.00
  vertex 147.72 26.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.50 0.00 2.00
  vertex 147.72 26.05 2.00
  vertex 3.45 0.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.50 0.00 0.00
  vertex 147.72 26.05 0.00
  vertex 150.00 0.00 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.50 0.00 0.00
  vertex 3.45 0.61 0.00
  vertex 147.72 26.05 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 150.00 0.00 0.00
  vertex 147.72 26.05 0.00
  vertex 147.72 26.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 150.00 0.00 0.00
  vertex 147.72 26.05 2.00
  vertex 150.00 0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.50 0.00 0.00
  vertex 3.45 0.61 2.00
  vertex 3.45 0.61 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.50 0.00 0.00
  vertex 3.50 0.00 2.00
  vertex 3.45 0.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 0.61 2.00
  vertex 147.72 26.05 2.00
  vertex 140.95 51.30 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 0.61 2.00
  vertex 140.95 51.30 2.00
  vertex 3.29 1.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 0.61 0.00
  vertex 140.95 51.30 0.00
  vertex 147.72 26.05 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 0.61 0.00
  vertex 3.29 1.20 0.00
  vertex 140.95 51.30 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 147.72 26.05 0.00
  vertex 140.95 51.30 0.00
  vertex 140.95 51.30 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 147.72 26.05 0.00
  vertex 140.95 51.30 2.00
  vertex 147.72 26.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 0.61 0.00
  vertex 3.29 1.20 2.00
  vertex 3.29 1.20 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 0.61 0.00
  vertex 3.45 0.61 2.00
  vertex 3.29 1.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 1.20 2.00
  vertex 140.95 51.30 2.00
  vertex 129.90 75.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 1.20 2.00
  vertex 129.90 75.00 2.00
  vertex 3.03 1.75 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 1.20 0.00
  vertex 129.90 75.00 0.00
  vertex 140.95 51.30 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 1.20 0.00
  vertex 3.03 1.75 0.00
  vertex 129.90 75.00 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 140.95 51.30 0.00
  vertex 129.90 75.00 0.00
  vertex 129.90 75.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 140.95 51.30 0.00
  vertex 129.90 75.00 2.00
  vertex 140.95 51.30 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 1.20 0.00
  vertex 3.03 1.75 2.00
  vertex 3.03 1.75 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 1.20 0.00
  vertex 3.29 1.20 2.00
  vertex 3.03 1.75 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 1.75 2.00
  vertex 129.90 75.00 2.00
  vertex 114.91 96.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 1.75 2.00
  vertex 114.91 96.42 2.00
  vertex 2.68 2.25 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 1.75 0.00
  vertex 114.91 96.42 0.00
  vertex 129.90 75.00 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 1.75 0.00
  vertex 2.68 2.25 0.00
  vertex 114.91 96.42 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 129.90 75.00 0.00
  vertex 114.91 96.42 0.00
  vertex 114.91 96.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 129.90 75.00 0.00
  vertex 114.91 96.42 2.00
  vertex 129.90 75.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 1.75 0.00
  vertex 2.68 2.25 2.00
  vertex 2.68 2.25 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 1.75 0.00
  vertex 3.03 1.75 2.00
  vertex 2.68 2.25 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 2.25 2.00
  vertex 114.91 96.42 2.00
  vertex 96.42 114.91 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 2.25 2.00
  vertex 96.42 114.91 2.00
  vertex 2.25 2.68 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 2.25 0.00
  vertex 96.42 114.91 0.00
  vertex 114.91 96.42 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 2.25 0.00
  vertex 2.25 2.68 0.00
  vertex 96.42 114.91 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 114.91 96.42 0.00
  vertex 96.42 114.91 0.00
  vertex 96.42 114.91 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 114.91 96.42 0.00
  vertex 96.42 114.91 2.00
  vertex 114.91 96.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 2.25 0.00
  vertex 2.25 2.68 2.00
  vertex 2.25 2.68 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 2.25 0.00
  vertex 2.68 2.25 2.00
  vertex 2.25 2.68 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 2.68 2.00
  vertex 96.42 114.91 2.00
  vertex 75.00 129.90 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 2.68 2.00
  vertex 75.00 129.90 2.00
  vertex 1.75 3.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 2.68 0.00
  vertex 75.00 129.90 0.00
  vertex 96.42 114.91 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 2.68 0.00
  vertex 1.75 3.03 0.00
  vertex 75.00 129.90 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 96.42 114.91 0.00
  vertex 75.00 129.90 0.00
  vertex 75.00 129.90 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 96.42 114.91 0.00
  vertex 75.00 129.90 2.00
  vertex 96.42 114.91 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 2.68 0.00
  vertex 1.75 3.03 2.00
  vertex 1.75 3.03 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 2.68 0.00
  vertex 2.25 2.68 2.00
  vertex 1.75 3.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 3.03 2.00
  vertex 75.00 129.90 2.00
  vertex 51.30 140.95 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 3.03 2.00
  vertex 51.30 140.95 2.00
  vertex 1.20 3.29 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 3.03 0.00
  vertex 51.30 140.95 0.00
  vertex 75.00 129.90 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 3.03 0.00
  vertex 1.20 3.29 0.00
  vertex 51.30 140.95 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 75.00 129.90 0.00
  vertex 51.30 140.95 0.00
  vertex 51.30 140.95 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 75.00 129.90 0.00
  vertex 51.30 140.95 2.00
  vertex 75.00 129.90 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 3.03 0.00
  vertex 1.20 3.29 2.00
  vertex 1.20 3.29 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 3.03 0.00
  vertex 1.75 3.03 2.00
  vertex 1.20 3.29 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 3.29 2.00
  vertex 51.30 140.95 2.00
  vertex 26.05 147.72 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 3.29 2.00
  vertex 26.05 147.72 2.00
  vertex 0.61 3.45 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 3.29 0.00
  vertex 26.05 147.72 0.00
  vertex 51.30 140.95 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 3.29 0.00
  vertex 0.61 3.45 0.00
  vertex 26.05 147.72 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 51.30 140.95 0.00
  vertex 26.05 147.72 0.00
  vertex 26.05 147.72 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 51.30 140.95 0.00
  vertex 26.05 147.72 2.00
  vertex 51.30 140.95 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 3.29 0.00
  vertex 0.61 3.45 2.00
  vertex 0.61 3.45 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 3.29 0.00
  vertex 1.20 3.29 2.00
  vertex 0.61 3.45 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 3.45 2.00
  vertex 26.05 147.72 2.00
  vertex 0.00 150.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 3.45 2.00
  vertex 0.00 150.00 2.00
  vertex 0.00 3.50 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 3.45 0.00
  vertex 0.00 150.00 0.00
  vertex 26.05 147.72 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 3.45 0.00
  vertex 0.00 3.50 0.00
  vertex 0.00 150.00 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 26.05 147.72 0.00
  vertex 0.00 150.00 0.00
  vertex 0.00 150.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 26.05 147.72 0.00
  vertex 0.00 150.00 2.00
  vertex 26.05 147.72 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 3.45 0.00
  vertex 0.00 3.50 2.00
  vertex 0.00 3.50 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 3.45 0.00
  vertex 0.61 3.45 2.00
  vertex 0.00 3.50 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 3.50 2.00
  vertex 0.00 150.00 2.00
  vertex -26.05 147.72 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 3.50 2.00
  vertex -26.05 147.72 2.00
  vertex -0.61 3.45 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 3.50 0.00
  vertex -26.05 147.72 0.00
  vertex 0.00 150.00 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 3.50 0.00
  vertex -0.61 3.45 0.00
  vertex -26.05 147.72 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 150.00 0.00
  vertex -26.05 147.72 0.00
  vertex -26.05 147.72 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 150.00 0.00
  vertex -26.05 147.72 2.00
  vertex 0.00 150.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 3.50 0.00
  vertex -0.61 3.45 2.00
  vertex -0.61 3.45 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 3.50 0.00
  vertex 0.00 3.50 2.00
  vertex -0.61 3.45 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 3.45 2.00
  vertex -26.05 147.72 2.00
  vertex -51.30 140.95 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 3.45 2.00
  vertex -51.30 140.95 2.00
  vertex -1.20 3.29 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 3.45 0.00
  vertex -51.30 140.95 0.00
  vertex -26.05 147.72 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 3.45 0.00
  vertex -1.20 3.29 0.00
  vertex -51.30 140.95 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -26.05 147.72 0.00
  vertex -51.30 140.95 0.00
  vertex -51.30 140.95 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -26.05 147.72 0.00
  vertex -51.30 140.95 2.00
  vertex -26.05 147.72 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 3.45 0.00
  vertex -1.20 3.29 2.00
  vertex -1.20 3.29 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 3.45 0.00
  vertex -0.61 3.45 2.00
  vertex -1.20 3.29 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 3.29 2.00
  vertex -51.30 140.95 2.00
  vertex -75.00 129.90 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 3.29 2.00
  vertex -75.00 129.90 2.00
  vertex -1.75 3.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 3.29 0.00
  vertex -75.00 129.90 0.00
  vertex -51.30 140.95 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 3.29 0.00
  vertex -1.75 3.03 0.00
  vertex -75.00 129.90 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -51.30 140.95 0.00
  vertex -75.00 129.90 0.00
  vertex -75.00 129.90 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -51.30 140.95 0.00
  vertex -75.00 129.90 2.00
  vertex -51.30 140.95 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 3.29 0.00
  vertex -1.75 3.03 2.00
  vertex -1.75 3.03 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 3.29 0.00
  vertex -1.20 3.29 2.00
  vertex -1.75 3.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 3.03 2.00
  vertex -75.00 129.90 2.00
  vertex -96.42 114.91 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 3.03 2.00
  vertex -96.42 114.91 2.00
  vertex -2.25 2.68 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 3.03 0.00
  vertex -96.42 114.91 0.00
  vertex -75.00 129.90 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 3.03 0.00
  vertex -2.25 2.68 0.00
  vertex -96.42 114.91 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -75.00 129.90 0.00
  vertex -96.42 114.91 0.00
  vertex -96.42 114.91 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -75.00 129.90 0.00
  vertex -96.42 114.91 2.00
  vertex -75.00 129.90 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 3.03 0.00
  vertex -2.25 2.68 2.00
  vertex -2.25 2.68 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 3.03 0.00
  vertex -1.75 3.03 2.00
  vertex -2.25 2.68 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 2.68 2.00
  vertex -96.42 114.91 2.00
  vertex -114.91 96.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 2.68 2.00
  vertex -114.91 96.42 2.00
  vertex -2.68 2.25 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 2.68 0.00
  vertex -114.91 96.42 0.00
  vertex -96.42 114.91 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 2.68 0.00
  vertex -2.68 2.25 0.00
  vertex -114.91 96.42 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -96.42 114.91 0.00
  vertex -114.91 96.42 0.00
  vertex -114.91 96.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -96.42 114.91 0.00
  vertex -114.91 96.42 2.00
  vertex -96.42 114.91 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 2.68 0.00
  vertex -2.68 2.25 2.00
  vertex -2.68 2.25 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 2.68 0.00
  vertex -2.25 2.68 2.00
  vertex -2.68 2.25 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 2.25 2.00
  vertex -114.91 96.42 2.00
  vertex -129.90 75.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 2.25 2.00
  vertex -129.90 75.00 2.00
  vertex -3.03 1.75 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 2.25 0.00
  vertex -129.90 75.00 0.00
  vertex -114.91 96.42 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 2.25 0.00
  vertex -3.03 1.75 0.00
  vertex -129.90 75.00 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -114.91 96.42 0.00
  vertex -129.90 75.00 0.00
  vertex -129.90 75.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -114.91 96.42 0.00
  vertex -129.90 75.00 2.00
  vertex -114.91 96.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 2.25 0.00
  vertex -3.03 1.75 2.00
  vertex -3.03 1.75 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 2.25 0.00
  vertex -2.68 2.25 2.00
  vertex -3.03 1.75 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 1.75 2.00
  vertex -129.90 75.00 2.00
  vertex -140.95 51.30 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 1.75 2.00
  vertex -140.95 51.30 2.00
  vertex -3.29 1.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 1.75 0.00
  vertex -140.95 51.30 0.00
  vertex -129.90 75.00 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 1.75 0.00
  vertex -3.29 1.20 0.00
  vertex -140.95 51.30 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -129.90 75.00 0.00
  vertex -140.95 51.30 0.00
  vertex -140.95 51.30 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -129.90 75.00 0.00
  vertex -140.95 51.30 2.00
  vertex -129.90 75.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 1.75 0.00
  vertex -3.29 1.20 2.00
  vertex -3.29 1.20 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 1.75 0.00
  vertex -3.03 1.75 2.00
  vertex -3.29 1.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 1.20 2.00
  vertex -140.95 51.30 2.00
  vertex -147.72 26.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 1.20 2.00
  vertex -147.72 26.05 2.00
  vertex -3.45 0.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 1.20 0.00
  vertex -147.72 26.05 0.00
  vertex -140.95 51.30 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 1.20 0.00
  vertex -3.45 0.61 0.00
  vertex -147.72 26.05 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -140.95 51.30 0.00
  vertex -147.72 26.05 0.00
  vertex -147.72 26.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -140.95 51.30 0.00
  vertex -147.72 26.05 2.00
  vertex -140.95 51.30 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 1.20 0.00
  vertex -3.45 0.61 2.00
  vertex -3.45 0.61 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 1.20 0.00
  vertex -3.29 1.20 2.00
  vertex -3.45 0.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 0.61 2.00
  vertex -147.72 26.05 2.00
  vertex -150.00 0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 0.61 2.00
  vertex -150.00 0.00 2.00
  vertex -3.50 0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 0.61 0.00
  vertex -150.00 0.00 0.00
  vertex -147.72 26.05 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 0.61 0.00
  vertex -3.50 0.00 0.00
  vertex -150.00 0.00 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -147.72 26.05 0.00
  vertex -150.00 0.00 0.00
  vertex -150.00 0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -147.72 26.05 0.00
  vertex -150.00 0.00 2.00
  vertex -147.72 26.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 0.61 0.00
  vertex -3.50 0.00 2.00
  vertex -3.50 0.00 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 0.61 0.00
  vertex -3.45 0.61 2.00
  vertex -3.50 0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.50 0.00 2.00
  vertex -150.00 0.00 2.00
  vertex -147.72 -26.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.50 0.00 2.00
  vertex -147.72 -26.05 2.00
  vertex -3.45 -0.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.50 0.00 0.00
  vertex -147.72 -26.05 0.00
  vertex -150.00 0.00 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.50 0.00 0.00
  vertex -3.45 -0.61 0.00
  vertex -147.72 -26.05 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -150.00 0.00 0.00
  vertex -147.72 -26.05 0.00
  vertex -147.72 -26.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -150.00 0.00 0.00
  vertex -147.72 -26.05 2.00
  vertex -150.00 0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.50 0.00 0.00
  vertex -3.45 -0.61 2.00
  vertex -3.45 -0.61 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.50 0.00 0.00
  vertex -3.50 0.00 2.00
  vertex -3.45 -0.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 -0.61 2.00
  vertex -147.72 -26.05 2.00
  vertex -140.95 -51.30 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 -0.61 2.00
  vertex -140.95 -51.30 2.00
  vertex -3.29 -1.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 -0.61 0.00
  vertex -140.95 -51.30 0.00
  vertex -147.72 -26.05 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 -0.61 0.00
  vertex -3.29 -1.20 0.00
  vertex -140.95 -51.30 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -147.72 -26.05 0.00
  vertex -140.95 -51.30 0.00
  vertex -140.95 -51.30 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -147.72 -26.05 0.00
  vertex -140.95 -51.30 2.00
  vertex -147.72 -26.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 -0.61 0.00
  vertex -3.29 -1.20 2.00
  vertex -3.29 -1.20 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 -0.61 0.00
  vertex -3.45 -0.61 2.00
  vertex -3.29 -1.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 -1.20 2.00
  vertex -140.95 -51.30 2.00
  vertex -129.90 -75.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 -1.20 2.00
  vertex -129.90 -75.00 2.00
  vertex -3.03 -1.75 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 -1.20 0.00
  vertex -129.90 -75.00 0.00
  vertex -140.95 -51.30 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 -1.20 0.00
  vertex -3.03 -1.75 0.00
  vertex -129.90 -75.00 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -140.95 -51.30 0.00
  vertex -129.90 -75.00 0.00
  vertex -129.90 -75.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -140.95 -51.30 0.00
  vertex -129.90 -75.00 2.00
  vertex -140.95 -51.30 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 -1.20 0.00
  vertex -3.03 -1.75 2.00
  vertex -3.03 -1.75 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 -1.20 0.00
  vertex -3.29 -1.20 2.00
  vertex -3.03 -1.75 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 -1.75 2.00
  vertex -129.90 -75.00 2.00
  vertex -114.91 -96.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 -1.75 2.00
  vertex -114.91 -96.42 2.00
  vertex -2.68 -2.25 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 -1.75 0.00
  vertex -114.91 -96.42 0.00
  vertex -129.90 -75.00 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 -1.75 0.00
  vertex -2.68 -2.25 0.00
  vertex -114.91 -96.42 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -129.90 -75.00 0.00
  vertex -114.91 -96.42 0.00
  vertex -114.91 -96.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -129.90 -75.00 0.00
  vertex -114.91 -96.42 2.00
  vertex -129.90 -75.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 -1.75 0.00
  vertex -2.68 -2.25 2.00
  vertex -2.68 -2.25 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 -1.75 0.00
  vertex -3.03 -1.75 2.00
  vertex -2.68 -2.25 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 -2.25 2.00
  vertex -114.91 -96.42 2.00
  vertex -96.42 -114.91 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 -2.25 2.00
  vertex -96.42 -114.91 2.00
  vertex -2.25 -2.68 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 -2.25 0.00
  vertex -96.42 -114.91 0.00
  vertex -114.91 -96.42 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 -2.25 0.00
  vertex -2.25 -2.68 0.00
  vertex -96.42 -114.91 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -114.91 -96.42 0.00
  vertex -96.42 -114.91 0.00
  vertex -96.42 -114.91 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -114.91 -96.42 0.00
  vertex -96.42 -114.91 2.00
  vertex -114.91 -96.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 -2.25 0.00
  vertex -2.25 -2.68 2.00
  vertex -2.25 -2.68 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 -2.25 0.00
  vertex -2.68 -2.25 2.00
  vertex -2.25 -2.68 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 -2.68 2.00
  vertex -96.42 -114.91 2.00
  vertex -75.00 -129.90 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 -2.68 2.00
  vertex -75.00 -129.90 2.00
  vertex -1.75 -3.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 -2.68 0.00
  vertex -75.00 -129.90 0.00
  vertex -96.42 -114.91 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 -2.68 0.00
  vertex -1.75 -3.03 0.00
  vertex -75.00 -129.90 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -96.42 -114.91 0.00
  vertex -75.00 -129.90 0.00
  vertex -75.00 -129.90 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -96.42 -114.91 0.00
  vertex -75.00 -129.90 2.00
  vertex -96.42 -114.91 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 -2.68 0.00
  vertex -1.75 -3.03 2.00
  vertex -1.75 -3.03 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 -2.68 0.00
  vertex -2.25 -2.68 2.00
  vertex -1.75 -3.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 -3.03 2.00
  vertex -75.00 -129.90 2.00
  vertex -51.30 -140.95 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 -3.03 2.00
  vertex -51.30 -140.95 2.00
  vertex -1.20 -3.29 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 -3.03 0.00
  vertex -51.30 -140.95 0.00
  vertex -75.00 -129.90 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 -3.03 0.00
  vertex -1.20 -3.29 0.00
  vertex -51.30 -140.95 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -75.00 -129.90 0.00
  vertex -51.30 -140.95 0.00
  vertex -51.30 -140.95 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -75.00 -129.90 0.00
  vertex -51.30 -140.95 2.00
  vertex -75.00 -129.90 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 -3.03 0.00
  vertex -1.20 -3.29 2.00
  vertex -1.20 -3.29 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 -3.03 0.00
  vertex -1.75 -3.03 2.00
  vertex -1.20 -3.29 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 -3.29 2.00
  vertex -51.30 -140.95 2.00
  vertex -26.05 -147.72 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 -3.29 2.00
  vertex -26.05 -147.72 2.00
  vertex -0.61 -3.45 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 -3.29 0.00
  vertex -26.05 -147.72 0.00
  vertex -51.30 -140.95 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 -3.29 0.00
  vertex -0.61 -3.45 0.00
  vertex -26.05 -147.72 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -51.30 -140.95 0.00
  vertex -26.05 -147.72 0.00
  vertex -26.05 -147.72 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -51.30 -140.95 0.00
  vertex -26.05 -147.72 2.00
  vertex -51.30 -140.95 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 -3.29 0.00
  vertex -0.61 -3.45 2.00
  vertex -0.61 -3.45 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 -3.29 0.00
  vertex -1.20 -3.29 2.00
  vertex -0.61 -3.45 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 -3.45 2.00
  vertex -26.05 -147.72 2.00
  vertex -0.00 -150.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 -3.45 2.00
  vertex -0.00 -150.00 2.00
  vertex -0.00 -3.50 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 -3.45 0.00
  vertex -0.00 -150.00 0.00
  vertex -26.05 -147.72 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 -3.45 0.00
  vertex -0.00 -3.50 0.00
  vertex -0.00 -150.00 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -26.05 -147.72 0.00
  vertex -0.00 -150.00 0.00
  vertex -0.00 -150.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -26.05 -147.72 0.00
  vertex -0.00 -150.00 2.00
  vertex -26.05 -147.72 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 -3.45 0.00
  vertex -0.00 -3.50 2.00
  vertex -0.00 -3.50 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 -3.45 0.00
  vertex -0.61 -3.45 2.00
  vertex -0.00 -3.50 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -3.50 2.00
  vertex -0.00 -150.00 2.00
  vertex 26.05 -147.72 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -3.50 2.00
  vertex 26.05 -147.72 2.00
  vertex 0.61 -3.45 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -3.50 0.00
  vertex 26.05 -147.72 0.00
  vertex -0.00 -150.00 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -3.50 0.00
  vertex 0.61 -3.45 0.00
  vertex 26.05 -147.72 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -150.00 0.00
  vertex 26.05 -147.72 0.00
  vertex 26.05 -147.72 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -150.00 0.00
  vertex 26.05 -147.72 2.00
  vertex -0.00 -150.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -3.50 0.00
  vertex 0.61 -3.45 2.00
  vertex 0.61 -3.45 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -3.50 0.00
  vertex -0.00 -3.50 2.00
  vertex 0.61 -3.45 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 -3.45 2.00
  vertex 26.05 -147.72 2.00
  vertex 51.30 -140.95 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 -3.45 2.00
  vertex 51.30 -140.95 2.00
  vertex 1.20 -3.29 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 -3.45 0.00
  vertex 51.30 -140.95 0.00
  vertex 26.05 -147.72 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 -3.45 0.00
  vertex 1.20 -3.29 0.00
  vertex 51.30 -140.95 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 26.05 -147.72 0.00
  vertex 51.30 -140.95 0.00
  vertex 51.30 -140.95 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 26.05 -147.72 0.00
  vertex 51.30 -140.95 2.00
  vertex 26.05 -147.72 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 -3.45 0.00
  vertex 1.20 -3.29 2.00
  vertex 1.20 -3.29 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 -3.45 0.00
  vertex 0.61 -3.45 2.00
  vertex 1.20 -3.29 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 -3.29 2.00
  vertex 51.30 -140.95 2.00
  vertex 75.00 -129.90 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 -3.29 2.00
  vertex 75.00 -129.90 2.00
  vertex 1.75 -3.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 -3.29 0.00
  vertex 75.00 -129.90 0.00
  vertex 51.30 -140.95 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 -3.29 0.00
  vertex 1.75 -3.03 0.00
  vertex 75.00 -129.90 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 51.30 -140.95 0.00
  vertex 75.00 -129.90 0.00
  vertex 75.00 -129.90 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 51.30 -140.95 0.00
  vertex 75.00 -129.90 2.00
  vertex 51.30 -140.95 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 -3.29 0.00
  vertex 1.75 -3.03 2.00
  vertex 1.75 -3.03 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 -3.29 0.00
  vertex 1.20 -3.29 2.00
  vertex 1.75 -3.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 -3.03 2.00
  vertex 75.00 -129.90 2.00
  vertex 96.42 -114.91 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 -3.03 2.00
  vertex 96.42 -114.91 2.00
  vertex 2.25 -2.68 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 -3.03 0.00
  vertex 96.42 -114.91 0.00
  vertex 75.00 -129.90 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 -3.03 0.00
  vertex 2.25 -2.68 0.00
  vertex 96.42 -114.91 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 75.00 -129.90 0.00
  vertex 96.42 -114.91 0.00
  vertex 96.42 -114.91 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 75.00 -129.90 0.00
  vertex 96.42 -114.91 2.00
  vertex 75.00 -129.90 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 -3.03 0.00
  vertex 2.25 -2.68 2.00
  vertex 2.25 -2.68 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 -3.03 0.00
  vertex 1.75 -3.03 2.00
  vertex 2.25 -2.68 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 -2.68 2.00
  vertex 96.42 -114.91 2.00
  vertex 114.91 -96.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 -2.68 2.00
  vertex 114.91 -96.42 2.00
  vertex 2.68 -2.25 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 -2.68 0.00
  vertex 114.91 -96.42 0.00
  vertex 96.42 -114.91 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 -2.68 0.00
  vertex 2.68 -2.25 0.00
  vertex 114.91 -96.42 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 96.42 -114.91 0.00
  vertex 114.91 -96.42 0.00
  vertex 114.91 -96.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 96.42 -114.91 0.00
  vertex 114.91 -96.42 2.00
  vertex 96.42 -114.91 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 -2.68 0.00
  vertex 2.68 -2.25 2.00
  vertex 2.68 -2.25 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 -2.68 0.00
  vertex 2.25 -2.68 2.00
  vertex 2.68 -2.25 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 -2.25 2.00
  vertex 114.91 -96.42 2.00
  vertex 129.90 -75.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 -2.25 2.00
  vertex 129.90 -75.00 2.00
  vertex 3.03 -1.75 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 -2.25 0.00
  vertex 129.90 -75.00 0.00
  vertex 114.91 -96.42 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 -2.25 0.00
  vertex 3.03 -1.75 0.00
  vertex 129.90 -75.00 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 114.91 -96.42 0.00
  vertex 129.90 -75.00 0.00
  vertex 129.90 -75.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 114.91 -96.42 0.00
  vertex 129.90 -75.00 2.00
  vertex 114.91 -96.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 -2.25 0.00
  vertex 3.03 -1.75 2.00
  vertex 3.03 -1.75 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 -2.25 0.00
  vertex 2.68 -2.25 2.00
  vertex 3.03 -1.75 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 -1.75 2.00
  vertex 129.90 -75.00 2.00
  vertex 140.95 -51.30 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 -1.75 2.00
  vertex 140.95 -51.30 2.00
  vertex 3.29 -1.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 -1.75 0.00
  vertex 140.95 -51.30 0.00
  vertex 129.90 -75.00 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 -1.75 0.00
  vertex 3.29 -1.20 0.00
  vertex 140.95 -51.30 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 129.90 -75.00 0.00
  vertex 140.95 -51.30 0.00
  vertex 140.95 -51.30 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 129.90 -75.00 0.00
  vertex 140.95 -51.30 2.00
  vertex 129.90 -75.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 -1.75 0.00
  vertex 3.29 -1.20 2.00
  vertex 3.29 -1.20 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 -1.75 0.00
  vertex 3.03 -1.75 2.00
  vertex 3.29 -1.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 -1.20 2.00
  vertex 140.95 -51.30 2.00
  vertex 147.72 -26.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 -1.20 2.00
  vertex 147.72 -26.05 2.00
  vertex 3.45 -0.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 -1.20 0.00
  vertex 147.72 -26.05 0.00
  vertex 140.95 -51.30 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 -1.20 0.00
  vertex 3.45 -0.61 0.00
  vertex 147.72 -26.05 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 140.95 -51.30 0.00
  vertex 147.72 -26.05 0.00
  vertex 147.72 -26.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 140.95 -51.30 0.00
  vertex 147.72 -26.05 2.00
  vertex 140.95 -51.30 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 -1.20 0.00
  vertex 3.45 -0.61 2.00
  vertex 3.45 -0.61 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 -1.20 0.00
  vertex 3.29 -1.20 2.00
  vertex 3.45 -0.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 -0.61 2.00
  vertex 147.72 -26.05 2.00
  vertex 150.00 -0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 -0.61 2.00
  vertex 150.00 -0.00 2.00
  vertex 3.50 -0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 -0.61 0.00
  vertex 150.00 -0.00 0.00
  vertex 147.72 -26.05 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 -0.61 0.00
  vertex 3.50 -0.00 0.00
  vertex 150.00 -0.00 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 147.72 -26.05 0.00
  vertex 150.00 -0.00 0.00
  vertex 150.00 -0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 147.72 -26.05 0.00
  vertex 150.00 -0.00 2.00
  vertex 147.72 -26.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 -0.61 0.00
  vertex 3.50 -0.00 2.00
  vertex 3.50 -0.00 0.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 -0.61 0.00
  vertex 3.45 -0.61 2.00
  vertex 3.50 -0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.50 0.00 2.60
  vertex 52.00 0.00 2.60
  vertex 51.21 9.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.50 0.00 2.60
  vertex 51.21 9.03 2.60
  vertex 3.45 0.61 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.50 0.00 2.00
  vertex 51.21 9.03 2.00
  vertex 52.00 0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.50 0.00 2.00
  vertex 3.45 0.61 2.00
  vertex 51.21 9.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 52.00 0.00 2.00
  vertex 51.21 9.03 2.00
  vertex 51.21 9.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 52.00 0.00 2.00
  vertex 51.21 9.03 2.60
  vertex 52.00 0.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.50 0.00 2.00
  vertex 3.45 0.61 2.60
  vertex 3.45 0.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.50 0.00 2.00
  vertex 3.50 0.00 2.60
  vertex 3.45 0.61 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 0.61 2.60
  vertex 51.21 9.03 2.60
  vertex 48.86 17.79 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 0.61 2.60
  vertex 48.86 17.79 2.60
  vertex 3.29 1.20 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 0.61 2.00
  vertex 48.86 17.79 2.00
  vertex 51.21 9.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 0.61 2.00
  vertex 3.29 1.20 2.00
  vertex 48.86 17.79 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 51.21 9.03 2.00
  vertex 48.86 17.79 2.00
  vertex 48.86 17.79 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 51.21 9.03 2.00
  vertex 48.86 17.79 2.60
  vertex 51.21 9.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 0.61 2.00
  vertex 3.29 1.20 2.60
  vertex 3.29 1.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 0.61 2.00
  vertex 3.45 0.61 2.60
  vertex 3.29 1.20 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 1.20 2.60
  vertex 48.86 17.79 2.60
  vertex 45.03 26.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 1.20 2.60
  vertex 45.03 26.00 2.60
  vertex 3.03 1.75 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 1.20 2.00
  vertex 45.03 26.00 2.00
  vertex 48.86 17.79 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 1.20 2.00
  vertex 3.03 1.75 2.00
  vertex 45.03 26.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 48.86 17.79 2.00
  vertex 45.03 26.00 2.00
  vertex 45.03 26.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 48.86 17.79 2.00
  vertex 45.03 26.00 2.60
  vertex 48.86 17.79 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 1.20 2.00
  vertex 3.03 1.75 2.60
  vertex 3.03 1.75 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 1.20 2.00
  vertex 3.29 1.20 2.60
  vertex 3.03 1.75 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 1.75 2.60
  vertex 45.03 26.00 2.60
  vertex 39.83 33.42 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 1.75 2.60
  vertex 39.83 33.42 2.60
  vertex 2.68 2.25 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 1.75 2.00
  vertex 39.83 33.42 2.00
  vertex 45.03 26.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 1.75 2.00
  vertex 2.68 2.25 2.00
  vertex 39.83 33.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 45.03 26.00 2.00
  vertex 39.83 33.42 2.00
  vertex 39.83 33.42 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 45.03 26.00 2.00
  vertex 39.83 33.42 2.60
  vertex 45.03 26.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 1.75 2.00
  vertex 2.68 2.25 2.60
  vertex 2.68 2.25 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 1.75 2.00
  vertex 3.03 1.75 2.60
  vertex 2.68 2.25 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 2.25 2.60
  vertex 39.83 33.42 2.60
  vertex 33.42 39.83 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 2.25 2.60
  vertex 33.42 39.83 2.60
  vertex 2.25 2.68 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 2.25 2.00
  vertex 33.42 39.83 2.00
  vertex 39.83 33.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 2.25 2.00
  vertex 2.25 2.68 2.00
  vertex 33.42 39.83 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 39.83 33.42 2.00
  vertex 33.42 39.83 2.00
  vertex 33.42 39.83 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 39.83 33.42 2.00
  vertex 33.42 39.83 2.60
  vertex 39.83 33.42 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 2.25 2.00
  vertex 2.25 2.68 2.60
  vertex 2.25 2.68 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 2.25 2.00
  vertex 2.68 2.25 2.60
  vertex 2.25 2.68 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 2.68 2.60
  vertex 33.42 39.83 2.60
  vertex 26.00 45.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 2.68 2.60
  vertex 26.00 45.03 2.60
  vertex 1.75 3.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 2.68 2.00
  vertex 26.00 45.03 2.00
  vertex 33.42 39.83 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 2.68 2.00
  vertex 1.75 3.03 2.00
  vertex 26.00 45.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 33.42 39.83 2.00
  vertex 26.00 45.03 2.00
  vertex 26.00 45.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 33.42 39.83 2.00
  vertex 26.00 45.03 2.60
  vertex 33.42 39.83 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 2.68 2.00
  vertex 1.75 3.03 2.60
  vertex 1.75 3.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 2.68 2.00
  vertex 2.25 2.68 2.60
  vertex 1.75 3.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 3.03 2.60
  vertex 26.00 45.03 2.60
  vertex 17.79 48.86 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 3.03 2.60
  vertex 17.79 48.86 2.60
  vertex 1.20 3.29 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 3.03 2.00
  vertex 17.79 48.86 2.00
  vertex 26.00 45.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 3.03 2.00
  vertex 1.20 3.29 2.00
  vertex 17.79 48.86 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 26.00 45.03 2.00
  vertex 17.79 48.86 2.00
  vertex 17.79 48.86 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 26.00 45.03 2.00
  vertex 17.79 48.86 2.60
  vertex 26.00 45.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 3.03 2.00
  vertex 1.20 3.29 2.60
  vertex 1.20 3.29 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 3.03 2.00
  vertex 1.75 3.03 2.60
  vertex 1.20 3.29 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 3.29 2.60
  vertex 17.79 48.86 2.60
  vertex 9.03 51.21 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 3.29 2.60
  vertex 9.03 51.21 2.60
  vertex 0.61 3.45 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 3.29 2.00
  vertex 9.03 51.21 2.00
  vertex 17.79 48.86 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 3.29 2.00
  vertex 0.61 3.45 2.00
  vertex 9.03 51.21 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.79 48.86 2.00
  vertex 9.03 51.21 2.00
  vertex 9.03 51.21 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.79 48.86 2.00
  vertex 9.03 51.21 2.60
  vertex 17.79 48.86 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 3.29 2.00
  vertex 0.61 3.45 2.60
  vertex 0.61 3.45 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 3.29 2.00
  vertex 1.20 3.29 2.60
  vertex 0.61 3.45 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 3.45 2.60
  vertex 9.03 51.21 2.60
  vertex 0.00 52.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 3.45 2.60
  vertex 0.00 52.00 2.60
  vertex 0.00 3.50 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 3.45 2.00
  vertex 0.00 52.00 2.00
  vertex 9.03 51.21 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 3.45 2.00
  vertex 0.00 3.50 2.00
  vertex 0.00 52.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 9.03 51.21 2.00
  vertex 0.00 52.00 2.00
  vertex 0.00 52.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 9.03 51.21 2.00
  vertex 0.00 52.00 2.60
  vertex 9.03 51.21 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 3.45 2.00
  vertex 0.00 3.50 2.60
  vertex 0.00 3.50 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 3.45 2.00
  vertex 0.61 3.45 2.60
  vertex 0.00 3.50 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 3.50 2.60
  vertex 0.00 52.00 2.60
  vertex -9.03 51.21 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 3.50 2.60
  vertex -9.03 51.21 2.60
  vertex -0.61 3.45 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 3.50 2.00
  vertex -9.03 51.21 2.00
  vertex 0.00 52.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 3.50 2.00
  vertex -0.61 3.45 2.00
  vertex -9.03 51.21 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 52.00 2.00
  vertex -9.03 51.21 2.00
  vertex -9.03 51.21 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 52.00 2.00
  vertex -9.03 51.21 2.60
  vertex 0.00 52.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 3.50 2.00
  vertex -0.61 3.45 2.60
  vertex -0.61 3.45 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 3.50 2.00
  vertex 0.00 3.50 2.60
  vertex -0.61 3.45 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 3.45 2.60
  vertex -9.03 51.21 2.60
  vertex -17.79 48.86 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 3.45 2.60
  vertex -17.79 48.86 2.60
  vertex -1.20 3.29 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 3.45 2.00
  vertex -17.79 48.86 2.00
  vertex -9.03 51.21 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 3.45 2.00
  vertex -1.20 3.29 2.00
  vertex -17.79 48.86 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -9.03 51.21 2.00
  vertex -17.79 48.86 2.00
  vertex -17.79 48.86 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -9.03 51.21 2.00
  vertex -17.79 48.86 2.60
  vertex -9.03 51.21 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 3.45 2.00
  vertex -1.20 3.29 2.60
  vertex -1.20 3.29 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 3.45 2.00
  vertex -0.61 3.45 2.60
  vertex -1.20 3.29 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 3.29 2.60
  vertex -17.79 48.86 2.60
  vertex -26.00 45.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 3.29 2.60
  vertex -26.00 45.03 2.60
  vertex -1.75 3.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 3.29 2.00
  vertex -26.00 45.03 2.00
  vertex -17.79 48.86 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 3.29 2.00
  vertex -1.75 3.03 2.00
  vertex -26.00 45.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.79 48.86 2.00
  vertex -26.00 45.03 2.00
  vertex -26.00 45.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.79 48.86 2.00
  vertex -26.00 45.03 2.60
  vertex -17.79 48.86 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 3.29 2.00
  vertex -1.75 3.03 2.60
  vertex -1.75 3.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 3.29 2.00
  vertex -1.20 3.29 2.60
  vertex -1.75 3.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 3.03 2.60
  vertex -26.00 45.03 2.60
  vertex -33.42 39.83 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 3.03 2.60
  vertex -33.42 39.83 2.60
  vertex -2.25 2.68 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 3.03 2.00
  vertex -33.42 39.83 2.00
  vertex -26.00 45.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 3.03 2.00
  vertex -2.25 2.68 2.00
  vertex -33.42 39.83 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -26.00 45.03 2.00
  vertex -33.42 39.83 2.00
  vertex -33.42 39.83 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -26.00 45.03 2.00
  vertex -33.42 39.83 2.60
  vertex -26.00 45.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 3.03 2.00
  vertex -2.25 2.68 2.60
  vertex -2.25 2.68 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 3.03 2.00
  vertex -1.75 3.03 2.60
  vertex -2.25 2.68 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 2.68 2.60
  vertex -33.42 39.83 2.60
  vertex -39.83 33.42 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 2.68 2.60
  vertex -39.83 33.42 2.60
  vertex -2.68 2.25 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 2.68 2.00
  vertex -39.83 33.42 2.00
  vertex -33.42 39.83 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 2.68 2.00
  vertex -2.68 2.25 2.00
  vertex -39.83 33.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -33.42 39.83 2.00
  vertex -39.83 33.42 2.00
  vertex -39.83 33.42 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -33.42 39.83 2.00
  vertex -39.83 33.42 2.60
  vertex -33.42 39.83 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 2.68 2.00
  vertex -2.68 2.25 2.60
  vertex -2.68 2.25 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 2.68 2.00
  vertex -2.25 2.68 2.60
  vertex -2.68 2.25 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 2.25 2.60
  vertex -39.83 33.42 2.60
  vertex -45.03 26.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 2.25 2.60
  vertex -45.03 26.00 2.60
  vertex -3.03 1.75 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 2.25 2.00
  vertex -45.03 26.00 2.00
  vertex -39.83 33.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 2.25 2.00
  vertex -3.03 1.75 2.00
  vertex -45.03 26.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -39.83 33.42 2.00
  vertex -45.03 26.00 2.00
  vertex -45.03 26.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -39.83 33.42 2.00
  vertex -45.03 26.00 2.60
  vertex -39.83 33.42 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 2.25 2.00
  vertex -3.03 1.75 2.60
  vertex -3.03 1.75 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 2.25 2.00
  vertex -2.68 2.25 2.60
  vertex -3.03 1.75 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 1.75 2.60
  vertex -45.03 26.00 2.60
  vertex -48.86 17.79 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 1.75 2.60
  vertex -48.86 17.79 2.60
  vertex -3.29 1.20 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 1.75 2.00
  vertex -48.86 17.79 2.00
  vertex -45.03 26.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 1.75 2.00
  vertex -3.29 1.20 2.00
  vertex -48.86 17.79 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -45.03 26.00 2.00
  vertex -48.86 17.79 2.00
  vertex -48.86 17.79 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -45.03 26.00 2.00
  vertex -48.86 17.79 2.60
  vertex -45.03 26.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 1.75 2.00
  vertex -3.29 1.20 2.60
  vertex -3.29 1.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 1.75 2.00
  vertex -3.03 1.75 2.60
  vertex -3.29 1.20 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 1.20 2.60
  vertex -48.86 17.79 2.60
  vertex -51.21 9.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 1.20 2.60
  vertex -51.21 9.03 2.60
  vertex -3.45 0.61 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 1.20 2.00
  vertex -51.21 9.03 2.00
  vertex -48.86 17.79 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 1.20 2.00
  vertex -3.45 0.61 2.00
  vertex -51.21 9.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -48.86 17.79 2.00
  vertex -51.21 9.03 2.00
  vertex -51.21 9.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -48.86 17.79 2.00
  vertex -51.21 9.03 2.60
  vertex -48.86 17.79 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 1.20 2.00
  vertex -3.45 0.61 2.60
  vertex -3.45 0.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 1.20 2.00
  vertex -3.29 1.20 2.60
  vertex -3.45 0.61 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 0.61 2.60
  vertex -51.21 9.03 2.60
  vertex -52.00 0.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 0.61 2.60
  vertex -52.00 0.00 2.60
  vertex -3.50 0.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 0.61 2.00
  vertex -52.00 0.00 2.00
  vertex -51.21 9.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 0.61 2.00
  vertex -3.50 0.00 2.00
  vertex -52.00 0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -51.21 9.03 2.00
  vertex -52.00 0.00 2.00
  vertex -52.00 0.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -51.21 9.03 2.00
  vertex -52.00 0.00 2.60
  vertex -51.21 9.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 0.61 2.00
  vertex -3.50 0.00 2.60
  vertex -3.50 0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 0.61 2.00
  vertex -3.45 0.61 2.60
  vertex -3.50 0.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.50 0.00 2.60
  vertex -52.00 0.00 2.60
  vertex -51.21 -9.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.50 0.00 2.60
  vertex -51.21 -9.03 2.60
  vertex -3.45 -0.61 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.50 0.00 2.00
  vertex -51.21 -9.03 2.00
  vertex -52.00 0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.50 0.00 2.00
  vertex -3.45 -0.61 2.00
  vertex -51.21 -9.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -52.00 0.00 2.00
  vertex -51.21 -9.03 2.00
  vertex -51.21 -9.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -52.00 0.00 2.00
  vertex -51.21 -9.03 2.60
  vertex -52.00 0.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.50 0.00 2.00
  vertex -3.45 -0.61 2.60
  vertex -3.45 -0.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.50 0.00 2.00
  vertex -3.50 0.00 2.60
  vertex -3.45 -0.61 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 -0.61 2.60
  vertex -51.21 -9.03 2.60
  vertex -48.86 -17.79 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 -0.61 2.60
  vertex -48.86 -17.79 2.60
  vertex -3.29 -1.20 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 -0.61 2.00
  vertex -48.86 -17.79 2.00
  vertex -51.21 -9.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 -0.61 2.00
  vertex -3.29 -1.20 2.00
  vertex -48.86 -17.79 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -51.21 -9.03 2.00
  vertex -48.86 -17.79 2.00
  vertex -48.86 -17.79 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -51.21 -9.03 2.00
  vertex -48.86 -17.79 2.60
  vertex -51.21 -9.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 -0.61 2.00
  vertex -3.29 -1.20 2.60
  vertex -3.29 -1.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.45 -0.61 2.00
  vertex -3.45 -0.61 2.60
  vertex -3.29 -1.20 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 -1.20 2.60
  vertex -48.86 -17.79 2.60
  vertex -45.03 -26.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 -1.20 2.60
  vertex -45.03 -26.00 2.60
  vertex -3.03 -1.75 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 -1.20 2.00
  vertex -45.03 -26.00 2.00
  vertex -48.86 -17.79 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 -1.20 2.00
  vertex -3.03 -1.75 2.00
  vertex -45.03 -26.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -48.86 -17.79 2.00
  vertex -45.03 -26.00 2.00
  vertex -45.03 -26.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -48.86 -17.79 2.00
  vertex -45.03 -26.00 2.60
  vertex -48.86 -17.79 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 -1.20 2.00
  vertex -3.03 -1.75 2.60
  vertex -3.03 -1.75 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.29 -1.20 2.00
  vertex -3.29 -1.20 2.60
  vertex -3.03 -1.75 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 -1.75 2.60
  vertex -45.03 -26.00 2.60
  vertex -39.83 -33.42 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 -1.75 2.60
  vertex -39.83 -33.42 2.60
  vertex -2.68 -2.25 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 -1.75 2.00
  vertex -39.83 -33.42 2.00
  vertex -45.03 -26.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 -1.75 2.00
  vertex -2.68 -2.25 2.00
  vertex -39.83 -33.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -45.03 -26.00 2.00
  vertex -39.83 -33.42 2.00
  vertex -39.83 -33.42 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -45.03 -26.00 2.00
  vertex -39.83 -33.42 2.60
  vertex -45.03 -26.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 -1.75 2.00
  vertex -2.68 -2.25 2.60
  vertex -2.68 -2.25 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -3.03 -1.75 2.00
  vertex -3.03 -1.75 2.60
  vertex -2.68 -2.25 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 -2.25 2.60
  vertex -39.83 -33.42 2.60
  vertex -33.42 -39.83 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 -2.25 2.60
  vertex -33.42 -39.83 2.60
  vertex -2.25 -2.68 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 -2.25 2.00
  vertex -33.42 -39.83 2.00
  vertex -39.83 -33.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 -2.25 2.00
  vertex -2.25 -2.68 2.00
  vertex -33.42 -39.83 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -39.83 -33.42 2.00
  vertex -33.42 -39.83 2.00
  vertex -33.42 -39.83 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -39.83 -33.42 2.00
  vertex -33.42 -39.83 2.60
  vertex -39.83 -33.42 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 -2.25 2.00
  vertex -2.25 -2.68 2.60
  vertex -2.25 -2.68 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.68 -2.25 2.00
  vertex -2.68 -2.25 2.60
  vertex -2.25 -2.68 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 -2.68 2.60
  vertex -33.42 -39.83 2.60
  vertex -26.00 -45.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 -2.68 2.60
  vertex -26.00 -45.03 2.60
  vertex -1.75 -3.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 -2.68 2.00
  vertex -26.00 -45.03 2.00
  vertex -33.42 -39.83 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 -2.68 2.00
  vertex -1.75 -3.03 2.00
  vertex -26.00 -45.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -33.42 -39.83 2.00
  vertex -26.00 -45.03 2.00
  vertex -26.00 -45.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -33.42 -39.83 2.00
  vertex -26.00 -45.03 2.60
  vertex -33.42 -39.83 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 -2.68 2.00
  vertex -1.75 -3.03 2.60
  vertex -1.75 -3.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -2.25 -2.68 2.00
  vertex -2.25 -2.68 2.60
  vertex -1.75 -3.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 -3.03 2.60
  vertex -26.00 -45.03 2.60
  vertex -17.79 -48.86 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 -3.03 2.60
  vertex -17.79 -48.86 2.60
  vertex -1.20 -3.29 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 -3.03 2.00
  vertex -17.79 -48.86 2.00
  vertex -26.00 -45.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 -3.03 2.00
  vertex -1.20 -3.29 2.00
  vertex -17.79 -48.86 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -26.00 -45.03 2.00
  vertex -17.79 -48.86 2.00
  vertex -17.79 -48.86 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -26.00 -45.03 2.00
  vertex -17.79 -48.86 2.60
  vertex -26.00 -45.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 -3.03 2.00
  vertex -1.20 -3.29 2.60
  vertex -1.20 -3.29 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.75 -3.03 2.00
  vertex -1.75 -3.03 2.60
  vertex -1.20 -3.29 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 -3.29 2.60
  vertex -17.79 -48.86 2.60
  vertex -9.03 -51.21 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 -3.29 2.60
  vertex -9.03 -51.21 2.60
  vertex -0.61 -3.45 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 -3.29 2.00
  vertex -9.03 -51.21 2.00
  vertex -17.79 -48.86 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 -3.29 2.00
  vertex -0.61 -3.45 2.00
  vertex -9.03 -51.21 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.79 -48.86 2.00
  vertex -9.03 -51.21 2.00
  vertex -9.03 -51.21 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.79 -48.86 2.00
  vertex -9.03 -51.21 2.60
  vertex -17.79 -48.86 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 -3.29 2.00
  vertex -0.61 -3.45 2.60
  vertex -0.61 -3.45 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -1.20 -3.29 2.00
  vertex -1.20 -3.29 2.60
  vertex -0.61 -3.45 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 -3.45 2.60
  vertex -9.03 -51.21 2.60
  vertex -0.00 -52.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 -3.45 2.60
  vertex -0.00 -52.00 2.60
  vertex -0.00 -3.50 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 -3.45 2.00
  vertex -0.00 -52.00 2.00
  vertex -9.03 -51.21 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 -3.45 2.00
  vertex -0.00 -3.50 2.00
  vertex -0.00 -52.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -9.03 -51.21 2.00
  vertex -0.00 -52.00 2.00
  vertex -0.00 -52.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -9.03 -51.21 2.00
  vertex -0.00 -52.00 2.60
  vertex -9.03 -51.21 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 -3.45 2.00
  vertex -0.00 -3.50 2.60
  vertex -0.00 -3.50 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.61 -3.45 2.00
  vertex -0.61 -3.45 2.60
  vertex -0.00 -3.50 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -3.50 2.60
  vertex -0.00 -52.00 2.60
  vertex 9.03 -51.21 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -3.50 2.60
  vertex 9.03 -51.21 2.60
  vertex 0.61 -3.45 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -3.50 2.00
  vertex 9.03 -51.21 2.00
  vertex -0.00 -52.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -3.50 2.00
  vertex 0.61 -3.45 2.00
  vertex 9.03 -51.21 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -52.00 2.00
  vertex 9.03 -51.21 2.00
  vertex 9.03 -51.21 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -52.00 2.00
  vertex 9.03 -51.21 2.60
  vertex -0.00 -52.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -3.50 2.00
  vertex 0.61 -3.45 2.60
  vertex 0.61 -3.45 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -3.50 2.00
  vertex -0.00 -3.50 2.60
  vertex 0.61 -3.45 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 -3.45 2.60
  vertex 9.03 -51.21 2.60
  vertex 17.79 -48.86 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 -3.45 2.60
  vertex 17.79 -48.86 2.60
  vertex 1.20 -3.29 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 -3.45 2.00
  vertex 17.79 -48.86 2.00
  vertex 9.03 -51.21 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 -3.45 2.00
  vertex 1.20 -3.29 2.00
  vertex 17.79 -48.86 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 9.03 -51.21 2.00
  vertex 17.79 -48.86 2.00
  vertex 17.79 -48.86 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 9.03 -51.21 2.00
  vertex 17.79 -48.86 2.60
  vertex 9.03 -51.21 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 -3.45 2.00
  vertex 1.20 -3.29 2.60
  vertex 1.20 -3.29 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.61 -3.45 2.00
  vertex 0.61 -3.45 2.60
  vertex 1.20 -3.29 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 -3.29 2.60
  vertex 17.79 -48.86 2.60
  vertex 26.00 -45.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 -3.29 2.60
  vertex 26.00 -45.03 2.60
  vertex 1.75 -3.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 -3.29 2.00
  vertex 26.00 -45.03 2.00
  vertex 17.79 -48.86 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 -3.29 2.00
  vertex 1.75 -3.03 2.00
  vertex 26.00 -45.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.79 -48.86 2.00
  vertex 26.00 -45.03 2.00
  vertex 26.00 -45.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.79 -48.86 2.00
  vertex 26.00 -45.03 2.60
  vertex 17.79 -48.86 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 -3.29 2.00
  vertex 1.75 -3.03 2.60
  vertex 1.75 -3.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.20 -3.29 2.00
  vertex 1.20 -3.29 2.60
  vertex 1.75 -3.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 -3.03 2.60
  vertex 26.00 -45.03 2.60
  vertex 33.42 -39.83 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 -3.03 2.60
  vertex 33.42 -39.83 2.60
  vertex 2.25 -2.68 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 -3.03 2.00
  vertex 33.42 -39.83 2.00
  vertex 26.00 -45.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 -3.03 2.00
  vertex 2.25 -2.68 2.00
  vertex 33.42 -39.83 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 26.00 -45.03 2.00
  vertex 33.42 -39.83 2.00
  vertex 33.42 -39.83 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 26.00 -45.03 2.00
  vertex 33.42 -39.83 2.60
  vertex 26.00 -45.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 -3.03 2.00
  vertex 2.25 -2.68 2.60
  vertex 2.25 -2.68 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1.75 -3.03 2.00
  vertex 1.75 -3.03 2.60
  vertex 2.25 -2.68 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 -2.68 2.60
  vertex 33.42 -39.83 2.60
  vertex 39.83 -33.42 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 -2.68 2.60
  vertex 39.83 -33.42 2.60
  vertex 2.68 -2.25 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 -2.68 2.00
  vertex 39.83 -33.42 2.00
  vertex 33.42 -39.83 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 -2.68 2.00
  vertex 2.68 -2.25 2.00
  vertex 39.83 -33.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 33.42 -39.83 2.00
  vertex 39.83 -33.42 2.00
  vertex 39.83 -33.42 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 33.42 -39.83 2.00
  vertex 39.83 -33.42 2.60
  vertex 33.42 -39.83 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 -2.68 2.00
  vertex 2.68 -2.25 2.60
  vertex 2.68 -2.25 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.25 -2.68 2.00
  vertex 2.25 -2.68 2.60
  vertex 2.68 -2.25 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 -2.25 2.60
  vertex 39.83 -33.42 2.60
  vertex 45.03 -26.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 -2.25 2.60
  vertex 45.03 -26.00 2.60
  vertex 3.03 -1.75 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 -2.25 2.00
  vertex 45.03 -26.00 2.00
  vertex 39.83 -33.42 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 -2.25 2.00
  vertex 3.03 -1.75 2.00
  vertex 45.03 -26.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 39.83 -33.42 2.00
  vertex 45.03 -26.00 2.00
  vertex 45.03 -26.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 39.83 -33.42 2.00
  vertex 45.03 -26.00 2.60
  vertex 39.83 -33.42 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 -2.25 2.00
  vertex 3.03 -1.75 2.60
  vertex 3.03 -1.75 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 2.68 -2.25 2.00
  vertex 2.68 -2.25 2.60
  vertex 3.03 -1.75 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 -1.75 2.60
  vertex 45.03 -26.00 2.60
  vertex 48.86 -17.79 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 -1.75 2.60
  vertex 48.86 -17.79 2.60
  vertex 3.29 -1.20 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 -1.75 2.00
  vertex 48.86 -17.79 2.00
  vertex 45.03 -26.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 -1.75 2.00
  vertex 3.29 -1.20 2.00
  vertex 48.86 -17.79 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 45.03 -26.00 2.00
  vertex 48.86 -17.79 2.00
  vertex 48.86 -17.79 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 45.03 -26.00 2.00
  vertex 48.86 -17.79 2.60
  vertex 45.03 -26.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 -1.75 2.00
  vertex 3.29 -1.20 2.60
  vertex 3.29 -1.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.03 -1.75 2.00
  vertex 3.03 -1.75 2.60
  vertex 3.29 -1.20 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 -1.20 2.60
  vertex 48.86 -17.79 2.60
  vertex 51.21 -9.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 -1.20 2.60
  vertex 51.21 -9.03 2.60
  vertex 3.45 -0.61 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 -1.20 2.00
  vertex 51.21 -9.03 2.00
  vertex 48.86 -17.79 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 -1.20 2.00
  vertex 3.45 -0.61 2.00
  vertex 51.21 -9.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 48.86 -17.79 2.00
  vertex 51.21 -9.03 2.00
  vertex 51.21 -9.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 48.86 -17.79 2.00
  vertex 51.21 -9.03 2.60
  vertex 48.86 -17.79 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 -1.20 2.00
  vertex 3.45 -0.61 2.60
  vertex 3.45 -0.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.29 -1.20 2.00
  vertex 3.29 -1.20 2.60
  vertex 3.45 -0.61 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 -0.61 2.60
  vertex 51.21 -9.03 2.60
  vertex 52.00 -0.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 -0.61 2.60
  vertex 52.00 -0.00 2.60
  vertex 3.50 -0.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 -0.61 2.00
  vertex 52.00 -0.00 2.00
  vertex 51.21 -9.03 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 -0.61 2.00
  vertex 3.50 -0.00 2.00
  vertex 52.00 -0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 51.21 -9.03 2.00
  vertex 52.00 -0.00 2.00
  vertex 52.00 -0.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 51.21 -9.03 2.00
  vertex 52.00 -0.00 2.60
  vertex 51.21 -9.03 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 -0.61 2.00
  vertex 3.50 -0.00 2.60
  vertex 3.50 -0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 3.45 -0.61 2.00
  vertex 3.45 -0.61 2.60
  vertex 3.50 -0.00 2.60
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 100.00 0.00 2.25
  vertex 101.20 0.00 2.25
  vertex 99.66 17.57 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 100.00 0.00 2.25
  vertex 99.66 17.57 2.25
  vertex 98.48 17.36 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 100.00 0.00 2.00
  vertex 99.66 17.57 2.00
  vertex 101.20 0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 100.00 0.00 2.00
  vertex 98.48 17.36 2.00
  vertex 99.66 17.57 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 101.20 0.00 2.00
  vertex 99.66 17.57 2.00
  vertex 99.66 17.57 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 101.20 0.00 2.00
  vertex 99.66 17.57 2.25
  vertex 101.20 0.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 100.00 0.00 2.00
  vertex 98.48 17.36 2.25
  vertex 98.48 17.36 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 100.00 0.00 2.00
  vertex 100.00 0.00 2.25
  vertex 98.48 17.36 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 98.48 17.36 2.25
  vertex 99.66 17.57 2.25
  vertex 95.10 34.61 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 98.48 17.36 2.25
  vertex 95.10 34.61 2.25
  vertex 93.97 34.20 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 98.48 17.36 2.00
  vertex 95.10 34.61 2.00
  vertex 99.66 17.57 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 98.48 17.36 2.00
  vertex 93.97 34.20 2.00
  vertex 95.10 34.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 99.66 17.57 2.00
  vertex 95.10 34.61 2.00
  vertex 95.10 34.61 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 99.66 17.57 2.00
  vertex 95.10 34.61 2.25
  vertex 99.66 17.57 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 98.48 17.36 2.00
  vertex 93.97 34.20 2.25
  vertex 93.97 34.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 98.48 17.36 2.00
  vertex 98.48 17.36 2.25
  vertex 93.97 34.20 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 93.97 34.20 2.25
  vertex 95.10 34.61 2.25
  vertex 87.64 50.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 93.97 34.20 2.25
  vertex 87.64 50.60 2.25
  vertex 86.60 50.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 93.97 34.20 2.00
  vertex 87.64 50.60 2.00
  vertex 95.10 34.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 93.97 34.20 2.00
  vertex 86.60 50.00 2.00
  vertex 87.64 50.60 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 95.10 34.61 2.00
  vertex 87.64 50.60 2.00
  vertex 87.64 50.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 95.10 34.61 2.00
  vertex 87.64 50.60 2.25
  vertex 95.10 34.61 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 93.97 34.20 2.00
  vertex 86.60 50.00 2.25
  vertex 86.60 50.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 93.97 34.20 2.00
  vertex 93.97 34.20 2.25
  vertex 86.60 50.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 86.60 50.00 2.25
  vertex 87.64 50.60 2.25
  vertex 77.52 65.05 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 86.60 50.00 2.25
  vertex 77.52 65.05 2.25
  vertex 76.60 64.28 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 86.60 50.00 2.00
  vertex 77.52 65.05 2.00
  vertex 87.64 50.60 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 86.60 50.00 2.00
  vertex 76.60 64.28 2.00
  vertex 77.52 65.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 87.64 50.60 2.00
  vertex 77.52 65.05 2.00
  vertex 77.52 65.05 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 87.64 50.60 2.00
  vertex 77.52 65.05 2.25
  vertex 87.64 50.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 86.60 50.00 2.00
  vertex 76.60 64.28 2.25
  vertex 76.60 64.28 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 86.60 50.00 2.00
  vertex 86.60 50.00 2.25
  vertex 76.60 64.28 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 76.60 64.28 2.25
  vertex 77.52 65.05 2.25
  vertex 65.05 77.52 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 76.60 64.28 2.25
  vertex 65.05 77.52 2.25
  vertex 64.28 76.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 76.60 64.28 2.00
  vertex 65.05 77.52 2.00
  vertex 77.52 65.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 76.60 64.28 2.00
  vertex 64.28 76.60 2.00
  vertex 65.05 77.52 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 77.52 65.05 2.00
  vertex 65.05 77.52 2.00
  vertex 65.05 77.52 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 77.52 65.05 2.00
  vertex 65.05 77.52 2.25
  vertex 77.52 65.05 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 76.60 64.28 2.00
  vertex 64.28 76.60 2.25
  vertex 64.28 76.60 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 76.60 64.28 2.00
  vertex 76.60 64.28 2.25
  vertex 64.28 76.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 64.28 76.60 2.25
  vertex 65.05 77.52 2.25
  vertex 50.60 87.64 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 64.28 76.60 2.25
  vertex 50.60 87.64 2.25
  vertex 50.00 86.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 64.28 76.60 2.00
  vertex 50.60 87.64 2.00
  vertex 65.05 77.52 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 64.28 76.60 2.00
  vertex 50.00 86.60 2.00
  vertex 50.60 87.64 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 65.05 77.52 2.00
  vertex 50.60 87.64 2.00
  vertex 50.60 87.64 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 65.05 77.52 2.00
  vertex 50.60 87.64 2.25
  vertex 65.05 77.52 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 64.28 76.60 2.00
  vertex 50.00 86.60 2.25
  vertex 50.00 86.60 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 64.28 76.60 2.00
  vertex 64.28 76.60 2.25
  vertex 50.00 86.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 50.00 86.60 2.25
  vertex 50.60 87.64 2.25
  vertex 34.61 95.10 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 50.00 86.60 2.25
  vertex 34.61 95.10 2.25
  vertex 34.20 93.97 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 50.00 86.60 2.00
  vertex 34.61 95.10 2.00
  vertex 50.60 87.64 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 50.00 86.60 2.00
  vertex 34.20 93.97 2.00
  vertex 34.61 95.10 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 50.60 87.64 2.00
  vertex 34.61 95.10 2.00
  vertex 34.61 95.10 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 50.60 87.64 2.00
  vertex 34.61 95.10 2.25
  vertex 50.60 87.64 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 50.00 86.60 2.00
  vertex 34.20 93.97 2.25
  vertex 34.20 93.97 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 50.00 86.60 2.00
  vertex 50.00 86.60 2.25
  vertex 34.20 93.97 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 34.20 93.97 2.25
  vertex 34.61 95.10 2.25
  vertex 17.57 99.66 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 34.20 93.97 2.25
  vertex 17.57 99.66 2.25
  vertex 17.36 98.48 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 34.20 93.97 2.00
  vertex 17.57 99.66 2.00
  vertex 34.61 95.10 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 34.20 93.97 2.00
  vertex 17.36 98.48 2.00
  vertex 17.57 99.66 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 34.61 95.10 2.00
  vertex 17.57 99.66 2.00
  vertex 17.57 99.66 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 34.61 95.10 2.00
  vertex 17.57 99.66 2.25
  vertex 34.61 95.10 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 34.20 93.97 2.00
  vertex 17.36 98.48 2.25
  vertex 17.36 98.48 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 34.20 93.97 2.00
  vertex 34.20 93.97 2.25
  vertex 17.36 98.48 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.36 98.48 2.25
  vertex 17.57 99.66 2.25
  vertex 0.00 101.20 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.36 98.48 2.25
  vertex 0.00 101.20 2.25
  vertex 0.00 100.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.36 98.48 2.00
  vertex 0.00 101.20 2.00
  vertex 17.57 99.66 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.36 98.48 2.00
  vertex 0.00 100.00 2.00
  vertex 0.00 101.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.57 99.66 2.00
  vertex 0.00 101.20 2.00
  vertex 0.00 101.20 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.57 99.66 2.00
  vertex 0.00 101.20 2.25
  vertex 17.57 99.66 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.36 98.48 2.00
  vertex 0.00 100.00 2.25
  vertex 0.00 100.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.36 98.48 2.00
  vertex 17.36 98.48 2.25
  vertex 0.00 100.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 100.00 2.25
  vertex 0.00 101.20 2.25
  vertex -17.57 99.66 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 100.00 2.25
  vertex -17.57 99.66 2.25
  vertex -17.36 98.48 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 100.00 2.00
  vertex -17.57 99.66 2.00
  vertex 0.00 101.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 100.00 2.00
  vertex -17.36 98.48 2.00
  vertex -17.57 99.66 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 101.20 2.00
  vertex -17.57 99.66 2.00
  vertex -17.57 99.66 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 101.20 2.00
  vertex -17.57 99.66 2.25
  vertex 0.00 101.20 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 100.00 2.00
  vertex -17.36 98.48 2.25
  vertex -17.36 98.48 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0.00 100.00 2.00
  vertex 0.00 100.00 2.25
  vertex -17.36 98.48 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.36 98.48 2.25
  vertex -17.57 99.66 2.25
  vertex -34.61 95.10 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.36 98.48 2.25
  vertex -34.61 95.10 2.25
  vertex -34.20 93.97 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.36 98.48 2.00
  vertex -34.61 95.10 2.00
  vertex -17.57 99.66 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.36 98.48 2.00
  vertex -34.20 93.97 2.00
  vertex -34.61 95.10 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.57 99.66 2.00
  vertex -34.61 95.10 2.00
  vertex -34.61 95.10 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.57 99.66 2.00
  vertex -34.61 95.10 2.25
  vertex -17.57 99.66 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.36 98.48 2.00
  vertex -34.20 93.97 2.25
  vertex -34.20 93.97 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.36 98.48 2.00
  vertex -17.36 98.48 2.25
  vertex -34.20 93.97 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -34.20 93.97 2.25
  vertex -34.61 95.10 2.25
  vertex -50.60 87.64 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -34.20 93.97 2.25
  vertex -50.60 87.64 2.25
  vertex -50.00 86.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -34.20 93.97 2.00
  vertex -50.60 87.64 2.00
  vertex -34.61 95.10 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -34.20 93.97 2.00
  vertex -50.00 86.60 2.00
  vertex -50.60 87.64 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -34.61 95.10 2.00
  vertex -50.60 87.64 2.00
  vertex -50.60 87.64 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -34.61 95.10 2.00
  vertex -50.60 87.64 2.25
  vertex -34.61 95.10 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -34.20 93.97 2.00
  vertex -50.00 86.60 2.25
  vertex -50.00 86.60 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -34.20 93.97 2.00
  vertex -34.20 93.97 2.25
  vertex -50.00 86.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -50.00 86.60 2.25
  vertex -50.60 87.64 2.25
  vertex -65.05 77.52 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -50.00 86.60 2.25
  vertex -65.05 77.52 2.25
  vertex -64.28 76.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -50.00 86.60 2.00
  vertex -65.05 77.52 2.00
  vertex -50.60 87.64 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -50.00 86.60 2.00
  vertex -64.28 76.60 2.00
  vertex -65.05 77.52 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -50.60 87.64 2.00
  vertex -65.05 77.52 2.00
  vertex -65.05 77.52 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -50.60 87.64 2.00
  vertex -65.05 77.52 2.25
  vertex -50.60 87.64 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -50.00 86.60 2.00
  vertex -64.28 76.60 2.25
  vertex -64.28 76.60 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -50.00 86.60 2.00
  vertex -50.00 86.60 2.25
  vertex -64.28 76.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -64.28 76.60 2.25
  vertex -65.05 77.52 2.25
  vertex -77.52 65.05 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -64.28 76.60 2.25
  vertex -77.52 65.05 2.25
  vertex -76.60 64.28 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -64.28 76.60 2.00
  vertex -77.52 65.05 2.00
  vertex -65.05 77.52 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -64.28 76.60 2.00
  vertex -76.60 64.28 2.00
  vertex -77.52 65.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -65.05 77.52 2.00
  vertex -77.52 65.05 2.00
  vertex -77.52 65.05 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -65.05 77.52 2.00
  vertex -77.52 65.05 2.25
  vertex -65.05 77.52 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -64.28 76.60 2.00
  vertex -76.60 64.28 2.25
  vertex -76.60 64.28 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -64.28 76.60 2.00
  vertex -64.28 76.60 2.25
  vertex -76.60 64.28 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -76.60 64.28 2.25
  vertex -77.52 65.05 2.25
  vertex -87.64 50.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -76.60 64.28 2.25
  vertex -87.64 50.60 2.25
  vertex -86.60 50.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -76.60 64.28 2.00
  vertex -87.64 50.60 2.00
  vertex -77.52 65.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -76.60 64.28 2.00
  vertex -86.60 50.00 2.00
  vertex -87.64 50.60 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -77.52 65.05 2.00
  vertex -87.64 50.60 2.00
  vertex -87.64 50.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -77.52 65.05 2.00
  vertex -87.64 50.60 2.25
  vertex -77.52 65.05 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -76.60 64.28 2.00
  vertex -86.60 50.00 2.25
  vertex -86.60 50.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -76.60 64.28 2.00
  vertex -76.60 64.28 2.25
  vertex -86.60 50.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -86.60 50.00 2.25
  vertex -87.64 50.60 2.25
  vertex -95.10 34.61 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -86.60 50.00 2.25
  vertex -95.10 34.61 2.25
  vertex -93.97 34.20 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -86.60 50.00 2.00
  vertex -95.10 34.61 2.00
  vertex -87.64 50.60 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -86.60 50.00 2.00
  vertex -93.97 34.20 2.00
  vertex -95.10 34.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -87.64 50.60 2.00
  vertex -95.10 34.61 2.00
  vertex -95.10 34.61 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -87.64 50.60 2.00
  vertex -95.10 34.61 2.25
  vertex -87.64 50.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -86.60 50.00 2.00
  vertex -93.97 34.20 2.25
  vertex -93.97 34.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -86.60 50.00 2.00
  vertex -86.60 50.00 2.25
  vertex -93.97 34.20 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -93.97 34.20 2.25
  vertex -95.10 34.61 2.25
  vertex -99.66 17.57 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -93.97 34.20 2.25
  vertex -99.66 17.57 2.25
  vertex -98.48 17.36 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -93.97 34.20 2.00
  vertex -99.66 17.57 2.00
  vertex -95.10 34.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -93.97 34.20 2.00
  vertex -98.48 17.36 2.00
  vertex -99.66 17.57 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -95.10 34.61 2.00
  vertex -99.66 17.57 2.00
  vertex -99.66 17.57 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -95.10 34.61 2.00
  vertex -99.66 17.57 2.25
  vertex -95.10 34.61 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -93.97 34.20 2.00
  vertex -98.48 17.36 2.25
  vertex -98.48 17.36 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -93.97 34.20 2.00
  vertex -93.97 34.20 2.25
  vertex -98.48 17.36 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -98.48 17.36 2.25
  vertex -99.66 17.57 2.25
  vertex -101.20 0.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -98.48 17.36 2.25
  vertex -101.20 0.00 2.25
  vertex -100.00 0.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -98.48 17.36 2.00
  vertex -101.20 0.00 2.00
  vertex -99.66 17.57 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -98.48 17.36 2.00
  vertex -100.00 0.00 2.00
  vertex -101.20 0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -99.66 17.57 2.00
  vertex -101.20 0.00 2.00
  vertex -101.20 0.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -99.66 17.57 2.00
  vertex -101.20 0.00 2.25
  vertex -99.66 17.57 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -98.48 17.36 2.00
  vertex -100.00 0.00 2.25
  vertex -100.00 0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -98.48 17.36 2.00
  vertex -98.48 17.36 2.25
  vertex -100.00 0.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -100.00 0.00 2.25
  vertex -101.20 0.00 2.25
  vertex -99.66 -17.57 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -100.00 0.00 2.25
  vertex -99.66 -17.57 2.25
  vertex -98.48 -17.36 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -100.00 0.00 2.00
  vertex -99.66 -17.57 2.00
  vertex -101.20 0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -100.00 0.00 2.00
  vertex -98.48 -17.36 2.00
  vertex -99.66 -17.57 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -101.20 0.00 2.00
  vertex -99.66 -17.57 2.00
  vertex -99.66 -17.57 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -101.20 0.00 2.00
  vertex -99.66 -17.57 2.25
  vertex -101.20 0.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -100.00 0.00 2.00
  vertex -98.48 -17.36 2.25
  vertex -98.48 -17.36 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -100.00 0.00 2.00
  vertex -100.00 0.00 2.25
  vertex -98.48 -17.36 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -98.48 -17.36 2.25
  vertex -99.66 -17.57 2.25
  vertex -95.10 -34.61 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -98.48 -17.36 2.25
  vertex -95.10 -34.61 2.25
  vertex -93.97 -34.20 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -98.48 -17.36 2.00
  vertex -95.10 -34.61 2.00
  vertex -99.66 -17.57 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -98.48 -17.36 2.00
  vertex -93.97 -34.20 2.00
  vertex -95.10 -34.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -99.66 -17.57 2.00
  vertex -95.10 -34.61 2.00
  vertex -95.10 -34.61 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -99.66 -17.57 2.00
  vertex -95.10 -34.61 2.25
  vertex -99.66 -17.57 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -98.48 -17.36 2.00
  vertex -93.97 -34.20 2.25
  vertex -93.97 -34.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -98.48 -17.36 2.00
  vertex -98.48 -17.36 2.25
  vertex -93.97 -34.20 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -93.97 -34.20 2.25
  vertex -95.10 -34.61 2.25
  vertex -87.64 -50.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -93.97 -34.20 2.25
  vertex -87.64 -50.60 2.25
  vertex -86.60 -50.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -93.97 -34.20 2.00
  vertex -87.64 -50.60 2.00
  vertex -95.10 -34.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -93.97 -34.20 2.00
  vertex -86.60 -50.00 2.00
  vertex -87.64 -50.60 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -95.10 -34.61 2.00
  vertex -87.64 -50.60 2.00
  vertex -87.64 -50.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -95.10 -34.61 2.00
  vertex -87.64 -50.60 2.25
  vertex -95.10 -34.61 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -93.97 -34.20 2.00
  vertex -86.60 -50.00 2.25
  vertex -86.60 -50.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -93.97 -34.20 2.00
  vertex -93.97 -34.20 2.25
  vertex -86.60 -50.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -86.60 -50.00 2.25
  vertex -87.64 -50.60 2.25
  vertex -77.52 -65.05 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -86.60 -50.00 2.25
  vertex -77.52 -65.05 2.25
  vertex -76.60 -64.28 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -86.60 -50.00 2.00
  vertex -77.52 -65.05 2.00
  vertex -87.64 -50.60 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -86.60 -50.00 2.00
  vertex -76.60 -64.28 2.00
  vertex -77.52 -65.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -87.64 -50.60 2.00
  vertex -77.52 -65.05 2.00
  vertex -77.52 -65.05 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -87.64 -50.60 2.00
  vertex -77.52 -65.05 2.25
  vertex -87.64 -50.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -86.60 -50.00 2.00
  vertex -76.60 -64.28 2.25
  vertex -76.60 -64.28 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -86.60 -50.00 2.00
  vertex -86.60 -50.00 2.25
  vertex -76.60 -64.28 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -76.60 -64.28 2.25
  vertex -77.52 -65.05 2.25
  vertex -65.05 -77.52 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -76.60 -64.28 2.25
  vertex -65.05 -77.52 2.25
  vertex -64.28 -76.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -76.60 -64.28 2.00
  vertex -65.05 -77.52 2.00
  vertex -77.52 -65.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -76.60 -64.28 2.00
  vertex -64.28 -76.60 2.00
  vertex -65.05 -77.52 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -77.52 -65.05 2.00
  vertex -65.05 -77.52 2.00
  vertex -65.05 -77.52 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -77.52 -65.05 2.00
  vertex -65.05 -77.52 2.25
  vertex -77.52 -65.05 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -76.60 -64.28 2.00
  vertex -64.28 -76.60 2.25
  vertex -64.28 -76.60 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -76.60 -64.28 2.00
  vertex -76.60 -64.28 2.25
  vertex -64.28 -76.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -64.28 -76.60 2.25
  vertex -65.05 -77.52 2.25
  vertex -50.60 -87.64 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -64.28 -76.60 2.25
  vertex -50.60 -87.64 2.25
  vertex -50.00 -86.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -64.28 -76.60 2.00
  vertex -50.60 -87.64 2.00
  vertex -65.05 -77.52 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -64.28 -76.60 2.00
  vertex -50.00 -86.60 2.00
  vertex -50.60 -87.64 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -65.05 -77.52 2.00
  vertex -50.60 -87.64 2.00
  vertex -50.60 -87.64 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -65.05 -77.52 2.00
  vertex -50.60 -87.64 2.25
  vertex -65.05 -77.52 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -64.28 -76.60 2.00
  vertex -50.00 -86.60 2.25
  vertex -50.00 -86.60 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -64.28 -76.60 2.00
  vertex -64.28 -76.60 2.25
  vertex -50.00 -86.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -50.00 -86.60 2.25
  vertex -50.60 -87.64 2.25
  vertex -34.61 -95.10 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -50.00 -86.60 2.25
  vertex -34.61 -95.10 2.25
  vertex -34.20 -93.97 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -50.00 -86.60 2.00
  vertex -34.61 -95.10 2.00
  vertex -50.60 -87.64 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -50.00 -86.60 2.00
  vertex -34.20 -93.97 2.00
  vertex -34.61 -95.10 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -50.60 -87.64 2.00
  vertex -34.61 -95.10 2.00
  vertex -34.61 -95.10 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -50.60 -87.64 2.00
  vertex -34.61 -95.10 2.25
  vertex -50.60 -87.64 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -50.00 -86.60 2.00
  vertex -34.20 -93.97 2.25
  vertex -34.20 -93.97 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -50.00 -86.60 2.00
  vertex -50.00 -86.60 2.25
  vertex -34.20 -93.97 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -34.20 -93.97 2.25
  vertex -34.61 -95.10 2.25
  vertex -17.57 -99.66 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -34.20 -93.97 2.25
  vertex -17.57 -99.66 2.25
  vertex -17.36 -98.48 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -34.20 -93.97 2.00
  vertex -17.57 -99.66 2.00
  vertex -34.61 -95.10 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -34.20 -93.97 2.00
  vertex -17.36 -98.48 2.00
  vertex -17.57 -99.66 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -34.61 -95.10 2.00
  vertex -17.57 -99.66 2.00
  vertex -17.57 -99.66 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -34.61 -95.10 2.00
  vertex -17.57 -99.66 2.25
  vertex -34.61 -95.10 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -34.20 -93.97 2.00
  vertex -17.36 -98.48 2.25
  vertex -17.36 -98.48 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -34.20 -93.97 2.00
  vertex -34.20 -93.97 2.25
  vertex -17.36 -98.48 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.36 -98.48 2.25
  vertex -17.57 -99.66 2.25
  vertex -0.00 -101.20 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.36 -98.48 2.25
  vertex -0.00 -101.20 2.25
  vertex -0.00 -100.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.36 -98.48 2.00
  vertex -0.00 -101.20 2.00
  vertex -17.57 -99.66 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.36 -98.48 2.00
  vertex -0.00 -100.00 2.00
  vertex -0.00 -101.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.57 -99.66 2.00
  vertex -0.00 -101.20 2.00
  vertex -0.00 -101.20 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.57 -99.66 2.00
  vertex -0.00 -101.20 2.25
  vertex -17.57 -99.66 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.36 -98.48 2.00
  vertex -0.00 -100.00 2.25
  vertex -0.00 -100.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -17.36 -98.48 2.00
  vertex -17.36 -98.48 2.25
  vertex -0.00 -100.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -100.00 2.25
  vertex -0.00 -101.20 2.25
  vertex 17.57 -99.66 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -100.00 2.25
  vertex 17.57 -99.66 2.25
  vertex 17.36 -98.48 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -100.00 2.00
  vertex 17.57 -99.66 2.00
  vertex -0.00 -101.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -100.00 2.00
  vertex 17.36 -98.48 2.00
  vertex 17.57 -99.66 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -101.20 2.00
  vertex 17.57 -99.66 2.00
  vertex 17.57 -99.66 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -101.20 2.00
  vertex 17.57 -99.66 2.25
  vertex -0.00 -101.20 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -100.00 2.00
  vertex 17.36 -98.48 2.25
  vertex 17.36 -98.48 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex -0.00 -100.00 2.00
  vertex -0.00 -100.00 2.25
  vertex 17.36 -98.48 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.36 -98.48 2.25
  vertex 17.57 -99.66 2.25
  vertex 34.61 -95.10 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.36 -98.48 2.25
  vertex 34.61 -95.10 2.25
  vertex 34.20 -93.97 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.36 -98.48 2.00
  vertex 34.61 -95.10 2.00
  vertex 17.57 -99.66 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.36 -98.48 2.00
  vertex 34.20 -93.97 2.00
  vertex 34.61 -95.10 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.57 -99.66 2.00
  vertex 34.61 -95.10 2.00
  vertex 34.61 -95.10 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.57 -99.66 2.00
  vertex 34.61 -95.10 2.25
  vertex 17.57 -99.66 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.36 -98.48 2.00
  vertex 34.20 -93.97 2.25
  vertex 34.20 -93.97 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 17.36 -98.48 2.00
  vertex 17.36 -98.48 2.25
  vertex 34.20 -93.97 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 34.20 -93.97 2.25
  vertex 34.61 -95.10 2.25
  vertex 50.60 -87.64 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 34.20 -93.97 2.25
  vertex 50.60 -87.64 2.25
  vertex 50.00 -86.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 34.20 -93.97 2.00
  vertex 50.60 -87.64 2.00
  vertex 34.61 -95.10 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 34.20 -93.97 2.00
  vertex 50.00 -86.60 2.00
  vertex 50.60 -87.64 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 34.61 -95.10 2.00
  vertex 50.60 -87.64 2.00
  vertex 50.60 -87.64 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 34.61 -95.10 2.00
  vertex 50.60 -87.64 2.25
  vertex 34.61 -95.10 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 34.20 -93.97 2.00
  vertex 50.00 -86.60 2.25
  vertex 50.00 -86.60 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 34.20 -93.97 2.00
  vertex 34.20 -93.97 2.25
  vertex 50.00 -86.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 50.00 -86.60 2.25
  vertex 50.60 -87.64 2.25
  vertex 65.05 -77.52 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 50.00 -86.60 2.25
  vertex 65.05 -77.52 2.25
  vertex 64.28 -76.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 50.00 -86.60 2.00
  vertex 65.05 -77.52 2.00
  vertex 50.60 -87.64 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 50.00 -86.60 2.00
  vertex 64.28 -76.60 2.00
  vertex 65.05 -77.52 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 50.60 -87.64 2.00
  vertex 65.05 -77.52 2.00
  vertex 65.05 -77.52 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 50.60 -87.64 2.00
  vertex 65.05 -77.52 2.25
  vertex 50.60 -87.64 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 50.00 -86.60 2.00
  vertex 64.28 -76.60 2.25
  vertex 64.28 -76.60 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 50.00 -86.60 2.00
  vertex 50.00 -86.60 2.25
  vertex 64.28 -76.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 64.28 -76.60 2.25
  vertex 65.05 -77.52 2.25
  vertex 77.52 -65.05 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 64.28 -76.60 2.25
  vertex 77.52 -65.05 2.25
  vertex 76.60 -64.28 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 64.28 -76.60 2.00
  vertex 77.52 -65.05 2.00
  vertex 65.05 -77.52 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 64.28 -76.60 2.00
  vertex 76.60 -64.28 2.00
  vertex 77.52 -65.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 65.05 -77.52 2.00
  vertex 77.52 -65.05 2.00
  vertex 77.52 -65.05 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 65.05 -77.52 2.00
  vertex 77.52 -65.05 2.25
  vertex 65.05 -77.52 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 64.28 -76.60 2.00
  vertex 76.60 -64.28 2.25
  vertex 76.60 -64.28 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 64.28 -76.60 2.00
  vertex 64.28 -76.60 2.25
  vertex 76.60 -64.28 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 76.60 -64.28 2.25
  vertex 77.52 -65.05 2.25
  vertex 87.64 -50.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 76.60 -64.28 2.25
  vertex 87.64 -50.60 2.25
  vertex 86.60 -50.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 76.60 -64.28 2.00
  vertex 87.64 -50.60 2.00
  vertex 77.52 -65.05 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 76.60 -64.28 2.00
  vertex 86.60 -50.00 2.00
  vertex 87.64 -50.60 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 77.52 -65.05 2.00
  vertex 87.64 -50.60 2.00
  vertex 87.64 -50.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 77.52 -65.05 2.00
  vertex 87.64 -50.60 2.25
  vertex 77.52 -65.05 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 76.60 -64.28 2.00
  vertex 86.60 -50.00 2.25
  vertex 86.60 -50.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 76.60 -64.28 2.00
  vertex 76.60 -64.28 2.25
  vertex 86.60 -50.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 86.60 -50.00 2.25
  vertex 87.64 -50.60 2.25
  vertex 95.10 -34.61 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 86.60 -50.00 2.25
  vertex 95.10 -34.61 2.25
  vertex 93.97 -34.20 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 86.60 -50.00 2.00
  vertex 95.10 -34.61 2.00
  vertex 87.64 -50.60 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 86.60 -50.00 2.00
  vertex 93.97 -34.20 2.00
  vertex 95.10 -34.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 87.64 -50.60 2.00
  vertex 95.10 -34.61 2.00
  vertex 95.10 -34.61 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 87.64 -50.60 2.00
  vertex 95.10 -34.61 2.25
  vertex 87.64 -50.60 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 86.60 -50.00 2.00
  vertex 93.97 -34.20 2.25
  vertex 93.97 -34.20 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 86.60 -50.00 2.00
  vertex 86.60 -50.00 2.25
  vertex 93.97 -34.20 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 93.97 -34.20 2.25
  vertex 95.10 -34.61 2.25
  vertex 99.66 -17.57 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 93.97 -34.20 2.25
  vertex 99.66 -17.57 2.25
  vertex 98.48 -17.36 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 93.97 -34.20 2.00
  vertex 99.66 -17.57 2.00
  vertex 95.10 -34.61 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 93.97 -34.20 2.00
  vertex 98.48 -17.36 2.00
  vertex 99.66 -17.57 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 95.10 -34.61 2.00
  vertex 99.66 -17.57 2.00
  vertex 99.66 -17.57 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 95.10 -34.61 2.00
  vertex 99.66 -17.57 2.25
  vertex 95.10 -34.61 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 93.97 -34.20 2.00
  vertex 98.48 -17.36 2.25
  vertex 98.48 -17.36 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 93.97 -34.20 2.00
  vertex 93.97 -34.20 2.25
  vertex 98.48 -17.36 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 98.48 -17.36 2.25
  vertex 99.66 -17.57 2.25
  vertex 101.20 -0.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 98.48 -17.36 2.25
  vertex 101.20 -0.00 2.25
  vertex 100.00 -0.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 98.48 -17.36 2.00
  vertex 101.20 -0.00 2.00
  vertex 99.66 -17.57 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 98.48 -17.36 2.00
  vertex 100.00 -0.00 2.00
  vertex 101.20 -0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 99.66 -17.57 2.00
  vertex 101.20 -0.00 2.00
  vertex 101.20 -0.00 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 99.66 -17.57 2.00
  vertex 101.20 -0.00 2.25
  vertex 99.66 -17.57 2.25
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 98.48 -17.36 2.00
  vertex 100.00 -0.00 2.25
  vertex 100.00 -0.00 2.00
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 98.48 -17.36 2.00
  vertex 98.48 -17.36 2.25
  vertex 100.00 -0.00 2.25
 endloop
endfacet
endsolid record
```
