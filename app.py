import streamlit as st
import subprocess
import sys

st.set_page_config(
    page_title="CodePilot",
    page_icon="🤖",
    layout="wide",
)

# ---------- Styling ----------

st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        color: #888;
        font-size: 18px;
        margin-bottom: 25px;
    }

    .status {
        padding: 10px 15px;
        border-radius: 10px;
        background: rgba(0, 128, 0, 0.08);
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Session State ----------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- Header ----------

st.markdown(
    '<div class="main-title">🤖 CodePilot</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Your intelligent AI coding assistant</div>',
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------

with st.sidebar:
    st.header("⚙️ Agent")

    st.success("Agent ready")

    st.markdown("### Available tools")

    st.markdown(
        """
        🔍 **get_files_info**  
        Inspect files and directories.

        📖 **get_file_content**  
        Read source code.

        ▶️ **run_python_file**  
        Execute Python files.

        ✏️ **write_file**  
        Create or modify files.
        """
    )

    st.markdown("---")

    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.rerun()

# ---------- Conversation ----------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------- Chat Input ----------

user_prompt = st.chat_input(
    "Ask CodePilot to inspect, fix, or modify your project..."
)

if user_prompt:
    # Show user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Run agent
    with st.chat_message("assistant"):
        with st.spinner("Agent is working..."):
            try:
                result = subprocess.run(
                    [sys.executable, "main.py", user_prompt],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                output = result.stdout.strip()

                if result.stderr:
                    output += "\n\n```text\n" + result.stderr.strip() + "\n```"

                if not output:
                    output = "The agent returned no output."

                st.markdown(output)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": output,
                    }
                )

            except subprocess.TimeoutExpired:
                error_message = "⏱️ The agent took too long to respond."
                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )

            except Exception as e:
                error_message = f"❌ Something went wrong: {e}"
                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )
