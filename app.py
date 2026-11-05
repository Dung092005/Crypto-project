"""BroadcastGuard Streamlit router for the two educational laboratories."""

import streamlit as st

st.set_page_config(
    page_title="BroadcastGuard · Cryptography Laboratory",
    page_icon=":material/security:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Shared, static styling. User text is rendered only by native Streamlit widgets.
st.html("""
<style>
  .block-container { max-width: 1220px; padding-top: 2rem; }
  h1 { letter-spacing: -0.035em; }
  h2 { margin-top: 1.8rem; }
  [data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; }
</style>
""")

page = st.navigation(
    [
        st.Page("app_pages/attack_lab.py", title="Attack Lab", icon=":material/bug_report:", default=True),
        st.Page("app_pages/defense_lab.py", title="Defense Lab", icon=":material/shield:"),
    ],
    position="top",
)
page.run()
