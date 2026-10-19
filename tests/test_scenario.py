"""Szenario: Generatoren (Eigenschaften, Determinismus), Lehrbuch-Graphen und ihre Zeichnungen."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

import pfb_algorithm as A
import pfb_constants as C
import pfb_scenario as S

ROOT = Path(__file__).resolve().parent.parent


def _crossings(inst):
    """Zahl der Kreuzungen der Strecken in der Zeichnung (ohne gemeinsamen Endpunkt, Überlagerungen ausgenommen)."""
    def cross(p1, p2, q1, q2):
        rx, ry, sx, sy = p2[0] - p1[0], p2[1] - p1[1], q2[0] - q1[0], q2[1] - q1[1]
        den = rx * sy - ry * sx
        if den == 0:
            return False
        qpx, qpy = q1[0] - p1[0], q1[1] - p1[1]
        t, u = (qpx * sy - qpy * sx) / den, (qpx * ry - qpy * rx) / den
        return 1e-9 < t < 1 - 1e-9 and 1e-9 < u < 1 - 1e-9

    count = 0
    for i, (a, b) in enumerate(inst.edges):
        for c, d in inst.edges[i + 1:]:
            if len({a, b, c, d}) == 4 and cross(inst.pos[a], inst.pos[b], inst.pos[c], inst.pos[d]):
                count += 1
    return count


def test_target_edge_count_is_a_percentage_of_the_bound():
    assert S.target_edge_count(14, 100) == 36 and S.target_edge_count(14, 50) == 18 and S.euler_bound(2) == 1


def test_same_inputs_give_the_same_instance_and_other_seeds_differ():
    for net in C.NET_TYPES:
        a = S.make_instance(net, 25, 80, 4)
        assert a == S.make_instance(net, 25, 80, 4) and a != S.make_instance(net, 25, 80, 5)


@pytest.mark.parametrize("n", [8, 25, 60, 120])
@pytest.mark.parametrize("density", [30, 70, 100])
def test_maps_and_grids_are_planar_straight_line_drawings(n, density):
    for net in C.NET_TYPES:
        inst = S.make_instance(net, n, density, 3)
        assert inst.m <= S.euler_bound(n) and _crossings(inst) == 0 and list(inst.edges) == sorted(set(inst.edges)), (net, n, density)


def test_the_full_grid_with_diagonals_is_three_colourable():
    inst = S.make_instance("grid", 36, 100, 1)
    assert A.colorable_k(A.adjacency(inst.n, inst.edges), 3).status == "ja"


def test_grid_dimensions_and_a_partial_last_row():
    assert S.grid_dimensions(36) == (6, 6) and S.grid_dimensions(7) == (3, 3)
    inst = S.make_instance("grid", 7, 100, 1)
    assert inst.n == 7 and all(0 <= u < v < 7 for u, v in inst.edges) and _crossings(inst) == 0


def test_the_instance_does_not_depend_on_the_hash_seed():
    code = (
        "import sys; sys.path.insert(0, %r); import pfb_evaluation as ev; "
        "a = ev.analyse(ev.Settings('delaunay', 40, 100, 7001, 'kempe')); print(a.inst.edges, a.run.colors, a.run.chains)" % str(ROOT)
    )
    outputs = []
    for hash_seed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=hash_seed, PYTHONIOENCODING="utf-8")
        outputs.append(subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, check=True).stdout)
    assert outputs[0] == outputs[1] and outputs[0].strip()


EXPECTED = {"Ikosaeder": (12, 30, True), "Oktaeder": (6, 12, True), "K4": (4, 6, True), "K5 minus eine Kante": (5, 9, True), "K5": (5, 10, False), "Petersen-Graph": (10, 15, False)}


def test_the_textbook_graphs_have_the_documented_size_and_planarity_flag():
    assert set(EXPECTED) == set(C.HAND_GRAPHS)
    for name, (n, m, planar) in EXPECTED.items():
        g = S.hand_graph(name)
        assert (g.n, g.m, g.planar) == (n, m, planar), name
        if planar:
            assert _crossings(g) == 0, name                                  # kreuzungsfrei gezeichnet


def test_the_icosahedron_has_degree_five_everywhere_and_a_straight_line_drawing_with_proper_order():
    g = S.hand_graph("Ikosaeder")
    adj = A.adjacency(g.n, g.edges)
    assert {len(a) for a in adj} == {5}
    # jeder Knoten hat im Umlauf fünf Nachbarn, aufeinanderfolgende sind benachbart (Flächen sind Dreiecke)
    for v in range(g.n):
        around = A.neighbours_by_angle(g.pos, v, adj[v])
        assert all(around[(i + 1) % 5] in adj[around[i]] for i in range(5)), v


def test_unknown_textbook_graph_is_rejected():
    with pytest.raises(ValueError):
        S.hand_graph("Banane")
