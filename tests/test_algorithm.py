"""Einheiten des Kerns an Mini-Graphen, von Hand gerechnet (DEMO-PLAYBOOK §1b): eine Regel = ein Test."""

import math

import pytest

import pfb_algorithm as A


def test_violations_name_edges_with_equal_colours_and_ignore_uncoloured_vertices():
    adj = A.adjacency(3, [(0, 1), (1, 2)])
    assert A.violations(adj, [0, 1, 0]) == []
    assert A.violations(adj, [0, 0, 1]) == [(0, 1)]
    assert A.violations(adj, [-1, -1, 2]) == []               # zwei ungefärbte Nachbarn sind kein Verstoß


def test_color_count():
    assert A.color_count([]) == 0 and A.color_count([-1, -1]) == 0 and A.color_count([0, 2, 1]) == 3 and A.color_count([4]) == 5


def test_smallest_free():
    assert A.smallest_free(set()) == 0 and A.smallest_free({0, 1, 3}) == 2 and A.smallest_free({1}) == 0


def test_smallest_last_order_of_a_path_and_a_star(path5):
    """Pfad: immer ein Endknoten (kleinste Nummer bei Gleichstand). Stern mit Mitte 0: erst die Blätter, die Mitte vor dem letzten Blatt."""
    assert A.smallest_last_order(path5) == [0, 1, 2, 3, 4]
    star = A.adjacency(4, [(0, 1), (0, 2), (0, 3)])
    assert A.smallest_last_order(star) == [1, 2, 0, 3]


def test_greedy_colours_a_path_with_two_colours_in_the_given_order(path5):
    colors, events = A.greedy_color(path5, [0, 1, 2, 3, 4])
    assert colors == [0, 1, 0, 1, 0] and [e.kind for e in events] == ["color"] * 5 and events[2].assign == ((2, 0),)


def test_greedy_smallest_last_on_k4_uses_four_colours_in_reverse_order(k4):
    """Entfernungsreihenfolge 0, 1, 2, 3; gefärbt wird 3, 2, 1, 0 mit 0, 1, 2, 3."""
    colors, _ = A.greedy_smallest_last(k4)
    assert colors == [3, 2, 1, 0]


def test_dsatur_on_a_triangle_with_a_tail():
    """Dreieck 0-1-2 mit Schwanz 2-3: erst Knoten 2 (größter Grad) mit 0, dann Knoten 0 (Sättigung 1, kleinste Nummer) mit 1, Knoten 1 mit 2, Knoten 3 mit 1."""
    adj = A.adjacency(4, [(0, 1), (1, 2), (0, 2), (2, 3)])
    colors, events = A.dsatur(adj)
    assert colors == [1, 2, 0, 1] and [e.vertex for e in events] == [2, 0, 1, 3]


def test_kempe_chain_is_the_component_of_the_two_colours():
    adj = A.adjacency(5, [(0, 1), (1, 2), (2, 3), (3, 4)])
    colors = [0, 1, 2, 1, 0]
    assert A.kempe_chain(adj, colors, 0, 0, 1) == (0, 1)
    assert A.kempe_chain(adj, colors, 1, 0, 1) == (0, 1)
    assert A.kempe_chain(adj, colors, 3, 0, 1) == (3, 4)
    assert A.kempe_chain(adj, colors, 2, 2, 1) == (1, 2, 3)


def test_swap_chain_exchanges_the_two_colours_on_the_chain_only():
    colors = [0, 1, 2, 1, 0]
    assert A.swap_chain(colors, (0, 1), 0, 1) == [1, 0, 2, 1, 0]
    assert colors == [0, 1, 2, 1, 0]                           # Eingabe bleibt unverändert


def test_neighbours_are_ordered_by_angle():
    pos = {0: (0.0, 0.0), 1: (1.0, 0.0), 2: (0.0, 1.0), 3: (-1.0, 0.0), 4: (0.0, -1.0)}
    assert A.neighbours_by_angle(pos, 0, [1, 2, 3, 4]) == [4, 1, 2, 3]       # −90°, 0°, 90°, 180°


def test_heawood_takes_a_free_colour_when_one_exists(wheel5):
    adj, pos = wheel5
    colors = [0, 1, 2, 3, -1, -1]                                # Nabe hat vier gefärbte Nachbarn
    new, events, needed = A.heawood_step(adj, pos, colors, 5)
    assert new[5] == 4 and not needed and [e.kind for e in events] == ["color"]
    new, _, _ = A.heawood_step(adj, pos, colors, 5, choose="high")
    assert new[5] == 4                                           # einzige freie Farbe


def test_heawood_swaps_the_first_chain_that_does_not_connect(wheel5):
    """Rand mit fünf verschiedenen Farben; Umlauf um die Nabe: 2, 3, 4, 0, 1. Kette der Farben 2 und 4 ab Knoten 2 ist nur {2}: tauschen, Nabe bekommt Farbe 2."""
    adj, pos = wheel5
    colors = [0, 1, 2, 3, 4, -1]
    new, events, needed = A.heawood_step(adj, pos, colors, 5)
    assert needed and new[2] == 4 and new[5] == 2 and not A.violations(adj, new)
    assert [e.kind for e in events] == ["kempe", "color"] and events[0].chain == (2,) and events[0].pair == (2, 4) and events[0].assign == ((2, 4),)


def test_heawood_tries_the_next_pair_when_the_first_chain_connects():
    """Zwei Hilfsknoten 6 (Farbe 4) und 7 (Farbe 2) verbinden Knoten 2 und 4 über eine Kette 2-4-2-4: das erste Paar scheitert, das zweite (Knoten 3 und 0) klappt."""
    edges = [(i, (i + 1) % 5) for i in range(5)] + [(i, 5) for i in range(5)] + [(2, 6), (6, 7), (7, 4)]
    adj = A.adjacency(8, edges)
    pos = [(math.cos(math.radians(90 + 72 * i)), math.sin(math.radians(90 + 72 * i))) for i in range(5)] + [(0.0, 0.0), (-2.0, -2.0), (2.0, -2.0)]
    colors = [0, 1, 2, 3, 4, -1, 4, 2]
    assert A.violations(adj, colors) == []
    new, events, needed = A.heawood_step(adj, pos, colors, 5)
    assert needed and events[0].chain == (3,) and events[0].pair == (3, 0) and new[3] == 0 and new[5] == 3 and not A.violations(adj, new)


def test_heawood_gets_stuck_on_k6():
    """K6 ist nicht planar: alle Ketten verbinden, das Verfahren meldet es."""
    adj = A.adjacency(6, [(u, v) for u in range(6) for v in range(u + 1, 6)])
    pos = [(math.cos(2 * math.pi * i / 6), math.sin(2 * math.pi * i / 6)) for i in range(6)]
    with pytest.raises(A.HeawoodStuck):
        A.heawood_color(adj, pos)


def test_heawood_rejects_more_than_five_coloured_neighbours():
    adj = A.adjacency(7, [(0, k) for k in range(1, 7)])
    with pytest.raises(ValueError):
        A.heawood_step(adj, [(0.0, 0.0)] * 7, [-1, 0, 1, 2, 3, 4, 5], 0)


def test_heawood_colours_a_planar_graph_properly_with_at_most_five_colours(k4):
    pos = [(0.0, 1.3), (-1.2, -0.8), (1.2, -0.8), (0.0, 0.0)]
    r = A.heawood_color(k4, pos)
    assert not A.violations(k4, r.colors) and A.color_count(r.colors) == 4 and r.chains == 0 and r.needing == 0


def test_kempe_reduce_recolours_a_leaf_directly_when_a_colour_is_free():
    adj = A.adjacency(3, [(0, 1), (1, 2)])
    r = A.kempe_reduce(adj, [0, 1, 4], 4)
    assert r.colors == [0, 1, 0] and r.chains == 0 and r.remaining == 0 and r.success and [e.kind for e in r.events] == ["color"]


def test_kempe_reduce_swaps_one_chain_around_a_star():
    """Mitte 3 mit der fünften Farbe, Blätter 0, 1, 2 mit 0, 1, 2: Kette (0, 1) ab Blatt 0 ist {0}; getauscht hat Blatt 0 die Farbe 1, Farbe 0 ist frei."""
    adj = A.adjacency(4, [(3, 0), (3, 1), (3, 2)])
    r = A.kempe_reduce(adj, [0, 1, 2, 4], 4)
    assert r.colors == [1, 1, 2, 0] and r.chains == 1 and r.success and not A.violations(adj, r.colors)
    assert [e.kind for e in r.events] == ["kempe", "color"] and r.events[0].chain == (0,) and r.events[0].pair == (0, 1)


def test_kempe_reduce_cannot_help_on_k5():
    """K5 braucht fünf Farben: jede Kette verbindet alles, die Reduktion bleibt hängen und lässt die Färbung unverändert."""
    adj = A.adjacency(5, [(u, v) for u in range(5) for v in range(u + 1, 5)])
    r = A.kempe_reduce(adj, [0, 1, 2, 3, 4], 4)
    assert r.colors == [0, 1, 2, 3, 4] and r.remaining == 1 and not r.success and r.events == []


def test_exact_decision_on_small_graphs(k4):
    assert A.colorable_k(k4, 3).status == "nein" and A.colorable_k(k4, 4).status == "ja"
    r = A.colorable_k(k4, 4)
    assert not A.violations(k4, r.colors) and A.color_count(r.colors) == 4
    path = A.adjacency(4, [(0, 1), (1, 2), (2, 3)])
    assert A.colorable_k(path, 2).status == "ja" and A.colorable_k(path, 1).status == "nein"
    triangle = A.adjacency(3, [(0, 1), (1, 2), (0, 2)])
    assert A.colorable_k(triangle, 2).status == "nein"


def test_exact_decision_reports_undecided_at_the_end_of_the_budget_never_no():
    adj = A.adjacency(5, [(u, v) for u in range(5) for v in range(u + 1, 5)])
    r = A.colorable_k(adj, 4, budget=1)
    assert r.status == "unentschieden" and r.colors is None
    assert A.colorable_k(adj, 4, budget=10_000).status == "nein"


def test_replay_applies_the_events_in_order():
    adj = A.adjacency(4, [(3, 0), (3, 1), (3, 2)])
    r = A.kempe_reduce(adj, [0, 1, 2, 4], 4)
    assert A.replay(4, r.events, 0) == [-1, -1, -1, -1]
    assert A.replay(4, r.events, 1) == [1, -1, -1, -1]            # nach dem Tausch hat Blatt 0 die Farbe 1
    assert A.replay(4, r.events, 2) == [1, -1, -1, 0] and A.replay(4, r.events, 99) == [1, -1, -1, 0]


def test_color_count_with_a_single_colour_and_partial_colourings():
    assert A.color_count([0]) == 1 and A.color_count([0, 0]) == 1
    assert A.color_count([-1, 2]) == 3 and A.color_count([2, -1]) == 3        # ungefärbte Knoten zählen nicht, die größte Farbe entscheidet


def test_kempe_reduce_respects_the_number_of_rounds():
    adj = A.adjacency(4, [(3, 0), (3, 1), (3, 2)])
    assert A.kempe_reduce(adj, [0, 1, 2, 4], 4, rounds=1).success
    none = A.kempe_reduce(adj, [0, 1, 2, 4], 4, rounds=0)
    assert not none.success and none.remaining == 1 and none.colors == [0, 1, 2, 4]


def test_freeing_a_colour_needs_as_many_swaps_as_neighbours_carry_it():
    """Stern, Mitte mit der fünften Farbe, drei nicht benachbarte Blätter mit Farbe 0: drei Tausche (je Blatt eine Kette) und eine abschließende Prüfung, dann ist Farbe 0 frei."""
    adj = A.adjacency(4, [(3, 0), (3, 1), (3, 2)])
    r = A.kempe_reduce(adj, [0, 0, 0, 4], 4)
    assert r.success and r.colors == [1, 1, 1, 0] and r.chains == 3 and not A.violations(adj, r.colors)


def test_the_budget_counts_branching_nodes_inclusively():
    """Der leere Graph braucht genau einen Knoten: Budget 1 genügt, Budget 0 nicht."""
    empty = A.adjacency(0, [])
    assert A.colorable_k(empty, 1, budget=1).status == "ja" and A.colorable_k(empty, 1, budget=0).status == "unentschieden"
