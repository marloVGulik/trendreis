#!/usr/bin/env python3
"""Vernieuwt tabblad 'Trends' in trendlijst.ods + corrigeert tabblad 1.

Correcties op basis van Marlo's readings (2026-10-09):
  Wortelstoffen -> Grondstoffen (foutje in vertaling)
  Aibaarheidsfactor -> Aaibaarheidsfactor (hoe graag mensen iets willen aanraken; husky = hoog, naakte kat = laag)
  Transhumanisatie = cybernetics, robotonderdelen die mensen helpen
  Digireligie = geloven in het algoritme + AI-verwarrendheid, mensen kunnen er niet mee omgaan
  Globalisering = globalisering; slobalisation = het langzamer worden ervan
  Infobubbel/infobesitas = mensen krijgen alleen info binnen hun bubbel, manipulatie door algoritmes
  Cryptokoorts = overdreven neiging om in Bitcoin te investeren
  Exclusief -> inclusief = software: iedereen kan apps/websites bouwen zonder programmeerkennis
  Digital ID = digitaal bijhouden wie wat doet en waar iemand aanmeldt; kan toegang ontzeggen bij fouten
  Cobot/hubot = robot naast mensen, mag niet meer door regelgeving
  Agentic commerce = marketing, zoals betalen om bij Google bovenaan te komen
  Platform switch = zelf bouwen, verschuiving van grote bedrijven naar eigen specifieke tools

Groepen: alles eerst in bestaande groepen, lege groepen weg (Werk & leren), nieuwe alleen waar nodig.
"""
import re, html, zipfile, os

BASE = "/home/marlo/Documents/School/minor/trendreis"
ODS = os.path.join(BASE, "trendlijst.ods")

HEAD1 = ["Trend", "Waar ik de trend vandaan heb", "Trend thema", "Trend DESTEP thema",
         "Doorgaan? (ja/nee)", "Waarom doorgaan?"]

HEAD = ["Trend", "Van -> naar",
        "Producttrend (micro 0-1)", "Markttrend (midi 1-5)",
        "Consumententrend (maxi 5-15)", "Maatschappelijke trend (mega 15-50)",
        "Signalen", "Welke signalen", "DESTEP",
        "Behoefte", "Opkomende verwachting", "A/B/C/D", "Doorgaan? (ja/nee)", "Waarom?"]

WIDTHS = ["40mm", "40mm", "34mm", "34mm", "34mm", "34mm", "12mm", "55mm", "20mm",
          "34mm", "34mm", "14mm", "16mm", "34mm"]

# correcties op tabblad 1: naam -> (nieuwe naam, nieuw thema)
FIX = {
    "Wortelstoffen / vleesproxy": ("Grondstoffen", "Duurzaamheid & klimaat"),
    "Aibaarheidsfactor": ("Aaibaarheidsfactor", "Consumptie & retail"),
    "Sustainable relations": ("Sustainable relations", "Software & platforms"),
    "Exclusief → inclusief": ("Exclusief → inclusief", "Software & platforms"),
    "Body mining / brein download": ("Body mining / brein download", "Gezondheid & food"),
}
# extra rij: vleesproxy apart, omdat het geen food is
EXTRA = [("Vleesproxy", "E(econ) + T", "AI & data", "Ja",
          "persoon zonder kritisch denkvermogen die herhaalt wat AI zegt")]

# (trend, van->naar, product, markt, consument, maatschappelijk, destep, [signalen])
TRENDS = [
    ("Automatisering van de keuze", "van menselijke beslissing naar machine-beslissing",
     "LLM's die producten verkopen (agentic commerce)",
     "advisering en verkoop worden door agents gedaan, niet door mensen",
     "verwacht dat een machine de keuze voor hem maakt en ontlast",
     "een wereld waarin beslissingen delegabel zijn aan algoritmen",
     "T + E(econ)",
     ["Agentic commerce — LLM's verkopen producten aan mensen",
      "OpenAI doet bod op Medal: trainingsdata → real-world keuzes voor automatisering",
      "'Slimme' maatschappij: alles meten, algoritmes, dataverzameling, geïnformeerde keuzes",
      "AI eats doctor"]),
    ("Data als grondstof", "van data als bijproduct naar data als bezit en grondstof",
     "dataplatformen, sensoren, chips",
     "data wordt gekocht en verkocht als grondstof; bedrijven concurreren op data",
     "verwacht gratis tools in ruil voor zijn data",
     "een wereld waarin persoonlijke data het kapitaal is",
     "E(econ) + T",
     ["Data = nieuw goed / nieuwe olie", "Chips = nieuwe olie"]),
    ("Informatie wordt bubbel", "van open informatie naar bubbel",
     "algoritmes die filteren wat je ziet",
     "aanbod wordt gestuurd, niet gekozen",
     "krijgt alleen info binnen zijn bubbel en ziet de rest niet",
     "een wereld waarin manipulatie via algoritmes normaal is",
     "T + S",
     ["Infobubbel / infobesitas"]),
    ("Te veel info", "van meer naar minder verwerken",
     "filter- en contentdieet-tools",
     "aanbod groeit sneller dan verwerking",
     "kiest bewust minder input",
     "een wereld waarin aandacht de schaarse grondstof is",
     "T + S",
     ["Datadieet"]),
    ("Zonder eigen denkvermogen", "van eigen oordeel naar herhalen wat AI zegt",
     "AI-assistenten die antwoorden geven",
     "mensen volgen het antwoord zonder te controleren",
     "verwacht dat het algoritme gelijk heeft en kan er niet mee omgaan",
     "een wereld met een nieuwe, niet-religieuze religie",
     "S + T",
     ["Digireligie", "Vleesproxy"]),
    ("Gegenereerd in plaats van gemaakt", "van maken naar genereren",
     "Claude, AI-posters, electrische reclameborden",
     "genereren vervangt met de hand maken",
     "wil gemakkelijk visuelen maken",
     "een wereld waarin AI flink aan het groeien is",
     "T",
     ["AI-gegenereerde posters en plaatjes voor bedrijven"]),
    ("Digitalisering als koepel", "van analoog naar digitaal",
     "digitale producten en apparaten",
     "alles wordt digitaal en technologisch",
     "verwacht dat alles online en meetbaar is",
     "een volledig digitaliseerde samenleving",
     "T",
     ["Digitalisering", "Technologisering"]),
    ("Van bezit naar toegang", "van bezitten naar cloud en toegang",
     "cloudabonnementen, bucloud",
     "toegang wordt het product in plaats van bezit",
     "verwacht toegang zonder te bezitten",
     "een wereld waarin 1% bezit heeft en de rest toegang",
     "T + E(econ)",
     ["Cloud living / cloud worker / cloud economie / buycloud",
      "1% bezit vs 50% — Oxfam Novib, 42 mensen = 3,7 miljard"]),
    ("Van meetbaar naar merkbaar", "van meten naar merken",
     "belevingsproducten en tastbare materialen",
     "waarde wordt bepaald door beleving, niet door cijfers",
     "verwacht dat iets voelbaar meer waard is",
     "een wereld waarin perceptie de maat is",
     "E(econ) + S",
     ["Van meetbaar naar merkbaar", "Aaibaarheidsfactor"]),
    ("Klein wint van groot", "van groot bedrijf naar kleine startup met een idee",
     "kleine tools van kleine startups",
     "kleine tech-startups met een goed idee worden populair",
     "verwacht dat een klein bedrijf het beter kan dan een groot",
     "een wereld waarin groot niet automatisch beter is",
     "E(econ) + T",
     ["Kleine tech-startups met een goed idee zijn populair", "Innovatieladder"]),
    ("Nieuwe geldvormen", "van traditioneel geld naar nieuwe geldvormen",
     "crypto, bitcoin, alternatieve betaalmiddelen",
     "geldstromen lopen via marktplaatsen en superstar firms",
     "verwacht dat geld niet van een bank hoeft te komen",
     "een wereld met verdeelde, niet-centrale waarde",
     "E(econ)",
     ["Cryptokoorts", "Donuteconomie / new economy / new money",
      "Investeren in bitcoin / superstar firms / marktplaatsen met datastromen"]),
    ("Tekort als motor", "van overvloed naar tekort",
     "reststromen, grondstoffen, tweedehands",
     "tekort (woning, grondstof) bepaalt prijs en aanbod",
     "verwacht schaarsheid en past zijn gedrag aan",
     "een tekorteconomie",
     "E(econ) + E(ecol) + D",
     ["Grondstoffen", "Grondstoftekort / tekorteconomie", "Woningtekort"]),
    ("Globalisering en slobalisation", "van lokaal naar wereldwijd — en nu weer langzamer",
     "wereldwijd leverbare producten",
     "markten zijn wereldwijd verbonden, maar vertragen",
     "verwacht wereldwijde beschikbaarheid",
     "een wereld die als één systeem functioneert",
     "E(econ) + S",
     ["Globalisering / slobalisation"]),
    ("Van vertrouwen in het systeem naar wantrouwen", "van vertrouwen naar wantrouwen",
     "keurmerken en verificatie-tools",
     "claims en greenwashing worden betwist",
     "verwacht dat claims niet kloppen",
     "een samenleving met systeemmoe en angstgeneratie",
     "S + P",
     ["Trust / angstgeneratie / systeemmoe", "Greenwashing"]),
    ("Van vertrouwen in big tech naar eigen controle", "van vertrouwen in een partij naar eigen controle",
     "lokale AI, self-hosted systemen, eigen servers",
     "bedrijven willen niet permanent afhankelijk zijn van AI-bedrijven",
     "verwacht dat zijn data lokaal en onder eigen beheer blijft",
     "een wereld waarin soevereiniteit een waarde is",
     "P + T",
     ["Bedrijven zijn angstig om grote AI-bedrijven permanent te vertrouwen",
      "Cyber / cybersecurity", "Zorgvelden die gehackt worden"]),
    ("Massacontrole via registratie", "van vertrouwen naar registratie",
     "digital ID-systemen",
     "registratie bepaalt wie wat mag",
     "verwacht dat toegang wordt ontzegd bij een fout",
     "een wereld waarin wie waar aanmeldt wordt bijgehouden",
     "P + T",
     ["Digital id", "Controle door rijken, big tech die misbruik maakt"]),
    ("Regel als barrière voor automatisering", "van automatiseren naar niet-automatiseren door regels",
     "cobots en hubots die niet naast mensen mogen werken",
     "automatisering stopt bij de regels",
     "verwacht dat bepaalde sectoren handmatig blijven",
     "een wereld waarin regelgeving de tech remt",
     "P + T",
     ["Regelfetjisisme", "Automatisering kan niet vanwege regels (sector die automatisering mist)",
      "Cobot / hubot"]),
    ("Duurzaamheid wordt efficiëntie en instoot", "van ideaal naar efficiëntie",
     "micro-fabrieken, solar democracy, CO2-zuigen",
     "duurzaamheid wordt een efficiëntieargument",
     "verwacht dat duurzaam ook efficiënter is",
     "een wereld die teruginput in plaats van uitstoot",
     "E(ecol) + E(econ) + P",
     ["Duurzaam = efficiënt (mijn definitie)", "Uitstoot → instoot",
      "Biobased bouwen / solar democracy / CO2 zuigen / micro-fabriek / wat is afval"]),
    ("Klimaat als conditie", "van zorg naar gegeven",
     "hittestress-bestendige bouw en koeling",
     "klimaat wordt randvoorwaarde en kostenpost",
     "verwacht warmte en restricties",
     "een wereld met hitterecords en een transitie",
     "E(ecol) + S + P",
     ["Opwarming / hitterecord / klimaattransition", "Hittestress"]),
    ("Van menselijke bediening naar automatische uitvoering", "van bedienden naar automatisch draaien",
     "automaten, grasmaaiers, dark factories",
     "uitvoering gebeurt zonder mens",
     "verwacht dat dingen automatisch draaien",
     "een wereld waarin werken wordt overgenomen",
     "T",
     ["Automaten (suikerspinmachines, blikautomaten, snackmuren)",
      "Dark factories / fabrieken op zee / indoor farming",
      "Op-afstand-bestuurde grasmaaier van de gemeente"]),
    ("Van kopen naar zelf maken", "van kopen naar lokaal zelf maken",
     "3D-printers, op maat gemaakte spullen",
     "zelf maken concurrert met kopen",
     "verwacht dat hij zelf kan maken ('dat kan ik thuis ook')",
     "een wereld van prosumers",
     "S + T",
     ["3D-printer op de markt", "'Dat kan ik thuis ook' — zelf maken i.p.v. kopen",
      "Op maat gemaakte spullen"]),
    ("Slimme apparatuur wordt standaard in de openbare ruimte", "van bord naar slimme apparatuur",
     "kentekenherkenning, electrische reclameborden",
     "de openbare ruimte wordt apparatuur",
     "verwacht registratie en slimme infrastructuur",
     "een wereld die continu registreert",
     "T",
     ["Electrische reclameborden", "Kentekenherkenning in parkeergarages — slimme apparatuur wordt standaard"]),
    ("Kopen wordt spel", "van kopen naar spelen",
     "labubu, squishies, verrassingspakketten",
     "gamification en gokken, gericht op kinderen",
     "verwacht vermaak bij het kopen",
     "een wereld waarin consumptie spel is",
     "T + S",
     ["Gameficering / gamyshopping",
      "Gemaskert gokken met 'rare' producten (labubu, squishies), gericht op kinderen",
      "Verloren pakketjes kopen per gewicht"]),
    ("Van behandelen naar optimaliseren", "van genezen naar optimaliseren",
     "DNA-assessment, health-tech, slaap-tools, robotonderdelen",
     "gezondheid wordt optimalisatie",
     "verwacht dat hij beter kan presteren",
     "een wereld van transhumanisatie",
     "T + E(econ)",
     ["Smartheal / elite health / health-tech / DNA assessment",
      "Slaaplessen / slaaptekort / beter slapen", "Transhumanisatie",
      "Body mining / brein download", "Ecologische eugenetica"]),
    ("Van gezond naar obsessief", "van gezond naar obsessief",
     "tracking-apps en dieet-cultuur",
     "gezondheid wordt obsessie",
     "verwacht controle over lichaam en voetafdruk",
     "een wereld van ecorexia",
     "S + E(ecol)",
     ["Ecorexia / orthorexia / ecotexia"]),
    ("Leven wordt ontworpen", "van gegeven naar ontworpen",
     "kunsteileider op een chip, CRISPR, babyfabriek",
     "biotech wordt een keuze",
     "verwacht dat leven aanpasbaar is",
     "een wereld van ontworpen levens",
     "D + T",
     ["CRISPR babies / geboren in babyfabriek",
      "Kunsteileider op een chip / uitstervende dieren redden"]),
    ("Wonen wordt slim, klein en stedelijk", "van groot en vast naar slim, klein en stedelijk",
     "smart living-systemen, huizen verkopen met VR",
     "woning wordt slim en compact",
     "verwacht een klein, slim huis in de stad",
     "een wereld van bubble living en verstedelijking",
     "T + S + D",
     ["Smart living", "Bubble living", "Huizen verkopen met VR-brillen",
      "Verstedelijking / cityliving"]),
    ("Leefruimte wordt groter dan de aarde", "van aarde naar ruimte",
     "space farm, airfarm, ruimte-toerisme",
     "ruimte wordt economisch interessant",
     "verwacht dat leefruimte niet aardgebonden is",
     "een wereld met een gedeelde toekomst op andere planeten",
     "T + E(econ)",
     ["Ruimte toerisme / space living / space farm / airfarm",
      "Gedeelde toekomst / water op andere planeten"]),
    ("Van menselijk contact naar machinecontact", "van mens naar machine",
     "robot huisdier, datingapps",
     "machine vervangt contact",
     "verwacht contact van een machine",
     "een wereld waarin relaties hybride zijn",
     "T + S",
     ["Robot huisdier / robot love", "Datingtech / trashdating / oude mensen op datingsites"]),
    ("Van verbinding naar eenzaamheid", "van verbinding naar eenzaamheid",
     "apps die eenzaamheid moeten oplossen",
     "eenzaamheid wordt een markt",
     "verwacht verbinding maar krijgt een scherm",
     "een eenzaamheidspandemie",
     "D + S",
     ["Eenzaamheidspandemie", "FOMO / JOMO"]),
    ("Software als relatie", "van product naar platform voor relaties",
     "LinkedIn, Instagram",
     "software bepaalt hoe mensen omgaan",
     "verwacht relaties via software",
     "een wereld waarin contact via platforms loopt",
     "T + S",
     ["Sustainable relations"]),
    ("Software wordt voor iedereen bouwbaar", "van exclusief naar inclusief",
     "Claude, site-builders, weekend-tools",
     "van grote bedrijven die software leveren naar mensen die zelf bouwen",
     "verwacht dat hij zonder programmeerkennis iets kan bouwen",
     "een wereld waarin iedereen kan bouwen",
     "T + S",
     ["Exclusief → inclusief", "Iedereen wil een site en denkt dat het met Claude kan",
      "Platform switch: Playstore & telefoons → nu AI",
      "Disposable software: kleine tools in een weekend bouwen"]),
    ("Van ik naar wij", "van ik naar wij",
     "gedeelde producten, do-it-together",
     "inclusie wordt verkoopargument",
     "verwacht erbij horen",
     "een wereld van wij",
     "S",
     ["Wij = nieuwe ik / do-it-together"]),
    ("Levensloop wordt langer en in fases", "van levensloop naar fases",
     "producten voor 100+",
     "multi stage life wordt een segment",
     "verwacht werken tot zijn 100ste",
     "een wereld met fases in plaats van één levensloop",
     "D + S",
     ["100+ / multi stage life / werken tot je 100ste"]),
    ("Gemak als norm", "van inspanning naar gemak",
     "apps, bezorging, de korte weg",
     "gemak wordt standaard",
     "verwacht de kortste route",
     "een gemaksmaatschappij",
     "S + E(econ)",
     ["Gemaksmaatschappij: korte weg, comfort, etes online, daten op apps", "Simplificering"]),
    ("Polarisering", "van midden naar extremen",
     "niche-producten per groep",
     "het midden verdwijnt",
     "verwacht een keuze per kamp",
     "een gepolariseerde samenleving",
     "S + P",
     ["Polarisering"]),
    ("Stijl als statement", "van functioneel naar statement",
     "statement-fashion, e-Mustang",
     "stijl wordt statement",
     "verwacht uitdrukking via uiterlijk",
     "een wereld van symbolen",
     "S + T",
     ["Fashion als statement / 'vreemde' fashion",
      "Autnostalgie — modellen worden teruggebracht (e-Mustang)"]),
    ("Technologie als machtsmiddel", "van commercieel naar geopolitiek machtsmiddel",
     "drones en defensie-tech",
     "kleine startups in defensie worden populair",
     "verwacht dat tech geopolitiek is",
     "een wereld waarin tech macht is",
     "P + T",
     ["AI war / tech power"]),
    ("Treintrots", "van auto naar trein",
     "treintickets en treinabonnementen",
     "trein wint van auto",
     "verwacht trein boven auto",
     "een wereld die voor openbaar vervoer kiest",
     "S + E(ecol)",
     ["Treintrots"]),
]

LEGEND = [
    "Signaal = een gebeurtenis ('dit bestaat'). Trend = een richting ('van A naar B').",
    "Definitie uit de deck: een trend is een richting waarin waarden en behoeften veranderen, opgestuwd door externe krachten, en manifesteert zich door gedrag, producten en diensten.",
    "Testen bij omvormen: (1) richting? (2) externe DESTEP-kracht eronder? (3) >=2 signalen in dezelfde richting? (4) manifesteert het zich in gedrag/product/dienst? (5) niveau + horizon?",
    "Vier niveaus per trend: producttrend micro 0-1 (welke producten zijn populair) · markttrend midi 1-5 (wat gebeurt er in de markt) · consumententrend maxi 5-15 (hoe gedragen consumenten zich, wat verwacht de consument) · maatschappelijke trend mega 15-50 (in wat voor wereld leven we).",
    "Voorbeeld 'van gemaakt naar gegenereerd': product = Claude · markt = genereren i.p.v. met de hand maken · consument = wil gemakkelijk visuelen maken · maatschappelijk = een wereld waarin AI groeit.",
    "A/B/C/D uit de trechter: A interesseveld · B doelgroep · C vakgebied · D toekomst.",
    "Behoefte en Opkomende verwachting vul je zelf in — dat is hoofdstuk #3.",
    "Correcties: Wortelstoffen -> Grondstoffen (vertalingfout); Aibaarheidsfactor -> Aaibaarheidsfactor (hoe graag mensen iets willen aanraken, husky = hoog, naakte kat = laag); vleesproxy = persoon zonder kritisch denkvermogen die herhaalt wat AI zegt; kunsteileider = product dat vrouwen met een eileiderprobleem helpt; transhumanisatie = cybernetics; sustainable relations = software als LinkedIn/Instagram; slobalisation = vertraging van globalisering; Werk & leren is leeg en dus weg.",
    "Alles is in de bestaande groepen gezet; alleen 'Software als relatie' is een nieuwe groep omdat er geen bestaande groep paste.",
]


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))


def cells_in(row):
    return [html.unescape(m.group(1) or "") for m in
            re.finditer(r"<table:table-cell[^>]*>(?:<text:p>(.*?)</text:p>)?", row)]


def table_xml(name, header, rows, widths=None):
    out = [f'<table:table table:name="{esc(name)}">']
    if widths:
        out.append("<table:table-columns>")
        for w in widths:
            out.append(f'<table:table-column fo:width="{w}" fo:width-guess="true"/>')
        out.append("</table:table-columns>")
    out.append("<table:table-row>")
    for h in header:
        out.append(f'<table:table-cell office:value-type="string"><text:p>{esc(h)}</text:p></table:table-cell>')
    out.append("</table:table-row>")
    for r in rows:
        out.append("<table:table-row>")
        for v in r:
            out.append(f'<table:table-cell office:value-type="string"><text:p>{esc(v)}</text:p></table:table-cell>')
        out.append("</table:table-row>")
    out.append("</table:table>")
    return "".join(out)


def main():
    z = zipfile.ZipFile(ODS)
    content = z.read("content.xml").decode("utf-8")
    names = z.namelist()
    items = [(n, z.read(n)) for n in names]
    z.close()

    content = re.sub(r'<table:table table:name="Trends">.*?</table:table>', "", content)
    content = re.sub(r'<table:table table:name="Legend">.*?</table:table>', "", content)

    # tabblad 1: correcties + vleesproxy als aparte rij
    tabs = re.findall(r'(<table:table table:name="[^"]+"[^>]*>)(.*?)</table:table>', content)
    first_open, first_body = tabs[0]
    first_name = re.search(r'table:name="([^"]+)"', first_open).group(1)
    rows = [cells_in(r) for r in re.findall(r"<table:table-row[^>]*>.*?</table:table-row>", first_body)]
    header, data = rows[0], rows[1:]
    data = [r for r in data if len(r) >= 6 and r[0]]
    changed = []
    for r in data:
        if r[0] in FIX:
            new_name, new_theme = FIX[r[0]]
            changed.append(f"{r[0]}  ->  {new_name}  [{new_theme}]")
            r[0], r[2] = new_name, new_theme
    for name, destep, theme, ja, why in EXTRA:
        data.append([name, "woordopdracht in de les", theme, destep, ja, why])
        changed.append(f"+ {name}  [{theme}]")
    print("correcties tabblad 1:")
    for c in changed:
        print("  " + c)

    new1 = table_xml(first_name, HEAD1, data, ["50mm", "48mm", "32mm", "24mm", "20mm", "60mm"])

    # controle dekking
    used = {}
    for t in TRENDS:
        for s in t[7]:
            used[s] = used.get(s, 0) + 1
    have = {r[0] for r in data if r[4].strip().lower() == "ja"}
    missing = have - set(used)
    extra = set(used) - have
    dup = {k: v for k, v in used.items() if v > 1}
    print(f"\ntrends: {len(TRENDS)} · signalen: {len(used)} van {len(have)}")
    if missing:
        print("NIET TOEGEWEZELD:", *sorted(missing), sep="\n  ")
    if extra:
        print("NIET IN TAB 1:", *sorted(extra), sep="\n  ")
    if dup:
        print("DUBEL:", dup)

    out_rows = [[t[0], t[1], t[2], t[3], t[4], t[5], str(len(t[7])), "; ".join(t[7]),
                 t[6], "", "", "", "", ""] for t in TRENDS]
    new2 = table_xml("Trends", HEAD, out_rows, WIDTHS)
    new3 = table_xml("Legend", ["Toelichting"], [[l] for l in LEGEND])

    content = content.replace(first_open + first_body + "</table:table>", new1)
    content = content.replace("<table:named-expressions/>", new2 + new3 + "<table:named-expressions/>")

    with zipfile.ZipFile(ODS, "w") as out:
        out.writestr(zipfile.ZipInfo("mimetype"), "application/vnd.oasis.opendocument.spreadsheet",
                     compress_type=zipfile.ZIP_STORED)
        for n, b in items:
            if n == "mimetype":
                continue
            if n == "content.xml":
                b = content.encode("utf-8")
            out.writestr(n, b)
    print("\ntabbladen vernieuwd in", ODS)


if __name__ == "__main__":
    main()
