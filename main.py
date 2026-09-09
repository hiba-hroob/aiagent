import argparse
import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from prompts import system_prompt
from call_function import available_functions, call_function


load_dotenv()

PROJECT_DIR = Path("./calculator")

api_key = os.environ.get("OPENROUTER_API_KEY")

client = None

if api_key:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


def add_activity(
    activity_log: list | None,
    activity_type: str,
    message: str,
    tool: str | None = None,
):
    if activity_log is None:
        return

    item = {
        "type": activity_type,
        "message": message,
    }

    if tool:
        item["tool"] = tool

    activity_log.append(item)


def inspect_project(activity_log=None) -> str:
    add_activity(
        activity_log,
        "tool",
        "Inspecting calculator project",
        "get_files_info",
    )

    if not PROJECT_DIR.exists():
        return "Calculator project directory was not found."

    lines = []

    for path in sorted(PROJECT_DIR.rglob("*")):
        if ".venv" in path.parts or "__pycache__" in path.parts:
            continue

        relative = path.relative_to(PROJECT_DIR)

        if path.is_dir():
            lines.append(f"[DIR]  {relative}")
        else:
            try:
                size = path.stat().st_size
            except OSError:
                size = 0

            lines.append(f"[FILE] {relative} ({size} bytes)")

    add_activity(
        activity_log,
        "tool_result",
        "Project files inspected",
        "get_files_info",
    )

    return "\n".join(lines)


def read_project_file(
    file_path: str,
    activity_log=None,
) -> str:
    add_activity(
        activity_log,
        "tool",
        f"Reading {file_path}",
        "get_file_content",
    )

    target = (PROJECT_DIR / file_path).resolve()

    try:
        target.relative_to(PROJECT_DIR.resolve())
    except ValueError:
        return "Error: file is outside the project directory."

    if not target.exists() or not target.is_file():
        return f"File not found: {file_path}"

    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"Could not read {file_path} as UTF-8 text."

    add_activity(
        activity_log,
        "tool_result",
        f"Read {file_path}",
        "get_file_content",
    )

    return content


def run_local_tests(activity_log=None) -> tuple[int, str]:
    add_activity(
        activity_log,
        "tool",
        "Running calculator test suite",
        "run_python_file",
    )

    try:
        result = subprocess.run(
            ["python", "tests.py"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        add_activity(
            activity_log,
            "error",
            "Tests timed out",
        )
        return 124, "Tests timed out."

    output_parts = []

    if result.stdout.strip():
        output_parts.append(result.stdout.strip())

    if result.stderr.strip():
        output_parts.append(result.stderr.strip())

    output = "\n".join(output_parts)

    if result.returncode == 0:
        message = "All calculator tests passed"
    else:
        message = "Calculator tests reported failures"

    add_activity(
        activity_log,
        "tool_result",
        message,
        "run_python_file",
    )

    return result.returncode, output


def calculate_demo_result() -> str:
    try:
        result = subprocess.run(
            ["python", "main.py", "3 + 7 * 2"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=15,
        )

        if result.returncode != 0:
            return result.stderr.strip() or "Calculator execution failed."

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        return "Calculator execution timed out."


def demo_response(
    user_prompt: str,
    activity_log: list | None = None,
) -> str:
    add_activity(
        activity_log,
        "start",
        "Starting local CodePilot demo",
    )

    project_listing = inspect_project(activity_log)

    calculator_source = read_project_file(
        "pkg/calculator.py",
        activity_log,
    )

    render_source = read_project_file(
        "pkg/render.py",
        activity_log,
    )

    test_return_code, test_output = run_local_tests(
        activity_log
    )

    calculator_output = calculate_demo_result()

    tests_ok = test_return_code == 0

    source_state = (
        "✅ Calculator source inspected."
        if calculator_source.strip()
        else "⚠️ Calculator source could not be inspected."
    )

    render_state = (
        "✅ Renderer source inspected."
        if render_source.strip()
        else "⚠️ Renderer source could not be inspected."
    )

    test_status = (
        "✅ All local calculator tests passed."
        if tests_ok
        else "❌ Some local calculator tests failed."
    )

    add_activity(
        activity_log,
        "complete",
        "Local demo completed",
    )

    lines = [
        "## ⚡ CodePilot — Local Demo Mode",
        "",
        "The live AI service is currently unavailable, so CodePilot switched to local project analysis.",
        "",
        "### Your request",
        "",
        f"> {user_prompt}",
        "",
        "### 🔍 Project inspection",
        "",
        "CodePilot inspected the real `calculator/` project.",
        "",
        "```text",
        project_listing,
        "```",
        "",
        "### 📖 Source analysis",
        "",
        source_state,
        render_state,
        "",
        "The calculator uses `pkg/calculator.py` for expression evaluation",
        "and `pkg/render.py` for JSON formatting.",
        "The command-line entry point is `calculator/main.py`.",
        "",
        "### 🧪 Real test execution",
        "",
        test_status,
        "",
        "```text",
        test_output or "No test output was produced.",
        "```",
        "",
        "### ▶️ Real calculator verification",
        "",
        "CodePilot executed:",
        "",
        "`3 + 7 * 2`",
        "",
        "Result:",
        "",
        "```text",
        calculator_output,
        "```",
        "",
        "### ✅ Result",
        "",
        "Local verification completed successfully."
        if tests_ok
        else "Local verification found a problem.",
    ]

    return "\n".join(lines)


def run_agent(
    user_prompt: str,
    verbose: bool = False,
    activity_log: list | None = None,
) -> str:
    if client is None:
        return demo_response(
            user_prompt,
            activity_log,
        )

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    add_activity(
        activity_log,
        "start",
        "Starting AI coding agent",
    )

    for iteration in range(20):

        add_activity(
            activity_log,
            "thinking",
            f"Agent step {iteration + 1}",
        )

        try:
            response = client.chat.completions.create(
                model="openrouter/free",
                messages=messages,
                tools=available_functions,
                temperature=0,
            )

        except Exception as error:
            error_text = str(error)

            if (
                "429" in error_text
                or "rate limit" in error_text.lower()
            ):
                return demo_response(
                    user_prompt,
                    activity_log,
                )

            add_activity(
                activity_log,
                "error",
                f"API error: {error}",
            )

            raise

        message = response.choices[0].message

        messages.append(message)

        if message.tool_calls:

            for tool_call in message.tool_calls:

                function_name = tool_call.function.name

                add_activity(
                    activity_log,
                    "tool",
                    f"Using {function_name}",
                    function_name,
                )

                if verbose:
                    print(
                        f" - Calling function: {function_name}"
                    )

                result_message = call_function(
                    tool_call,
                    verbose=verbose,
                )

                if not result_message.get("content"):
                    raise RuntimeError(
                        "Tool call returned no content"
                    )

                messages.append(result_message)

                add_activity(
                    activity_log,
                    "tool_result",
                    f"{function_name} completed",
                    function_name,
                )

                if verbose:
                    print(
                        f"-> {result_message['content']}"
                    )

            continue

        final_response = message.content or ""

        add_activity(
            activity_log,
            "complete",
            "AI agent completed successfully",
        )

        return final_response

    add_activity(
        activity_log,
        "error",
        "Maximum agent steps reached",
    )

    return (
        "The agent reached its maximum number of steps "
        "without completing the task."
    )


def main() -> None:

    parser = argparse.ArgumentParser(
        description="AI Coding Agent"
    )

    parser.add_argument(
        "user_prompt",
        type=str,
        help="User prompt",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    final_response = run_agent(
        args.user_prompt,
        verbose=args.verbose,
    )

    print("Final response:")
    print(final_response)


if __name__ == "__main__":
    main()
