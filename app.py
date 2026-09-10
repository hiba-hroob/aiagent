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

    if suffix == ".json":
        return "◈"

    return "📎"


def get_stage(activity):
    tools = {
        item.get("tool")
        for item in activity
        if item.get("type") == "tool"
    }

    completed = any(
        item.get("type") == "complete"
        for item in activity
    )

    if completed:
        return "VERIFIED"

    if "write_file" in tools:
        return "FIXING"

    if "run_python_file" in tools:
        return "TESTING"

    if "get_file_content" in tools:
        return "READING"

    if "get_files_info" in tools:
        return "SCANNING"

    return "READY"


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


# =========================================================
# Session
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "activity" not in st.session_state:
    st.session_state.activity = []

if "mission_id" not in st.session_state:
    st.session_state.mission_id = 1


# =========================================================
# Visual theme
# =========================================================

st.markdown(
    """
    <style>
    #MainMenu {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    .stApp {
        background-color: #080a0f;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.2rem;
        padding-bottom: 1.5rem;
    }

    [data-testid="stMetric"] {
        background: #10131b;
        border: 1px solid #242a36;
        border-radius: 14px;
        padding: 10px;
    }

    [data-testid="stMetricValue"] {
        color: #f2f4f8;
    }

    [data-testid="stMetricLabel"] {
        color: #778095;
    }

    .stButton button {
        border-radius: 10px;
        border: 1px solid #2a3040;
        background: #11141c;
        color: #dce1eb;
        font-weight: 700;
    }

    .stButton button:hover {
        border-color: #7661ff;
        color: white;
        background: #17152a;
    }

    .stChatInputContainer textarea {
        background: #0f1219 !important;
        color: #f1f3f8 !important;
        border: 1px solid #302a50 !important;
        border-radius: 14px !important;
    }

    div[data-testid="stChatMessage"] {
        border: 1px solid #1d222d;
        border-radius: 14px;
        background: #0e1118;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Header
# =========================================================

header_left, header_right = st.columns(
    [5, 1],
    vertical_alignment="center",
)

with header_left:
    st.title("🧬 CodePilot")
    st.caption(
        "Autonomous Coding Intelligence"
    )

with header_right:
    st.success("● READY")


st.divider()


# =========================================================
# Mission
# =========================================================

mission_left, mission_right = st.columns(
    [3, 2],
    vertical_alignment="center",
)

with mission_left:
    st.markdown(
        f"### Mission #{st.session_state.mission_id:03d}"
    )

with mission_right:
    st.caption(
        "UNDERSTAND  →  SCAN  →  READ  →  TEST  →  PROVE"
    )


# =========================================================
# Main layout
# =========================================================

left, center, right = st.columns(
    [1, 2.4, 1],
    gap="large",
)


# =========================================================
# Left: Project DNA
# =========================================================

with left:

    st.subheader("Project DNA")

    files = get_project_files()

    if files:

        for file_path in files:
            st.write(
                f"{get_file_icon(file_path)}  {file_path}"
            )

    else:
        st.warning(
            "calculator/ directory not found."
        )

    st.divider()

    st.subheader("Agent")

    st.write("🔍 Inspect")
    st.write("📖 Read")
    st.write("🧪 Test")
    st.write("✏️ Modify")

    st.divider()

    if st.button(
        "↻ New mission",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.session_state.activity = []
        st.session_state.mission_id += 1
        st.rerun()


# =========================================================
# Center: Mission Core
# =========================================================

with center:

    st.subheader("Mission Control")

    st.markdown(
        "## Give it a problem. Get proof."
    )

    st.caption(
        "CodePilot investigates the project, executes tools, "
        "and verifies the result."
    )

    current_stage = get_stage(
        st.session_state.activity
    )

    st.markdown("### 🧬 Mission Core")

    core_col1, core_col2, core_col3 = st.columns(3)

    with core_col1:
        st.metric(
            "Stage",
            current_stage,
        )

    with core_col2:
        st.metric(
            "Files",
            len(files),
        )

    with core_col3:

        test_count = None

        for message in st.session_state.messages:

            if message["role"] == "assistant":

                count = extract_test_count(
                    message["content"]
                )

                if count:
                    test_count = count

        st.metric(
            "Tests",
            f"{test_count}/{test_count}"
            if test_count
            else "—",
        )

    st.progress(
        1.0
        if current_stage == "VERIFIED"
        else 0.75
        if current_stage == "TESTING"
        else 0.5
        if current_stage == "READING"
        else 0.25
        if current_stage == "SCANNING"
        else 0.05
    )

    stage_columns = st.columns(5)

    stage_names = [
        "UNDERSTAND",
        "SCAN",
        "READ",
        "TEST",
        "PROVE",
    ]

    stage_tools = {
        "SCAN": "get_files_info",
        "READ": "get_file_content",
        "TEST": "run_python_file",
    }

    used_tools = {
        item.get("tool")
        for item in st.session_state.activity
        if item.get("type") == "tool"
    }

    mission_complete = any(
        item.get("type") == "complete"
        for item in st.session_state.activity
    )

    for index, stage in enumerate(stage_names):

        with stage_columns[index]:

            if stage == "UNDERSTAND":
                done = bool(
                    st.session_state.activity
                )

            elif stage == "PROVE":
                done = mission_complete

            else:
                done = (
                    stage_tools[stage]
                    in used_tools
                )

            if done:
                st.success(
                    f"✓ {stage}"
                )
            else:
                st.info(stage)

    st.divider()

    if not st.session_state.messages:

        st.info(
            "🧬 Mission Core ready. "
            "Send a task below to activate CodePilot."
        )

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):
            st.markdown(
                message["content"]
            )

    prompt = st.chat_input(
        "Describe a bug, task, or question..."
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
                "🧬 CodePilot is working..."
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


# =========================================================
# Right: Live DNA
# =========================================================

with right:

    st.subheader("Live DNA")

    if not st.session_state.activity:

        st.info(
            "Waiting for mission..."
        )

    else:

        shown_tools = set()
        mission_complete = False

        for item in st.session_state.activity:

            item_type = item.get("type")
            tool = item.get("tool")
            message = item.get(
                "message",
                "",
            )

            if item_type == "tool" and tool:

                if tool not in shown_tools:

                    st.write(
                       f"✓ {tool}"
                    )

                    st.caption(message)

                    shown_tools.add(tool)

            elif item_type == "complete":

                mission_complete = True

        if mission_complete:

            st.success(
                "🟢 MISSION VERIFIED"
            )

            test_count = None

            for message in st.session_state.messages:

                if message["role"] == "assistant":

                    count = extract_test_count(
                        message["content"]
                    )

                    if count:
                        test_count = count

            metric1, metric2 = st.columns(2)

            with metric1:
                st.metric(
                    "Tools",
                    len(shown_tools),
                )

            with metric2:
                st.metric(
                    "Tests",
                    (
                        f"{test_count}/{test_count}"
                        if test_count
                        else "OK"
                    ),
                )
