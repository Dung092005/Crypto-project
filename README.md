# BroadcastGuard

Ứng dụng giáo dục mật mã cho project giữa kỳ. Các bước 01–03 xây lõi toán học,
Attack Lab và bộ phân tích điều kiện. TASK 04 thêm Defense Lab so sánh Textbook
RSA với RSA-OAEP trên cùng thông điệp, cùng ba khóa và cùng phép thử của Eve.
TASK 05 bổ sung mã hóa file cho nhiều người nhận bằng AES-256-GCM và RSA-OAEP.
TASK 06 thêm giao diện Streamlit tương tác cho Attack Lab. Defense UI và
Secure Sharing UI chưa được triển khai.

## Cài đặt trên Windows

Cần Python 3.11 trở lên và Git. Chạy PowerShell trong thư mục repo:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -X utf8 examples\01_demo_de_hieu.py
.\.venv\Scripts\python.exe -X utf8 examples\02_demo_rsa_2048.py
.\.venv\Scripts\python.exe -X utf8 examples\03_demo_oaep.py
.\.venv\Scripts\python.exe -X utf8 examples\04_attack_lab.py
.\.venv\Scripts\python.exe -X utf8 examples\05_conditions_analyzer.py
.\.venv\Scripts\python.exe -X utf8 examples\06_defense_lab.py
.\.venv\Scripts\python.exe -X utf8 examples\07_hybrid_sharing.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Không cần activate môi trường, đổi ExecutionPolicy hoặc quyền admin. Dùng
`python` thay `py -3` nếu máy không có Python Launcher. Trên macOS/Linux dùng
`python3 -m venv .venv`, rồi `.venv/bin/python` thay đường dẫn Windows.

`pyproject.toml` quản lý `cryptography`, `streamlit` và `pytest` trong extra
`dev`. `requirements.txt` pin phiên bản runtime để Streamlit Community Cloud
cài đúng môi trường đã kiểm chứng. Lõi toán học chỉ dùng standard library.
Ứng dụng local mở ở `http://localhost:8501`; xem [hướng dẫn Cloud](docs/DEPLOYMENT.md)
trước khi triển khai. TASK 06 chưa được deploy công khai.

## Cấu trúc

```text
broadcastguard/           Python package
    __init__.py
    math_core.py          CRT, căn nguyên, mô phỏng tấn công, bytes ↔ integer
    attack_lab.py         Kịch bản, Eve, bộ đánh giá thực nghiệm
    conditions_analyzer.py Phân tích bảy tập người nhận và quét độ dài
    defense_lab.py        So sánh Textbook RSA / RSA-OAEP có kiểm soát
    hybrid_sharing.py     Mã hóa file nhiều người nhận, gói v1
    ui/attack_presenter.py Định dạng kết quả cho Attack Lab UI
app.py                    Streamlit Attack Lab entrypoint
.streamlit/config.toml    Theme dark
requirements.txt          Runtime dependencies cho Community Cloud
examples/                 Bảy demo CLI
tests/                    Unit tests và smoke tests chạy demo bằng subprocess
docs/
    PROJECT_CONTEXT.md    Mục tiêu, phạm vi, threat model, acceptance criteria
    PROGRESS.md           Kết quả thực tế và việc còn tồn đọng
    DECISIONS.md          Quyết định kiến trúc và lý do
    REVIEW_CHECKPOINT.md Bàn giao trạng thái đã kiểm chứng
    SECURE_SHARING_DESIGN.md Định dạng gói và giới hạn bảo mật
    UI_DESIGN.md          Luồng tương tác và màu Attack Lab
    DEPLOYMENT.md         Hướng dẫn Cloud, kiểm tra và rollback
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
- Defense Lab giữ e=3 và cùng ba cặp khóa RSA-2048 cho cả hai mode. OAEP dùng
  SHA-256, MGF1-SHA256 và label rỗng từ `cryptography`, tối đa 190 byte.
  Eve dùng lại CRT + căn bậc ba trên cả hai bộ quan sát. OAEP mã hóa ngẫu nhiên
  trước RSA, nên điều kiện `M³ < N` của Textbook RSA không giải thích kết quả
  OAEP. Sự thất bại của phép thử này không chứng minh an toàn tuyệt đối.
- Textbook RSA chỉ dành cho attack lab. Secure Sharing dùng
  AES-256-GCM + RSA-OAEP và RSA e=65537, không tái sử dụng Textbook RSA.

TASK 05: `broadcastguard.hybrid_sharing` mã hóa file bytes đúng một lần bằng
khóa AES-256 mới và nonce 12 byte mới. Khóa AES được bọc riêng cho 1–5 người
nhận bằng RSA-OAEP SHA-256/MGF1-SHA256. `generate_demo_recipients(count)` tạo
keypair trong RAM. `encrypt_file_for_recipients(data, filename, public_recipients)`
trả `EncryptedPackage`; `serialize_package` / `deserialize_package` chuyển
gói JSON/Base64 v1; `decrypt_file_for_recipient(package, id, private_key)`
chỉ trả file khi giải mã và xác thực thành công. `summarize_package` trả dữ
liệu công khai, ngắn cho UI sau này; `attempt_decrypt_file_for_recipient` trả
trạng thái có cấu trúc và không trả dữ liệu khi giải mã thất bại.

Giới hạn file thử nghiệm 5 MiB. Header canonical JSON là AAD của GCM nên
metadata, danh sách người nhận và wrapped keys được xác thực. `PackageValidationError`
báo cấu trúc sai; `DecryptionFailed` báo người nhận/khóa/xác thực không thành công.
Public keys phải được xác thực trước; package không có chữ ký người gửi và không
chống replay hoặc thay thế toàn bộ. Xem [thiết kế gói v1](docs/SECURE_SHARING_DESIGN.md).

TASK 06: chạy `app.py`, chọn mẫu 1/96/180 byte hoặc nhập UTF-8 tối đa 190 byte,
bấm **Generate RSA Scenario**, chọn các ciphertext Eve thu được, rồi bấm
**Run Broadcast Attack**. Giao diện hiển thị CRT, căn bậc ba, kết quả đối
chiếu riêng, bảng bảy tập con và phép quét độ dài dùng cùng bộ modulus.
Chỉ bấm Generate mới sinh bộ khóa mới; đổi bản nháp chưa thay kịch bản đang xem.
Không có cache chung chứa plaintext hoặc kịch bản của người dùng. Xem
[UI design](docs/UI_DESIGN.md) và [deployment guide](docs/DEPLOYMENT.md).

## API và kiểm chứng

Import bằng `from broadcastguard.math_core import broadcast_attack` sau khi cài
package. Không sửa `sys.path`. `crt` nhận sequence số nguyên, trả `(X, N)`;
`integer_nth_root` trả `(root, exact)`; `broadcast_attack` trả dataclass bất biến.
Sai kiểu gây `TypeError`, sai miền giá trị gây `ValueError`. Boolean không được
coi là số nguyên hợp lệ. Chuyển bytes dùng big-endian không dấu; giữ độ dài gốc
để bảo toàn byte 0 đầu. `integer_to_message` yêu cầu độ dài dương và số vừa độ dài.
Việc kiểm tra thông điệp `M < n` thuộc nơi gọi RSA, không thuộc hàm đổi bytes.

TASK 02 thêm API trong `broadcastguard.attack_lab`:

- `build_scenario(plaintext: bytes)` sinh ba RSA key pair 2048-bit/e=3, chỉ
  trả plaintext thí nghiệm và ba `PublicObservation` gồm ID, `n`, `e`, `c`.
  Public key và ciphertext đầy đủ được giữ trong cấu trúc; thuộc tính
  `modulus_bits` và `ciphertext_preview` phù hợp hiển thị ngắn.
- `attack_observations(observations)` nhận 1–3 quan sát công khai theo bất kỳ
  tập con/thứ tự nào, trả `AttackOutcome`. Dữ liệu sai được mô tả trong `reason`;
  trường hợp không có căn nguyên chính xác được báo riêng.
- `evaluate_experiment(scenario, observed, outcome)` mới được xem plaintext,
  kiểm tra `M**3 < product(moduli)` và trả `ExperimentEvaluation` với trạng thái
  `recovered`, `wrong_exact_root`, `no_exact_root` hoặc `invalid_input`.
  Nếu ứng viên vừa độ dài, `candidate_bytes` giữ nguyên byte `0x00` đầu.

Module này chỉ mô phỏng Textbook RSA cố ý không an toàn. `AttackOutcome` không
chứa plaintext hoặc private key. Lỗi không có căn chính xác không chứng minh
Textbook RSA an toàn. Demo 04 dùng mẫu 180 byte để minh họa 1/2/3 bản mã.

TASK 03 thêm `broadcastguard.conditions_analyzer`:

- `analyze_scenario(scenario)` xét bảy tập con của Alice, Bob, Charlie theo
  thứ tự xác định. `SubsetAnalysis` giữ N, X, căn ứng viên, trạng thái căn,
  điều kiện M³ < N, kết quả đối chiếu và lời giải thích gắn nhãn Experimenter.
  `ScenarioAnalysis.table_rows()` xuất dict đơn giản.
- `sweep_message_lengths(base_scenario, lengths=(1, 96, 180))` mã hóa lại
  `b"B" * length` bằng cùng ba public moduli. `LengthSweep.matrix_rows()`,
  `minimum_rows()` và `comparison_rows()` chuẩn bị dữ liệu cho UI sau này.
- `minimum_successful_count` trả `None` nếu không có kết quả thành công.
  Một kịch bản hợp lệ đủ ba modulus đều lớn hơn M luôn thành công với cả ba;
  `None` hữu ích khi tổng hợp một tập kết quả bị lọc hoặc rỗng.

Số byte không đủ để suy ra khả năng khôi phục: cần xét giá trị M và tích
modulus của tập người nhận cụ thể. `wrong_exact_root` khác `recovered`.

TASK 04 thêm `broadcastguard.defense_lab.run_defense_comparison(plaintext)`.
Hàm sinh đúng một bộ ba khóa RSA trong RAM, mã hóa cùng bytes bằng Textbook RSA
và RSA-OAEP, rồi trả `DefenseComparison` với `summary_rows()`,
`recipient_rows()` và `detail_rows()` cho UI tương lai. Kết quả giữ scheme của
từng ciphertext, trạng thái Eve và trạng thái giải mã OAEP của từng người nhận.
`private_keys` tùy chọn chỉ phục vụ thí nghiệm/kiểm thử có kiểm soát và không
được lưu trong kết quả. `randomization_trials` minh họa Textbook RSA lặp lại
cùng bản mã còn các lần OAEP tạo bản mã khác nhau.

Giới hạn OAEP theo [RFC 8017 §7.1](https://www.rfc-editor.org/rfc/rfc8017.html#section-7.1):
`mLen <= k - 2*hLen - 2`, với RSA-2048 (`k=256`) và SHA-256 (`hLen=32`) là
190 byte. OAEP trong dự án dùng `label=None` (nhãn rỗng).

```powershell
.\.venv\Scripts\python.exe -c "import broadcastguard; import broadcastguard.math_core; print(broadcastguard.__version__)"
.\.venv\Scripts\python.exe -m compileall -q broadcastguard examples tests
git diff --check
```

Tests toán học dùng dữ liệu cố định; demo sinh khóa bằng nguồn ngẫu nhiên bảo mật,
không ghi khóa ra đĩa. Không mong đợi ciphertext lặp lại giữa các lần chạy.
Xem [bối cảnh dự án](docs/PROJECT_CONTEXT.md), [tiến độ](docs/PROGRESS.md) và
[quyết định](docs/DECISIONS.md) trước khi tiếp tục. [Review checkpoint](docs/REVIEW_CHECKPOINT.md)
tóm tắt trạng thái cho agent mới. Mỗi task dừng để review.
