"""TASK 04: controlled Textbook RSA and RSA-OAEP comparison."""

from broadcastguard.defense_lab import run_defense_comparison


def main() -> None:
    message = b"B" * 180
    print("=== BroadcastGuard: RSA-OAEP Defense Lab ===")
    print(f"Thông điệp mẫu: {len(message)} byte, cùng nội dung cho Alice, Bob, Charlie.")
    print("Sinh một bộ ba RSA-2048/e=3, dùng lại cho cả Textbook RSA và RSA-OAEP...")
    comparison = run_defense_comparison(message)
    print("\nNgười nhận | Số bit n | e | Public modulus (rút gọn)")
    for row in comparison.recipient_rows()[:3]:
        print(f"{row['recipient_id']:<10} | {row['modulus_bits']:<8} | {row['public_exponent']} | {row['modulus_preview']}")

    print("\nMã hóa cùng plaintext và cho Eve thử cùng CRT + căn bậc ba:")
    print("Scheme       | Số bản mã | Căn đúng? | Khôi phục M? | Giải mã hợp lệ?")
    for row in comparison.summary_rows():
        decrypt = "không áp dụng" if row["legitimate_decryption"] is None else str(row["legitimate_decryption"])
        print(f"{row['scheme']:<12} | {row['recipient_count']:^10} | {str(row['exact_root']):^9} | "
              f"{str(row['recovered_original']):^11} | {decrypt}")
    print("\nBản mã công khai (rút gọn):")
    for row in comparison.recipient_rows():
        print(f"{row['scheme']:<8} {row['recipient_id']:<7}: {row['ciphertext_preview']}")
    print("\nKết quả giải mã OAEP theo từng người nhận:")
    for item in comparison.decryptions:
        print(f"  {item.recipient_id}: {item.recovered_original_bytes}")
    random = comparison.randomization
    print("\nThử mã hóa lặp lại trên cùng khóa của Alice:")
    print(f"  Textbook RSA cho cùng ciphertext: {random.textbook_ciphertexts_identical}")
    print(f"  {random.trial_count} ciphertext OAEP khác nhau: {random.oaep_ciphertexts_distinct}")
    print(f"  Tất cả lần OAEP đều giải mã đúng: {random.oaep_all_decrypt}")
    print("\nGiải thích: Textbook RSA mã hóa trực tiếp cùng số M, nên khi M³ nhỏ hơn")
    print("tích ba modulus, CRT tái dựng M³ và Eve lấy căn được M. OAEP thêm")
    print("mã hóa ngẫu nhiên trước phép RSA, nên ba ciphertext không còn tương ứng")
    print("với cùng M³. Người nhận có khóa bí mật vẫn giải mã đúng.")
    print("Đây là quan sát của phép thử CRT-and-root, không phải chứng minh an toàn tuyệt đối.")
    if not comparison.textbook.recovered_original or comparison.oaep.recovered_original:
        raise RuntimeError("Controlled comparison did not show the expected attack distinction.")
    if not all(item.recovered_original_bytes for item in comparison.decryptions):
        raise RuntimeError("A legitimate recipient failed to decrypt OAEP.")


if __name__ == "__main__":
    main()
