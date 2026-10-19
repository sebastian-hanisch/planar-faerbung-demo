# Planare Graphen färben – Vierfarbensatz, Kempe-Ketten, Greedy und exakt – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-planar-faerbung-demo.streamlit.app/)** -->

Zweites Stück der **Planarität-und-Zeichnen-Linie** (Graphentheorie) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“, Kante `fix` zum ersten Stück [planaritaet-demo](https://github.com/sebastian-hanisch/planaritaet-demo) (Karten als planare Instanzen, Delaunay-Generator). Verwandt: [graph-coloring-demo](https://github.com/sebastian-hanisch/graph-coloring-demo) (Greedy, DSATUR, exakte Färbung allgemein; dort steht „planar ≤ 4 nicht geprüft“, hier wird es geprüft).

Eine Karte lässt sich so färben, dass angrenzende Gebiete verschiedene Farben haben, und nach dem **Vierfarbensatz** genügen **vier** Farben. Fünf zu erreichen ist beweisbar einfach (Heawood 1890, mit **Kempe-Ketten**), die Vier zu finden ist schwerer. Die Demo färbt Karten aus zufälligen Standorten (Delaunay-Triangulierung) und Raster mit Greedy, DSATUR, dem **Heawood-Verfahren** und einer **Kempe-Reduktion** von fünf auf vier Farben und vergleicht sie mit einer exakten Entscheidung „vier Farben möglich?“. Eigene Löser in Python, `networkx` nur als Gegenprobe in den Tests.

## Warum dieses Problem

Frequenzen, Zuständigkeitsgebiete oder Kartenfarben dürfen sich an Grenzen nicht wiederholen: Gebiete sind Knoten, Nachbarschaft sind Kanten. Der Vierfarbensatz sagt, dass vier Farben für jede planare Karte reichen, aber nicht, wie man sie findet. Kernfrage: **welche Verfahren finden die Vier, was leisten Kempe-Ketten, und wo hilft der Satz dem Rechnen nicht?**

## Modell

Ein einfacher ungerichteter planarer Graph, geradlinig gezeichnet. **Greedy** färbt in der umgekehrten Smallest-Last-Reihenfolge, **DSATUR** nimmt den Knoten mit den meisten verschiedenen Nachbarfarben. **Heawood:** in Smallest-Last-Reihenfolge eingesetzt hat jeder Knoten höchstens fünf gefärbte Nachbarn; haben sie fünf verschiedene Farben, wird eine Kempe-Kette (Zusammenhangskomponente in zwei Farben) zwischen zwei Nachbarn im Umlauf getauscht: höchstens fünf Farben. **Kempe-Reduktion:** für jeden Knoten mit der fünften Farbe werden Ketten getauscht, bis eine der anderen Farben rund um ihn frei ist (Heuristik ohne Garantie). **Exakt:** DSATUR-Verzweigung mit Budget; bei Budgetende steht „unentschieden“, nie „nein“. Formeln und Literatur im Expander „📐 Mathematische Formulierung“ der App.

Netztypen (Kantenzahl = Dichte in Prozent von 3n − 6): **Karte** (Kanten der Delaunay-Triangulierung zufälliger Standorte, verdünnt) und **Raster** (Gitter mit Diagonalen). Dazu Lehrbuch-Graphen: Ikosaeder (Grad 5 überall), Oktaeder, K4, K5 minus eine Kante, K5 und Petersen-Graph.

## Methodik

- **Vergleich auf einer Karte:** alle vier Verfahren, unabhängiger Zulässigkeitsprüfer, Abspielen Schritt für Schritt (Kempe-Ketten hervorgehoben).
- **Messreihen:** (1) Anteil der Karten mit höchstens 4 Farben je Verfahren (volle Triangulierungen, n = 30 bis 300, je 20 feste Karten), (2) wie oft das Heawood-Verfahren eine Kette braucht (Karten, Ikosaeder in 30 zufälligen Reihenfolgen), (3) exakte Entscheidung gegen Kempe-Reduktion (n = 30 bis 200, Budget 100.000 Verzweigungsknoten) und 3-Färbbarkeit verdünnter Karten (55 % von 3n − 6 Kanten).

## Befunde (gemessen, keine Behauptungen)

| Frage | Befund | Test |
|---|---|---|
| Finden Greedy und DSATUR die Vier? | Mit wachsender Größe nicht mehr: DSATUR endet auf vier Farben bei n = 30 / 60 / 100 / 200 / 300 in 65 / 40 / 5 / 0 / 0 % der Karten, Greedy in 75 / 15 / 0 / 0 / 0 % (sonst fünf); der Vierfarbensatz garantiert vier für alle. | `test_four_table_shares` |
| Wie weit kommen die Kempe-Ketten? | Heawood mit anschließender Kempe-Reduktion bringt 100 / 95 / 95 / 90 / 90 % der Karten auf vier Farben; die übrigen bleiben bei fünf hängen (die Reduktion ist eine Heuristik). Heawood allein endet immer mit höchstens fünf Farben. Mittlere getauschte Ketten je Karte: 0,5 bei n = 30, rund 12 bei n = 300. | `test_four_table_shares`, `test_kempe_chains_per_map_grow_with_the_size` |
| Braucht das Heawood-Verfahren die Kette? | Auf zufälligen Karten **nie**: 0 von 60 Läufen, mit kleinster wie mit zufälliger freier Farbe. Am Ikosaeder (jeder Knoten Grad 5) in 8 von 30 zufälligen Reihenfolgen. | `test_heawood_needs_no_chain_on_random_maps_but_sometimes_on_the_icosahedron` |
| Wie schlägt sich die exakte Entscheidung? | Bei n = 200 beantwortet sie „4-färbbar?“ nur 16 von 20 Karten im Budget (4 unentschieden), die Kempe-Reduktion bringt 18 von 20 auf vier Farben; bei n = 30 sind es 20 von 20 (Median 31 Verzweigungsknoten), bei n = 100 Median 116,5. | `test_exact_decision_against_the_kempe_reduction` |
| Hilft der Satz bei drei Farben? | Nein: verdünnte Karten sind bei n = 60 in 19 von 20 Fällen 3-färbbar, bei n = 100 in 14 von 20 (2 unentschieden); 4-färbbar sind alle 20. | `test_three_colourability_of_thinned_maps` |
| Gilt der Satz für nichtplanare Graphen? | Nein: K5 braucht 5 Farben (exakt); der Petersen-Graph kommt mit 3 aus. | `test_k5_does_not_obey_the_four_colour_theorem`, `test_textbook_graph_table` |
| Wie färbt sich der Ikosaeder? | Kleinste Farbenzahl 4; Greedy, DSATUR und Heawood enden bei 5, Heawood mit Kempe-Reduktion bei 4. | `test_textbook_graph_table` |

## Ehrliche Grenzen

- **Die Kette ist selten nötig.** Der Beweis des Fünffarbensatzes braucht sie, die Praxis auf zufälligen Karten fast nie (0 von 60); erst Graphen mit Grad 5 überall (Ikosaeder) zwingen sie. Die Demo zeigt das und tut nicht so, als arbeite die Kette jedes Mal.
- **Die Kempe-Reduktion ist eine Heuristik.** Sie scheitert in einzelnen Fällen (5 bis 10 % der Karten ab n = 60), obwohl vier Farben nach dem Satz immer reichen. Kempes eigener Beweis des Vierfarbensatzes von 1879 war fehlerhaft.
- **Die exakte Entscheidung ist kein Maßstab für große Karten.** Im Budget bleibt sie ab n = 60 gelegentlich stecken; „unentschieden“ heißt nicht „nein“.
- **Keine Aussage zu Laufzeiten.** Verglichen werden Farbenzahlen und Anteile, keine Sekunden.
- **Die Stichprobe ist klein:** 20 feste Karten je Größe; die Anteile haben entsprechend Spielraum (Bänder in den Tests).

## Befunde und Korrekturen gegenüber dem Plan

- **Kempe-Reduktion:** die Vormessung im Einzelplan fand 19 / 20 bei n = 60, 20 / 20 bei 100, 19 / 20 bei 200, 18 / 20 bei 300; die Demo-Umsetzung (kürzere, deterministische Schleife) kommt auf 19 / 19 / 18 / 18 von 20 bei n = 60 / 100 / 200 / 300. Die Tendenz gilt, die Zahlen sind nicht vergleichbar.
- **Ikosaeder:** die Vormessung fand die Kette bei zufälliger Reihenfolge und zufälliger Farbwahl; mit „kleinste freie Farbe“ nie. Die Demo nimmt die zufällige Wahl über einen übergebenen Generator (`choose="random"`).
- **Raster:** wie in der Vormessung braucht jedes Raster mit Diagonalen drei Farben; es dient als Gegenprobe, nicht als Hauptvehikel.

## Verifikation

- **Kern gegen Handrechnung:** Verstöße, Farbenzahl, Smallest-Last-Ordnung, Greedy, DSATUR, Kempe-Kette, Tausch, Winkelordnung, ein Heawood-Schritt mit freier Farbe, mit erster und mit zweiter Kette, Abbruch auf K6, Kempe-Reduktion am Stern und an K5, exakte Entscheidung, Wiedergabe der Ereignisse (`tests/test_algorithm.py`).
- **Orakel:** `tests/test_oracle_planar_faerbung.py`: exakte Entscheidung gegen Brute Force aller Färbungen (120 kleine Graphen, k = 2, 3, 4), Kempe-Ketten gegen die Zusammenhangskomponenten des induzierten Teilgraphen (`networkx`), der Kettentausch hält jede Färbung zulässig (Satz), alle Verfahren zulässig innerhalb ihrer Garantie auf 150 planaren Instanzen (Smallest-Last ≤ 6, DSATUR ≤ Δ + 1, Heawood ≤ 5), die exakte Entscheidung sagt auf planaren Graphen nie „nein“ (Vierfarbensatz), bekannte chromatische Zahlen (Ikosaeder 4, K5 5, Petersen 3).
- **Mutationsprüfung** (`tools/mutate_demo.py`, Stand vor dem ersten Commit): 93 von 94 Stellen des Kerns gesichert (gefangen oder als äquivalent festgehalten, `tests/mutation_state.json`), keine offene Lücke; 1 Mutant ergab eine Endlosschleife (Zeitüberschreitung, zählt nicht). Die äquivalenten sind Sortierreihenfolgen, Schleifengrenzen und Konstanten, die das Ergebnis nicht ändern.
- **Randfälle:** leerer Graph, ein und zwei Knoten, isolierte Knoten, Gleichstände, alle Ecken der Regler, nichtplanare Eingabe (`tests/test_edge_cases.py`).
- **Verdikte** als reine Funktionen, jede Zahl und Schwelle (`tests/test_verdicts.py`); **Claims:** jede Zahl dieser README (`tests/test_claims.py`).
- **Szenario:** Generatoren planar und kreuzungsfrei, Hash-Seed-Unabhängigkeit, Lehrbuch-Graphen, Ikosaeder mit Dreiecksflächen im Umlauf (`tests/test_scenario.py`); Darstellung (`tests/test_visualization.py`); Presets halten, was ihre Hilfetexte sagen (`tests/test_presets.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an beiden Enden, jede Option der Auswahlfelder, jeder Schritt der Wiedergabe), Layout, Footer, Laufzeit-Importe.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `pfb_algorithm.py` | Kern: Greedy, DSATUR, Kempe-Kette, Heawood-Verfahren, Kempe-Reduktion, exakte Entscheidung, Wiedergabe |
| `pfb_constants.py` | Regler-Grenzen, Rechengrenzen, Farben, Presets |
| `pfb_evaluation.py` | Läufe der Verfahren, Messreihen, Verdikte, deutsche Zahlenformate |
| `pfb_layout.py` | Fester Kopf (Stylesheet) |
| `pfb_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste), Zufalls-Seed-Button |
| `pfb_scenario.py` | Instanzen: Karte, Raster, Lehrbuch-Graphen |
| `pfb_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest und networkx (Gegenprobe) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Handrechnung, Orakel, Randfälle, Verdikte, Claims, Szenario, Darstellung, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- Ein Beweis oder eine Nachrechnung des Vierfarbensatzes (nur Anwendung; die Computerbeweise von Appel und Haken und von Robertson, Sanders, Seymour und Thomas sind Literatur).
- Ein Verfahren, das nach Robertson u. a. in quadratischer Zeit eine Vierfärbung findet.
- Die Zeichnung der Einbettung aus dem Planaritätstest (die Karten haben ihre Lage aus den Standorten).
- Zufallsverbindungen und andere nichtplanare Instanzen als Vehikel (Heawood braucht eine kreuzungsfreie Zeichnung).

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy und SciPy (Delaunay-Triangulierung der Standorte).

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
