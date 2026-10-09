# WERKWIJZE.md — hoe de data tot stand is gekomen en waar hij later voor gebruikt wordt

Basis voor de content van de site. Dit document is de brug tussen de Excel en de hoofdstukken.

## De twee tabbladen in `trendlijst.ods`

### Tabblad 1 — `trendlijst` (signaleringen)
130 rijen · 84 ja / 46 nee.

| kolom | wat erin staat |
|---|---|
| Trend | het signaal zelf (een gebeurtenis, "dit bestaat") |
| Waar ik de trend vandaan heb | de locatie/bron — dit is de context die de les vraagt |
| Trend thema | één van de 13 groepen (Werk & leren is leeg en dus weg) |
| Trend DESTEP thema | de externe kracht |
| Doorgaan? (ja/nee) | mijn oordeel per signaal |
| Waarom doorgaan? | mijn reden per signaal |

**Gebruik in de site:** hoofdstuk #1 (signaallijst) en #3 (DESTEP + behoeften).

### Tabblad 2 — `Trends` (39 trends)
Een trend is een richting ("van A naar B"), niet een gebeurtenis. 84 ja-signalen → 39 trends. Elke signaal staat exact één keer.

| kolom | wat erin staat |
|---|---|
| Trend | de naam = de richting, nooit een product of merk |
| Van → naar | de richting in één zin |
| Producttrend (micro 0-1) | welke producten zijn populair |
| Markttrend (midi 1-5) | wat gebeurt er in de markt |
| Consumententrend (maxi 5-15) | hoe gedraagt de consument zich, wat wilt/verwacht deze |
| Maatschappelijke trend (mega 15-50) | in wat voor wereld leven we |
| Signalen | hoeveel signalen eronder vallen |
| Welke signalen | de exacte signalen uit tabblad 1 |
| DESTEP | de kracht |
| Locatie/context | dezelfde bron als in tabblad 1 |
| Behoefte | wat mensen nodig hebben |
| Opkomende verwachting | wat ze gaan verwachten |
| A/B/C/D | de reden om de trend verder te verkennen |
| Doorgaan? | **automatisch**: ja als er een letter staat, nee als die leeg is |
| Waarom? | de reden — zowel om mee te nemen als om te laten vallen |

**Gebruik in de site:** hoofdstuk #2 (trends), #3 (behoeften), #4 (pyramides), #5 (waarden).

## De 5 testen bij signaal → trend

1. **Richting** — formuleerbaar als "van … naar …"? Zo nee: blijft signaal.
2. **Externe kracht** — welke DESTEP-kracht duwt eronder? Zo nee: mode of moment.
3. **Meerdere signalen** — één signaal is anekdote, ≥2 nodig.
4. **Manifestatie** — verandert het gedrag, producten of diensten? Zo nee: alleen waardeverschuiving.
5. **Niveau** — niet één niveau kiezen, maar de trend op alle vier niveaus lezen.

Stand: **28 trends** slagen test 3, **11 trends** hebben 1 signaal en zijn anekdote. Later filteren.

## A/B/C/D — de reden om verder te verkennen

Letterlijk uit Week 2 Dag 1: *"mogelijk kom je tot de ontdekking dat je er daarvan 20 interessant vindt om verder te verkennen omdat je…"*

- **A.** nog totaal géén bedrijfsidee, maar hier kansen in ziet
- **B.** ze sluiten aan bij je bedrijfsidee
- **C.** ze sluiten aan bij je ikigai
- **D.** je ze meeneemt om out of the box te kijken
- **E.** …（leeg in de deck)

Stand: **31 trends meegenomen** — D 13 · B 11 · C 7 · **A 0**. A wordt niet gebruikt omdat er al een bedrijfsidee is. Dat is zelf een bevinding voor de site.

**8 trends laten vallen:** Nieuwe geldvormen · Massacontrole via registratie · Van gezond naar obsessief · Leven wordt ontworpen · Wonen wordt slim, klein en stedelijk · Van ik naar wij · Levensloop wordt langer en in fases · Polarisering.

Spanning voor de site: deze 8 hebben wél ja-signalen in tabblad 1 — *signaal ja, trend niet meegenomen*.

## Correcties die zijn doorgevoerd

| correction | reden |
|---|---|
| Wortelstoffen → **Grondstoffen** | foutje in een vertaling |
| Aibaarheidsfactor → **Aaibaarheidsfactor** | hoe graag mensen iets willen aanraken (husky = hoog, naakte kat = laag) |
| **Vleesproxy** apart | persoon zonder kritisch denkvermogen die herhaalt wat AI zegt — geen food |
| **Kunsteileider op een chip** | product dat vrouwen met een eugenetisch eileiderprobleem helpt kinderen te krijgen |
| **Transhumanisatie** | cybernetics, robotonderdelen die mensen helpen |
| **Digireligie** | geloven in het algoritme + AI-verwarrendheid, mensen kunnen er niet mee omgaan |
| **Slobalisation** | het langzamer worden van globalisering |
| **Infobubbel / infobesitas** | mensen krijgen alleen info binnen hun bubbel — manipulatie door algoritmes |
| **Cryptokoorts** | overdreven neiging om in Bitcoin te investeren |
| **Exclusief → inclusief** | software: iedereen kan apps en websites bouwen zonder programmeerkennis |
| **Digital ID** | digitaal bijhouden wie wat doet en waar iemand aanmeldt; kan toegang ontzeggen bij een fout |
| **Cobot / hubot** | robot die naast mensen mag werken, maar niet meer mag door regelgeving |
| **Agentic commerce** | marketing — betalen om bovenaan te komen, zoals bij Google |
| **Platform switch** | zelf bouwen; verschuiving van grote bedrijven naar eigen specifieke tools |

Groepen: alles in de bestaande groepen gezegd, lege groep **Werk & leren** weg, alleen **Software als relatie** als nieuwe trend.

## Horizon

De deck is inconsistent (maxi 5-15 vs 5-10, mega 15-50 vs 10-15). Dit is een **richtlijn, geen regel** en mag genegeerd worden. Beter is om te kijken naar **hoe lokaal iets verandert** — AI is nieuw, maar is op deze manier al wereldwijd geadopteerd.

## Script

`scripts/make_trendstab.py` — idempotent. Draai hem opnieuw na wijzigingen:
- verwijdert en bouwt het `Trends`- en `Legend`-tabblad
- behoudt Marlo's invulling (A/B/C/D + Waarom) uit het bestaande Trends-tabblad
- corrigeert tabblad 1 en voegt Vleesproxy toe als aparte rij
- controleert of alle 84 ja-signalen gedekt zijn
- leidt `Doorgaan?` af uit de letter

Let op bij `.ods`: `mimetype` moet de eerste, uncompressed zip-entry zijn, en `content.xml` moet expliciet teruggeschreven worden.

## Wat er nog open is

- 11 trends met 1 signaal — later filteren
- 4 thema's voor de pyramides in #4.1, en die pyramides als 3D-prisma
- de 3D-scène van de trechter zelf
- #3 behoeften uitwerken per trend
- #5 waarden en verschuivingen
- #6 kansrijke opties (1–3 ideeën)
- meer links naar materiaal, later
