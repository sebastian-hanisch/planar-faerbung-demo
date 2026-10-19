"""Planare Graphen färben – Vierfarbensatz, Kempe-Ketten, Greedy und exakt - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Lauffähig mit: streamlit run app.py
"""

import numpy as np
import streamlit as st

import pfb_algorithm as A
import pfb_constants as C
import pfb_evaluation as ev
import pfb_scenario as S
from pfb_layout import dunkles_design, kopf_css
from pfb_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from pfb_visualization import build_coloring, build_exact, build_four, build_playback

st.set_page_config(page_title="Planare Graphen färben – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return ev.analyse(settings)


@st.cache_data(show_spinner=False)
def _four_rows():
    return ev.four_table()


@st.cache_data(show_spinner=False)
def _need():
    return ev.need_table()


@st.cache_data(show_spinner=False)
def _hand_rows():
    return ev.hand_table()


@st.cache_data(show_spinner=False)
def _exact_rows():
    return ev.exact_table(), ev.three_table()


@st.cache_data(show_spinner=False)
def _exact_one(settings):
    inst = S.make_instance(settings.net, settings.n, settings.density, settings.seed)
    return A.colorable_k(A.adjacency(inst.n, inst.edges), 4, C.EXACT_BUDGET)


@st.cache_data(show_spinner=False)
def _icosahedron_run(order_seed: int):
    ik = S.hand_graph("Ikosaeder")
    adj = A.adjacency(ik.n, ik.edges)
    rng = np.random.default_rng(order_seed)
    order = [int(x) for x in rng.permutation(ik.n)]
    h = A.heawood_color(adj, ik.pos, order=order, choose="random", rng=rng)
    return ik, order, h


def _event_text(events, step):
    """Ein Satz zum Schritt `step` (1 = erstes Ereignis)."""
    e = events[step - 1]
    if e.kind == "kempe":
        a, b = e.pair
        names = C.COLOR_NAMES
        return (
            f"Schritt {step}: Kempe-Kette aus {len(e.chain)} Knoten in den Farben {names[a % len(names)]} und {names[b % len(names)]} (dick umrandet) wird getauscht; "
            f"rund um Knoten {e.vertex} wird eine Farbe frei."
        )
    v, c = e.assign[0]
    return f"Schritt {step}: Knoten {v} bekommt die Farbe {C.COLOR_NAMES[c % len(C.COLOR_NAMES)]}."


def _playback(inst, run, key_prefix):
    """Schrittregler über die Ereignisse eines Laufs, Bild und ein Satz zum Schritt."""
    total = len(run.events)
    step = st.slider("Schritt", 0, total, total, key=f"{key_prefix}_step_{total}", help="0 = noch nichts gefärbt; der letzte Schritt zeigt das Ergebnis.")
    st.plotly_chart(build_playback(inst, run, step), width="stretch", key=f"{key_prefix}_play_{step}")
    if step:
        st.markdown(_event_text(run.events, step))
    else:
        st.caption("Vor dem ersten Schritt: noch kein Knoten gefärbt. Mit dem Regler vorwärts.")


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in pfb_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🎨 Planare Graphen färben – Vierfarbensatz, Kempe-Ketten, Greedy und exakt")
st.markdown(
    """
Karten lassen sich so färben, dass angrenzende Gebiete verschiedene Farben haben, und nach dem **Vierfarbensatz** reichen dafür **vier Farben** (Appel und Haken 1976). Eine Karte mit **fünf** Farben zu färben, ist beweisbar einfach (**Heawood 1890**, mit **Kempe-Ketten**), die **vier** zu finden ist schwerer.
Diese Demo färbt Karten aus Standorten mit Greedy, DSATUR, dem Heawood-Verfahren und einer **Kempe-Reduktion** von fünf auf vier Farben und zeigt, wo jedes Verfahren die Vier findet oder verfehlt. Zweites Stück der Linie *Planarität und Zeichnen*; es setzt auf die Karten und die Planaritätsprüfung des ersten Stücks (`planaritaet-demo`) auf.

Weiter unten: **🔬 Wie oft finden die Verfahren die Vier?**, **🔬 Wann braucht Heawood eine Kette?**, **🔬 Exakt oder Ketten?**, **🔬 Lehrbuch-Graphen**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktionieren die Verfahren", expanded=True):
    st.markdown(
        """
1. **Greedy** färbt die Knoten in der umgekehrten Smallest-Last-Reihenfolge (ein Knoten kleinsten Grades wird immer zuerst entfernt, am Ende zuletzt eingesetzt) mit der kleinsten freien Farbe. **DSATUR** nimmt jeweils den Knoten mit den meisten verschiedenen Nachbarfarben. Beide kennen die Planarität nicht.
2. **Heawood:** In einem planaren Graphen hat ein Knoten höchstens fünf Nachbarn, wenn man in Smallest-Last-Reihenfolge einsetzt. Sind darunter höchstens vier Farben, ist eine frei. Sonst ordnet man die fünf Nachbarn im Umlauf um den Knoten und prüft die **Kempe-Kette** (Knoten in zwei Farben, die zusammenhängen) zwischen dem ersten und dritten: Verbindet sie beide nicht, tauscht man ihre Farben, und eine Farbe wird frei. Verbindet sie beide, kann die Kette zwischen dem zweiten und vierten nicht verbinden (Planarität), und man tauscht diese. So reichen **fünf Farben**.
3. **Kempe-Reduktion:** Hat ein Knoten die fünfte Farbe, wird versucht, eine der vier anderen rund um ihn freizustellen, indem man Ketten tauscht, die die Zahl der Nachbarn mit dieser Farbe senken. Das gelingt oft, aber nicht immer (Kempes Beweis des Vierfarbensatzes von 1879 war fehlerhaft).
4. **Exakt:** eine Verzweigung nach DSATUR entscheidet „vier Farben möglich?“ und bricht bei einem festen Budget ab; dann bleibt die Antwort **unentschieden**, nie „nein“.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Karte**")
    net = st.selectbox("Netztyp", list(C.NET_TYPES), key="net_select", format_func=C.NET_TYPES.get, help=C.NET_HELP)
    n = st.slider("Knoten n", *bounds("n_slider"), key="n_slider", help="Zahl der Gebiete (bei einem Raster Zeile für Zeile gefüllt).")
    density = st.slider(C.DENSITY_LABEL, *bounds("density_slider"), key="density_slider", help="Zahl der Kanten als Anteil der Höchstzahl 3n − 6 eines planaren Graphen. 100 % entspricht beim Karten-Netz einer vollen Triangulierung.")
    seed = st.number_input("Zufalls-Seed der Instanz", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neue Instanz generieren", width="stretch", on_click=randomize_seed)
    st.markdown("**Verfahren**")
    method = st.selectbox("Verfahren", list(C.METHODS), key="method_select", format_func=C.METHODS.get, help=C.METHOD_HELP)

sync_query_params({"net_select": net, "n_slider": int(n), "density_slider": int(density), "seed_input": int(seed), "method_select": method})

settings = ev.Settings(net, int(n), int(density), int(seed), method)
a = _analysis(settings)
inst, run = a.inst, a.run

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Knoten n", f"{inst.n}")
m2.metric("Kanten m", f"{inst.m}", delta=f"Grad bis {a.max_degree}", delta_color="off", help="Zahl der Kanten; darunter der größte Grad im Graphen.")
m3.metric("Farben", f"{run.n_colors}", delta="Satz: 4 genügen", delta_color="off", help="Zahl der verwendeten Farben. Der Vierfarbensatz garantiert, dass vier genügen.")
m4.metric("Ketten", f"{run.chains}", delta="Kempe-Ketten", delta_color="off", help=f"Zahl der getauschten Kempe-Ketten (nur Heawood und Kempe-Reduktion). Beim Heawood-Verfahren hatten {run.needing} Knoten fünf verschiedene Nachbarfarben.")
kind, text = ev.verdict_coloring(a)
getattr(st, kind)(text)
kind, text = ev.verdict_chains(a)
getattr(st, kind)(text)
st.plotly_chart(build_coloring(inst, run.colors, title=f"{inst.name}: {inst.n} Knoten, {inst.m} Kanten, {run.n_colors} Farben"), width="stretch", key="main_graph")
st.caption("Jede Kante verbindet zwei verschieden gefärbte Gebiete (unabhängig geprüft: " + ("keine Kante mit gleichfarbigen Enden" if not run.violations else "**Verstoß**") + ").")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wer findet die Vier, und was leisten die Ketten?")
st.markdown("### Das gewählte Verfahren, Schritt für Schritt")
_playback(inst, run, "main")

st.markdown("### Alle Verfahren auf derselben Karte")
table = [
    {"Verfahren": C.METHODS[key], "Farben": str(r.n_colors), "Getauschte Ketten": str(r.chains) if key in ("heawood", "kempe") else "-", "Zulässig": "ja" if not r.violations else "nein"}
    for key, r in a.runs.items()
]
if not inst.planar:
    table.append({"Verfahren": "Heawood und Kempe-Reduktion", "Farben": "-", "Getauschte Ketten": "-", "Zulässig": "nicht planar: nicht anwendbar"})
st.dataframe(table, hide_index=True, width="stretch")

if st.button("🧮 Exakt prüfen: sind vier Farben möglich?", key="run_exact_one"):
    with st.spinner("Verzweige …"):
        st.session_state["exact_one"] = (settings, _exact_one(settings))
stored = st.session_state.get("exact_one")
if stored and stored[0] == settings:
    r = stored[1]
    if r.status == "ja":
        st.success(f"Exakt bewiesen: Die Karte ist 4-färbbar ({ev.num(r.nodes)} Verzweigungsknoten).")
    elif r.status == "nein":
        st.error(f"Exakt bewiesen: Die Karte ist **nicht** 4-färbbar ({ev.num(r.nodes)} Verzweigungsknoten); das widerspräche dem Vierfarbensatz, falls der Graph planar ist.")
    else:
        st.info(f"Unentschieden: Im Budget von {ev.num(C.EXACT_BUDGET)} Knoten ist keine Antwort herausgekommen. Das heißt nicht „nein“: Nach dem Vierfarbensatz ist jede planare Karte 4-färbbar.")

st.markdown("---")

# --- Experiment 1 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Wie oft finden die Verfahren die Vier?")
st.caption(f"Volle Delaunay-Karten, je Größe {len(C.SWEEP_SEEDS)} feste Instanzen. Der Vierfarbensatz garantiert vier Farben für alle; die Frage ist, welches Verfahren sie findet.")
with st.spinner("Rechne die Messreihe …"):
    four = _four_rows()
st.plotly_chart(build_four(four), width="stretch", key="four_chart")
kind, text = ev.verdict_four(four)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 2 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Wann braucht Heawood eine Kette?")
st.caption("Das Heawood-Verfahren braucht eine Kette nur, wenn ein Knoten beim Einsetzen fünf Nachbarn mit fünf verschiedenen Farben hat.")
with st.spinner("Zähle die Ketten …"):
    need = _need()
st.dataframe(
    [{"Graph": f"Karte mit {m['n']} Knoten", "Läufe": str(m["samples"]), "mit Kette (kleinste freie Farbe)": str(m["low"]), "mit Kette (zufällige freie Farbe)": str(m["random"])} for m in need["maps"]]
    + [{"Graph": "Ikosaeder (zufällige Reihenfolgen)", "Läufe": str(need["icosahedron"]["orders"]), "mit Kette (kleinste freie Farbe)": "-", "mit Kette (zufällige freie Farbe)": str(need["icosahedron"]["needing"])}],
    hide_index=True, width="stretch",
)
kind, text = ev.verdict_need(need)
getattr(st, kind)(text)
st.markdown("**Der Ikosaeder in zufälliger Reihenfolge** (jeder Knoten hat Grad 5): Reihenfolge wählen und die Kette suchen.")
order_seed = st.slider("Reihenfolge Nr.", 0, C.ICOSAHEDRON_ORDERS - 1, 0, key="ik_seed", help="Welche der zufälligen Reihenfolgen und Farbwahlen; manche brauchen eine Kette, die meisten nicht.")
ik, order, h = _icosahedron_run(order_seed)
ik_run = ev.Run("heawood", h.colors, h.events, A.color_count(h.colors), len(A.violations(A.adjacency(ik.n, ik.edges), h.colors)), h.chains, h.needing)
_playback(ik, ik_run, "ik")
st.caption(f"Reihenfolge der Einfügung (rückwärts gelesen): {', '.join(map(str, reversed(order)))}. Ketten getauscht: {h.chains}; Farben: {ik_run.n_colors}.")

st.markdown("---")

# --- Experiment 3 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Exakt oder Ketten?")
st.caption(
    f"Die exakte Entscheidung „4-färbbar?“ (Verzweigung nach DSATUR, Budget {ev.num(C.EXACT_BUDGET)} Knoten) gegen die Kempe-Reduktion, dazu verdünnte Karten, bei denen schon drei Farben die Frage sind. Das Rechnen dauert einen Moment und läuft nur auf Klick."
)
if st.button("📊 Messreihen rechnen", key="run_exact"):
    with st.spinner("Rechne die Messreihen …"):
        st.session_state["exact_rows"] = _exact_rows()
if "exact_rows" in st.session_state:
    exact, three = st.session_state["exact_rows"]
    st.plotly_chart(build_exact(exact), width="stretch", key="exact_chart")
    kind, text = ev.verdict_exact(exact)
    getattr(st, kind)(text)
    kind, text = ev.verdict_three(three)
    getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 4 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Lehrbuch-Graphen")
st.caption("Kleine Graphen mit ihrer kleinsten Farbenzahl (exakt bestimmt) und den Farben der Verfahren. Der Vierfarbensatz gilt nur für planare Graphen: K5 braucht fünf.")
hand = st.selectbox("Graph", C.HAND_GRAPHS, index=C.HAND_GRAPHS.index(C.DEFAULT_HAND), key="hand_select")
hand_rows = _hand_rows()
st.dataframe(
    [
        {"Graph": r["name"], "Planar": "ja" if r["planar"] else "nein", "Knoten": str(r["n"]), "Kanten": str(r["m"]), "Kleinste Farbenzahl": str(r["chi"]), "Greedy": str(r["greedy"]), "DSATUR": str(r["dsatur"]),
         "Heawood": str(r["heawood"]) if r["heawood"] is not None else "-", "Heawood + Kempe": str(r["kempe"]) if r["kempe"] is not None else "-"}
        for r in hand_rows
    ],
    hide_index=True, width="stretch",
)
ha = ev.analyse_instance(S.hand_graph(hand), "kempe" if S.hand_graph(hand).planar else "dsatur")
st.plotly_chart(build_coloring(ha.inst, ha.run.colors, title=f"{hand}: {ha.run.n_colors} Farben ({C.METHODS[ha.run.method]})", height=360), width="stretch", key="hand_graph")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Der Graph ist planar** | Der Vierfarbensatz und das Heawood-Verfahren brauchen es. K5 braucht fünf Farben; bei einer nichtplanaren Zeichnung wäre die Nachbarreihenfolge um einen Knoten falsch (Heawood bricht dann ab oder liefert zu viele Farben). | - |
| **Die Zeichnung ist geradlinig und kreuzungsfrei** | Heawood ordnet die Nachbarn nach dem Winkel in der Zeichnung; nur dann ist das die Reihenfolge der Einbettung. Die Karten und Raster dieser Demo erfüllen es. | - |
| **Die Kempe-Reduktion findet immer vier** | Nein: sie ist eine Heuristik. Auf Karten bleibt sie in einzelnen Fällen bei fünf Farben hängen (siehe Messreihe); der Vierfarbensatz garantiert vier, aber nicht, dass diese Ketten sie finden. | - |
| **Die exakte Entscheidung kommt immer zum Ende** | Nein: bei größeren Karten bleibt sie im Budget stecken und meldet „unentschieden“, nie „nein“. | - |
| **Drei Farben reichen oft** | Ob drei reichen, ist auch für planare Graphen schwer; der Satz sagt dazu nichts. | - |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben** ein einfacher ungerichteter planarer Graph $G=(V,E)$; **gesucht** eine Färbung $c: V \to \{0,1,\dots\}$ mit $c(u)\ne c(v)$ für jede Kante $uv\in E$ und möglichst wenigen Farben.

| Symbol | Bedeutung |
|---|---|
| $\chi(G)$ | kleinste Farbenzahl, mit der eine zulässige Färbung gelingt |
| $d(v)$ | Grad von $v$ |
| Kempe-Kette | Zusammenhangskomponente des Teilgraphen der Knoten mit den Farben $a$ oder $b$ |
| Smallest-Last-Ordnung | Reihenfolge $v_1,\dots,v_n$, in der $v_i$ ein Knoten kleinsten Grades in $G-\{v_1,\dots,v_{i-1}\}$ ist |

**Vierfarbensatz.** Jeder planare Graph ist 4-färbbar: $\chi(G)\le 4$. Die Aussage gilt nur für planare Graphen: $\chi(K_5)=5$.

**Fünffarbensatz (Heawood 1890).** Ein planarer Graph hat einen Knoten vom Grad höchstens 5 (aus $m\le 3n-6$). Entfernt man ihn, färbt den Rest rekursiv und setzt ihn wieder ein, sind seine höchstens fünf Nachbarn mit höchstens fünf Farben gefärbt. Sind es fünf verschiedene, seien $v_1,\dots,v_5$ die Nachbarn im Umlauf mit den Farben $1,\dots,5$. Verbindet die Kette der Farben 1 und 3 ab $v_1$ nicht $v_1$ mit $v_3$, tauscht man sie, und Farbe 1 wird frei. Sonst trennt diese Kette (mit $v$) $v_2$ von $v_4$ und $v_5$, und die Kette der Farben 2 und 4 ab $v_2$ erreicht $v_4$ nicht: tauschen, Farbe 2 wird frei. Also $\chi(G)\le 5$.

**Smallest-Last-Greedy.** Jeder Knoten hat beim Einsetzen höchstens $5$ gefärbte Nachbarn, also genügen 6 Farben.

**Kempe-Reduktion.** Zu einem Knoten $v$ mit der fünften Farbe wird für eine Farbe $c<4$ wiederholt eine Kette $(c,d)$ getauscht, wenn dadurch die Zahl der Nachbarn von $v$ mit der Farbe $c$ sinkt; ist sie null, bekommt $v$ die Farbe $c$. Das ist eine Heuristik ohne Garantie.

**Exakte Entscheidung.** Verzweigung: wähle den ungefärbten Knoten mit den meisten verschiedenen Nachbarfarben, probiere jede erlaubte Farbe (höchstens eine neue je Schritt, um Symmetrie zu brechen). Bei Budgetende lautet das Ergebnis „unentschieden“.

**Literatur.** A. B. Kempe, *On the geographical problem of the four colours*, American Journal of Mathematics 2 (1879), 193–200. P. J. Heawood, *Map-colour theorem*, Quarterly Journal of Pure and Applied Mathematics 24 (1890), 332–338 (der Titel der Zeitschrift wird in Quellen teils abweichend angegeben); Heawood fand den Fehler in Kempes Beweis des Vierfarbensatzes und rettete den Fünffarbensatz. K. Appel, W. Haken, *Every planar map is four colorable, Part I: Discharging*, Illinois Journal of Mathematics 21 (1977), 429–490 (Teil II „Reducibility“ im selben Band). N. Robertson, D. Sanders, P. Seymour, R. Thomas, *A new proof of the four-colour theorem*, Electronic Research Announcements of the AMS 2 (1996), 17–25. M. R. Garey, D. S. Johnson, L. Stockmeyer, *Some simplified NP-complete graph problems*, Theoretical Computer Science 1 (1976), 237–267 (die 3-Färbbarkeit planarer Graphen ist NP-vollständig). Die Angaben wurden per Suche gegen Bibliografie-Einträge geprüft, die Originalarbeiten nicht gelesen.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
