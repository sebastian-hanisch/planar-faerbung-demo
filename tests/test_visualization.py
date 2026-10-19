"""Darstellung: Zustand des Abspielens und dass jede Figur ohne Fehler entsteht, mit festen Achsen."""

import plotly.graph_objects as go
import pytest

import pfb_algorithm as A
import pfb_constants as C
import pfb_evaluation as ev
import pfb_scenario as S
import pfb_visualization as V


def _star():
    inst = S.Instance(4, ((0, 3), (1, 3), (2, 3)), ((0.0, 1.0), (1.0, 0.0), (-1.0, 0.0), (0.0, 0.0)), "Stern")
    adj = A.adjacency(4, inst.edges)
    r = A.kempe_reduce(adj, [0, 1, 2, 4], 4)
    run = ev.Run("kempe", r.colors, r.events, 3, 0, r.chains, 0)
    return inst, run


def test_playback_before_the_first_event_shows_the_start_colours():
    inst, run = _star()
    assert A.replay(inst.n, run.events, 0) == [-1, -1, -1, -1]
    fig = V.build_playback(inst, run, 0)
    assert isinstance(fig, go.Figure) and list(fig.data[-1].marker.color) == [C.COLOR_NONE] * 4


def test_playback_highlights_the_chain_of_a_swap_event_and_the_focus_vertex():
    inst, run = _star()
    fig = V.build_playback(inst, run, 1)                                      # erstes Ereignis: Kette (0,) getauscht
    nodes = fig.data[-1]
    assert list(nodes.marker.line.width) == [4, 1, 1, 4]                       # Kettenknoten 0 und der Fokusknoten 3 (um ihn geht es) dick umrandet
    fig2 = V.build_playback(inst, run, 2)                                     # zweites Ereignis: Knoten 3 bekommt Farbe 0, keine Kette, Fokus 3
    assert list(fig2.data[-1].marker.line.width) == [1, 1, 1, 4]


def test_playback_beyond_the_end_is_the_final_state():
    inst, run = _star()
    assert list(V.build_playback(inst, run, 99).data[-1].marker.color) == list(V.build_playback(inst, run, len(run.events)).data[-1].marker.color)


def test_colour_helper_wraps_around_the_palette_and_marks_uncoloured_vertices():
    assert V._color(-1) == C.COLOR_NONE and V._color(0) == C.COLORS[0] and V._color(len(C.COLORS)) == C.COLORS[0]


def _fixed(fig):
    return fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange


@pytest.mark.parametrize("method", list(C.METHODS))
def test_every_method_draws_at_every_step_end(method):
    a = ev.analyse(ev.Settings("delaunay", 30, 100, 7000, method))
    for step in (0, len(a.run.events) // 2, len(a.run.events)):
        assert _fixed(V.build_playback(a.inst, a.run, step))


def test_every_textbook_graph_draws():
    for name in C.HAND_GRAPHS:
        inst = S.hand_graph(name)
        a = ev.analyse_instance(inst, "dsatur")
        assert _fixed(V.build_coloring(inst, a.run.colors, title=name))


def test_measure_figures_have_fixed_axes():
    four = [{"n": n, "samples": 20, "greedy": g, "dsatur": d, "heawood": g, "kempe": k, "chains": 1.0, "heawood_five": 1.0} for n, g, d, k in ((30, 0.7, 0.6, 1.0), (100, 0.0, 0.05, 0.95))]
    exact = [{"n": 100, "samples": 20, "yes": 20, "undecided": 0, "kempe": 19, "median_nodes": 100.0, "budget": 1000}]
    for fig in (V.build_four(four), V.build_exact(exact)):
        assert fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange
