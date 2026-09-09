import argparse
import os

import argparse
import os

from dotenv import load_dotenv
from openai import OpenAI

from prompts import system_prompt
from call_function import available_functions, call_function


load_dotenv()

api_key = os.environ.get("OPENROUTER_API_KEY")

if api_key is None:
    raise RuntimeError("OPENROUTER_API_KEY is not set")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


def run_agent(
    user_prompt: str,
    verbose: bool = False,
    activity_log: list | None = None,
) -> str:
    """
    Run the AI coding agent.

    The agent can inspect files, read code, execute Python files,
    and modify files using the available tools.
    """

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

    if activity_log is not None:
        activity_log.append(
            {
                "type": "start",
                "message": "Agent started",
            }
        )

    for iteration in range(20):

        if activity_log is not None:
            activity_log.append(
                {
                    "type": "thinking",
                    "message": f"Agent step {iteration + 1}",
                }
            )

        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            tools=available_functions,
            temperature=0,
        )

        message = response.choices[0].message

        # Add the assistant message to the conversation.
        messages.append(message)

        # ---------------------------------
        # Agent wants to use tools
        # ---------------------------------

        if message.tool_calls:

            for tool_call in message.tool_calls:

                function_name = tool_call.function.name

                if activity_log is not None:
                    activity_log.append(
                        {
                            "type": "tool",
                            "tool": function_name,
                            "message": f"Using {function_name}",
                        }
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

                if activity_log is not None:
                    activity_log.append(
                        {
                            "type": "tool_result",
                            "tool": function_name,
                            "message": f"{function_name} completed",
                        }
                    )

                if verbose:
                    print(
                        f"-> {result_message['content']}"
                    )

            # The agent needs another model response
            # after receiving the tool results.
            continue

        # ---------------------------------
        # No tools = final answer
        # ---------------------------------

        final_response = message.content or ""

        if activity_log is not None:
            activity_log.append(
                {
                    "type": "complete",
                    "message": "Agent completed successfully",
                }
            )

        return final_response

    # ---------------------------------
    # Safety limit
    # ---------------------------------

    if activity_log is not None:
        activity_log.append(
            {
                "type": "error",
                "message": "Maximum agent steps reached",
            }
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

