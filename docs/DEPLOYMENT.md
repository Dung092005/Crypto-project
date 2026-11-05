# Streamlit Community Cloud readiness · TASK 06

Tài liệu chuẩn bị triển khai, **chưa triển khai**. App chạy local bằng
`app.py`; runtime không dùng đường dẫn Windows, file hệ thống, credential
hoặc database. Dữ liệu kịch bản nằm trong `st.session_state` theo phiên.

## Chạy local trên Windows

```powershell
cd C:\path\to\Crypto-project
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Mở `http://localhost:8501`, chọn preset, Generate, chọn subset, Run Attack và
Compare message lengths. `app.py` là entrypoint từ repository root. Không cần
`secrets.toml` cho TASK 06; file này đã được ignore nếu sau này có dùng.

## Triển khai Community Cloud sau khi reviewer đồng ý

1. Xác minh commit đã review trên GitHub. Chọn nhánh
   `feat/step-06-attack-ui` hoặc **reviewed integration branch** chứa TASK 06.
   `main` có thể đang ở TASK 02 và **không có `app.py`**; không chọn `main` cũ.
2. Tại [share.streamlit.io](https://share.streamlit.io), chọn workspace của
   owner `Dung092005` → **Create app** → **Yup, I have an app**. Nhập repository
   `Dung092005/Crypto-project`, branch đã review ở bước 1, main file path
   `app.py` (root). Chọn URL tùy ý.
3. Trong Advanced settings chọn **Python 3.12** để khớp môi trường đã kiểm
   chứng. Không cần secrets cho Attack Lab. Bấm Deploy **chỉ khi được giao
   triển khai**.
4. Root `requirements.txt` được Cloud đọc; nó cài package local (`-e .`) và
   pin `streamlit==1.60.0`, `cryptography==48.0.1`. `pyproject.toml` là cấu
   hình package/dev. `.streamlit/config.toml` đặt theme dark; không cần
   `packages.txt` hay hệ thống build frontend.

Community Cloud đọc dependency file và config từ repo, cho phép chọn branch,
entrypoint và Python version khi tạo app. Xem [file organization](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization),
[dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)
và [deploy](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

## Checklist sau triển khai thật

- Xem Cloud build logs: dependencies cài xong, `app.py` chạy không exception.
- Mở URL public; Generate 1-byte preset, Eve chọn Alice, Run Attack thấy
  `Recovered`. Chọn 180-byte preset, 1–2 bản mã không recovered, 3 recovered.
- Bảng đủ bảy tập con; sweep 1/96/180 cho minimum 1/2/3; Generate mới reset
  attack cũ. Kiểm tra hai browser sessions không thấy kịch bản của nhau.
- Kiểm tra cả desktop/mobile, không có số nguyên 2048-bit tràn bảng. Xem
  [Cloud logs](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app)
  nếu app không lên. Chỉ công bố URL sau khi kiểm tra này hoàn tất.

## Rollback

Không force-push hoặc chọn `feat/step-05-hybrid-sharing` làm bản UI dự phòng:
nhánh đó chưa có `app.py`. Với bản đầu tiên lỗi, ngừng chia sẻ URL, sửa trên
feature branch và review lại trước deploy. Với các bản sau, giữ một reviewed
integration branch/commit chạy tốt rồi revert thay đổi lỗi hoặc chọn lại nhánh
ổn định trong cấu hình Cloud; xác minh lại URL và logs. Nếu cần đổi Python
version sau deploy, Community Cloud yêu cầu xóa và deploy lại theo
[hướng dẫn chính thức](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/upgrade-python).
