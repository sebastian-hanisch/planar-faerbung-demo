"""Auswertung: Verfahren auf einer Instanz, Messreihen (Vierfarben-Anteile, Heawood-Ketten, exakte Entscheidung, 3-Färbbarkeit) und die Verdikte als reine Funktionen."""

from __future__ import annotations

import statistics
from dataclasses import dataclass

import numpy as np

import pfb_algorithm as A
import pfb_constants as C
import pfb_scenario as S


def num(x: float, digits: int = 0) -> str:
    """Zahl im deutschen Format: Tausenderpunkt, Dezimalkomma."""
    return f"{x:,.{digits}f}".translate(str.maketrans({",": ".", ".": ","}))


def plural(count: int, singular: str, plural_form: str) -> str:
    return f"{count} {singular if count == 1 else plural_form}"


@dataclass(frozen=True)
class Settings:
    net: str = C.DEFAULT_NET
    n: int = C.DEFAULT_N
    density: int = C.DEFAULT_DENSITY
    seed: int = C.DEFAULT_SEED
    method: str = C.DEFAULT_METHOD


@dataclass(frozen=True)
class Run:
    """Ergebnis eines Verfahrens auf einer Instanz."""

    method: str
    colors: list[int]
    events: list[A.Event]
    n_colors: int
    violations: int              # Kanten mit gleichfarbigen Enden (muss 0 sein)
    chains: int                  # getauschte Kempe-Ketten
    needing: int                 # Knoten, die bei Heawood fünf verschiedene Nachbarfarben hatten
    stuck: bool = False          # Heawood nicht ausführbar (Zeichnung nicht planar)


@dataclass(frozen=True)
class Analysis:
    inst: S.Instance
    run: Run                     # das gewählte Verfahren
    runs: dict[str, Run]         # alle Verfahren auf derselben Instanz
    max_degree: int
    reduce_remaining: int        # Knoten mit fünfter Farbe nach der Kempe-Reduktion


def _run_from(method: str, colors, events, chains=0, needing=0, adj=None, stuck=False) -> Run:
    return Run(method, colors, events, A.color_count(colors), len(A.violations(adj, colors)) if adj is not None else 0, chains, needing, stuck)


def run_methods(inst: S.Instance) -> tuple[dict[str, Run], int]:
    """Alle vier Verfahren auf einer Instanz; Heawood nur, wenn die Zeichnung planar ist. Gibt die Läufe und die Zahl der Restknoten der Kempe-Reduktion zurück."""
    adj = A.adjacency(inst.n, inst.edges)
    runs: dict[str, Run] = {}
    colors, events = A.greedy_smallest_last(adj)
    runs["greedy"] = _run_from("greedy", colors, events, adj=adj)
    colors, events = A.dsatur(adj)
    runs["dsatur"] = _run_from("dsatur", colors, events, adj=adj)
    remaining = 0
    if inst.planar:
        h = A.heawood_color(adj, inst.pos)
        runs["heawood"] = _run_from("heawood", h.colors, h.events, h.chains, h.needing, adj)
        r = A.kempe_reduce(adj, h.colors, 4, C.KEMPE_ROUNDS)
        remaining = r.remaining
        runs["kempe"] = _run_from("kempe", r.colors, h.events + r.events, h.chains + r.chains, h.needing, adj)
    return runs, remaining


def analyse(settings: Settings) -> Analysis:
    return analyse_instance(S.make_instance(settings.net, settings.n, settings.density, settings.seed), settings.method)


def analyse_instance(inst: S.Instance, method: str = C.DEFAULT_METHOD) -> Analysis:
    runs, remaining = run_methods(inst)
    chosen = method if method in runs else "dsatur"
    adj = A.adjacency(inst.n, inst.edges)
    return Analysis(inst, runs[chosen], runs, max((len(a) for a in adj), default=0), remaining)


# --- Messreihen -----------------------------------------------------------------------------------------------------------------------------


def four_table(ns=C.FOUR_NS, seeds=C.SWEEP_SEEDS) -> list[dict]:
    """Je Knotenzahl: Anteil der Karten, auf denen jedes Verfahren mit höchstens 4 Farben endet, und Mittel der getauschten Ketten."""
    rows = []
    for n in ns:
        cnt = {"greedy": 0, "dsatur": 0, "heawood": 0, "kempe": 0}
        chains, five_only = [], 0
        for seed in seeds:
            runs, _ = run_methods(S.make_instance("delaunay", n, 100, seed))
            for key in cnt:
                cnt[key] += runs[key].n_colors <= 4
            chains.append(runs["kempe"].chains)
            five_only += runs["heawood"].n_colors <= 5
        k = len(seeds)
        rows.append({"n": n, "samples": k, **{key: cnt[key] / k for key in cnt}, "chains": statistics.mean(chains), "heawood_five": five_only / k})
    return rows


def need_table(ns=C.NEED_NS, seeds=C.SWEEP_SEEDS, orders=C.ICOSAHEDRON_ORDERS) -> dict:
    """Wie oft braucht das Heawood-Verfahren überhaupt eine Kette? Auf Karten (kleinste Farbe, zufällige Farbe) und am Ikosaeder bei zufälliger Reihenfolge."""
    maps = []
    for n in ns:
        low = rnd = 0
        for seed in seeds:
            inst = S.make_instance("delaunay", n, 100, seed)
            adj = A.adjacency(inst.n, inst.edges)
            low += A.heawood_color(adj, inst.pos).needing > 0
            rng = np.random.default_rng(seed)
            rnd += A.heawood_color(adj, inst.pos, choose="random", rng=rng).needing > 0
        maps.append({"n": n, "samples": len(seeds), "low": low, "random": rnd})
    ik = S.hand_graph("Ikosaeder")
    adj = A.adjacency(ik.n, ik.edges)
    needing = chains = 0
    for seed in range(orders):
        rng = np.random.default_rng(seed)
        order = [int(x) for x in rng.permutation(ik.n)]
        h = A.heawood_color(adj, ik.pos, order=order, choose="random", rng=rng)
        needing += h.needing > 0
        chains += h.chains
    return {"maps": maps, "icosahedron": {"orders": orders, "needing": needing, "chains": chains}}


def exact_table(ns=C.EXACT_NS, seeds=C.SWEEP_SEEDS, budget=C.EXACT_BUDGET) -> list[dict]:
    """Je Knotenzahl: wie viele Karten die exakte Entscheidung „4-färbbar?“ im Budget beantwortet, und wie viele die Kempe-Reduktion auf 4 Farben bringt."""
    rows = []
    for n in ns:
        yes = open_ = kempe = 0
        nodes = []
        for seed in seeds:
            inst = S.make_instance("delaunay", n, 100, seed)
            adj = A.adjacency(inst.n, inst.edges)
            r = A.colorable_k(adj, 4, budget)
            yes += r.status == "ja"
            open_ += r.status == "unentschieden"
            nodes.append(r.nodes)
            runs, _ = run_methods(inst)
            kempe += runs["kempe"].n_colors <= 4
        rows.append({"n": n, "samples": len(seeds), "yes": yes, "undecided": open_, "kempe": kempe, "median_nodes": statistics.median(nodes), "budget": budget})
    return rows


def three_table(ns=C.THREE_NS, seeds=C.SWEEP_SEEDS, budget=C.EXACT_BUDGET, density=C.THREE_DENSITY) -> list[dict]:
    """Verdünnte Karten: wie viele sind 3-färbbar, wie viele 4-färbbar (exakt, im Budget)."""
    rows = []
    for n in ns:
        three = four = undecided = 0
        for seed in seeds:
            inst = S.make_instance("delaunay", n, density, seed + 2000)
            adj = A.adjacency(inst.n, inst.edges)
            r3 = A.colorable_k(adj, 3, budget)
            three += r3.status == "ja"
            undecided += r3.status == "unentschieden"
            four += A.colorable_k(adj, 4, budget).status == "ja"
        rows.append({"n": n, "samples": len(seeds), "three": three, "four": four, "undecided": undecided, "density": density})
    return rows


def hand_table() -> list[dict]:
    """Lehrbuch-Graphen: kleinste Farbenzahl (exakt) und Farben der vier Verfahren."""
    rows = []
    for name in C.HAND_GRAPHS:
        inst = S.hand_graph(name)
        adj = A.adjacency(inst.n, inst.edges)
        k = next(k for k in range(1, inst.n + 1) if A.colorable_k(adj, k).status == "ja")
        runs, _ = run_methods(inst)
        rows.append(
            {
                "name": name, "planar": inst.planar, "n": inst.n, "m": inst.m, "chi": k,
                "greedy": runs["greedy"].n_colors, "dsatur": runs["dsatur"].n_colors,
                "heawood": runs["heawood"].n_colors if "heawood" in runs else None, "kempe": runs["kempe"].n_colors if "kempe" in runs else None,
            }
        )
    return rows


# --- Verdikte (reine Funktionen: Art, Text) -------------------------------------------------------------------------------------------------


def verdict_coloring(a: Analysis) -> tuple[str, str]:
    """Hauptergebnis: zulässig? wie viele Farben im Verhältnis zum Vierfarbensatz?"""
    r = a.run
    name = C.METHODS[r.method]
    if r.violations:
        return "error", f"**Fehler:** {name} liefert keine zulässige Färbung ({plural(r.violations, 'Kante hat', 'Kanten haben')} gleichfarbige Enden)."
    if r.n_colors <= 4:
        return "success", f"{name}: **{r.n_colors} Farben**, zulässig. Der Vierfarbensatz garantiert, dass vier immer genügen; hier sind es {'genau vier' if r.n_colors == 4 else 'weniger'}."
    if a.inst.planar:
        return (
            "warning",
            f"{name}: **{r.n_colors} Farben**, zulässig, aber nicht optimal: Der Vierfarbensatz garantiert, dass **vier** genügen. Das Verfahren kennt die Planarität nicht oder nutzt sie nur für fünf.",
        )
    return "info", f"{name}: **{r.n_colors} Farben**. Der Graph ist nicht planar: der Vierfarbensatz gilt nicht."


def verdict_chains(a: Analysis) -> tuple[str, str]:
    """Wie viele Kempe-Ketten wurden getauscht, und waren sie nötig?"""
    r = a.run
    if r.method not in ("heawood", "kempe"):
        return "info", "Greedy und DSATUR tauschen keine Ketten."
    if r.method == "heawood":
        if r.needing == 0:
            return "info", "Das Heawood-Verfahren hat hier **keine Kette** gebraucht: Kein Knoten hatte fünf verschiedene Nachbarfarben, die kleinste freie Farbe genügte immer."
        return "info", f"Das Heawood-Verfahren brauchte an {plural(r.needing, 'Knoten', 'Knoten')} eine Kette ({plural(r.chains, 'Kette', 'Ketten')} getauscht)."
    if a.reduce_remaining:
        return "warning", f"Die Kempe-Reduktion bleibt hängen: {plural(a.reduce_remaining, 'Knoten hat', 'Knoten haben')} noch eine fünfte Farbe ({plural(r.chains, 'Kette', 'Ketten')} getauscht). Vier Farben gibt es nach dem Vierfarbensatz trotzdem."
    return "success", f"Die Kempe-Reduktion hat die fünfte Farbe mit {plural(r.chains, 'Kette', 'Ketten')} beseitigt."


def verdict_four(rows: list[dict]) -> tuple[str, str]:
    """Anteil mit 4 Farben je Verfahren und Größe."""
    first, last = rows[0], rows[-1]
    return (
        "info",
        f"Bei n = {first['n']} enden {num(first['dsatur'] * 100)} % der Karten mit DSATUR auf vier Farben, bei n = {last['n']} {num(last['dsatur'] * 100)} %; "
        f"Greedy {num(first['greedy'] * 100)} % und {num(last['greedy'] * 100)} %. Die Kempe-Reduktion bringt {num(first['kempe'] * 100)} % und {num(last['kempe'] * 100)} % der Karten auf vier Farben. "
        f"Der Vierfarbensatz garantiert vier für alle.",
    )


def verdict_need(t: dict) -> tuple[str, str]:
    """Wann braucht Heawood eine Kette?"""
    total = sum(m["samples"] for m in t["maps"])
    low = sum(m["low"] for m in t["maps"])
    rnd = sum(m["random"] for m in t["maps"])
    ik = t["icosahedron"]
    return (
        "info",
        f"Auf zufälligen Karten brauchte das Heawood-Verfahren in {low} von {total} Fällen eine Kette (kleinste freie Farbe) und in {rnd} von {total} (zufällige freie Farbe). "
        f"Am Ikosaeder, wo jeder Knoten Grad 5 hat, brauchte es in {ik['needing']} von {ik['orders']} zufälligen Reihenfolgen eine Kette.",
    )


def verdict_exact(rows: list[dict]) -> tuple[str, str]:
    """Die exakte Entscheidung gegen die Kempe-Reduktion."""
    last = rows[-1]
    return (
        "info",
        f"Bei n = {last['n']} beantwortet die exakte Entscheidung „4-färbbar?“ {last['yes']} von {last['samples']} Karten im Budget von {num(last['budget'])} Knoten, "
        f"{last['undecided']} bleiben unentschieden (nie als „nein“ gewertet); die Kempe-Reduktion bringt {last['kempe']} von {last['samples']} auf vier Farben.",
    )


def verdict_three(rows: list[dict]) -> tuple[str, str]:
    """Drei Farben: der Satz hilft nicht."""
    parts = [f"n = {r['n']}: {r['three']} von {r['samples']} 3-färbbar, {r['four']} 4-färbbar" + (f", {r['undecided']} bei drei Farben unentschieden" if r["undecided"] else "") for r in rows]
    return "info", f"Verdünnte Karten ({rows[0]['density']} % von 3n − 6 Kanten): " + "; ".join(parts) + ". Ob drei Farben reichen, ist auch für planare Graphen schwer; vier reichen immer."
