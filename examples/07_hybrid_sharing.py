"""TASK 05: local, educational hybrid file sharing demo."""

from dataclasses import replace

from broadcastguard.hybrid_sharing import (
    DecryptionFailed,
    decrypt_file_for_recipient,
    deserialize_package,
    encrypt_file_for_recipients,
    generate_demo_recipients,
    serialize_package,
    summarize_package,
)


def main() -> None:
    filename = "secret_exam.txt"
    data = "Đây là file giả lập của BroadcastGuard.\n".encode("utf-8")
    recipients = generate_demo_recipients(3)
    package = encrypt_file_for_recipients(data, filename, tuple(item.public for item in recipients))
    encoded = serialize_package(package)
    imported = deserialize_package(encoded)
    summary = summarize_package(imported)

    print("=== BroadcastGuard: Secure Hybrid File Sharing ===")
    print(f"File giả lập: {filename} ({len(data)} byte)")
    print("Nội dung mẫu:", data.decode("utf-8").strip())
    print(f"Gói JSON/Base64 đã mã hóa: {summary.package_size} byte")
    print(f"Thuật toán: {summary.content_algorithm} + {summary.key_wrap_algorithm}")
    print("Ba khóa AES được bọc riêng cho người nhận (chỉ hiện preview):")
    for entry in imported.header.recipients:
        print(f"  {entry.recipient_id:<7} fingerprint={entry.fingerprint[:12]}… "
              f"wrapped={entry.wrapped_key.hex()[:12]}… ({len(entry.wrapped_key)} byte)")

    print("\nGiải mã hợp lệ:")
    for recipient in recipients:
        recovered = decrypt_file_for_recipient(imported, recipient.recipient_id, recipient.private_key)
        print(f"  {recipient.recipient_id}: {recovered == data}")
        if recovered != data:
            raise RuntimeError("A legitimate recipient did not recover the original file.")

    try:
        decrypt_file_for_recipient(imported, "Alice", recipients[1].private_key)
    except DecryptionFailed:
        print("\nKhóa sai của Bob dùng cho Alice: bị từ chối.")
    else:
        raise RuntimeError("A wrong private key unexpectedly decrypted the package.")

    modified_content = bytes([imported.encrypted_content[0] ^ 1]) + imported.encrypted_content[1:]
    tampered = replace(imported, encrypted_content=modified_content)
    try:
        decrypt_file_for_recipient(tampered, "Alice", recipients[0].private_key)
    except DecryptionFailed:
        print("Sửa một byte ciphertext: xác thực AES-GCM thất bại, không trả plaintext.")
    else:
        raise RuntimeError("A tampered ciphertext unexpectedly decrypted.")

    print("\nGiải thích: AES-GCM mã hóa file đúng một lần bằng khóa mới. RSA-OAEP bọc")
    print("khóa AES đó riêng cho từng người. Mỗi người dùng private key của mình để")
    print("mở khóa AES rồi kiểm tra tag trước khi nhận file. Header là AAD nên sửa")
    print("metadata cũng làm giải mã thất bại. Hệ thống giả định public key đã được")
    print("xác thực trước; AES-GCM không tự chứng minh ai là người gửi.")


if __name__ == "__main__":
    main()
