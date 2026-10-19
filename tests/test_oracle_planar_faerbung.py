"""Orakel-Test planar-faerbung-demo: Kern gegen unabhängige Rechenwege (DEMO-PLAYBOOK §12).

Orakel: (1) Brute Force über alle Färbungen mit k Farben für kleine Graphen, (2) networkx (Zusammenhangskomponenten der Kempe-Ketten, Planarität, Bipartitheit),
(3) Sätze: jede Kempe-Kette lässt sich tauschen, ohne die Zulässigkeit zu verletzen; der Vierfarbensatz (die exakte Entscheidung darf auf planaren Graphen nie „nein“
sagen); Smallest-Last-Greedy braucht auf planaren Graphen höchstens 6 Farben (Entartung ≤ 5); DSATUR höchstens Δ + 1; Heawood höchstens 5.
Der große Lauf (mindestens 200 Zufallsinstanzen) lief im Scratch-Ordner; hier die schnelle Fassung."""

import itertools
import random

import numpy as np
import pytest

import pfb_algorithm as A
import pfb_scenario as S

nx = pytest.importorskip("networkx")


def brute_force_colorable(adj, k):
    n = len(adj)
    for colors in itertools.product(range(k), repeat=n):
        if all(colors[u] != colors[v] for u in range(n) for v in adj[u] if u < v):
            return True
    return False


def _random_graph(rng, n, m):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    return A.adjacency(n, rng.sample(pairs, min(m, len(pairs))))


def _planar_instances(count, rng):
    nets = ("delaunay", "grid")
    for i in range(count):
        n = rng.randint(8, 60)
        yield S.make_instance(nets[i % 2], n, rng.choice((40, 70, 100)), rng.randrange(10**6))


def test_the_brute_force_oracle_on_known_graphs():
    """Das Orakel vorher an Handbeispielen prüfen: K4 braucht 4, Dreieck 3, Fünfeck 3, Pfad 2."""
    k4 = A.adjacency(4, [(u, v) for u in range(4) for v in range(u + 1, 4)])
    assert not brute_force_colorable(k4, 3) and brute_force_colorable(k4, 4)
    c5 = A.adjacency(5, [(i, (i + 1) % 5) for i in range(5)])
    assert not brute_force_colorable(c5, 2) and brute_force_colorable(c5, 3)


def test_the_exact_decision_agrees_with_brute_force_on_small_random_graphs():
    rng = random.Random(7)
    yes = no = 0
    for _ in range(120):
        n = rng.randint(4, 7)
        adj = _random_graph(rng, n, rng.randint(n, n * (n - 1) // 2))
        for k in (2, 3, 4):
            mine = A.colorable_k(adj, k).status
            assert mine in ("ja", "nein")
            assert (mine == "ja") == brute_force_colorable(adj, k), (n, k)
            yes += mine == "ja"
            no += mine == "nein"
    assert yes > 50 and no > 50                                  # beide Antworten kommen vor


def test_the_exact_decision_returns_proper_colourings_with_at_most_k_colours():
    rng = random.Random(8)
    for _ in range(60):
        n = rng.randint(5, 14)
        adj = _random_graph(rng, n, rng.randint(n, 2 * n))
        for k in (3, 4):
            r = A.colorable_k(adj, k)
            if r.status == "ja":
                assert A.violations(adj, r.colors) == [] and A.color_count(r.colors) <= k


def test_known_chromatic_numbers():
    ik, k5 = S.hand_graph("Ikosaeder"), S.hand_graph("K5")
    pet, k4 = S.hand_graph("Petersen-Graph"), S.hand_graph("K4")
    for inst, chi in ((ik, 4), (k5, 5), (pet, 3), (k4, 4), (S.hand_graph("Oktaeder"), 3)):
        adj = A.adjacency(inst.n, inst.edges)
        assert A.colorable_k(adj, chi).status == "ja" and A.colorable_k(adj, chi - 1).status == "nein", inst.name


def test_bipartite_graphs_are_two_colourable_exactly_when_networkx_says_so():
    rng = random.Random(9)
    for _ in range(60):
        n = rng.randint(4, 10)
        adj = _random_graph(rng, n, rng.randint(n - 1, 2 * n))
        g = nx.Graph([(u, v) for u in range(n) for v in adj[u] if u < v])
        g.add_nodes_from(range(n))
        assert (A.colorable_k(adj, 2).status == "ja") == nx.is_bipartite(g)


def test_kempe_chains_equal_the_components_of_the_induced_subgraph():
    rng = random.Random(10)
    for inst in _planar_instances(40, rng):
        adj = A.adjacency(inst.n, inst.edges)
        colors, _ = A.dsatur(adj)
        a, b = rng.sample(range(max(2, A.color_count(colors))), 2)
        starts = [v for v in range(inst.n) if colors[v] in (a, b)]
        if not starts:
            continue
        v = rng.choice(starts)
        g = nx.Graph()
        g.add_nodes_from(starts)
        g.add_edges_from((x, y) for x in starts for y in adj[x] if y in set(starts) and x < y)
        assert A.kempe_chain(adj, colors, v, a, b) == tuple(sorted(nx.node_connected_component(g, v)))


def test_swapping_a_kempe_chain_keeps_the_colouring_proper():
    """Der Satz hinter allen Kempe-Verfahren: Tausch auf einer ganzen Kette lässt jede zulässige Färbung zulässig."""
    rng = random.Random(11)
    for inst in _planar_instances(60, rng):
        adj = A.adjacency(inst.n, inst.edges)
        colors, _ = A.dsatur(adj)
        k = A.color_count(colors)
        if k < 2:
            continue
        a, b = rng.sample(range(k), 2)
        starts = [v for v in range(inst.n) if colors[v] in (a, b)]
        chain = A.kempe_chain(adj, colors, rng.choice(starts), a, b)
        assert A.violations(adj, A.swap_chain(colors, chain, a, b)) == []


def test_every_method_gives_a_proper_colouring_within_its_guarantee_on_planar_instances():
    rng = random.Random(12)
    for inst in _planar_instances(150, rng):
        adj = A.adjacency(inst.n, inst.edges)
        delta = max((len(a) for a in adj), default=0)
        g, ge = A.greedy_smallest_last(adj)
        d, de = A.dsatur(adj)
        h = A.heawood_color(adj, inst.pos)
        r = A.kempe_reduce(adj, h.colors, 4)
        for colors in (g, d, h.colors, r.colors):
            assert A.violations(adj, colors) == [] and min(colors) >= 0
        assert A.color_count(g) <= 6 and A.color_count(d) <= delta + 1 and A.color_count(h.colors) <= 5
        assert A.color_count(r.colors) <= A.color_count(h.colors) and (r.remaining == 0) == (A.color_count(r.colors) <= 4)
        # die Ereignisse spielen die Endfarben genau nach
        assert A.replay(inst.n, ge, len(ge)) == g and A.replay(inst.n, de, len(de)) == d
        assert A.replay(inst.n, h.events, len(h.events)) == h.colors
        assert A.replay(inst.n, h.events + r.events, len(h.events + r.events)) == r.colors


def test_four_colour_theorem_the_exact_decision_never_says_no_on_planar_instances():
    """Wäre es je „nein“, wäre der Kern falsch (oder der Graph nicht planar): der Satz verbietet es."""
    rng = random.Random(13)
    for inst in _planar_instances(80, rng):
        if inst.n > 40:
            continue
        adj = A.adjacency(inst.n, inst.edges)
        assert nx.check_planarity(nx.Graph(list(inst.edges)))[0]
        assert A.colorable_k(adj, 4, budget=200_000).status in ("ja", "unentschieden")


def test_k5_and_k33_style_counterexamples_need_more_than_four_or_three_colours():
    k5 = S.hand_graph("K5")
    assert A.colorable_k(A.adjacency(5, k5.edges), 4).status == "nein"
    k6 = A.adjacency(6, [(u, v) for u in range(6) for v in range(u + 1, 6)])
    assert A.colorable_k(k6, 5).status == "nein" and A.colorable_k(k6, 6).status == "ja"


def test_heawood_needs_a_chain_only_on_degree_five_graphs():
    """Auf Karten nie (kleinste freie Farbe); am Ikosaeder bei einigen zufälligen Reihenfolgen: der Zweig läuft also, und das Ergebnis bleibt zulässig."""
    ik = S.hand_graph("Ikosaeder")
    adj = A.adjacency(ik.n, ik.edges)
    used = 0
    for seed in range(30):
        rng = np.random.default_rng(seed)
        order = [int(x) for x in rng.permutation(ik.n)]
        h = A.heawood_color(adj, ik.pos, order=order, choose="random", rng=rng)
        assert A.violations(adj, h.colors) == [] and A.color_count(h.colors) <= 5
        used += h.chains
    assert used > 0
