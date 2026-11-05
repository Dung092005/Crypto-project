"""Bài 1: số nhỏ. Chạy từ repo: python examples/01_demo_de_hieu.py."""

from math import prod

from broadcastguard.math_core import broadcast_attack


def main() -> None:
    # Chỉ để giảng giải, không phải khóa bảo vệ dữ liệu thật.
    moduli = [55, 391, 1189]
    exponent = 3
    print("\n=== BroadcastGuard: Hiểu tấn công với số nhỏ ===")
    print("Cùng thông điệp M được gửi cho Alice, Bob, Charlie.")
    for message in (2, 12, 30):
        print(f"\nTHÔNG ĐIỆP M = {message} (M^3 = {message**3})")
        ciphertexts = [pow(message, exponent, n) for n in moduli]
        for count in (1, 2, 3):
            outcome = broadcast_attack(ciphertexts[:count], moduli[:count], exponent)
            found = outcome.exact and outcome.root == message
            condition = message**exponent < prod(moduli[:count])
            if found != condition:
                raise RuntimeError("Kết quả không khớp điều kiện của ví dụ.")
            status = "KHÔI PHỤC ĐÚNG" if found else "CHƯA KHÔI PHỤC ĐƯỢC"
            print(f"  Eve có {count} bản mã: X = {outcome.combined}; "
                  f"căn chính xác = {outcome.exact}; {status}")
        required = next(k for k in (1, 2, 3)
                        if message**exponent < prod(moduli[:k]))
        print(f"  Điều kiện M^3 < tích modulus bắt đầu đúng từ {required} bản mã.")
    print("\nĐây là lỗi của Textbook RSA không padding, không phải mọi RSA.\n")


if __name__ == "__main__":
    main()
