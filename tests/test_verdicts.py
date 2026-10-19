"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier."""

import dataclasses

import pfb_evaluation as ev
import pfb_scenario as S


def _analysis(method, n_colors, violations=0, chains=0, needing=0, remaining=0, planar=True):
    inst = S.hand_graph("K4") if planar else S.hand_graph("K5")
    run = ev.Run(method, [0] * inst.n, [], n_colors, violations, chains, needing)
    return ev.Analysis(inst, run, {method: run}, 3, remaining)


def test_num_and_plural():
    assert ev.num(1234567.891, 1) == "1.234.567,9" and ev.num(0.5, 1) == "0,5" and ev.num(1000) == "1.000"
    assert ev.plural(1, "Kette", "Ketten") == "1 Kette" and ev.plural(0, "Kette", "Ketten") == "0 Ketten"


def test_verdict_coloring_four_colours_is_a_success_and_names_the_theorem():
    kind, text = ev.verdict_coloring(_analysis("kempe", 4))
    assert kind == "success" and "**4 Farben**" in text and "genau vier" in text and "Vierfarbensatz" in text
    kind, text = ev.verdict_coloring(_analysis("greedy", 3))
    assert kind == "success" and "weniger" in text


def test_verdict_coloring_five_colours_on_a_planar_graph_is_a_warning():
    kind, text = ev.verdict_coloring(_analysis("dsatur", 5))
    assert kind == "warning" and "**5 Farben**" in text and "**vier** genügen" in text
    kind, text = ev.verdict_coloring(_analysis("dsatur", 6))
    assert kind == "warning" and "**6 Farben**" in text


def test_verdict_coloring_non_planar_graph_and_violations():
    kind, text = ev.verdict_coloring(_analysis("dsatur", 5, planar=False))
    assert kind == "info" and "nicht planar" in text and "gilt nicht" in text
    kind, text = ev.verdict_coloring(_analysis("dsatur", 5, violations=2))
    assert kind == "error" and "2 Kanten haben gleichfarbige Enden" in text
    kind, text = ev.verdict_coloring(_analysis("dsatur", 5, violations=1))
    assert "1 Kante hat gleichfarbige Enden" in text


def test_verdict_chains_cases():
    assert ev.verdict_chains(_analysis("greedy", 4)) == ("info", "Greedy und DSATUR tauschen keine Ketten.")
    kind, text = ev.verdict_chains(_analysis("heawood", 5, needing=0))
    assert kind == "info" and "keine Kette" in text
    kind, text = ev.verdict_chains(_analysis("heawood", 5, chains=2, needing=2))
    assert kind == "info" and "an 2 Knoten eine Kette (2 Ketten getauscht)" in text
    kind, text = ev.verdict_chains(_analysis("kempe", 4, chains=3))
    assert kind == "success" and "mit 3 Ketten beseitigt" in text
    kind, text = ev.verdict_chains(_analysis("kempe", 5, chains=1, remaining=2))
    assert kind == "warning" and "2 Knoten haben noch eine fünfte Farbe" in text and "1 Kette getauscht" in text
    kind, text = ev.verdict_chains(_analysis("kempe", 5, chains=1, remaining=1))
    assert "1 Knoten hat noch eine fünfte Farbe" in text


def test_verdict_four_names_first_and_last_size():
    rows = [
        {"n": 30, "samples": 20, "greedy": 0.75, "dsatur": 0.65, "heawood": 0.75, "kempe": 1.0, "chains": 0.5, "heawood_five": 1.0},
        {"n": 300, "samples": 20, "greedy": 0.0, "dsatur": 0.0, "heawood": 0.0, "kempe": 0.9, "chains": 12.4, "heawood_five": 1.0},
    ]
    kind, text = ev.verdict_four(rows)
    assert kind == "info"
    assert "Bei n = 30 enden 65 % der Karten mit DSATUR auf vier Farben, bei n = 300 0 %" in text
    assert "Greedy 75 % und 0 %" in text and "100 % und 90 %" in text


def test_verdict_need_sums_over_all_maps():
    t = {"maps": [{"n": 30, "samples": 20, "low": 0, "random": 1}, {"n": 100, "samples": 20, "low": 2, "random": 0}], "icosahedron": {"orders": 30, "needing": 8, "chains": 9}}
    kind, text = ev.verdict_need(t)
    assert kind == "info" and "in 2 von 40 Fällen eine Kette (kleinste freie Farbe) und in 1 von 40" in text and "in 8 von 30 zufälligen Reihenfolgen" in text


def test_verdict_exact_uses_the_largest_size():
    rows = [{"n": 100, "samples": 20, "yes": 20, "undecided": 0, "kempe": 19, "median_nodes": 116.0, "budget": 100000},
            {"n": 200, "samples": 20, "yes": 16, "undecided": 4, "kempe": 18, "median_nodes": 247.0, "budget": 100000}]
    kind, text = ev.verdict_exact(rows)
    assert "Bei n = 200" in text and "16 von 20 Karten im Budget von 100.000 Knoten" in text and "4 bleiben unentschieden" in text and "18 von 20 auf vier Farben" in text


def test_verdict_three_mentions_undecided_cases_only_when_there_are_some():
    rows = [{"n": 60, "samples": 20, "three": 19, "four": 20, "undecided": 0, "density": 55}, {"n": 100, "samples": 20, "three": 14, "four": 20, "undecided": 2, "density": 55}]
    kind, text = ev.verdict_three(rows)
    assert "55 % von 3n − 6 Kanten" in text and "n = 60: 19 von 20 3-färbbar, 20 4-färbbar;" in text
    assert "n = 100: 14 von 20 3-färbbar, 20 4-färbbar, 2 bei drei Farben unentschieden" in text
    assert "bei drei Farben unentschieden" not in ev.verdict_three(rows[:1])[1]


def test_run_dataclass_is_frozen():
    a = _analysis("dsatur", 4)
    try:
        dataclasses.replace(a.run, n_colors=9)
    except Exception:
        raise AssertionError("replace darf nicht scheitern")
