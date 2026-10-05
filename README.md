# 🧬 CodePilot

**CodePilot** is an AI-powered coding agent built with Python and Streamlit.

It can inspect a real software project, read and modify files, execute Python programs, and iteratively work toward solving development tasks.

Instead of only generating code suggestions, CodePilot can interact with a project workspace through tool and function calling.

## 🌐 Live Demo

Try CodePilot online:

**https://codepilott-ai.streamlit.app/**

The deployed version provides an interactive web interface where you can give CodePilot a software-engineering task and watch it inspect the project, use tools, test code, and verify the result.

## ✨ Features

* 🤖 AI-powered coding agent
* 📂 Inspect project files and directories
* 📖 Read source code and file contents
* ✏️ Create and modify files
* ▶️ Execute Python files
* 🔄 Iterative agent and tool execution
* 🧪 Run and verify code during tasks
* 🖥️ Interactive Streamlit web interface
* 🧰 Modular tool/function architecture
* 🧮 Includes a sample Python calculator project
* 🌐 Deployed as a live web application

## 🏗️ Architecture

CodePilot follows an agent-based architecture where the language model decides which tools it needs to use to complete a task.

```text
                         User
                           │
                           ▼
                  ┌─────────────────┐
                  │   Streamlit UI  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │    AI Agent     │
                  │    Main Loop    │
                  └────────┬────────┘
                           │
                  Tool / Function Calls
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
       Read Files      Write Files    Run Python
            │              │              │
            └──────────────┼──────────────┘
                           ▼
                  Project Workspace
```

The agent can repeatedly inspect, modify, execute, and verify code as it works toward the requested task.

## 🔄 How CodePilot Works

A typical task follows this workflow:

```text
User Request
     ↓
Understand Task
     ↓
Scan Project
     ↓
Read Relevant Files
     ↓
Select Tools
     ↓
Modify Code
     ↓
Run Python / Tests
     ↓
Analyze Results
     ↓
Fix and Retest if Needed
     ↓
Verify Result
```

For example, a user can ask:

> Fix the bug in the calculator project.

CodePilot can then inspect the project, read the relevant files, modify the implementation, execute Python code, analyze the result, and continue iterating when necessary.

## 🔧 Available Tools

### `get_files_info`

Inspects files and directories inside the project workspace.

### `get_file_content`

Reads the contents of a source file so the agent can understand the existing implementation.

### `write_file`

Creates or modifies files inside the allowed project workspace.

### `run_python_file`

Executes a Python file and returns the result to the agent.

Together, these tools allow the model to move beyond text generation and interact directly with a software project.

## 📁 Project Structure

```text
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
│   ├── README.md
│   ├── main.py
│   ├── lorem.txt
│   ├── verify_calc.py
│   ├── tests.py
│   └── pkg/
│       ├── calculator.py
│       ├── render.py
│       └── morelorem.txt
│
├── test_get_files_info.py
├── test_get_file_content.py
├── test_write_file.py
├── test_run_python_file.py
│
├── pyproject.toml
├── uv.lock
└── README.md
```

## 🖥️ Web Interface

CodePilot uses **Streamlit** to provide an interactive browser-based interface.

The interface shows:

* Current agent stage
* Project files
* User requests
* Tool activity
* Agent results
* Verification status

A typical successful task progresses through stages such as:

```text
UNDERSTAND → SCAN → READ → TEST → PROVE
```

## 💻 Local Development

### Requirements

* Python 3.14+
* Git
* `uv`
* OpenAI API access

### Clone the repository

```bash
git clone git@github.com:hiba-hroob/aiagent.git
cd aiagent
```

### Install dependencies

This project uses `pyproject.toml` and `uv.lock`.

```bash
uv sync
```

### Configure environment variables

Create a local `.env` file and provide the required OpenAI API key.

```env
OPENAI_API_KEY=your_api_key_here
```

**Never commit `.env` or API keys to GitHub.**

### Run the application

```bash
uv run streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

## 🚀 Deployment

CodePilot is deployed using **Streamlit Community Cloud**.

The deployed application runs `app.py` as the Streamlit entry point.

```text
GitHub Repository
       ↓
Streamlit Community Cloud
       ↓
Streamlit Application
       ↓
Python AI Agent
       ↓
OpenAI API + Project Tools
```

Secrets such as the OpenAI API key should be stored using the deployment platform's secret management rather than committed to the repository.

## 💡 Example Task

Once CodePilot is running, try:

```text
Inspect the calculator project and tell me what files it contains.
```

Or:

```text
Fix the bug in the calculator project.
```

The agent can inspect the project, read the relevant files, use its tools, execute Python code, and verify its work.

## 🧪 Testing

The repository includes tests for the main project-operation tools.

Run the full test suite:

```bash
uv run pytest
```

Run an individual test file:

```bash
uv run pytest test_get_files_info.py
```

The tests cover functionality such as:

* File and directory inspection
* File content reading
* File writing
* Python file execution

## 🔐 Security Considerations

CodePilot is designed as a learning and experimentation project around AI-powered software engineering.

Potential production improvements include:

* Stronger filesystem isolation
* Sandboxed code execution
* More restrictive tool permissions
* Better resource limits
* Safer handling of untrusted project code
* Improved authentication and authorization
* More robust logging and monitoring

Because the agent can modify files and execute Python code, execution boundaries should be carefully controlled before using a similar architecture in a production environment.

## 🎯 Project Goal

The goal of CodePilot is to explore how Large Language Models can be combined with tools and an execution environment to perform practical software-engineering tasks.

Instead of only generating code, the agent can:

```text
Inspect
   ↓
Understand
   ↓
Read
   ↓
Modify
   ↓
Execute
   ↓
Analyze
   ↓
Verify
```

This creates a foundation for building more capable autonomous coding systems.

## 🚧 Current Limitations

The current version is a functional foundation rather than a production-ready autonomous coding platform.

Areas for improvement include:

* Stronger sandboxing and execution isolation
* More comprehensive agent-level evaluation
* Better planning and verification
* Improved observability
* Safer rollback and change tracking
* More robust error handling
* Support for larger and more complex projects

## 🛣️ Future Improvements

Planned improvements include:

* 🧠 Better task planning
* 🔄 Automated test → fix → retest workflows
* 🔐 Stronger execution isolation
* 📊 Agent evaluation and performance metrics
* 🌳 Git integration and change tracking
* ↩️ Safer rollback mechanisms
* 🖥️ Enhanced agent monitoring
* 🧪 Larger evaluation benchmarks
* 📚 Improved documentation and examples

## 📌 Project Status

**Status: Active Development**

CodePilot currently provides a working AI coding-agent foundation with:

* ✅ AI-powered task execution
* ✅ Tool/function calling
* ✅ Project inspection
* ✅ File reading and writing
* ✅ Python execution
* ✅ Iterative workflows
* ✅ Verification steps
* ✅ Streamlit web interface
* ✅ Live web deployment
* ✅ Automated tool tests

## 👩‍💻 Author

**Hiba Hroob**

GitHub:

https://github.com/hiba-hroob

Repository:

https://github.com/hiba-hroob/aiagent

## 📄 License

This project is currently under active development. License information can be added when the project is prepared for public release.
