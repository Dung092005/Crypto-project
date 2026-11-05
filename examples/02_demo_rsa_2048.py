"""Bài 2: python examples/02_demo_rsa_2048.py sau khi cài package."""

from math import prod

from cryptography.hazmat.primitives.asymmetric import rsa

from broadcastguard.math_core import (
    broadcast_attack,
    integer_to_message,
    message_to_integer,
)


def main() -> None:
    print("\n=== BroadcastGuard: RSA 2048-bit Broadcast Attack ===")
    print("Đang sinh ba cặp khóa thử nghiệm, e = 3...")
    private_keys = [rsa.generate_private_key(public_exponent=3, key_size=2048)
                    for _ in range(3)]
    moduli = [key.public_key().public_numbers().n for key in private_keys]
    print("Đã tạo 3 public key khác nhau; Eve KHÔNG dùng private key.")
    for length in (1, 96, 180):
        data = b"B" * length
        message = message_to_integer(data)
        if message >= min(moduli):
            raise ValueError("Thông điệp phải nhỏ hơn mọi modulus.")
        # Textbook RSA chỉ dùng trong phòng thí nghiệm tấn công.
        ciphertexts = [pow(message, 3, n) for n in moduli]
        print(f"\nThông điệp dài {length} byte:")
        for count in (1, 2, 3):
            outcome = broadcast_attack(ciphertexts[:count], moduli[:count])
            recovered = outcome.exact and outcome.root == message
            if recovered and integer_to_message(outcome.root, length) != data:
                raise RuntimeError("Thông điệp byte khôi phục bị sai.")
            condition = message**3 < prod(moduli[:count])
            if recovered != condition:
                raise RuntimeError("Kết quả không khớp điều kiện của mẫu thử.")
            print(f"  Eve thu {count} ciphertext: điều kiện toán học={condition}; "
                  f"căn chính xác={outcome.exact}; khôi phục đúng={recovered}")
    print("\nSố bản mã cần thiết tùy độ lớn M và tích modulus.")
    print("KHÔNG dùng Textbook RSA để bảo vệ dữ liệu thật.\n")


if __name__ == "__main__":
    main()
