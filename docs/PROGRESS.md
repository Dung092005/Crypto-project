# Tiến độ BroadcastGuard

## TASK 01 — PARTIAL: engineering đã kiểm chứng, tích hợp GitHub BLOCKED

Ngày: 2026-11-05. Nhánh cục bộ: `feat/step-01-bootstrap`.
Acceptance criteria: xem `PROJECT_CONTEXT.md`.

### Đã thực hiện

- Workspace gốc không có `.git`, chưa có source BroadcastGuard. Không sửa
  `cs-research-lab`, `_hw`, AGENTS của workspace hay tài liệu proposal gốc.
- Clone `https://github.com/Dung092005/Crypto-project.git` không thành công:
  không kết nối được proxy `127.0.0.1:9`. Chưa đọc được code/lịch sử remote.
- ZIP nguồn: `BroadcastGuard_Buoc1_Starter.zip` trong Downloads, 6489 byte.
  SHA-256: `a61b3491579108add8d9044b5965ce37e3631509bdce2ba5e0a9004eaf34a3fe`.
- Kiểm tra đủ 7 file; từ chối đường dẫn tuyệt đối, traversal, drive/ADS,
  symlink và đường dẫn trùng; giới hạn dung lượng trước giải nén vào thư mục mới
  `.task01-work/starter` nằm ngoài repo. Đọc toàn bộ starter.
- Baseline: `python -m unittest discover -s . -p test_core.py -v` tại thư mục
  starter: **4 tests OK**, chưa sửa starter trước chạy.
- Tái sử dụng CRT, binary search căn nguyên, dataclass, đổi bytes và cả 3 demo.
  Thêm validation và test, migrate sang `broadcastguard.math_core`.
- Tạo README, pyproject, ignore, AGENTS, context và decisions.
- Graph codebase-memory chưa index repo này; đã đọc trực tiếp toàn bộ source
  trong phạm vi thay vì dựa trên kết quả graph không có coverage.

### Môi trường và giới hạn kiểm chứng

Python 3.12.10, Windows; cryptography 48.0.1, pytest 9.1.1,
setuptools 80.10.2, wheel 0.48.0, cffi 2.0.0. Chỉ kiểm chứng trên môi trường này,
chưa kiểm chứng Python 3.11 hoặc hệ điều hành khác.

Venv ban đầu gặp PermissionError khi ensurepip/pip tạo thư mục tạm bằng mode
0700: ACL của thư mục mới loại trừ tiến trình sandbox. Đổi TEMP đơn thuần chưa đủ.
Đã xác nhận thư mục kế thừa ACL của workspace ghi được; thư mục 0700 không ghi được.
Tạo venv bằng `python -m venv --without-pip --system-site-packages .venv`, rồi dùng
pip và dependencies sẵn có để cài offline. Đây là venv có kế thừa packages hệ thống,
chưa phải kiểm chứng cài dependencies trong venv hoàn toàn cô lập từ PyPI.

Helper `../.task01-work/runtime/sitecustomize.py` chỉ áp dụng trong các process
kiểm chứng: mkdir 0700 ở `../.task01-work/tmp` kế thừa ACL workspace. Không đổi
ACL hay hành vi ngoài thư mục này; helper nằm ngoài repo, không phải mã ứng dụng.
Các demo chạy riêng không dùng helper/PYTHONPATH. README hướng dẫn cài venv
cô lập bình thường cho máy không có hạn chế sandbox này.

### Lệnh và kết quả thực tế

Các lệnh dưới chạy ở root của project. Với bước cài và pytest trong sandbox,
thiết lập environment sau (không cần trên máy Windows thông thường):

```powershell
$taskTemp = (Resolve-Path '..\.task01-work\tmp').Path
$env:TEMP = $taskTemp
$env:TMP = $taskTemp
$env:BROADCASTGUARD_TASK_TEMP = $taskTemp
$env:PYTHONPATH = (Resolve-Path '..\.task01-work\runtime').Path
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
.\.venv\Scripts\python.exe -m pip install --no-index --no-build-isolation -e ".[dev]"
.\.venv\Scripts\python.exe -X utf8 -m pytest -q -p no:cacheprovider --basetemp '..\.task01-work\tmp\pytest-task01-final'
```

- Cài editable `broadcastguard==0.1.0` từ pyproject: **PASS**.
- Lần pytest đầu: **94 passed**, có 1 cảnh báo không tạo được cache trong sandbox.
  Lần xác nhận sau tắt cacheprovider: **94 passed in 1.30s**, không warning.
- Smoke tests chạy đủ ba demo trong subprocess, cwd ngoài repo, bỏ PYTHONPATH,
  không tạo file trong thư mục làm việc. Có sinh RSA 2048 bit thực tế.
- Chạy riêng (không helper) ba lệnh
  `.venv\Scripts\python.exe -X utf8 examples\01_demo_de_hieu.py`,
  `... examples\02_demo_rsa_2048.py`, `... examples\03_demo_oaep.py`: **PASS**.
- RSA thật: mẫu `b'B' * 1/96/180` khôi phục đúng từ tối thiểu 1/2/3 ciphertext
  trong lần chạy đã quan sát; code kiểm tra điều kiện thực tế, không suy luận từ số byte.
- OAEP: CRT-and-root không khôi phục plaintext; cả ba người nhận giải mã đúng.
- Import `broadcastguard`, `broadcastguard.math_core` và version qua metadata: **PASS**.
- `.venv\Scripts\python.exe -m compileall -q broadcastguard examples tests`: **PASS**.
- Diff và staged-content/sensitive-file review được thực hiện trước commit.

### Git và phần còn tồn đọng

Repo cục bộ được init riêng vì clone thất bại, có origin URL dự kiến. Không có
code/commit cũ trong thư mục mới để ghi đè. Commit TASK 01 giữ cục bộ; tra SHA
bằng `git log -1 --format=%H`. Không merge main, không force-push.

**BLOCKED:** chưa đối chiếu code/quy tắc/lịch sử remote, chưa push. Không tạo URL
commit GitHub giả. Cần bản clone đúng lịch sử hoặc môi trường có quyền truy cập
GitHub; sau đó đọc repo, áp dụng thay đổi có review, chạy lại checks và push
feature branch. Không đẩy trực tiếp lịch sử cục bộ độc lập lên remote.

Chưa thực hiện TASK 02, Streamlit, AES/file sharing, benchmark, thí nghiệm 20 lần,
report học thuật hoặc triển khai. Dừng sau TASK 01 để chờ review.

## TASK 02 — PARTIAL: Attack Engine PASS, GitHub push BLOCKED

Ngày: 2026-11-05. Nhánh `feat/step-02-attack-engine` được tạo từ
`a30c675d9037543e7b7d4466ef0de2284847ee59`. Local `main` và tracking ref
`origin/main` cùng SHA trên; reviewer đã xác minh GitHub `main` cũng chứa SHA đó.
`git ls-remote` live vẫn bị proxy của phiên (`HTTP_PROXY`, `HTTPS_PROXY`,
`ALL_PROXY` là `http://127.0.0.1:9`) chặn. Không có Git proxy config riêng.
Không sửa cấu hình mạng hoặc force-push.

### Acceptance criteria và kết quả

- `attack_lab.py` có `build_scenario` sinh ba RSA 2048-bit/e=3 thật và tạo
  `PublicObservation` cho Alice/Bob/Charlie. Plaintext không rỗng và M nhỏ hơn
  mọi modulus; moduli phải đôi một nguyên tố cùng nhau.
- `attack_observations` chỉ nhận 1–3 public observations, theo bất kỳ tập con
  và thứ tự, dùng `broadcast_attack` của `math_core.py`. Đầu vào sai trả reason.
- `evaluate_experiment` giữ riêng ground truth, xác nhận ứng viên, điều kiện
  M³ < N và bốn trạng thái. Test phản ví dụ căn chính xác nhưng ứng viên sai.
- Có preview ngắn cho UI, vẫn giữ full n/c và các số CRT trong dataclass.
  `candidate_bytes` bảo toàn byte 0 đầu. Không có private key trong kết quả.
- Tạo `examples/04_attack_lab.py`; cập nhật README, context, decisions, AGENTS,
  smoke test cũ và thêm `tests/test_attack_lab.py`. Không sửa `math_core.py`
  hay ba demo cũ. Không thực hiện TASK 03 hoặc report.

### Kiểm chứng thực tế

- Trong venv Python 3.12.10 có cryptography 48.0.1, pytest 9.1.1; sandbox
  vẫn cần helper temp ngoài repo được mô tả ở TASK 01. Lệnh chạy:

```powershell
$taskTemp = (Resolve-Path '..\.task01-work\tmp').Path
$env:TEMP = $taskTemp
$env:TMP = $taskTemp
$env:BROADCASTGUARD_TASK_TEMP = $taskTemp
$env:PYTHONPATH = (Resolve-Path '..\.task01-work\runtime').Path
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
.\.venv\Scripts\python.exe -X utf8 -m pytest -q -p no:cacheprovider --basetemp '..\.task01-work\tmp\pytest-task02-final2'
```

  Kết quả cuối sau chỉnh sửa: **123 passed in 2.88s**. Bao gồm smoke tests của cả bốn demo,
  phản ví dụ exact root sai plaintext, subset Bob/Charlie và RSA 2048-bit thật.
- Chạy riêng demo 04 và `compileall`: PASS. Mẫu 180 byte `'B'` trong lần chạy
  cho 1/2 ciphertext chưa khôi phục, 3 ciphertext khôi phục đúng; tất cả modulus
  dài 2048 bit. Khóa bí mật không in ra và không lưu file.
- `git diff --check` và rà file staged/nhạy cảm trước commit: PASS.

### Git và giới hạn

`git push --set-upstream origin feat/step-02-attack-engine` đã được chạy từ repo
`Crypto-project` và **thất bại**: `Failed to connect to 127.0.0.1 port 9`.
Commit TASK 02 nằm trên nhánh local, chưa có URL commit GitHub. Không sửa proxy,
không force-push, không merge main. Tra SHA cuối bằng `git log -1 --format=%H`.

Các ciphertext/keypair demo là ngẫu nhiên, không kỳ vọng giá trị lặp lại; test
kiểm tra invariant. Builder chỉ dành cho Textbook RSA không an toàn. Chưa có UI,
OAEP workflow mới, AES-GCM, benchmark hay report. Không báo URL GitHub giả.

**Cập nhật GitHub sau TASK 02:** reviewer xác minh `main` và
`feat/step-02-attack-engine` đều trỏ tới
`74e2a6c43a3997dd8fdfd90605a3079379227f2e`. Lỗi proxy và askpass ở trên
là sự kiện lịch sử của phiên trước, không phải trạng thái GitHub hiện tại.

## TASK 03 — Attack Conditions Analyzer

Nhánh `feat/step-03-conditions-analyzer` xuất phát từ commit TASK 02 đã xác minh.
Trước khi sửa: working tree sạch; `git ls-remote` (bỏ proxy của riêng process)
xác nhận `main` và nhánh TASK 02 trên GitHub cùng SHA TASK 02; nhánh TASK 03
chưa tồn tại. Không thay `main` hoặc lịch sử cũ.

### Hoàn thành và acceptance criteria

- `conditions_analyzer.py`: `analyze_scenario` dùng lại attack engine và
  evaluator cho cả bảy tập con theo thứ tự 1/2/3 người. Có N, X, căn ứng viên,
  exact, bound, trạng thái khôi phục, giải thích và dict rows cho UI.
- `sweep_message_lengths`: thử `b"B" * length` với cùng ba public moduli, kiểm tra
  M < n trước khi mã hóa. Có matrix, minimum và prediction-vs-observation rows.
- Giữ nguyên `math_core.py`, `attack_lab.py` và API cũ. Không truyền M cho Eve.
  Kịch bản sai ciphertext, thiếu người nhận, modulus không hợp lệ, M quá lớn
  đều bị từ chối rõ. `wrong_exact_root` tách khỏi `recovered`.
- Tạo CLI demo 05, tests, review checkpoint. Cập nhật README, AGENTS,
  PROJECT_CONTEXT, DECISIONS và ghi tiến độ này; không làm TASK 04.

### Kiểm chứng thực tế

- Suite đầu có 144 pass, 1 fail do assertion smoke test đếm sai khoảng trắng
  căn cột CLI. Sửa assertion; suite cuối: **145 passed in 4.01s**.
- Lệnh pytest trong venv (sandbox dùng helper temp ngoài repo như TASK 01):

```powershell
$taskTemp = (Resolve-Path '..\.task01-work\tmp').Path
$env:TEMP=$taskTemp
$env:TMP=$taskTemp
$env:BROADCASTGUARD_TASK_TEMP=$taskTemp
$env:PYTHONPATH=(Resolve-Path '..\.task01-work\runtime').Path
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
.\.venv\Scripts\python.exe -X utf8 -m pytest -q -p no:cacheprovider --basetemp '..\.task01-work\tmp\pytest-task03-final'
```

- Chạy riêng cả năm lệnh `python -X utf8 examples/<01..05>.py` bằng venv:
  **PASS**. Demo 05 dùng 3 modulus RSA 2048 bit thật và cho minimum 1/2/3
  với 1/96/180 byte; ma trận có 7 cột tập người nhận, 21 kết quả.

```powershell
$files = @('01_demo_de_hieu.py','02_demo_rsa_2048.py','03_demo_oaep.py','04_attack_lab.py','05_conditions_analyzer.py')
foreach ($file in $files) { & .\.venv\Scripts\python.exe -X utf8 (Join-Path 'examples' $file) }
```
- `.venv\Scripts\python.exe -m compileall -q broadcastguard examples tests`:
  **PASS**. Import ba module: **PASS**. `git diff --check`: **PASS**.
- Review staged files và kiểm tra không có private key, token, venv hay dữ liệu
  sinh ra trước commit. SHA cuối và trạng thái push xem `git log -1` và remote.

### Giới hạn

Giá trị khóa RSA demo ngẫu nhiên, không dùng làm benchmark. Với ba modulus hợp
lệ mỗi modulus đều lớn hơn M, tập cả ba luôn thỏa M³ < N, nên no-success chỉ
áp dụng khi tổng hợp một tập kết quả bị lọc/rỗng. Chưa có UI, AES-GCM, report
hay thí nghiệm hiệu năng. `REVIEW_CHECKPOINT.md` là tài liệu bàn giao ngắn.
