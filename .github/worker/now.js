// The record player, drawn fresh on every visit.
//
// GitHub shows README images through its image proxy, which asks again on each page view when the answer says not
// to keep it. So this Worker looks up what's playing (Spotify, then Last.fm, like .github/profile/data.py) and fills
// it into the deck's templates, which the "Now playing" workflow publishes to GitHub Pages as kit.json. The layout
// numbers come from that kit too, and the drawing below mirrors info_markup() in .github/profile/layout.py, so both
// look the same. If anything goes wrong, it hands over the copy on Pages, which is at most a few minutes old.

const KIT_SECONDS = 300; // how long a fetched kit is kept
const NOW_SECONDS = 15; // how long a lookup is reused, so the images of one page view share it
const BLANK_COVER = "2a96cbd8b46e442fc41c2b86b821562f"; // Last.fm's grey star placeholder
const MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
const FRESH = {
  "cache-control": "no-cache, no-store, must-revalidate, max-age=0",
  expires: "0",
  pragma: "no-cache",
};

let kept = { kit: null, at: 0 };
let lastLookup = { now: undefined, at: 0 };
const tokens = new Map(); // Spotify account → { token, until }
const spotifyUsers = new Map();

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const image = url.pathname.match(/^\/img\/(dark|light|m)\/([\w-]+)\.svg$/);
    try {
      const kit = await loadKit(env);
      if (image && image[2] === kit.file) {
        const svg = await deck(kit, image[1], await nowPlaying(env, kit));
        return new Response(svg, { headers: { "content-type": "image/svg+xml; charset=utf-8", ...FRESH } });
      }
      const go = url.pathname.match(/^\/go\/(play|song|artist|context|user)\/?$/);
      if (go) {
        return new Response(null, { status: 302, headers: { location: links(kit, await nowPlaying(env, kit))[go[1]], ...FRESH } });
      }
      if (url.pathname === "/now.json") {
        const now = await nowPlaying(env, kit);
        return Response.json({ now, links: links(kit, now) }, { headers: FRESH });
      }
      return new Response(null, { status: 302, headers: { location: kit.profile } });
    } catch (error) {
      console.error(error);
      if (image && env.PAGES_URL) {
        try {
          const copy = await fetch(`${env.PAGES_URL.replace(/\/?$/, "/")}img/${image[1]}/${image[2]}.svg`);
          return new Response(copy.body, { status: copy.status, headers: { "content-type": "image/svg+xml; charset=utf-8", ...FRESH } });
        } catch (fallback) {
          console.error(fallback);
        }
      }
      return new Response("The record player is resting.", { status: 503, headers: FRESH });
    }
  },
};

async function loadKit(env) {
  if (kept.kit && Date.now() - kept.at < KIT_SECONDS * 1000) return kept.kit;
  const response = await fetch(env.KIT_URL, { cf: { cacheTtl: KIT_SECONDS } });
  if (!response.ok) {
    if (kept.kit) return kept.kit;
    throw new Error(`kit: ${response.status}`);
  }
  kept = { kit: await response.json(), at: Date.now() };
  return kept.kit;
}

// ── what's playing ──────────────────────────────────────────────────────────

async function nowPlaying(env, kit) {
  if (lastLookup.now !== undefined && Date.now() - lastLookup.at < NOW_SECONDS * 1000) return lastLookup.now;
  const now = await lookUp(env, kit);
  lastLookup = { now, at: Date.now() };
  return now;
}

// Spotify accounts, then Last.fm accounts: the first one playing wins, else the most recent play anywhere.
async function lookUp(env, kit) {
  const quietly = (promise) => promise.catch((error) => (console.error(error), null));
  const [spotify, scrobbled] = await Promise.all([
    Promise.all(spotifyAccounts(env).map((account) => quietly(spotifyNow(account)))),
    Promise.all(env.LASTFM_API_KEY ? kit.lastfm.map((entry, i) => quietly(lastfmNow(env.LASTFM_API_KEY, kit, entry, 10 + i))) : []),
  ]);
  const heard = spotify.filter(Boolean);
  const playing = heard.find((c) => c.playing);
  if (playing) return playing;
  // Spotify scrobbles to Last.fm too; that's the same play.
  const others = scrobbled.filter((r) => r && !heard.some((c) => c.title === r.title && c.artist === r.artist));
  const live = others.find((r) => r.playing);
  if (live) return live;
  const candidates = [...heard, ...others];
  if (!candidates.length) return kit.now || null;
  return candidates.reduce((best, c) => {
    const a = c.when || "", b = best.when || "";
    return a > b || (a === b && (c.account ?? 9) < (best.account ?? 9)) ? c : best;
  });
}

async function getJSON(url, headers = {}, options = {}) {
  const response = await fetch(url, { headers: { "user-agent": "robyrew-profile", ...headers }, ...options });
  if (!response.ok) throw new Error(`${new URL(url).host}: ${response.status}`);
  const body = await response.text();
  return body ? JSON.parse(body) : null;
}

function minutes(date) {
  return date.toISOString().slice(0, 16) + "+00:00";
}

function quotePlus(part) {
  return encodeURIComponent(part).replace(/%20/g, "+").replace(/[!'()*]/g, (c) => "%" + c.charCodeAt(0).toString(16).toUpperCase());
}

function lastfmMusicUrl(...parts) {
  return "https://www.last.fm/music/" + parts.map(quotePlus).join("/");
}

function playUrl(kit, platform, title, artist) {
  const template = kit.play_search[platform] || kit.play_search["Last.fm"];
  return template.replace("{q}", encodeURIComponent(`${title} ${artist}`.trim()));
}

function lastfmImage(images, size = "large") {
  const bySize = Object.fromEntries((images || []).map((i) => [i.size, i["#text"]]));
  const url = bySize[size] || bySize.large || bySize.medium || bySize.extralarge || "";
  return url.includes(BLANK_COVER) ? "" : url;
}

// Last.fm sends a cover as JPEG when its name ends in .jpg: about a fifth of the PNG's weight.
function asJpeg(url) {
  return url.endsWith(".png") && url.includes(".fastly.net/") ? url.slice(0, -4) + ".jpg" : url;
}

async function lastfmNow(key, kit, entry, account) {
  const query = new URLSearchParams({ method: "user.getrecenttracks", user: entry.user, limit: "1", extended: "1", api_key: key, format: "json" });
  const data = await getJSON(`https://ws.audioscrobbler.com/2.0/?${query}`);
  let tracks = data?.recenttracks?.track;
  if (!tracks) return null;
  if (!Array.isArray(tracks)) tracks = [tracks];
  const track = tracks[0];
  if (!track) return null;
  const playing = track["@attr"]?.nowplaying === "true";
  const when = !playing && track.date?.uts ? minutes(new Date(Number(track.date.uts) * 1000)) : "";
  const artist = track.artist || {};
  const artistName = artist.name || artist["#text"] || "";
  const album = track.album?.["#text"] || "";
  const title = track.name || "";
  const platform = entry.platform || "Last.fm";
  return {
    playing, paused: false, title, artist: artistName,
    cover: asJpeg(lastfmImage(track.image)),
    context: album, context_kind: album ? "Album" : "", device: "", device_type: "",
    user: entry.user, platform, when, account,
    song_url: track.url || lastfmMusicUrl(artistName, "_", title),
    artist_url: artist.url || lastfmMusicUrl(artistName),
    context_url: album ? lastfmMusicUrl(artistName, album) : "",
    user_url: `https://www.last.fm/user/${encodeURIComponent(entry.user)}`,
    play_url: playUrl(kit, platform, title, artistName),
  };
}

function spotifyAccounts(env) {
  const accounts = [];
  for (let n = 1; n <= 5; n++) {
    const refresh = env[`SPOTIFY_REFRESH_TOKEN_${n}`] || (n === 1 ? env.SPOTIFY_REFRESH_TOKEN : "");
    const id = env[`SPOTIFY_CLIENT_ID_${n}`] || env.SPOTIFY_CLIENT_ID;
    const secret = env[`SPOTIFY_CLIENT_SECRET_${n}`] || env.SPOTIFY_CLIENT_SECRET;
    if (refresh && id && secret) accounts.push({ n, id, secret, refresh });
  }
  return accounts;
}

async function spotifyToken(account) {
  const known = tokens.get(account.n);
  if (known && known.until > Date.now()) return known.token;
  const data = await getJSON("https://accounts.spotify.com/api/token", {
    authorization: `Basic ${btoa(`${account.id}:${account.secret}`)}`,
    "content-type": "application/x-www-form-urlencoded",
  }, { method: "POST", body: new URLSearchParams({ grant_type: "refresh_token", refresh_token: account.refresh }).toString() });
  tokens.set(account.n, { token: data.access_token, until: Date.now() + ((data.expires_in || 3600) - 60) * 1000 });
  return data.access_token;
}

function smallestImage(images, minimum = 64) {
  const usable = (images || []).filter((i) => i.url);
  if (!usable.length) return "";
  const fitting = usable.filter((i) => (i.width || 0) >= minimum);
  return (fitting.length ? fitting : usable).reduce((a, b) => ((b.width || 0) < (a.width || 0) ? b : a)).url;
}

async function spotifyContext(context, item, bearer) {
  if (!context) {
    const album = item.album;
    return album ? ["Album", album.name || "", album.external_urls?.spotify || ""] : ["", "", ""];
  }
  const url = context.external_urls?.spotify || "";
  switch (context.type) {
    case "playlist":
      try {
        const playlist = await getJSON(`https://api.spotify.com/v1/playlists/${context.uri.split(":").pop()}?fields=name`, bearer);
        return ["Playlist", playlist.name, url];
      } catch {
        return ["Playlist", "A playlist", url];
      }
    case "album":
      return ["Album", item.album?.name || "", url];
    case "artist":
      return ["Radio", item.artists?.length ? `${item.artists[0].name} radio` : "Artist radio", url];
    case "collection":
      return ["Library", "Liked Songs", "https://open.spotify.com/collection/tracks"];
    default:
      return ["", "", url];
  }
}

async function spotifyItem(item, context, bearer, user, playing, paused, device, when) {
  const [kind, name, url] = await spotifyContext(context, item, bearer);
  const artists = item.artists || [];
  const song = item.external_urls?.spotify || "";
  return {
    playing, paused, title: item.name || "",
    artist: artists.map((a) => a.name).join(", ") || item.show?.name || "",
    cover: smallestImage(item.album?.images || item.images, 160), // big enough for the record
    context: name, context_kind: kind, device: device.name || "", device_type: device.type || "",
    user: user.name || "", platform: "Spotify", when,
    song_url: song, artist_url: artists[0]?.external_urls?.spotify || "", context_url: url,
    user_url: user.url || "", play_url: song,
  };
}

async function spotifyNow(account) {
  const bearer = { authorization: `Bearer ${await spotifyToken(account)}` };
  let user = spotifyUsers.get(account.n);
  if (!user) {
    const me = (await getJSON("https://api.spotify.com/v1/me", bearer)) || {};
    user = { name: me.display_name || me.id || "", url: me.external_urls?.spotify || "" };
    spotifyUsers.set(account.n, user);
  }
  let result = null;
  const player = await getJSON("https://api.spotify.com/v1/me/player?additional_types=track,episode", bearer);
  if (player?.item) {
    const playing = Boolean(player.is_playing);
    result = await spotifyItem(player.item, player.context, bearer, user, playing, !playing, player.device || {}, minutes(new Date()));
  } else {
    const recent = await getJSON("https://api.spotify.com/v1/me/player/recently-played?limit=1", bearer);
    const play = recent?.items?.[0];
    if (play) result = await spotifyItem(play.track, play.context, bearer, user, false, false, {}, play.played_at || "");
  }
  if (result) result.account = account.n;
  return result;
}

// Where each part of the record player links to, as now_links() in build.py.
function links(kit, now) {
  now = now || {};
  const { title = "", artist = "" } = now;
  const keys = ["play", "song", "artist", "context", "user"];
  if (!title) return Object.fromEntries(keys.map((k) => [k, kit.fallback]));
  const platform = now.platform || "Last.fm";
  const song = now.song_url || lastfmMusicUrl(artist, "_", title);
  const artistUrl = now.artist_url || (artist ? lastfmMusicUrl(artist) : song);
  let context = now.context_url;
  if (!context && now.context && (now.context_kind || "Album") === "Album" && artist) context = lastfmMusicUrl(artist, now.context);
  let user = now.user_url;
  if (!user && now.user) user = `https://www.last.fm/user/${encodeURIComponent(now.user)}`;
  return {
    play: now.play_url || playUrl(kit, platform, title, artist),
    song,
    artist: artistUrl,
    context: context || artistUrl,
    user: user || kit.fallback,
  };
}

// ── drawing ─────────────────────────────────────────────────────────────────

async function deck(kit, version, now) {
  const playing = Boolean(now?.playing);
  const cover = now?.cover ? await dataUri(now.cover) : null;
  const look = kit.templates[`${playing ? "playing" : "idle"}-${cover ? "cover" : "label"}`][version];
  // Replacements are functions, so a "$" in a song title is just a "$".
  let svg = look.svg.replace(/\{\{font:(\w+)\}\}/g, (_, key) => kit.fonts[key]);
  if (cover) svg = svg.replace("{{cover}}", () => cover);
  for (const slot of look.slots) svg = svg.replace(`<!--now:${slot.ids}-->`, () => infoMarkup(kit, slot, now));
  return svg;
}

async function dataUri(url) {
  try {
    const response = await fetch(url, { headers: { "user-agent": "robyrew-profile" }, cf: { cacheTtl: 86400 } });
    if (!response.ok) return null;
    const bytes = new Uint8Array(await response.arrayBuffer());
    if (!bytes.length || bytes.length > 400_000) return null;
    let binary = "";
    for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
    const kind = (response.headers.get("content-type") || "image/jpeg").split(";")[0];
    return `data:${kind};base64,${btoa(binary)}`;
  } catch {
    return null;
  }
}

function num(v) {
  let s = v.toFixed(2);
  if (s.includes(".")) s = s.replace(/0+$/, "").replace(/\.$/, "");
  return s;
}

function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#x27;");
}

function paint(color, attr = "fill") {
  return Array.isArray(color) ? `${attr}="${color[0]}" ${attr}-opacity="${num(color[1])}"` : `${attr}="${color}"`;
}

function iconMarkup(kit, name, x, y, size, strokePaint, stroke) {
  return (
    `<g transform="translate(${num(x)} ${num(y)}) scale(${num(size / 24)})" fill="none" ${strokePaint} ` +
    `stroke-width="${num((stroke * 24) / size)}" stroke-linecap="round" stroke-linejoin="round">${kit.icons[name]}</g>`
  );
}

// Text measuring, as canvas.Face without kerning: the templates' fonts carry none.
function face(kit, key) {
  const { upm, advance } = kit.faces[key];
  const width = (text, size, tracking = 0) => {
    const chars = Array.from(text);
    return (chars.reduce((sum, c) => sum + (advance[c] ?? upm * 0.55), 0) * size) / upm + tracking * chars.length;
  };
  const fit = (text, size, max, tracking = 0) => {
    max = Math.max(max, 1);
    if (width(text, size, tracking) <= max) return text;
    let chars = Array.from(text);
    while (chars.length && width(chars.join("") + "…", size, tracking) > max) chars.pop();
    return chars.join("").replace(/[ ,.;:—\-·]+$/, "") + "…";
  };
  const wrap = (text, size, max, maxLines = 99) => {
    const lines = [];
    let line = "";
    const words = text.split(/\s+/).filter(Boolean);
    for (let i = 0; i < words.length; i++) {
      const trial = `${line} ${words[i]}`.trim();
      if (line && width(trial, size) > max) {
        lines.push(line);
        line = words[i];
        if (lines.length === maxLines) {
          lines[lines.length - 1] = fit([lines[lines.length - 1], ...words.slice(i)].join(" "), size, max);
          return lines;
        }
      } else {
        line = trial;
      }
    }
    return line ? [...lines, line] : lines;
  };
  return { width, fit, wrap };
}

function whenLabel(stamp) {
  if (!stamp) return "";
  const moment = new Date(stamp);
  return Number.isNaN(moment.getTime()) ? "" : `${MONTHS[moment.getUTCMonth()]} ${moment.getUTCDate()}`;
}

function statusText(now) {
  if (!now) return "OFF AIR";
  if (now.playing) return "NOW PLAYING";
  if (now.paused) return "PAUSED";
  const stamp = whenLabel(now.when);
  return stamp ? `LAST PLAYED · ${stamp}` : "LAST PLAYED";
}

function infoItems(now) {
  if (!now) {
    return { status: "OFF AIR", title: "Nothing on the deck", artist: "Music is usually on, check back soon", album: "", kind: "", platform: "", user: "" };
  }
  return {
    status: statusText(now), title: now.title || "Untitled", artist: now.artist || "", album: now.context || "",
    kind: now.context_kind || "", platform: now.platform || "Last.fm", user: now.user || "",
  };
}

// What's on the deck, as info_markup() in layout.py.
function infoMarkup(kit, k, now) {
  const semi = face(kit, "semi"), mono = face(kit, "mono");
  const text = (x, y, s, font, size, color, tracking = 0) =>
    s ? `<text x="${num(x)}" y="${num(y)}" class="f-${font}" font-size="${num(size)}" ${paint(color)}` +
      `${tracking ? ` letter-spacing="${num(tracking)}"` : ""}>${esc(s)}</text>` : "";
  const item = infoItems(now);
  const playing = Boolean(now?.playing);
  const { x, w, phone, gaps } = k;
  const status = phone ? item.status.split(" · ")[0] : item.status;
  const titles = semi.wrap(item.title, k.title, w, k.lines);
  if (!titles.length) titles.push("");
  let artist = item.artist, album = item.album;
  const where = item.platform + (item.user ? ` · @${item.user}` : "");
  if (phone) {
    artist = [artist, album].filter(Boolean).join(" · ");
    album = "";
  }
  const cap = 0.72;
  let height = k.status * cap + gaps[0] + k.title * cap + (titles.length - 1) * k.lh;
  if (artist) height += gaps[1] + k.artist * cap;
  if (album) height += gaps[2] + k.album * cap;
  const pill = phone ? 0 : 20;
  if (item.platform) height += phone ? gaps[2] + k.album * cap : gaps[3] + pill;
  let y = k.y0 + (k.y1 - k.y0 - height) / 2 + k.status * cap;
  const out = [], style = [];
  if (playing) style.push(".pulse{animation:pulse 1.6s ease-in-out infinite alternate}@keyframes pulse{to{opacity:.3}}");
  out.push(`<circle${playing ? ' class="pulse"' : ""} cx="${num(x + 3)}" cy="${num(y - k.status * 0.36)}" r="3" fill="${playing ? "#30D158" : "#8E8E93"}"/>`);
  const label = mono.fit(status, k.status, w - 30, 1.2);
  out.push(text(x + 11, y, label, "mono", k.status, k.dim, 1.2));
  if (playing) {
    // Bars bouncing to the music, after the status.
    const bx = x + 11 + mono.width(label, k.status, 1.2) + 7;
    style.push(".eq rect{transform-box:fill-box;transform-origin:50% 100%;animation:eq .9s ease-in-out infinite alternate}@keyframes eq{from{transform:scaleY(.3)}}");
    let bars = "";
    for (let i = 0; i < 4; i++) {
      bars += `<rect x="${num(bx + i * 3.6)}" y="${num(y - 8)}" width="2.2" height="8" rx=".8" fill="#30D158" style="animation-delay:${num(-0.27 * i * (i + 1))}s"/>`;
    }
    out.push(`<g class="eq">${bars}</g>`);
  }
  y += gaps[0] + k.title * cap;
  titles.forEach((line, i) => {
    out.push(text(x, y, line, "semi", k.title, k.ink, -0.2));
    if (i < titles.length - 1) y += k.lh;
  });
  if (artist) {
    y += gaps[1] + k.artist * cap;
    out.push(text(x, y, semi.fit(artist, k.artist, w), "semi", k.artist, k.dim));
  }
  if (album) {
    y += gaps[2] + k.album * cap;
    const size = k.album + 1;
    out.push(iconMarkup(kit, item.kind === "Playlist" ? "list" : "disc", x, y - size * 0.82, size, paint(k.faint, "stroke"), 2));
    out.push(text(x + size + 5, y, semi.fit(album, k.album, w - size - 5), "semi", k.album, k.faint));
  }
  if (item.platform) {
    const color = kit.platforms[item.platform] || "#9CA3AF";
    if (phone) {
      y += gaps[2] + k.album * cap;
      out.push(`<circle cx="${num(x + 3)}" cy="${num(y - k.album * 0.34)}" r="2.6" fill="${color}"/>`);
      out.push(text(x + 10, y, semi.fit(where, k.album, w - 10), "semi", k.album, k.faint));
    } else {
      y += gaps[3];
      const size = 9.5;
      const shown = semi.fit(where, size, w - 26);
      const width = semi.width(shown, size) + 26;
      out.push(`<rect x="${num(x)}" y="${num(y)}" width="${num(width)}" height="${pill}" rx="${pill / 2}" ${paint(k.glass)} ${paint(k.edge, "stroke")}/>`);
      out.push(`<circle cx="${num(x + 10)}" cy="${num(y + pill / 2)}" r="3" fill="${color}"/>`);
      out.push(text(x + 18, y + pill / 2 + size * 0.36, shown, "semi", size, k.dim));
    }
  }
  return (style.length ? `<style>${style.join("")}</style>` : "") + out.join("");
}
