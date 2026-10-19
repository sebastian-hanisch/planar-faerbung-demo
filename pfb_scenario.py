"""Szenario: planare Karten (Delaunay), Raster mit Diagonalen und Lehrbuch-Graphen, geradlinig gezeichnet.

Ein Graph ist eine Kantenliste über den Knoten 0 bis n − 1 (ungerichtet, einfach, jede Kante als (u, v) mit u < v) und eine Lage der Knoten. Das Heawood-Verfahren
nutzt die Lage, um die Nachbarn um einen Knoten in der Reihenfolge der Einbettung zu ordnen; das ist nur bei kreuzungsfrei gezeichneten Graphen richtig."""

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Instance:
    """n Knoten, Kanten (sortierte Paare), Lage der Knoten (x, y) und ein Name für die Anzeige."""

    n: int
    edges: tuple[tuple[int, int], ...]
    pos: tuple[tuple[float, float], ...]
    name: str = ""
    planar: bool = True          # kreuzungsfrei gezeichnet (nur dann darf Heawood laufen)

    @property
    def m(self) -> int:
        return len(self.edges)


def normalize_edges(edges) -> tuple[tuple[int, int], ...]:
    return tuple(sorted({(min(u, v), max(u, v)) for u, v in edges if u != v}))


def euler_bound(n: int) -> int:
    """Höchste Kantenzahl eines planaren einfachen Graphen mit n Knoten: 3n − 6 (ab n = 3; darunter alle Paare)."""
    return n * (n - 1) // 2 if n < 3 else 3 * n - 6


def target_edge_count(n: int, density: int) -> int:
    return max(0, round(density / 100 * euler_bound(n)))


def circle_layout(n: int) -> tuple[tuple[float, float], ...]:
    return tuple((round(math.cos(2 * math.pi * i / n), 4), round(math.sin(2 * math.pi * i / n), 4)) for i in range(n))


def _delaunay_edges(points: np.ndarray) -> list[tuple[int, int]]:
    from scipy.spatial import Delaunay

    found = set()
    for simplex in Delaunay(points).simplices:
        a, b, c = (int(x) for x in simplex)
        found.update({(min(a, b), max(a, b)), (min(b, c), max(b, c)), (min(a, c), max(a, c))})
    return sorted(found)


def _pick(rng, candidates: list, count: int) -> list:
    count = min(count, len(candidates))
    if count <= 0:
        return []
    chosen = rng.choice(len(candidates), size=count, replace=False)
    return [candidates[int(i)] for i in sorted(chosen)]


def make_delaunay(n: int, density: int, seed: int) -> Instance:
    """Zufällige Standorte im Einheitsquadrat, Kanten aus ihrer Delaunay-Triangulierung (verdünnt auf die Dichte)."""
    rng = np.random.default_rng(seed)
    points = rng.random((n, 2))
    kept = _pick(rng, _delaunay_edges(points), target_edge_count(n, density))
    pos = tuple((round(float(x), 4), round(float(y), 4)) for x, y in points)
    return Instance(n, normalize_edges(kept), pos, "Karte")


def grid_dimensions(n: int) -> tuple[int, int]:
    width = max(2, math.ceil(math.sqrt(n)))
    return width, math.ceil(n / width)


def make_grid(n: int, density: int, seed: int) -> Instance:
    """Raster: zuerst Gitterkanten, dann eine Diagonale je Zelle; zufällig verdünnt auf die Dichte."""
    rng = np.random.default_rng(seed)
    width, _ = grid_dimensions(n)
    lattice, diagonal = [], []
    for i in range(n):
        r, c = divmod(i, width)
        right = i + 1 if c + 1 < width and i + 1 < n else None
        below = i + width if i + width < n else None
        diag = i + width + 1 if c + 1 < width and i + width + 1 < n else None
        if right is not None:
            lattice.append((i, right))
        if below is not None:
            lattice.append((i, below))
        if diag is not None and right is not None and below is not None:
            diagonal.append((i, diag))
    want = target_edge_count(n, density)
    kept = _pick(rng, lattice, want) if want <= len(lattice) else lattice + _pick(rng, diagonal, want - len(lattice))
    pos = tuple((float(i % width), float(-(i // width))) for i in range(n))
    return Instance(n, normalize_edges(kept), pos, "Raster")


def make_instance(net: str, n: int, density: int, seed: int) -> Instance:
    """Deterministisch aus den Reglern: gleiche Eingabe, gleiche Instanz."""
    return {"delaunay": make_delaunay, "grid": make_grid}[net](n, density, seed)


# --- Lehrbuch-Graphen -----------------------------------------------------------------------------------------------------------------------

# Ikosaeder, planar gezeichnet (Tutte-Einbettung mit einem Dreieck als Außenfläche, 2026-10-19 gerechnet); alle zwölf Knoten haben Grad 5
ICOSAHEDRON_POS = (
    (0.0, 2.4), (-2.0785, -1.2), (-0.5669, -0.3273), (0.0, -0.2182), (0.5669, -0.3273), (2.0785, -1.2),
    (0.0, -0.6545), (0.0, 0.6545), (-0.5669, 0.3273), (-0.189, 0.1091), (0.189, 0.1091), (0.5669, 0.3273),
)
ICOSAHEDRON_EDGES = (
    (0, 1), (0, 5), (0, 7), (0, 8), (0, 11), (1, 2), (1, 5), (1, 6), (1, 8), (2, 3), (2, 6), (2, 8), (2, 9), (3, 4), (3, 6), (3, 9), (3, 10),
    (4, 5), (4, 6), (4, 10), (4, 11), (5, 6), (5, 11), (7, 8), (7, 9), (7, 10), (7, 11), (8, 9), (9, 10), (10, 11),
)


def _pentagon(radius: float, phase: float = 90.0) -> list[tuple[float, float]]:
    return [(round(radius * math.cos(math.radians(phase + 72 * i)), 4), round(radius * math.sin(math.radians(phase + 72 * i)), 4)) for i in range(5)]


def hand_graph(name: str) -> Instance:
    """Die Lehrbuch-Graphen; die planaren sind kreuzungsfrei gezeichnet, K5 und der Petersen-Graph (nichtplanar) in einer üblichen Lage."""
    if name == "Ikosaeder":
        return Instance(12, ICOSAHEDRON_EDGES, ICOSAHEDRON_POS, name, True)
    if name == "Oktaeder":
        pos = ((0.0, 1.4), (-1.2, -0.7), (1.2, -0.7), (0.0, -0.35), (0.45, 0.35), (-0.45, 0.35))
        edges = [(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (0, 4), (0, 5), (1, 3), (1, 5), (2, 3), (2, 4)]
        return Instance(6, normalize_edges(edges), pos, name, True)
    if name == "K4":
        pos = ((0.0, 1.3), (-1.2, -0.8), (1.2, -0.8), (0.0, 0.0))
        return Instance(4, normalize_edges([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]), pos, name, True)
    if name == "K5 minus eine Kante":
        pos = ((0.0, 1.3), (0.0, -0.45), (-1.2, -0.8), (1.2, -0.8), (0.0, 0.1))
        edges = [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
        return Instance(5, normalize_edges(edges), pos, name, True)
    if name == "K5":
        edges = [(u, v) for u in range(5) for v in range(u + 1, 5)]
        return Instance(5, normalize_edges(edges), circle_layout(5), name, False)
    if name == "Petersen-Graph":
        pos = tuple(_pentagon(1.4) + _pentagon(0.7))
        edges = [(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)] + [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
        return Instance(10, normalize_edges(edges), pos, name, False)
    raise ValueError(f"unbekannter Lehrbuch-Graph: {name}")
