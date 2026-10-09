#!/usr/bin/env python3
# Genereert trendlijst.ods (LibreOffice Calc) uit de trends in notebook + Eva's presentaties.
# Kolommen: Trend | Waar ik de trend vandaan heb | Trend thema | Trend DESTEP thema | Doorgaan? (ja/nee)
# "Doorgaan?" laten we leeg — Marlo vult zelf in.
#
# Bronnen zijn herleidbaar: notebook-pagina (P00-01 … P18-19), online-notes, les-PDF's,
# Tegenlicht, scanplan/podcast, hunt-foto's, klasgenoot, gastles, oud-reizigers.

import csv, os, subprocess, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_ODS = os.path.join(BASE, "trendlijst.ods")
OUT_CSV = os.path.join(BASE, "trendlijst.csv")

HEAD = ["Trend", "Waar ik de trend vandaan heb", "Trend thema", "Trend DESTEP thema", "Doorgaan? (ja/nee)"]

# (trend, bron, thema, destep)
ROWS = [
    # ---- MARLO ZELF: stoepwatch / scan / online-notes ----
    ("Automaten (suikerspinmachines, blikautomaten, snackmuren)", "stoepwatch + scan — online-notes / P16-17", "automatisering & robots", "T"),
    ("3D-printer op de markt", "stoepwatch — online-notes", "automatisering & robots", "T"),
    ("Op-afstand-bestuurde grasmaaier van de gemeente", "stoepwatch — online-notes", "automatisering & robots", "T + P"),
    ("Electrische reclameborden", "stoepwatch — online-notes", "aandacht & AI", "T + S"),
    ("AI-gegenereerde posters en plaatjes voor bedrijven", "stoepwatch — online-notes", "AI & data", "T"),
    ("AI-gegenereerde 'kunst' verkopen", "stoepwatch — online-notes", "AI & data", "T + S"),
    ("Iedereen wil een site en denkt dat het met Claude kan", "stoepwatch — online-notes", "software & platforms", "T + S"),
    ("Disposable software: kleine tools in een weekend bouwen", "scanplan maandag — podcast", "software & platforms", "T + E(econ)",
    ),
    ("Agentic commerce — LLM's verkopen producten aan mensen", "online-notes", "AI & data", "T + E(econ)"),
    ("Platform switch: Playstore & telefoons → nu AI", "online-notes", "software & platforms", "T + P"),
    ("Volledig advies- & maakbureau voor printplaten", "online-notes", "automatisering & robots", "T"),
    ("OpenAI koopt Medal: trainingsdata → real-world keuzes voor automatisering", "online-notes", "AI & data", "T + E(econ)"),
    ("Memoires: data over hoe mensen AI gebruiken en wat ze op willen slaan", "online-notes", "AI & data", "T + S"),
    ("Kentekenherkenning in parkeergarages — slimme apparatuur wordt standaard", "hunt-foto", "automatisering & robots", "T"),
    ("Zonnepaneel-schoonmaakborstels", "stoepwatch — online-notes", "duurzaamheid & efficiëntie", "E(ecol) + T"),
    ("Plastic rietjes: mensen willen geen vieze papieren rietjes", "stoepwatch — online-notes", "consumptie & afval", "S + E(ecol)"),
    ("Verloren pakketjes kopen per gewicht", "les 2026-10-05", "consumptie & afval", "S + E(econ)"),
    ("Gemaskert gokken met 'rare' producten (labubu, squishies), gericht op kinderen", "les 2026-10-05", "consumptie & aandacht", "S + E(econ)"),
    ("Popup store", "stoepwatch — online-notes", "consumptie & retail", "S + E(econ)"),
    ("Ouderen die alleen eten", "stoepwatch — online-notes", "eenzaamheid & aandacht", "D + S"),
    ("Driewieler / toegankelijke fiets voor ouderen", "stoepwatch — online-notes", "mobiliteit & toegankelijkheid", "D + T"),
    ("Geavanceerde / gescandeerde bakfiets", "stoepwatch + hunt-foto", "mobiliteit", "D + T + E(ecol)"),
    ("Grote SUV-auto's (SUV-ificatie)", "hunt-foto", "mobiliteit", "S + E(econ)"),
    ("Autnostalgie — modellen worden teruggebracht (e-Mustang)", "hunt-foto", "identiteit & fashion", "S + T"),
    ("Oortjes in tijdens gesprekken", "stoepwatch — online-notes", "eenzaamheid & aandacht", "S"),
    ("Dure lunchtent in de natuur waar geen jongeren zitten", "stoepwatch — online-notes", "eenzaamheid & retail", "S + D"),
    ("Kleurloze kinderspeelhoek zonder kinderen", "stoepwatch — online-notes", "eenzaamheid & aandacht", "S + D"),
    ("Asociaal fatbike-rijden (mensen natspuiten)", "stoepwatch — online-notes", "mobiliteit & gedrag", "S"),
    ("Een enkeling die een mondkapje draagt", "stoepwatch — online-notes", "gezondheid & lichaam", "S + P"),
    ("Fashion als statement / 'vreemde' fashion", "stoepwatch — online-notes", "identiteit & fashion", "S"),
    ("'Dat kan ik thuis ook' — zelf maken i.p.v. kopen", "notebook P16-17", "consumptie & DIY", "S + T"),
    ("Op maat gemaakte spullen", "notebook P16-17", "consumptie & retail", "T + E(econ)"),
    ("Gemaksmaatschappij: korte weg, comfort, etes online, daten op apps", "notebook P08-09", "makkelijk & toegankelijk", "S + E(econ)"),
    ("'Slimme' maatschappij: alles meten, algoritmes, dataverzameling, geïnformeerde keuzes", "notebook P08-09", "AI & data", "T + S"),
    ("Infobubbel / infobesitas", "notebook P08-09 + Eva", "aandacht & AI", "T + S"),
    ("Data = nieuw goed / nieuwe olie", "notebook P16-17", "AI & data", "E(econ) + T"),
    ("Chips = nieuwe olie", "notebook P18-19", "AI & data", "T + P"),
    ("Duurzaam = efficiënt (mijn definitie)", "notebook P18-19", "duurzaamheid & efficiëntie", "E(ecol) + E(econ)"),
    ("Food: van 70% van het salaris naar 10%", "notebook P18-19", "food & lichaam", "E(econ) + S"),
    ("Automatisering kan niet vanwege regels (sector die automatisering mist)", "Tegenlicht — Game of drones", "automatisering & robots", "P + T"),
    ("Kleine tech-startups met een goed idee zijn populair", "Tegenlicht — Game of drones", "geld & ondernemen", "E(econ) + T"),
    ("Robot huisdier / robot love", "notebook P04-05 + Eva", "eenzaamheid & AI", "T + S"),
    ("Aibaarheidsfactor", "woordopdracht in de les", "geld & economie", "E(econ)"),
    ("Leefloon", "woordopdracht in de les", "geld & samenleving", "E(econ) + S"),
    ("Verkoop niet de wafel, maar het gevoel dat iemand je uit de brand helpt", "klasgenoot (quote)", "aandacht & retail", "S"),

    # ---- EVA: FutureFit / trendwoorden / trendkaart ----
    ("Van consumer naar playsumer", "Eva — FutureFit résumé", "consumptie & retail", "S"),
    ("Van meetbaar naar merkbaar", "Eva — FutureFit résumé", "geld & economie", "E(econ) + S"),
    ("Van bezit naar bereik (abonnement)", "Eva — FutureFit résumé", "consumptie & retail", "S + E(econ)"),
    ("Van indoor naar outdoor", "Eva — FutureFit résumé", "ruimte & living", "S + E(ecol)"),
    ("Mono → holo", "Eva — FutureFit résumé", "samenleving", "S"),
    ("On → off", "Eva — FutureFit résumé", "energie & tech", "T"),
    ("Uitstoot → instoot", "Eva — FutureFit résumé", "energie & klimaat", "E(ecol) + P"),
    ("Exclusief → inclusief", "Eva — FutureFit résumé", "samenleving", "S"),
    ("#metoo → #wetoo", "Eva — FutureFit résumé", "samenleving", "S"),
    ("Wij = nieuwe ik / do-it-together", "Eva — FutureFit résumé", "samenleving", "S"),
    ("Sustainable relations", "Eva — FutureFit résumé", "duurzaamheid & efficiëntie", "E(ecol) + S"),
    ("Phygital", "Eva — FutureFit résumé", "software & platforms", "T + S"),
    ("Cobot / hubot", "Eva — FutureFit résumé", "automatisering & robots", "T"),
    ("Cloud living / cloud worker / cloud economie / buycloud", "Eva — FutureFit résumé", "ruimte & economie", "T + E(econ)"),
    ("Smart living", "Eva — FutureFit résumé", "ruimte & living", "T + S"),
    ("Smart education / social learning / on-life-leren / ethical educators", "Eva — FutureFit résumé", "werk & leren", "T + S"),
    ("Huidhonger", "Eva — FutureFit résumé", "gezondheid & lichaam", "S"),
    ("Bewegingsarmoede / tech-fit / DIY-sport", "Eva — FutureFit résumé", "gezondheid & lichaam", "S + D"),
    ("Eenzaamheidspandemie", "Eva — FutureFit résumé", "eenzaamheid & aandacht", "D + S"),
    ("Screenliving / beeldschermtrui", "Eva — FutureFit résumé", "software & platforms", "T + S"),
    ("Digireligie", "Eva — FutureFit résumé", "AI & samenleving", "S + T"),
    ("Innovatieladder", "Eva — FutureFit résumé", "geld & economie", "E(econ)"),
    ("Warmtekamers", "Eva — FutureFit résumé", "energie & klimaat", "E(ecol) + T"),
    ("Wortelstoffen / vleesproxy", "Eva — FutureFit résumé", "food & lichaam", "T + S"),
    ("Smartheal / elite health / health-tech / DNA assessment", "Eva — FutureFit résumé", "gezondheid & tech", "T + E(econ)"),
    ("Virtividu", "Eva — FutureFit résumé", "software & platforms", "T + S"),
    ("Datingtech / trashdating / oude mensen op datingsites", "Eva — FutureFit résumé", "eenzaamheid & aandacht", "D + S"),
    ("Body mining / brein download", "Eva — FutureFit résumé", "AI & lichaam", "T + S"),
    ("Avatar docent", "Eva — FutureFit résumé", "werk & leren", "T + S"),
    ("Transhumanisatie", "Eva — FutureFit résumé", "lichaam & tech", "T + S"),
    ("Mannenval", "Eva — FutureFit résumé", "samenleving", "S + D"),
    ("Slaaplessen / slaaptekort / beter slapen", "Eva — FutureFit résumé + P12-13", "gezondheid & lichaam", "S"),
    ("Toetsgeneratie", "Eva — FutureFit résumé", "werk & leren", "S"),
    ("Regelfetjisisme", "Eva — FutureFit résumé", "vertrouwen & soevereiniteit", "P + S"),
    ("Pritection", "Eva — FutureFit résumé", "geld & tech", "E(econ) + T"),
    ("FOMO / JOMO", "Eva — FutureFit résumé", "eenzaamheid & aandacht", "S"),
    ("Mensenzieb / aandachts­economisering", "Eva — FutureFit résumé", "aandacht & economie", "S + E(econ)"),
    ("Datadieet", "Eva — FutureFit résumé", "AI & data", "S + T"),
    ("Bubble living", "Eva — FutureFit résumé", "ruimte & living", "S"),
    ("Indoor generatie", "Eva — FutureFit résumé", "ruimte & living", "D + S"),
    ("Cactusgesprek / schootel", "Eva — FutureFit résumé", "eenzaamheid & aandacht", "S"),
    ("Gameficering / gamyshopping", "Eva — FutureFit + trendwoorden", "consumptie & tech", "T + S"),
    ("Dreamotion (langzamer leven, nieuwe dromen)", "Eva — trendwoorden", "makkelijk & samenleving", "S"),
    ("Bosapotheek (natur, kruiden als medicijn)", "Eva — trendwoorden", "gezondheid & ecologie", "E(ecol) + S"),
    ("Woestijnspijt", "Eva — trendwoorden", "energie & klimaat", "E(ecol) + S"),
    ("Hamsterschaamte", "Eva — trendwoorden", "consumptie & afval", "S"),
    ("Cryptokoorts", "Eva — trendwoorden", "geld & economie", "E(econ) + T"),
    ("Netflixisering", "Eva — trendwoorden", "software & platforms", "T + S"),
    ("Treintrots", "Eva — trendwoorden", "mobiliteit & samenleving", "S + E(ecol)"),
    ("Ecorexia / orthorexia / ecotexia", "Eva — trendwoorden", "gezondheid & ecologie", "S + E(ecol)"),
    ("Genderless / gender bender / genderkinderen", "Eva — trendkaart", "samenleving", "S"),
    ("100+ / multi stage life / werken tot je 100ste", "Eva — trendkaart", "demografie", "D + S"),
    ("Donuteconomie / new economy / new money", "Eva — trendkaart", "geld & economie", "E(econ)"),
    ("Gedeelde toekomst / water op andere planeten", "Eva — trendkaart", "energie & ruimte", "E(ecol) + T"),
    ("1% bezit vs 50% — Oxfam Novib, 42 mensen = 3,7 miljard", "Eva — trendkaart", "ongelijkheid & economie", "E(econ) + S"),
    ("Investeren in bitcoin / superstar firms / marktplaatsen met datastromen", "Eva — trendkaart", "geld & tech", "E(econ) + T"),
    ("CRISPR babies / geboren in babyfabriek", "Eva — trendkaart", "demografie & tech", "D + T"),
    ("Ecologische eugenetica", "Eva — trendkaart", "gezondheid & ecologie", "S + E(ecol)"),
    ("Deelfietsbedrijven / samenwerken", "Eva — trendkaart", "mobiliteit & economie", "E(econ) + T"),
    ("Huizen verkopen met VR-brillen", "Eva — trendkaart", "ruimte & tech", "T + E(econ)"),
    ("Kunsteileider op een chip / uitstervende dieren redden", "Eva — trendkaart", "gezondheid & ecologie", "T + E(ecol)"),
    ("Greenwashing", "Eva — FutureFit (prof woorden)", "vertrouwen & soevereiniteit", "S + P"),
    ("AI eats doctor", "Eva — FutureFit (prof woorden)", "AI & gezondheid", "T + S"),
    ("Controle door rijken, big tech die misbruik maakt", "Eva — FutureFit (thema's)", "vertrouwen & soevereiniteit", "P + E(econ)"),
    ("Zorgvelden die gehackt worden", "notebook P16-17", "vertrouwen & soevereiniteit", "P + T"),
    ("Digital id", "Eva — FutureFit (people woorden)", "vertrouwen & tech", "T + P"),
    ("Cyber / cybersecurity", "Eva — FutureFit (people woorden)", "vertrouwen & tech", "T + P"),
    ("Opwarming / hitterecord / klimaattransition", "Eva — FutureFit + P18-19", "energie & klimaat", "E(ecol) + P"),
    ("Hittestress", "Eva — FutureFit", "energie & klimaat", "E(ecol) + S"),
    ("Woningtekort", "Eva — FutureFit + P18-19", "ruimte & economie", "D + E(econ)"),
    ("Grondstoftekort / tekorteconomie", "Eva — FutureFit + P18-19", "economie & ecologie", "E(econ) + E(ecol)"),
    ("Dementie / vergrijzing", "Eva — FutureFit + megatrends", "demografie", "D"),
    ("Individualisering", "Eva — megatrendlijst", "samenleving", "S + D"),
    ("Globalisering / slobalisation", "Eva — megatrendlijst", "economie & samenleving", "E(econ) + S"),
    ("Digitalisering", "Eva — megatrendlijst", "AI & data", "T"),
    ("Technologisering", "Eva — megatrendlijst", "AI & tech", "T"),
    ("Simplificering", "Eva — megatrendlijst", "makkelijk & toegankelijk", "S"),
    ("Spiritualisering", "Eva — megatrendlijst", "samenleving", "S"),
    ("Verstedelijking / cityliving", "Eva — megatrendlijst", "ruimte & living", "D + S"),
    ("Polarisering", "Eva — megatrendlijst", "samenleving", "S + P"),
    ("Betekenisconomisering", "Eva — megatrendlijst", "economie & samenleving", "E(econ) + S"),
    ("Ruimte toerisme / space living / space farm / airfarm", "Eva — FutureFit + P18-19", "ruimte & tech", "T + E(econ)"),
    ("Dark factories / fabrieken op zee / indoor farming", "Eva — FutureFit (Spacemakers)", "automatisering & robots", "T + E(ecol)"),
    ("Biobased bouwen / solar democracy / CO2 zuigen / micro-fabriek / wat is afval", "Eva — FutureFit (Schoonmakers)", "duurzaamheid & efficiëntie", "E(ecol) + T"),
    ("AI war / tech power", "Eva — FutureFit (planet woorden)", "vertrouwen & politiek", "P + T"),
    ("Trust / angstgeneratie / systeemmoe", "Eva — FutureFit + P12-13", "vertrouwen & samenleving", "S + P"),
    ("Bedrijven zijn angstig om grote AI-bedrijven permanent te vertrouwen", "Boris (oud-reiziger) — P06-07", "vertrouwen & soevereiniteit", "P + S"),
    ("Meervoudige waardecreatie — meerdere problemen in één oplossing, trends combineren", "gastles Bart Krinner", "methodiek / waardecreatie", "E(econ) + S"),
    ("Massa = kassa; branding en marketing belangrijker dan smaak", "gastles Bart Krinner", "consumptie & branding", "S + E(econ)"),
]

# Hoofdthema's (voor clustering in hoofdstuk #2) — de ruwe thema's worden hieronder
# naar deze 14 hoofdthema's normaliseerd.
CANON = {
    "AI & data": "AI & data",
    "aandacht & AI": "AI & data",
    "AI & samenleving": "AI & data",
    "AI & lichaam": "AI & data",
    "AI & tech": "AI & data",
    "AI & gezondheid": "AI & data",
    "automatisering & robots": "Automatisering & robots",
    "software & platforms": "Software & platforms",
    "vertrouwen & soevereiniteit": "Vertrouwen & soevereiniteit",
    "vertrouwen & tech": "Vertrouwen & soevereiniteit",
    "vertrouwen & politiek": "Vertrouwen & soevereiniteit",
    "vertrouwen & samenleving": "Vertrouwen & soevereiniteit",
    "eenzaamheid & aandacht": "Eenzaamheid & aandacht",
    "eenzaamheid & retail": "Eenzaamheid & aandacht",
    "eenzaamheid & AI": "Eenzaamheid & aandacht",
    "aandacht & economie": "Eenzaamheid & aandacht",
    "aandacht & retail": "Eenzaamheid & aandacht",
    "gezondheid & lichaam": "Gezondheid & food",
    "gezondheid & tech": "Gezondheid & food",
    "gezondheid & ecologie": "Gezondheid & food",
    "lichaam & tech": "Gezondheid & food",
    "food & lichaam": "Gezondheid & food",
    "duurzaamheid & efficiëntie": "Duurzaamheid & klimaat",
    "energie & klimaat": "Duurzaamheid & klimaat",
    "energie & tech": "Duurzaamheid & klimaat",
    "energie & ruimte": "Duurzaamheid & klimaat",
    "economische ecologie": "Duurzaamheid & klimaat",
    "economie & ecologie": "Duurzaamheid & klimaat",
    "consumptie & retail": "Consumptie & retail",
    "consumptie & afval": "Consumptie & retail",
    "consumptie & DIY": "Consumptie & retail",
    "consumptie & tech": "Consumptie & retail",
    "consumptie & branding": "Consumptie & retail",
    "consumptie & aandacht": "Consumptie & retail",
    "geld & economie": "Geld & economie",
    "geld & tech": "Geld & economie",
    "geld & samenleving": "Geld & economie",
    "geld & ondernemen": "Geld & economie",
    "ongelijkheid & economie": "Geld & economie",
    "economie & samenleving": "Geld & economie",
    "ruimte & economie": "Geld & economie",
    "samenleving": "Samenleving & demografie",
    "demografie": "Samenleving & demografie",
    "demografie & tech": "Samenleving & demografie",
    "identiteit & fashion": "Samenleving & demografie",
    "makkelijk & samenleving": "Samenleving & demografie",
    "makkelijk & toegankelijk": "Samenleving & demografie",
    "ruimte & living": "Ruimte & living",
    "ruimte & tech": "Ruimte & living",
    "mobiliteit": "Mobiliteit",
    "mobiliteit & toegankelijkheid": "Mobiliteit",
    "mobiliteit & gedrag": "Mobiliteit",
    "mobiliteit & samenleving": "Mobiliteit",
    "mobiliteit & economie": "Mobiliteit",
    "werk & leren": "Werk & leren",
    "methodiek / waardecreatie": "Methodiek",
}

LEGEND = [
    "DESTEP: D = demografie · E(econ) = economie · S = sociologie · T = techniek · E(ecol) = ecologie · P = politiek",
    "Kolom 'Doorgaan?' vul je zelf in met ja/nee.",
    "Trend thema = 14 hoofdthema's (clustering voor hoofdstuk #2).",
]


def set_widths(path):
    """Leesbare kolom-breedtes (CSV→ODS geeft standaardbreedtes)."""
    import zipfile, re, os
    z = zipfile.ZipFile(path)
    xml = z.read("content.xml").decode("utf-8")
    widths = ["50mm", "48mm", "32mm", "24mm", "20mm"]
    new = "".join(f'<table:table-column table:column-width="{w}"/>' for w in widths)
    xml2 = re.sub(r"(?:<table:table-column [^>]*/>){5}", new, xml, count=1)
    names = z.namelist()
    tmp = path + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
        # ODF-eis: 'mimetype' moet als eerste entry en uncompressed staan
        for n in names:
            data = xml2.encode("utf-8") if n == "content.xml" else z.read(n)
            if n == "mimetype":
                out.writestr(zipfile.ZipInfo("mimetype"), data, compress_type=zipfile.ZIP_STORED)
            else:
                out.writestr(n, data)
    z.close()
    os.replace(tmp, path)


def main():
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEAD)
        for r in ROWS:
            theme = CANON.get(r[2], r[2])
            w.writerow([r[0], r[1], theme, r[3], ""])
        w.writerow([])
        for line in LEGEND:
            w.writerow([line])

    print(f"CSV: {OUT_CSV}  ({len(ROWS)} trends)")

    try:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "ods", "--outdir", BASE, OUT_CSV],
            check=True, capture_output=True, timeout=120,
        )
        print(f"ODS: {OUT_ODS}")
        set_widths(OUT_ODS)
    except Exception as e:
        print("soffice-conversie mislukt:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
