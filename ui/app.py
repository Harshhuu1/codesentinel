import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="CodeSentinel",
    layout="wide",
    initial_sidebar_state="expanded"
)

# minimal clean styling
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
    }
    .issue-count {
        font-size: 28px;
        font-weight: 600;
        color: #e05252;
    }
    .meta-tag {
        background: #f0f0f0;
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 12px;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# sidebar
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
    st.markdown("""supervisor
     |
  security
     |
performance
     |
   style
     |
  critic""")
    
    st.markdown("---")
    st.markdown("**API Status**")
    try:
        r = requests.get(f"{API_URL}/health", timeout=2)
        if r.status_code == 200:
            st.success("API running")
        else:
            st.error("API unreachable")
    except:
        st.error("API unreachable")

# main
st.markdown("## Code Review")
st.markdown("Paste your code below and run the review pipeline.")

code_input = st.text_area(
    "Code",
    height=320,
    placeholder="Paste code here...",
    label_visibility="collapsed"
)

col1, col2 = st.columns([1, 9])
with col1:
    review_btn = st.button("Run Review", type="primary")

st.markdown("---")

if review_btn:
    if not code_input.strip():
        st.warning("No code provided.")
    else:
        with st.spinner("Running pipeline..."):
            try:
                response = requests.post(
                    f"{API_URL}/review",
                    json={"code": code_input, "language": language},
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()

                    # summary row
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Total Issues", data["total_issues"])
                    with c2:
                        st.metric("Language", data["language"])
                    with c3:
                        st.metric("Agents Run", len(data["agent_path"]))

                    # agent path
                    st.markdown("**Execution path**")
                    st.markdown(
                        f'<div class="agent-path">{" → ".join(data["agent_path"])}</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown("")

                    # results tabs
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

                else:
                    st.error(f"API returned {response.status_code}: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API on port 8000.")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")