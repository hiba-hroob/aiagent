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


def run_agent(user_prompt: str, verbose: bool = False) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    for _ in range(20):
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            tools=available_functions,
            temperature=0,
        )

        message = response.choices[0].message

        # Keep the assistant response in the conversation.
        messages.append(message)

        # The agent wants to use one or more tools.
        if message.tool_calls:
            for tool_call in message.tool_calls:
                result_message = call_function(
                    tool_call,
                    verbose=verbose,
                )

                if not result_message.get("content"):
                    raise RuntimeError("Tool call returned no content")

                # Give the tool result back to the agent.
                messages.append(result_message)

                if verbose:
                    print(f"-> {result_message['content']}")

            # Continue the loop so the agent can inspect
            # the tool result and decide what to do next.
            continue

        # No more tools means the agent has finished.
        return message.content or ""

    raise RuntimeError(
        "Maximum iterations reached without a final response."
    )


def main():
    parser = argparse.ArgumentParser(description="AI Coding Agent")

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

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")

    final_response = run_agent(
        args.user_prompt,
        verbose=args.verbose,
    )

    print("Final response:")
    print(final_response)


if __name__ == "__main__":
    main()
