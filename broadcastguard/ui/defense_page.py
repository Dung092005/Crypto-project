"""Interactive Defense Lab. Cryptographic work stays in defense_lab."""

import streamlit as st

from broadcastguard.defense_lab import (
    DefenseAttackResult,
    DefenseComparison,
    OAEP_MAX_MESSAGE_BYTES,
    run_defense_comparison,
)
from broadcastguard.ui.attack_presenter import preview_integer, readable_message
from broadcastguard.ui.defense_presenter import (
    DEFENSE_PRESETS,
    DEFENSE_STATUS_LABELS,
    comparison_rows,
    defense_message_bytes,
    recipient_comparison_rows,
)


def _scheme_panel(result: DefenseAttackResult, *, legitimate: bool | None) -> None:
    """Show real observed status, including unexpected outcomes."""
    is_textbook = result.scheme == "textbook"
    st.subheader("Textbook RSA" if is_textbook else "RSA-OAEP SHA-256")
    st.caption("c = M³ mod n · deterministic" if is_textbook else
               "OAEP randomized encoding → RSA · SHA-256 / MGF1-SHA256")
    if result.status == "recovered":
        st.error("Eve recovered the original plaintext", icon=":material/warning:")
    elif result.status == "wrong_exact_root":
        st.warning("Exact cube root, wrong plaintext", icon=":material/info:")
    elif result.status == "no_exact_root":
        st.success("No exact cube root in this attempt", icon=":material/shield:")
    else:
        st.warning("Invalid public observations", icon=":material/info:")
    st.metric("Recovered original", "Yes" if result.recovered_original else "No")
    st.write(f"Eve candidate: `{preview_integer(result.outcome.candidate)}`")
    st.write(f"Exact integer cube root: **{result.outcome.exact}**")
    if legitimate is not None:
        st.write(f"Legitimate OAEP decryption: **{'all succeeded' if legitimate else 'failure observed'}**")
    if is_textbook:
        st.caption(f"Experimenter: M³ < N = {result.textbook_bound_holds}.")
    else:
        st.caption("Experimenter: M³ < N của Textbook RSA không giải thích OAEP.")


def render_defense_page() -> None:
    """Render one session's comparison; only the Run button creates RSA keys."""
    st.session_state.setdefault("defense_comparison", None)
    st.session_state.setdefault("defense_run_number", 0)

    st.caption("BROADCASTGUARD  /  DEFENSE LAB  /  02")
    st.title("How can we defend against RSA Broadcast Attack?")
    st.write("Same message. Same RSA keys. Same attacker. Different encryption scheme.")
    st.caption("Thí nghiệm có kiểm soát: chỉ thay cách mã hóa, giữ nguyên thông điệp, ba khóa RSA và phép thử của Eve.")
    st.warning("Textbook RSA intentionally insecure · chỉ dùng để học, không bảo vệ dữ liệu thật.")
    with st.container(horizontal=True):
        st.badge("RSA-2048", color="blue")
        st.badge("e = 3", color="blue")
        st.badge("Alice · Bob · Charlie", color="green")
        st.badge("Textbook vs OAEP", color="red")
        st.badge("SHA-256 / MGF1-SHA256", color="blue")

    st.header("01 / Controlled experiment")
    st.write("Chọn cùng một plaintext bytes cho cả hai mode. Mỗi lần bấm Run sinh đúng một bộ ba khóa dùng chung.")
    mode = st.radio("Defense message source", ("Preset samples", "Custom message"),
                    horizontal=True, key="defense_message_mode")
    if mode == "Preset samples":
        preset = st.selectbox("Defense sample size", tuple(DEFENSE_PRESETS), key="defense_sample_size")
        custom_text = ""
    else:
        preset = ""
        custom_text = st.text_area("Defense plaintext (UTF-8)", key="defense_custom_plaintext",
                                   placeholder="Nhập tối đa 190 byte UTF-8", height=100)
    try:
        draft = defense_message_bytes(mode, preset, custom_text)
        draft_error = None
        st.caption(f"Bản nháp: {len(draft)} byte UTF-8 · giới hạn {OAEP_MAX_MESSAGE_BYTES} byte.")
    except (ValueError, UnicodeEncodeError) as error:
        draft, draft_error = None, str(error)
        st.error(draft_error)
    st.caption("OAEP-SHA256 với RSA-2048 giới hạn mLen ≤ 256 − 2×32 − 2 = 190 byte; dữ liệu vượt giới hạn bị từ chối.")

    if st.button("Run Defense Comparison", type="primary", icon=":material/play_arrow:"):
        if draft is None:
            st.error(draft_error or "Thông điệp không hợp lệ.")
        else:
            st.session_state["defense_comparison"] = None
            try:
                with st.spinner("Đang tạo ba khóa RSA-2048, mã hóa hai mode và kiểm chứng giải mã..."):
                    new_comparison = run_defense_comparison(draft)
            except Exception:
                st.error("Không chạy được thí nghiệm. Vui lòng thử lại.")
            else:
                st.session_state["defense_comparison"] = new_comparison
                st.session_state["defense_run_number"] += 1
                st.success("Thí nghiệm hoàn tất; các kết quả bên dưới thuộc cùng một bộ khóa.")

    comparison: DefenseComparison | None = st.session_state["defense_comparison"]
    if comparison is None:
        st.info("Chọn thông điệp và bấm Run Defense Comparison để bắt đầu.")
        return
    kind, active_text = readable_message(comparison.scenario.plaintext)
    st.caption(f"Thí nghiệm đang xem: #{st.session_state['defense_run_number']} · "
               f"{len(comparison.scenario.plaintext)} byte · {kind}: {active_text}")
    if draft != comparison.scenario.plaintext:
        st.info("Bản nháp đã đổi; kết quả bên dưới vẫn thuộc thí nghiệm đã chạy. Bấm Run để cập nhật.")

    st.header("02 / Before vs after")
    st.write("Cùng plaintext, cùng ba public keys và cùng CRT + căn bậc ba; chỉ scheme mã hóa thay đổi.")
    left, right = st.columns(2, gap="large")
    with left, st.container(border=True):
        _scheme_panel(comparison.textbook, legitimate=None)
    with right, st.container(border=True):
        _scheme_panel(comparison.oaep, legitimate=all(
            item.recovered_original_bytes for item in comparison.decryptions
        ))
    st.dataframe(comparison_rows(comparison), hide_index=True)
    st.caption("Các trạng thái trên là kết quả quan sát của run hiện tại; exact root không tự chứng minh ứng viên đúng.")

    st.header("03 / Same keys, fair comparison")
    st.write("Both schemes use exactly the same RSA public keys. Only the encryption scheme changes.")
    st.dataframe(recipient_comparison_rows(comparison), hide_index=True)
    with st.expander("Xem public moduli và ciphertext đầy đủ"):
        st.caption("OAEP ciphertext được đưa vào cùng phép thử toán học; nó không phải Textbook RSA ciphertext.")
        for textbook, oaep in zip(comparison.scenario.textbook_observations,
                                  comparison.scenario.oaep_observations):
            st.write(f"**{textbook.recipient_id}** · n dùng chung: "
                     f"{textbook.public.n == oaep.public.n}")
            st.code(f"n = {textbook.public.n}\nTextbook c = {textbook.public.c}\nOAEP c = {oaep.public.c}",
                    language=None)

    st.header("04 / Eve tries the same attack")
    st.caption("EVE'S COMPUTATION · chỉ có public keys và ba ciphertext của từng mode")
    st.markdown("1. Thu ba ciphertext và public moduli.  2. Tính $N = n_A n_B n_C$.  "
                "3. Dùng CRT dựng $X$.  4. Thử căn bậc ba nguyên chính xác.")
    st.caption("EXPERIMENTER'S VERIFICATION · so sánh ứng viên của Eve với plaintext thật sau khi Eve tính xong")
    for result in (comparison.textbook, comparison.oaep):
        st.write(f"**{'Textbook RSA' if result.scheme == 'textbook' else 'RSA-OAEP'}:** "
                 f"{DEFENSE_STATUS_LABELS[result.status]} · "
                 f"{result.outcome.used_count} ciphertext · "
                 f"N dài {result.outcome.product.bit_length() if result.outcome.product else 0} bit")
    with st.expander("Xem CRT và căn nguyên đầy đủ"):
        for result in (comparison.textbook, comparison.oaep):
            st.write(f"**{result.scheme}**")
            st.code(f"N = {result.outcome.product}\nX = {result.outcome.combined}\nr = {result.outcome.candidate}",
                    language=None)
    st.caption("Phép thử CRT-and-root không khôi phục được M trong một run không chứng minh hệ mã an toàn tuyệt đối.")

    st.header("05 / OAEP randomization experiment")
    randomization = comparison.randomization
    st.write(f"Cùng plaintext và cùng public key {randomization.recipient_id}; "
             f"{randomization.trial_count} lần mã hóa OAEP riêng biệt.")
    with st.container(horizontal=True):
        st.metric("Textbook ciphertexts identical", "Yes" if randomization.textbook_ciphertexts_identical else "No")
        st.metric("OAEP ciphertexts distinct", "Yes" if randomization.oaep_ciphertexts_distinct else "No")
        st.metric("OAEP samples decrypt", "All" if randomization.oaep_all_decrypt else "Not all")
    st.caption("Khác biệt ciphertext minh họa randomized encoding, không phải chứng minh bảo mật đầy đủ.")

    st.header("06 / Legitimate recipient verification")
    with st.container(horizontal=True):
        for item in comparison.decryptions:
            with st.container(border=True, width="stretch"):
                st.subheader(item.recipient_id)
                if item.recovered_original_bytes:
                    st.success("Decrypted correctly")
                else:
                    st.error("Decryption failed")
    st.caption("Private keys chỉ tồn tại trong lúc orchestration giải mã; kết quả UI không chứa khóa bí mật.")

    st.header("07 / Educational takeaways")
    st.markdown(
        "1. Textbook RSA dùng trực tiếp $M^3 \\bmod n$ và mã hóa lặp lại có cùng kết quả.\n"
        "2. OAEP tạo biểu diễn ngẫu nhiên trước phép RSA, nên ba ciphertext không còn cùng raw $M^3$.\n"
        "3. Eve dùng lại CRT và căn bậc ba; kết quả được kiểm tra riêng với plaintext gốc.\n"
        "4. Người nhận hợp lệ vẫn giải mã OAEP bằng private key của mình.\n"
        "5. RSA-2048/OAEP-SHA256 chỉ nhận tối đa 190 byte; file lớn cần hybrid encryption "
        "ở TASK 08."
    )
    st.caption("BroadcastGuard · Defense Lab · TASK 07. Không suy ra bảo mật tuyệt đối từ một phép thử thất bại.")
