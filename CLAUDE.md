# CLAUDE.md
- 如果在本次运行中你新写了测试脚本，请在运行结束后删掉这些测试脚本。
- 每次修改该仓库的代码，都请对应地更新这个md文件。
- 不需要有recent change这个部分，只需要介绍目前最新的代码库状态

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

## Project Structure

```
tp_agent/
├── core/
│   ├── host.py           # Main TPAgent class
│   ├── llm_interface.py  # OpenAI API interface
│   └── problem_io.py      # Problem file loading
├── executors/
│   ├── tools.py           # Python and Mathematica executors
│   └── wolfram_manager.py # Wolfram Engine Docker management
├── utils/
│   ├── config.py          # Configuration loading
│   └── prompts.py         # System prompt management
config/
├── tp_agent_config.json  # API configuration
└── system_prompt.txt      # Agent system prompt
examples/
├── run_problem.py         # Main runner with save functionality
├── problem_sho.md         # Simple harmonic oscillator example
└── problem_quantum.md     # Quantum mechanics example
scripts/
└── setup_wolfram.py       # Wolfram Engine Docker setup
tests/
└── test_agent.py          # Unit tests
```

## Commands

### Installation
```bash
# Install dependencies
pip install -e ".[dev]"
```

### Running the Agent
```bash
# Basic usage - run a problem file with save functionality
python examples/run_problem.py --file path/to/problem.txt --rounds 10

# Save outputs to JSON and log files
python examples/run_problem.py --file path/to/problem.txt --save --output-dir outputs

# Quiet mode (no console output)
python examples/run_problem.py --file path/to/problem.txt --save --quiet
```

### Development
```bash
# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_agent.py::test_python_executor -v

# Format code
black tp_agent/ tests/ examples/

# Type checking
mypy tp_agent/
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

### API Configuration
Create `config/tp_agent_config.json`:
```json
{
  "api_key": "your-openai-api-key",
  "api_base": "https://api.openai.com/v1",
  "model": "gpt-4o-mini",
  "max_tokens": 4096,
  "temperature": 0.1
}
```

### Environment Variables
- `OPENAI_API_KEY`: Override API key
- `USE_WOLFRAMENGINE_DOCKER`: Enable Docker for Wolfram
- `WOLFRAMENGINE_DOCKER_IMAGE`: Wolfram Docker image name
- `WOLFRAM_EMAIL`, `WOLFRAM_PASSWORD`: Wolfram credentials (for .env file)

## Features

### Problem Execution
- Load problems from text/markdown files
- Execute Python code with SymPy, NumPy, SciPy
- Execute Mathematica/Wolfram code
- Automatic timeout handling
- Structured JSON communication with LLM

### Save Functionality
The `run_problem.py` script includes built-in save features:
- **JSON output**: Complete context with metadata
- **Log file**: Human-readable execution log
- **Summary statistics**: Message counts, success rates
- Output files use timestamp-based naming

### Testing
Tests use `MockLLMInterface` to simulate LLM responses without API calls. The test suite covers:
- Executor functionality (Python/Mathematica)
- Agent flow control
- Error handling
- Timeout management

## Known Issues

1. **NumPy in subprocess**: Resource limits can cause NumPy import failures due to threading issues (OpenBLAS). Currently disabled in executors/tools.py.
2. **Wolfram Docker**: Requires proper Docker setup and Wolfram Engine image.
3. **API key configuration**: Ensure valid API keys in config/tp_agent_config.json.