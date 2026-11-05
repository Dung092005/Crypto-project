# Hướng dẫn làm việc với BroadcastGuard

- Trước khi sửa code, đọc toàn bộ `README.md`, `docs/PROJECT_CONTEXT.md`,
  `docs/PROGRESS.md` và các quyết định liên quan trong `docs/DECISIONS.md`.
- Kiểm tra working directory, git status, branch và remote. Bảo toàn thay đổi
  chưa commit; không force-push, tự merge main hoặc ghi đè code chưa đọc.
- Mỗi task phải có acceptance criteria và tests tương ứng; ghi kết quả chạy
  thực tế, lệnh kiểm chứng và phần bị BLOCKED trong PROGRESS.
- Ưu tiên thay đổi nhỏ, có thể review. Chỉ hoàn thành task được giao rồi dừng;
  không tự chuyển sang task kế tiếp và không viết report học thuật khi chưa được yêu cầu.
- Không tùy ý thay kiến trúc, threat model hay cryptographic assumptions.
  `broadcastguard/math_core.py` chỉ phục vụ nghiên cứu Textbook RSA không an toàn.
  Module chia sẻ file sau này phải tách riêng và dùng thuật toán chuẩn của thư viện.
- Không tự viết OAEP, AES hay sinh số nguyên tố. Không seed bộ sinh khóa mật mã
  để làm demo xác định; test toán học dùng đầu vào cố định.
- Không lưu/commit private key, credential, token, `.venv` hoặc dữ liệu nhạy cảm.
  Các demo chỉ giữ khóa trong RAM; không in private components.
- Kiểm thử: `python -m pytest`, chạy các demo theo README, kiểm tra import,
  compileall và git diff. `AttackResult.exact` không có nghĩa đã xác nhận plaintext.
- Với truy vấn cấu trúc code, dùng skill `codebase-memory` nếu có; nếu graph chưa
  bao phủ, đọc source thực tế và ghi rõ giới hạn. Không index/cài công cụ lớn chỉ để bootstrap.
- Không dùng công cụ tìm bài báo cho bước engineering này. Khi được giao report
  học thuật riêng, tuân thủ workflow nghiên cứu và quy tắc provenance của workspace.
