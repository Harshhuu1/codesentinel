import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="CodeSentinel",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .stTextArea textarea { font-family: 'Courier New', monospace; font-size: 13px; }
    .stTabs [data-baseweb="tab"] { font-size: 13px; }
    .agent-path {
        background: #1e1e1e;
        color: #d4d4d4;
        padding: 8px 12px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 13px;
        margin-bottom: 1rem;
    }
    .guard-ok { color: #3c9e3c; font-family: monospace; font-size: 13px; }
    .guard-warn { color: #e05252; font-family: monospace; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### CodeSentinel")
    st.markdown("Multi-agent code review pipeline")
    st.markdown("---")

    language = st.selectbox(
        "Language",
        ["python", "javascript", "java", "cpp", "go", "rust", "other"],
        index=0
    )

    st.markdown("---")
    st.markdown("**Pipeline**")
    st.code("""supervisor
    |
 security
    |
performance
    |
  style
    |
 critic""", language=None)

    st.markdown("---")
    st.markdown("**API**")
    try:
        r = requests.get(f"{API_URL}/health", timeout=2)
        if r.status_code == 200:
            st.success("connected")
        else:
            st.error("unreachable")
    except:
        st.error("unreachable")

    st.markdown(f"<small style='color:gray'>{API_URL}</small>", unsafe_allow_html=True)

st.markdown("## Code Review")
st.markdown("Paste code and run the 5-agent review pipeline.")

code_input = st.text_area(
    "code_input",
    height=320,
    placeholder="Paste code here...",
    label_visibility="collapsed"
)

run_btn = st.button("Run Review", type="primary")
st.markdown("---")

if run_btn:
    if not code_input.strip():
        st.warning("No code provided.")
    else:
        with st.spinner("Running pipeline..."):
            try:
                response = requests.post(
                    f"{API_URL}/review",
                    json={"code": code_input, "language": language},
                    timeout=120
                )

                if response.status_code == 200:
                    data = response.json()

                    # metrics row
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Issues Found", data["total_issues"])
                    with c2:
                        st.metric("Language", data["language"])
                    with c3:
                        st.metric("Agents Run", len(data["agent_path"]))

                    st.markdown("")

                    # guardrail row
                    g1, g2 = st.columns(2)
                    with g1:
                        pii = data.get("pii_detected", False)
                        css = "guard-warn" if pii else "guard-ok"
                        label = "[WARN] PII detected" if pii else "[OK] No PII detected"
                        st.markdown(f'<div class="{css}">{label}</div>', unsafe_allow_html=True)
                    with g2:
                        inj = data.get("injection_detected", False)
                        css = "guard-warn" if inj else "guard-ok"
                        label = "[WARN] Injection pattern detected" if inj else "[OK] No injection detected"
                        st.markdown(f'<div class="{css}">{label}</div>', unsafe_allow_html=True)

                    st.markdown("")

                    # execution path
                    st.markdown("**Execution path**")
                    st.markdown(
                        f'<div class="agent-path">{" → ".join(data["agent_path"])}</div>',
                        unsafe_allow_html=True
                    )

                    # agent outputs
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "Security", "Performance", "Style", "Critic Report"
                    ])

                    with tab1:
                        st.code(data["security_issues"], language=None)
                    with tab2:
                        st.code(data["performance_issues"], language=None)
                    with tab3:
                        st.code(data["style_issues"], language=None)
                    with tab4:
                        st.code(data["critic_output"], language=None)

                elif response.status_code == 400:
                    st.error(f"Blocked by guardrail: {response.json().get('detail', 'unknown reason')}")
                else:
                    st.error(f"API error {response.status_code}: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error(f"Cannot connect to API at {API_URL}")
            except requests.exceptions.Timeout:
                st.error("Request timed out. The pipeline may be overloaded.")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")