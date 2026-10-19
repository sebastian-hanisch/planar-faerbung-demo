"""Kern: Färbung planarer Graphen mit Greedy, DSATUR, Heawood-Verfahren (Kempe-Ketten), Kempe-Reduktion und exakter Entscheidung „k-färbbar?“.

Eine Einheit ist eine Regel: Reihenfolge bestimmen, einen Knoten färben, eine Kette bestimmen, eine Kette tauschen, einen Knoten freistellen, verzweigen.
Kein Zufall, keine Modul-Globals; Gleichstand entscheidet die kleinere Knotennummer. Farben sind Zahlen 0, 1, 2, …; −1 heißt „noch nicht gefärbt“.
Graphen sind einfach und ungerichtet (Nachbarmengen), Knoten 0 bis n − 1."""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass


def adjacency(n: int, edges) -> list[set[int]]:
    adj: list[set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def violations(adj, colors) -> list[tuple[int, int]]:
    """Kanten, deren Enden dieselbe Farbe haben (unabhängiger Prüfer); ungefärbte Knoten (−1) verletzen nichts."""
    return [(u, v) for u in range(len(adj)) for v in sorted(adj[u]) if u < v and colors[u] == colors[v] and colors[u] >= 0]


def color_count(colors) -> int:
    """Zahl der verwendeten Farben (größte Farbnummer plus eins; 0 ohne gefärbten Knoten)."""
    return max(colors) + 1 if colors and max(colors) >= 0 else 0


def smallest_last_order(adj) -> list[int]:
    """Entfernungsreihenfolge: wiederholt ein Knoten kleinsten Grades im Restgraphen (Gleichstand: kleinste Nummer) wird entfernt."""
    degree = {v: len(adj[v]) for v in range(len(adj))}
    alive = set(degree)
    order = []
    while alive:
        v = min(alive, key=lambda x: (degree[x], x))
        order.append(v)
        alive.discard(v)
        for u in adj[v]:
            if u in alive:
                degree[u] -= 1
    return order


def smallest_free(used) -> int:
    c = 0
    while c in used:
        c += 1
    return c


@dataclass(frozen=True)
class Event:
    """Ein Schritt zum Abspielen: 'color' (ein Knoten bekommt eine Farbe) oder 'kempe' (eine Kette wird getauscht; `assign` sind die neuen Farben der Kette)."""

    kind: str
    vertex: int                                  # der Knoten, um den es geht
    assign: tuple[tuple[int, int], ...]          # (Knoten, neue Farbe)
    chain: tuple[int, ...] = ()                  # Knoten der getauschten Kette
    pair: tuple[int, int] = (-1, -1)             # die beiden Farben der Kette (vor dem Tausch)


def greedy_color(adj, order) -> tuple[list[int], list[Event]]:
    """Färbt in der gegebenen Reihenfolge jeden Knoten mit der kleinsten Farbe, die kein schon gefärbter Nachbar hat."""
    colors = [-1] * len(adj)
    events = []
    for v in order:
        c = smallest_free({colors[u] for u in adj[v] if colors[u] >= 0})
        colors[v] = c
        events.append(Event("color", v, ((v, c),)))
    return colors, events


def greedy_smallest_last(adj) -> tuple[list[int], list[Event]]:
    """Greedy in der umgekehrten Smallest-Last-Reihenfolge (garantiert höchstens 6 Farben auf planaren Graphen)."""
    return greedy_color(adj, list(reversed(smallest_last_order(adj))))


def dsatur(adj) -> tuple[list[int], list[Event]]:
    """DSATUR: der nächste Knoten ist der mit den meisten verschiedenen Nachbarfarben (Gleichstand: größter Grad, dann kleinste Nummer)."""
    n = len(adj)
    colors = [-1] * n
    seen: list[set[int]] = [set() for _ in range(n)]
    events = []
    for _ in range(n):
        v = max((x for x in range(n) if colors[x] < 0), key=lambda x: (len(seen[x]), len(adj[x]), -x))
        c = smallest_free(seen[v])
        colors[v] = c
        events.append(Event("color", v, ((v, c),)))
        for u in adj[v]:
            seen[u].add(c)
    return colors, events


def kempe_chain(adj, colors, start: int, a: int, b: int) -> tuple[int, ...]:
    """Kempe-Kette: die Zusammenhangskomponente von `start` im Teilgraphen der Knoten mit den Farben a oder b (sortiert)."""
    seen = {start}
    queue = deque([start])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if y not in seen and colors[y] in (a, b):
                seen.add(y)
                queue.append(y)
    return tuple(sorted(seen))


def swap_chain(colors, chain, a: int, b: int) -> list[int]:
    """Vertauscht a und b auf der Kette (neue Liste); bleibt die Färbung zulässig, wenn `chain` eine ganze Kempe-Kette ist."""
    new = list(colors)
    for x in chain:
        new[x] = b if colors[x] == a else a
    return new


def neighbours_by_angle(pos, v: int, nbrs) -> list[int]:
    """Nachbarn im Uhrzeigersinn-unabhängigen Umlaufsinn um v (nach Winkel); nur bei geradlinig planarer Zeichnung die Reihenfolge der Einbettung."""
    return sorted(nbrs, key=lambda u: (math.atan2(pos[u][1] - pos[v][1], pos[u][0] - pos[v][0]), u))


class HeawoodStuck(Exception):
    """Fünf verschiedene Nachbarfarben, und keine der Ketten trennt: bei planarer Einbettung unmöglich (Zeichnung nicht planar oder Grad zu hoch)."""


@dataclass(frozen=True)
class HeawoodResult:
    colors: list[int]
    events: list[Event]
    chains: int                  # getauschte Ketten
    needing: int                 # Knoten, die fünf verschiedene Nachbarfarben hatten


KEMPE_PAIRS = ((0, 2), (1, 3), (2, 4), (3, 0), (4, 1))   # Paare von Nachbarn im Umlauf, deren Kette geprüft wird


def heawood_step(adj, pos, colors, v: int, choose: str = "low", rng=None):
    """Färbt v mit höchstens fünf Farben: freie Farbe (`choose`: kleinste, größte oder zufällige über den Generator `rng`), sonst eine Kempe-Kette zwischen zwei Nachbarn tauschen.
    Gibt neue Farben, Ereignisse und ob eine Kette nötig war zurück."""
    nbrs = [u for u in sorted(adj[v]) if colors[u] >= 0]
    if len(nbrs) > 5:
        raise ValueError("mehr als fünf gefärbte Nachbarn")
    used = {colors[u] for u in nbrs}
    free = [c for c in range(5) if c not in used]
    if free:
        c = free[0] if choose == "low" else free[-1] if choose == "high" else free[int(rng.integers(len(free)))]
        new = list(colors)
        new[v] = c
        return new, [Event("color", v, ((v, c),))], False
    around = neighbours_by_angle(pos, v, nbrs)
    for i, j in KEMPE_PAIRS:
        a, b = colors[around[i]], colors[around[j]]
        chain = kempe_chain(adj, colors, around[i], a, b)
        if around[j] not in chain:
            new = swap_chain(colors, chain, a, b)
            new[v] = a
            swapped = tuple((x, new[x]) for x in chain)
            return new, [Event("kempe", v, swapped, chain, (a, b)), Event("color", v, ((v, a),))], True
    raise HeawoodStuck(f"Knoten {v}")


def heawood_color(adj, pos, order=None, choose: str = "low", rng=None) -> HeawoodResult:
    """Heawood-Verfahren: Knoten in umgekehrter Entfernungsreihenfolge einfügen (Standard: Smallest-Last), jeder hat beim Einfügen höchstens fünf gefärbte Nachbarn."""
    order = list(order) if order is not None else smallest_last_order(adj)
    colors = [-1] * len(adj)
    events: list[Event] = []
    chains = needing = 0
    for v in reversed(order):
        colors, evs, needed = heawood_step(adj, pos, colors, v, choose, rng)
        events += evs
        needing += needed
        chains += sum(1 for e in evs if e.kind == "kempe")
    return HeawoodResult(colors, events, chains, needing)


@dataclass(frozen=True)
class ReduceResult:
    colors: list[int]
    events: list[Event]
    chains: int                  # getauschte Ketten
    remaining: int               # Knoten, die noch eine Farbe ab k haben
    success: bool


def try_free_color(adj, colors, v: int, c: int, k: int):
    """Versucht, die Farbe c rund um v freizustellen: Ketten (c, d) mit d < k tauschen, wenn sie die Zahl der Nachbarn mit Farbe c senken.
    Gibt (Erfolg, neue Farben, Tauschliste) zurück; bei Misserfolg unverändert."""
    work = list(colors)
    swaps: list[tuple[tuple[int, ...], int, int, tuple[tuple[int, int], ...]]] = []
    for _ in range(len(adj[v]) + 1):
        with_c = [u for u in sorted(adj[v]) if work[u] == c]
        if not with_c:
            return True, work, swaps
        improved = False
        for u in with_c:
            for d in range(k):
                if d == c:
                    continue
                chain = kempe_chain(adj, work, u, c, d)
                trial = swap_chain(work, chain, c, d)
                if sum(1 for w in adj[v] if trial[w] == c) < len(with_c):
                    swaps.append((chain, c, d, tuple((x, trial[x]) for x in chain)))
                    work = trial
                    improved = True
                    break
            if improved:
                break
        if not improved:
            return False, list(colors), []
    return False, list(colors), []


def kempe_reduce(adj, colors, k: int = 4, rounds: int = 30) -> ReduceResult:
    """Kempe-Reduktion: jeder Knoten mit einer Farbe ab k bekommt eine Farbe unter k, wenn sich diese durch Kettentausch rund um ihn freistellen lässt."""
    col = list(colors)
    events: list[Event] = []
    chains = 0
    for _ in range(rounds):
        todo = [v for v in range(len(adj)) if col[v] >= k]
        progress = False
        for v in todo:
            for c in range(k):
                ok, new, swaps = try_free_color(adj, col, v, c, k)
                if ok:
                    for chain, a, b, assigned in swaps:
                        events.append(Event("kempe", v, assigned, chain, (a, b)))
                    col = new
                    col[v] = c
                    events.append(Event("color", v, ((v, c),)))
                    chains += len(swaps)
                    progress = True
                    break
        if not progress:
            break
    remaining = sum(1 for c in col if c >= k)
    return ReduceResult(col, events, chains, remaining, remaining == 0)


@dataclass(frozen=True)
class ExactResult:
    status: str                  # "ja", "nein" oder "unentschieden" (Budget erreicht)
    colors: list[int] | None
    nodes: int


def colorable_k(adj, k: int, budget: int = 100_000) -> ExactResult:
    """Exakte Entscheidung „k-färbbar?“ durch DSATUR-Verzweigung. Bei Budgetende „unentschieden“ (nie „nein“)."""
    n = len(adj)
    colors = [-1] * n
    nodes = 0

    def pick() -> int:
        best, key = -1, None
        for v in range(n):
            if colors[v] >= 0:
                continue
            kk = (len({colors[u] for u in adj[v] if colors[u] >= 0}), len(adj[v]), -v)
            if key is None or kk > key:
                best, key = v, kk
        return best

    class Over(Exception):
        pass

    def rec(done: int, used: int) -> bool:
        nonlocal nodes
        nodes += 1
        if nodes > budget:
            raise Over
        if done == n:
            return True
        v = pick()
        forbidden = {colors[u] for u in adj[v] if colors[u] >= 0}
        for c in range(min(used + 1, k)):
            if c in forbidden:
                continue
            colors[v] = c
            if rec(done + 1, max(used, c + 1)):
                return True
            colors[v] = -1
        return False

    try:
        found = rec(0, 0)
    except Over:
        return ExactResult("unentschieden", None, nodes)
    return ExactResult("ja", list(colors), nodes) if found else ExactResult("nein", None, nodes)


def replay(n: int, events, upto: int) -> list[int]:
    """Farben nach den ersten `upto` Ereignissen (−1: noch ungefärbt)."""
    colors = [-1] * n
    for e in events[:max(0, upto)]:
        for x, c in e.assign:
            colors[x] = c
    return colors
