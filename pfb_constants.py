"""Konstanten: Regler-Grenzen, Rechengrenzen, feste Annahmen, Farben und Presets."""

N_MIN, N_MAX, DEFAULT_N = 8, 120, 40                    # Knoten; Smallest-Last und DSATUR O(n^2), Heawood und Kempe-Reduktion bis n = 120 in Millisekunden
DENSITY_MIN, DENSITY_MAX, DEFAULT_DENSITY = 30, 100, 100  # Kanten in Prozent der Höchstzahl 3n − 6 planarer Graphen (Euler-Schranke)
SEED_MAX, DEFAULT_SEED = 999999, 7000
SWEEP_SEEDS = tuple(range(7000, 7020))                  # feste Instanzen für alle Messreihen (20): nie ein einzelner Seed als Befund

NET_TYPES = {"delaunay": "Karte (Delaunay-Netz aus Standorten)", "grid": "Raster (Gitter mit Diagonalen)"}
DEFAULT_NET = "delaunay"
NET_HELP = (
    "Beide Netztypen sind planar und geradlinig gezeichnet; die Kantenzahl ist die Dichte in Prozent von 3n − 6. "
    "Karte: zufällige Standorte, die Kanten sind Kanten ihrer Delaunay-Triangulierung, zufällig verdünnt. "
    "Raster: zuerst Gitterkanten, dann eine Diagonale je Zelle; ein vollständiges Raster mit Diagonalen lässt sich mit drei Farben färben."
)
DENSITY_LABEL = "Dichte (% von 3n − 6 Kanten)"

# Verfahren
METHODS = {
    "greedy": "Greedy (Smallest-Last-Reihenfolge)",
    "dsatur": "DSATUR",
    "heawood": "Heawood (höchstens 5 Farben)",
    "kempe": "Heawood + Kempe-Reduktion (auf 4 Farben)",
}
DEFAULT_METHOD = "kempe"
METHOD_HELP = (
    "Greedy: färbt in der umgekehrten Smallest-Last-Reihenfolge jeden Knoten mit der kleinsten freien Farbe. DSATUR: wählt stets den Knoten mit den meisten verschiedenen Nachbarfarben. "
    "Heawood: entfernt Knoten vom Grad höchstens 5, färbt den Rest und tauscht bei fünf verschiedenen Nachbarfarben eine Kempe-Kette (garantiert höchstens 5 Farben). "
    "Kempe-Reduktion: tauscht danach Ketten, bis die fünfte Farbe verschwindet."
)

# Rechengrenzen
EXACT_BUDGET = 100_000       # Verzweigungsknoten der exakten Entscheidung „k-färbbar?“ je Instanz (danach: unentschieden, nie „nein“)
KEMPE_ROUNDS = 30            # Durchläufe der Kempe-Reduktion über die Knoten mit fünfter Farbe
HAND_GRAPHS = ("Ikosaeder", "Oktaeder", "K4", "K5 minus eine Kante", "K5", "Petersen-Graph")
DEFAULT_HAND = "Ikosaeder"

# Experimente
FOUR_NS = (30, 60, 100, 200, 300)
NEED_NS = (30, 100, 300)
ICOSAHEDRON_ORDERS = 30      # zufällige Reihenfolgen am Ikosaeder
EXACT_NS = (30, 60, 100, 200)
THREE_NS = (60, 100)
THREE_DENSITY = 55           # verdünnte Karten für die Frage „3-färbbar?“

# Farben (Index = Farbe; die letzte Farbe ist „noch nicht gefärbt“)
COLORS = ("#4c78a8", "#e0a030", "#2F6B65", "#c0504d", "#8c6bb1", "#6baed6", "#8c564b", "#bcbd22")
COLOR_NAMES = ("blau", "gelb", "grün", "rot", "violett", "hellblau", "braun", "oliv")
COLOR_NONE = "#cfd6dd"
COLOR_CHAIN = "#222222"
COLOR_EDGE = "rgba(150,150,150,0.45)"

PRESETS = {
    "Lehrbeispiel: eine Karte": {"net": "delaunay", "n": 40, "density": 100, "seed": 7000, "method": "kempe"},
    "DSATUR verpasst die Vier": {"net": "delaunay", "n": 100, "density": 100, "seed": 7001, "method": "dsatur"},
    "Kempe-Ketten holen sie zurück": {"net": "delaunay", "n": 100, "density": 100, "seed": 7001, "method": "kempe"},
    "Heawood: fünf Farben genügen": {"net": "delaunay", "n": 60, "density": 100, "seed": 7002, "method": "heawood"},
    "Raster mit Diagonalen": {"net": "grid", "n": 36, "density": 100, "seed": 7000, "method": "greedy"},
}
PRESET_HELP = {
    "Lehrbeispiel: eine Karte": "40 Standorte mit allen Kanten ihrer Delaunay-Triangulierung, gefärbt mit Heawood und anschließender Kempe-Reduktion. Mit dem Schrittregler lassen sich die Kempe-Ketten ansehen.",
    "DSATUR verpasst die Vier": "100 Standorte: DSATUR braucht fünf Farben, obwohl nach dem Vierfarbensatz vier genügen.",
    "Kempe-Ketten holen sie zurück": "Dieselbe Karte mit Heawood und Kempe-Reduktion: Die Ketten tauschen Farben, bis die fünfte Farbe verschwindet.",
    "Heawood: fünf Farben genügen": "Das Verfahren, das fünf Farben garantiert. Auf zufälligen Karten braucht es fast nie eine Kette; der Ikosaeder weiter unten zeigt, wann doch.",
    "Raster mit Diagonalen": "Ein Raster mit Diagonalen lässt sich schon mit drei Farben färben: als Instanz zu leicht, als Gegenprobe nützlich.",
}
