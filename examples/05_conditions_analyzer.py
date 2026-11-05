"""Show all seven intercepted subsets for three controlled message sizes."""

from broadcastguard.attack_lab import build_scenario
from broadcastguard.conditions_analyzer import sweep_message_lengths

STATUS_LABELS = {
    "recovered": "OK",
    "wrong_exact_root": "SAI",
    "no_exact_root": "KHÔNG",
    "invalid_input": "LỖI",
}


def main() -> None:
    print("=== BroadcastGuard: Attack Conditions Analyzer ===")
    print("Sinh một bộ ba khóa RSA 2048-bit/e=3 cho Alice, Bob, Charlie...")
    base = build_scenario(b"B")
    for item in base.observations:
        print(f"  {item.recipient_id}: e={item.e}, modulus {item.modulus_bits} bit")
    sweep = sweep_message_lengths(base)
    labels = ["/".join(row.recipient_ids) for row in sweep.analyses[0].subsets]
    print("\nCùng bộ modulus, thông điệp b'B' * số byte:")
    print("Byte  M(bit) " + " ".join(f"{label:>8}" for label in labels) + "  Tối thiểu")
    for analysis in sweep.analyses:
        cells = " ".join(f"{STATUS_LABELS[row.status]:>8}" for row in analysis.subsets)
        print(f"{analysis.message_length:>4}  {analysis.message_bits:>6} {cells}"
              f"  {analysis.minimum_successful_count}")
    print("\nOK: Eve tìm đúng M; SAI: căn nguyên chính xác nhưng sai M; "
          "KHÔNG: không có căn nguyên chính xác.")
    print("Bộ đánh giá biết M để so sánh M³ < N; Eve chỉ nhận public key và ciphertext.")
    print("Giữ cùng khóa giúp so sánh ảnh hưởng của thông điệp; chính giá trị M, "
          "không chỉ số byte, quyết định điều kiện.")
    print("Thất bại của phép thử CRT và căn nguyên không chứng minh Textbook RSA an toàn.")


if __name__ == "__main__":
    main()
