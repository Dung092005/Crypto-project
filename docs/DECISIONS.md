# Quyết định kiến trúc

## D001 — Package đơn giản với source ở broadcastguard

Dùng package ở root, bên cạnh examples và tests; chưa cần src layout cho quy mô
này. Setuptools chỉ discover `broadcastguard*`. Examples import package đã cài;
smoke tests chạy ngoài thư mục repo và bỏ PYTHONPATH để kiểm tra import thực tế.
Không thao tác sys.path. Không thêm module trống cho chức năng tương lai.

## D002 — Giữ lõi starter, siết hợp đồng đầu vào

Giữ CRT với nghịch đảo modular, binary search căn nguyên và dataclass bất biến
AttackResult. Không dùng float. Thêm validation số nguyên không nhận bool,
sequence, miền giá trị và bytes. Đổi số sang bytes yêu cầu length >=1 và báo
ValueError khi không vừa độ dài; khác starter vốn có thể lộ OverflowError hoặc
chấp nhận độ dài 0. Giữ độ dài tường minh để không mất byte 0 đầu.
Các dữ liệu hợp lệ của starter giữ nguyên kết quả.

## D003 — Tách mô phỏng không an toàn khỏi chức năng bảo mật

math_core chỉ phục vụ attack lab. Module bảo mật sau này phải tách riêng và dùng
RSA-OAEP/AES-GCM từ thư viện, không tái sử dụng Textbook RSA. Chưa tạo module
file encryption trong TASK 01. Demo OAEP có mặt vì được migrate từ starter,
không đồng nghĩa đã xây DEFENSE LAB hoàn chỉnh.

## D004 — Exact root không đồng nghĩa plaintext được xác nhận

API trả root và exact, không tự đặt cờ recovered khi không biết plaintext.
Test phản ví dụ M=2, n=7 cho ứng viên 1 exact nhưng sai plaintext.
Demo OAEP so sánh số trước khi đổi bytes, tránh OverflowError nếu ứng viên
không vừa độ dài thông điệp. Không suy luận bảo mật tuyệt đối từ một lần thử.

## D005 — Dependencies và test tối thiểu

Giữ range cryptography của starter; chỉ thêm pytest trong dev extra và setuptools
cho packaging. Không thêm Streamlit cho CLI bootstrap. Tests toán học xác định;
demo RSA thật dùng CSPRNG và test invariant, không seed hoặc snapshot ciphertext.
Demo kiểm tra lỗi bằng exception để vẫn kiểm chứng khi Python bật -O.

## D006 — Giữ an toàn lịch sử khi GitHub bị chặn

Workspace ban đầu không phải repo và không có code BroadcastGuard. Clone HTTPS
bị chặn bởi proxy kết nối 127.0.0.1:9. Chuẩn bị thư mục mới từ starter và giữ
commit cục bộ nếu chưa nhận được clone có lịch sử. Không khẳng định đã đọc repo
remote, không merge/push lịch sử độc lập lên GitHub. Khi có truy cập, cần clone
repo thật, đọc quy tắc/code rồi áp dụng commit bằng cherry-pick hoặc patch có review.
Remote URL cấu hình chỉ thể hiện đích dự kiến, không chứng minh truy cập được.

## D007 — Attack Lab chia ba trách nhiệm

`build_scenario` tạo khóa RSA thật, mã hóa cùng M và chỉ giữ public observations
trong kết quả; private keys chỉ tồn tại trong phạm vi hàm. `attack_observations`
nhận 1–3 `PublicObservation` theo bất kỳ tập con/thứ tự, không nhận scenario,
plaintext hoặc private key. `evaluate_experiment` mới nhận scenario chứa
plaintext và đối chiếu kết quả Eve với ground truth. Cách tách này giữ ranh giới
threat model rõ cho sinh viên và cho UI sau này.

## D008 — Kết quả toán học và đánh giá thực nghiệm là hai lớp dữ liệu

`AttackOutcome` chứa các giá trị nguyên đầy đủ (`product`, `combined`,
`candidate`) cùng `exact`, `reason`, `steps`; `PublicObservation` có thuộc tính
preview để UI không phải in số 2048 bit. `ExperimentEvaluation` có bốn trạng
thái riêng, điều kiện M³ < N và `candidate_bytes` theo độ dài bản gốc để giữ
byte 0 đầu. Input sai trả reason từ attacker; evaluator từ chối ghép outcome
với quan sát của run khác. Không thêm framework hay class chứa khóa bí mật.

## D009 — Dùng cùng public moduli cho phép quét độ dài

`sweep_message_lengths` lấy một kịch bản RSA có sẵn rồi mã hóa các mẫu
`b"B" * length` bằng đúng ba modulus đó. Mỗi mẫu là một `AttackScenario` được
đánh giá riêng; Eve vẫn chỉ nhận quan sát công khai. Cách này cô lập biến độ
lớn thông điệp khỏi biến khóa, không seed bộ sinh khóa. Analyzer từ chối
kịch bản có ciphertext không khớp M, modulus không hợp lệ, thiếu người nhận
hoặc M không nhỏ hơn mọi modulus. Không sửa API toán học và Attack Lab cũ.

## D010 — Tách trạng thái kết quả khỏi màu giao diện

`SubsetAnalysis` giữ N, X và căn nguyên đầy đủ; `status` dùng semantic labels
`recovered`, `wrong_exact_root`, `no_exact_root`. Các hàm `table_rows`,
`matrix_rows`, `minimum_rows`, `comparison_rows` trả dict đơn giản; UI sau này
chọn màu. Lời giải thích có nhãn `Experimenter` nếu dùng M³ < N. Với ba
modulus hợp lệ cùng lớn hơn M, tích của cả ba chắc chắn lớn hơn M³; tuy vậy
thuộc tính minimum vẫn trả `None` cho tập kết quả rỗng/bị lọc.

## D011 — So sánh OAEP bằng cùng khóa, cùng Eve và evaluator riêng

`run_defense_comparison` sinh đúng một bộ ba RSA-2048/e=3 trong RAM rồi dùng
cùng plaintext, người nhận và public moduli cho Textbook RSA và RSA-OAEP.
OAEP dùng API `cryptography` với SHA-256, MGF1(SHA-256), label=None; không
tự viết encoding. Mỗi observation có scheme rõ ràng. Cả hai mode đều gọi
`attack_observations` với dữ liệu công khai. Bộ đánh giá Defense Lab so sánh
ứng viên với M riêng; không gọi evaluator Textbook RSA để suy luận OAEP từ
`M³ < N`. Kết quả chỉ giữ public numbers, ciphertext, trạng thái và preview;
private keys chỉ sống trong phạm vi điều phối và giải mã.

## D012 — Ghi nhận ngẫu nhiên hóa như một quan sát thực nghiệm

Lặp mã hóa trên cùng public key và plaintext, kiểm tra các ciphertext OAEP
quan sát được khác nhau và vẫn giải mã đúng; Textbook RSA lặp lại đúng cùng
ciphertext. Không seed CSPRNG, không dùng snapshot ciphertext, không coi vài
lần thử là chứng minh bảo mật. TASK 05 dùng e=65537 cho Secure Sharing và
không tái sử dụng phép Textbook RSA ở đây.

## D013 — Hybrid encryption tách khỏi các lab Textbook RSA

`hybrid_sharing.py` không import hoặc gọi `math_core` / `attack_lab`. Dùng
AESGCM của `cryptography` mã hóa file đúng một lần và RSA-OAEP SHA-256 bọc
khóa AES cho từng public key RSA-2048/e=65537. Tạo khóa và nonce mới từng lần
mã hóa. Demo keypair nằm riêng trong RAM; public recipient objects dùng lúc
mã hóa, private key chỉ dùng lúc giải mã. Fingerprint SHA-256(DER SPKI) ổn định,
không thay thế việc xác thực public key ngoài ứng dụng.

## D014 — JSON v1 canonical làm AAD và validation nghiêm ngặt

Header chứa version, thuật toán, tên file, kích thước, nonce và toàn bộ wrapped
key entries. JSON UTF-8 `sort_keys=True`, separators gọn, Base64 canonical;
header bytes là AAD. AESGCM tạo ciphertext + tag 16 byte trong một lần gọi.
Import giới hạn 8 MiB, từ chối duplicate JSON keys, trường thừa/thiếu, version
hoặc thuật toán khác, nonce/Base64/độ dài sai, ID/fingerprint trùng. File demo
giới hạn 5 MiB, filename chỉ là basename hiển thị. `PackageValidationError`
tách lỗi format khỏi `DecryptionFailed` khi recipient/OAEP/GCM không xác thực.
Không pickle, không thêm sender signature, replay protection hay persistence
trong TASK 05; xem `SECURE_SHARING_DESIGN.md`.
