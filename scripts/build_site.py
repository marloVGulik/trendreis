#!/usr/bin/env python3
"""Bouwt de TRENDREIS-website (orange console) uit content/*.md.

Gebruik:  python3 scripts/build_site.py
Leest:    content/00-cover.md .. content/07-colofon.md
Schrijft: site/index.html  (+ linkt naar site/theme.css en site/main.js)

De markdown is opzettelijk klein gehouden (koppen, alinea's, quotes, lijsten,
tabellen, vet/koersief, inline code) — precies wat de content bestanden gebruiken.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
SITE = ROOT / "site"
OUT = SITE / "index.html"

ORDER = [
    ("00-cover", "Cover"),
    ("01-wie-ben-ik", "Wie ben ik?"),
    ("02-signalen", "Signalen"),
    ("03-analyseren", "Analyseren"),
    ("04-waardeverschuivingen", "Waardeverschuivingen"),
    ("05-bedrijf", "Het bedrijf"),
    ("06-reis", "De reis"),
    ("07-colofon", "Colofon"),
]


# ---------------------------------------------------------------- inline
def inline(t: str) -> str:
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", t)
    return t


# ---------------------------------------------------------------- blocks
def render_table(rows):
    """rows: list of raw '| a | b |' lines (header, separator, data...)."""
    def cells(line):
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        return [c.strip() for c in line.split("|")]

    parsed = [cells(r) for r in rows]
    # drop separator row (---)
    parsed = [r for r in parsed if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
    if not parsed:
        return ""
    head, *body = parsed
    th = "".join(f"<th>{inline(c)}</th>" for c in head)
    trs = "".join(
        "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body
    )
    return (
        '<div class="tblwrap"><table class="tbl">'
        f"<thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>"
    )


LIST_RE = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")


def render_nodes(nodes):
    if not nodes:
        return ""
    t = "ol" if nodes[0]["ordered"] else "ul"
    out = [f"<{t}>"]
    for node in nodes:
        out.append(f"<li>{inline(node['text'])}")
        if node["children"]:
            out.append(render_nodes(node["children"]))
        out.append("</li>")
    out.append(f"</{t}>")
    return "".join(out)


def render_list_items(items):
    """items: list of dicts {level, ordered, text} → genestde <ul>/<ol>."""
    root = []
    stack = []
    for it in items:
        node = {"text": it["text"], "ordered": it["ordered"], "children": [], "_level": it["level"]}
        lvl = it["level"]
        while stack and stack[-1]["_level"] >= lvl:
            stack.pop()
        (stack[-1]["children"] if stack else root).append(node)
        stack.append(node)
    return render_nodes(root)


def consume_list(lines, i):
    """Verteert een lijstblok (incl. meervoudige-regel items). Retourneert (html, new_i)."""
    items = []
    n = len(lines)
    while i < n:
        ln = lines[i]
        stripped = ln.strip()
        if not stripped:
            break
        lm = LIST_RE.match(ln)
        if lm:
            indent = len(lm.group(1).expandtabs(2))
            level = min(1, indent // 2)
            ordered = not lm.group(2).startswith(("-", "*"))
            items.append({"level": level, "ordered": ordered, "text": lm.group(3)})
            i += 1
        elif ln[:1] in (" ", "\t"):
            # continuation line (ingedeukt) van het vorige item
            if items:
                items[-1]["text"] += " " + stripped
            i += 1
        else:
            break
    return render_list_items(items), i


def md_to_html(md: str) -> str:
    lines = md.splitlines()
    out = []
    i = 0
    n = len(lines)
    para = []

    def flush_para():
        nonlocal para
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para = []

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            flush_para()
            i += 1
            continue

        # horizontal rule
        if re.fullmatch(r"-{3,}|\*{3,}", stripped):
            flush_para()
            out.append("<hr>")
            i += 1
            continue

        # headings
        m = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if m:
            flush_para()
            level = len(m.group(1))
            # cover uses '# TITLE' inside a quote; here plain headings only
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # blockquote (group consecutive '> ' lines)
        if stripped.startswith(">"):
            flush_para()
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                q = lines[i].strip()
                if q.startswith("> "):
                    q = q[2:]
                elif q == ">":
                    q = ""
                quote.append(q)
                i += 1
            # collapse into paragraphs
            body = []
            cur = []
            for q in quote:
                if q == "":
                    if cur:
                        body.append("<p>" + inline(" ".join(cur)) + "</p>")
                        cur = []
                else:
                    cur.append(q)
            if cur:
                body.append("<p>" + inline(" ".join(cur)) + "</p>")
            out.append("<blockquote>" + "".join(body) + "</blockquote>")
            continue

        # table (line starts with '|')
        if stripped.startswith("|"):
            flush_para()
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(render_table(rows))
            continue

        # list (group consecutive list lines + continuation lines)
        if LIST_RE.match(line):
            flush_para()
            html_list, i = consume_list(lines, i)
            out.append(html_list)
            continue

        # default: paragraph text
        para.append(stripped)
        i += 1

    flush_para()
    return "\n".join(out)


# ---------------------------------------------------------------- anaglyph
def anaglyph_svg():
    """Een wireframe 'reis' scene (grid + poorten + ster) zonder tekst.
    Tekst blijft plat in de HTML; alleen deze scène wordt rood-cyan gesplitst."""
    VP = (400, 120)
    W, H = 800, 320
    parts = []

    def layer(name, inner):
        return f'<g class="layer-{name}">{inner}</g>'

    # --- FAR: horizon, floor grid, target star, far gate
    far = []
    far.append(f'<line x1="0" y1="120" x2="800" y2="120" class="ln strong"/>')
    # horizontal floor lines (spacing grows toward viewer)
    for y in (140, 165, 200, 250, 320):
        far.append(f'<line x1="0" y1="{y}" x2="800" y2="{y}" class="ln"/>')
    # converging vertical lines from VP to bottom
    for xb in (0, 100, 200, 300, 400, 500, 600, 700, 800):
        far.append(f'<line x1="400" y1="120" x2="{xb}" y2="320" class="ln dim"/>')
    # target star at the horizon (stip op de horizon)
    far.append(
        '<g class="star">'
        '<circle cx="400" cy="120" r="10" class="ln strong"/>'
        '<path d="M400 108 L412 120 L400 132 L388 120 Z" class="ln strong"/>'
        '<line x1="392" y1="120" x2="408" y2="120" class="ln"/>'
        '<line x1="400" y1="112" x2="400" y2="128" class="ln"/>'
        "</g>"
    )
    # far gate (smallest, nearest the horizon)
    far.append('<rect x="372" y="138" width="56" height="24" rx="2" class="gate"/>')
    far.append('<line x1="400" y1="138" x2="400" y2="162" class="ln"/>')
    far_html = layer("far", "".join(far))

    # --- MID: mid gate
    mid = []
    mid.append('<rect x="350" y="168" width="100" height="44" rx="3" class="gate"/>')
    mid.append('<line x1="400" y1="168" x2="400" y2="212" class="ln"/>')
    mid.append('<circle cx="400" cy="212" r="3" class="node"/>')
    mid_html = layer("mid", "".join(mid))

    # --- NEAR: road edges, center line, near gate
    near = []
    near.append('<line x1="200" y1="320" x2="400" y2="120" class="road"/>')
    near.append('<line x1="600" y1="320" x2="400" y2="120" class="road"/>')
    near.append('<line x1="400" y1="320" x2="400" y2="150" class="center"/>')
    near.append('<rect x="326" y="202" width="148" height="80" rx="4" class="gate"/>')
    near.append('<line x1="400" y1="202" x2="400" y2="282" class="ln"/>')
    near.append('<circle cx="400" cy="282" r="4" class="node"/>')
    near_html = layer("near", "".join(near))

    scene = f'{far_html}{mid_html}{near_html}'
    # two channels: red (base) + cyan (offset per layer for true parallax)
    return f'''
<svg class="anaglyph" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet"
     role="img" aria-label="Een pad van drie poorten naar een ster op de horizon — van signaal tot bedrijf">
  <defs>
    <style>
      .ln {{ stroke: currentColor; stroke-width: 1; fill: none; }}
      .ln.strong {{ stroke-width: 1.6; }}
      .ln.dim {{ opacity: .4; }}
      .road {{ stroke: currentColor; stroke-width: 2; fill: none; }}
      .center {{ stroke: currentColor; stroke-width: 1; stroke-dasharray: 4 6; fill: none; }}
      .gate {{ stroke: currentColor; stroke-width: 1.4; fill: none; opacity: .95; }}
      .node {{ fill: currentColor; stroke: none; }}
      .star {{ stroke: currentColor; fill: none; }}
    </style>
  </defs>
  <g id="chR" class="chR">{scene}</g>
  <g id="chC" class="chC">{scene}</g>
</svg>'''


def strip_first_h1(md: str) -> str:
    """Haalt de eerste '# ...' (H1) — de ch-head toont de titel al."""
    lines = md.splitlines()
    for i, ln in enumerate(lines):
        if not ln.strip():
            continue
        if ln.strip().startswith("# "):
            return "\n".join(lines[i + 1:])
        break
    return md


def strip_first_blockquote(md: str) -> str:
    """Haalt de eerste blockquote (titelblok) uit de cover — die staat al in de hero."""
    lines = md.splitlines()
    out = []
    seen_quote = False
    in_quote = False
    for ln in lines:
        s = ln.strip()
        if s.startswith(">"):
            if seen_quote:
                out.append(ln)  # latere quotes blijven (bijv. de letter)
            else:
                in_quote = True  # eerste quote overslaan
            continue
        if in_quote:
            in_quote = False
            seen_quote = True
            out.append(ln)
            continue
        out.append(ln)
    return "\n".join(out)


# ---------------------------------------------------------------- shell
def build():
    chapters = []
    for idx, (fname, title) in enumerate(ORDER):
        f = CONTENT / f"{fname}.md"
        if not f.exists():
            continue
        md = f.read_text(encoding="utf-8")
        md = strip_first_h1(md)
        if idx == 0:
            # de hero toont de titel al; haal de titel-blockquote uit de cover
            md = strip_first_blockquote(md)
        body = md_to_html(md)
        chap_id = f"{fname}"
        if idx == 0:
            chapters.append(
                f'<section class="chapter" id="{chap_id}">\n'
                f'  <div class="ch-head">\n'
                f'    <span class="ch-id">TR-00</span>\n'
                f'    <h1 class="ch-title">{html.escape(title)}</h1>\n'
                f"  </div>\n"
                f"  <div class=\"ch-body\">\n    {body}\n  </div>\n"
                f"</section>"
            )
        else:
            tag = f"L{idx-1}"
            chapters.append(
                f'<section class="chapter" id="{chap_id}">\n'
                f'  <div class="ch-head">\n'
                f'    <span class="ch-id">TR-{idx:02d}</span>\n'
                f'    <h1 class="ch-title">{html.escape(title)}</h1>\n'
                f'    <span class="ch-tag">{tag}</span>\n'
                f"  </div>\n"
                f'  <div class="ch-body">\n    {body}\n  </div>\n'
                f"</section>"
            )

    nav = ['<a href="#00-cover" data-sec="00-cover">Start</a>']
    for idx, (fname, title) in enumerate(ORDER):
        if idx == 0:
            continue
        nav.append(f'<a href="#{fname}" data-sec="{fname}">{html.escape(title)}</a>')

    page = f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TRENDREIS — van signaal tot stip op de horizon</title>
<meta name="description" content="Wat ik de trendweken leerde, en hoe ik die verbind met het bedrijf dat ik wil bouwen.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="theme.css">
</head>
<body>
<div class="shell" data-3d="on">
  <header class="topbar">
    <span class="wordmark">TRENDREIS<span class="dim"> / ontdekkingsreis</span></span>
    <span class="spacer"></span>
    <nav class="nav" aria-label="Hoofdstukken">{''.join(nav)}</nav>
    <span class="tb-sep"></span>
    <button class="btn" id="d3Btn" aria-pressed="true" title="Rood-cyan 3D aan/uit"><span class="dot"></span>3D</button>
    <button class="btn" id="themeBtn" title="Thema wisselen">LIGHT</button>
  </header>

  <main class="main">
    <div class="readcol">

      <section class="chapter hero" id="scene" style="scroll-margin-top:70px">
        <div class="hero-stage">
          <div class="hero-head">
            <h1 class="hero-title">TREND<span class="accent">REIS</span></h1>
            <p class="hero-sub">van signaal tot stip op de horizon</p>
            <p class="hero-meta">Marlo van Gulik · ONDEON18 · Onderneem! De Ontdekkingsreis</p>
            <p class="hero-meta">HAN University of Applied Sciences — oktober 2026</p>
          </div>
          {anaglyph_svg()}
          <div class="hero-controls">
            <span class="depth" id="depthWrap">
              <span>DIEPTE</span>
              <input type="range" id="depthRange" min="0" max="30" step="1" value="10" aria-label="3D diepte">
              <span class="dnum" id="depthNum">10px</span>
            </span>
            <span class="hint">rood-cyan brilletjes voor de 3D · zonder bril ook leesbaar</span>
            <span class="spacer"></span>
            <a class="btn" href="#00-cover">LEES →</a>
          </div>
        </div>
      </section>

      {''.join(chapters)}

    </div>
  </main>

  <footer class="foot">
    <p class="quote">"Je verkoopt niet de wafel — je verkoopt het gevoel dat iemand jou uit de brand helpt."</p>
  </footer>

  <div class="statusbar">
    <span class="dot"></span>
    <span>TRENDREIS · TK1</span>
    <span class="sig">qwen 3.8 27b · lokaal</span>
    <span class="grow"></span>
    <span>3D: <span id="sb3d">AAN</span></span>
    <span>© 2026 M. van Gulik</span>
  </div>
</div>
<script src="main.js"></script>
</body>
</html>
"""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"OK: {OUT} ({len(page)} bytes, {len(ORDER)} hoofdstukken)")


if __name__ == "__main__":
    build()
