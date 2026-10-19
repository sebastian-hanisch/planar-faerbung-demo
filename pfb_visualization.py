"""Plotly-Figuren: gefärbter Graph, Abspielen der Ereignisse (Kempe-Ketten hervorgehoben), Messreihen. Alle Achsen fest (fixedrange)."""

from __future__ import annotations

import plotly.graph_objects as go

import pfb_algorithm as A
import pfb_constants as C


def _color(c: int) -> str:
    return C.COLOR_NONE if c < 0 else C.COLORS[c % len(C.COLORS)]


def _edge_trace(pos, edges, color, width):
    xs, ys = [], []
    for u, v in edges:
        xs += [pos[u][0], pos[v][0], None]
        ys += [pos[u][1], pos[v][1], None]
    return go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=color, width=width), hoverinfo="skip", showlegend=False)


def _layout(fig, title, height):
    fig.update_layout(
        title=dict(text=title, x=0, font=dict(size=14)) if title else None,
        height=height, margin=dict(l=10, r=10, t=40 if title else 10, b=10), showlegend=False, plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True, scaleanchor="x", scaleratio=1)
    return fig


def build_coloring(inst, colors, title=None, height=440, chain=(), focus=None):
    """Der Graph mit den Farben der Knoten; eine Kempe-Kette (Knotenliste) hervorgehoben, ein Knoten (`focus`) mit dickem Rand."""
    fig = go.Figure()
    chain_set = set(chain)
    link = [e for e in inst.edges if e[0] in chain_set and e[1] in chain_set]
    rest = [e for e in inst.edges if e not in set(link)]
    fig.add_trace(_edge_trace(inst.pos, rest, C.COLOR_EDGE, 2))
    if link:
        fig.add_trace(_edge_trace(inst.pos, link, C.COLOR_CHAIN, 5))
    labels = inst.n <= 40
    size = 24 if inst.n <= 40 else 13 if inst.n <= 100 else 9
    border = [4 if (v == focus or v in chain_set) else 1 for v in range(inst.n)]
    fig.add_trace(
        go.Scatter(
            x=[p[0] for p in inst.pos], y=[p[1] for p in inst.pos], mode="markers+text" if labels else "markers",
            marker=dict(color=[_color(c) for c in colors], size=size, line=dict(color=[C.COLOR_CHAIN if b > 1 else "white" for b in border], width=border)),
            text=[str(v) for v in range(inst.n)] if labels else None, textfont=dict(color="white", size=max(8, size - 12)), textposition="middle center",
            hovertext=[f"Knoten {v}: {'ungefärbt' if colors[v] < 0 else C.COLOR_NAMES[colors[v] % len(C.COLOR_NAMES)]}" for v in range(inst.n)], hoverinfo="text",
        )
    )
    return _layout(fig, title, height)


def build_playback(inst, run, step: int, title=None, height=440):
    """Zustand nach `step` Ereignissen; war das letzte Ereignis ein Kettentausch, ist die Kette hervorgehoben."""
    colors = A.replay(inst.n, run.events, step)
    last = run.events[step - 1] if 0 < step <= len(run.events) else None
    chain = last.chain if last is not None and last.kind == "kempe" else ()
    focus = last.vertex if last is not None else None
    return build_coloring(inst, colors, title, height, chain, focus)


def build_four(rows, title="Anteil der Karten mit höchstens 4 Farben"):
    fig = go.Figure()
    styles = (("greedy", "Greedy (Smallest-Last)", C.COLORS[0]), ("dsatur", "DSATUR", C.COLORS[1]), ("kempe", "Heawood + Kempe-Reduktion", C.COLORS[2]))
    for key, name, color in styles:
        fig.add_trace(go.Scatter(x=[r["n"] for r in rows], y=[r[key] * 100 for r in rows], mode="lines+markers", name=name, line=dict(color=color, width=3),
                                 hovertemplate="n = %{x}: %{y:.0f} %<extra>" + name + "</extra>"))
    fig.update_layout(title=dict(text=title, x=0, font=dict(size=14)), height=360, margin=dict(l=10, r=10, t=40, b=10), legend=dict(orientation="h", y=-0.25, x=0))
    fig.update_xaxes(title="Knoten n", fixedrange=True, type="log", tickmode="array", tickvals=[r["n"] for r in rows], ticktext=[str(r["n"]) for r in rows])
    fig.update_yaxes(title="mit höchstens 4 Farben (%)", fixedrange=True, range=[-3, 103])
    return fig


def build_exact(rows, title="Exakte Entscheidung gegen Kempe-Reduktion"):
    fig = go.Figure()
    xs = [f"n = {r['n']}" for r in rows]
    fig.add_trace(go.Bar(x=xs, y=[r["yes"] / r["samples"] * 100 for r in rows], name="exakt: 4-färbbar bewiesen", marker_color=C.COLORS[0]))
    fig.add_trace(go.Bar(x=xs, y=[r["undecided"] / r["samples"] * 100 for r in rows], name="exakt: unentschieden (Budget)", marker_color=C.COLORS[3]))
    fig.add_trace(go.Bar(x=xs, y=[r["kempe"] / r["samples"] * 100 for r in rows], name="Kempe-Reduktion: 4 Farben", marker_color=C.COLORS[2]))
    fig.update_layout(title=dict(text=title, x=0, font=dict(size=14)), height=360, barmode="group", margin=dict(l=10, r=10, t=40, b=10), legend=dict(orientation="h", y=-0.25, x=0))
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(title="Anteil der Karten (%)", fixedrange=True, range=[0, 105])
    return fig
