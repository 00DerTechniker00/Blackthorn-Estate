import json

# Import layers from generate_mega_mansion
import generate_mega_mansion as gmm

layers = gmm.layers
palette = gmm.PALETTE
dimensions = {
    "width": gmm.W,
    "depth": gmm.D,
    "layerCount": len(layers),
    "heightBlocks": 46,
    "anchor": {
        "x": -662,
        "y": 126,
        "z": 790,
        "seed": "-4815224116428668341",
        "version": "26.2 (1.20+ / 1.21+)",
        "orientation": "Süd-Westen (Abendsonne)"
    }
}

# Calculate total materials
total_counts = {}
for l in layers:
    for bId, count in l["counts"].items():
        total_counts[bId] = total_counts.get(bId, 0) + count

materials_list = []
# 1 Shulker Box = 27 Stacks = 1,728 items
# 1 Stack = 64 items
for bId, count in sorted(total_counts.items(), key=lambda x: int(x[0])):
    if bId == "0": continue
    meta = palette.get(bId, {"name": "Unbekannt", "glyph": "❓"})
    stacks = round(count / 64, 1)
    shulkers = round(count / 1728, 2)
    
    # Category
    cat = "Baublöcke"
    if bId in ["13", "14"]: cat = "Holz & Ausbau"
    elif bId in ["11", "12"]: cat = "Glas & Fenster"
    elif bId in ["18", "19", "20", "25", "26", "27"]: cat = "Redstone, Technik & Keller"
    elif bId in ["21", "22", "23", "24", "28", "29", "30", "31"]: cat = "Dekoration & Beleuchtung"
    elif bId in ["4", "5", "6", "7", "16"]: cat = "Prunk & Quarz-Fassade"

    materials_list.append({
        "id": bId,
        "name": meta["name"],
        "glyph": meta["glyph"],
        "color": meta["color"],
        "count": count,
        "stacks": stacks,
        "shulkers": shulkers,
        "category": cat
    })

rooms = [
    {
        "id": "keller3_lounge",
        "name": "Keller 3: Klippen-Lounge & Panorama-Bar",
        "level": "Y = 105 - 110 (Tiefste Ebene)",
        "coords": "X: -644 bis -611 | Z: 771 bis 776",
        "dimensions": "34 × 23 Blöcke",
        "desc": "Direkt in die 60 Meter senkrecht abfallende Felswand gesprengte Entspannungs-Lounge. Zwei Stockwerke hohe Glasfront mit atemberaubendem Blick in das Sonnenuntergangs-Tal.",
        "highlights": [
            "Freitragender Klippenbalkon mit Glasboden über dem 60-Block-Abgrund",
            "Gemütlicher Seelenfeuer-Natursteinkamin mit Kaminzug zur Klippenwand",
            "Voll ausgestattete Bar mit Eichenfässern, Brauständen und Bartresen",
            "Geheimer Wasseraufzug als Express-Verbindung direkt ins Foyer"
        ]
    },
    {
        "id": "keller2_dungeon",
        "name": "Keller 2: Villager-Dungeon ('Folterkeller')",
        "level": "Y = 114 - 119",
        "coords": "X: -646 bis -609 | Z: 777 bis 803",
        "dimensions": "38 × 27 Blöcke",
        "desc": "Hochmoderner, vollautomatisierter Dorfbewohner-Veredelungskomplex mit 16 isolierten Handelszellen und Zombie-Kreislauf für garantierte 1-Smaragd-Preise.",
        "highlights": [
            "16 separate Zellen mit Sticky-Piston-Boden für kontrollierte Zombie-Infektion",
            "Laufender Zombie im Loren-Kreislauf auf Hard-Schwierigkeitsgrad (100% Konvertierung)",
            "Automatischer Brau- & Wurfspender für Schwäche-Tränke und Goldapfel-Depot",
            "4 gewölbte Expansions-Portale (Norden: Deepslate-Mine, Süden: Nether-Hub, Osten: Bunker, Westen: Farmen)"
        ]
    },
    {
        "id": "keller1_lager",
        "name": "Keller 1: Steampunk Kupfer-Lager & Relog-Teleporter",
        "level": "Y = 121 - 124",
        "coords": "X: -648 bis -607 | Z: 777 bis 803",
        "dimensions": "42 × 27 Blöcke",
        "desc": "Massives automatisches Sortierlager im Steampunk-Stil mit 96 Doppelkisten, Kupfergittern und warmen Kupferlampen. Beinhaltet die zentrale Notfall-Enderperlen-Stasiskammer.",
        "highlights": [
            "96 Doppelkisten in 4 übersichtlichen Gängen mit Trichter-Kategoriensortierung",
            "Enderperlen-Stasiskammer im Zentrum: Seelensand-Wasseraufzug hält eine geworfene Perle schwebend",
            "Relog-Sensor & Notfall-Panikschalter: Schließt die Eisenfalltür und teleportiert den Spieler sofort nach Hause",
            "Exponierte Kupferrohre, Kupferbirnen und Fichtengebälk"
        ]
    },
    {
        "id": "eg_foyer",
        "name": "EG: Vestibül, Foyer & Zweiläufige Kaisertreppe",
        "level": "Y = 126 - 132 (Plateau-Ebene)",
        "coords": "X: -669 bis -656 | Z: 787 bis 803",
        "dimensions": "14 × 17 Blöcke (2 Stockwerke hoch)",
        "desc": "Das monumentale Herzstück des Anwesens. Schachbrettmuster aus poliertem Diorit und Quarz, beleuchtet von einem gewaltigen Goldkronleuchter.",
        "highlights": [
            "Zweiläufige Kaisertreppe aus glattem Quarz mit Zwischenpodest",
            "Offene Mezzanin-Galerie mit Quarzgeländer im 1. Obergeschoss",
            "Hohes Eingangsportal mit geschnitzten dunklen Eichentüren",
            "Direkter Blick durch die Flügeltüren auf die Klippe"
        ]
    },
    {
        "id": "eg_salon_bibliothek",
        "name": "EG Westflügel: Kamin-Salon & Große Bibliothek",
        "level": "Y = 126 - 132",
        "coords": "X: -693 bis -675 | Z: 779 bis 811",
        "dimensions": "19 × 32 Blöcke",
        "desc": "Eleganter Salon im linken Achteck-Erkerturm mit herrschaftlichem Marmorkamin, gemütlicher Ledersitzgruppe und zweistöckiger Bibliothek mit Zaubertisch.",
        "highlights": [
            "Achteckiger Erkerturm mit 3 hohen Sprossenfenstern",
            "Voll bestückte Bücherwände für Maximal-Verzauberungen (Level 30)",
            "Kamin mit Ziegelabzug bis in den Schornsteinkopf Y=152",
            "Kartentisch und Lesepulte mit Ausblick auf das Bergplateau"
        ]
    },
    {
        "id": "eg_speisesaal_kueche",
        "name": "EG Ostflügel: Bankettsaal & Gourmetküche",
        "level": "Y = 126 - 132",
        "coords": "X: -655 bis -631 | Z: 779 bis 811",
        "dimensions": "25 × 32 Blöcke",
        "desc": "Prunkvoller Speisesaal im rechten Erkerturm mit 14-Personen-Tafel, Flügelklavier und angeschlossener Küche mit Rauchöfen und Speiseaufzug.",
        "highlights": [
            "Festtafel mit Samtstühlen und Kerzenleuchtern im Achteck-Erker",
            "Gourmetküche mit Schnell-Schmelzöfen, Kesseln und Vorratsfässern",
            "Speiseaufzug (Dumbwaiter) mit Trichterlinie direkt ins Kellerlager",
            "Große Fenstertüren zur Ostterrasse"
        ]
    },
    {
        "id": "eg_infinity_pool",
        "name": "Hinterseite: Freitragender Klippen-Infinity-Pool",
        "level": "Y = 125 - 127 (Rückseite zur Schlucht)",
        "coords": "X: -674 bis -650 | Z: 768 bis 779",
        "dimensions": "25 × 12 Blöcke (ragt 9 Blöcke frei über die Klippe!)",
        "desc": "Das spektakuläre Markenzeichen des Anwesens: Ein 25 Blöcke breiter Luxus-Pool, dessen Wasserwand scheinbar nahtlos in die Wolken und den 60-Block-Abgrund stürzt.",
        "highlights": [
            "Unterwasserscheinwerfer mit Seelaternen unter azurblauem Glas",
            "Klippenkante aus nahtlosem Glas – Schwimmen direkt über dem Abgrund",
            "Flankierende Sonnenterrassen mit Quarzquader-Liegen und Sonnenschirmen",
            "Massive Tiefenschiefer-Stützbögen verankern das Becken im Fels"
        ]
    },
    {
        "id": "og_master_suite",
        "name": "1. OG: Master-Suite, Gästeflügel & Waffenkammer",
        "level": "Y = 133 - 138",
        "coords": "X: -693 bis -631 | Z: 779 bis 803",
        "dimensions": "63 × 25 Blöcke",
        "desc": "Königliche Schlafgemächer im Obergeschoss. Die Master-Suite verfügt über ein Baldachinbett, ein eigenes Luxusbad und Zugang zum Portikus-Balkon.",
        "highlights": [
            "Portikus-Balkon direkt über dem Haupteingang mit Blick auf den Vorplatz",
            "Mezzanin-Galerie mit freiem Blick auf das Foyer",
            "Waffenkammer & Trophäensaal mit Rüstungsständern für Netherit-Rüstungen",
            "Elytren-Startrampe auf dem hinteren Klippenbalkon"
        ]
    },
    {
        "id": "dach_plattform",
        "name": "Dachgeschoss: Gauben, Dachterrasse & Kamine",
        "level": "Y = 139 - 150 (Höchste Ebene)",
        "coords": "X: -662 ± 25 | Z: 790 ± 15",
        "dimensions": "40 × 20 Blöcke Plattform auf Y=145",
        "desc": "Mächtiges Tiefenschiefer-Walmdach mit 4 Ziergauben, weißem Quarz-Dachkamm (Cresting) und zwei rauchenden Zwillingsschornsteinen.",
        "highlights": [
            "4 voll ausgebaute Dachgauben mit Dreiecksgiebeln und Glasscheiben",
            "Dach-Aussichtsplattform (Widow's Walk) mit Quarz-Zinnen",
            "Zwei monumentale Ziegelschornsteine mit Lagerfeuern für permanenten Kaminrauch",
            "Höchster Punkt bei Y=152 mit uneingeschränkter 360-Grad-Sicht über das Biom"
        ]
    }
]

redstone_guides = [
    {
        "id": "stasis_teleporter",
        "name": "Enderperlen-Stasis Relog-Teleporter",
        "category": "Überlebens- & Notfalltechnik",
        "level": "Keller 1 (Y = 121 - 124)",
        "coords": "X: -662, Y: 121..124, Z: 790",
        "desc": "Ein unverzichtbares Survival-Feature: Schwebt eine geworfene Enderperle in einer Seelensand-Wassersäule, wird der Spieler sofort teleportiert, sobald die Perle einen Block berührt.",
        "mechanic": "Seelensand auf Y=121 erzeugt eine Aufwärts-Blasensäule. Wasserquellblöcke auf Y=122, 123 und 124 halten die Perle in der Schwebe. Eine Eisenfalltür auf Y=124 schließt sich über der Wasseroberfläche.",
        "triggers": [
            "Relog-Erkennung: Ein Beobachter (Observer) registriert das Laden des Chunks oder das Signal einer Schneedruckplatte beim Server-Beitritt und löst die Falltür aus.",
            "Notfall-Panikhebel: Versteckter Hebel im Foyer oder per Fernschaltung (Sculk/Funk) schließt die Kammer sofort.",
            "Automatische Nachladung: Kiste mit Vorratsperlen und Auswurfspender direkt neben dem Becken."
        ],
        "materials": [
            "1x Seelensand (Y=121)",
            "3x Wasserquellblöcke (kein fließendes Wasser!)",
            "1x Eisenfalltür (an der Oberkante von Y=124)",
            "1x Beobachter (Observer)",
            "4x Redstone-Staub",
            "1x Redstone-Verstärker (auf 2 Ticks)"
        ]
    },
    {
        "id": "villager_curing",
        "name": "Villager 'Folterkeller' 1-Smaragd Rabatt-Kreislauf",
        "category": "Wirtschaft & Dorfbewohner",
        "level": "Keller 2 (Y = 114 - 119)",
        "coords": "X: -646 bis -609 | Z: 777 bis 803",
        "desc": "Auf dem Spielmodus 'Schwer' (Hard) wird ein von einem Zombie getöteter Villager zu 100% in einen Zombie-Villager verwandelt. Nach der Heilung mit Schwächetrank und Goldapfel sinken alle Preise dauerhaft auf 1 Smaragd!",
        "mechanic": "Hinter jeder der 16 Zellen verläuft eine geschützte Gleisstrecke, auf der ein nametagged Zombie ('Herr Zomboss') in einer Lore patrouilliert. Der Boden jeder Zelle besteht aus einem Klebrigen Kolben (Sticky Piston).",
        "steps": [
            "1. Hebel an der Zellenvorderseite betätigen: Kolben zieht den Bodenblock um 1 nach unten.",
            "2. Villager rutscht in die Sichtlinie des fahrenden Zombies -> Zombie infiziert den Villager in Sekunden.",
            "3. Hebel erneut betätigen: Kolben schiebt den Zombie-Villager wieder nach oben in seine sichere Zelle.",
            "4. Druckknopf betätigen: Decken-Spender wirft eine Wurftrank der Schwäche auf die Zelle.",
            "5. Dem Zombie-Villager einen Goldenen Apfel füttern -> Partikeleffekt startet -> Nach 2 Minuten ist der Villager geheilt mit maximalen Rabatten (Mending für 1 Smaragd)!"
        ],
        "materials": [
            "16x Klebrige Kolben (Sticky Pistons)",
            "16x Hebel & 16x Knöpfe",
            "16x Werfer (Dispensers) an der Decke",
            "16x Lesepulte (Lecterns)",
            "1x Lore mit nametagged Zombie ('Herr Zomboss')",
            "32x Antriebsschienen & 48x Normale Schienen"
        ]
    },
    {
        "id": "steampunk_sorter",
        "name": "Steampunk Kupfer-Sortierlager (96 Doppelkisten)",
        "category": "Lager & Logistik",
        "level": "Keller 1 (Y = 121 - 124)",
        "coords": "X: -648 bis -607 | Z: 777 bis 803",
        "desc": "Automatisches Kistensystem nach dem bewährten Impuls-Trichterfilter-Prinzip. Sortiert alle Baumaterialien, Erze und Drops vollautomatisch ein und zeigt Füllstände über Kupferbirnen an.",
        "mechanic": "Standard-Impuls-Sortierfilter: Trichter mit 41x Ziel-Item + 4x Füll-Items (z.B. umbenannte Stöcke) gibt ein Redstone-Signal an einen Komparator ab. Kupferbirnen leuchten auf, wenn die Kisten voll sind.",
        "features": [
            "4 lange Lagergassen mit insgesamt 96 Doppelkisten (192 Einzelkisten)",
            "Sortiergeschwindigkeit: 1 Item alle 0,4 Sekunden pro Trichterstraße",
            "Unsortiert-Rücklaufkiste am Ende der Linie mit Warnton",
            "Schaltbare Kupferbeleuchtung für maximale Atmosphäre"
        ],
        "materials": [
            "192x Kisten (96 Doppelkisten)",
            "192x Trichter (Hoppers)",
            "96x Redstone-Komparatoren",
            "96x Redstone-Verstärker",
            "192x Redstone-Staub",
            "48x Kupferlampen (Copper Bulbs)"
        ]
    }
]

phases = [
    {
        "id": 1,
        "name": "Phase 1: Klippenaushub & Keller 3 (Klippen-Lounge)",
        "yRange": "Y = 105 - 110",
        "focus": "Erdaushub in der Felswand, Tiefenschiefer-Fundamente, Klippenbalkon über der Schlucht",
        "checklist": [
            "Felswand an der Klippe (Z: 771 bis 776) 20 Blöcke unter das Plateau aushöhlen",
            "Bruchstein- und Tiefenschiefer-Pfeiler für die Klippenplattform verankern",
            "Klippenbalkon mit Glasboden und Eisengeländern über der Schlucht montieren",
            "Zweistöckige Panorama-Glaswand (Getöntes Glas) einbauen",
            "Seelenfeuer-Kamin und Lounge-Bar einrichten"
        ]
    },
    {
        "id": 2,
        "name": "Phase 2: Keller 2 (Villager-Dungeon & Curing-Kreislauf)",
        "yRange": "Y = 114 - 119",
        "focus": "Redstone-Pistons, Zombie-Gleisschleife, 16 Handelszellen, Expansions-Portale",
        "checklist": [
            "Dungeon-Ebene bei Y=114 ausheben und Tiefenschiefer-Boden verlegen",
            "Schienenkreis für den Zombie hinter den Zellen montieren und Lore einsetzen",
            "16 Sticky Pistons unter den Dorfbewohner-Plätzen verkabeln",
            "Spender für Schwäche-Wurftränke an der Decke installieren",
            "4 gewölbte Portale für spätere Tunnel zur Mine und Nether anlegen"
        ]
    },
    {
        "id": 3,
        "name": "Phase 3: Keller 1 (Kupferlager & Relog-Teleporter)",
        "yRange": "Y = 121 - 124",
        "focus": "96 Doppelkisten, Trichterstraßen, Enderperlen-Stasiskammer, Kupfer-Design",
        "checklist": [
            "Lagerraum aushöhlen und Fichten-Balkendecke einziehen",
            "96 Doppelkisten in 4 Gängen mit Trichterfiltern aufbauen",
            "Stasis-Wassersäule mit Seelensand auf Y=121 errichten und Perle einwerfen",
            "Eisenfalltür mit Relog-/Observer-Sensorik und Panikschalter verbinden",
            "Kupferlampen und Kupfergitter für Steampunk-Atmosphäre anbringen"
        ]
    },
    {
        "id": 4,
        "name": "Phase 4: Fundamente, Freitreppe & Infinity-Pool",
        "yRange": "Y = 125 - 126",
        "focus": "Plateausockel nivellieren, Portikus-Treppe, Infinity-Pool über dem Abgrund",
        "checklist": [
            "Bergplateau bei Y=125 mit Tiefenschieferziegeln exakt einebnen",
            "Freitreppe am Haupteingang (X: -668 bis -657) mit Quarzstufen setzen",
            "Infinity-Pool (25×12 Blöcke) über die Klippenkante hinausbauen",
            "Poolbecken mit Seelaternen und azurblauem Wasser fluten; Glaskante abdichten",
            "Foyer-Schachbrettboden aus Diorit und Quarz verlegen"
        ]
    },
    {
        "id": 5,
        "name": "Phase 5: Erdgeschoss-Fassade & Prunkräume",
        "yRange": "Y = 127 - 132",
        "focus": "Ziegelwände, Quarz-Eckquader, Portikus-Säulen, Erker, Salon, Foyer-Kaisertreppe",
        "checklist": [
            "Ziegelaußenwände hochziehen und Quarz-Eckquader an allen Ecken setzen",
            "2x2 Kolossalsäulen des Portikus mit Basen und Kapitellen errichten",
            "Die beiden Achteck-Erkertürme mit 3 hohen Fenstern pro Seite mauern",
            "Kaisertreppe mit Quarzstufen im Foyer schwungvoll hochführen",
            "Hervorspringendes Quarz-Geschossgesims rund um das Gebäude abschließen"
        ]
    },
    {
        "id": 6,
        "name": "Phase 6: 1. Obergeschoss & Portikus-Balkon",
        "yRange": "Y = 133 - 138",
        "focus": "Mezzanin-Galerie, Master-Suite, Balkone, Dreiecksgiebel, Zahnfries-Gesims",
        "checklist": [
            "Bodenplatte und Mezzanin-Galerie mit Blick ins Foyer einziehen",
            "Portikus-Sonnenterrasse mit Quarzstufen-Balustrade absichern",
            "Schlafsuiten, Bibliothek und Trophäensaal mit Fenstern ausstatten",
            "Klassischen Dreiecksgiebel über dem Portikus mit Quarzstufen vollenden",
            "Ausladendes Konsolengesims (Zahnfries) als Träger für das Dach anbringen"
        ]
    },
    {
        "id": 7,
        "name": "Phase 7: Tiefenschiefer-Walmdach, Gauben & Kamine",
        "yRange": "Y = 139 - 150",
        "focus": "Steildach, 4 Dachgauben, Aussichtsplattform, Quarz-Zinnen, Schornsteinrauch",
        "checklist": [
            "Umlaufende Traufe aus Tiefenschiefer-Treppen anbringen",
            "Steiles Walmdach stufenweise hochziehen",
            "4 Dachgauben mit Ziergiebeln und Fenstern in die Dachschräge einarbeiten",
            "Aussichtsplattform (Widow's Walk) mit weißem Quarz-Zinnenkamm krönen",
            "Zwei Zwillings-Ziegelschornsteine mit Lagerfeuern für permanenten Rauch errichten"
        ]
    }
]

world_data = {
    "seed": "-4815224116428668341",
    "version": "26.2 (kompatibel mit 1.20 / 1.21+)",
    "coordinates": {
        "x": -662,
        "y": 126,
        "z": 790,
        "dimension": "Overworld",
        "biome": "Stony Peaks / Jagged Peaks (Gipfel & Klippen)"
    },
    "orientation": {
        "front": "Süd-Westen (Blick direkt in den Sonnenuntergang)",
        "rear": "Nord-Osten (Senkrechte 60m-Klippe zum Tal mit Flusslauf)",
        "leftWing": "Nord-Westen (Berggrat)",
        "rightWing": "Süd-Osten (Alpines Hochplateau)"
    },
    "siteNotes": [
        "Das Plateau wurde auf Höhe Y=126 planiert; ein Aushubgraben markiert das Baufeld.",
        "Die Klippenkante im Nordosten fällt 60 Blöcke steil ab – ideal für den Infinity-Pool und die Klippen-Lounge.",
        "Der Vorplatz im Südwesten bietet reichlich Platz für die gepflasterte Auffahrt und Baumalleen.",
        "Ein pinkfarbener Leuchtfeuer-Strahl (Beacon) bei X=-657 markiert den zentralen Punkt."
    ]
}

full_data = {
    "dimensions": dimensions,
    "palette": palette,
    "layers": layers,
    "materials": materials_list,
    "rooms": rooms,
    "redstoneGuides": redstone_guides,
    "phases": phases,
    "world": world_data
}

with open("data.js", "w", encoding="utf-8") as f:
    f.write("// Autogenerated Enhanced Mega Mansion Data with 36 Layers & Full Architecture\n")
    f.write("window.MANSION_DATA = ")
    json.dump(full_data, f, indent=2, ensure_ascii=False)
    f.write(";\n")

print("Successfully wrote full data.js!")
print("File size:", len(open("data.js").read()), "bytes")
