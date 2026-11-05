"""Attack Lab CLI: run from the repository with an installed package.

    python examples/04_attack_lab.py
"""

from broadcastguard.attack_lab import (
    attack_observations,
    build_scenario,
    evaluate_experiment,
)


def main() -> None:
    plaintext = b"B" * 180
    print("=== BroadcastGuard: RSA Broadcast Attack Lab ===")
    print(f"Người gửi chọn thông điệp: {len(plaintext)} byte ký tự 'B'.")
    print("Sinh ba cặp khóa RSA 2048 bit độc lập, số mũ công khai e=3...")
    scenario = build_scenario(plaintext)

    print("\nNgười nhận và dữ liệu Eve quan sát được:")
    for observation in scenario.observations:
        modulus_hex = f"{observation.n:x}"
        modulus_preview = f"0x{modulus_hex[:12]}…{modulus_hex[-12:]}"
        print(f"  {observation.recipient_id}: e={observation.e}, "
              f"n={observation.modulus_bits} bit ({modulus_preview})")
        print(f"    Mã hóa cùng M: c=M^3 mod n -> {observation.ciphertext_preview}")
    print("Khóa bí mật không được trao cho Eve hoặc in ra màn hình.")

    for count in (1, 2, 3):
        observed = scenario.observations[:count]
        outcome = attack_observations(observed)
        evaluation = evaluate_experiment(scenario, observed, outcome)
        print(f"\nEve thu {count} bản mã: {', '.join(outcome.recipient_ids)}")
        for step in outcome.steps:
            print(f"  {step}")
        print(f"  M^3 < tích modulus: {evaluation.bound_holds}")
        print(
            f"  Trạng thái: {evaluation.status}; "
            f"khớp thông điệp gốc: {evaluation.matches_original}"
        )
        if evaluation.matches_original:
            print("  Giải thích: CRT cho đúng M^3; căn bậc ba nguyên trả lại M.")
        elif outcome.exact:
            print("  Giải thích: có căn nguyên chính xác nhưng không phải M gốc.")
        else:
            print("  Giải thích: X sau CRT không là lập phương hoàn hảo trong phép thử này.")
    print("\nPhép thử thất bại không chứng minh Textbook RSA an toàn.")


if __name__ == "__main__":
    main()
