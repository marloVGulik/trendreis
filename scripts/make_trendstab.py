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
     "delegeert zijn keuze — hij wil niet kiezen, hij wil het goede resultaat",
     "een samenleving die beslissen uitbesteedt",
     "T + E(econ)",
     ["Agentic commerce — LLM's verkopen producten aan mensen",
      "OpenAI doet bod op Medal: trainingsdata → real-world keuzes voor automatisering",
      "'Slimme' maatschappij: alles meten, algoritmes, dataverzameling, geïnformeerde keuzes",
      "AI eats doctor"]),
    ("Data als grondstof", "van data als bijproduct naar data als bezit en grondstof",
     "dataplatformen, sensoren, chips",
     "data wordt gekocht en verkocht als grondstof; bedrijven concurreren op data",
     "ruilt zijn data voor gratis tools en merkt pas later wat hij kwijt is",
     "data is het nieuwe kapitaal",
     "E(econ) + T",
     ["Data = nieuw goed / nieuwe olie", "Chips = nieuwe olie"]),
    ("Informatie wordt bubbel", "van open informatie naar bubbel",
     "algoritmes die filteren wat je ziet",
     "aanbod wordt gestuurd, niet gekozen",
     "krijgt alleen wat erbij past en denkt dat hij zelf kiest",
     "de bubbel is de wereld",
     "T + S",
     ["Infobubbel / infobesitas"]),
    ("Te veel info", "van meer naar minder verwerken",
     "filter- en contentdieet-tools",
     "aanbod groeit sneller dan verwerking",
     "filtert, dieet, schakelt uit — hij wil minder input",
     "aandacht is de munt",
     "T + S",
     ["Datadieet"]),
    ("Zonder eigen denkvermogen", "van eigen oordeel naar herhalen wat AI zegt",
     "AI-assistenten die antwoorden geven",
     "mensen volgen het antwoord zonder te controleren",
     "herhaalt wat AI zegt en kan er niet mee omgaan",
     "een nieuwe religie: het algoritme",
     "S + T",
     ["Digireligie", "Vleesproxy"]),
    ("Gegenereerd in plaats van gemaakt", "van maken naar genereren",
     "Claude, AI-posters, electrische reclameborden",
     "genereren vervangt met de hand maken",
     "wil een beeld, niet een maker",
     "handwerk verdwijnt, genereren komt",
     "T",
     ["AI-gegenereerde posters en plaatjes voor bedrijven"]),
    ("Digitalisering als koepel", "van analoog naar digitaal",
     "digitale producten en apparaten",
     "alles wordt digitaal en technologisch",
     "neemt digitaal als normaal aan",
     "een digitale wereld",
     "T",
     ["Digitalisering", "Technologisering"]),
    ("Van bezit naar toegang", "van bezitten naar cloud en toegang",
     "cloudabonnementen, bucloud",
     "toegang wordt het product in plaats van bezit",
     "huurt en abonnement, bezit wordt onnodig",
     "1% bezit, 99% toegang",
     "T + E(econ)",
     ["Cloud living / cloud worker / cloud economie / buycloud",
      "1% bezit vs 50% — Oxfam Novib, 42 mensen = 3,7 miljard"]),
    ("Van meetbaar naar merkbaar", "van meten naar merken",
     "belevingsproducten en tastbare materialen",
     "waarde wordt bepaald door beleving, niet door cijfers",
     "wil voelen, niet meten — een husky is meer waard dan een naakte kat",
     "perceptie is de maat",
     "E(econ) + S",
     ["Van meetbaar naar merkbaar", "Aaibaarheidsfactor"]),
    ("Klein wint van groot", "van groot bedrijf naar kleine startup met een idee",
     "kleine tools van kleine startups",
     "kleine tech-startups met een goed idee worden populair",
     "kiest het kleine idee boven het grote bedrijf",
     "groot is niet automatisch beter",
     "E(econ) + T",
     ["Kleine tech-startups met een goed idee zijn populair", "Innovatieladder"]),
    ("Nieuwe geldvormen", "van traditioneel geld naar nieuwe geldvormen",
     "crypto, bitcoin, alternatieve betaalmiddelen",
     "geldstromen lopen via marktplaatsen en superstar firms",
     "speculeert overdreven en vertrouwt de bank niet meer",
     "waarde is verdeeld en niet-centraal",
     "E(econ)",
     ["Cryptokoorts", "Donuteconomie / new economy / new money",
      "Investeren in bitcoin / superstar firms / marktplaatsen met datastromen"]),
    ("Tekort als motor", "van overvloed naar tekort",
     "reststromen, grondstoffen, tweedehands",
     "tekort (woning, grondstof) bepaalt prijs en aanbod",
     "rekent met schaarsheid en koopt reststromen",
     "een tekortwereld",
     "E(econ) + E(ecol) + D",
     ["Grondstoffen", "Grondstoftekort / tekorteconomie", "Woningtekort"]),
    ("Globalisering en slobalisation", "van lokaal naar wereldwijd — en nu weer langzamer",
     "wereldwijd leverbare producten",
     "markten zijn wereldwijd verbonden, maar vertragen",
     "wil wereldwijd, maar merkt de vertraging",
     "globaliseert, maar langzamer",
     "E(econ) + S",
     ["Globalisering / slobalisation"]),
    ("Van vertrouwen in het systeem naar wantrouwen", "van vertrouwen naar wantrouwen",
     "keurmerken en verificatie-tools",
     "claims en greenwashing worden betwist",
     "gelooft claims niet meer",
     "systeemmoe en angst",
     "S + P",
     ["Trust / angstgeneratie / systeemmoe", "Greenwashing"]),
    ("Van vertrouwen in big tech naar eigen controle", "van vertrouwen in een partij naar eigen controle",
     "lokale AI, self-hosted systemen, eigen servers",
     "bedrijven willen niet permanent afhankelijk zijn van AI-bedrijven",
     "wil zijn data lokaal en zelf in beheer",
     "soevereiniteit is een waarde",
     "P + T",
     ["Bedrijven zijn angstig om grote AI-bedrijven permanent te vertrouwen",
      "Cyber / cybersecurity", "Zorgvelden die gehackt worden"]),
    ("Massacontrole via registratie", "van vertrouwen naar registratie",
     "digital ID-systemen",
     "registratie bepaalt wie wat mag",
     "wordt geregistreerd en verliest toegang bij een fout",
     "registratie bepaalt wie wat mag",
     "P + T",
     ["Digital id", "Controle door rijken, big tech die misbruik maakt"]),
    ("Regel als barrière voor automatisering", "van automatiseren naar niet-automatiseren door regels",
     "cobots en hubots die niet naast mensen mogen werken",
     "automatisering stopt bij de regels",
     "merkt dat tech hier stopt bij de regels",
     "regels remmen de tech",
     "P + T",
     ["Regelfetjisisme", "Automatisering kan niet vanwege regels (sector die automatisering mist)",
      "Cobot / hubot"]),
    ("Duurzaamheid wordt efficiëntie en instoot", "van ideaal naar efficiëntie",
     "micro-fabrieken, solar democracy, CO2-zuigen",
     "duurzaamheid wordt een efficiëntieargument",
     "kiest duurzaam omdat het efficiënter is, niet omdat het goed is",
     "teruginput in plaats van uitstoot",
     "E(ecol) + E(econ) + P",
     ["Duurzaam = efficiënt (mijn definitie)", "Uitstoot → instoot",
      "Biobased bouwen / solar democracy / CO2 zuigen / micro-fabriek / wat is afval"]),
    ("Klimaat als conditie", "van zorg naar gegeven",
     "hittestress-bestendige bouw en koeling",
     "klimaat wordt randvoorwaarde en kostenpost",
     "plant rond de warmte — zijn studentenkamer kan niet koel blijven",
     "hitterecords zijn de norm",
     "E(ecol) + S + P",
     ["Opwarming / hitterecord / klimaattransition", "Hittestress"]),
    ("Van menselijke bediening naar automatische uitvoering", "van bedienden naar automatisch draaien",
     "automaten, grasmaaiers, dark factories",
     "uitvoering gebeurt zonder mens",
     "verwacht dat dingen draaien zonder iemand",
     "werken wordt overgenomen",
     "T",
     ["Automaten (suikerspinmachines, blikautomaten, snackmuren)",
      "Dark factories / fabrieken op zee / indoor farming",
      "Op-afstand-bestuurde grasmaaier van de gemeente"]),
    ("Van kopen naar zelf maken", "van kopen naar lokaal zelf maken",
     "3D-printers, op maat gemaakte spullen",
     "zelf maken concurrert met kopen",
     "zegt 'dat kan ik thuis ook' en bouwt zelf",
     "koper wordt maker",
     "S + T",
     ["3D-printer op de markt", "'Dat kan ik thuis ook' — zelf maken i.p.v. kopen",
      "Op maat gemaakte spullen"]),
    ("Slimme apparatuur wordt standaard in de openbare ruimte", "van bord naar slimme apparatuur",
     "kentekenherkenning, electrische reclameborden",
     "de openbare ruimte wordt apparatuur",
     "wordt registratie gewend in het straatbeeld",
     "de straat registreert",
     "T",
     ["Electrische reclameborden", "Kentekenherkenning in parkeergarages — slimme apparatuur wordt standaard"]),
    ("Kopen wordt spel", "van kopen naar spelen",
     "labubu, squishies, verrassingspakketten",
     "gamification en gokken, gericht op kinderen",
     "koopt voor het spel, niet voor het product",
     "consumptie is gokken",
     "T + S",
     ["Gameficering / gamyshopping",
      "Gemaskert gokken met 'rare' producten (labubu, squishies), gericht op kinderen",
      "Verloren pakketjes kopen per gewicht"]),
    ("Van behandelen naar optimaliseren", "van genezen naar optimaliseren",
     "DNA-assessment, health-tech, slaap-tools, robotonderdelen",
     "gezondheid wordt optimalisatie",
     "wil presteren en laat zijn lichaam aanpassen",
     "mens en machine smelten samen",
     "T + E(econ)",
     ["Smartheal / elite health / health-tech / DNA assessment",
      "Slaaplessen / slaaptekort / beter slapen", "Transhumanisatie",
      "Body mining / brein download", "Ecologische eugenetica"]),
    ("Van gezond naar obsessief", "van gezond naar obsessief",
     "tracking-apps en dieet-cultuur",
     "gezondheid wordt obsessie",
     "maakt van iets normaals een obsessie",
     "de voetafdruk wordt obsessie",
     "S + E(ecol)",
     ["Ecorexia / orthorexia / ecotexia"]),
    ("Leven wordt ontworpen", "van gegeven naar ontworpen",
     "kunsteileider op een chip, CRISPR, babyfabriek",
     "biotech wordt een keuze",
     "kiest techniek om een kind te krijgen",
     "levens worden ontworpen",
     "D + T",
     ["CRISPR babies / geboren in babyfabriek",
      "Kunsteileider op een chip / uitstervende dieren redden"]),
    ("Wonen wordt slim, klein en stedelijk", "van groot en vast naar slim, klein en stedelijk",
     "smart living-systemen, huizen verkopen met VR",
     "woning wordt slim en compact",
     "woont klein, slim en in de stad",
     "bubbel en verstedelijking",
     "T + S + D",
     ["Smart living", "Bubble living", "Huizen verkopen met VR-brillen",
      "Verstedelijking / cityliving"]),
    ("Leefruimte wordt groter dan de aarde", "van aarde naar ruimte",
     "space farm, airfarm, ruimte-toerisme",
     "ruimte wordt economisch interessant",
     "denkt buiten de aarde",
     "de toekomst is gedeeld, ook op andere planeten",
     "T + E(econ)",
     ["Ruimte toerisme / space living / space farm / airfarm",
      "Gedeelde toekomst / water op andere planeten"]),
    ("Van menselijk contact naar machinecontact", "van mens naar machine",
     "robot huisdier, datingapps",
     "machine vervangt contact",
     "kies een machine voor gezelschap",
     "relaties zijn hybride",
     "T + S",
     ["Robot huisdier / robot love", "Datingtech / trashdating / oude mensen op datingsites"]),
    ("Van verbinding naar eenzaamheid", "van verbinding naar eenzaamheid",
     "apps die eenzaamheid moeten oplossen",
     "eenzaamheid wordt een markt",
     "wil verbinding, krijgt een scherm",
     "een eenzaamheidspandemie",
     "D + S",
     ["Eenzaamheidspandemie", "FOMO / JOMO"]),
    ("Software als relatie", "van product naar platform voor relaties",
     "LinkedIn, Instagram",
     "software bepaalt hoe mensen omgaan",
     "onderhoudt relaties via software",
     "contact loopt via platforms",
     "T + S",
     ["Sustainable relations"]),
    ("Software wordt voor iedereen bouwbaar", "van exclusief naar inclusief",
     "Claude, site-builders, weekend-tools",
     "van grote bedrijven die software leveren naar mensen die zelf bouwen",
     "bouwt zelf zonder kennis",
     "iedereen kan bouwen",
     "T + S",
     ["Exclusief → inclusief", "Iedereen wil een site en denkt dat het met Claude kan",
      "Platform switch: Playstore & telefoons → nu AI",
      "Disposable software: kleine tools in een weekend bouwen"]),
    ("Van ik naar wij", "van ik naar wij",
     "gedeelde producten, do-it-together",
     "inclusie wordt verkoopargument",
     "wil erbij horen",
     "wij, niet ik",
     "S",
     ["Wij = nieuwe ik / do-it-together"]),
    ("Levensloop wordt langer en in fases", "van levensloop naar fases",
     "producten voor 100+",
     "multi stage life wordt een segment",
     "werkt tot zijn 100ste",
     "fases, niet één levensloop",
     "D + S",
     ["100+ / multi stage life / werken tot je 100ste"]),
    ("Gemak als norm", "van inspanning naar gemak",
     "apps, bezorging, de korte weg",
     "gemak wordt standaard",
     "neemt de kortste route",
     "een gemaksmaatschappij",
     "S + E(econ)",
     ["Gemaksmaatschappij: korte weg, comfort, etes online, daten op apps", "Simplificering"]),
    ("Polarisering", "van midden naar extremen",
     "niche-producten per groep",
     "het midden verdwijnt",
     "kiest een kamp",
     "een gepolariseerde samenleving",
     "S + P",
     ["Polarisering"]),
    ("Stijl als statement", "van functioneel naar statement",
     "statement-fashion, e-Mustang",
     "stijl wordt statement",
     "drukt zich uit via uiterlijk",
     "stijl is symbool",
     "S + T",
     ["Fashion als statement / 'vreemde' fashion",
      "Autnostalgie — modellen worden teruggebracht (e-Mustang)"]),
    ("Technologie als machtsmiddel", "van commercieel naar geopolitiek machtsmiddel",
     "drones en defensie-tech",
     "kleine startups in defensie worden populair",
     "bespeurt dat tech macht is, niet alleen nut",
     "tech is macht",
     "P + T",
     ["AI war / tech power"]),
    ("Treintrots", "van auto naar trein",
     "treintickets en treinabonnementen",
     "trein wint van auto",
     "is trots op groen",
     "groen is trots",
     "S + E(ecol)",
     ["Treintrots"]),
]

BEHOEFTE = {
    "Automatisering van de keuze": ("ontlast worden van keuzes", "dat de machine de juiste keuze maakt en dat je ziet op basis waarvan"),
    "Data als grondstof": ("controle over eigen data, via open source en lokaal", "dat gratis tools niet met zijn data worden betaald"),
    "Informatie wordt bubbel": ("informatie buiten de eigen bubbel", "dat het algoritme hem niet alleen naar zijn eigen mening stuurt"),
    "Te veel info": ("rust en een filter", "dat minder input een keuze is, geen tekort"),
    "Zonder eigen denkvermogen": ("zelf kunnen nadenken en controleren", "dat een antwoord niet automatisch waar is"),
    "Gegenereerd in plaats van gemaakt": ("snel en goedkoop beeld en materiaal", "dat genereren normaal wordt en makers duurder"),
    "Digitalisering als koepel": ("toegang tot digitale systemen", "dat alles digitaal beschikbaar is"),
    "Van bezit naar toegang": ("toegang zonder vastleggen", "dat abonnementen betaalbaar blijven"),
    "Van meetbaar naar merkbaar": ("iets voelen, niet alleen cijfers", "dat beleving beloond wordt"),
    "Klein wint van groot": ("dat een klein idee serieus genomen wordt", "dat klein beter kan zijn dan groot"),
    "Nieuwe geldvormen": ("geld dat niet van een bank komt", "dat waarde anders vastgelegd kan worden"),
    "Tekort als motor": ("zekerheid over grondstoffen en woning", "dat schaarsheid prijs en keuze bepaalt"),
    "Globalisering en slobalisation": ("lokaal beschikbaar blijven", "dat wereldwijde toelevering afremt"),
    "Van vertrouwen in het systeem naar wantrouwen": ("bewijs in plaats van claims", "dat claims niet kloppen tot ze bewezen zijn"),
    "Van vertrouwen in big tech naar eigen controle": ("eigen, lokale systemen", "dat afhankelijkheid tijdelijk is, niet permanent"),
    "Massacontrole via registratie": ("toegang behouden ondanks een fout", "dat registratie consequenties heeft"),
    "Regel als barrière voor automatisering": ("regels die techniek niet onnodig blokkeren", "dat regelgeving meebeweegt met de tech"),
    "Duurzaamheid wordt efficiëntie en instoot": ("duurzaam dat ook goedkoper is", "dat duurzaamheid een businesscase is, geen imago"),
    "Klimaat als conditie": ("koel en leefbaar blijven", "dat warmte de standaard is"),
    "Van menselijke bediening naar automatische uitvoering": ("dat dingen draaien zonder iemand", "dat automatisering de norm is"),
    "Van kopen naar zelf maken": ("zelf kunnen bouwen", "dat zelf maken concurrerend is"),
    "Slimme apparatuur wordt standaard in de openbare ruimte": ("registratie die niets onnodig vastlegt", "dat de straat slim blijft"),
    "Kopen wordt spel": ("vermaak bij het kopen", "dat kopen een ervaring is, geen transactie"),
    "Van behandelen naar optimaliseren": ("presteren en verbeteren", "dat het lichaam aanpasbaar is"),
    "Van gezond naar obsessief": ("maat houden", "dat obsessie wordt gezien als ziekte"),
    "Leven wordt ontworpen": ("kinderen kunnen krijgen ondanks een probleem", "dat leven aanpasbaar is"),
    "Wonen wordt slim, klein en stedelijk": ("klein wonen dat toch werkt", "dat de stad compacter wordt"),
    "Leefruimte wordt groter dan de aarde": ("grondstoffen en ruimte buiten de aarde", "dat ruimtevaart economisch normaal wordt"),
    "Van menselijk contact naar machinecontact": ("gezelschap zonder verplichting", "dat een machine er mag zijn"),
    "Van verbinding naar eenzaamheid": ("echt contact", "dat een scherm niet volstaat"),
    "Software als relatie": ("relaties die software verdragen", "dat platforms de plek zijn waar je iemand tegenkomt"),
    "Software wordt voor iedereen bouwbaar": ("zelf bouwen zonder kennis", "dat iedereen kan bouwen"),
    "Van ik naar wij": ("erbij horen", "dat samen doen de norm is"),
    "Levensloop wordt langer en in fases": ("fases die passen bij leeftijd", "dat werken tot 100 normaal wordt"),
    "Gemak als norm": ("de kortste route", "dat gemak geen extra kosten mag hebben"),
    "Polarisering": ("een midden", "dat het midden verdwijnt"),
    "Stijl als statement": ("uitdrukking", "dat uiterlijk een standpunt is"),
    "Technologie als machtsmiddel": ("eigen tech, niet afhankelijk", "dat tech macht bepaalt"),
    "Treintrots": ("groen reizen zonder inleveren", "dat trein boven auto gaat"),
}

LEGEND = [
    "Signaal = een gebeurtenis ('dit bestaat'). Trend = een richting ('van A naar B').",
    "Definitie uit de deck: een trend is een richting waarin waarden en behoeften veranderen, opgestuwd door externe krachten, en manifesteert zich door gedrag, producten en diensten.",
    "Testen bij omvormen: (1) richting? (2) externe DESTEP-kracht eronder? (3) >=2 signalen in dezelfde richting? (4) manifesteert het zich in gedrag/product/dienst? (5) niveau + horizon?",
    "Vier niveaus per trend: producttrend micro 0-1 (welke producten zijn populair) · markttrend midi 1-5 (wat gebeurt er in de markt) · consumententrend maxi 5-15 (hoe gedraagt de consument zich, wat wilt/verwacht deze) · maatschappelijke trend mega 15-50 (in wat voor wereld leven we).",
    "Voorbeeld 'van gemaakt naar gegenereerd': product = Claude · markt = genereren i.p.v. met de hand maken · consument = wil gemakkelijk visuelen maken · maatschappelijk = een wereld waarin AI groeit.",
    "A/B/C/D uit de trechter: A interesseveld · B doelgroep · C vakgebied · D toekomst.",
    "Behoefte en Opkomende verwachting zijn ingevuld als concept — dat is hoofdstuk #3 en moet je nog bevestigen. A/B/C/D, Doorgaan? en Waarom? vul jij in.",
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
    seen, dedup = set(), []
    for r in data:
        if r[0] in seen:
            continue
        seen.add(r[0])
        dedup.append(r)
    if len(dedup) != len(data):
        print(f"dubbele rijen verwijderd: {len(data) - len(dedup)}")
    data = dedup
    changed = []
    for r in data:
        if r[0] in FIX:
            new_name, new_theme = FIX[r[0]]
            changed.append(f"{r[0]}  ->  {new_name}  [{new_theme}]")
            r[0], r[2] = new_name, new_theme
    existing = {r[0] for r in data}
    for name, destep, theme, ja, why in EXTRA:
        if name in existing:
            continue
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
                 t[6], BEHOEFTE[t[0]][0], BEHOEFTE[t[0]][1], "", "", ""] for t in TRENDS]
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
