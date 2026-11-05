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

## Stack

Python >=3.11, standard library cho số học; pyca/cryptography cho RSA và OAEP;
pytest cho test; setuptools và pyproject.toml để đóng gói. Streamlit dự kiến
cho giao diện ở task sau, chưa cài vào runtime dependencies.
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
  để tách tác động của padding. Với cấu hình này, giới hạn plaintext là 190 byte.
- Chia sẻ an toàn sau này giả định public keys người nhận đã được xác thực trước.
  Chưa xử lý phân phối/chứng thực public keys qua mạng, danh tính người gửi,
  replay, thu hồi khóa hoặc bảo vệ endpoint bị chiếm quyền. AES-GCM không tự
  chứng minh danh tính người gửi; các giới hạn này không được quảng cáo thành tính năng.
- Secure Sharing dự kiến RSA 2048 bit e=65537, AES-256-GCM, khóa AES mới 32 byte
  và nonce 12 byte mới mỗi lần gửi; không tái sử dụng nonce với cùng khóa.
  Metadata cần được serialize nhất quán và xác thực bằng AAD.

## Quy tắc bảo mật và tái lập

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
