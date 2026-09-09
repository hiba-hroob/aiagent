import streamlit as st
import subprocess
import sys

st.set_page_config(
    page_title="AI Coding Agent",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 AI Coding Agent")
st.caption("Your intelligent coding assistant")

st.markdown("---")

user_prompt = st.text_area(
    "What do you want me to do?",
    placeholder="Example: Fix the bug in the calculator...",
    height=150,
)

if st.button("🚀 Run Agent", type="primary"):
    if not user_prompt.strip():
        st.warning("Please enter a request first.")
    else:
        with st.spinner("Agent is working..."):
            try:
                result = subprocess.run(
                    [sys.executable, "main.py", user_prompt],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                if result.stdout:
                    st.subheader("Agent Output")
                    st.code(result.stdout)

                if result.stderr:
                    st.subheader("Errors")
                    st.code(result.stderr)

            except subprocess.TimeoutExpired:
                st.error("The agent took too long to respond.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")
