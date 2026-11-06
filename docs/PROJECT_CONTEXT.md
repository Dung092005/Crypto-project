# Bối cảnh dự án BroadcastGuard

## Mục tiêu và phạm vi

Project giữa kỳ môn Introduction to Cryptography: giải thích được toán học,
có code dễ bảo trì và kiểm thử tái lập. Đây là mô phỏng giáo dục chạy cục bộ,
không phải dịch vụ nhắn tin thương mại. Nhóm có trình độ lập trình không đồng đều;
ưu tiên module nhỏ, demo dễ đọc, kiểm thử và phân tích hơn tính năng trang trí.

Ba màn hình dự kiến:

1. ATTACK LAB: Textbook RSA e=3, CRT và căn nguyên; phân tích điều kiện theo
   số bản mã và độ lớn thông điệp. Có thể khôi phục từ 1/2/3 bản mã tùy điều kiện.
2. DEFENSE LAB: RSA-OAEP để đối chiếu cùng phép thử; người nhận hợp lệ giải mã được.
3. SECURE SHARING: AES-256-GCM mã hóa file một lần; RSA-OAEP khóa AES riêng
   cho từng người nhận, metadata làm AAD; dữ liệu bị sửa phải bị từ chối.

TASK 01 chỉ bootstrap package, chuyển lõi và demo có sẵn, tests và tài liệu.
Không xây các màn hình, AES/file sharing, analyzer giao diện, benchmark hay report.

TASK 02 xây `attack_lab.py`: builder sinh ba RSA 2048-bit/e=3 và tạo public
observations; Eve chỉ nhận quan sát công khai; evaluator riêng giữ plaintext
để xác nhận kết quả. `AttackOutcome.exact` chỉ là tính chất căn nguyên, còn
`ExperimentEvaluation.status` phân biệt khôi phục đúng, căn đúng nhưng sai
plaintext, không có căn nguyên và đầu vào không hợp lệ. Chưa có giao diện.

TASK 03 thêm Attack Conditions Analyzer: xét bảy tập con không rỗng của ba
người nhận và quét các thông điệp `b"B" * length` với cùng bộ modulus. Kết quả
so sánh dự đoán M³ < N với ứng viên Eve khôi phục và có trạng thái riêng cho
căn chính xác nhưng sai M. Tất cả giải thích dùng M được gắn nhãn là góc nhìn
người đánh giá, không phải tri thức của Eve. Chưa có giao diện hoặc phép đo hiệu năng.

TASK 04 thêm RSA-OAEP Defense Lab. Một lần chạy dùng cùng plaintext bytes và
cùng ba keypair RSA-2048/e=3 cho Textbook RSA và OAEP-SHA256/MGF1-SHA256,
label rỗng. Chỉ cách mã hóa thay đổi; Eve dùng cùng CRT + căn bậc ba với ba
quan sát công khai. Bộ đánh giá tách riêng so sánh ứng viên với plaintext,
không dùng điều kiện Textbook `M³ < N` để diễn giải OAEP. Private keys chỉ nằm
trong RAM lúc tạo và giải mã thí nghiệm, không nằm trong dữ liệu trả về.

TASK 05 thêm Secure Hybrid File Sharing tại `hybrid_sharing.py`: mã hóa file
bytes (0–5 MiB) **một lần** bằng AES-256-GCM với khóa 32 byte/nonce 12 byte
mới mỗi lần; RSA-2048/e=65537 OAEP-SHA256/MGF1-SHA256 bọc khóa AES cho mỗi
người nhận. Header JSON canonical v1 làm AAD và gồm cả recipient list cùng
wrapped keys. Package không chứa plaintext, AES key rõ hoặc private key.
API từ chối package sai cấu trúc và lỗi xác thực riêng; không trả plaintext
một phần. Filename chỉ dùng hiển thị, không quyết định đường dẫn ghi file.

TASK 06 thêm Streamlit Attack Lab UI tại `app.py`. Người dùng chọn preset
1/96/180 byte hoặc custom UTF-8 tối đa 190 byte, Generate tạo RSA scenario,
Eve chọn 1–3 quan sát công khai và Run Attack. UI tách phép tính Eve khỏi bộ
đánh giá biết plaintext, giải thích CRT/căn nguyên và hiển thị bảy subset cùng
sweep độ dài. Kịch bản/attack/sweep chỉ trong session state; không cache toàn
cục dữ liệu người dùng hoặc tự sinh khóa khi rerun. Cloud deployment chưa thực hiện.

## Stack

Python >=3.11, standard library cho số học; pyca/cryptography cho RSA và OAEP;
Streamlit >=1.60 cho Attack Lab UI; pytest cho test; setuptools và pyproject.toml
để đóng gói. Runtime Cloud pin trong `requirements.txt`; config theme ở
`.streamlit/config.toml`. Defense/Secure Sharing UI thuộc task sau.
Không Docker, database, server hay authentication trong bước này.

## Threat model và giả định mật mã

- Eve chỉ quan sát ciphertext và public keys `(n, e)`, không có private keys.
  Hàm tấn công chỉ nhận ciphertexts, moduli và exponent; không truy cập private key.
- Broadcast attack xét cùng một thông điệp nguyên không padding và cùng exponent.
  Moduli đôi một nguyên tố cùng nhau. Khi `M**e < product(moduli)`, CRT trả
  chính xác `M**e` để lấy căn nguyên. Mỗi phép RSA yêu cầu `0 <= M < n_i`.
- `exact=True` là thuộc tính toán học của ứng viên, không xác nhận plaintext gốc.
  Chỉ môi trường thử nghiệm mới so sánh với bản gốc đã biết.
- Thiếu điều kiện hoặc thất bại một phương pháp không chứng minh hệ thống an toàn.
- OAEP của thư viện dùng SHA-256 và MGF1-SHA256; demo dùng RSA 2048 bit e=3
  để tách tác động của padding. Với cấu hình này, giới hạn plaintext là 190 byte
  theo `mLen <= k - 2*hLen - 2` của [RFC 8017 §7.1](https://www.rfc-editor.org/rfc/rfc8017.html#section-7.1).
  OAEP mã hóa ngẫu nhiên thành các representative khác nhau trước RSA; không thể
  suy ra kết quả OAEP từ bất đẳng thức dành cho cùng một M của Textbook RSA.
- Chia sẻ an toàn giả định public keys người nhận đã được xác thực trước.
  TASK 05 áp dụng giả định này; fingerprint là SHA-256 của DER SPKI nhưng không
  tự chứng thực danh tính. Không có sender authentication hoặc chữ ký số.
  Chưa xử lý phân phối/chứng thực public keys qua mạng, danh tính người gửi,
  replay, thu hồi khóa hoặc bảo vệ endpoint bị chiếm quyền. AES-GCM không tự
  chứng minh danh tính người gửi; các giới hạn này không được quảng cáo thành tính năng.
- Secure Sharing dùng RSA 2048 bit e=65537, AES-256-GCM, khóa AES mới 32 byte
  và nonce 12 byte mới mỗi lần gửi; không tái sử dụng nonce với cùng khóa.
  Metadata cần được serialize nhất quán và xác thực bằng AAD.

## Quy tắc bảo mật và tái lập

TASK 08 bổ sung thí nghiệm offline E1–E4 và bằng chứng có provenance; chi tiết thiết kế, biến độc lập/phụ thuộc, điều kiện kiểm soát, schema và giới hạn diễn giải nằm trong `EXPERIMENT_PROTOCOL.md`. Các phép đo hiệu năng không chạy từ Streamlit, không tính sinh khóa vào chi phí mã hóa file thường lệ, và không tự động biến thất bại của CRT-and-root trên OAEP thành một chứng minh bảo mật. TASK 08 không mở rộng giao diện hay viết academic report.

TASK 07 trình bày hai phòng thí nghiệm qua `app.py` và `st.navigation`.
Attack Lab giữ Scenario/Outcome trong `st.session_state` hiện có; Defense Lab
giữ `DefenseComparison` và run number trong keys riêng cùng browser session.
`run_defense_comparison()` dùng cùng plaintext, ba RSA-2048/e=3 keypairs và
cùng phép CRT-and-root cho hai mode, chỉ đổi Textbook RSA sang OAEP-SHA256.
Private keys chỉ tồn tại bên trong orchestration, không xuất hiện trong UI
state. OAEP randomization là quan sát thực nghiệm; `exact_root` phải được
đối chiếu riêng với plaintext gốc. Entrypoint Cloud vẫn là `app.py`.

Textbook RSA nằm riêng trong attack lab; không được gọi để bảo vệ file thật.
Không tự viết OAEP/AES/bộ sinh số nguyên tố. Không ghi private key ra đĩa hoặc
log; mọi khóa demo chỉ tồn tại trong RAM. Ignore credential, môi trường và output.
Unit tests số học dùng đầu vào xác định; RSA/OAEP dùng nguồn ngẫu nhiên mật mã,
kiểm tra invariant thay vì mong đợi ciphertext xác định. Ghi phiên bản và lệnh
đã chạy; các kết quả hiện tại là kiểm chứng engineering, chưa phải số liệu nghiên cứu.

## Acceptance criteria của TASK 01

- Kiểm tra repo/branch/remote và starter ZIP; không làm mất code đã tồn tại.
- Kiểm tra đường dẫn archive trước giải nén; đọc đủ bảy file và chạy baseline.
- Source/examples/tests tách biệt; cài package có dev extra từ pyproject.toml.
- CRT, căn nguyên lớn, AttackResult, đổi bytes có validation và giữ hành vi đúng.
- Tests gồm ví dụ M=12, trường hợp thiếu bản mã, exact khác recovered, đầu vào sai.
- Ba demo chạy qua package mới, không sửa sys.path và không ghi private key.
- README Windows, AGENTS, context/progress/decisions đủ cho người tiếp tục.
- Chạy pytest/import/syntax/diff, kiểm tra dữ liệu nhạy cảm trước commit.
- Commit trên feature branch; chỉ push khi kết nối được repo và đối chiếu lịch sử.
  Nếu môi trường chặn phần nào, ghi BLOCKED và không báo toàn task PASS.
- Dừng sau TASK 01, chờ review.
TASK 09 phan tich khoa hoc duoc them tai analysis/ va docs/analysis/. CLI chi doc official evidence, chay validator hien co, kiem tra manifest/SHA/schema/so dong va tinh lai summary tu raw CSV truoc khi sinh bang va hinh. Pipeline tach E1/E2/E3/E4 theo don vi quan sat va khong chay benchmark khi import. Mo hinh kich thuoc package bam theo serializer JSON canonical v1 hien tai, giu filename va recipient IDs cua E3, va kiem tra residual tren ca 9 cau hinh. Hinh PNG 300-DPI va SVG duoc sinh bang Matplotlib Agg; app.py va cac trang Streamlit khong bi thay doi.
