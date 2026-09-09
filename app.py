
import streamlit as st
from main import run_agent


st.set_page_config(
    page_title="CodePilot",
    page_icon="🤖",
    layout="wide",
)


# -----------------------------
# Page styling
# -----------------------------

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
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Session state
# -----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------
# Header
# -----------------------------

st.markdown(
    '<div class="main-title">🤖 CodePilot</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Your intelligent AI coding assistant</div>',
    unsafe_allow_html=True,
)


# -----------------------------
# Sidebar
# -----------------------------

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


# -----------------------------
# Conversation history
# -----------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -----------------------------
# Chat input
# -----------------------------

user_prompt = st.chat_input(
    "Ask CodePilot to inspect, fix, or modify your project..."
)


if user_prompt:

    # Display user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_prompt)


    # Run the AI agent
    with st.chat_message("assistant"):

        with st.spinner("🤖 Agent is working..."):

            try:
                response = run_agent(
                    user_prompt,
                    verbose=True,
                )

                if not response:
                    response = "The agent returned no response."

                st.markdown(response)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )

            except Exception as e:

                error_message = f"❌ Agent error: {e}"

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )

