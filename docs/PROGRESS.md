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

## TASK 04 — RSA-OAEP Defense Lab (chờ reviewer xác nhận)

Nhánh `feat/step-04-oaep-defense` được tạo từ TASK 03 đã review, SHA
`3ef78b63877017f0e92a1f71f1eab1ef2dab0569`. Trước khi sửa, working tree
sạch, HEAD khớp SHA này và remote là `Dung092005/Crypto-project.git`.

### Acceptance criteria và thay đổi thực tế

- `defense_lab.py` tạo đúng một bộ ba keypair RSA-2048/e=3 trong RAM cho cả
  Textbook RSA và RSA-OAEP. Cùng plaintext, người nhận, khóa, tập ba ciphertext
  và `attack_observations()`; chỉ scheme mã hóa thay đổi. Có kiểm tra kiểu,
  rỗng, giới hạn OAEP 190 byte, `M < n_i`, e/bit length và moduli đôi một coprime.
- OAEP dùng `cryptography` SHA-256/MGF1(SHA-256), label=None theo RFC 8017.
  `SchemeObservation` gắn nhãn scheme với dữ liệu công khai. Bộ đánh giá riêng
  chỉ sau Eve mới so sánh ứng viên với M; không áp dụng bound Textbook cho OAEP.
  `exact=True` không tự đồng nghĩa khôi phục đúng.
- Người nhận hợp lệ giải mã OAEP bằng private key tương ứng trong RAM; kết quả
  chỉ giữ trạng thái của Alice/Bob/Charlie. Thử lặp OAEP cùng plaintext/key,
  ghi ciphertext có khác và từng lần có giải mã đúng; Textbook RSA lặp lại.
- `DefenseComparison` trả summary, per-recipient và detail rows cho UI sau.
  Tạo CLI demo 06, tests và cập nhật README/context/decisions/checkpoint.
  Không sửa API hoặc code của TASK 01–03, không xây UI/AES/report.

### Kiểm chứng đã chạy

- Python 3.12.10, Windows; venv dùng workaround ACL tạm ngoài repo như TASK 01.
  Lệnh suite cuối:

```powershell
$taskTemp = (Resolve-Path '..\.task01-work\tmp').Path
$env:TEMP=$taskTemp
$env:TMP=$taskTemp
$env:BROADCASTGUARD_TASK_TEMP=$taskTemp
$env:PYTHONPATH=(Resolve-Path '..\.task01-work\runtime').Path
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
.\.venv\Scripts\python.exe -X utf8 -m pytest -q -p no:cacheprovider --basetemp '..\.task01-work\tmp\pytest-task04-final2'
```

  Kết quả cuối: **162 passed in 4.40s**; bao gồm smoke tests của demo 01–06.
- Chạy riêng `python -X utf8 examples/<01..06>.py` bằng venv: **cả sáu PASS**.
  Demo 06 với 180 byte: Textbook RSA có `exact=True`, khôi phục M;
  OAEP có `exact=False`, không khôi phục M; Alice/Bob/Charlie đều giải mã
  đúng. Ba ciphertext OAEP lặp cùng khóa khác nhau, tất cả giải mã đúng;
  hai lần Textbook RSA cho cùng ciphertext. Đây là một run, không phải benchmark.
- `.venv\Scripts\python.exe -m compileall -q broadcastguard examples tests`:
  **PASS**. Import `math_core`, `attack_lab`, `conditions_analyzer`,
  `defense_lab`: **PASS**. `git diff --check`: **PASS**.
- Kiểm tra file staged và mẫu private key/token trước commit; trạng thái GitHub
  và SHA remote được đối chiếu riêng sau push.

### Giới hạn

Kết quả OAEP ngẫu nhiên có thể khác ở lần chạy khác, nên tests kiểm tra invariant,
không so ciphertext cố định. Không suy ra an toàn tuyệt đối từ thất bại của
CRT-and-root. Phép thử e=3 chỉ để cô lập tác động padding; Secure Sharing ở
TASK 05 sẽ dùng e=65537 sau khi được giao riêng. Chưa có UI, AES-GCM, report
hoặc số liệu nghiên cứu/hiệu năng.

## TASK 05 — Secure Hybrid File Sharing (chờ reviewer xác nhận)

Nhánh `feat/step-05-hybrid-sharing` tạo từ TASK 04 đã review,
`2ab75d50a2fe036aa3811809b7b9a608c46bbdc4`. Trước khi sửa, working tree
sạch, HEAD khớp baseline, remote là `Dung092005/Crypto-project.git`. Graph
`codebase-memory` chưa index repo này; đã đọc source thực tế trong phạm vi task.

### Acceptance criteria và công việc đã làm

- `hybrid_sharing.py` tách keypair demo trong RAM, public recipients, AES-GCM
  mã hóa file một lần, RSA-OAEP bọc khóa AES riêng, package JSON v1, validation,
  giải mã theo người nhận, summary công khai và wrapper trạng thái cho UI.
  Không import các module Textbook
  RSA. Dùng RSA-2048/e=65537, OAEP SHA-256/MGF1-SHA256/label=None, AES-256-GCM,
  khóa 32 byte mới và nonce 12 byte mới cho từng package; GCM tag đủ 16 byte.
- Header canonical UTF-8 JSON (sorted keys, compact separators, Base64) làm
  AAD, gồm version/algorithms/filename/size/nonce/recipient entries/wrapped
  keys. Giới hạn 1–5 recipients, file 5 MiB, serialized package 8 MiB.
  Từ chối trùng ID/public key, version/algorithm sai, duplicate JSON keys,
  Base64/nonce/kích thước sai và path-like filename. `PackageValidationError`
  tách khỏi `DecryptionFailed`; không trả plaintext khi xác thực thất bại.
- CLI demo 07 và tests thực thi 1/3/5 recipients, file rỗng/binary/UTF-8,
  10 KB/100 KB/1 MiB/5 MiB, serialization và các kiểu tampering. Tài liệu
  `SECURE_SHARING_DESIGN.md` ghi rõ luồng, format và giới hạn bảo mật.
  Không xây Streamlit, networking, database, benchmark hoặc report.

### Kiểm chứng đã thực hiện

- Venv Python 3.12.10. Cài editable project + dev extra thành công bằng
  `.venv\Scripts\python.exe -X utf8 -m pip install --no-index --no-build-isolation -e ".[dev]"`;
  cryptography 48.0.1, pytest 9.1.1 đã có sẵn. Sandbox cần TEMP/PYTHONPATH
  workaround ngoài repo như TASK 01.
- `tests/test_hybrid_sharing.py`: ban đầu **39 passed**. Lần chạy đầu lỗi setup do pytest
  tự đưa dữ liệu 1 MiB vào tên case/đường dẫn Windows; đặt case IDs ngắn,
  chạy lại **39 passed in 0.84s**. Sau đó thêm test trạng thái UI; suite cuối
  có 40 bài hybrid. Không có lỗi thuật toán.
- Toàn bộ suite gồm smoke tests demo 01–07: **203 passed in 5.34s** ở lần chạy cuối.
  Lệnh:

```powershell
$taskTemp = (Resolve-Path '..\.task01-work\tmp').Path
$env:TEMP=$taskTemp
$env:TMP=$taskTemp
$env:BROADCASTGUARD_TASK_TEMP=$taskTemp
$env:PYTHONPATH=(Resolve-Path '..\.task01-work\runtime').Path
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
.\.venv\Scripts\python.exe -X utf8 -m pytest -q -p no:cacheprovider --basetemp '..\.task01-work\tmp\pytest-task05-final2'
```

- Chạy riêng cả bảy demo `python -X utf8 examples/<01..07>.py`: **PASS**.
  Demo 07: Alice/Bob/Charlie khôi phục đúng file giả lập; khóa Bob dùng cho
  Alice bị từ chối; sửa một byte ciphertext bị từ chối. Output kích thước
  package của run này không phải benchmark.
- `.venv\Scripts\python.exe -m compileall -q broadcastguard examples tests`:
  **PASS**. Import năm module: **PASS**. `git diff --check`: **PASS**.
- Rà staged files và mẫu private key/token trước commit; SHA remote đối chiếu
  sau push.

### Giới hạn và technical debt

Public keys phải được xác thực ở ngoài module; fingerprint không tự chứng thực
danh tính. Không có chữ ký người gửi, chống replay/thay thế nguyên package,
key persistence hoặc streaming trên 5 MiB. Filename chỉ là metadata hiển thị,
không là đường dẫn ghi file. Tests kiểm tra invariant với randomness thật,
không tạo số liệu hiệu năng nghiên cứu. TASK 06 là Attack Lab Streamlit UI sau
khi TASK 05 được review và giao riêng; academic report chưa thực hiện.

## TASK 06 — Interactive Attack Lab UI (chờ reviewer xác nhận)

Nhánh `feat/step-06-attack-ui` được tạo từ commit TASK 05 đã review
`3e8b5249eb832899a22253b946683ada99792bbc`; working tree sạch trước khi sửa.
Giữ nguyên API và code của các module mật mã TASK 01–05. `codebase-memory` không
index repo này, nên đã đọc source thực tế. Áp dụng skill `developing-with-streamlit`
với tài liệu khớp Streamlit 1.60.0 đã cài.

### Acceptance criteria và thay đổi

- `app.py`: Attack Lab gồm giới thiệu, sender simulator, ba recipient cards,
  Eve chọn 1–3 ciphertext, walkthrough CRT/căn bậc ba, bảng bảy tập con và
  sweep 1/96/180 byte. Dữ liệu tính bằng backend thật. Preset/custom UTF-8
  tối đa 190 byte, không cắt ngắn. Eve chỉ nhận public observations; evaluator
  được gọi sau để đối chiếu với plaintext. Trạng thái `exact` và `recovered`
  tách riêng; điều kiện M³ < N gắn nhãn Experimenter.
- Scenario, analysis, attack và sweep chỉ ở `st.session_state`. Generate mới
  sinh khóa và reset kết quả; chọn widget không sinh khóa. Sweep chỉ tính theo
  yêu cầu một lần mỗi scenario. Không có cache toàn cục dữ liệu người dùng.
- `ui/attack_presenter.py` định dạng preview và bảng; `.streamlit/config.toml`
  theme dark; `requirements.txt` pin runtime Cloud; `pyproject.toml` thêm
  Streamlit; `.gitignore` bỏ qua secrets file. Tạo `UI_DESIGN.md`,
  `DEPLOYMENT.md`; chưa deploy hoặc làm UI TASK 07–08.

### Kiểm chứng thực tế

- Python 3.12.10, Streamlit 1.60.0, cryptography 48.0.1. Lệnh
  `.venv\Scripts\python.exe -X utf8 -m pip install --no-index --no-build-isolation -e ".[dev]"`
  và `-r requirements.txt`: **PASS** với các dependencies đã có.
- `tests/test_attack_ui.py` dùng `streamlit.testing.v1.AppTest`: **9 passed**.
  Test thật startup, Generate, tập 1/2/3 ciphertext, threshold 1/96/180,
  reset, input lỗi, bảy subset, sweep, wrong exact root và cô lập hai sessions.
- Toàn bộ pytest lần cuối: **212 passed in 15.60s**. Lệnh trong venv (sandbox cần
  TEMP/PYTHONPATH workaround ngoài repo như TASK 01):

```powershell
$taskTemp = (Resolve-Path '..\.task01-work\tmp').Path
$env:TEMP=$taskTemp
$env:TMP=$taskTemp
$env:BROADCASTGUARD_TASK_TEMP=$taskTemp
$env:PYTHONPATH=(Resolve-Path '..\.task01-work\runtime').Path
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
.\.venv\Scripts\python.exe -X utf8 -m pytest -q -p no:cacheprovider --basetemp '..\.task01-work\tmp\pytest-task06-final3'
```

- Chạy riêng demo CLI 01–07: **cả bảy PASS**. `compileall -q broadcastguard
  examples tests app.py`: **PASS**; import sáu module liên quan và Streamlit:
  **PASS**; `git diff --check`: **PASS**.
- `.venv\Scripts\python.exe -m streamlit run app.py --server.headless true
  --server.port 8501`: server khởi động, `http://127.0.0.1:8501/_stcore/health`
  trả **200 ok**, không có crash terminal. Không deploy lên Cloud.
- Không có screenshot hoặc xác nhận bằng mắt: browser host của computer-use
  không khả dụng; Playwright headless bị sandbox Windows từ chối tạo pipe
  (`WinError 5`); lệnh khởi chạy Chrome headless bằng `Start-Process` bị
  automatic approval review từ chối vì thao tác cần sandbox approval nhưng
  loại approval đó bị tắt. AppTest và health check là bằng chứng runtime/UI.

### Giới hạn

Chưa kiểm tra trực quan desktop/mobile bằng browser thật trong môi trường này.
Việc sinh ba khóa RSA trong Cloud vẫn có thể chậm khi tài nguyên hạn chế;
spinner và yêu cầu bấm Generate giúp tránh tạo khóa trên mỗi rerun. Không có
Defense UI, Secure Sharing UI, benchmark hoặc report. TASK 07 cần được giao
riêng sau review TASK 06.

**Cập nhật sau TASK 06:** Theo yêu cầu của người dùng, `main` được fast-forward
từ `74e2a6c43a3997dd8fdfd90605a3079379227f2e` đến commit TASK 06
`0dc6ad3a8f6bf9cd5abb79ab7ee681d3a2af268d` và push lên GitHub; SHA
remote đã xác minh trùng local. Hướng dẫn Cloud được cập nhật để chọn `main`
khi nhánh đó còn chứa commit TASK 06. Chưa deploy app.

## TASK 07 — Defense Lab UI và multipage integration

Baseline chính xác `0dc6ad3a8f6bf9cd5abb79ab7ee681d3a2af268d`;
working tree sạch trước khi tạo `feat/step-07-defense-ui`. `main` lúc bắt đầu
ở docs commit `806ba9e`; không lấy nhánh này làm base.

Acceptance criteria đã thực hiện: `app.py` chỉ làm router `st.Page` +
`st.navigation` ở top; Attack Lab TASK 06 được chuyển sang `ui/attack_page.py`
và giữ nguyên tương tác; Defense Lab mới gọi `run_defense_comparison()` thật.
Hai panel đọc status thực tế, bảng ba public moduli chứng minh dùng cùng keys,
Eve thử cùng CRT/root, randomization và ba trạng thái giải mã hợp lệ. Input
1/96/180/190 byte hoặc UTF-8, reject rỗng/>190 byte. State Defense tách khỏi
Attack, không cache key/plaintext và không sinh khóa khi chỉ rerun/chuyển trang.
Không sửa API mật mã TASK 01–05.

Kiểm chứng thực tế:

- `tests/test_attack_ui.py`: **9 passed** sau refactor multipage.
- `tests/test_defense_ui.py`: **8 passed**; AppTest kiểm tra startup, điều
  hướng, validation, cùng moduli/e=3, Textbook recovered, OAEP không recovered
  trong run, randomization, giải mã 3 người nhận, 190/191 byte, state qua
  hai trang, custom UTF-8, không sinh lại key khi rerun, cô lập hai sessions.
- Full suite: **220 passed in 27.57s**. Lần đầu 212 passed + 7 errors ở
  `tests/test_examples.py` do pytest không được tạo temp tại Windows Temp
  (`WinError 5`); chạy lại với basetemp trong workspace thì toàn bộ PASS.

```powershell
$taskTemp = (Resolve-Path '..\.task01-work\tmp').Path
$taskRuntime = (Resolve-Path '..\.task01-work\runtime').Path
$env:TEMP=$taskTemp; $env:TMP=$taskTemp
$env:BROADCASTGUARD_TASK_TEMP=$taskTemp; $env:PYTHONPATH=$taskRuntime
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'; $env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\python.exe -X utf8 -m pytest -q -p no:cacheprovider --basetemp '..\.task01-work\tmp\pytest-task07-final2'
```

- `examples/01_demo_de_hieu.py` đến `07_hybrid_sharing.py` chạy riêng:
  **7/7 PASS**. `compileall -q app.py app_pages broadcastguard examples tests`:
  **PASS**; import Streamlit và các module backend/UI: **PASS**.
- `python -m streamlit run app.py --server.headless true --server.port 8503`:
  server khởi động; `GET /_stcore/health` trả **200 ok**. `git diff --check`:
  **PASS** trước commit. AppTest kiểm chứng luồng UI; browser host CUA không
  khả dụng nên **chưa** visual QA bằng trình duyệt/screenshot.
- Chạy riêng `run_defense_comparison(b"B" * 180)`: cùng moduli `True`,
  Textbook `recovered`/exact root `True`, OAEP `no_exact_root` trong run này,
  giải mã `[True, True, True]`, randomization flags đều `True`.
- `pip check` trong venv hiện tại **không PASS** vì các package nghiên cứu
  ngoài BroadcastGuard có constraint xung đột (protobuf, pyopenssl, ragas,
  sentence-transformers). Không thay đổi dependency dự án để sửa môi trường
  ngoài phạm vi; `pytest`, demos, imports và runtime đều PASS.

TASK 08 Secure Sharing UI chưa làm; không làm benchmark/report hoặc public
deployment ở TASK 07. Reviewer cần kiểm tra branch và UI thực tế trước khi
người dùng triển khai Cloud.

## Repository documentation refresh · README + MIT

Theo yêu cầu của người dùng, viết lại root README cho người mới: mục tiêu,
trạng thái ba lab, quick start Windows/macOS/Linux, các bước demo, lệnh test,
kiến trúc, giới hạn bảo mật, liên kết tài liệu và hỗ trợ. Thêm `LICENSE` MIT
với holder `BroadcastGuard contributors` (2026); `pyproject.toml` khai báo
SPDX `MIT`, `license-files = ["LICENSE"]` và yêu cầu setuptools >=77.0.3 để
build backend hiểu PEP 639. Không đổi code mật mã hoặc giao diện.

Kiểm chứng: editable install và wheel build PASS; wheel chứa LICENSE và
`License-Expression: MIT`. Các liên kết nội bộ trong README tồn tại.
Toàn bộ pytest **220 passed in 31.52s** với `--basetemp` trong workspace;
compileall, imports và `git diff --check` PASS. Không có benchmark hoặc
public deployment mới được thực hiện ở bước tài liệu này.

## TASK 08 — Scientific experiments and evidence collection

Baseline: verified `main` commit `626c68e881a459d63a82f7f844ab558abed81752`; branch `feat/step-08-research-experiments`. Added an offline E1–E4 runner, raw CSV schemas, read-back validation, statistics and a predeclared protocol. E1 tests all seven recipient subsets for 1/96/180-byte `B` samples and a 96-byte leading-zero sample, using the same three e=3 moduli within each trial. E2 compares Textbook/OAEP on those keys. E3 measures prepared-key hybrid workflows separately from RSA keygen. E4 records controlled acceptance/rejection cases. `results/` is ignored; no UI module is changed.

Official run ID, sample counts, validation and test commands are recorded in `EXPERIMENT_EVIDENCE.md`. Academic report and TASK 09/10 are still pending.

**Official execution:** runner source commit `46c455819e4588736d4777c252d844fa03e7caf3`, clean tree; `official-20261106T083221Z-3bbf57cc`, 20 measured repetitions and 2 E3 warmups. `python -m experiments.run_experiments --mode official --repetitions 20 --warmup 2 --output results/official-task08-20261106` completed: E1 560, E2 60, E3 180, separate keygen 60, E4 11 rows. `--validate-only` returned `VALID` on both raw and curated copies. No failed rows. Quick preflight and a separate quick test run also validated. Full suite: **225 passed in 24.15s** with the project's Windows sandbox temp settings. Technical results and limits are in `EXPERIMENT_EVIDENCE.md`; no formal report was written.
