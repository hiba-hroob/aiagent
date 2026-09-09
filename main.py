import argparse
import os
import re
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
    activity_log,
    activity_type,
    message,
    tool=None,
):
    if activity_log is None:
        return

    item = {
        "type": activity_type,
        "message": message,
    }

    if tool is not None:
        item["tool"] = tool

    activity_log.append(item)


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


def inspect_project(activity_log=None):
    add_activity(
        activity_log,
        "tool",
        "Inspecting calculator project",
        "get_files_info",
    )

    files = get_project_files()

    if not files:
        output = "No project files were found."
    else:
        output = "\n".join(
            f"- {file_path}"
            for file_path in files
        )

    add_activity(
        activity_log,
        "tool_result",
        f"Found {len(files)} project files",
        "get_files_info",
    )

    return output


def read_project_file(
    file_path,
    activity_log=None,
):
    add_activity(
        activity_log,
        "tool",
        f"Reading {file_path}",
        "get_file_content",
    )

    project_root = PROJECT_DIR.resolve()
    target = (PROJECT_DIR / file_path).resolve()

    try:
        target.relative_to(project_root)
    except ValueError:
        return "Error: file is outside the project."

    if not target.exists():
        return f"File not found: {file_path}"

    if not target.is_file():
        return f"Not a file: {file_path}"

    try:
        content = target.read_text(
            encoding="utf-8"
        )
    except UnicodeDecodeError:
        return f"Could not read {file_path}."

    add_activity(
        activity_log,
        "tool_result",
        f"Read {file_path}",
        "get_file_content",
    )

    return content


def run_local_tests(activity_log=None):
    add_activity(
        activity_log,
        "tool",
        "Running calculator tests",
        "run_python_file",
    )

    commands = [
        ["python", "tests.py"],
        ["python3", "tests.py"],
    ]

    result = None

    for command in commands:
        try:
            result = subprocess.run(
                command,
                cwd=PROJECT_DIR,
                capture_output=True,
                text=True,
                timeout=30,
            )
            break

        except FileNotFoundError:
            continue

        except subprocess.TimeoutExpired:
            add_activity(
                activity_log,
                "error",
                "Tests timed out",
            )
            return 124, "Tests timed out."

    if result is None:
        message = "Python executable was not found."

        add_activity(
            activity_log,
            "error",
            message,
        )

        return 127, message

    output_parts = []

    if result.stdout.strip():
        output_parts.append(
            result.stdout.strip()
        )

    if result.stderr.strip():
        output_parts.append(
            result.stderr.strip()
        )

    output = "\n".join(output_parts)

    if result.returncode == 0:
        status = "All calculator tests passed."
    else:
        status = "Calculator tests reported failures."

    add_activity(
        activity_log,
        "tool_result",
        status,
        "run_python_file",
    )

    return result.returncode, output


def run_calculator(
    expression,
    activity_log=None,
):
    expression = expression.strip()

    if not expression:
        return "No expression was provided."

    if not re.fullmatch(
        r"[0-9+\-*/().\s]+",
        expression,
    ):
        return "The expression contains unsupported characters."

    add_activity(
        activity_log,
        "tool",
        f"Running expression: {expression}",
        "run_python_file",
    )

    commands = [
        ["python", "main.py", expression],
        ["python3", "main.py", expression],
    ]

    result = None

    for command in commands:
        try:
            result = subprocess.run(
                command,
                cwd=PROJECT_DIR,
                capture_output=True,
                text=True,
                timeout=15,
            )
            break

        except FileNotFoundError:
            continue

        except subprocess.TimeoutExpired:
            return "Calculator execution timed out."

    if result is None:
        return "Python executable was not found."

    if result.returncode != 0:
        return (
            result.stderr.strip()
            or result.stdout.strip()
            or "Calculator execution failed."
        )

    output = result.stdout.strip()

    add_activity(
        activity_log,
        "tool_result",
        "Calculator execution completed",
        "run_python_file",
    )

    return output


def detect_expression(text):
    matches = re.findall(
        r"(?<!\w)"
        r"(?:\d+(?:\.\d+)?\s*)"
        r"(?:[+\-*/]\s*(?:\d+(?:\.\d+)?\s*))+",
        text,
    )

    if not matches:
        return None

    return matches[0].strip()


def explain_project(activity_log=None):
    calculator_source = read_project_file(
        "pkg/calculator.py",
        activity_log,
    )

    render_source = read_project_file(
        "pkg/render.py",
        activity_log,
    )

    main_source = read_project_file(
        "main.py",
        activity_log,
    )

    explanation = []

    if "class Calculator" in calculator_source:
        explanation.append(
            "• pkg/calculator.py contains the Calculator "
            "class responsible for evaluating expressions."
        )
    else:
        explanation.append(
            "• pkg/calculator.py contains the calculator logic."
        )

    if "json.dumps" in render_source:
        explanation.append(
            "• pkg/render.py formats the calculator result as JSON."
        )
    else:
        explanation.append(
            "• pkg/render.py handles output formatting."
        )

    if "sys.argv" in main_source:
        explanation.append(
            "• calculator/main.py is the command-line entry point."
        )
    else:
        explanation.append(
            "• calculator/main.py is the application entry point."
        )

    return "\n".join(explanation)


def demo_response(
    user_prompt,
    activity_log=None,
):
    add_activity(
        activity_log,
        "start",
        "Starting CodePilot local mode",
    )

    prompt_lower = user_prompt.lower()

    wants_tests = (
        "test" in prompt_lower
        or "tests" in prompt_lower
        or "run the calculator" in prompt_lower
    )

    wants_explanation = (
        "explain" in prompt_lower
        or "how does" in prompt_lower
        or "how the calculator" in prompt_lower
        or "how the application" in prompt_lower
    )

    wants_files = (
        "file" in prompt_lower
        or "files" in prompt_lower
        or "inspect" in prompt_lower
        or "project structure" in prompt_lower
    )

    expression = detect_expression(
        user_prompt
    )

    if wants_tests and wants_explanation:

        files = inspect_project(
            activity_log
        )

        explanation = explain_project(
            activity_log
        )

        test_code, test_output = run_local_tests(
            activity_log
        )

        if test_code == 0:
            status = "✅ All calculator tests passed."
        else:
            status = "❌ Some calculator tests failed."

        response = "\n".join(
            [
                "## ⚡ CodePilot — Local Mode",
                "",
                "### Request",
                "",
                f"> {user_prompt}",
                "",
                "### 🔍 Project inspection",
                "",
                files,
                "",
                "### 🧠 How the application works",
                "",
                explanation,
                "",
                "### 🧪 Test execution",
                "",
                status,
                "",
                "```text",
                test_output or "No test output was produced.",
                "```",
                "",
                "### ✅ Result",
                "",
                "CodePilot inspected the real project, explained its structure,",
                "and ran the real calculator tests locally.",
            ]
        )

        add_activity(
            activity_log,
            "complete",
            "Inspection, explanation, and testing completed",
        )

        return response

    if wants_tests:

        test_code, test_output = run_local_tests(
            activity_log
        )

        if test_code == 0:
            status = "✅ All calculator tests passed."
        else:
            status = "❌ Some calculator tests failed."

        response = "\n".join(
            [
                "## ⚡ CodePilot — Local Mode",
                "",
                "### Request",
                "",
                f"> {user_prompt}",
                "",
                "### 🧪 Test execution",
                "",
                status,
                "",
                "```text",
                test_output or "No test output was produced.",
                "```",
                "",
                "### ✅ Result",
                "",
                "CodePilot ran the real calculator test suite locally.",
            ]
        )

        add_activity(
            activity_log,
            "complete",
            "Test task completed",
        )

        return response

    if wants_explanation:

        files = inspect_project(
            activity_log
        )

        explanation = explain_project(
            activity_log
        )

        response = "\n".join(
            [
                "## ⚡ CodePilot — Local Mode",
                "",
                "### Request",
                "",
                f"> {user_prompt}",
                "",
                "### 📁 Project structure",
                "",
                files,
                "",
                "### 🧠 How it works",
                "",
                explanation,
                "",
                "### ✅ Result",
                "",
                "This explanation was built from the real project files.",
            ]
        )

        add_activity(
            activity_log,
            "complete",
            "Project explanation completed",
        )

        return response

    if wants_files:

        files = inspect_project(
            activity_log
        )

        response = "\n".join(
            [
                "## ⚡ CodePilot — Local Mode",
                "",
                "### Request",
                "",
                f"> {user_prompt}",
                "",
                "### 📁 Project files",
                "",
                files,
                "",
                "### ✅ Result",
                "",
                "The real calculator workspace was inspected successfully.",
            ]
        )

        add_activity(
            activity_log,
            "complete",
            "Project inspection completed",
        )

        return response

    if expression:

        result = run_calculator(
            expression,
            activity_log,
        )

        response = "\n".join(
            [
                "## ⚡ CodePilot — Local Mode",
                "",
                "### Request",
                "",
                f"> {user_prompt}",
                "",
                "### ▶️ Calculator execution",
                "",
                f"Expression: `{expression}`",
                "",
                "```text",
                result,
                "```",
                "",
                "### ✅ Result",
                "",
                "The real calculator evaluated the expression.",
            ]
        )

        add_activity(
            activity_log,
            "complete",
            "Calculator task completed",
        )

        return response

    files = inspect_project(
        activity_log
    )

    test_code, test_output = run_local_tests(
        activity_log
    )

    if test_code == 0:
        status = "✅ Tests passed."
    else:
        status = "❌ Tests reported failures."

    response = "\n".join(
        [
            "## ⚡ CodePilot — Local Mode",
            "",
            "### Request",
            "",
            f"> {user_prompt}",
            "",
            "### 📁 Workspace",
            "",
            files,
            "",
            "### 🧪 Verification",
            "",
            status,
            "",
            "```text",
            test_output or "No test output was produced.",
            "```",
            "",
            "### ✅ Result",
            "",
            "The local project was inspected and verified.",
        ]
    )

    add_activity(
        activity_log,
        "complete",
        "General project analysis completed",
    )

    return response


def run_agent(
    user_prompt,
    verbose=False,
    activity_log=None,
):
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

                function_name = (
                    tool_call.function.name
                )

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


def main():

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
