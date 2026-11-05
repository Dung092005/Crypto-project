"""Real Streamlit AppTest interactions against the reviewed Attack Lab backend."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from broadcastguard.attack_lab import AttackScenario, PublicObservation
from broadcastguard.conditions_analyzer import analyze_scenario
from broadcastguard.ui.attack_presenter import PRESETS, message_bytes, readable_message


APP = Path(__file__).resolve().parents[1] / "app.py"


def open_app() -> AppTest:
    app = AppTest.from_file(APP, default_timeout=60).run()
    assert not list(app.exception)
    return app


def generate(app: AppTest) -> AppTest:
    app.button[0].click().run()
    assert not list(app.exception)
    assert app.session_state["scenario"] is not None
    return app


def attack(app: AppTest, selected: list[str]) -> AppTest:
    app.multiselect[0].set_value(selected).run()
    app.button[1].click().run()
    assert not list(app.exception)
    return app


def test_startup_sections_and_disabled_attack() -> None:
    app = open_app()
    assert app.title[0].value == "Can RSA be broken without a private key?"
    assert [item.value for item in app.header] == [
        "01 / Sender simulator", "02 / Alice, Bob and Charlie",
        "03 / Eve attack simulator", "04 / Mathematical walkthrough",
        "05 / Attack conditions analyzer",
    ]
    assert app.button[1].disabled
    assert app.session_state["scenario"] is None


def test_preset_bytes_are_exact_and_custom_limit_is_utf8() -> None:
    assert [len(item) for item in PRESETS.values()] == [1, 96, 180]
    assert all(item == b"B" * len(item) for item in PRESETS.values())
    assert message_bytes("Custom message", "", "é" * 95) == ("é" * 95).encode()
    with pytest.raises(ValueError, match="192 byte"):
        message_bytes("Custom message", "", "é" * 96)
    with pytest.raises(ValueError, match="để trống"):
        message_bytes("Custom message", "", "")
    assert readable_message(b"\x00\xff")[0] == "Hex preview"


def test_generate_and_all_seven_subsets_use_one_scenario() -> None:
    app = generate(open_app())
    scenario = app.session_state["scenario"]
    assert len(scenario.observations) == 3
    assert len(scenario.plaintext) == 1
    assert all(item.modulus_bits == 2048 and item.e == 3 for item in scenario.observations)
    assert app.dataframe[0].value.shape == (7, 7)
    assert app.dataframe[0].value["Subset"].tolist() == [
        "Alice", "Bob", "Charlie", "Alice + Bob", "Alice + Charlie",
        "Bob + Charlie", "Alice + Bob + Charlie",
    ]
    before = tuple(item.n for item in scenario.observations)
    app.multiselect[0].set_value(["Bob", "Charlie"]).run()
    assert tuple(item.n for item in app.session_state["scenario"].observations) == before
    assert app.session_state["scenario_analysis"] is not None


def test_separate_streamlit_sessions_do_not_share_scenarios() -> None:
    first = generate(open_app())
    first_scenario = first.session_state["scenario"]
    second = open_app()
    assert second.session_state["scenario"] is None
    generate(second)
    assert second.session_state["scenario"] is not first_scenario
    assert tuple(item.n for item in second.session_state["scenario"].observations) != (
        tuple(item.n for item in first_scenario.observations)
    )
    assert first.session_state["scenario"] is first_scenario


def test_one_two_three_ciphertexts_and_recovery_status() -> None:
    app = generate(open_app())  # B: one ciphertext already satisfies M³ < n.
    original_moduli = tuple(item.n for item in app.session_state["scenario"].observations)
    for selected in (["Alice"], ["Bob", "Charlie"], ["Alice", "Bob", "Charlie"]):
        attack(app, selected)
        outcome = app.session_state["attack_outcome"]
        evaluation = app.session_state["attack_evaluation"]
        assert outcome.used_count == len(selected)
        assert set(outcome.recipient_ids) == set(selected)
        assert evaluation.status == "recovered" and evaluation.matches_original
        assert any("Recovered" in item.value for item in app.success)
        assert tuple(item.n for item in app.session_state["scenario"].observations) == original_moduli


def test_medium_and_long_thresholds_and_reset_on_generate() -> None:
    app = open_app()
    app.selectbox[0].set_value("Medium · 96 bytes").run()
    generate(app)
    attack(app, ["Alice"])
    assert app.session_state["attack_evaluation"].status != "recovered"
    attack(app, ["Bob", "Charlie"])
    assert app.session_state["attack_evaluation"].status == "recovered"
    previous = app.session_state["scenario"]

    app.selectbox[0].set_value("Long · 180 bytes").run()
    assert app.session_state["scenario"] is previous
    assert app.session_state["attack_evaluation"] is not None
    assert any("bản nháp" in item.value for item in app.info)
    generate(app)
    assert app.session_state["scenario"] is not previous
    assert len(app.session_state["scenario"].plaintext) == 180
    assert app.session_state["attack_evaluation"] is None
    assert app.session_state["attack_outcome"] is None
    attack(app, ["Alice", "Charlie"])
    assert app.session_state["attack_evaluation"].status != "recovered"
    attack(app, ["Alice", "Bob", "Charlie"])
    assert app.session_state["attack_evaluation"].status == "recovered"


def test_empty_subset_and_invalid_custom_input() -> None:
    app = generate(open_app())
    app.multiselect[0].set_value([]).run()
    app.button[1].click().run()
    assert app.session_state["attack_outcome"] is None
    assert any("ít nhất một ciphertext" in item.value for item in app.warning)

    app.radio[0].set_value("Custom message").run()
    assert any("để trống" in item.value for item in app.error)
    app.button[0].click().run()
    assert app.session_state["scenario"] is not None  # Invalid draft did not replace it.
    app.text_area[0].set_value("é" * 96).run()
    assert any("192 byte" in item.value for item in app.error)
    app.button[0].click().run()
    assert len(app.session_state["scenario"].plaintext) == 1
    assert not list(app.exception)


def test_custom_utf8_message_and_message_length_sweep_once() -> None:
    app = open_app()
    app.radio[0].set_value("Custom message").run()
    app.text_area[0].set_value("Xin chào").run()
    generate(app)
    assert app.session_state["scenario"].plaintext == "Xin chào".encode("utf-8")
    app.button[2].click().run()
    sweep = app.session_state["length_sweep"]
    assert sweep is not None and len(sweep.analyses) == 3
    assert [row.message_length for row in sweep.analyses] == [1, 96, 180]
    assert [row.minimum_successful_count for row in sweep.analyses] == [1, 2, 3]
    assert app.dataframe[1].value.shape[0] == 3
    app.multiselect[0].set_value(["Bob"]).run()
    assert app.session_state["length_sweep"] is sweep


def test_wrong_exact_root_is_not_shown_as_recovered() -> None:
    # A deterministic miniature scenario exercises a status rare with RSA-2048.
    message = 2
    observations = tuple(
        PublicObservation(name, n, 3, pow(message, 3, n))
        for name, n in zip(("Alice", "Bob", "Charlie"), (7, 11, 13))
    )
    scenario = AttackScenario(b"\x02", observations)
    app = open_app()
    app.session_state["scenario"] = scenario
    app.session_state["scenario_analysis"] = analyze_scenario(scenario)
    app.session_state["intercepts"] = ["Alice"]
    app.run()
    app.button[1].click().run()
    assert not list(app.exception)
    assert app.session_state["attack_outcome"].exact
    assert app.session_state["attack_evaluation"].status == "wrong_exact_root"
    assert not app.session_state["attack_evaluation"].matches_original
    assert any("Wrong exact root" in item.value for item in app.warning)
