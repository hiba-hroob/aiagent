import streamlit as st

from main import run_agent


st.set_page_config(
    page_title="CodePilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .block-container {
        max-width: 1450px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* Header */

    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 4px 22px 4px;
        border-bottom: 1px solid rgba(128,128,128,.18);
        margin-bottom: 25px;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-icon {
        width: 44px;
        height: 44px;
        border-radius: 13px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 23px;
        background: linear-gradient(
            135deg,
            #6d5dfc,
            #9b6cff
        );
        color: white;
        box-shadow: 0 8px 25px rgba(109,93,252,.25);
    }

    .brand-name {
        font-size: 25px;
        font-weight: 800;
        line-height: 1;
    }

    .brand-subtitle {
        font-size: 12px;
        color: #888;
        margin-top: 5px;
    }

    .online {
        padding: 8px 14px;
        border-radius: 30px;
        background: rgba(46,204,113,.10);
        border: 1px solid rgba(46,204,113,.22);
        color: #2ecc71;
        font-size: 13px;
        font-weight: 600;
    }

    /* Hero */

    .hero {
        padding: 35px 0 25px 0;
    }

    .hero h1 {
        font-size: 38px;
        margin: 0;
        font-weight: 800;
        letter-spacing: -1px;
    }

    .hero p {
        color: #888;
        font-size: 16px;
        margin-top: 8px;
    }

    /* Cards */

    .panel {
        border: 1px solid rgba(128,128,128,.18);
        border-radius: 18px;
        padding: 20px;
        background: rgba(128,128,128,.035);
    }

    .panel-title {
        font-size: 15px;
        font-weight: 750;
        margin-bottom: 15px;
    }

    .workspace-file {
        padding: 8px 10px;
        border-radius: 8px;
        margin: 3px 0;
        font-size: 13px;
    }

    .workspace-file:hover {
        background: rgba(109,93,252,.10);
    }

    .tool {
        padding: 10px 12px;
        border-radius: 10px;
        background: rgba(128,128,128,.06);
        margin: 7px 0;
        font-size: 13px;
    }

    /* Welcome */

    .welcome {
        text-align: center;
        padding: 55px 25px 35px 25px;
    }

    .welcome-icon {
        font-size: 50px;
        margin-bottom: 10px;
    }

    .welcome-title {
        font-size: 25px;
        font-weight: 750;
    }

    .welcome-text {
        color: #888;
        margin-top: 7px;
    }

    /* Activity */

    .activity {
        padding: 12px 14px;
        border-left: 3px solid #6d5dfc;
        margin: 8px 0;
        background: rgba(109,93,252,.05);
        border-radius: 0 10px 10px 0;
        font-size: 13px;
    }

    .activity-success {
        padding: 12px 14px;
        border-left: 3px solid #2ecc71;
        margin: 8px 0;
        background: rgba(46,204,113,.06);
        border-radius: 0 10px 10px 0;
        font-size: 13px;
    }

    /* Quick actions */

    .quick-title {
        font-size: 14px;
        font-weight: 700;
        margin: 20px 0 10px 0;
    }

    /* Hide chat input border noise */

    textarea {
        border-radius: 14px !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# State
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "activity" not in st.session_state:
    st.session_state.activity = []


# =========================================================
# Top bar
# =========================================================

st.markdown(
    """
    <div class="topbar">

        <div class="brand">

            <div class="brand-icon">
                ⚡
            </div>

            <div>
                <div class="brand-name">
                    CodePilot
                </div>

                <div class="brand-subtitle">
                    Autonomous AI Coding Engineer
                </div>
            </div>

        </div>

        <div class="online">
            ● Agent Ready
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Layout
# =========================================================

workspace, main_area, activity_area = st.columns(
    [1, 2.5, 1.2],
    gap="large",
)


# =========================================================
# Workspace
# =========================================================

with workspace:

    st.markdown(
        '<div class="panel-title">📁 WORKSPACE</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="workspace-file">
            📁 <b>calculator</b>
        </div>

        <div class="workspace-file">
            &nbsp;&nbsp;📄 main.py
        </div>

        <div class="workspace-file">
            &nbsp;&nbsp;📄 tests.py
        </div>

        <div class="workspace-file">
            &nbsp;&nbsp;📄 README.md
        </div>

        <div class="workspace-file">
            &nbsp;&nbsp;📁 pkg
        </div>

        <div class="workspace-file">
            &nbsp;&nbsp;&nbsp;&nbsp;📄 calculator.py
        </div>

        <div class="workspace-file">
            &nbsp;&nbsp;&nbsp;&nbsp;📄 render.py
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown(
        '<div class="panel-title">🛠️ AGENT TOOLS</div>',
        unsafe_allow_html=True,
    )

    tools = [
        ("🔍", "Inspect files"),
        ("📖", "Read code"),
        ("▶️", "Run Python"),
        ("✏️", "Write files"),
    ]

    for icon, name in tools:
        st.markdown(
            f"""
            <div class="tool">
                {icon} &nbsp; {name}
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# Main chat
# =========================================================

with main_area:

    st.markdown(
        """
        <div class="hero">
            <h1>Build. Debug. Ship. 🚀</h1>
            <p>
                Tell CodePilot what you want to change in your project.
                Your AI coding agent will investigate and act.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.messages:

        st.markdown(
            """
            <div class="welcome">

                <div class="welcome-icon">
                    ⚡
                </div>

                <div class="welcome-title">
                    What are we building today?
                </div>

                <div class="welcome-text">
                    Ask CodePilot to inspect, explain, debug,
                    or modify your codebase.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])


    st.markdown(
        '<div class="quick-title">Quick actions</div>',
        unsafe_allow_html=True,
    )

    quick1, quick2, quick3 = st.columns(3)

    with quick1:
        if st.button(
            "🐛 Fix a bug",
            use_container_width=True,
        ):
            st.session_state.quick_prompt = (
                "Inspect the calculator project and find "
                "any bug that should be fixed."
            )

    with quick2:
        if st.button(
            "🔍 Explain code",
            use_container_width=True,
        ):
            st.session_state.quick_prompt = (
                "Explain how the calculator project works."
            )

    with quick3:
        if st.button(
            "🧪 Run tests",
            use_container_width=True,
        ):
            st.session_state.quick_prompt = (
                "Run the calculator tests and report the results."
            )


# =========================================================
# Activity
# =========================================================

with activity_area:

    st.markdown(
        '<div class="panel-title">⚡ ACTIVITY</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.activity:

        st.caption(
            "Agent activity will appear here."
        )

        st.markdown(
            """
            <div class="activity">
                ◌ Waiting for task...
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        seen = set()

        for item in st.session_state.activity:

            item_type = item.get("type")
            tool = item.get("tool")
            message = item.get("message", "")

            if item_type == "tool" and tool:

                if tool not in seen:

                    st.markdown(
                        f"""
                        <div class="activity">
                            🔧 <b>{tool}</b><br>
                            <small>{message}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    seen.add(tool)

            elif item_type == "complete":

                st.markdown(
                    """
                    <div class="activity-success">
                        ✅ <b>Task completed</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            elif item_type == "error":

                st.error(message)


# =========================================================
# Chat input
# =========================================================

prompt = st.chat_input(
    "Ask CodePilot to inspect, fix, or modify your project..."
)


# Quick action support

if "quick_prompt" in st.session_state:

    prompt = st.session_state.quick_prompt

    del st.session_state.quick_prompt


# =========================================================
# Run agent
# =========================================================

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    activity_log = []

    try:

        with st.spinner("⚡ CodePilot is working..."):

            response = run_agent(
                prompt,
                verbose=False,
                activity_log=activity_log,
            )

        st.session_state.activity = activity_log

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

        st.rerun()

    except Exception as error:

        st.session_state.activity = activity_log

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": (
                    "⚠️ **Agent unavailable right now.**\n\n"
                    f"`{error}`"
                ),
            }
        )

        st.rerun()

