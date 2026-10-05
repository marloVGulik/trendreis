# AI-chat — bijlage (HAN-richtlijn)

Per de HAN-richtlijn "Verantwoord AI" is dit de **volledige AI-chat** (prompts én
output) die is gebruikt voor dit project, als bijlage.

## Inhoud
| Bestand | Wat |
|---|---|
| `transcript.md` | Leesbaar transcript: elke prompt (je), elke reactie (AI), en het toolgebruik. |
| `sessie-01a10830.jsonl` | De volledige, ruwe sessie (JSONL) — het complete record. |

## Hoe deze chat tot stand is gekomen
- **Model:** `ollama/qwen3.8-27b` — lokaal op Marlo's eigen computer (geen cloud).
- **Werkvorm:** Marlo stuurde prompt + instructies; de AI las de notities
  (`raw-data/`), maakte een plan (`PLAN.md`), een koppeling (`MAPPING.md`), en
  schreef de hoofdstukken (`content/`). Marlo beoordeelde en gaf feedback per
  ronde; de AI paste het aan.
- **Wat níet door de AI is gedaan:** het oorspronkelijk verwerken van de
  notebook-foto's naar tekst (dat is handmatig/via een aparte OCR-stap, zie
  `raw-data/extracted.txt`).

## Privacy
- De persoonlijke A/B/C/D "supportnet"-notities (met namen van mensen) staan
  **bewust níet** in de site of de tekst. In dit transcript zijn die namen
  geredacteerd tot `[·]`; de context (dat er een supportnet was en dat het om
  privacy-reasons is weggelaten) blijft leesbaar.
- De notebook-foto's (`raw-data/*.jpg`) blijven wél staan — daarin zijn de
  originele handschrift-notities te zien.

## Transcript opnieuw genereren
```bash
python3 scripts/export_chat.py <sessie.jsonl> AI-chat/transcript.md
```
