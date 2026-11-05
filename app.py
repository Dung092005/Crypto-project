"""BroadcastGuard Attack Lab — Streamlit Community Cloud entrypoint."""

import streamlit as st

from broadcastguard.attack_lab import (
    RECIPIENT_IDS,
    AttackScenario,
    attack_observations,
    build_scenario,
    evaluate_experiment,
)
from broadcastguard.conditions_analyzer import analyze_scenario, sweep_message_lengths
from broadcastguard.ui.attack_presenter import (
    PRESETS,
    STATUS_LABELS,
    message_bytes,
    preview_integer,
    readable_message,
    subset_rows,
    sweep_rows,
)


st.set_page_config(page_title="BroadcastGuard · Attack Lab", page_icon=":material/security:",
                   layout="wide", initial_sidebar_state="collapsed")

# Static CSS only. User-provided plaintext is rendered by native Streamlit widgets.
st.html("""
<style>
  .block-container { max-width: 1220px; padding-top: 2rem; }
  h1 { letter-spacing: -0.035em; }
  h2 { margin-top: 1.8rem; }
  [data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; }
</style>
""")


def clear_attack() -> None:
    st.session_state["attack_outcome"] = None
    st.session_state["attack_evaluation"] = None
    st.session_state["attack_ids"] = ()


for key, initial in (
    ("scenario", None), ("scenario_analysis", None), ("length_sweep", None),
    ("attack_outcome", None), ("attack_evaluation", None), ("attack_ids", ()),
    ("scenario_number", 0),
):
    st.session_state.setdefault(key, initial)


st.caption("BROADCASTGUARD  /  ATTACK LAB  /  01")
st.title("Can RSA be broken without a private key?")
st.write(
    "Explore how a low public exponent and repeated plaintext can expose textbook RSA encryption."
)
st.caption(
    "Mô phỏng giáo dục: cùng một thông điệp được gửi cho ba người nhận bằng Textbook RSA cố ý không an toàn."
)
st.warning("Educational demonstration · intentionally insecure textbook RSA. Không dùng để bảo vệ dữ liệu thật.")

with st.container(horizontal=True):
    st.badge("RSA-2048", color="blue")
    st.badge("e = 3", color="blue")
    st.badge("Alice · Bob · Charlie", color="green")
    st.badge("CRT + exact cube root", color="red")

st.header("01 / Sender simulator")
st.write("Người gửi chọn một thông điệp; ba khóa công khai khác nhau sẽ tạo ba ciphertext.")
mode = st.radio("Message source", ("Preset samples", "Custom message"), horizontal=True,
                key="message_mode")
if mode == "Preset samples":
    preset = st.selectbox("Sample size", tuple(PRESETS), key="sample_size")
    custom_text = ""
    st.caption("Mẫu B lặp lại giúp thấy điều kiện toán học thay đổi theo độ lớn M.")
else:
    preset = ""
    custom_text = st.text_area("Plaintext (UTF-8)", key="custom_plaintext",
                               placeholder="Nhập thông điệp của bạn (tối đa 190 byte UTF-8)", height=110)

try:
    draft = message_bytes(mode, preset, custom_text)
    draft_error = None
    st.caption(f"Độ dài thực tế: {len(draft)} byte UTF-8 · Giới hạn: 190 byte. Nội dung không bị cắt bớt.")
except (ValueError, UnicodeEncodeError) as error:
    draft = None
    draft_error = str(error)
    st.error(draft_error)

if st.button("Generate RSA Scenario", type="primary", icon=":material/key:"):
    if draft is None:
        st.error(draft_error or "Thông điệp không hợp lệ.")
    else:
        try:
            with st.spinner("Đang tạo ba khóa RSA-2048 và mã hóa thông điệp..."):
                new_scenario = build_scenario(draft)
                new_analysis = analyze_scenario(new_scenario)
        except Exception:
            st.error("Không tạo được kịch bản RSA. Vui lòng thử lại; kết quả cũ vẫn được giữ.")
        else:
            st.session_state["scenario"] = new_scenario
            st.session_state["scenario_analysis"] = new_analysis
            st.session_state["length_sweep"] = None
            st.session_state["scenario_number"] += 1
            st.session_state["intercepts"] = list(RECIPIENT_IDS)
            clear_attack()
            st.success("Đã tạo kịch bản mới. Khóa sẽ được giữ cho đến khi bạn bấm Generate lần nữa.")

scenario: AttackScenario | None = st.session_state["scenario"]
if scenario is not None:
    kind, active_preview = readable_message(scenario.plaintext)
    st.caption(
        f"Kịch bản đang xem: #{st.session_state['scenario_number']} · "
        f"{len(scenario.plaintext)} byte · {kind}: {active_preview}"
    )
    if draft is None or draft != scenario.plaintext:
        st.info("Bạn đã đổi bản nháp. Kết quả bên dưới vẫn thuộc kịch bản đang xem; bấm Generate để tạo kịch bản mới.")

st.header("02 / Alice, Bob and Charlie")
if scenario is None:
    st.info("Bấm Generate RSA Scenario để tạo ba ciphertext đầu tiên.")
else:
    with st.container(horizontal=True):
        for observation in scenario.observations:
            with st.container(border=True, width="stretch"):
                st.badge("Ciphertext ready", color="green")
                st.subheader(observation.recipient_id)
                st.caption(f"Public key · n dài {observation.modulus_bits} bit · e = {observation.e}")
                st.code(f"n  {preview_integer(observation.n)}\nc  {observation.ciphertext_preview}", language=None)
                with st.expander("Xem số công khai đầy đủ"):
                    st.caption("Đây là public modulus và ciphertext, không phải khóa bí mật.")
                    st.code(f"n = {observation.n}\n\nc = {observation.c}", language=None)

st.header("03 / Eve attack simulator")
st.badge("Eve · public observations only", color="red")
st.write("Eve chỉ chọn những cặp public key và ciphertext đã thu được. Chọn bất kỳ 1–3 người nhận.")
if scenario is None:
    st.button("Run Broadcast Attack", disabled=True, icon=":material/play_arrow:")
    st.caption("Cần tạo kịch bản trước khi Eve tính toán.")
else:
    selected_ids = st.multiselect("Ciphertexts Eve intercepted", RECIPIENT_IDS,
                                  key="intercepts", on_change=clear_attack)
    if st.button("Run Broadcast Attack", icon=":material/play_arrow:"):
        if not selected_ids:
            st.warning("Hãy chọn ít nhất một ciphertext để Eve thử tấn công.")
        else:
            selected_public = tuple(
                observation for observation in scenario.observations
                if observation.recipient_id in selected_ids
            )
            try:
                with st.spinner("Eve đang kết hợp CRT và lấy căn bậc ba nguyên..."):
                    # The attacker receives ONLY public observations.
                    outcome = attack_observations(selected_public)
                    # Ground truth is supplied only after Eve has computed a candidate.
                    evaluation = evaluate_experiment(scenario, selected_public, outcome)
            except Exception:
                clear_attack()
                st.error("Không tính được kết quả tấn công. Vui lòng kiểm tra lựa chọn và thử lại.")
            else:
                st.session_state["attack_outcome"] = outcome
                st.session_state["attack_evaluation"] = evaluation
                st.session_state["attack_ids"] = tuple(item.recipient_id for item in selected_public)

    outcome = st.session_state["attack_outcome"]
    evaluation = st.session_state["attack_evaluation"]
    if outcome is not None and evaluation is not None:
        label, explanation = STATUS_LABELS[evaluation.status]
        if evaluation.status == "recovered":
            st.success(f"{label} · {explanation}", icon=":material/check_circle:")
        elif evaluation.status == "wrong_exact_root":
            st.warning(f"{label} · {explanation}", icon=":material/warning:")
        else:
            st.error(f"{label} · {explanation}", icon=":material/info:")
        st.caption(
            f"Eve thu {outcome.used_count} ciphertext · exact root = {outcome.exact} · "
            f"recovered original = {evaluation.matches_original}"
        )
        if evaluation.status == "invalid_input" and outcome.reason:
            st.caption(f"Dữ liệu công khai không hợp lệ: {outcome.reason}")
        if evaluation.status != "recovered":
            st.caption("Một phép CRT và căn bậc ba thất bại không chứng minh hệ mã an toàn.")

st.header("04 / Mathematical walkthrough")
if scenario is None or st.session_state["attack_outcome"] is None:
    st.info("Chọn ciphertext và bấm Run Broadcast Attack để xem năm bước toán học.")
else:
    outcome = st.session_state["attack_outcome"]
    evaluation = st.session_state["attack_evaluation"]
    st.caption("EVE'S COMPUTATION · chỉ dựa trên dữ liệu công khai")
    st.markdown("**Step 1 — Public observations.** Eve thấy các cặp $(n_i, e, c_i)$ đã chọn.")
    st.write("Đã chọn:", " + ".join(st.session_state["attack_ids"]))
    st.markdown("**Step 2 — Modulus product.**")
    st.latex(r"N = \prod_{i \in S} n_i")
    st.write(f"N dài {outcome.product.bit_length() if outcome.product is not None else 0} bit · {preview_integer(outcome.product)}")
    st.markdown("**Step 3 — Chinese Remainder Theorem.**")
    st.latex(r"X \equiv c_i \pmod{n_i}\quad (i \in S),\qquad 0 \leq X < N")
    st.write("CRT kết hợp X:", preview_integer(outcome.combined))
    st.markdown("**Step 4 — Exact integer cube root.**")
    st.latex(r"r = \lfloor \sqrt[3]{X} \rfloor,\qquad exact \iff r^3 = X")
    st.write(f"Ứng viên r: {preview_integer(outcome.candidate)} · exact = {outcome.exact}")
    st.caption("EXPERIMENTER'S VERIFICATION · chỉ bộ đánh giá mới biết plaintext gốc")
    st.markdown("**Step 5 — Compare with the original.**")
    st.write(f"Ứng viên khớp plaintext gốc: {evaluation.matches_original}")
    st.write(f"Điều kiện Textbook RSA $M^3 < N$: {evaluation.bound_holds}")
    if evaluation.candidate_bytes is not None:
        kind, candidate_text = readable_message(evaluation.candidate_bytes)
        st.caption(f"Ứng viên dưới dạng {kind} (dùng độ dài bytes gốc):")
        st.code(candidate_text, language=None)
    with st.expander("Xem các số nguyên đầy đủ"):
        st.caption("Dữ liệu toán học công khai của Eve; có thể rất dài.")
        st.code(f"N = {outcome.product}\n\nX = {outcome.combined}\n\nr = {outcome.candidate}", language=None)
    st.caption("Thông điệp rất ngắn có thể thỏa $M^3 < n_i$ với chỉ một ciphertext; đó là hệ quả của Textbook RSA e=3.")

st.header("05 / Attack conditions analyzer")
if scenario is None:
    st.info("Sau khi tạo kịch bản, bảng sẽ phân tích đủ bảy tập con Alice/Bob/Charlie.")
else:
    analysis = st.session_state["scenario_analysis"]
    st.write("Cùng một thông điệp, bảy tập ciphertext Eve có thể thu được:")
    st.dataframe(subset_rows(analysis), hide_index=True)
    minimum = analysis.minimum_successful_count
    st.caption(f"Số ciphertext ít nhất để khôi phục trong kịch bản này: {minimum if minimum is not None else 'không có tập thành công'}.")
    with st.container(horizontal=True):
        st.badge("Recovered", color="green")
        st.badge("Wrong exact root", color="orange")
        st.badge("No exact root", color="red")
    st.caption("Cột M³ < N là kiểm tra của người đánh giá, không phải dữ liệu Eve biết trước.")
    with st.expander("Xem giải thích từng tập con"):
        for row in analysis.subsets:
            st.write(f"**{' + '.join(row.recipient_ids)}:** {row.explanation}")

    st.subheader("Explore message length")
    st.write("Giữ nguyên ba public moduli; chỉ thay giá trị thông điệp bằng B × 1, 96 hoặc 180 byte.")
    if st.button("Compare 1 / 96 / 180 bytes", icon=":material/table_chart:"):
        if st.session_state["length_sweep"] is None:
            try:
                with st.spinner("Đang phân tích 21 phép thử trên cùng ba modulus..."):
                    st.session_state["length_sweep"] = sweep_message_lengths(scenario)
            except Exception:
                st.error("Không hoàn tất được phép so sánh độ dài. Vui lòng thử lại.")
    sweep = st.session_state["length_sweep"]
    if sweep is not None:
        st.dataframe(sweep_rows(sweep), hide_index=True)
        st.caption("Các ô là kết quả tính thật, không hardcode. Độ dài byte chỉ là gợi ý; giá trị nguyên M mới quyết định bất đẳng thức.")

st.caption("BroadcastGuard · Attack Lab · TASK 06. Defense Lab và Secure Sharing UI sẽ được xây ở task riêng.")
