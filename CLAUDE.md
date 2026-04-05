# CLAUDE.md — Open Interpreter Codebase Guide

This document orients AI assistants working in this repository. Read it before making changes.

---

## Project Overview

**Open Interpreter** lets language models run code locally. The core loop is: user message → LLM decides what code to run → computer executes it → output fed back to LLM → repeat.

- **Package name**: `open-interpreter` v0.4.3
- **Python**: >=3.9, <3.13
- **License**: AGPL
- **CLI entry points**: `i`, `interpreter`, `wtf`, `interpreter-classic`

---

## Repository Structure

```
interpreter/
├── core/
│   ├── core.py                  # OpenInterpreter class (sync)
│   ├── async_core.py            # AsyncInterpreter (server/WebSocket)
│   ├── respond.py               # Main LLM ↔ computer loop
│   ├── llm/
│   │   ├── llm.py               # LiteLLM wrapper + context handling
│   │   ├── run_tool_calling_llm.py
│   │   └── run_text_llm.py
│   ├── computer/
│   │   ├── computer.py          # Computer API coordinator
│   │   ├── terminal/
│   │   │   ├── terminal.py      # Language runtime manager
│   │   │   ├── base_language.py # Abstract base for all languages
│   │   │   ├── subprocess_language.py
│   │   │   ├── jupyter_language.py
│   │   │   └── languages/       # python, shell, js, ruby, r, java, etc.
│   │   ├── mouse/, keyboard/    # Desktop input simulation
│   │   ├── display/             # Screenshots, resolution
│   │   ├── browser/             # Selenium automation
│   │   ├── vision/              # OCR and computer vision
│   │   ├── files/, os/          # Filesystem and OS operations
│   │   └── mail/, sms/, calendar/, contacts/
│   ├── render_message.py
│   ├── default_system_message.py
│   └── utils/                   # Telemetry, truncation, token counting
├── terminal_interface/
│   ├── start_terminal_interface.py  # CLI arg parsing, profile loading
│   ├── terminal_interface.py        # Interactive REPL
│   ├── magic_commands.py            # %verbose, %reset, %undo, %tokens
│   ├── local_setup.py               # First-run setup wizard
│   ├── conversation_navigator.py
│   └── components/, utils/
├── computer_use/
│   ├── loop.py                  # Async computer-use execution loop
│   └── tools/                   # bash, edit, run, computer tools
└── __init__.py                  # Package entry point

tests/
├── test_interpreter.py          # Main test suite (51KB)
└── core/

docs/                            # Markdown docs + translations
scripts/
└── wtf.py                       # "WTF" debug command
outreach-automation/             # Separate sub-project (n8n + AI)
```

---

## Development Setup

```bash
# Install with Poetry
poetry install

# Install with optional extras
poetry install -E server    # FastAPI/WebSocket server
poetry install -E os        # Desktop control (pyautogui, OpenCV)
poetry install -E local     # Local ML models (torch, transformers)
poetry install -E safe      # Semgrep security scanning

# Activate environment
poetry shell
```

---

## Running Tests

```bash
# Run the full test suite
poetry run pytest -s -x -k test_

# Run specific test
poetry run pytest -s -x tests/test_interpreter.py::test_name
```

The CI pipeline (`python-package.yml`) runs on Python 3.10 and 3.12 and requires `OPENAI_API_KEY`.

---

## Code Style

- **Formatter**: Black (target: Python 3.11) — run via pre-commit
- **Import sorting**: isort with black profile
- **Pre-commit**: `.pre-commit-config.yaml` enforces both on commit

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

Naming conventions:
- Classes: `CamelCase`
- Functions/methods: `snake_case`, verb-first (`run_code`, `render_message`)
- Private: `_leading_underscore`

---

## Architecture — Key Concepts

### Message Format (LMC)

All communication between the user, LLM, and computer uses this dict format:

```python
{
  "role": "user" | "assistant" | "computer",
  "type": "message" | "code" | "output" | "image",
  "format": "python" | "shell" | "javascript" | ...,  # for code/image
  "content": "..."
}
```

### Streaming via Generators

`chat()` and `respond()` are generators — they `yield` message chunks as they arrive. This enables real-time terminal output and streaming API responses. Do not convert them to blocking calls unless absolutely necessary.

### OpenInterpreter vs AsyncInterpreter

- `OpenInterpreter` (`core.py`): synchronous, used for CLI and embedded usage
- `AsyncInterpreter` (`async_core.py`): async, used for server mode with WebSocket/HTTP

Both share the same LLM and computer infrastructure.

### Language Runtimes

Languages are registered in `terminal.py` as instances of subclasses of `BaseLanguage`. Two base implementations:

- `SubprocessLanguage`: runs a subprocess, sends code via stdin, reads stdout
- `JupyterLanguage`: uses a Jupyter kernel (persistent kernel for Python)

To add a new language: subclass one of these, implement `run()`, register in `terminal.py`.

### Computer API

`Computer` in `computer/computer.py` coordinates all hardware/OS subsystems. Its `system_message` property generates the docstring that tells the LLM what APIs are available. Each subsystem (e.g., `computer.browser`, `computer.display`) exposes methods that are called by the LLM-generated code.

---

## Configuration and Profiles

Open Interpreter uses YAML profiles stored in `~/.config/open-interpreter/profiles/`. The default profile is `default.yaml`.

Profiles control:
- `model`, `api_key`, `api_base`, `context_window`, `max_tokens`
- `auto_run` (skip confirmation before executing code)
- `safe_mode` (`off`, `ask`, `auto`)
- `system_message`, `custom_instructions`
- `offline`, `os` (enable computer control)

The `--profile` CLI flag selects a profile. Profiles can also be passed programmatically.

---

## Safety Model

By default, the interpreter asks for user confirmation before running each code block. This behavior is controlled by:

- `interpreter.auto_run = True` — skips confirmation (use carefully)
- `interpreter.safe_mode = "ask"` — uses semgrep to scan code and asks about risky patterns
- `interpreter.safe_mode = "auto"` — auto-rejects dangerous code

Do not change safety defaults when making modifications unless explicitly asked.

---

## Server Mode

```bash
interpreter --server           # HTTP + WebSocket at :8000
interpreter --server --port 8080
```

`AsyncInterpreter` handles server connections. The Docker setup exposes port 8000.

WebSocket protocol: clients send LMC-formatted JSON messages and receive streamed LMC chunks back.

---

## Outreach Automation Sub-Project

`/outreach-automation/` is a self-contained sub-project integrating n8n, Airtable, and AI for automated outreach campaigns. It has its own README, config (`config/mcp_config.json`), and web app (`webapp/`). Changes here do not affect the core interpreter.

---

## CI/CD

- **`.github/workflows/python-package.yml`**: Runs `pytest` on push to `main`/`development` and on PRs
- **`.github/workflows/potential-duplicates.yml`**: Auto-labels duplicate issues

---

## Common Tasks

### Add a new language runtime

1. Create `interpreter/core/computer/terminal/languages/yourlang.py`
2. Subclass `SubprocessLanguage` or `BaseLanguage`
3. Implement `run(code)` — yield output chunks
4. Register in `interpreter/core/computer/terminal/terminal.py`

### Modify the system prompt

Edit `interpreter/core/default_system_message.py`. The computer API docs are injected dynamically from `computer.system_message`.

### Add a new computer subsystem

1. Create a class in `interpreter/core/computer/yourmodule/`
2. Import and instantiate it in `computer.py`
3. Add the module to `computer.system_message` so the LLM knows it exists

### Change LLM behavior

The LLM abstraction lives in `interpreter/core/llm/llm.py`. It wraps LiteLLM, so any model supported by LiteLLM can be used. Token counting, context truncation, and vision support are all handled here.

---

## Do Not

- Do not change `auto_run` defaults to `True` in production code
- Do not store API keys in code — use environment variables or profile YAML
- Do not break the LMC message format — all subsystems depend on it
- Do not make `respond()` or `chat()` non-generators without updating all callers
- Do not add Python 3.13+ syntax — the constraint is `<3.13`
