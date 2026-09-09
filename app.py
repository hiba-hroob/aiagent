import streamlit as st
from pathlib import Path

from main import run_agent


st.set_page_config(
    page_title="CodePilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROJECT_DIR = Path("calculator")


# =========================================================
# Helpers
# =========================================================

def get_project_files():
    """Return real files from the calculator project."""
    files = []

    if not PROJECT_DIR.exists():
        return files

    for path in sorted(PROJECT_DIR.rglob("*")):
        if ".venv" in path.parts or "__pycache__" in path.parts:
            continue

        if path.is_file():
            files.append(path.relative_to(PROJECT_DIR))

    return files


def get_file_icon(path):
    """Choose an icon based on file type."""
    if path.suffix == ".py":
        return "🐍"

    if path.suffix in {".md", ".txt"}:
        return "📄"

    if path.suffix == ".json":
        return "🧾"

    return "📎"


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

    .file-count {
        color: #888;
        font-size: 12px;
        margin-bottom: 12px;
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

    project_files = get_project_files()

    st.markdown(
        f'<div class="file-count">{len(project_files)} files detected</div>',
        unsafe_allow_html=True,
    )

    if not PROJECT_DIR.exists():

        st.warning("calculator/ project not found.")

    else:

        folders = {}

        for file_path in project_files:

            parent = str(file_path.parent)

            if parent not in folders:
                folders[parent] = []

            folders[parent].append(file_path)

        root_files = folders.get(".", [])

        if root_files:

            for file_path in root_files:

                icon = get_file_icon(file_path)

                st.markdown(
                    f"""
                    <div class="workspace-file">
                        {icon} {file_path.name}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        subfolders = sorted(
            key for key in folders
            if key != "."
        )

        for folder in subfolders:

            st.markdown(
                f"""
                <div class="workspace-file">
                    📁 <b>{folder}/</b>
                </div>
                """,
                unsafe_allow_html=True,
            )

            for file_path in folders[folder]:

                icon = get_file_icon(file_path)

                st.markdown(
                    f"""
                    <div class="workspace-file">
                        &nbsp;&nbsp;{icon} {file_path.name}
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

    st.markdown("---")

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.session_state.activity = []
        st.rerun()


# =========================================================
# Main chat
# =========================================================

with main_area:

    st.markdown(
        """
        <div class="hero">
            <h1>Build. Debug. Ship. 🚀</h1>
            <p>
                Tell CodePilot what you want to change.
                Your coding agent will inspect, reason, test, and respond.
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
                    test, or modify your codebase.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input(
        "Ask CodePilot to inspect, fix, or modify your project..."
    )

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

            error_message = (
                "⚠️ **Agent unavailable right now.**\n\n"
                f"`{error}`"
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )

            st.rerun()


# =========================================================
# Activity
# =========================================================

with activity_area:

    st.markdown(
        '<div class="panel-title">⚡ ACTIVITY</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.activity:

        st.caption("Agent activity will appear here.")

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
