"""Bài 3: python examples/03_demo_oaep.py. Giữ e=3 để so sánh padding."""

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from broadcastguard.math_core import broadcast_attack, message_to_integer


def oaep() -> padding.OAEP:
    """Dùng OAEP của thư viện; không tự cài đặt padding."""
    return padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    )


def main() -> None:
    data = b"B" * 180  # Giới hạn RSA 2048 + OAEP SHA-256 là 190 byte.
    keys = [rsa.generate_private_key(public_exponent=3, key_size=2048)
            for _ in range(3)]
    moduli = [key.public_key().public_numbers().n for key in keys]
    encrypted = [key.public_key().encrypt(data, oaep()) for key in keys]
    ciphertexts = [int.from_bytes(ciphertext, "big") for ciphertext in encrypted]
    result = broadcast_attack(ciphertexts, moduli, exponent=3)
    # So sánh số trước: căn ứng viên có thể không vừa độ dài plaintext.
    attacked = result.exact and result.root == message_to_integer(data)
    legitimate = [key.decrypt(ciphertext, oaep()) == data
                  for key, ciphertext in zip(keys, encrypted)]
    print("\n=== BroadcastGuard: OAEP defense ===")
    print("Eve thử CRT + căn bậc ba trên 3 ciphertext RSA-OAEP.")
    print("Có căn nguyên chính xác:", result.exact)
    print("Eve lấy lại plaintext bằng cách cũ:", attacked)
    print("Cả ba người nhận có giải mã được không:", all(legitimate))
    if attacked or not all(legitimate):
        raise RuntimeError("Thí nghiệm OAEP không đạt kết quả mong đợi.")
    print("Kết quả chỉ đánh giá cách tấn công CRT-and-root trong mẫu thử này.")


if __name__ == "__main__":
    main()
