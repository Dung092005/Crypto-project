# BroadcastGuard

Ứng dụng giáo dục mật mã cho project giữa kỳ. TASK 01 chuẩn hóa package Python,
tái sử dụng lõi toán học và ba demo starter, bổ sung kiểm thử và bối cảnh dự án.
Chưa có giao diện hoặc chức năng mã hóa file.

## Cài đặt trên Windows

Cần Python 3.11 trở lên và Git. Chạy PowerShell trong thư mục repo:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -X utf8 examples\01_demo_de_hieu.py
.\.venv\Scripts\python.exe -X utf8 examples\02_demo_rsa_2048.py
.\.venv\Scripts\python.exe -X utf8 examples\03_demo_oaep.py
```

Không cần activate môi trường, đổi ExecutionPolicy hoặc quyền admin. Dùng
`python` thay `py -3` nếu máy không có Python Launcher. Trên macOS/Linux dùng
`python3 -m venv .venv`, rồi `.venv/bin/python` thay đường dẫn Windows.

`pyproject.toml` quản lý dependency: `cryptography` cho demo RSA/OAEP và `pytest`
trong extra `dev`. Lõi toán học chỉ dùng standard library. Streamlit là kế hoạch
giai đoạn sau, chưa phải dependency của TASK 01.

## Cấu trúc

```text
broadcastguard/           Python package
    __init__.py
    math_core.py          CRT, căn nguyên, mô phỏng tấn công, bytes ↔ integer
examples/                 Ba demo CLI đã chuyển import từ starter
tests/                    Unit tests và smoke tests chạy demo bằng subprocess
docs/
    PROJECT_CONTEXT.md    Mục tiêu, phạm vi, threat model, acceptance criteria
    PROGRESS.md           Kết quả thực tế và việc còn tồn đọng
    DECISIONS.md          Quyết định kiến trúc và lý do
AGENTS.md                 Quy tắc tiếp tục công việc cho coding agent
pyproject.toml            Packaging, dependencies và pytest
```

## Đọc kết quả đúng cách

- Với cùng thông điệp nguyên M, Textbook RSA dùng `c_i = M**e mod n_i`.
  CRT đòi hỏi các modulus đôi một nguyên tố cùng nhau. Nếu
  `M**e < product(moduli)`, kết quả CRT chính là `M**e`.
- `AttackResult.exact` chỉ nói căn ứng viên là căn nguyên chính xác của số CRT.
  Demo so sánh riêng với plaintext đã biết để xác nhận khôi phục đúng.
  Ví dụ `M=2, n=7, e=3`: bản mã bằng 1 có căn chính xác bằng 1, nhưng không phải M.
- Không khẳng định luôn cần ba bản mã: M nhỏ có thể chỉ cần một hoặc hai.
  Khi phương pháp CRT-and-root thất bại, chưa thể kết luận Textbook RSA an toàn.
- Demo OAEP giữ e=3 để so sánh tác động của padding; dùng SHA-256 và MGF1-SHA256
  từ thư viện. Đây chỉ là phép thử cách tấn công trên mẫu đã chọn.
- Textbook RSA chỉ dành cho attack lab. Secure Sharing sau này dùng
  AES-256-GCM + RSA-OAEP và RSA e=65537, không tái sử dụng Textbook RSA.

## API và kiểm chứng

Import bằng `from broadcastguard.math_core import broadcast_attack` sau khi cài
package. Không sửa `sys.path`. `crt` nhận sequence số nguyên, trả `(X, N)`;
`integer_nth_root` trả `(root, exact)`; `broadcast_attack` trả dataclass bất biến.
Sai kiểu gây `TypeError`, sai miền giá trị gây `ValueError`. Boolean không được
coi là số nguyên hợp lệ. Chuyển bytes dùng big-endian không dấu; giữ độ dài gốc
để bảo toàn byte 0 đầu. `integer_to_message` yêu cầu độ dài dương và số vừa độ dài.
Việc kiểm tra thông điệp `M < n` thuộc nơi gọi RSA, không thuộc hàm đổi bytes.

```powershell
.\.venv\Scripts\python.exe -c "import broadcastguard; import broadcastguard.math_core; print(broadcastguard.__version__)"
.\.venv\Scripts\python.exe -m compileall -q broadcastguard examples tests
git diff --check
```

Tests toán học dùng dữ liệu cố định; demo sinh khóa bằng nguồn ngẫu nhiên bảo mật,
không ghi khóa ra đĩa. Không mong đợi ciphertext lặp lại giữa các lần chạy.
Xem [bối cảnh dự án](docs/PROJECT_CONTEXT.md), [tiến độ](docs/PROGRESS.md) và
[quyết định](docs/DECISIONS.md) trước khi tiếp tục. Dừng sau TASK 01 để review.
