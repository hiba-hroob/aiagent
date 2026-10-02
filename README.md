# 🤖 AI Coding Agent

An AI-powered coding agent built with Python that can inspect a software project, read and modify files, execute Python code, and iteratively work toward solving development tasks.

The project uses an LLM with tool/function calling to allow the agent to interact with a real project workspace instead of only generating text responses.

## ✨ Features

* 🤖 AI-powered coding assistant
* 📂 Inspect project files and directories
* 📖 Read source code and file contents
* ✏️ Create and modify files
* ▶️ Execute Python files
* 🔄 Iterative agent/tool execution
* 🧪 Run and verify code during tasks
* 🖥️ Streamlit-based web interface
* 🧰 Modular tool/function architecture
* 🧮 Includes a sample Python calculator project for testing the agent

## 🏗️ Architecture

The project follows an agent-based architecture where the language model can decide which tools it needs to use to complete a task.


                    User
                      │
                      ▼
              ┌───────────────┐
              │  Streamlit UI │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │   AI Agent    │
              │   Main Loop   │
              └───────┬───────┘
                      │
              Tool / Function Calls
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   Read Files     Write Files    Run Python
        │             │             │
        └─────────────┼─────────────┘
                      ▼
                 Project Workspace


## 📁 Project Structure


aiagent/
│
├── app.py
├── main.py
├── call_function.py
├── prompts.py
│
├── functions/
│   ├── get_files_info.py
│   ├── get_file_content.py
│   ├── write_file.py
│   └── run_python_file.py
│
├── calculator/
│   └── Sample Python project
│
├── test_get_files_info.py
├── test_get_file_content.py
├── test_write_file.py
├── test_run_python_file.py
│
├── pyproject.toml
├── uv.lock
└── README.md

## 🔧 Available Tools

The agent can interact with the project through several tools.

### `get_files_info`

Inspects files and directories inside the project workspace.

### `get_file_content`

Reads the contents of a source file so the agent can understand the existing implementation.

### `write_file`

Creates or modifies files inside the allowed project workspace.

### `run_python_file`

Executes a Python file and returns the result to the agent.

These tools allow the model to move from simply suggesting code to actually interacting with a software project.

## 🔄 How the Agent Works

A typical task follows an iterative process:


User Request
     │
     ▼
Understand Task
     │
     ▼
Inspect Project
     │
     ▼
Read Relevant Files
     │
     ▼
Select Tools
     │
     ▼
Modify Code
     │
     ▼
Run Python / Tests
     │
     ▼
Analyze Result
     │
     └──────► Continue if needed
     │
     ▼
Final Response


For example, a user can provide a task such as:

> Fix the bug in the calculator project.

The agent can inspect the project, identify relevant files, modify the code, execute Python code, and use the resulting output to continue working on the task.

## 🖥️ Running the Project

### Requirements

* Python 3
* Git
* `uv`
* An LLM API key/configuration required by the application
* Streamlit

### Clone the repository


git clone https://github.com/hiba-hroob/aiagent.git
cd aiagent


### Install dependencies

This project uses `pyproject.toml` and `uv.lock`.


uv sync


### Run the web application


uv run streamlit run app.py


Then open the local Streamlit URL shown in the terminal, usually:


http://localhost:8501


## 🧪 Running Tests

The repository contains tests for the main file-operation and Python-execution tools.

Run the test suite using:


pytest


or run individual tests, for example:


pytest test_get_files_info.py


## 🎯 Project Goal

The goal of this project is to explore how Large Language Models can be combined with tools and an execution environment to create an AI agent capable of performing practical software-engineering tasks.

Instead of only generating code, the agent can interact with an existing project by inspecting files, modifying code, executing Python programs, and using the results to continue its work.

## 🚧 Current Limitations

This is an actively developing project. The current version is a functional foundation for an AI coding agent, but several areas can be improved before production use, including:

* Stronger sandboxing and security controls
* More robust error handling
* More comprehensive agent-level testing
* Better task planning and verification
* Improved observability and logging
* More systematic evaluation of agent performance
* Enhanced user interface and developer experience

## 🛣️ Future Improvements

Planned improvements include:

* 🧠 Better task planning and reasoning
* 🔄 Automated test → fix → retest workflows
* 🔐 Stronger execution and filesystem isolation
* 📊 Agent evaluation and performance metrics
* 🌳 Git integration and change tracking
* ↩️ Safer rollback mechanisms
* 🖥️ Improved agent monitoring UI
* 🧪 Larger automated evaluation benchmark
* 📚 Improved documentation and examples

## 📌 Project Status

**Status: Active Development**

The current version provides the core functionality required for an AI coding agent and serves as the foundation for further improvements in reliability, security, evaluation, and autonomous software-engineering capabilities.

## 👩‍💻 Author

**Hiba Hroob**

GitHub: https://github.com/hiba-hroob/aiagent

## 📄 License

This project is currently under development. License information can be added when the project is prepared for public release.
