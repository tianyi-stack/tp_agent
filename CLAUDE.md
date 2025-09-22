# CLAUDE.md
- 如果在本次运行中你新写了测试脚本，请在运行结束后删掉这些测试脚本。
- 每次修改该仓库的代码，都请对应地更新这个md文件。

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TP-Agent is a reasoning-first agent for theoretical physics problems. It orchestrates physics computations through a minimal LLM interface that can execute Python (SymPy, NumPy, SciPy) and Mathematica/Wolfram code.

## Architecture

The agent follows a simple request-response loop:
1. **TPAgent** (core/host.py) manages the conversation context and tool execution
2. **LLMInterface** (core/llm_interface.py) handles OpenAI-compatible API calls with JSON mode
3. **Executors** (executors/tools.py) provide sandboxed Python and Mathematica execution
4. Problems are loaded from text/markdown files and converted to initial context

Key design: The LLM returns structured JSON with fields like `role`, `say`, `tool`, `code`, `timeout`, `done`. When `tool` is specified, the corresponding executor runs the code and appends results to context.

## Commands

### Development
```bash
# Install dependencies (including dev dependencies)
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run a specific test
pytest tests/test_agent.py::test_python_executor -v

# Format code
black tp_agent/ tests/ examples/

# Type checking
mypy tp_agent/
```

### Running the Agent
```bash
# Run on a problem file
python examples/run_problem.py --file path/to/problem.txt --rounds 10

# Use config file for API credentials
python examples/run_problem.py --file path/to/problem.txt --use-config

# Run with save functionality (saves JSON and log files)
python examples/run_problem_with_save.py --file path/to/problem.txt --save --output-dir outputs

# Run example scripts
python examples/sho_example.py
```

### Wolfram/Mathematica Setup
```bash
# Setup Wolfram Engine container (if using Docker)
python scripts/setup_wolfram.py

# Or set environment variables for Docker usage
export USE_WOLFRAMENGINE_DOCKER=1
export WOLFRAMENGINE_DOCKER_IMAGE=wolframresearch/wolframengine
```

## Configuration

API credentials can be configured in:
- **config/tp_agent_config.json** - OpenAI API settings
- **.env** file - Wolfram credentials (WOLFRAM_EMAIL, WOLFRAM_PASSWORD)
- Environment variables - Override any setting

## Testing Approach

Tests use `MockLLMInterface` to simulate LLM responses without API calls. The test suite focuses on:
- Executor functionality (Python/Mathematica code execution)
- Agent flow control (context management, tool dispatch)
- Error handling (timeouts, execution failures)

## Recent Changes

### Import Fixes
- Fixed imports in `tp_agent/utils/__init__.py` to export `load_config`, `get_openai_settings`, `get_system_prompt`
- Fixed imports in `tp_agent/core/__init__.py` to remove non-existent `save_solution`
- Fixed import path in `examples/run_problem.py` from `tp_agent.llm_interface` to `tp_agent.core.llm_interface`

### Executor Updates
- Temporarily disabled resource limits in `PythonExecutor` (line 48 in tools.py) to fix NumPy import issues in subprocess

### New Features
- Added `examples/run_problem_with_save.py` with functionality to save execution logs as JSON and human-readable log files
- Outputs saved to `outputs/` directory with timestamp-based filenames

## Known Issues

1. **NumPy in subprocess**: Resource limits can cause NumPy import failures due to threading issues (OpenBLAS). Currently disabled.
2. **Finite dimension effects**: Quantum commutator verification requires larger dimensions (n≥20) and checking bulk regions to avoid boundary effects.
3. **API key configuration**: Ensure API keys in config/tp_agent_config.json are valid and have proper format.