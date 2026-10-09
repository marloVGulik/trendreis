#!/usr/bin/env python3
"""TRENDREIS — bouwt de MULTI-PAGE site (orange console) uit content/*.md.

Gebruik:  python3 scripts/build_site.py
Leest:    content/00-cover.md .. content/07-colofon.md  (+ AI-chat/transcript.md)
Schrijft: site/index.html + site/<hoofdstuk>.html + site/ai-chat.html + site/materiaal.html
          (+ kopieert foto's naar site/media/)

Layout: linksidebar · inhoud over volle breedte · speelse vakken (grid) ·
figuren (SVG) · bron-quotes die linken naar de notebook-foto (rechthoek) ·
AI-chat in een nep-console-venster · light/dark + 3D (anaglyph op de home).
"""
import html
import math
import random
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
SITE = ROOT / "site"
MEDIA = SITE / "media"
NB_DIR = MEDIA / "notebook"
RAW = ROOT / "raw-data"
HUNTER = ROOT / "hunter-pics"
TRANSCRIPT = ROOT / "AI-chat" / "transcript.md"
RAW_JSONL = ROOT / "AI-chat" / "sessie-01a10830.jsonl"

# ---------------------------------------------------------------------- pages
PAGES = [
    {"file": "00-cover", "page": "index.html", "id": "home", "num": "00",
     "title": "Cover", "short": "van signaal tot stip op de horizon"},
    {"file": "01-wie-ben-ik", "page": "wie-ben-ik.html", "id": "wie-ben-ik", "num": "01",
     "title": "Wie ben ik?", "short": "ikigai, levenswiel, gewoonten, doelen en mijn eerste €5"},
    {"file": "02-signalen", "page": "signalen.html", "id": "signalen", "num": "02",
     "title": "Signalen", "short": "zes vensters: Tegenlicht, FutureFit, de Hunt en mijn eigen radar"},
    {"file": "03-analyseren", "page": "analyseren.html", "id": "analyseren", "num": "03",
     "title": "Analyseren", "short": "trends, de trendpyramide, DESTEP, scenario’s en de trendcanvas"},
    {"file": "04-waardeverschuivingen", "page": "waardeverschuivingen.html", "id": "waardeverschuivingen", "num": "04",
     "title": "Waardeverschuivingen", "short": "van bezit naar bereik, consumer naar prosumer, en de food future"},
    {"file": "05-bedrijf", "page": "bedrijf.html", "id": "bedrijf", "num": "05",
     "title": "Het bedrijf", "short": "de kern: 5 ideeën, de noorderster en hoe ik valideer"},
    {"file": "06-reis", "page": "reis.html", "id": "reis", "num": "06",
     "title": "De reis", "short": "het pad dat ik liep, wat er nu komt, en de volgende stappen"},
    {"file": "07-colofon", "page": "colofon.html", "id": "colofon", "num": "07",
     "title": "Bronnen & colofon", "short": "methode, proces, AI-gebruik en APA-bronnen"},
]
EXTRA_PAGES = [
    {"page": "ai-chat.html", "id": "ai-chat", "num": "AI", "title": "AI-chat",
     "short": "de volledige chat (prompt → reactie) in een console-venster"},
    {"page": "materiaal.html", "id": "materiaal", "num": "M", "title": "Materiaal",
     "short": "mijn notebook: de originele foto’s met de bron-quotes gemarkeerd"},
]
ALL_PAGES = PAGES + EXTRA_PAGES

# figuren: (naam, insert_voor_section_title | "intro")
FIGURES = {
    "wie-ben-ik": [
        ("ikigai", "Ikigai"),
        ("levenswiel", "Levenswiel (2026-09-04)"),
    ],
    "analyseren": [
        ("assenstelsel", "Trendwoorden & het assenstelsel"),
        ("trendcanvas", "Trendcanvas — van trend naar innovatie"),
        ("automaten", "Trendcanvas — van trend naar innovatie"),
        ("prisma", "De trendpyramide"),
    ],
    "waardeverschuivingen": [
        ("pyramide_c", "intro"),
    ],
}

# hunter-foto’s (ch.2 “Mijn foto’s”)
HUNTER_PHOTOS = [
    ("electrische-bakfietsen", "Elektrische bakfietsen", "meer kinderen naar school + boodschappen"),
    ("grote-suv-autos", "Grote SUV-autos", "een oude Volvo 240 was toen “groot”, nu is dat gemiddeld-klein"),
    ("nostalgie-voor-automodellen", "Nostalgie voor automodellen", "merken brengen modellen terug (o.a. e-Mustang)"),
    ("slimme-parkeerplaats-kentekenherkenning", "Slimme parkeerplaatsen", "kentekenherkenning wordt standaard in parkeergarages"),
]

# bron-quotes → rechthoek op de notebook-foto (x%, y%, w%, h%)
HIGHLIGHTS = {
    "robot-huisdier": {"photo": "P04-05", "box": [3, 89, 20, 7],
                       "label": "P04-05 · 12 ideeën, nr. 11", "quote": "Robot huisdier!"},
    "food-70-10": {"photo": "P18-19", "box": [55, 42.5, 31, 6],
                   "label": "P18-19 · the future / food", "quote": "van 70% uitgaven aan voedsel naar 10%"},
    "salatomaat": {"photo": "P12-13", "box": [5, 69.5, 26, 9],
                   "label": "P12-13 · ideeën, nr. 2", "quote": "Saladomat — automatische salade"},
    "automatisering-regels": {"photo": "P10-11", "box": [5, 76.5, 46, 8],
                              "label": "P10-11 · Tegenlicht, game of drones",
                              "quote": "deze sector kan veel automatisering niet aan vanwege regels"},
    "ikigai-open-source": {"photo": "Opdr-ikigai-voorkant", "box": [59, 56, 38, 21],
                           "label": "Ikigai · open-source-annotatie",
                           "quote": "bedrijven begeleiden naar … open-source … automatisering software voor bedrijven"},
}

# APA-bronnen (colofon § Bronnen)
BRONNEN = [
    {"label": "Tegenlicht — “Game of drones”",
     "apa": 'Tegenlicht. (2025, 5 april). <em>Game of drones</em> [Webartikel]. VPRO. <a href="https://tegenlicht.vpro.nl/artikelen/game-of-drones" target="_blank" rel="noopener">tegenlicht.vpro.nl/artikelen/game-of-drones</a>',
     "used": "venster 1 (signalen) + assenstelsel (analyseren)"},
    {"label": "POM — “Iedereen rijk door vibecoding”",
     "apa": 'POM. (2026). <em>Iedereen rijk door vibecoding</em> [Podcast-episode]. Spotify. <a href="https://open.spotify.com/episode/12ufJLmLnb4jIljfzwve0X" target="_blank" rel="noopener">open.spotify.com/episode/12ufJLmLnb4jIljfzwve0X</a>',
     "used": "scanplan + disposable/vibecoding-software (signalen)"},
]


# =================================================================== inline
def inline(t: str) -> str:
    t = html.escape(t, quote=False)
    # bron-quote marker → chip die naar de notebook-foto linkt
    t = re.sub(r"\{#bron:([A-Za-z0-9_-]+)\}",
               r'<a class="bron-chip" href="materiaal.html?hl=\1" title="Bekijk deze zin in mijn schrift (rechthoek op de foto)">↳ schrift</a>',
               t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return t


# =================================================================== blocks
def render_table(rows):
    def cells(line):
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        return [c.strip() for c in line.split("|")]
    parsed = [cells(r) for r in rows]
    parsed = [r for r in parsed if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
    if not parsed:
        return ""
    head, *body = parsed
    th = "".join(f"<th>{inline(c)}</th>" for c in head)
    trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
    return ('<div class="tblwrap"><table class="tbl">'
            f"<thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>")


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
        elif ln[:1] in (" ", "\t") and items:
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
        if re.fullmatch(r"-{3,}|\*{3,}", stripped):
            flush_para()
            out.append("<hr>")
            i += 1
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if m:
            flush_para()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue
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
            body, cur = [], []
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
        if stripped.startswith("|"):
            flush_para()
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(render_table(rows))
            continue
        if LIST_RE.match(line):
            flush_para()
            html_list, i = consume_list(lines, i)
            out.append(html_list)
            continue
        para.append(stripped)
        i += 1
    flush_para()
    return "\n".join(out)


def split_sections(md: str):
    """Scheidt (intro, [(title, html), ...]) op basis van H2-koppen."""
    lines = md.splitlines()
    intro = []
    sections = []
    cur_title = None
    cur_body = []
    for ln in lines:
        m = re.match(r"^##\s+(.*)$", ln.strip())
        if m:
            if cur_title is None:
                intro.append(ln)
            else:
                sections.append((cur_title, "\n".join(cur_body)))
            cur_title = m.group(1)
            cur_body = []
        elif cur_title is None:
            intro.append(ln)
        else:
            cur_body.append(ln)
    if cur_title is not None:
        sections.append((cur_title, "\n".join(cur_body)))
    intro_html = md_to_html("\n".join(intro)).strip()
    return intro_html, [(t, md_to_html(b).strip()) for t, b in sections]


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def span_for(html_body):
    """kort → half vak, lang → volledig vak."""
    return 2 if len(strip_tags(html_body)) > 520 else 1


# =================================================================== figuren
def _svg_open(label, w, h):
    return (f'<svg class="fig" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="{html.escape(label)}" preserveAspectRatio="xMidYMid meet">')


def fig_ikigai():
    # ---- 3D-ikigai: vier overlappende schijven in één vlak + kern, interactief draaien ----
    import json
    scene = {
        "center": [0, 0, 2],
        "disks": [
            {"c": [0, 0.44, 2], "r": 0.46, "br": 0.34},
            {"c": [-0.44, 0, 2], "r": 0.46, "br": 0.30},
            {"c": [0.44, 0, 2], "r": 0.46, "br": 0.30},
            {"c": [0, -0.44, 2], "r": 0.46, "br": 0.30},
            {"c": [0, 0, 2.02], "r": 0.17, "br": 0.95}
        ],
        "labels": [
            {"p": [0, 0.92, 2], "t": "waar je van houdt", "dy": -4, "cls": "lbl-dim"},
            {"p": [-0.92, 0, 2], "t": "waar je goed in bent", "dx": -6, "dy": 4, "anchor": "end"},
            {"p": [0.92, 0, 2], "t": "wat de wereld nodig heeft", "dx": 6, "dy": 4, "anchor": "start"},
            {"p": [0, -0.92, 2], "t": "waar je voor betaald kunt worden", "dy": 14, "cls": "lbl-dim"},
            {"p": [-0.21, 0.21, 2.06], "t": "PASSIE", "cls": "lbl-dim", "fs": 10},
            {"p": [0.21, 0.21, 2.06], "t": "MISSIE", "cls": "lbl-dim", "fs": 10},
            {"p": [-0.21, -0.21, 2.06], "t": "BEROEP", "cls": "lbl-dim", "fs": 10},
            {"p": [0.21, -0.21, 2.06], "t": "ROEPING", "cls": "lbl-dim", "fs": 10},
            {"p": [0, 0, 2.1], "t": "IKIGAI", "dy": 4, "cls": "lbl-accent", "fs": 12}
        ],
        "params": {"F": 1.5, "S": 175, "CX": 300, "CY": 150,
                    "camL": [-0.02, 0.1, 0], "camR": [0.02, 0.1, 0],
                    "viewBox": "0 0 600 300"}
    }
    aria = "Ikigai in 3D: vier overlappende schijven (waar je van houdt / goed in bent / wat de wereld nodig heeft / waar je voor betaald wordt) met de kern IKIGAI. Sleep om te draaien."
    scene_json = json.dumps(scene, separators=(",", ":"))
    return (f'<div class="anaglyph-orbit" role="img" aria-label="{aria}" '
            f'data-scene=\'{scene_json}\'>')
    + '<div class="orbit-hint">&#8596; sleep om te draaien</div></div>'


def fig_levenswiel():
    # ---- 3D-levenswiel: vlakke schijf + 8 spaken, "werk & school" gemarkeerd, interactief draaien ----
    import json, math
    labels = ["vrienden", "romantiek", "gezondheid", "ontwikkeling",
              "werk & school", "ontspanning & plezier", "maatschappelijke bijdrage", "liefde & familie"]
    n = len(labels); R = 0.78
    spokes, lbls = [], []
    for i in range(n):
        a = math.radians(-90 + i * (360.0 / n))
        hot = (i == 4)  # "werk & school"
        ex, ey = R * math.cos(a), R * math.sin(a)
        spokes.append({"a": [0, 0, 2], "b": [round(ex, 3), round(ey, 3), 2],
                       "w": 2.6 if hot else 1.6, "br": 1.0 if hot else 0.78})
        lx, ly = (R * 1.28) * math.cos(a), (R * 1.28) * math.sin(a)
        c = math.cos(a)
        anchor = "start" if c > 0.35 else ("end" if c < -0.35 else "middle")
        lbls.append({"p": [round(lx, 3), round(ly, 3), 2.02], "t": labels[i],
                     "anchor": anchor, "cls": "lbl-accent" if hot else "lbl-dim", "fs": 10})
    scene = {
        "center": [0, 0, 2],
        "disks": [{"c": [0, 0, 2], "r": R, "br": 0.42}],
        "lines": spokes,
        "points": [{"p": [0, 0, 2.04], "hot": True}],
        "labels": lbls + [{"p": [0, 0, 2.1], "t": "eigenaarschap", "dy": 3, "cls": "lbl-dim", "fs": 11}],
        "params": {"F": 1.5, "S": 150, "CX": 300, "CY": 150,
                    "camL": [-0.02, 0.1, 0], "camR": [0.02, 0.1, 0],
                    "viewBox": "0 0 600 300"}
    }
    aria = "Levenswiel in 3D: acht segmenten rond eigenaarschap, met werk & school gemarkeerd. Sleep om te draaien."
    scene_json = json.dumps(scene, separators=(",", ":"))
    return (f'<div class="anaglyph-orbit" role="img" aria-label="{aria}" '
            f'data-scene=\'{scene_json}\'>')
    + '<div class="orbit-hint">&#8596; sleep om te draaien</div></div>'


def fig_assenstelsel():
    # ---- 3D-assenstelsel (bipolair, −1 tot +1) — INTERACTIEF: camera draait bij muis-sleep ----
    # Scène-data als JSON; JavaScript projecteert (twee camera's) en rendert live.
    import json
    scene = {
        "center": [0, 0, 2],
        "axes": [
            {"a": [-1, 0, 2], "b": [1, 0, 2], "w": 1.6},
            {"a": [0, -1, 2], "b": [0, 1, 2], "w": 1.6},
            {"a": [0, 0, 1], "b": [0, 0, 3], "w": 1.3, "dash": "4 4"}
        ],
        "points": [
            {"p": [-0.3, 0.2, 2.2], "label": "open source", "hot": True, "ldx": -8, "ldy": -3, "anchor": "end"},
            {"p": [0.2, 0.3, 2.4], "label": "lokale AI", "hot": False, "ldx": 2, "ldy": -15, "anchor": "middle"},
            {"p": [0.3, -0.2, 2.6], "label": "automatisering", "hot": False, "ldx": 9, "ldy": 4, "anchor": "start"},
            {"p": [-0.2, -0.3, 2.8], "label": "robot huisdier", "hot": True, "ldx": -4, "ldy": 22, "anchor": "middle"}
        ],
        "origin": [0, 0, 2],
        "endLabels": [
            {"p": [1, 0, 2], "t": "+", "dx": 8, "dy": 4, "anchor": "start"},
            {"p": [-1, 0, 2], "t": "−", "dx": -8, "dy": 4, "anchor": "end"},
            {"p": [0, 1, 2], "t": "+", "dx": 8, "dy": -6, "anchor": "start"},
            {"p": [0, -1, 2], "t": "−", "dx": 8, "dy": 14, "anchor": "start"},
            {"p": [0, 0, 3], "t": "+", "dx": 8, "dy": 4, "anchor": "start"},
            {"p": [0, 0, 1], "t": "−", "dx": 8, "dy": 14, "anchor": "start"}
        ],
        "params": {"F": 1.5, "S": 180, "CX": 300, "CY": 150,
                    "camL": [-0.02, 0.1, 0], "camR": [0.02, 0.1, 0],
                    "viewBox": "0 0 600 300"}
    }
    aria = "Assenstelsel in 3D: drie bipolaire assen (−1 tot +1), signalen in verschillende kwadranten (concept). Sleep met de muis om te draaien."
    scene_json = json.dumps(scene, separators=(",", ":"))
    return (f'<div class="anaglyph-orbit" role="img" aria-label="{aria}" '
            f'data-scene=\'{scene_json}\'>'
            f'<div class="orbit-hint">&#8596; sleep om te draaien</div></div>')


def fig_trendcanvas():
    # ---- 3D-trendcanvas: acht blokken in een 2x4-rooster, interactief draaien ----
    import json
    steps = [
        ("Trend", False), ("Basisbehoeften", False), ("Inspiratie", False), ("Drivers", False),
        ("Verwachtingen", False), ("Innovatie-type", False), ("Voor wie", False), ("Mijn innovatie", True),
    ]
    xs = [-1.55, -0.52, 0.52, 1.55]; ys = [0.6, -0.6]
    blocks = []
    for i, (lab, hot) in enumerate(steps):
        r, c = divmod(i, 4)
        blocks.append({"c": [xs[c], ys[r], 2], "w": 0.44, "h": 0.44, "d": 0.3,
                       "label": lab, "hot": hot, "br": 1.0 if hot else 0.6})
    scene = {
        "center": [0, 0, 2],
        "blocks": blocks,
        "params": {"F": 1.5, "S": 120, "CX": 300, "CY": 150,
                    "camL": [-0.02, 0.12, 0], "camR": [0.02, 0.12, 0],
                    "viewBox": "0 0 600 300"}
    }
    aria = "Trendcanvas in 3D: acht stappen van trend naar mijn innovatie, als 3D-blokjes in een rooster. Sleep om te draaien."
    scene_json = json.dumps(scene, separators=(",", ":"))
    return (f'<div class="anaglyph-orbit" role="img" aria-label="{aria}" '
            f'data-scene=\'{scene_json}\'>')
    + '<div class="orbit-hint">&#8596; sleep om te draaien</div></div>'


def fig_automaten():
    # ---- 3D-alles-automaten: vlakke kaart (wegen) + 4 automaten als 3D-blokjes, interactief draaien ----
    import json
    roads = [
        {"a": [-1, 0.55, 2], "b": [1, 0.55, 2], "w": 1.2, "br": 0.45},
        {"a": [-1, 0, 2], "b": [1, 0, 2], "w": 1.2, "br": 0.45},
        {"a": [-1, -0.55, 2], "b": [1, -0.55, 2], "w": 1.2, "br": 0.45},
        {"a": [-0.55, 0.55, 2], "b": [-0.55, -0.55, 2], "w": 1.2, "br": 0.45},
        {"a": [0.1, 0.55, 2], "b": [0.1, -0.55, 2], "w": 1.2, "br": 0.45},
        {"a": [0.75, 0.55, 2], "b": [0.75, -0.55, 2], "w": 1.2, "br": 0.45},
    ]
    autos = [(-0.55, 0.55, True), (0.1, 0.0, True), (0.75, 0.55, False), (0.1, -0.55, True)]
    blocks = [{"c": [x, y, 2.06], "w": 0.3, "h": 0.4, "d": 0.24, "br": 1.0 if on else 0.4} for (x, y, on) in autos]
    scene = {
        "center": [0, 0, 2],
        "lines": roads,
        "blocks": blocks,
        "points": [{"p": [0.75, 0.55, 2.02], "hot": False}],
        "labels": [
            {"p": [0, 0.82, 2], "t": "status · inhoud · locatie", "cls": "lbl-dim", "fs": 10},
            {"p": [0, -0.82, 2], "t": "helder = actief  ·  dof = leeg", "cls": "lbl-dim", "fs": 10}
        ],
        "params": {"F": 1.5, "S": 130, "CX": 300, "CY": 150,
                    "camL": [-0.02, 0.12, 0], "camR": [0.02, 0.12, 0],
                    "viewBox": "0 0 600 300"}
    }
    aria = "Alles-automaten in 3D: een kaart met wegen en vier automaten als 3D-blokjes (helder = actief, dof = leeg). Sleep om te draaien."
    scene_json = json.dumps(scene, separators=(",", ":"))
    return (f'<div class="anaglyph-orbit" role="img" aria-label="{aria}" '
            f'data-scene=\'{scene_json}\'>')
    + '<div class="orbit-hint">&#8596; sleep om te draaien</div></div>'


def fig_prisma():
    # ---- 3D-prisma: elk vlak = een thema. Je draait rond het prisma en leest de vier vlakken. ----
    import json
    themes = [
        {"n": [0, 0, -1], "u": [1, 0, 0], "v": [0, 1, 0], "pts": [[-1,0,-1],[1,0,-1],[1,1,-1],[-1,1,-1]],
         "lines": [{"t": "AI &amp; data", "dy": -18, "fs": 16}, {"t": "T 14 · S 6", "dy": 4, "fs": 11},
                   {"t": "14 signalen", "dy": 22, "fs": 12}]},
        {"n": [1, 0, 0], "u": [0, 0, -1], "v": [0, 1, 0], "pts": [[1,0,-1],[1,0,1],[1,1,1],[1,1,-1]],
         "lines": [{"t": "Automatisering", "dy": -18, "fs": 16}, {"t": "&amp; robots", "dy": 4, "fs": 16},
                   {"t": "T 7 · P 2", "dy": 24, "fs": 12}]},
        {"n": [0, 0, 1], "u": [-1, 0, 0], "v": [0, 1, 0], "pts": [[1,0,1],[-1,0,1],[-1,1,1],[1,1,1]],
         "lines": [{"t": "Vertrouwen &amp;", "dy": -18, "fs": 16}, {"t": "soevereiniteit", "dy": 4, "fs": 16},
                   {"t": "P 9 · S 4", "dy": 24, "fs": 12}]},
        {"n": [-1, 0, 0], "u": [0, 0, 1], "v": [0, 1, 0], "pts": [[-1,0,1],[-1,0,-1],[-1,1,-1],[-1,1,1]],
         "lines": [{"t": "Geld &amp;", "dy": -18, "fs": 16}, {"t": "economische", "dy": 4, "fs": 16},
                   {"t": "E(econ) 10", "dy": 24, "fs": 12}]},
        {"n": [0, 1, 0], "u": [1, 0, 0], "v": [0, 0, -1], "pts": [[-1,1,-1],[1,1,-1],[1,1,1],[-1,1,1]],
         "lines": [{"t": "4 thema&#39;s", "dy": 0, "fs": 13}], "br": 0.85},
    ]
    scene = {
        "center": [0, 0.4, 2.1],
        "prism": {"c": [0, 0.0, 2.1], "half": 0.5, "height": 0.8, "faces": themes},
        "params": {"F": 1.5, "S": 210, "CX": 300, "CY": 170,
                   "camL": [-0.02, 0.1, 0], "camR": [0.02, 0.1, 0],
                   "viewBox": "0 0 600 300"}
    }
    aria = ("3D-prisma met vier vlakken, een vlak per gekozen thema: AI & data, Automatisering & robots, "
            "Vertrouwen & soevereiniteit, Geld & economie. Sleep om rond het prisma te draaien.")
    scene_json = json.dumps(scene, separators=(",", ":"))
    return (f'<div class="anaglyph-orbit" role="img" aria-label="{aria}" '
            f'data-scene=\'{scene_json}\'>') + (
            '<div class="orbit-hint">&#8596; sleep om te draaien</div></div>')

def fig_pyramide_c():
    # ---- 3D-piramide (via de Anaglyph-motor) ----
    a = Anaglyph(viewBox="0 0 420 320", aria="Waardepiramide C: 3D-piramide, leeg frame nog te vullen (3 lagen)",
                 CX=210, CY=190, F=1.4, S=92, camL=(-0.08, 1.0, 0.0), camR=(0.08, 1.0, 0.0))
    H, B, ZC = 1.5, 1.0, 2.0              # apex-hoogte, basis-halfte, diepte-centrum
    apex = (0, H, ZC)
    base = [(-B, 0, ZC - B), (B, 0, ZC - B), (B, 0, ZC + B), (-B, 0, ZC + B)]   # nabij, nabij, ver, ver
    faces = [                                                              # (punten, normale) => schaduw
        ([apex, base[3], base[0]], (0, 0.5, -1)),   # voor (nabij)
        ([apex, base[1], base[2]], (1, 0.5, 0)),    # rechts
        ([apex, base[2], base[3]], (0, 0.5, 1)),    # achter (ver)
        ([apex, base[0], base[1]], (-1, 0.5, 0)),   # links
    ]
    tiers = [0.34, 0.67]                                                   # 3 lagen (2 scheidingslijnen)
    def tier_sq(frac):
        y = H * frac; hw = B * (1 - frac)
        return [(-hw, y, ZC - hw), (hw, y, ZC - hw), (hw, y, ZC + hw), (-hw, y, ZC + hw)]
    def render(cam, channel):
        fd = []
        for (pts, n) in faces:
            proj = [a.P(p, cam) for p in pts]
            if all(proj): fd.append((sum(p[2] for p in pts) / len(pts), pts, a.brightness(n)))
        fd.sort(key=lambda d: d[0], reverse=True)                          # ver -> nabij (solide)
        o = [a.poly(pts, cam, a.facefill(b, channel), stroke=a.facefill(b * 0.35, channel), sw=1.6)
             for _, pts, b in fd]
        for frac in tiers:                                                # tier-scheidingslijnen
            sq = tier_sq(frac)
            o += [a.line(sq[i], sq[(i + 1) % 4], cam, a.facefill(0.55, channel), 1.2, dash="4 4") for i in range(4)]
        return "".join(o)
    labels = []                                                           # flat 2D-labels (blijven leesbaar)
    for frac, txt in [(0.98, "top"), (0.5, "laag 2"), (0.02, "laag 1")]:
        p = a.center_proj((B * (1 - frac) + 0.15, H * frac, ZC))
        if p: labels.append(f'<text x="{p[0] + 12:.1f}" y="{p[1] + 4:.1f}" class="lbl-dim" font-size="12">{txt}</text>')
    p0 = a.center_proj((0, -0.12, ZC))
    if p0: labels.append(f'<text x="210" y="{min(p0[1] + 22, 312):.1f}" text-anchor="middle" class="lbl-dim" font-size="11">concept — nog te vullen</text>')
    return a.render(render, labels="".join(labels))


# ---- 3D-anaglyph motor (herbruikbaar voor alle figuren) ---------------------------
# Echte twee-camera-anaglyph (standaard bril: links=rood, rechts=cyaan). De 3D-scène
# wordt tweemaal in perspectief geprojecteerd (links- en rechts-oog); de beelden
# overlappen en de hersenen smelten ze tot 3D. Geen "offset-truc" maar echte paralaxe.
class Anaglyph:
    def __init__(self, camL=(-0.06, 1.0, 0.0), camR=(0.06, 1.0, 0.0),
                 F=1.4, S=300.0, CX=400, CY=155, viewBox="0 80 800 240", aria=""):
        self.camL, self.camR = camL, camR
        self.F, self.S, self.CX, self.CY = F, S, CX, CY
        self.viewBox, self.aria = viewBox, aria
        _l = (0.0, 0.35, -1.0)                      # lichtbron van boven-vóór => 3D-vorm
        _lm = math.sqrt(sum(c * c for c in _l))
        self.LIGHT = tuple(c / _lm for c in _l)
    def P(self, pt, cam):
        px, py, pz = pt; cx, cy, cz = cam
        rz = pz - cz
        if rz <= 0.02: return None
        return (self.CX + self.F * (px - cx) / rz * self.S, self.CY - self.F * (py - cy) / rz * self.S)
    def brightness(self, n):
        d = n[0] * self.LIGHT[0] + n[1] * self.LIGHT[1] + n[2] * self.LIGHT[2]
        return 0.22 + 0.78 * max(0.0, d)
    def facefill(self, b, channel):
        if channel == 'red':
            return 'rgb(%d,%d,%d)' % (int(255 * b), int(16 * b), int(16 * b))
        return 'rgb(0,%d,%d)' % (int(229 * b), int(229 * b))
    def poly(self, pts, cam, fill, stroke=None, sw=1.5, opacity=None):
        r = [self.P(p, cam) for p in pts]
        if all(r):
            s = '<polygon points="%s" fill="%s"' % (" ".join(f"{x:.1f},{y:.1f}" for x, y in r), fill)
            if opacity is not None: s += f' fill-opacity="{opacity}"'
            if stroke: s += f' stroke="{stroke}" stroke-width="{sw}"'
            return s + "/>"
        return ""
    def line(self, a, b, cam, stroke, sw=1.5, dash=None):
        pa, pb = self.P(a, cam), self.P(b, cam)
        if pa and pb:
            s = f'<line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" stroke="{stroke}" stroke-width="{sw}"'
            if dash: s += f' stroke-dasharray="{dash}"'
            return s + "/>"
        return ""
    def circle(self, center, radius, cam, fill):
        p = self.P(center, cam)
        if not p: return ""
        p2 = self.P((center[0] + radius, center[1], center[2]), cam)
        r = abs(p2[0] - p[0]) if p2 else radius
        return f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{r:.1f}" fill="{fill}"/>'
    def render(self, render_scene, labels=""):
        """render_scene(cam, channel) -> SVG van de scène vanuit één camera.
        labels: optionele FLAT 2D-tekst (niet in rood/cyaan) die over de scène heen ligt."""
        red = render_scene(self.camL, 'red')
        cyan = render_scene(self.camR, 'cyan')
        lab = f'\n  <g id="anaglyphLabels" class="anaglyph-labels">{labels}</g>' if labels else ""
        return (f'<svg class="anaglyph" viewBox="{self.viewBox}" preserveAspectRatio="xMidYMid meet" '
                f'role="img" aria-label="{self.aria}">\n'
                f'  <g id="chR" class="chR">{red}</g>\n'
                f'  <g id="chC" class="chC">{cyan}</g>{lab}\n'
                f'</svg>')
    def center_proj(self, pt):
        """projectie vanuit een midden-camera (geen offset) => voor 2D-labelposities."""
        return self.P(pt, (0.0, self.camL[1], 0.0))


def anaglyph_svg():
    # ---- 3D-hero (via de herbruikbare Anaglyph-motor) ----
    # Een WEG met DUNNE mijlpalen + VLIEGENDE blokken + noorderster. Richting A: "reis met stappen".
    a = Anaglyph(aria="Een weg met mijlpalen die naar een noorderster op de horizon loopt — de trendreis, in 3D")
    # ---- 3D-scene (wereldcoordinaten: x=links/rechts, y=omhoog, z=verder) ----
    # Een WEG met DUNNE 3D-mijlpalen (slanke zuilen) + WILLEKEURIG VLIEGENDE 3D-blokjes
    # (elk met een vaste willekeurige rotatie) die rondom vliegen en uit het scherm springen,
    # richting de noorderster. Grote ingevulde vlakken => rood+cyaan smelten tot 3D.
    RW = 0.95                  # pad-halfte-breedte
    ZN, ZF = 3.0, 28.0         # pad: nabij -> horizon
    road = [(-RW,0,ZN),(RW,0,ZN),(RW,0,ZF),(-RW,0,ZF)]
    cross = [((-RW,0,z),(RW,0,z)) for z in (4.5,6.5,9.5,14,20,26)]
    edges = [((-RW,0,ZN),(-RW,0,ZF)), ((RW,0,ZN),(RW,0,ZF)), ((0,0,ZN),(0,0,ZF))]
    # mijlpalen = DUNNE, slanke zuilen (cx, z, breedte, hoogte, diepte), afwisselend + gespreid
    milestones = [
        ( 0.55,  5.0, 0.38, 1.65, 0.26),
        (-0.55, 10.5, 0.38, 1.65, 0.26),
        ( 0.50, 16.5, 0.32, 1.40, 0.24),
        (-0.45, 23.0, 0.28, 1.15, 0.22),
    ]
    star = (0, 1.6, 28)
    # vliegende blokken: goed gespreid rond de scène (losse bits, geen blob), elk met een
    # willekeurige rotatie (seed => reproduceerbaar)
    rng = random.Random(20261011)
    flying_pos = [(-3.1, 1.8, 10.0), (-2.7, 0.9, 16.0), (3.2, 2.8, 14.0),
                  (2.9, 1.4, 20.0), (-0.4, 3.2, 27.0)]
    flying_sz = [0.28, 0.28, 0.28, 0.28, 0.28]   # alle blokken even groot => 3D-effect puur op diepte (geen grootte-correlatie)
    flying = [(x, y, z, flying_sz[i],
               (rng.uniform(0, 2*math.pi), rng.uniform(0, 2*math.pi), rng.uniform(0, 2*math.pi)))
              for i, (x, y, z) in enumerate(flying_pos)]
    def rot3(p, rx, ry, rz):
        x, y, z = p
        c, s = math.cos(rx), math.sin(rx); y, z = y*c - z*s, y*s + z*c
        c, s = math.cos(ry), math.sin(ry); x, z = x*c + z*s, -x*s + z*c
        c, s = math.cos(rz), math.sin(rz); x, y = x*c - y*s, x*s + y*c
        return (x, y, z)
    CUBE = [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]
    CUBE_F = [[0,1,2,3,(0,0,-1)],[4,5,6,7,(0,0,1)],[0,3,7,4,(-1,0,0)],[1,2,6,5,(1,0,0)],[0,1,5,4,(0,-1,0)],[3,2,6,7,(0,1,0)]]
    def cube(center, size, rot, cam, channel):
        cx, cy, cz = center; s = size/2
        pts = [(rot3(p, *rot)[0]+cx, rot3(p, *rot)[1]+cy, rot3(p, *rot)[2]+cz) for p in CUBE]
        data = []
        for f in CUBE_F:
            idx = f[:4]; n = rot3(f[4], *rot)
            proj = [a.P(pts[i], cam) for i in idx]
            if all(proj): data.append((sum(pts[i][2] for i in idx)/len(idx), proj, a.brightness(n)))
        data.sort(key=lambda d: d[0], reverse=True)   # ver -> nabij (painter's order => solide)
        return "".join('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.2"/>' % (
            " ".join(f"{x:.1f},{y:.1f}" for x, y in proj), a.facefill(b, channel), a.facefill(b*0.4, channel))
            for _, proj, b in data)
    def faces_of(cx, z, w, h, d):
        x0, x1 = cx - w/2, cx + w/2
        z0, z1 = z - d/2, z + d/2
        front = ([(x0,0,z0),(x1,0,z0),(x1,h,z0),(x0,h,z0)], (0,0,-1))
        top   = ([(x0,h,z0),(x1,h,z0),(x1,h,z1),(x0,h,z1)], (0,1,0))
        left  = ([(x0,0,z0),(x0,0,z1),(x0,h,z1),(x0,h,z0)], (-1,0,0))
        right = ([(x1,0,z0),(x1,0,z1),(x1,h,z1),(x1,h,z0)], (1,0,0))
        return [front, top, (left if cx > 0 else right)]
    def render(cam, channel):
        o = [a.poly(road, cam, "currentColor", opacity=0.3)]
        o += [a.line(a_, b_, cam, "currentColor", 1.5) for (a_, b_) in cross]
        o += [a.line(a_, b_, cam, "currentColor", 2.0) for (a_, b_) in edges]
        # ALLE 3D-objecten (palen + blokken + ster) sorteer op diepte (ver -> nabij) => correcte overlap
        objs = [(z, ('milestone', cx, z, w, h, d)) for (cx, z, w, h, d) in milestones]
        objs += [(cz, ('cube', cx, cy, cz, size, rot)) for (cx, cy, cz, size, rot) in flying]
        objs.append((star[2], ('star',)))
        objs.sort(key=lambda x: x[0], reverse=True)
        for depth, spec in objs:
            kind = spec[0]
            if kind == 'milestone':
                _, cx, z, w, h, d = spec
                for pts, n in faces_of(cx, z, w, h, d):
                    b = a.brightness(n)
                    o.append(a.poly(pts, cam, a.facefill(b, channel), stroke=a.facefill(b*0.4, channel), sw=1.5))
            elif kind == 'cube':
                _, cx, cy, cz, size, rot = spec
                o.append(cube((cx, cy, cz), size, rot, cam, channel))
            elif kind == 'star':
                p = a.P(star, cam)
                if p:
                    o.append('<circle cx="%.1f" cy="%.1f" r="7" fill="%s"/>' % (p[0], p[1], a.facefill(1.0, channel)))
                    o.append('<path d="M%.1f %.1f L%.1f %.1f M%.1f %.1f L%.1f %.1f" stroke="%s" stroke-width="2"/>' % (
                        p[0]-12, p[1], p[0]+12, p[1], p[0], p[1]-12, p[0], p[1]+12, a.facefill(1.0, channel)))
        return "".join(o)
    return a.render(render)


FIGURE_BUILDERS = {
    "ikigai": fig_ikigai,
    "levenswiel": fig_levenswiel,
    "assenstelsel": fig_assenstelsel,
    "trendcanvas": fig_trendcanvas,
    "automaten": fig_automaten,
    "pyramide_c": fig_pyramide_c,
    "prisma": fig_prisma,
}
FIGURE_CAPTIONS = {
    "ikigai": "Ikigai — waar de vier kringjes overlappen, staat het werk dat ik wil.",
    "levenswiel": "Levenswiel (2026-09-04) — eigenaarschap in het midden, acht leefgebieden eromheen.",
    "assenstelsel": "Assenstelsel — mijn signalen op twee assen (concept; assen nog te bevestigen).",
    "trendcanvas": "Trendcanvas — de 8 stappen van trend naar mijn innovatie.",
    "automaten": "Alles-automaten — een kaart met de status van automaten in de buurt.",
    "pyramide_c": "Waardepiramide C — leeg frame, nog te vullen.",
    "prisma": "Vier prisma's — een per gekozen thema, met de vier niveaus als lagen. Sleep om te draaien.",
}

# =================================================================== shell
def sidebar(active_id):
    items = []
    for p in ALL_PAGES:
        cls = "active" if p["id"] == active_id else ""
        items.append(
            f'<a class="snav {cls}" href="{p["page"]}">'
            f'<span class="snum">{p["num"]}</span>{html.escape(p["title"])}</a>'
        )
    return f'''
<aside class="sidebar" id="sidebar">
  <a class="brand" href="index.html">TREND<span class="accent">REIS</span>
    <span class="brand-sub">/ ontdekkingsreis</span></a>
  <nav class="snavs" aria-label="Hoofdnavigatie">{''.join(items)}</nav>
  <div class="sfoot">
    <div class="sfoot-row">
      <button class="btn" id="d3Btn" aria-pressed="true" title="Rood-cyan 3D (alleen de home-scène)"><span class="dot"></span>3D</button>
      <button class="btn" id="themeBtn" title="Thema wisselen">LIGHT</button>
    </div>
    <p class="sfoot-note">rood-cyan brilletjes voor de 3D · zonder bril ook leesbaar</p>
    <p class="sfoot-sig">qwen 3.8 27b · lokaal</p>
  </div>
</aside>
<div class="scrim" id="scrim"></div>
<button class="burger" id="burger" aria-label="Menu"><span></span><span></span><span></span></button>'''


def toc(items):
    if len(items) < 2:
        return ""
    links = "".join(f'<a href="#{h}">{t}</a>' for h, t in items)
    return f'<nav class="toc" aria-label="Op deze pagina"><span class="toc-h">Op deze pagina</span>{links}</nav>'


def anchor_of(title):
    a = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return a


def prev_next(active_id):
    ids = [p["id"] for p in ALL_PAGES]
    i = ids.index(active_id)
    out = '<nav class="pn" aria-label="Vorige en volgende">'
    if i > 0:
        p = ALL_PAGES[i - 1]
        out += f'<a class="pn-a" href="{p["page"]}"><span class="pn-l">← vorige</span><span class="pn-t">{p["num"]} · {html.escape(p["title"])}</span></a>'
    else:
        out += '<span></span>'
    if i < len(ids) - 1:
        p = ALL_PAGES[i + 1]
        out += f'<a class="pn-a next" href="{p["page"]}"><span class="pn-l">volgende →</span><span class="pn-t">{p["num"]} · {html.escape(p["title"])}</span></a>'
    else:
        out += '<span></span>'
    out += "</nav>"
    return out


def render_figure_block(name):
    return (f'<div class="block full figblock">'
            f'<figure class="figwrap">{FIGURE_BUILDERS[name]()}'
            f'<figcaption>{html.escape(FIGURE_CAPTIONS[name])}</figcaption>'
            f'</figure></div>')


def render_hunter_block():
    cards = "".join(
        f'<figure class="phcard"><img src="media/{h[0]}.jpg" alt="{html.escape(h[1])}" loading="lazy">'
        f'<figcaption><strong>{html.escape(h[1])}</strong><span>{html.escape(h[2])}</span></figcaption></figure>'
        for h in HUNTER_PHOTOS
    )
    return (f'<div class="block full photoblock"><div class="phgrid">{cards}</div></div>')


def content_blocks(page_id, md):
    """Bouw de 'blocks' grid voor een content-pagina."""
    md = re.sub(r"^#\s+.*$", "", md, count=1, flags=re.M)  # strip H1
    intro_html, sections = split_sections(md)
    items = []
    if intro_html:
        items.append(("intro", intro_html))
    for (f, b) in FIGURES.get(page_id, []):
        if b == "intro":
            items.append(("fig", f))
    for title, body in sections:
        # figuren vóór deze sectie
        for (f, b) in FIGURES.get(page_id, []):
            if b == title:
                items.append(("fig", f))
        items.append(("sec", title, body))
        # hunter-foto's na de Hunt-sectie (signalen)
        if page_id == "signalen" and title.startswith("Venster 5"):
            items.append(("photos", ""))
    blocks = []
    toc_items = []
    for it in items:
        if it[0] == "intro":
            blocks.append(f'<div class="block full intro">{it[1]}</div>')
        elif it[0] == "fig":
            blocks.append(render_figure_block(it[1]))
        elif it[0] == "photos":
            blocks.append(render_hunter_block())
        else:
            title, body = it[1], it[2]
            a = anchor_of(title)
            toc_items.append((a, title))
            span = span_for(body)
            cls = "sec"
            if re.match(r"Wat dit hoofdstuk toont", title):
                cls += " callout"
            blocks.append(f'<div class="block {cls} {span}" id="{a}"><h2>{inline(title)}</h2>{body}</div>')
    return "".join(blocks), toc_items


# =================================================================== pages
def page_head(title, desc, active_id):
    return f'''<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — TRENDREIS</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="theme.css">
</head>
<body data-page="{active_id}">
{sidebar(active_id)}
<div class="frame">
<main class="main">
<div class="page">
'''


def page_foot():
    return '''</div>
</main>
<footer class="foot"><p class="quote">“Je verkoopt niet de wafel — je verkoopt het gevoel dat iemand jou uit de brand helpt.”</p></footer>
<div class="statusbar">
  <span class="dot"></span><span>TRENDREIS · TK1</span><span class="sig">qwen 3.8 27b · lokaal</span>
  <span class="grow"></span><span>3D: <span id="sb3d">AAN</span></span><span>© 2026 M. van Gulik</span>
</div>
</div>
<div class="lightbox" id="lightbox" hidden>
  <div class="lb-head"><span class="lb-title"></span><button class="lb-close" type="button">✕ sluiten</button></div>
  <div class="lb-stage"><div class="lb-imgwrap"></div></div>
  <div class="lb-foot">klik buiten de foto, of druk ESC, om te sluiten</div>
</div>
<script src="main.js?v=7"></script>
</body>
</html>'''


def build_home():
    p = PAGES[0]
    head = page_head("TRENDREIS — van signaal tot stip op de horizon",
                     "Wat ik de trendweken leerde, en hoe ik die verbind met het bedrijf dat ik wil bouwen.", "home")
    # hero
    hero = f'''
<section class="hero" id="scene">
  <div class="hero-head">
    <h1 class="hero-title">TREND<span class="accent">REIS</span></h1>
    <p class="hero-sub">van signaal tot stip op de horizon</p>
    <p class="hero-meta">Marlo van Gulik · ONDEON18 · Onderneem! De Ontdekkingsreis</p>
    <p class="hero-meta">HAN University of Applied Sciences — oktober 2026</p>
  </div>
  {anaglyph_svg()}
  <div class="hero-controls">
    <span class="hint">rood-cyan brilletjes voor de 3D · zonder bril ook leesbaar</span>
    <span class="spacer"></span>
    <a class="btn primary" href="wie-ben-ik.html">START →</a>
  </div>
</section>
<section class="home-intro">
  <p>Dit is mijn creatieve aflevering van trendopdracht TK1: wat ik heb geleerd, en hoe ik
  de verbinding leg tussen <strong>trends</strong> en <strong>het bedrijf dat ik wil bouwen</strong>.
  Acht stappen, zes vensters, één noorderster — in de stijl van een console, met 3D als handtekening.</p>
</section>
<div class="cards">'''
    for pg in PAGES[1:] + EXTRA_PAGES:
        hero += f'''
  <a class="card" href="{pg["page"]}">
    <span class="card-num">{pg["num"]}</span>
    <span class="card-title">{html.escape(pg["title"])}</span>
    <span class="card-short">{html.escape(pg["short"])}</span>
    <span class="card-go">open →</span>
  </a>'''
    hero += "</div>"
    return head + hero + page_foot()


def build_content_page(p):
    md = (CONTENT / f'{p["file"]}.md').read_text(encoding="utf-8")
    head = page_head(p["title"], p["short"], p["id"])
    ch_head = (f'<div class="ch-head"><span class="ch-id">TR-{p["num"]}</span>'
               f'<h1 class="ch-title">{html.escape(p["title"])}</h1>'
               f'<span class="ch-kicker">{html.escape(p["short"])}</span></div>')
    blocks, toc_items = content_blocks(p["id"], md)
    # colofon: vul de bronnen in
    if p["id"] == "colofon":
        bron = "".join(
            f'<div class="bron"><div class="bron-label">{html.escape(b["label"])}</div>'
            f'<div class="bron-apa">{b["apa"]}</div>'
            f'<div class="bron-used">gebruikt bij: {html.escape(b["used"])}</div></div>'
            for b in BRONNEN
        )
        blocks = blocks.replace("__BRONNEN__", bron)
    right = toc(toc_items)
    return head + ch_head + f'<div class="cols"><div class="blocks">{blocks}</div><aside class="toccol">{right}{prev_next(p["id"])}</aside></div>' + page_foot()


# ---------------------------------------------------------------- ai-chat
def parse_transcript(md):
    lines = md.splitlines()
    exchanges = []
    cur = None
    for ln in lines:
        if ln.startswith("## "):  # prompt
            if cur:
                exchanges.append(cur)
            cur = {"prompt": [], "responses": []}
        elif cur is not None:
            if ln.startswith("### "):
                cur["responses"].append([])
            elif cur["responses"]:
                cur["responses"][-1].append(ln)
            else:
                cur["prompt"].append(ln)
    if cur:
        exchanges.append(cur)
    # drop the top H1 + intro (they land in the first 'prompt' before any ##)
    return exchanges


def build_ai_chat():
    p = [x for x in EXTRA_PAGES if x["id"] == "ai-chat"][0]
    head = page_head(p["title"], "De volledige AI-chat (prompt → reactie), in een console-venster.", "ai-chat")
    ch_head = (f'<div class="ch-head"><span class="ch-id">AI</span>'
               f'<h1 class="ch-title">{html.escape(p["title"])}</h1>'
               f'<span class="ch-kicker">de volledige sessie — lokaal, Qwen 3.8 27B (Ollama)</span></div>')
    md = TRANSCRIPT.read_text(encoding="utf-8")
    exchanges = parse_transcript(md)
    # count
    n_prompts = len(exchanges)
    n_resp = sum(len(e["responses"]) for e in exchanges)
    # drop a stray first exchange that is just the intro (no prompt body & no responses)
    body = []
    for i, e in enumerate(exchanges):
        prompt_md = md_to_html("\n".join(e["prompt"])).strip()
        if not prompt_md and not e["responses"]:
            continue
        first_line = next((l.strip().lstrip("#").strip() for l in e["prompt"] if l.strip()), "prompt")
        first_line = inline(re.sub(r"^#+\s*", "", first_line))[:90]
        resps = ""
        for r in e["responses"]:
            r_html = md_to_html("\n".join(r)).strip()
            if not r_html:
                continue
            resps += f'<details class="chat-r"><summary>🤖 reactie</summary><div class="chat-r-body">{r_html}</div></details>'
        body.append(
            f'<details class="chat-x" {"open" if i == 0 else ""}>'
            f'<summary><span class="px-p">❯</span><span class="px-q">{first_line}{"…" if len(first_line) >= 90 else ""}</span>'
            f'<span class="px-meta">{len(e["responses"])} reacties</span></summary>'
            f'<div class="chat-x-body">{prompt_md}{resps}</div></details>'
        )
    console = f'''
<section class="console">
  <div class="console-bar">
    <span class="console-dots"><i></i><i></i><i></i></span>
    <span class="console-title">trendreis — ai-chat · qwen 3.8 27b · lokaal</span>
    <span class="console-r"><a href="{ROOT.name}/AI-chat/sessie-01a10830.jsonl" target="_blank" rel="noopener">ruwe sessie ↓</a></span>
  </div>
  <div class="console-meta">
    <span>{n_prompts} prompts</span><span>·</span><span>{n_resp} reacties</span><span>·</span>
    <span>elke wisselwerking is inklapbaar — klik op een prompt</span>
  </div>
  <div class="console-body">{''.join(body)}</div>
</section>'''
    right = f'<div class="toc-note"><p>Per de HAN-regels: AI is geen primaire bron. Dit is de volledige, onbewerkte wisselwerking (prompts én reacties) — de bijlage die bij het werk hoort.</p></div>'
    return head + ch_head + f'<div class="cols"><div class="aiwrap">{console}</div><aside class="toccol">{right}{prev_next("ai-chat")}</aside></div>' + page_foot()


# ---------------------------------------------------------------- materiaal
def build_materiaal():
    p = [x for x in EXTRA_PAGES if x["id"] == "materiaal"][0]
    head = page_head(p["title"], "Mijn notebook: de originele foto’s, met de bron-quotes gemarkeerd.", "materiaal")
    ch_head = (f'<div class="ch-head"><span class="ch-id">M</span>'
               f'<h1 class="ch-title">{html.escape(p["title"])}</h1>'
               f'<span class="ch-kicker">de originele foto’s — klik een “↳ schrift”-markering elders op de site</span></div>')
    photos = sorted(RAW.glob("*.jpg"))
    by_photo = {}
    for hid, h in HIGHLIGHTS.items():
        by_photo.setdefault(h["photo"], []).append((hid, h))
    figs = []
    for ph in photos:
        name = ph.stem
        hls = by_photo.get(name, [])
        boxes = "".join(
            f'<div class="hlbox" id="hl-{hid}" data-id="{hid}" title="{html.escape(h["quote"])}" '
            f'style="left:{h["box"][0]}%;top:{h["box"][1]}%;width:{h["box"][2]}%;height:{h["box"][3]}%"></div>'
            for hid, h in hls
        )
        badge = f'<span class="nbbadge">{len(hls)} bron-quote{"s" if len(hls) != 1 else ""}</span>' if hls else ""
        figs.append(
            f'<figure class="nb" id="nb-{name}">'
            f'<div class="nb-img"><img src="media/notebook/{ph.name}" alt="Notebook {html.escape(name)}" loading="lazy">{boxes}</div>'
            f'<figcaption><span class="nb-name">{html.escape(name)}</span>{badge}</figcaption>'
            f'</figure>'
        )
    legend = "".join(
        f'<a class="leg" href="#hl-{hid}" data-hl="{hid}"><span class="leg-dot"></span>'
        f'{html.escape(HIGHLIGHTS[hid]["label"])}<span class="leg-q">“{html.escape(HIGHLIGHTS[hid]["quote"])}”</span></a>'
        for hid in HIGHLIGHTS
    )
    main = f'''
<section class="mat-intro">
  <p>Op de site staat mijn eigen tekst — maar dit is waar het vandaan komt: <strong>mijn notebook</strong>.
  Waar je elders op de site een <a class="bron-chip" href="#legend">↳ schrift</a>-markering ziet, staat hier een
  <strong>oranje rechthoek</strong> rond de exacte zin. Klik een quote onderaan, of een markering elders, dan scroll ik
  naar de foto en licht de rechthoek aan.</p>
</section>
<div class="legend" id="legend"><span class="legend-h">Bron-quotes (klik om naar de foto te gaan)</span>{legend}</div>
<div class="nbs">{''.join(figs)}</div>'''
    right = prev_next("materiaal")
    return head + ch_head + f'<div class="cols"><div class="matwrap">{main}</div><aside class="toccol">{right}</aside></div>' + page_foot()


# =================================================================== build
def copy_media():
    MEDIA.mkdir(parents=True, exist_ok=True)
    NB_DIR.mkdir(parents=True, exist_ok=True)
    n = 0
    for src in sorted(HUNTER.glob("*.jpg")):
        shutil.copy2(src, MEDIA / src.name); n += 1
    for src in sorted(RAW.glob("*.jpg")):
        shutil.copy2(src, NB_DIR / src.name); n += 1
    return n


def build():
    nmedia = copy_media()
    for p in PAGES:
        if p["id"] == "home":
            html_out = build_home()
        else:
            html_out = build_content_page(p)
        (SITE / p["page"]).write_text(html_out, encoding="utf-8")
        print(f"  {p['page']:28} {len(html_out):>7} bytes")
    html_out = build_ai_chat(); (SITE / "ai-chat.html").write_text(html_out, encoding="utf-8")
    print(f"  {'ai-chat.html':28} {len(html_out):>7} bytes")
    html_out = build_materiaal(); (SITE / "materiaal.html").write_text(html_out, encoding="utf-8")
    print(f"  {'materiaal.html':28} {len(html_out):>7} bytes")
    print(f"OK: {len(PAGES)+2} pagina's + {nmedia} foto's → {SITE}")


if __name__ == "__main__":
    build()
