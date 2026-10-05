# PLAN — 3D (anaglyph) op zo veel mogelijk plekken

**Doel:** 3D is de handtekening van deze site. Nu staat het alleen op de home-scène.
Dit plan maakt 3D **herbruikbaar** en voegt het toe op **zoveel mogelijk plekken** —
zodat de hele "trendreis" met rood-cyan brilletjes te "ervaren" is.

**Gouden regels (blijven):**
- Tekst blijft **altijd plat/2D** en leesbaar zónder bril. Alleen *scenes/figuren/graphics* krijgen diepte.
- Rood-cyan anaglyph: één scène, twee kanalen (rood + cyaan) met een kleine offset per dieptelaag.
- **Diepte-schuif** (bestaand) + **3D aan/uit** (bestaand) besturen alles centraal.
- Zonder bril = nette 2D-wireframe (fallback), dus de site is nooit "kapot".
- Stijl: orange console (donker/oranje, wireframe, harde lijnen, geen glass/gradients).

---

## Fase 0 — de 3D-motor (basis, 1x bouwen)

Alles hangt hieraan. Nu is de anaglyph-logica hard-gekoppeld aan de home-scène.
We maken er een **herbruikbare functie** van.

1. **`anaglyph(scene, opts)`** — neemt een SVG-scène (met lagen) en renderert automatisch
   `#chR` + `#chC` met parallax per laag. Elke figuur/scene kan hiermee 3D worden.
2. **Lagen-annotatie**: elke 3D-scène labelt zijn elementen met `.layer-0 … .layer-4`
   (of `data-depth="0.2|0.5|1.0"`). De motor leest `data-depth` en past de offset toe.
   → geen aparte `far/mid/near`-CSS meer nodig per scène.
3. **Centrale 3D-state**: één toggle (sidebar) + één diepte-waarde sturen **alle** 3D-scènes tegelijk.
   Nu alleen de hero; daarna elke `.anaglyph` op de pagina.
4. **Optioneel: muis-parallax** — kleine extra offset die volgt op de muis (subtiel, ±2px),
   naast de diepte-schuif. Geept "levend" gevoel. (Aan/uit via dezelfde 3D-toggle.)
5. **`prefers-reduced-motion`** respecteren (parallax uit, static offset).

> Na Fase 0 is "3D toevoegen op een nieuwe plek" = een SVG met `data-depth`-lagen + 1 regel `anaglyph()`.

---

## Fase 1 — de figuren in 3D (hoogste impact, on-brand)

Elke bestaande figuur wordt een 3D-wireframe. Dit is het meest zichtbare winst.

| Figuur | 3D-interpretatie | Dieptelagen (achter→voor) |
|---|---|---|
| **Ikigai** | 4 doorzichtige 3D-schijven/ringen die elkaars ruimte delen; overlap-zone "ikigai" zweeft voorop | achtergrond-ring → 3 overlappende ringen → centrale stip |
| **Levenswiel** | 3D-radar: aslijn loopt de ruimte in, score-polygoon zweeft op diepte | cirkel-grat (achter) → aslijnen → score-polygoon (voor) |
| **Assenstelsel** | al bijna 3D: x/y-assen + **z-as = tijd/trend**; een stip die langs de z-as "vooruit" beweegt | vlak (achter) → assen → trend-stip + pijl (voor) |
| **Trendcanvas** | 8 celletjes als 3D-paneel dat in de ruimte zweeft, licht gekanteld; elke cel op eigen diepte | paneel-achtergrond → cel-rijen (3 dieptes) → "mijn innovatie" cel (voor) |
| **Alles-automaten** | 3D-stratenplan/kaart: automaten als 3D-blokjes op een vlak, status-puntjes zweven | straten (achter) → automaat-blokjes → status/stars (voor) |
| **Pyramide-C** | natuurlijke **3D-piramide**: 4 lagen als diepteniveaus, wireframe, leeg (nog te vullen) | basis-laag (voor) … top-laag (achter) of omgekeerd |

> Elke figuur krijgt **diepte-schuif + 3D aan/uit** mee (via Fase 0). Zonder bril = nette 2D.

---

## Fase 2 — het verhaal in 3D (structuur & narrative)

6. **De reis (ch.6)** — de home-scène (pad + poorten + ster) wordt een **volledige 3D-reisscène**:
   één pad dat alle 8 hoofdstukken doorloopt, elk hoofdstuk = een poort, eindpunt = noorderster.
   Dit wordt hét 3D-bewijsstuk van de "trendreis".
7. **Hoofdstuk-poorten** — boven elke content-pagina een kleine 3D-poort/motief (uit de reisscène),
   zodat je bij elke stap "door een poort" loopt.
8. **Signalen-vensters (ch.2)** — de 6 vensters als **3D-portalen/kader** die je "in kijkt";
   elk venster op een eigen diepte → je kijkt letterlijk door vensters op de reis.
9. **Noorderster-motief** — een klein 3D-ster/compas-icoontje als herhalend 3D-element
   (sidebar, sectiekoppen, einde-afleveringen) → herkenbaar 3D-handtekening overal.
10. **Cover/home** — hero-scène (bestaand) + optionele subtiele **3D-sterrenveld** op de achtergrond
    (diepte = verschillende sterrenlagen), heel rustig.

---

## Fase 3 — verrassing & data in 3D

11. **Signalen-chips (ch.2)** — de belangrijkste signalen als **3D zwevende chips/tags**
    op verschillende dieptes (zoals "kaartjes in de ruimte").
12. **70% → 10% (ch.4)** — de voedsel-verschuiving als **3D-balk/donut** die van 70 naar 10 "inkruipt"
    (diepte = tijd); visueel sterk voor L3.
13. **Waardepyramides A + B (ch.4)** — zodra je die invult: **3D-piramides** (als Pyramide-C).
14. **Bron-quote foto's** — de notebook-foto's als **3D "polaroid"-kaartjes** die in de ruimte zweven
    (diepte per foto) op de materiaal-pagina, naast de platte grid.
15. **Hover-3D** — figuren/karten "lijden" met een subtiele 3D-parallax bij hover (extra diepte-gevoel).
16. **3D-intro (optioneel, impact)** — korte anaglyph-intro-animatie bij het laden van de home
    (sterren + pad dat zich ontvouwt), met direct "overslaan"-optie. (Alleen als het sneller en netter kan.)

---

## Prioriteit & volgorde

- **Fase 0 (motor)** — voorrang; zonder dit valt alles teruggooid. *(doe eerst, direct na content-review)*
- **Fase 1 (figuren)** — grootste zichtbare winst, 6 figuren. *(direct na Fase 0)*
- **Fase 2 (verhaal)** — reisscène + poorten + vensters + noorderster. *(na Fase 1)*
- **Fase 3 (verrassing)** — chips, 70→10, pyramides A/B, foto-3D, hover, intro. *(als er ruimte is)*

**Suggestie:** Fase 0 + 1 direct (figuren zijn al getekend → snel 3D-baar),
Fase 2 na content-review, Fase 3 als bonus.

---

## Techniek (hoe)

- **Brillen-mapping (belangrijk)**: Marlo's bril is **links = cyaan, rechts = rood** (omgekeerd van
  de standaard). Dus het **cyaan-kanal naar rechts** = "uit het scherm" (pop-out). De offset-richting
  in de code (cyaan +x) klopt hierop — niet omdraaien tenzij de bril anders is.
- **Anaglyph**: elke scène = 1 SVG, twee groepen `#chR` (rood) + `#chC` (cyaan).
  Per laag offset = `diepte × factor` (near grootste, far kleinste) → near komt voor, far zinkt weg.
- **Kleurmix (de fix)**: `#chC { mix-blend-mode: screen; }` op een **donkere viewport** (`#050505`).
  Additief: rood=rood, cyaan=cyaan, overlap= wit. Zonder dit (mix-blend normal) schilderde cyaan
  over rood → "alleen cyaan". Rood `#ff1010`, cyaan `#00e5e5`.
- **Diepte-schuif**: 0–24px (default 8px), schaalt alle laag-offsets.
- **Muis-parallax**: `mousemove` moduleert de diepte met ~±3px ("om je heen kijken"), lineair + transition.
- **3D off**: `#chC` verbergen + `#chR` naar lichtgrijs → nette 2D-wireframe.
- **Prestatie**: alles SVG + CSS-transform (GPU), geen canvas/WebGL. Licht en snel.
- **Toegankelijkheid**: 3D is altijd optioneel; tekst blijft 2D en leesbaar zónder bril.

---

## Keuzes (vastgelegd door Marlo, 2026-10-05)
1. **Muis-parallax: AAN** (subtiel, past in de stijl) — *geïmplementeerd*.
2. **Intro-animatie: geen 3D-intro** (niet 3D maken).
3. **Pyramides A + B: leeg laten** (Marlo bedenkt nog content) — alleen C als leeg raamwerk.
4. **Hoe "druk"**: mag **uit het scherm** springen — pagina mag druk zijn.
5. **3D standaard: AAN** (lezer schakelt zelf uit).
6. **Anaglyph-fix**: kleurmix (screen) + donkere viewport + richting volgens bril-mapping — *gedaan*.
7. **Extra**: 3D-fringe op diepte-elementen (actieve nav, 3D-toggle, START-knop) — *gedaan*.
