# Attack Lab UI design · TASK 06

Entrypoint `app.py` trình bày một câu chuyện năm phần theo thứ tự: người gửi
chọn plaintext → ba người nhận có public key/ciphertext → Eve chọn bản mã →
CRT và căn nguyên → phân tích bảy tập con. `attack_presenter.py` chỉ chuẩn hóa
preview, trạng thái và các hàng bảng; không làm phép RSA thay backend.

## Tương tác và trạng thái

- Preset 1/96/180 byte hoặc custom UTF-8 tối đa 190 byte; hiển thị số **byte**.
  Bản nháp đổi không thay kịch bản đang xem cho đến khi bấm Generate.
- Generate gọi `build_scenario` một lần rồi `analyze_scenario`; lưu kết quả
  trong `st.session_state` của phiên đó. Generate mới xóa attack và sweep cũ.
- Chọn bất kỳ subset Alice/Bob/Charlie; Run Attack chỉ truyền các
  `PublicObservation` vào `attack_observations`. `evaluate_experiment` chạy
  **sau** khi Eve đã tính ứng viên, để kiểm chứng với plaintext.
- Bảng bảy subset lấy từ `analyze_scenario`. Nút Explore message length dùng
  `sweep_message_lengths` trên cùng ba public moduli, tính một lần cho mỗi
  kịch bản. Không dùng cache toàn cục cho plaintext/scenario/private key.
- Lỗi đầu vào và lỗi backend được hiển thị gọn, không in traceback cho người
  xem. Test `AppTest` kiểm chứng trạng thái thật và các lần rerun.

## Thiết kế hình ảnh

Theme trong `.streamlit/config.toml`: nền navy/charcoal, chữ sáng, teal cho
dữ liệu người nhận và trạng thái hợp lệ, red/pink cho Eve hoặc tấn công,
amber cho căn chính xác nhưng sai plaintext. Cards dùng container có viền;
các thông số và bảng dùng widget native. CSS chỉ cố định khoảng cách/typography,
không chứa plaintext, không tải font/JS từ bên ngoài. Desktop ưu tiên ba cards
trong horizontal container co giãn; trên màn nhỏ chúng có thể tự xuống hàng.
Các số nguyên dài chỉ
nằm trong expander; bảng tổng hợp chỉ có bit length và trạng thái.

`recovered`, `wrong_exact_root`, `no_exact_root`, `invalid_input` luôn tách
nhãn. Eve's computation chỉ có số công khai; điều kiện `M³ < N` được ghi rõ
là xác minh của người đánh giá. Một lần thử không lấy được M không chứng minh
Textbook RSA an toàn. Thông điệp binary dùng hex preview thay vì văn bản lỗi.

TASK 06 không có Defense UI, Secure Sharing UI hoặc benchmark. Xem
`DEPLOYMENT.md` cho hướng dẫn Cloud sau khi nhánh được reviewer chấp thuận.
