# Secure Sharing: thiết kế gói v1

Tài liệu kỹ thuật cho TASK 05; chưa phải academic report. Module triển khai:
`broadcastguard/hybrid_sharing.py`. Dữ liệu nằm trong RAM; caller tự quyết định
cách lưu hoặc truyền `serialize_package()` ở các task sau.

## Luồng mã hóa

1. Kiểm tra file bytes (0–5 MiB), tên hiển thị dạng basename và 1–5 public key
   RSA-2048/e=65537 đã được xác thực bởi ứng dụng gọi. Từ chối ID/khóa trùng.
2. Tạo khóa AES-256 mới bằng `AESGCM.generate_key(256)` và nonce 12 byte mới
   từ CSPRNG. Mỗi lần gửi tạo cặp khóa/nonce mới.
3. Mã hóa **cùng khóa AES 32 byte** riêng cho từng public key bằng RSAES-OAEP,
   SHA-256, MGF1(SHA-256), `label=None`. Tính fingerprint SHA-256 trên DER
   SubjectPublicKeyInfo của từng khóa công khai.
4. Tạo header v1 và serialize canonical thành UTF-8 JSON: `sort_keys=True`,
   `separators=(",", ":")`, `ensure_ascii=False`; bytes dùng Base64 chuẩn.
   Dùng **toàn bộ header canonical** làm AES-GCM AAD.
5. Gọi `AESGCM(key).encrypt(nonce, file_bytes, aad)` đúng một lần. Kết quả
   là ciphertext nối tag 16 byte do thư viện tạo; không ghép tag thứ hai.

## Luồng giải mã

1. Giới hạn kích thước, parse JSON, từ chối duplicate keys và kiểm tra chặt
   format/version/algorithm/Base64/nonce/độ dài ciphertext/recipient entries.
2. Tìm entry theo recipient ID và so fingerprint của private key tương ứng.
3. Dùng RSA-OAEP giải mã wrapped AES key; yêu cầu đúng 32 byte.
4. Tái tạo cùng canonical header AAD và gọi `AESGCM.decrypt`. Chỉ sau khi
   tag hợp lệ và kích thước plaintext đúng header mới trả bytes.
5. Cấu trúc sai gây `PackageValidationError`; thiếu/sai khóa, OAEP hoặc GCM
   xác thực thất bại gây `DecryptionFailed`. Wrapper
   `attempt_decrypt_file_for_recipient` trả `decrypted`, `invalid_package` hoặc
   `decryption_failed` cho UI. Không trả plaintext một phần. Từ lỗi xác thực
   đơn thuần không thể kết luận chắc là package bị sửa hay private key sai.

## Format v1

Package là UTF-8 JSON (không pickle), tối đa 8 MiB. Ví dụ rút gọn:

```json
{
  "ciphertext": "<Base64 của ciphertext || 16-byte tag>",
  "header": {
    "content_algorithm": "AES-256-GCM",
    "filename": "secret_exam.txt",
    "format_version": 1,
    "key_wrap_algorithm": "RSA-OAEP-SHA256-MGF1SHA256",
    "nonce": "<Base64 của 12 byte>",
    "original_size": 123,
    "recipients": [
      {
        "fingerprint": "<64 ký tự hex thường SHA-256(DER SPKI)>",
        "recipient_id": "Alice",
        "wrapped_key": "<Base64 của 256 byte RSA ciphertext>"
      }
    ]
  }
}
```

Object JSON sắp khóa theo tên khi export; thứ tự phần tử `recipients` giữ nguyên.
Mọi trường header, kể cả danh sách người nhận, fingerprint và wrapped keys,
đều nằm trong AAD. Ciphertext không nằm trong AAD vì GCM xác thực nó trực tiếp.
Import chấp nhận whitespace/thứ tự khóa JSON khác, rồi dựng lại header canonical
để xác thực. Từ chối trường thừa/thiếu, duplicate JSON keys, version hoặc
algorithm khác, Base64 sai hoặc không canonical, cùng các độ dài sai. Filename
chỉ là metadata hiển thị; module không dùng nó để mở/ghi đường dẫn.

## Quản lý khóa và giới hạn bảo mật

`generate_demo_recipients()` giữ private keys trong RAM của phiên demo; package
chỉ chứa thông tin công khai và khóa AES đã bọc. Fingerprint giúp chọn đúng khóa
và phát hiện nhầm khóa, **không tự xác thực danh tính**. Bên gọi phải xác thực
public keys trước khi mã hóa. Không có quản lý/lưu trữ private key lâu dài.

GCM bảo vệ tính bí mật của file và tính toàn vẹn của ciphertext cùng header
đối với khóa AES đã chọn. Sửa một phần package làm validation hoặc giải mã
thất bại. GCM **không cung cấp sender authentication**; bất kỳ ai có public
keys đều có thể tạo một package mới hợp lệ. Thiết kế này chưa chống thay thế
toàn bộ package, replay, endpoint bị chiếm quyền, tráo public key trước khi
xác thực, hay metadata không nằm trong header. Không có chữ ký số, mạng,
database, certificate management hoặc streaming file trên 5 MiB.

Tham chiếu kỹ thuật: [RFC 8017 RSAES-OAEP](https://www.rfc-editor.org/rfc/rfc8017.html#section-7.1),
[NIST SP 800-38D GCM](https://csrc.nist.gov/pubs/sp/800/38/d/final),
[cryptography AESGCM](https://cryptography.io/en/stable/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM).
