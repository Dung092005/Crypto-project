"""Small, side-effect-free presentation helpers for the Attack Lab UI."""

from broadcastguard.attack_lab import EvaluationStatus
from broadcastguard.conditions_analyzer import LengthSweep, ScenarioAnalysis

PRESETS: dict[str, bytes] = {
    "Short · 1 byte": b"B",
    "Medium · 96 bytes": b"B" * 96,
    "Long · 180 bytes": b"B" * 180,
}
MAX_INPUT_BYTES = 190

STATUS_LABELS: dict[EvaluationStatus, tuple[str, str]] = {
    "recovered": ("Recovered", "Eve khôi phục đúng thông điệp trong thí nghiệm này."),
    "wrong_exact_root": (
        "Wrong exact root", "Có căn bậc ba nguyên chính xác, nhưng ứng viên không phải plaintext gốc."
    ),
    "no_exact_root": (
        "No exact root", "Giá trị CRT không có căn bậc ba nguyên chính xác theo cách thử này."
    ),
    "invalid_input": ("Invalid input", "Dữ liệu công khai không đủ hoặc không hợp lệ để tính toán."),
}


def message_bytes(mode: str, preset: str, custom_text: str) -> bytes:
    """Validate the draft exactly as entered; never truncate UTF-8 bytes."""
    if mode == "Preset samples":
        try:
            data = PRESETS[preset]
        except KeyError as error:
            raise ValueError("Mẫu thông điệp không hợp lệ.") from error
    elif mode == "Custom message":
        if not isinstance(custom_text, str):
            raise ValueError("Thông điệp tùy chỉnh phải là văn bản.")
        data = custom_text.encode("utf-8")
    else:
        raise ValueError("Chế độ nhập thông điệp không hợp lệ.")
    if not data:
        raise ValueError("Thông điệp không được để trống.")
    if len(data) > MAX_INPUT_BYTES:
        raise ValueError(f"Thông điệp dài {len(data)} byte; giới hạn là {MAX_INPUT_BYTES} byte UTF-8.")
    return data


def preview_integer(value: int | None, edge: int = 12) -> str:
    if value is None:
        return "—"
    digits = f"{value:x}"
    return f"0x{digits}" if len(digits) <= edge * 2 else f"0x{digits[:edge]}…{digits[-edge:]}"


def readable_message(data: bytes) -> tuple[str, str]:
    """Use a safe hex fallback for binary or control-heavy plaintext."""
    try:
        decoded = data.decode("utf-8")
    except UnicodeDecodeError:
        return "Hex preview", data[:48].hex() + ("…" if len(data) > 48 else "")
    if not decoded.isprintable():
        return "Hex preview", data[:48].hex() + ("…" if len(data) > 48 else "")
    return "UTF-8 text", decoded[:120] + ("…" if len(decoded) > 120 else "")


def subset_rows(analysis: ScenarioAnalysis) -> list[dict[str, object]]:
    return [
        {
            "Subset": " + ".join(row.recipient_ids),
            "Count": row.count,
            "N bits": row.product_bits,
            "Exact root": row.exact_root,
            "Recovered": row.recovered,
            "M³ < N": row.bound_holds,
            "Status": STATUS_LABELS[row.status][0],
        }
        for row in analysis.subsets
    ]


def sweep_rows(sweep: LengthSweep) -> list[dict[str, object]]:
    return [
        {
            "Bytes": analysis.message_length,
            "M bits": analysis.message_bits,
            "Minimum ciphertexts": analysis.minimum_successful_count,
            **{
                " + ".join(row.recipient_ids): STATUS_LABELS[row.status][0]
                for row in analysis.subsets
            },
        }
        for analysis in sweep.analyses
    ]
