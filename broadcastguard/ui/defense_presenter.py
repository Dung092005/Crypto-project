"""Pure presentation helpers for the controlled RSA-OAEP comparison."""

from broadcastguard.defense_lab import DefenseComparison, DefenseStatus, OAEP_MAX_MESSAGE_BYTES
from broadcastguard.ui.attack_presenter import preview_integer

DEFENSE_PRESETS: dict[str, bytes] = {
    "Short · 1 byte": b"B",
    "Medium · 96 bytes": b"B" * 96,
    "Long · 180 bytes": b"B" * 180,
    "Boundary · 190 bytes": b"B" * 190,
}

DEFENSE_STATUS_LABELS: dict[DefenseStatus, str] = {
    "recovered": "Recovered original",
    "wrong_exact_root": "Wrong exact root",
    "no_exact_root": "No exact root",
    "invalid_input": "Invalid observation",
}


def defense_message_bytes(mode: str, preset: str, custom_text: str) -> bytes:
    """Validate UTF-8 bytes without truncation or normalization."""
    if mode == "Preset samples":
        try:
            data = DEFENSE_PRESETS[preset]
        except KeyError as error:
            raise ValueError("Mẫu thông điệp không hợp lệ.") from error
    elif mode == "Custom message":
        if not isinstance(custom_text, str):
            raise ValueError("Thông điệp phải là văn bản UTF-8.")
        data = custom_text.encode("utf-8")
    else:
        raise ValueError("Chế độ nhập thông điệp không hợp lệ.")
    if not data:
        raise ValueError("Thông điệp không được để trống.")
    if len(data) > OAEP_MAX_MESSAGE_BYTES:
        raise ValueError(
            f"Thông điệp dài {len(data)} byte; RSA-2048/OAEP-SHA256 chỉ nhận tối đa "
            f"{OAEP_MAX_MESSAGE_BYTES} byte."
        )
    return data


def comparison_rows(comparison: DefenseComparison) -> list[dict[str, object]]:
    """Small, semantic rows without large integers or private material."""
    return [
        {
            "Scheme": "Textbook RSA" if row["scheme"] == "textbook" else "RSA-OAEP SHA-256",
            "Eve candidate": row["attack_candidate_preview"] or "—",
            "Exact root": row["exact_root"],
            "Recovered original": row["recovered_original"],
            "Legitimate decryption": row["legitimate_decryption"],
            "Status": DEFENSE_STATUS_LABELS[row["status"]],
        }
        for row in comparison.summary_rows()
    ]


def recipient_comparison_rows(comparison: DefenseComparison) -> list[dict[str, object]]:
    textbook = {item.recipient_id: item for item in comparison.scenario.textbook_observations}
    oaep = {item.recipient_id: item for item in comparison.scenario.oaep_observations}
    decrypted = {item.recipient_id: item.recovered_original_bytes for item in comparison.decryptions}
    return [
        {
            "Recipient": name,
            "n bits": textbook[name].public.modulus_bits,
            "e": textbook[name].public.e,
            "Public n": preview_integer(textbook[name].public.n),
            "Textbook c": preview_integer(textbook[name].public.c),
            "OAEP c": preview_integer(oaep[name].public.c),
            "OAEP decrypted": decrypted[name],
        }
        for name in textbook
    ]
