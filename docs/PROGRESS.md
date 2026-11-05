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
