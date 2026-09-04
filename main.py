import argparse
import json
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

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": args.user_prompt},
]

for _ in range(20):
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        tools=available_functions,
        temperature=0,
    )

    message = response.choices[0].message
    messages.append(message)

    if message.tool_calls:
        for tool_call in message.tool_calls:
            result_message = call_function(tool_call, args.verbose)

            if not result_message.get("content"):
                raise RuntimeError("Tool call returned no content")

            messages.append(result_message)

            if args.verbose:
                print(f"-> {result_message['content']}")
    else:
        print("Final response:")
        print(message.content)
        break
else:
    print("Maximum iterations reached without a final response.")
    exit(1)

if response.usage is None:
    raise RuntimeError("Response usage is missing")

message = response.choices[0].message

if args.verbose:
    print(f"User prompt: {args.user_prompt}")
    print(f"Prompt tokens: {response.usage.prompt_tokens}")
    print(f"Response tokens: {response.usage.completion_tokens}")

if message.tool_calls:
    for tool_call in message.tool_calls:
        result_message = call_function(tool_call, args.verbose)

        if not result_message.get("content"):
            raise RuntimeError("Tool call returned no content")

        if args.verbose:
            print(f"-> {result_message['content']}")
else:
    print(message.content)
