"""Jede Zahl der README wird hier nachgerechnet (DEMO-PLAYBOOK §4): über dieselben Auswertungsfunktionen wie in der App.

Zufallsabhängige Anteile (20 feste Karten je Zelle) mit Band, weil die Bibliotheksversionen der CI die Ziehungen verschieben dürfen; Handrechnungen exakt."""

import pytest

import pfb_algorithm as A
import pfb_constants as C
import pfb_evaluation as ev
import pfb_scenario as S

BAND = 0.1


@pytest.fixture(scope="module")
def four():
    return {r["n"]: r for r in ev.four_table()}


@pytest.fixture(scope="module")
def need():
    return ev.need_table()


@pytest.fixture(scope="module")
def exact():
    return {r["n"]: r for r in ev.exact_table()}


@pytest.fixture(scope="module")
def three():
    return {r["n"]: r for r in ev.three_table()}


def test_four_table_shares(four):
    dsatur = {30: 0.65, 60: 0.40, 100: 0.05, 200: 0.0, 300: 0.0}
    greedy = {30: 0.75, 60: 0.15, 100: 0.0, 200: 0.0, 300: 0.0}
    kempe = {30: 1.0, 60: 0.95, 100: 0.95, 200: 0.90, 300: 0.90}
    for n in dsatur:
        assert four[n]["dsatur"] == pytest.approx(dsatur[n], abs=BAND), n
        assert four[n]["greedy"] == pytest.approx(greedy[n], abs=BAND), n
        assert four[n]["kempe"] == pytest.approx(kempe[n], abs=BAND), n
        assert four[n]["heawood_five"] == 1.0                     # Heawood: immer höchstens fünf Farben
    assert C.FOUR_NS == (30, 60, 100, 200, 300) and len(C.SWEEP_SEEDS) == 20


def test_kempe_chains_per_map_grow_with_the_size(four):
    means = [four[n]["chains"] for n in (30, 60, 100, 200, 300)]
    assert means == sorted(means) and means[0] < 1.5 and 8 < means[-1] < 17


def test_heawood_needs_no_chain_on_random_maps_but_sometimes_on_the_icosahedron(need):
    assert all(m["low"] == 0 and m["random"] == 0 for m in need["maps"]) and sum(m["samples"] for m in need["maps"]) == 60
    ik = need["icosahedron"]
    assert ik["orders"] == 30 and 5 <= ik["needing"] <= 12 and ik["chains"] >= ik["needing"]


def test_exact_decision_against_the_kempe_reduction(exact):
    assert (exact[30]["yes"], exact[30]["undecided"], exact[30]["kempe"]) == (20, 0, 20)
    assert exact[60]["yes"] + exact[60]["undecided"] == 20 and exact[60]["undecided"] <= 2
    assert exact[100]["yes"] >= 19 and exact[100]["kempe"] >= 18
    assert exact[200]["undecided"] >= 2 and exact[200]["yes"] <= 18 and exact[200]["kempe"] >= 16
    assert exact[200]["kempe"] > exact[200]["yes"]                # bei n = 200 beantwortet die Kette mehr Fälle als die Entscheidung im Budget
    for n, median in ((30, 31), (60, 67), (100, 116.5), (200, 247)):
        assert exact[n]["median_nodes"] == pytest.approx(median, rel=0.4), n
    assert C.EXACT_BUDGET == 100_000


def test_three_colourability_of_thinned_maps(three):
    assert three[60]["four"] == 20 and three[100]["four"] == 20
    assert 17 <= three[60]["three"] <= 20 and 11 <= three[100]["three"] <= 17
    assert three[60]["three"] > three[100]["three"] and three[100]["three"] < 20
    assert C.THREE_DENSITY == 55


def test_textbook_graph_table():
    rows = {r["name"]: r for r in ev.hand_table()}
    assert (rows["Ikosaeder"]["chi"], rows["Ikosaeder"]["greedy"], rows["Ikosaeder"]["dsatur"], rows["Ikosaeder"]["heawood"], rows["Ikosaeder"]["kempe"]) == (4, 5, 5, 5, 4)
    assert rows["Oktaeder"]["chi"] == 3 and rows["K4"]["chi"] == 4 and rows["K5 minus eine Kante"]["chi"] == 4
    assert rows["K5"]["chi"] == 5 and rows["K5"]["heawood"] is None and rows["Petersen-Graph"]["chi"] == 3 and not rows["Petersen-Graph"]["planar"]


def test_k5_does_not_obey_the_four_colour_theorem():
    k5 = S.hand_graph("K5")
    assert A.colorable_k(A.adjacency(5, k5.edges), 4).status == "nein"


def test_the_preset_maps_of_the_readme():
    a = ev.analyse(ev.Settings(**C.PRESETS["DSATUR verpasst die Vier"]))
    assert (a.inst.n, a.runs["dsatur"].n_colors, a.runs["kempe"].n_colors) == (100, 5, 4)
    assert (ev.analyse(ev.Settings(**C.PRESETS["Heawood: fünf Farben genügen"])).run.n_colors) == 5
