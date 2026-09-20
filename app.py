"""
app.py
------
Streamlit front-end for the AI Research Agent.

This app is built to run on Streamlit Cloud, where the Groq API key
is provided via Streamlit Secrets (Settings -> Secrets), not a local
.env file.
"""

import streamlit as st

from research_agent import run_research


# ---------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔎",
    layout="centered",
)

st.title("🔎 AI Research Agent")
st.caption("Powered by CrewAI + Groq (openai/gpt-oss-120b) + DuckDuckGo Search")


# ---------------------------------------------------------------------
# GET THE GROQ API KEY (from Streamlit secrets only)
# ---------------------------------------------------------------------
api_key = st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.error(
        "No Groq API key found in Streamlit secrets. "
        "Go to your app's Settings -> Secrets and add:\n\n"
        '`GROQ_API_KEY = "your_key_here"`'
    )
    st.stop()


# ---------------------------------------------------------------------
# MAIN UI
# ---------------------------------------------------------------------
topic = st.text_input(
    "What topic do you want a research report on?",
    placeholder="e.g. The impact of AI on small businesses",
)

generate = st.button("Generate Report", type="primary", use_container_width=True)

if generate:
    if not topic.strip():
        st.error("Please enter a research topic.")
    else:
        with st.spinner("Researching your topic... this can take a minute ⏳"):
            try:
                report = run_research(topic, api_key=api_key)
                st.session_state["last_report"] = report
                st.session_state["last_topic"] = topic
            except Exception as e:
                st.error(f"Something went wrong: {e}")

# Show the last generated report (persists across reruns of the app)
if "last_report" in st.session_state:
    st.markdown("---")
    st.subheader(f"Report: {st.session_state['last_topic']}")
    st.markdown(st.session_state["last_report"])

    st.download_button(
        label="⬇️ Download report as Markdown",
        data=st.session_state["last_report"],
        file_name=f"{st.session_state['last_topic'].strip().replace(' ', '_')}_report.md",
        mime="text/markdown",
        use_container_width=True,
    )
