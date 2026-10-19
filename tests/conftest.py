"""Gemeinsame Fixtures: Mini-Graphen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pfb_algorithm as A  # noqa: E402


def complete(n):
    return [(u, v) for u in range(n) for v in range(u + 1, n)]


@pytest.fixture
def path5():
    """Pfad 0-1-2-3-4."""
    return A.adjacency(5, [(0, 1), (1, 2), (2, 3), (3, 4)])


@pytest.fixture
def k4():
    return A.adjacency(4, complete(4))


@pytest.fixture
def wheel5():
    """Rad: Rand 0-1-2-3-4 (Fünfeck), Nabe 5 mit allen fünf Randknoten verbunden; Lage: Fünfeck mit Knoten i bei Winkel 90 + 72 i Grad, Nabe in der Mitte."""
    import math

    adj = A.adjacency(6, [(i, (i + 1) % 5) for i in range(5)] + [(i, 5) for i in range(5)])
    pos = [(math.cos(math.radians(90 + 72 * i)), math.sin(math.radians(90 + 72 * i))) for i in range(5)] + [(0.0, 0.0)]
    return adj, pos
