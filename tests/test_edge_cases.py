"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): kleinste Graphen, Entartungen, Gleichstände, alle Ecken der Regler."""

import pytest

import pfb_algorithm as A
import pfb_constants as C
import pfb_evaluation as ev
import pfb_scenario as S


def test_empty_graph_and_single_vertex():
    adj = A.adjacency(0, [])
    assert A.smallest_last_order(adj) == [] and A.greedy_smallest_last(adj)[0] == [] and A.dsatur(adj)[0] == []
    one = A.adjacency(1, [])
    assert A.greedy_smallest_last(one)[0] == [0] and A.dsatur(one)[0] == [0] and A.heawood_color(one, [(0.0, 0.0)]).colors == [0]
    assert A.colorable_k(one, 1).status == "ja" and A.colorable_k(A.adjacency(0, []), 1).status == "ja"


def test_exactly_two_vertices_one_edge():
    """n = 2: der kleinste Fall, in dem zwei Farben nötig sind."""
    adj = A.adjacency(2, [(0, 1)])
    assert A.greedy_smallest_last(adj)[0] in ([0, 1], [1, 0]) and A.color_count(A.dsatur(adj)[0]) == 2
    assert A.colorable_k(adj, 1).status == "nein" and A.colorable_k(adj, 2).status == "ja"


def test_isolated_vertices_get_the_first_colour():
    adj = A.adjacency(4, [(0, 1)])
    colors, _ = A.dsatur(adj)
    assert colors[2] == 0 and colors[3] == 0 and A.violations(adj, colors) == []


def test_kempe_reduce_on_an_already_good_colouring_changes_nothing():
    adj = A.adjacency(3, [(0, 1), (1, 2)])
    r = A.kempe_reduce(adj, [0, 1, 0], 4)
    assert r.colors == [0, 1, 0] and r.events == [] and r.chains == 0 and r.success


def test_kempe_reduce_with_k_equal_to_the_colour_count_has_nothing_to_do():
    adj = A.adjacency(4, [(0, 1), (1, 2), (2, 3), (0, 3)])
    colors, _ = A.dsatur(adj)
    r = A.kempe_reduce(adj, colors, A.color_count(colors))
    assert r.colors == colors and r.success


def test_results_are_deterministic_and_do_not_depend_on_the_input_order_of_edges():
    edges = [(0, 1), (1, 2), (0, 2), (2, 3), (3, 4), (2, 4)]
    a = A.adjacency(5, edges)
    b = A.adjacency(5, list(reversed(edges)))
    assert A.dsatur(a) == A.dsatur(b) and A.greedy_smallest_last(a) == A.greedy_smallest_last(b)


def test_ties_in_the_exact_decision_are_broken_by_the_smaller_vertex():
    adj = A.adjacency(3, [(0, 1)])
    assert A.colorable_k(adj, 2).colors == [0, 1, 0]


def test_the_density_bound_is_inclusive_for_the_fullest_map():
    inst = S.make_instance("delaunay", 30, 100, 1)
    assert inst.m <= S.euler_bound(30) and inst.m > 30


@pytest.mark.parametrize("net", list(C.NET_TYPES))
@pytest.mark.parametrize("n", [C.N_MIN, C.N_MAX])
@pytest.mark.parametrize("density", [C.DENSITY_MIN, C.DENSITY_MAX])
@pytest.mark.parametrize("method", list(C.METHODS))
def test_every_corner_of_the_controls_gives_a_consistent_analysis(net, n, density, method):
    a = ev.analyse(ev.Settings(net, n, density, 7003, method))
    assert a.inst.n == n and a.run.method == method and a.run.violations == 0 and a.run.n_colors >= 1
    kind, text = ev.verdict_coloring(a)
    assert kind in ("success", "warning") and text


def test_non_planar_instances_skip_the_heawood_methods():
    a = ev.analyse_instance(S.hand_graph("K5"), "kempe")
    assert set(a.runs) == {"greedy", "dsatur"} and a.run.method == "dsatur"             # Heawood und Kempe nicht anwendbar: Rückfall auf DSATUR
    kind, text = ev.verdict_coloring(a)
    assert kind == "info" and "nicht planar" in text
