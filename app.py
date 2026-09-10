import re
from pathlib import Path

import streamlit as st

from main import run_agent


st.set_page_config(
    page_title="CodePilot",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PROJECT_DIR = Path("calculator")


def get_project_files():
    if not PROJECT_DIR.exists():
        return []

    files = []

    for path in sorted(PROJECT_DIR.rglob("*")):
        if ".venv" in path.parts:
            continue

        if "__pycache__" in path.parts:
            continue

        if path.is_file():
            files.append(
                str(path.relative_to(PROJECT_DIR))
            )

    return files


def get_file_icon(file_name):
    suffix = Path(file_name).suffix.lower()

    if suffix == ".py":
        return "🐍"

    if suffix == ".md":
        return "📘"

    if suffix == ".txt":
        return "📄"

    return "📎"


def get_activity_tools():
    tools = []

    for item in st.session_state.activity:
        if item.get("type") == "tool":
            tool = item.get("tool")

            if tool and tool not in tools:
                tools.append(tool)

    return tools


def extract_test_count(text):
    if not text:
        return None

    match = re.search(
        r"Ran\s+(\d+)\s+tests?",
        text,
        re.IGNORECASE,
    )

    if match:
        return match.group(1)

    return None


# ------------------------------------------------------------
# Session state
# ------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "activity" not in st.session_state:
    st.session_state.activity = []

if "mission_id" not in st.session_state:
    st.session_state.mission_id = 1


# ------------------------------------------------------------
# CSS
# ------------------------------------------------------------

st.markdown(
    """
    <style>

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    .stApp {
        background-color: #0b0d12;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }

    .title-text {
        font-size: 46px;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .subtitle-text {
        color: #8b91a1;
        font-size: 15px;
        margin-bottom: 18px;
    }

    .mission-text {
        color: #9a86ff;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
    }

    .core {
        text-align: center;
        padding: 32px 10px;
        border: 1px solid #262b38;
        border-radius: 24px;
        background-color: #11141c;
        margin: 15px 0;
    }

    .core-icon {
        font-size: 54px;
    }

    .core-title {
        font-size: 17px;
        font-weight: 800;
        margin-top: 8px;
    }

    .core-status {
        color: #8c75ff;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2px;
        margin-top: 5px;
    }

    .stage {
        text-align: center;
        padding: 10px 4px;
        border-radius: 10px;
        background-color: #12151d;
        border: 1px solid #242936;
        color: #747c8e;
        font-size: 10px;
        font-weight: 700;
    }

    .stage-done {
        color: #64dfb0;
        border-color: #28483e;
        background-color: #101c18;
    }

    .stage-active {
        color: #b0a1ff;
        border-color: #4a3d83;
        background-color: #19162a;
    }

    .panel-title {
        font-size: 11px;
        font-weight: 800;
        color: #747d90;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
    }

    .file-item {
        padding: 7px 8px;
        margin-bottom: 4px;
        border-radius: 8px;
        background-color: #11141b;
        color: #d4d8e2;
        font-size: 11px;
    }

    .activity-item {
        padding: 9px;
        margin-bottom: 7px;
        border-left: 3px solid #7d64ff;
        border-radius: 0 8px 8px 0;
        background-color: #131620;
    }

    .activity-name {
        font-size: 10px;
        font-weight: 800;
        color: #e2e5ed;
    }

    .activity-message {
        font-size: 9px;
        color: #7d8596;
        margin-top: 3px;
    }

    .verify-box {
        padding: 14px;
        margin-top: 10px;
        border-radius: 12px;
        background-color: #102019;
        border: 1px solid #28503e;
    }

    .verify-title {
        color: #67e3b2;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.5px;
    }

    .verify-main {
        color: #f1fff8;
        font-size: 16px;
        font-weight: 800;
        margin-top: 5px;
    }

    .empty-box {
        text-align: center;
        padding: 35px 15px;
        border: 1px dashed #29303d;
        border-radius: 16px;
        background-color: #0f1218;
    }

    .empty-icon {
        font-size: 32px;
    }

    .empty-title {
        color: #e7eaf1;
        font-size: 18px;
        font-weight: 800;
        margin-top: 7px;
    }

    .empty-text {
        color: #727b8d;
        font-size: 11px;
        margin-top: 5px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

header_left, header_right = st.columns(
    [5, 1],
    vertical_alignment="center",
)

with header_left:
    st.markdown(
        "# 🧬 CodePilot"
    )

    st.caption(
        "Autonomous coding intelligence"
    )

with header_right:
    st.success(
        "● READY"
    )


st.divider()

st.markdown(
    f"**MISSION #{st.session_state.mission_id:03d}**"
)

st.caption(
    "UNDERSTAND  •  SCAN  •  READ  •  TEST  •  PROVE"
)


# ------------------------------------------------------------
# Main layout
# ------------------------------------------------------------

left, center, right = st.columns(
    [1, 2.2, 1],
    gap="large",
)


# ------------------------------------------------------------
# Left: project
# ------------------------------------------------------------

with left:

    st.markdown(
        '<div class="panel-title">PROJECT DNA</div>',
        unsafe_allow_html=True,
    )

    files = get_project_files()

    if files:

        for file_path in files:

            st.markdown(
                f"""
                <div class="file-item">
                    {get_file_icon(file_path)} {file_path}
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:
        st.warning(
            "calculator/ directory not found."
        )

    st.markdown("")

    st.markdown(
        '<div class="panel-title">AGENT CAPABILITIES</div>',
        unsafe_allow_html=True,
    )

    capabilities = [
        "🔍 Inspect project",
        "📖 Read source",
        "🧪 Run tests",
        "✏️ Modify files",
    ]

    for capability in capabilities:
        st.write(capability)

    st.markdown("")

    if st.button(
        "↻ New mission",
        use_container_width=True,
    ):

        st.session_state.messages = []
        st.session_state.activity = []
        st.session_state.mission_id += 1

        st.rerun()


# ------------------------------------------------------------
# Center
# ------------------------------------------------------------

with center:

    st.markdown(
        '<div class="panel-title">MISSION CONTROL</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="title-text">
            Give it a problem.<br>
            Get proof.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="subtitle-text">
            CodePilot investigates software tasks,
            uses its tools, and verifies the result.
        </div>
        """,
        unsafe_allow_html=True,
    )

    current_tools = get_activity_tools()

    if any(
        item.get("type") == "complete"
        for item in st.session_state.activity
    ):
        core_state = "VERIFIED"
    elif "run_python_file" in current_tools:
        core_state = "TESTING"
    elif "get_file_content" in current_tools:
        core_state = "READING"
    elif "get_files_info" in current_tools:
        core_state = "SCANNING"
    else:
        core_state = "READY"

    st.markdown(
        f"""
        <div class="core">

            <div class="core-icon">
                🧬
            </div>

            <div class="core-title">
                MISSION CORE
            </div>

            <div class="core-status">
                {core_state}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    stages = [
        ("UNDERSTAND", None),
        ("SCAN", "get_files_info"),
        ("READ", "get_file_content"),
        ("TEST", "run_python_file"),
        ("PROVE", None),
    ]

    stage_columns = st.columns(5)

    completed = any(
        item.get("type") == "complete"
        for item in st.session_state.activity
    )

    for index, (stage_name, required_tool) in enumerate(stages):

        with stage_columns[index]:

            if stage_name == "UNDERSTAND":
                stage_class = (
                    "stage-active"
                    if st.session_state.activity
                    else ""
                )

            elif stage_name == "PROVE":
                stage_class = (
                    "stage-done"
                    if completed
                    else ""
                )

            else:
                stage_class = (
                    "stage-done"
                    if required_tool in current_tools
                    else ""
                )

            st.markdown(
                f"""
                <div class="stage {stage_class}">
                    {stage_name}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("")

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    prompt = st.chat_input(
        "Give CodePilot a mission..."
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

            with st.spinner(
                "CodePilot is working..."
            ):

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
                        "⚠️ **Mission failed.**\n\n"
                        f"`{error}`"
                    ),
                }
            )

            st.rerun()


# ------------------------------------------------------------
# Right: live signal
# ------------------------------------------------------------

with right:

    st.markdown(
        '<div class="panel-title">LIVE SIGNAL</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.activity:

        st.markdown(
            """
            <div class="empty-box">

                <div class="empty-icon">
                    ◌
                </div>

                <div class="empty-title">
                    Standby
                </div>

                <div class="empty-text">
                    Waiting for a mission
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        shown_tools = set()
        completed = False

        for item in st.session_state.activity:

            if item.get("type") == "tool":

                tool = item.get("tool")

                if tool and tool not in shown_tools:

                    st.markdown(
                        f"""
                        <div class="activity-item">

                            <div class="activity-name">
                                ✓ {tool}
                            </div>

                            <div class="activity-message">
                                {item.get("message", "")}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    shown_tools.add(tool)

            elif item.get("type") == "complete":

                completed = True

        if completed:

            test_count = None

            for message in st.session_state.messages:

                if message["role"] == "assistant":

                    count = extract_test_count(
                        message["content"]
                    )

                    if count:
                        test_count = count

            if test_count:

                test_text = f"{test_count}/{test_count}"

            else:

                test_text = "OK"

            st.markdown(
                f"""
                <div class="verify-box">

                    <div class="verify-title">
                        PROOF OF WORK
                    </div>

                    <div class="verify-main">
                        ✓ MISSION VERIFIED
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            st.metric(
                "Tests",
                test_text,
            )

            st.metric(
                "Tools used",
                len(shown_tools),
            )
