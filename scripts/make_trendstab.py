#!/usr/bin/env python3
"""Voegt tabblad 'Trends' toe aan trendlijst.ods.

Signaal -> trend: een signaal is een gebeurtenis (je kunt zeggen 'dit bestaat').
Een trend is een richting (je kunt zeggen 'van A naar B'). Meerdere signalen in
dezelfde richting vormen samen één trend.

Kolommen: Trend · Van -> naar · Niveau · Signalen · Welke signalen · DESTEP ·
Behoefte · Opkomende verwachting · A/B/C/D · Doorgaan? · Waarom?
"""
import re, html, zipfile, shutil, os

BASE = "/home/marlo/Documents/School/minor/trendreis"
ODS = os.path.join(BASE, "trendlijst.ods")

HEAD = ["Trend", "Van -> naar", "Niveau", "Signalen", "Welke signalen", "DESTEP",
        "Behoefte", "Opkomende verwachting", "A/B/C/D", "Doorgaan? (ja/nee)", "Waarom?"]

# trend, van->naar, niveau, DESTEP, [signalen uit tabblad 1]
TRENDS = [
    ("Automatisering van de keuze", "van menselijke beslissing naar machine-beslissing", "midi -> maxi", "T + E(econ)",
     ["Agentic commerce — LLM's verkopen producten aan mensen",
      "OpenAI doet bod op Medal: trainingsdata → real-world keuzes voor automatisering",
      "'Slimme' maatschappij: alles meten, algoritmes, dataverzameling, geïnformeerde keuzes",
      "AI eats doctor"]),
    ("Data als grondstof", "van data als bijproduct naar data als bezit en grondstof", "maxi", "E(econ) + T",
     ["Data = nieuw goed / nieuwe olie", "Chips = nieuwe olie", "Body mining / brein download"]),
    ("Aanbod groter dan verwerkingscapaciteit", "van meer info naar minder info verwerken", "midi", "T + S",
     ["Infobubbel / infobesitas", "Datadieet"]),
    ("Gegenereerd in plaats van gemaakt", "van maken naar genereren", "micro -> midi", "T",
     ["AI-gegenereerde posters en plaatjes voor bedrijven",
      "Iedereen wil een site en denkt dat het met Claude kan"]),
    ("Geloven in het algoritme", "van eigen oordeel naar algoritme-oordeel", "maxi", "S + T",
     ["Digireligie"]),
    ("Digitalisering als koepel", "van analoog naar digitaal", "mega", "T",
     ["Digitalisering", "Technologisering"]),
    ("Van bezit naar toegang", "van bezitten naar cloud en toegang", "maxi", "T + E(econ)",
     ["Cloud living / cloud worker / cloud economie / buycloud",
      "1% bezit vs 50% — Oxfam Novib, 42 mensen = 3,7 miljard"]),
    ("Van meetbaar naar merkbaar", "van meten naar merken", "maxi", "E(econ) + S",
     ["Van meetbaar naar merkbaar", "Aibaarheidsfactor"]),
    ("Klein wint van groot", "van groot bedrijf naar kleine startup met een idee", "midi", "E(econ) + T",
     ["Kleine tech-startups met een goed idee zijn populair", "Innovatieladder"]),
    ("Nieuwe geldvormen", "van traditioneel geld naar nieuwe geldvormen", "midi", "E(econ)",
     ["Cryptokoorts", "Donuteconomie / new economy / new money",
      "Investeren in bitcoin / superstar firms / marktplaatsen met datastromen"]),
    ("Tekort als motor", "van overvloed naar tekort", "maxi", "E(econ) + E(ecol) + D",
     ["Woningtekort", "Grondstoftekort / tekorteconomie"]),
    ("Globalisering", "van lokaal naar wereldwijd", "mega", "E(econ) + S",
     ["Globalisering / slobalisation"]),
    ("Van vertrouwen in het systeem naar wantrouwen", "van vertrouwen naar wantrouwen", "maxi", "S + P",
     ["Trust / angstgeneratie / systeemmoe", "Greenwashing",
      "Controle door rijken, big tech die misbruik maakt"]),
    ("Van vertrouwen in big tech naar eigen controle", "van vertrouwen in een partij naar eigen controle", "midi -> maxi", "P + T",
     ["Bedrijven zijn angstig om grote AI-bedrijven permanent te vertrouwen",
      "Digital id", "Cyber / cybersecurity", "Zorgvelden die gehackt worden"]),
    ("Regel als barrière voor automatisering", "van automatiseren naar niet-automatiseren door regels", "maxi", "P + T",
     ["Regelfetjisisme", "Automatisering kan niet vanwege regels (sector die automatisering mist)"]),
    ("Duurzaamheid wordt efficiëntie en instoot", "van ideaal naar efficiëntie", "midi -> maxi", "E(ecol) + E(econ) + P",
     ["Duurzaam = efficiënt (mijn definitie)", "Uitstoot → instoot",
      "Biobased bouwen / solar democracy / CO2 zuigen / micro-fabriek / wat is afval"]),
    ("Klimaat als conditie", "van zorg naar gegeven", "mega", "E(ecol) + S + P",
     ["Opwarming / hitterecord / klimaattransition", "Hittestress", "Sustainable relations"]),
    ("Van menselijke bediening naar automatische uitvoering", "van bedienden naar automatisch draaien", "midi", "T",
     ["Automaten (suikerspinmachines, blikautomaten, snackmuren)", "Cobot / hubot",
      "Dark factories / fabrieken op zee / indoor farming",
      "Op-afstand-bestuurde grasmaaier van de gemeente"]),
    ("Van kopen naar zelf maken", "van kopen naar lokaal zelf maken", "midi", "S + T",
     ["3D-printer op de markt", "'Dat kan ik thuis ook' — zelf maken i.p.v. kopen",
      "Op maat gemaakte spullen"]),
    ("Slimme apparatuur wordt standaard in de openbare ruimte", "van bord naar slimme apparatuur", "micro -> midi", "T",
     ["Electrische reclameborden", "Kentekenherkenning in parkeergarages — slimme apparatuur wordt standaard"]),
    ("Kopen wordt spel", "van kopen naar spelen", "midi", "T + S",
     ["Gameficering / gamyshopping", "Gemaskert gokken met 'rare' producten (labubu, squishies), gericht op kinderen",
      "Verloren pakketjes kopen per gewicht"]),
    ("Van behandelen naar optimaliseren", "van genezen naar optimaliseren", "maxi", "T + E(econ)",
     ["Smartheal / elite health / health-tech / DNA assessment",
      "Slaaplessen / slaaptekort / beter slapen", "Transhumanisatie"]),
    ("Van dierlijk naar alternatief", "van dierlijk naar alternatief", "midi", "T + E(ecol)",
     ["Wortelstoffen / vleesproxy", "Kunsteileider op een chip / uitstervende dieren redden"]),
    ("Van gezond naar obsessief", "van gezond naar obsessief", "midi", "S + E(ecol)",
     ["Ecorexia / orthorexia / ecotexia", "Ecologische eugenetica"]),
    ("Wonen wordt slim, klein en stedelijk", "van groot en vast naar slim, klein en stedelijk", "midi -> mega", "T + S + D",
     ["Smart living", "Bubble living", "Huizen verkopen met VR-brillen", "Verstedelijking / cityliving"]),
    ("Leefruimte wordt groter dan de aarde", "van aarde naar ruimte", "mega", "T + E(econ)",
     ["Ruimte toerisme / space living / space farm / airfarm",
      "Gedeelde toekomst / water op andere planeten"]),
    ("Technologie als machtsmiddel", "van commercieel naar geopolitiek machtsmiddel", "mega", "P + T",
     ["AI war / tech power"]),
    ("Leven wordt ontworpen", "van gegeven naar ontworpen", "mega", "D + T",
     ["CRISPR babies / geboren in babyfabriek"]),
    ("Van menselijk contact naar machinecontact", "van mens naar machine", "midi -> maxi", "T + S",
     ["Robot huisdier / robot love", "Datingtech / trashdating / oude mensen op datingsites"]),
    ("Van verbinding naar eenzaamheid", "van verbinding naar eenzaamheid", "maxi", "D + S",
     ["Eenzaamheidspandemie", "FOMO / JOMO"]),
    ("Van ik naar wij, van exclusief naar inclusief", "van exclusief en ik naar inclusief en wij", "maxi", "S",
     ["Exclusief → inclusief", "Wij = nieuwe ik / do-it-together"]),
    ("Levensloop wordt langer en in fases", "van levensloop naar fases", "mega", "D + S",
     ["100+ / multi stage life / werken tot je 100ste"]),
    ("Gemak als norm", "van inspanning naar gemak", "maxi", "S + E(econ)",
     ["Gemaksmaatschappij: korte weg, comfort, etes online, daten op apps", "Simplificering"]),
    ("Polarisering", "van midden naar extremen", "maxi", "S + P", ["Polarisering"]),
    ("Stijl als statement", "van functioneel naar statement", "midi", "S + T",
     ["Fashion als statement / 'vreemde' fashion",
      "Autnostalgie — modellen worden teruggebracht (e-Mustang)"]),
    ("Software wordt wegwerpmateriaal", "van product naar wegwerptool", "micro -> midi", "T + E(econ)",
     ["Disposable software: kleine tools in een weekend bouwen"]),
    ("Platform switch", "van Playstore en telefoon naar AI", "midi", "T + P",
     ["Platform switch: Playstore & telefoons → nu AI"]),
    ("Treintrots", "van auto naar trein", "midi", "S + E(ecol)", ["Treintrots"]),
]

WIDTHS = ["45mm", "45mm", "18mm", "14mm", "60mm", "22mm", "40mm", "40mm", "16mm", "18mm", "40mm"]

LEGEND = [
    "Signaal = een gebeurtenis ('dit bestaat'). Trend = een richting ('van A naar B').",
    "Definitie uit de les: een trend is een richting waarin waarden en behoeften veranderen, opgestuwd door externe krachten, en manifesteert zich door gedrag, producten en diensten.",
    "Testen bij omvormen: (1) richting? (2) externe DESTEP-kracht eronder? (3) >=2 signalen in dezelfde richting? (4) manifesteert het zich in gedrag/product/dienst? (5) niveau + horizon?",
    "Niveau: product micro 0-1 · markt midi 1-5 · consumenten maxi 5-15 · maatschappelijk mega 15-50.",
    "A/B/C/D uit de trechter: A interesseveld · B doelgroep · C vakgebied · D toekomst.",
    "Behoefte en Opkomende verwachting vul je zelf in — dat is hoofdstuk #3.",
    "83 ja-signalen uit tabblad 1 -> 38 trends. Elke signaal staat hier exact één keer.",
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
        out.append('<table:table-columns>')
        for w in widths:
            out.append(f'<table:table-column fo:width="{w}" fo:width-guess="true"/>')
        out.append('</table:table-columns>')
    out.append('<table:table-row><table:table-cell office:value-type="string">'
               f'<text:p>{esc(header[0])}</text:p></table:table-cell>')
    for h in header[1:]:
        out.append(f'<table:table-cell office:value-type="string"><text:p>{esc(h)}</text:p></table:table-cell>')
    out.append('</table:table-row>')
    for r in rows:
        out.append('<table:table-row>')
        for v in r:
            out.append(f'<table:table-cell office:value-type="string"><text:p>{esc(v)}</text:p></table:table-cell>')
        out.append('</table:table-row>')
    out.append('</table:table>')
    return "".join(out)


def main():
    z = zipfile.ZipFile(ODS)
    content = z.read("content.xml").decode("utf-8")
    rows = re.findall(r"<table:table-row[^>]*>.*?</table:table-row>", content)
    data = [cells_in(r) for r in rows[1:]]
    data = [c for c in data if len(c) >= 6 and c[0] and c[4].strip().lower() == "ja"]

    # controle: elke signaal exact één keer
    used = {}
    for t in TRENDS:
        for s in t[4]:
            used[s] = used.get(s, 0) + 1
    have = {c[0] for c in data}
    missing = have - set(used)
    extra = set(used) - have
    dup = {k: v for k, v in used.items() if v > 1}
    print(f"trends: {len(TRENDS)} · signalen: {len(used)} van {len(have)}")
    if missing:
        print("NIET TOEGEWEZELD:", *sorted(missing), sep="\n  ")
    if extra:
        print("NIET IN TAB 1:", *sorted(extra), sep="\n  ")
    if dup:
        print("DUBEL:", dup)

    out_rows = [[t[0], t[1], t[2], str(len(t[4])), "; ".join(t[4]), t[3], "", "", "", "", ""] for t in TRENDS]
    new_tab = table_xml("Trends", HEAD, out_rows, WIDTHS) + table_xml("Legend", ["Toelichting"], [[l] for l in LEGEND])
    content = content.replace("<table:named-expressions/>", new_tab + "<table:named-expressions/>")

    names = z.namelist()
    items = [(n, z.read(n)) for n in names]
    z.close()
    with zipfile.ZipFile(ODS, "w") as out:
        out.writestr(zipfile.ZipInfo("mimetype"), "application/vnd.oasis.opendocument.spreadsheet",
                     compress_type=zipfile.ZIP_STORED)
        for n, b in items:
            if n == "mimetype":
                continue
            if n == "content.xml":
                b = content.encode("utf-8")
            out.writestr(n, b)
    print("tabblad 'Trends' toegevoegd aan", ODS)


if __name__ == "__main__":
    main()
