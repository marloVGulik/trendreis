# Trendreis

De creatieve aflevering van trendopdracht **TK1** van de minor **Onderneem! De
Ontdekkingsreis** (ONDEON18) — HAN University of Applied Sciences.

Wat ik de afgelopen weken heb geleerd, en hoe ik de verbinding heb gelegd tussen
**trends** en **het bedrijf dat ik wil bouwen** — als website, met **3D-anaglyph**
als creatieve handtekening.

## Inhoud

| bestand / map | wat |
|---|---|
| `content/` | de tekst van de website, hoofdstuk per hoofdstuk (Nederlands) |
| `raw-data/` | mijn notebook (foto's) + de eruit gehaalde notities |
| `hunter-pics/` | foto's uit de Hunt / stoepwatch |
| `MAPPING.md` | hoe ik mijn notities aan het lesmateriaal heb gekoppeld |
| `PLAN.md` | het plan voor de website |
| `les-2026-10-05.txt` | notities van de les (o.a. de trendcanvas) |
| `scripts/` | het OCR-crop script + de website-builder |
| `site/` | de gebouwde website (HTML/CSS/JS) — de leverbare site |
| `AI-chat/` | de AI-chat (prompts + output), per HAN-richtlijn als bijlage |
| `TODO.md` | de takenlijst (voor mij + voor de AI) |

## De website

Statische site (HTML/CSS/JS, geen backend), in de "orange console"-stijl —
donker + oranje, mono-typografie, hoek-markeringen. De bron is de tekst in
`content/`; de build zet die om naar `site/index.html`.

**Bouwen** (na het aanpassen van de tekst in `content/`):
```bash
python3 scripts/build_site.py
```

**Lokaal bekijken:**
```bash
cd site && python3 -m http.server 8199
# → http://localhost:8199
```

Interactie: **3D** aan/uit, **diepte-schuif**, en **LIGHT/DARK**-thema (al
lokaal onthouden, geen server nodig).

## 3D

De site is ontworpen voor **rood-cyan 3D-brillen**: de teksten blijven plat
leesbaar, de scènes komen naar je toe. De 3D is een anaglyph (rood + cyan
kanaal met diepte-afhankelijke verschuiving) — de diepte is instelbaar via de
schuif. *(Zonder bril is alles ook in 2D te lezen: zet 3D op UIT.)*

## AI-gebruik

Per de HAN-regels voor verantwoord AI-gebruik: **alles is gedaan met Qwen3.8 27B,
lokaal op mijn eigen computer** — behalve het direct verwerken van de notebook-foto's
naar tekst (OCR), dat is een aparte stap. De volledige AI-chat (prompts én output)
staat in `AI-chat/` als bijlage.

## Privacy

De notebook-foto's zijn opgenomen als authentiek materiaal. Sommige persoonlijke
notities zijn bewust weggelaten uit de tekst; die staan uitsluitend nog op de foto's.

---

*Marlo van Gulik — HAN · Embedded Systems Engineering · ONDEON18*
