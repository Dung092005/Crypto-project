"""End-to-end AppTest coverage of the multipage Defense Lab."""

from dataclasses import fields
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from broadcastguard.defense_lab import DefenseComparison
from broadcastguard.ui.defense_presenter import (
    DEFENSE_PRESETS,
    comparison_rows,
    defense_message_bytes,
    recipient_comparison_rows,
)

APP = Path(__file__).resolve().parents[1] / "app.py"
DEFENSE = "app_pages/defense_lab.py"
ATTACK = "app_pages/attack_lab.py"


def open_app() -> AppTest:
    app = AppTest.from_file(APP, default_timeout=90).run()
    assert not list(app.exception)
    return app


def open_defense() -> AppTest:
    app = open_app().switch_page(DEFENSE).run()
    assert not list(app.exception)
    return app


def run_comparison(app: AppTest) -> DefenseComparison:
    app.button[0].click().run()
    assert not list(app.exception)
    result = app.session_state["defense_comparison"]
    assert isinstance(result, DefenseComparison)
    return result


def test_router_defaults_to_attack_and_defense_has_sections() -> None:
    app = open_app()
    assert app.title[0].value == "Can RSA be broken without a private key?"
    assert app.session_state["scenario"] is None
    app.switch_page(DEFENSE).run()
    assert not list(app.exception)
    assert app.title[0].value == "How can we defend against RSA Broadcast Attack?"
    assert [item.value for item in app.header] == [
        "01 / Controlled experiment", "02 / Before vs after",
        "03 / Same keys, fair comparison", "04 / Eve tries the same attack",
        "05 / OAEP randomization experiment", "06 / Legitimate recipient verification",
        "07 / Educational takeaways",
    ][:len(app.header)]  # Empty state only renders the first section.
    assert app.session_state["defense_comparison"] is None
    assert any("bấm Run Defense Comparison" in item.value for item in app.info)


def test_preset_and_utf8_validation() -> None:
    assert [len(value) for value in DEFENSE_PRESETS.values()] == [1, 96, 180, 190]
    assert all(value == b"B" * len(value) for value in DEFENSE_PRESETS.values())
    assert defense_message_bytes("Custom message", "", "é" * 95) == ("é" * 95).encode()
    with pytest.raises(ValueError, match="192 byte"):
        defense_message_bytes("Custom message", "", "é" * 96)
    with pytest.raises(ValueError, match="để trống"):
        defense_message_bytes("Custom message", "", "")
    with pytest.raises(ValueError, match="phải là văn bản"):
        defense_message_bytes("Custom message", "", 5)  # type: ignore[arg-type]


def test_real_comparison_uses_identical_keys_and_separates_outcomes() -> None:
    app = open_defense()
    app.selectbox[0].set_value("Long · 180 bytes").run()
    result = run_comparison(app)
    assert len(result.scenario.plaintext) == 180
    assert len(result.scenario.textbook_observations) == 3
    assert all(
        raw.public.n == padded.public.n and raw.public.e == padded.public.e == 3
        and raw.public.modulus_bits == padded.public.modulus_bits == 2048
        for raw, padded in zip(result.scenario.textbook_observations,
                               result.scenario.oaep_observations)
    )
    assert result.textbook.status == "recovered" and result.textbook.recovered_original
    assert result.oaep.status != "recovered" and not result.oaep.recovered_original
    assert all(item.recovered_original_bytes for item in result.decryptions)
    assert result.randomization.textbook_ciphertexts_identical
    assert result.randomization.oaep_ciphertexts_distinct
    assert result.randomization.oaep_all_decrypt
    assert [row["Scheme"] for row in comparison_rows(result)] == ["Textbook RSA", "RSA-OAEP SHA-256"]
    assert len(recipient_comparison_rows(result)) == 3
    assert len(app.dataframe) == 2
    assert app.dataframe[1].value.shape[0] == 3
    assert [item.value for item in app.header] == [
        "01 / Controlled experiment", "02 / Before vs after",
        "03 / Same keys, fair comparison", "04 / Eve tries the same attack",
        "05 / OAEP randomization experiment", "06 / Legitimate recipient verification",
        "07 / Educational takeaways",
    ]
    assert all(field.name != "private_keys" for field in fields(result))


def test_boundary_190_bytes_and_reject_191_without_replacing_result() -> None:
    app = open_defense()
    app.selectbox[0].set_value("Boundary · 190 bytes").run()
    result = run_comparison(app)
    assert len(result.scenario.plaintext) == 190
    app.radio[0].set_value("Custom message").run()
    assert any("để trống" in item.value for item in app.error)
    app.button[0].click().run()
    assert app.session_state["defense_comparison"] is result
    app.text_area[0].set_value("B" * 191).run()
    assert any("191 byte" in item.value for item in app.error)
    app.button[0].click().run()
    assert app.session_state["defense_comparison"] is result
    assert not list(app.exception)


def test_switching_pages_preserves_attack_and_defense_results() -> None:
    app = open_app()
    app.button[0].click().run()
    attack_scenario = app.session_state["scenario"]
    app.switch_page(DEFENSE).run()
    defense_result = run_comparison(app)
    app.switch_page(ATTACK).run()
    assert app.session_state["scenario"] is attack_scenario
    assert app.title[0].value == "Can RSA be broken without a private key?"
    app.switch_page(DEFENSE).run()
    assert app.session_state["defense_comparison"] is defense_result
    assert app.session_state["defense_run_number"] == 1


def test_navigation_and_widget_reruns_do_not_regenerate_keys() -> None:
    app = open_defense()
    result = run_comparison(app)
    moduli = tuple(item.public.n for item in result.scenario.textbook_observations)
    app.selectbox[0].set_value("Medium · 96 bytes").run()
    assert app.session_state["defense_comparison"] is result
    assert tuple(item.public.n for item in app.session_state["defense_comparison"].scenario.textbook_observations) == moduli
    assert app.session_state["defense_run_number"] == 1
    assert any("Bản nháp đã đổi" in item.value for item in app.info)


def test_custom_utf8_input_runs_without_changing_bytes() -> None:
    app = open_defense()
    app.radio[0].set_value("Custom message").run()
    app.text_area[0].set_value("Xin chào").run()
    result = run_comparison(app)
    assert result.scenario.plaintext == "Xin chào".encode("utf-8")
    assert result.textbook.recovered_original
    assert all(item.recovered_original_bytes for item in result.decryptions)


def test_sessions_are_isolated() -> None:
    first = open_defense()
    first_result = run_comparison(first)
    second = open_defense()
    assert second.session_state["defense_comparison"] is None
    second_result = run_comparison(second)
    assert second_result is not first_result
    assert first.session_state["defense_comparison"] is first_result
    assert tuple(item.public.n for item in second_result.scenario.textbook_observations) != (
        tuple(item.public.n for item in first_result.scenario.textbook_observations)
    )
