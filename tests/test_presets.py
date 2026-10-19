"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, und was die Hilfetexte über das Ergebnis behaupten."""

import pfb_constants as C
import pfb_evaluation as ev
import pfb_presets as P
import pfb_scenario as S


def _analysis(name):
    return ev.analyse(ev.Settings(**C.PRESETS[name]))


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_bounds():
    for preset in C.PRESETS.values():
        assert preset["net"] in C.NET_TYPES and preset["method"] in C.METHODS
        assert C.N_MIN <= preset["n"] <= C.N_MAX and C.DENSITY_MIN <= preset["density"] <= C.DENSITY_MAX and 0 <= preset["seed"] <= C.SEED_MAX


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS["Lehrbeispiel: eine Karte"]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_the_textbook_map_ends_with_four_colours_and_needs_at_least_one_chain():
    a = _analysis("Lehrbeispiel: eine Karte")
    assert a.run.method == "kempe" and a.run.n_colors == 4 and a.run.violations == 0 and a.run.chains >= 1


def test_dsatur_misses_the_four_and_the_chains_find_it_on_the_same_map():
    """Die zwei Presets gleicher Karte: DSATUR 5 Farben, Heawood + Kempe-Reduktion 4 (die Aussage ihrer Hilfetexte)."""
    dsatur, kempe = _analysis("DSATUR verpasst die Vier"), _analysis("Kempe-Ketten holen sie zurück")
    assert dsatur.inst == kempe.inst
    assert dsatur.run.n_colors == 5 and kempe.run.n_colors == 4 and kempe.run.chains >= 1


def test_heawood_preset_uses_five_colours_and_no_chain():
    a = _analysis("Heawood: fünf Farben genügen")
    assert a.run.method == "heawood" and a.run.n_colors == 5 and a.run.chains == 0


def test_the_grid_preset_needs_only_three_colours():
    a = _analysis("Raster mit Diagonalen")
    assert a.run.n_colors == 3 and all(r.n_colors == 3 for r in a.runs.values())


def test_randomize_seed_stays_inside_the_bounds():
    import streamlit as st

    st.session_state.clear()
    P.randomize_seed()
    assert 0 <= st.session_state["seed_input"] <= C.SEED_MAX


def test_hand_graph_names_are_all_defined():
    for name in C.HAND_GRAPHS:
        assert S.hand_graph(name).n >= 4
    assert C.DEFAULT_HAND in C.HAND_GRAPHS
