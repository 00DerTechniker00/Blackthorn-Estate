import json
import os

W = 70  # Width (X-axis, -697 to -628)
D = 50  # Depth (Z-axis, 765 to 814)
# Center: x=35 -> X=-662, z=25 -> Z=790
# z=0 is rear cliff (Z=765), z=49 is front driveway (Z=814)

PALETTE = {
    "0": {"name": "Luft", "color": "transparent", "border": "transparent", "glyph": ""},
    "1": {"name": "Ziegelstein (Brick)", "color": "#a04739", "border": "#72291d", "glyph": "🧱"},
    "2": {"name": "Ziegelsteintreppe", "color": "#af5244", "border": "#72291d", "glyph": "▲"},
    "3": {"name": "Ziegelsteinstufe", "color": "#b95d4f", "border": "#72291d", "glyph": "▬"},
    "4": {"name": "Glatter Quarz / Calcit (Eckquader & Gesims)", "color": "#edeae2", "border": "#c2bcaf", "glyph": "◈"},
    "5": {"name": "Quarzsäule (Portikus-Säulen)", "color": "#f7f5f0", "border": "#b8b2a3", "glyph": "🏛️"},
    "6": {"name": "Quarztreppe (Bogenstürze & Giebel)", "color": "#e3dfd3", "border": "#aaa495", "glyph": "△"},
    "7": {"name": "Quarzstufe (Gesimse & Dachkamm)", "color": "#dcd7cb", "border": "#aaa495", "glyph": "▫"},
    "8": {"name": "Tiefenschieferziegel (Sockel & Dach)", "color": "#313238", "border": "#1f2024", "glyph": "⬛"},
    "9": {"name": "Tiefenschiefer-Treppe (Walmdach)", "color": "#3c3e45", "border": "#212226", "glyph": "▲"},
    "10": {"name": "Tiefenschiefer-Stufe (Dachüberstand)", "color": "#484a52", "border": "#212226", "glyph": "▬"},
    "11": {"name": "Getöntes Glas / Schwarzes Glas", "color": "#1e293b", "border": "#0f172a", "glyph": "🪟"},
    "12": {"name": "Glasscheibe (Weiß / Hellgrau)", "color": "#94a3b8", "border": "#64748b", "glyph": "┼"},
    "13": {"name": "Fichtenholzbretter (Böden & Decken)", "color": "#6d5236", "border": "#4e3923", "glyph": "🪵"},
    "14": {"name": "Dunkles Eichenholz (Türen, Treppen, Rahmen)", "color": "#3b2816", "border": "#23180c", "glyph": "🚪"},
    "15": {"name": "Bruchstein / Glatter Stein (Fundamente)", "color": "#64748b", "border": "#475569", "glyph": "🪨"},
    "16": {"name": "Polierter Diorit / Quarz-Marmor (Foyer)", "color": "#cbd5e1", "border": "#94a3b8", "glyph": "◇"},
    "17": {"name": "Wasserblock (Infinity Pool & Stasis)", "color": "#0284c7", "border": "#0369a1", "glyph": "💧"},
    "18": {"name": "Kupferblock / Kupfergitter (Lager)", "color": "#d97706", "border": "#92400e", "glyph": "⚙️"},
    "19": {"name": "Eisenstangen / Falltür (Zellen)", "color": "#71717a", "border": "#3f3f46", "glyph": "⛓️"},
    "20": {"name": "Klebriger Kolben / Redstone", "color": "#ef4444", "border": "#991b1b", "glyph": "⚡"},
    "21": {"name": "Seelenfeuer / Seelensand (Kamin & Stasis)", "color": "#38bdf8", "border": "#0284c7", "glyph": "🔥"},
    "22": {"name": "Bücherregale / Werkbänke", "color": "#854d0e", "border": "#543007", "glyph": "📚"},
    "23": {"name": "Seelaterne / Laterne (Beleuchtung)", "color": "#38bdf8", "border": "#0ea5e9", "glyph": "💡"},
    "24": {"name": "Kiste / Fass (Lager & Schränke)", "color": "#b45309", "border": "#78350f", "glyph": "📦"},
    "25": {"name": "Enderperlen-Stasis-Kammer (Teleporter)", "color": "#10b981", "border": "#047857", "glyph": "🧿"},
    "26": {"name": "Schienen / Lore (Zombie-Kreislauf)", "color": "#fbbf24", "border": "#d97706", "glyph": "🛤️"},
    "27": {"name": "Braustand & Kessel (Heilung)", "color": "#a855f7", "border": "#7e22ce", "glyph": "🧪"},
    "28": {"name": "Roter Samtteppich / Läufer", "color": "#dc2626", "border": "#991b1b", "glyph": "🧶"},
    "29": {"name": "Kronleuchter / Hängeketten", "color": "#eab308", "border": "#a16207", "glyph": "✨"},
    "30": {"name": "Azaleen / Blumen / Hecken", "color": "#22c55e", "border": "#15803d", "glyph": "🌸"},
    "31": {"name": "Schornsteinrauch / Lagerfeuer", "color": "#e2e8f0", "border": "#94a3b8", "glyph": "💨"}
}

def empty_grid():
    return [[0 for _ in range(W)] for _ in range(D)]

def set_rect(grid, x1, z1, x2, z2, bId):
    for z in range(max(0, z1), min(D, z2 + 1)):
        for x in range(max(0, x1), min(W, x2 + 1)):
            grid[z][x] = bId

def outline_rect(grid, x1, z1, x2, z2, bId):
    for x in range(max(0, x1), min(W, x2 + 1)):
        if 0 <= z1 < D: grid[z1][x] = bId
        if 0 <= z2 < D: grid[z2][x] = bId
    for z in range(max(0, z1), min(D, z2 + 1)):
        if 0 <= x1 < W: grid[z][x1] = bId
        if 0 <= x2 < W: grid[z][x2] = bId

def draw_bay_facets(grid, bId, is_left=True):
    # Octagonal bay projection centered at x=12 (left) or x=57 (right)
    # Front reaches z=46, sides reach z=38
    cx = 12 if is_left else 57
    fz = 46
    # Front flat
    for x in range(cx - 3, cx + 4):
        grid[fz][x] = bId
    # Diagonals
    grid[fz - 1][cx - 4] = bId
    grid[fz - 1][cx - 5] = bId
    grid[fz - 2][cx - 6] = bId
    grid[fz - 3][cx - 6] = bId
    grid[fz - 1][cx + 4] = bId
    grid[fz - 1][cx + 5] = bId
    grid[fz - 2][cx + 6] = bId
    grid[fz - 3][cx + 6] = bId
    # Side walls connecting back to main wall z=38
    for z in range(38, fz - 3):
        grid[z][cx - 6] = bId
        grid[z][cx + 6] = bId

def fill_bay_interior(grid, bId, is_left=True):
    cx = 12 if is_left else 57
    fz = 46
    for z in range(38, fz):
        w_offset = 6
        if z == fz - 1: w_offset = 3
        elif z == fz - 2: w_offset = 5
        for x in range(cx - w_offset, cx + w_offset + 1):
            grid[z][x] = bId

# Generate All 36 Layers
layers = []

def make_layer(layer_id, name, cat, y_str, rel_y, desc, milestones, grid):
    counts = {}
    for r in grid:
        for val in r:
            if val != 0:
                sval = str(val)
                counts[sval] = counts.get(sval, 0) + 1
    return {
        "id": layer_id,
        "name": name,
        "category": cat,
        "yLevel": y_str,
        "relativeY": rel_y,
        "description": desc,
        "keyFeatures": milestones,
        "counts": counts,
        "grid": grid
    }

# --- 1. KELLER 3: KLIPPEN-LOUNGE (Y=105 to 110) ---
# Dim: x: 18..51 (34 wide), z: 6..28 (23 deep)
for y, idx, name, desc in [
    (105, 0, "K3: Klippen-Fundament & Lounge-Estrich", "Solide Bruchstein- und Tiefenschiefer-Fundamente, tief in die Klippenwand geschlagen. Klippenbalkon ragt frei über den Abgrund."),
    (106, 1, "K3: Lounge-Boden & Seelenfeuer-Kamin", "Polierter Tiefenschieferboden mit Fichtenholzeinlegern. Seelenfeuer-Kaminbasis und Bartresen-Fundament."),
    (107, 2, "K3: Klippenbalkon-Brüstung & Bar-Tresen", "Eichenholz-Tresen mit Fässern und Brauständen. Freitragender Balkon mit Glasboden über der 60-Block-Schlucht."),
    (108, 3, "K3: Panorama-Glasfront & Sitzecke", "Zweistöckige Fensterfront aus getöntem Glas mit Blick auf das Sonnenuntergangs-Tal. Leder-Sofas und Bücherregale."),
    (109, 4, "K3: Kaminabzug & Galerieansatz", "Massiver Ziegelkaminzug nach oben. Hängeketten mit Seelaternen für stimmungsvolle Lounge-Beleuchtung."),
    (110, 5, "K3: Tonnengewölbe & Klippendecke", "Romantisches Ziegelgewölbe mit Fichtenholzbalken schließt Keller 3 nach oben hin ab.")
]:
    g = empty_grid()
    if y == 105:
        set_rect(g, 18, 12, 51, 28, 8)  # Deepslate foundation
        set_rect(g, 22, 6, 47, 11, 15)  # Balcony stone support piers
    elif y == 106:
        set_rect(g, 18, 12, 51, 28, 8)
        set_rect(g, 20, 14, 49, 26, 13) # Spruce floor
        set_rect(g, 22, 6, 47, 11, 11)  # Glass balcony floor!
        set_rect(g, 33, 26, 36, 27, 21) # Soul fire fireplace
        set_rect(g, 42, 16, 47, 16, 14) # Bar counter
        g[20][35] = 17 # Secret emergency water elevator up
    elif y == 107:
        outline_rect(g, 18, 12, 51, 28, 1) # Brick walls
        set_rect(g, 22, 6, 47, 6, 19)  # Iron bars balcony railing
        set_rect(g, 22, 6, 22, 11, 19)
        set_rect(g, 47, 6, 47, 11, 19)
        set_rect(g, 33, 26, 36, 27, 21) # Soul fire
        set_rect(g, 42, 16, 47, 16, 14) # Dark oak bar
        set_rect(g, 43, 15, 46, 15, 24) # Barrels behind bar
        set_rect(g, 23, 22, 28, 25, 22) # Lounge bookshelves
        g[20][35] = 17
    elif y == 108:
        outline_rect(g, 18, 12, 51, 28, 1)
        set_rect(g, 22, 12, 47, 12, 11) # Panoramic tinted glass window wall!
        set_rect(g, 33, 26, 36, 27, 1)  # Chimney flue
        set_rect(g, 42, 16, 47, 16, 27) # Brewing stands on bar
        g[20][35] = 17
    elif y == 109:
        outline_rect(g, 18, 12, 51, 28, 1)
        set_rect(g, 22, 12, 47, 12, 11) # Glass wall upper tier
        set_rect(g, 33, 26, 36, 27, 1)
        for cx in [25, 35, 44]:
            g[18][cx] = 23 # Lanterns
        g[20][35] = 17
    elif y == 110:
        set_rect(g, 18, 12, 51, 28, 1) # Vaulted brick ceiling
        set_rect(g, 21, 14, 48, 26, 13) # Ceiling beams
        set_rect(g, 33, 26, 36, 27, 1)
        g[20][35] = 17
    
    milestones = [
        f"Klippen-Fundamente bei X: -644 bis -611 verankern",
        f"Freitragenden Glasbalkon bei Z: 771 bis 776 über der Schlucht montieren",
        f"Seelenfeuer-Kamin bei X: -629 und Bartresen errichten"
    ]
    layers.append(make_layer(idx, name, "Keller 3 (Klippen-Lounge)", f"Y = {y}", f"-{126-y} (unter EG)", desc, milestones, g))

# --- 2. KELLER 2: VILLAGER-DUNGEON ("FOLTERKELLER", Y=114 to 119) ---
# Dim: x: 16..53 (38 wide), z: 12..38 (27 deep)
# Central corridor x: 32..37. Left cells x: 20..27, Right cells x: 42..49.
for y, idx, name, desc in [
    (114, 6, "K2: Dungeon-Fundament & Zombie-Gleisbett", "Bruchsteinfundament mit eingelassener Redstone-Schienenstrecke für die Zombie-Lore hinter den Zellen."),
    (115, 7, "K2: 16 Handelszellen & Piston-Schächte", "Klebrige Kolben senken Villager um 1 Block ab, damit der Zombie sie auf 'Schwer' zu 100% infiziert."),
    (116, 8, "K2: Pulttische, Zombie-Tunnel & Curing-Station", "Arbeitsstationen (Lecterns) für Mending-Handel. Zombie-Schienenkreislauf hinter den Falltüren."),
    (117, 9, "K2: Eisengitter, Braustände & Schalthebel", "Isoliergitter und Schalter zur gezielten Auslösung einzelner Zellen. Automatischer Trank-Werfer an der Decke."),
    (118, 10, "K2: Bogenstürze & 4 Expansions-Portale", "Gewölbte Bogentore nach Norden (Mine), Süden (Nether), Osten (Bunker) und Westen (Farmen)."),
    (119, 11, "K2: Ziegel-Kreuzgewölbe & Notausgang", "Massive Tonnendecke mit Seelaternen und Zugangstreppe zum Kupferlager.")
]:
    g = empty_grid()
    if y == 114:
        set_rect(g, 16, 12, 53, 38, 8)  # Deepslate floor
        # Rails loop for zombie
        for z in range(16, 35):
            g[z][19] = 26 # Left rail line behind cells
            g[z][50] = 26 # Right rail line behind cells
        for x in range(19, 51):
            g[15][x] = 26
            g[35][x] = 26
        g[20][35] = 17 # Water elevator
    elif y == 115:
        outline_rect(g, 16, 12, 53, 38, 8)
        # Corridor floor
        set_rect(g, 32, 14, 37, 36, 16) # Polished diorite central walk
        # Sticky pistons under villager holding spots
        for z in [17, 19, 21, 23, 26, 28, 30, 32]:
            g[z][23] = 20 # Left cell pistons
            g[z][46] = 20 # Right cell pistons
            # Cell walls
            set_rect(g, 20, z-1, 26, z-1, 8)
            set_rect(g, 43, z-1, 49, z-1, 8)
        g[20][35] = 17
    elif y == 116:
        outline_rect(g, 16, 12, 53, 38, 8)
        # Workstations & Villagers
        for z in [17, 19, 21, 23, 26, 28, 30, 32]:
            g[z][25] = 22 # Lectern (Pult)
            g[z][44] = 22 # Lectern
            g[z][21] = 19 # Trapdoor to zombie
            g[z][48] = 19 # Trapdoor to zombie
            set_rect(g, 20, z-1, 26, z-1, 8)
            set_rect(g, 43, z-1, 49, z-1, 8)
        # Curing station brewing stand at corridor end
        g[14][34] = 27
        g[14][35] = 27
        g[20][35] = 17
    elif y == 117:
        outline_rect(g, 16, 12, 53, 38, 8)
        for z in [17, 19, 21, 23, 26, 28, 30, 32]:
            g[z][26] = 19 # Iron bars front
            g[z][43] = 19
            g[z][27] = 20 # Lever on wall
            g[z][42] = 20 # Lever on wall
        g[20][35] = 17
    elif y == 118:
        outline_rect(g, 16, 12, 53, 38, 8)
        # 4 Portal archways
        set_rect(g, 33, 12, 36, 12, 6) # North portal
        set_rect(g, 33, 38, 36, 38, 6) # South portal
        set_rect(g, 16, 24, 16, 27, 6) # West portal
        set_rect(g, 53, 24, 53, 27, 6) # East portal
        # Ceiling lights
        for z in [16, 22, 28, 34]:
            g[z][34] = 23
            g[z][35] = 23
        g[20][35] = 17
    elif y == 119:
        set_rect(g, 16, 12, 53, 38, 1) # Vaulted brick ceiling
        set_rect(g, 32, 14, 37, 36, 13)
        g[20][35] = 17
    
    milestones = [
        f"Gleisstrecke für die Zombie-Lore hinter den 16 Zellen verlegen",
        f"Piston-Absenkung mit Hebeln und Eisengittern verdrahten",
        f"Braustation für Schwächetränke & Goldäpfel an der Stirnwand einrichten",
        f"4 Tunnel-Portale (N/S/O/W) für zukünftige Minen ausstatten"
    ]
    layers.append(make_layer(idx, name, "Keller 2 (Villager-Dungeon)", f"Y = {y}", f"-{126-y} (unter EG)", desc, milestones, g))

# --- 3. KELLER 1: KUPFER-LAGER & STASIS-TELEPORTER (Y=121 to 124) ---
# Dim: x: 14..55 (42 wide), z: 12..38 (27 deep)
# 4 aisles of double chests, center Stasis Chamber at x=35, z=25
for y, idx, name, desc in [
    (121, 12, "K1: Lager-Estrich & Stasis-Seelensand", "Fichtenholzboden mit Kupfergitter-Akzenten. Seelensand-Block für den Enderperlen-Stasis-Aufzug im Zentrum."),
    (122, 13, "K1: 96 Kisten, Trichterstraßen & Stasis-Wasser", "Erste Ebene der 96 Doppelkisten mit Trichtersortierung. Wasserquellblöcke im Stasisschacht."),
    (123, 14, "K1: Kistenreihe 2 & Relog-Falltür-Mechanik", "Zweite Kistenebene. Eisenfalltür über dem Stasisschacht, verbunden mit Observer- und Schneedruckplatten-Sensor."),
    (124, 15, "K1: Kupferlampen-Decke & Fichten-Trägerbalken", "Atmosphärische Steampunk-Kupferdecken mit Fichtenholztraversen und Wendeltreppen zum Erdgeschoss.")
]:
    g = empty_grid()
    if y == 121:
        set_rect(g, 14, 12, 55, 38, 13) # Spruce floor
        outline_rect(g, 14, 12, 55, 38, 1)
        # Copper grid runners
        for z in range(14, 37, 4):
            set_rect(g, 16, z, 53, z, 18)
        # Stasis soul sand center
        g[25][35] = 21 # Soul sand
        g[20][35] = 17 # Lift
    elif y == 122:
        outline_rect(g, 14, 12, 55, 38, 1)
        # 4 Double chest rows (left and right)
        for z in [15, 17, 19, 21, 28, 30, 32, 34]:
            set_rect(g, 17, z, 30, z, 24) # Left chest aisles
            set_rect(g, 39, z, 52, z, 24) # Right chest aisles
        # Stasis chamber walls & water
        outline_rect(g, 33, 23, 37, 27, 4) # Quartz surround
        g[25][35] = 25 # Ender pearl suspended in water!
        g[20][35] = 17
    elif y == 123:
        outline_rect(g, 14, 12, 55, 38, 1)
        for z in [15, 17, 19, 21, 28, 30, 32, 34]:
            set_rect(g, 17, z, 30, z, 24)
            set_rect(g, 39, z, 52, z, 24)
        outline_rect(g, 33, 23, 37, 27, 4)
        g[25][35] = 25
        # Redstone trigger for stasis trapdoor
        g[24][35] = 20
        g[20][35] = 17
    elif y == 124:
        set_rect(g, 14, 12, 55, 38, 1)
        # Copper bulbs & chandeliers
        for cx in [20, 27, 42, 49]:
            for cz in [17, 23, 30]:
                g[cz][cx] = 18 # Copper lamp
        # Stasis trapdoor
        g[25][35] = 19 # Iron trapdoor
        g[20][35] = 17
    
    milestones = [
        f"96 Doppelkisten in 4 Regalreihen mit Trichtersortierung aufstellen",
        f"Enderperlen-Stasiskammer bei X: -662, Y: 121..124, Z: 790 mit Seelensand füllen",
        f"Eisenfalltür mit Relog-/Observer-Schaltung und Panikhebel koppeln",
        f"Kupferlampen für warmes Steampunk-Licht verdrahten"
    ]
    layers.append(make_layer(idx, name, "Keller 1 (Kupfer-Lager)", f"Y = {y}", f"-{126-y} (unter EG)", desc, milestones, g))

# --- 4. FUNDAMENT & PLATEAUSOCKEL (Y=125) ---
g125 = empty_grid()
# Solid foundation under mansion footprint
set_rect(g125, 4, 14, 65, 38, 8) # Deepslate foundation
# Octagonal bay foundations
fill_bay_interior(g125, 8, is_left=True)
fill_bay_interior(g125, 8, is_left=False)
draw_bay_facets(g125, 8, is_left=True)
draw_bay_facets(g125, 8, is_left=False)
# Portico staircase foundation
set_rect(g125, 29, 41, 40, 48, 6) # Quartz stairs/blocks
# Infinity Pool cantilever foundation
set_rect(g125, 23, 3, 46, 13, 8)  # Deepslate supports over cliff
# Front roundabout driveway outline (Gravel/Paved)
outline_rect(g125, 20, 42, 49, 49, 15)
g125[20][35] = 17

layers.append(make_layer(16, "Fundament, Freitreppe & Pool-Stützen", "Fundament", "Y = 125", "-1 (Fundament)",
    "Massiver Sockel aus Tiefenschieferziegeln gleicht die Klippenkante aus. Freitreppe am Haupteingang und Strebepfeiler des Infinity-Pools.",
    [
        "Tiefenschiefer-Sockel exakt auf Höhe des Bergplateaus (Y=125) nivellieren",
        "Freitreppe am Portikus mit Quarzstufen (X: -668 bis -657) anlegen",
        "Trägerpfeiler für den Infinity-Pool über dem Klippenabgrund (Z: 768 bis 778) setzen"
    ], g125))

# --- 5. ERDGESCHOSS (EG, Y=126 to 132) ---
# Main Mansion Body: x: 6..63, z: 14..38
# Central Portico: x: 29..40, z: 38..46
# Octagonal Bays: left x: 6..18, z: 36..46; right x: 51..63, z: 36..46
# Rear Infinity Pool: x: 23..46, z: 3..14

# Y=126: EG Floor & Pool Basin
g126 = empty_grid()
# Ground floor flooring
set_rect(g126, 6, 14, 63, 38, 13) # Spruce parquet
# Foyer grand marble pattern
set_rect(g126, 28, 22, 41, 38, 16) # Polished diorite / quartz
# Octagonal bay floors
fill_bay_interior(g126, 13, is_left=True)
fill_bay_interior(g126, 13, is_left=False)
# Portico landing
set_rect(g126, 29, 39, 40, 45, 4) # Smooth quartz porch
# Infinity Pool basin
outline_rect(g126, 23, 3, 46, 13, 4) # Quartz pool rim
set_rect(g126, 25, 5, 44, 12, 17)    # Water basin!
set_rect(g126, 24, 3, 45, 3, 11)     # Glass rim on cliff edge!
g126[20][35] = 17

layers.append(make_layer(17, "EG 0: Prunkboden, Foyer-Marmor & Pool-Becken", "Erdgeschoss (EG)", "Y = 126", "EG (Plateau)",
    "Prachtvoller Foyer-Boden im Schachbrettmuster, Fichtenparkett in den Flügeln und das mit Seelaternen beleuchtete Infinity-Pool-Becken.",
    [
        "Foyer-Schachbrettmuster aus poliertem Diorit und Quarz (X: -669 bis -656) verlegen",
        "Infinity-Pool mit 1 Block Wassertiefe und Glasabschlusskante zur Schlucht füllen",
        "Portikus-Vorplatz mit glatten Quarzquadern pflastern"
    ], g126))

# Helper to lay standard mansion walls
def build_mansion_walls(g, wall_id, quoin_id, col_id):
    # Main outer walls
    set_rect(g, 6, 14, 63, 14, wall_id)  # Rear wall
    set_rect(g, 6, 14, 6, 38, wall_id)   # Left wall
    set_rect(g, 63, 14, 63, 38, wall_id) # Right wall
    set_rect(g, 18, 38, 29, 38, wall_id) # Front left recessed wall
    set_rect(g, 40, 38, 51, 38, wall_id) # Front right recessed wall
    # Octagonal bays
    draw_bay_facets(g, wall_id, is_left=True)
    draw_bay_facets(g, wall_id, is_left=False)
    # Quoins on corners
    for (qx, qz) in [(6, 14), (63, 14), (6, 38), (63, 38), (18, 38), (51, 38), (29, 38), (40, 38)]:
        g[qz][qx] = quoin_id
    # Portico columns (2x2 twin pillars)
    set_rect(g, 29, 44, 30, 45, col_id)
    set_rect(g, 39, 44, 40, 45, col_id)

# Y=127: EG Walls 1 (Bases & Quoins)
g127 = empty_grid()
build_mansion_walls(g127, 1, 4, 5)
# Entrance doorway opening
g127[38][34] = 14 # Dark oak double door
g127[38][35] = 14
# Fireplace base in salon
set_rect(g127, 8, 24, 10, 28, 8)
g127[26][9] = 21 # Fireplace fire
# Pool terrace perimeter railing
outline_rect(g127, 23, 3, 46, 13, 7) # Quartz low railing
set_rect(g127, 24, 4, 45, 12, 0)
layers.append(make_layer(18, "EG 1: Außenwände, Quarz-Eckquader & Portikus-Säulen", "Erdgeschoss (EG)", "Y = 127", "+1",
    "Ziegelaußenwände mit markanten Quarz-Eckquadern. Die Zwillingssäulen des monumentalen Portikus beginnen.",
    [
        "Quarz-Eckquader an allen 8 Haupt-Gebäudeecken setzen",
        "2x2 Quarzsäulen des Portikus (X: -668 und -657) aufstellen",
        "Dunkle Eichentüren am Haupteingang und Kaminbasis im Salon errichten"
    ], g127))

# Y=128: EG Walls 2 (Windows sills)
g128 = empty_grid()
build_mansion_walls(g128, 1, 4, 5)
# Window openings with Quartz Sills
# Bay front windows: cx-2, cx, cx+2
for cx in [12, 57]:
    g128[46][cx-2] = 4
    g128[46][cx] = 4
    g128[46][cx+2] = 4
# Recessed bay windows
for wx in [22, 26, 43, 47]:
    g128[38][wx] = 4
# Side windows
for wz in [20, 26, 32]:
    g128[wz][6] = 4
    g128[wz][63] = 4
# Rear windows / pool doors
for wx in [12, 16, 53, 57]:
    g128[14][wx] = 4
set_rect(g128, 33, 14, 36, 14, 14) # Double terrace doors to pool
layers.append(make_layer(19, "EG 2: Fenster-Brüstungen & Kaminfeuer", "Erdgeschoss (EG)", "Y = 128", "+2",
    "Präzise Quarz-Fensterbänke für die hohen Viktorianischen Schiebefenster in den Erkern und Seitenwänden.",
    [
        "Quarz-Fensterbänke an den Erkern (je 3 Fenster pro Erker) einsetzen",
        "Große Panoramafenster in den Seitenflügeln vorbereiten",
        "Terrassentüren zum Infinity-Pool einbauen"
    ], g128))

# Y=129: EG Walls 3 (Tall Glazing)
g129 = empty_grid()
build_mansion_walls(g129, 1, 4, 5)
# Glazing with Tinted Glass & White Panes
for cx in [12, 57]:
    g129[46][cx-2] = 12
    g129[46][cx] = 12
    g129[46][cx+2] = 12
for wx in [22, 26, 43, 47]:
    g129[38][wx] = 12
for wz in [20, 26, 32]:
    g129[wz][6] = 12
    g129[wz][63] = 12
for wx in [12, 16, 53, 57]:
    g129[14][wx] = 12
# Imperial double staircase begins in foyer
set_rect(g129, 31, 26, 33, 27, 6) # Left sweep
set_rect(g129, 36, 26, 38, 27, 6) # Right sweep
layers.append(make_layer(20, "EG 3: Hohe Bogenfenster, Doppelflügeltür & Salon", "Erdgeschoss (EG)", "Y = 129", "+3",
    "Erhöhung der Fensterverglasung. Im Foyer beginnt der Schwung der prachtvollen zweiläufigen Kaisertreppe.",
    [
        "Weiße Glasscheiben in alle Erker- und Fassadenfenster einsetzen",
        "Kaisertreppe aus Quarzstufen im Foyer beginnen",
        "Kamin im Salon und Esszimmer-Kronleuchter-Halterungen befestigen"
    ], g129))

# Y=130: EG Walls 4 (Lintels & Archways)
g130 = empty_grid()
build_mansion_walls(g130, 1, 4, 5)
# Window lintels in Quartz
for cx in [12, 57]:
    g130[46][cx-2] = 6
    g130[46][cx] = 6
    g130[46][cx+2] = 6
for wx in [22, 26, 43, 47]:
    g130[38][wx] = 6
# Portico archway connects pillars
set_rect(g130, 29, 44, 40, 45, 6) # Arch lintel between twin columns
# Staircase landing
set_rect(g130, 31, 24, 38, 25, 4)
layers.append(make_layer(21, "EG 4: Bogenstürze, Portikus-Gewölbe & Kaisertreppe", "Erdgeschoss (EG)", "Y = 130", "+4",
    "Quarz-Bogenstürze schließen die Fenster ab. Der Eingangsbogen verbindet die vier Kolossalsäulen des Portikus.",
    [
        "Quarztreppen als profilierte Bogenstürze über allen Fenstern anbringen",
        "Portikus-Bogensturz zwischen den Säulenpaaren spannen",
        "Zwischenpodest der Kaisertreppe im Foyer ausbauen"
    ], g130))

# Y=131: EG Walls 5 (Upper Foyer & Chandeliers)
g131 = empty_grid()
build_mansion_walls(g131, 1, 4, 1) # Solid brick top before ceiling
# Staircase reaches 1st floor level
set_rect(g131, 30, 22, 32, 23, 6)
set_rect(g131, 37, 22, 39, 23, 6)
# Grand chandelier hanging point
g131[30][35] = 29
layers.append(make_layer(22, "EG 5: Foyer-Doppeltreppe & Prunk-Kronleuchter", "Erdgeschoss (EG)", "Y = 131", "+5",
    "Die Kaisertreppe erreicht die obere Galerie. Über dem Foyer wird der goldene Kronleuchter an Hängeketten montiert.",
    [
        "Treppenläufe bis zur Deckenhöhe hochziehen",
        "Kronleuchter im Foyer und Salon montieren",
        "Wandkrone für das Geschossgesims vorbereiten"
    ], g131))

# Y=132: EG Ceiling & Belt Course (Geschossgesims)
g132 = empty_grid()
# Solid ceiling / 1st floor base
set_rect(g132, 6, 14, 63, 38, 13) # Spruce ceiling beams
# Foyer mezzanine opening (open to below!)
set_rect(g132, 30, 25, 39, 35, 0) # Grand opening
outline_rect(g132, 29, 24, 40, 36, 7) # Railing around opening
# Continuous white quartz belt course projecting 1 block outwards
outline_rect(g132, 5, 13, 64, 39, 7)
# Bay tower projecting belt courses
draw_bay_facets(g132, 7, is_left=True)
draw_bay_facets(g132, 7, is_left=False)
# Portico balcony floor
set_rect(g132, 29, 41, 40, 46, 4)
layers.append(make_layer(23, "EG 6: Geschossgesims, Deckenbalken & Mezzanin", "Erdgeschoss (EG)", "Y = 132", "+6",
    "Hervorspringendes Quarz-Geschossgesims trennt Erdgeschoss und Obergeschoss optisch ab. Großzügige Mezzanin-Galerieöffnung.",
    [
        "Umlaufendes Quarzgesims an der Außenfassade ringsherum anbringen",
        "Deckenbalken aus Fichtenholz einziehen",
        "Große Galerieöffnung im Foyer mit Schutzgeländer aussparen"
    ], g132))

# --- 6. 1. OBERGESCHOSS (1. OG, Y=133 to 138) ---
# Y=133: 1. OG Floor & Portico Balcony
g133 = empty_grid()
set_rect(g133, 6, 14, 63, 38, 13) # Parquet
fill_bay_interior(g133, 13, is_left=True)
fill_bay_interior(g133, 13, is_left=False)
set_rect(g133, 30, 25, 39, 35, 0) # Foyer void
outline_rect(g133, 29, 24, 40, 36, 7)
# Portico Balcony railing (Zinnen / Balustrade)
outline_rect(g133, 29, 41, 40, 46, 7)
set_rect(g133, 30, 42, 39, 45, 0)
layers.append(make_layer(24, "1. OG 0: Bodenplatte & Portikus-Sonnenterrasse", "1. Obergeschoss (1. OG)", "Y = 133", "+7",
    "Bodenbelag des ersten Stocks mit Aussichtsbalkon auf dem Portikus über dem Haupteingang.",
    [
        "Fichtenparkett im gesamten 1. Obergeschoss verlegen",
        "Portikus-Balkon mit Quarzstufen-Balustrade absichern",
        "Galerie-Geländer rund um das Foyer fertigstellen"
    ], g133))

# Y=134: 1. OG Walls 1
g134 = empty_grid()
build_mansion_walls(g134, 1, 4, 4)
# French doors to portico balcony
g134[38][34] = 14
g134[38][35] = 14
# Portico upper columns/pilasters
set_rect(g134, 29, 44, 30, 45, 5)
set_rect(g134, 39, 44, 40, 45, 5)
layers.append(make_layer(25, "1. OG 1: Schlafzimmer-Wände & Säulen", "1. Obergeschoss (1. OG)", "Y = 134", "+8",
    "Außen- und Innenwände der Luxus-Schlafsuiten, der Bibliothek und des Trophäensaals.",
    [
        "Ziegelwände des 1. OG mit Eckquadern aufmauern",
        "Flügeltüren zum Portikus-Balkon einsetzen",
        "Raumaufteilung der Master-Suite und Gästezimmer festlegen"
    ], g134))

# Y=135: 1. OG Windows
g135 = empty_grid()
build_mansion_walls(g135, 1, 4, 5)
for cx in [12, 57]:
    g135[46][cx-2] = 12
    g135[46][cx] = 12
    g135[46][cx+2] = 12
for wx in [22, 26, 43, 47]:
    g135[38][wx] = 12
for wz in [20, 26, 32]:
    g135[wz][6] = 12
    g135[wz][63] = 12
for wx in [12, 16, 53, 57]:
    g135[14][wx] = 12
# Master canopy bed (West wing)
set_rect(g135, 9, 20, 11, 23, 28)
layers.append(make_layer(26, "1. OG 2: Obere Erkerfenster & Balkontüren", "1. Obergeschoss (1. OG)", "Y = 135", "+9",
    "Obere Fensterreihen mit Aussicht auf das Bergmassiv. Himmelbett in der Master-Suite.",
    [
        "Erkerfenster im 1. OG mit Glasscheiben verglasen",
        "Master-Suite mit Prunk-Himmelbett und Kamin ausstatten",
        "Rote Läuferteppiche auf der Galerie auslegen"
    ], g135))

# Y=136: 1. OG Lintels
g136 = empty_grid()
build_mansion_walls(g136, 1, 4, 5)
for cx in [12, 57]:
    g136[46][cx-2] = 6
    g136[46][cx] = 6
    g136[46][cx+2] = 6
for wx in [22, 26, 43, 47]:
    g136[38][wx] = 6
# Portico upper arch
set_rect(g136, 29, 44, 40, 45, 6)
layers.append(make_layer(27, "1. OG 3: Fensterstürze, Bibliothek & Galerie", "1. Obergeschoss (1. OG)", "Y = 136", "+10",
    "Bogenstürze der oberen Etage. Oberer Rundbogen des Portikus.",
    [
        "Quarztreppen-Stürze über allen Fenstern anbringen",
        "Rundbogen über dem Portikus-Balkon schließen",
        "Bibliotheksregale bis unter die Decke hochziehen"
    ], g136))

# Y=137: 1. OG Portico Pediment Base (Dreiecksgiebel)
g137 = empty_grid()
build_mansion_walls(g137, 1, 4, 1)
# Classical triangular pediment over portico
set_rect(g137, 28, 43, 41, 45, 6) # Pediment bottom cornice
g137[44][34] = 4 # Coat of arms in center
g137[44][35] = 4
layers.append(make_layer(28, "1. OG 4: Portikus-Dreiecksgiebel & Wappen", "1. Obergeschoss (1. OG)", "Y = 137", "+11",
    "Klassischer Dreiecksgiebel über dem Portikus mit zentralem Familienwappen in Calcit/Quarz.",
    [
        "Basis des Dreiecksgiebels über dem Portikus errichten",
        "Familienwappen / Uhrwerk in weißem Quarz einarbeiten",
        "Wandkrone für das Hauptdach vorbereiten"
    ], g137))

# Y=138: 1. OG Cornice (Konsolengesims / Zahnfries)
g138 = empty_grid()
# Major roof overhang cornice in Quartz
outline_rect(g138, 4, 12, 65, 40, 6) # Massive quartz dentil cornice
draw_bay_facets(g138, 6, is_left=True)
draw_bay_facets(g138, 6, is_left=False)
# Pediment peak
set_rect(g138, 32, 44, 37, 44, 6)
g138[44][34] = 7
g138[44][35] = 7
# Attic floor
set_rect(g138, 6, 14, 63, 38, 13)
layers.append(make_layer(29, "1. OG 5: Konsolengesims (Zahnfries) & Deckenabschluss", "1. Obergeschoss (1. OG)", "Y = 138", "+12",
    "Mächtiges Konsolengesims (Zahnfries) aus Quarztreppen ragt rundherum um 1 Block hervor und trägt das Walmdach.",
    [
        "Profilierte Quarztreppen ringsherum als Konsolengesims anbringen",
        "Dreiecksgiebel des Portikus an der Spitze vollenden",
        "Dachgeschossboden aus Fichtenbrettern schließen"
    ], g138))

# --- 7. DACHGESCHOSS, GAUBEN & DACHKAMM (Y=139 to 148) ---
# Y=139: Dach 1 (Eaves / Traufe)
g139 = empty_grid()
# Outer roof eaves in Deepslate Stairs
outline_rect(g139, 3, 11, 66, 41, 9)
draw_bay_facets(g139, 9, is_left=True)
draw_bay_facets(g139, 9, is_left=False)
layers.append(make_layer(30, "Dach 1: Traufe & Tiefenschiefer-Dachüberstand", "Dachgeschoss", "Y = 139", "+13",
    "Erste Reihe der Tiefenschiefer-Dachtreppen bildet die weit ausladende Traufe über dem Konsolengesims.",
    [
        "Umlaufende Traufe aus Tiefenschiefer-Treppen setzen",
        "Traufkanten an den polygonalen Erkerdächern exakt anschrägen",
        "Dachrinnen-Linie kontrollieren"
    ], g139))

# Y=140: Dach 2 (Slope 1 & 4 Dormer Sills)
g140 = empty_grid()
outline_rect(g140, 5, 13, 64, 39, 9)
# 4 Roof Dormers (Dachgauben) Sills: 2 Front, 2 Sides
# Front dormers: x: 22..25 and x: 44..47 at z: 39
set_rect(g140, 22, 39, 25, 39, 4)
set_rect(g140, 44, 39, 47, 39, 4)
# Side dormers: z: 24..27 at x: 5 and x: 64
set_rect(g140, 5, 24, 5, 27, 4)
set_rect(g140, 64, 24, 64, 27, 4)
# Chimney shafts begin
set_rect(g140, 14, 24, 16, 26, 1) # Left brick chimney
set_rect(g140, 53, 24, 55, 26, 1) # Right brick chimney
layers.append(make_layer(31, "Dach 2: Steile Walmdach-Schräge & 4 Gauben-Schwellen", "Dachgeschoss", "Y = 140", "+14",
    "Steilanstieg des Schieferdaches. Weiße Quarzschwellen für die 4 markanten Dachgauben.",
    [
        "Zweite Dachtreppenreihe nach innen versetzt hochziehen",
        "4 Gauben-Schwellen (2 Front, 2 Seiten) aus Quarz einpassen",
        "Die zwei Ziegelschornsteine aus dem Dach emporwachsen lassen"
    ], g140))

# Y=141: Dach 3 (Slope 2 & Dormer Windows)
g141 = empty_grid()
outline_rect(g141, 7, 15, 62, 37, 9)
# Dormer windows
g141[38][23] = 12
g141[38][24] = 12
g141[38][45] = 12
g141[38][46] = 12
g141[25][6] = 12
g141[26][6] = 12
g141[25][63] = 12
g141[26][63] = 12
# Chimneys
set_rect(g141, 14, 24, 16, 26, 1)
set_rect(g141, 53, 24, 55, 26, 1)
layers.append(make_layer(32, "Dach 3: Gauben-Fenster & Ziegelschornsteine", "Dachgeschoss", "Y = 141", "+15",
    "Gaubenfenster mit Glasscheiben und Ziegelwangen. Die beiden monumentalen Kamine steigen weiter an.",
    [
        "Glasfenster in alle 4 Gauben einsetzen",
        "Dachneigung gleichmäßig an den Ecken verjüngen",
        "Kaminzüge massiv mit Ziegeln hochmauern"
    ], g141))

# Y=142: Dach 4 (Slope 3 & Dormer Pediments)
g142 = empty_grid()
outline_rect(g142, 9, 17, 60, 35, 9)
# Dormer miniature gables (Quarztreppen)
set_rect(g142, 22, 38, 25, 38, 6)
set_rect(g142, 44, 38, 47, 38, 6)
set_rect(g142, 6, 24, 6, 27, 6)
set_rect(g142, 63, 24, 63, 27, 6)
# Chimneys
set_rect(g142, 14, 24, 16, 26, 1)
set_rect(g142, 53, 24, 55, 26, 1)
layers.append(make_layer(33, "Dach 4: Gaubengiebel & Zwillingskamine", "Dachgeschoss", "Y = 142", "+16",
    "Spitze Quarzgiebel krönen die Gauben. Schornsteine durchbrechen die Dachfläche.",
    [
        "Ziergiebel über den 4 Dachgauben aufsetzen",
        "Vierte Stufe des Walmdaches schließen",
        "Kamine weiterführen"
    ], g142))

# Y=143: Dach 5 (Slope 4)
g143 = empty_grid()
outline_rect(g143, 11, 19, 58, 33, 9)
set_rect(g143, 14, 24, 16, 26, 1)
set_rect(g143, 53, 24, 55, 26, 1)
layers.append(make_layer(34, "Dach 5: Obere Dachschräge & Gaubenspitzen", "Dachgeschoss", "Y = 143", "+17",
    "Fünfte Stufe des Steildaches führt zur zentralen Dachterrasse hinauf.",
    [
        "Obere Dachstufe mit Tiefenschiefertreppen schließen",
        "Gaubendächer nahtlos in die Hauptdachfläche übergehen lassen"
    ], g143))

# Y=144: Dach 6 (Roof plateau transition)
g144 = empty_grid()
outline_rect(g144, 13, 21, 56, 31, 9)
set_rect(g144, 14, 24, 16, 26, 1)
set_rect(g144, 53, 24, 55, 26, 1)
layers.append(make_layer(35, "Dach 6: Dachplateau-Einfassung", "Dachgeschoss", "Y = 144", "+18",
    "Abschluss der Schrägen und Übergang zur flachen Dach-Aussichtsplattform (Widow's Walk).",
    [
        "Letzte Dachtreppenstufe zur Plattform hin verlegen",
        "Kamine für den Kopfschmuck vorbereiten"
    ], g144))

# Y=145: Dachplateau & Quarz-Zinnen (Widow's Walk)
g145 = empty_grid()
# High roof observation deck (Polished Deepslate)
set_rect(g145, 15, 22, 54, 30, 8)
# White quartz rooftop cresting / balustrade (Quarz-Zinnen)
outline_rect(g145, 15, 22, 54, 30, 7)
# Alternating cresting spikes
for x in range(16, 54, 2):
    g145[22][x] = 4
    g145[30][x] = 4
for z in range(23, 30, 2):
    g145[z][15] = 4
    g145[z][54] = 4
# Chimneys with Campfires for smoke
set_rect(g145, 14, 24, 16, 26, 1)
g145[25][15] = 31 # Campfire smoke left!
set_rect(g145, 53, 24, 55, 26, 1)
g145[25][54] = 31 # Campfire smoke right!
layers.append(make_layer(36, "Dach 7: Dachplateau, Quarz-Zinnen & Kaminrauch", "Dachfirst & Kamine", "Y = 145", "+19 (First)",
    "Die Krönung des Herrenhauses: Viktorianischer Dachkamm (Cresting) mit weißen Zinnen und rauchende Schornsteine.",
    [
        "Flache Aussichtsplattform aus poliertem Tiefenschiefer pflastern",
        "Viktorianischen Dachkamm (Zinnen) aus Quarzstufen und Quarzblöcken aufstellen",
        "Lagerfeuer in den Schornsteinköpfen platzieren, damit dauerhaft Rauch aufsteigt"
    ], g145))

# Export to data.js
data_export = {
    "dimensions": {
        "width": W,
        "depth": D,
        "layerCount": len(layers),
        "heightBlocks": 46,
        "anchor": {"x": -662, "y": 126, "z": 790, "seed": "-4815224116428668341"}
    },
    "palette": PALETTE,
    "layers": layers
}

print(f"Generated {len(layers)} layers successfully!")
print("Checking material totals...")
total_blocks = {}
for l in layers:
    for bId, count in l["counts"].items():
        total_blocks[bId] = total_blocks.get(bId, 0) + count

print("Top materials:")
for bId, count in sorted(total_blocks.items(), key=lambda x: x[1], reverse=True)[:8]:
    print(f"  {PALETTE[bId]['name']}: {count} blocks")
