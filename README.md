# TP-Agent: Theoretical Physics Agent

Minimal reasoning-first agent for solving theoretical physics problems using Python and Mathematica.

## Features
- JSON-only communication protocol
- Python and Mathematica tool execution
- Minimal code, maximum efficiency
- Built for physics problem solving

## Quick Start
```bash
pip install -e .
export OPENAI_API_KEY="your-key"
python examples/sho_example.py
```

See [CLAUDE.md](CLAUDE.md) for detailed documentation.

## Customizing the System Prompt
- The agent loads its system prompt from `tp_agent/system_prompt.txt` (packaged).
- To override without editing the package, set env var `TP_AGENT_SYSTEM_PROMPT_PATH` to a custom file path.
- Loader is in `tp_agent/prompts.py` (`get_system_prompt`).

## Problem Input
- The problem must be provided via a text file (.txt or .md).
- Python usage: `agent.run_with_problem(problem_path="problem.md")`
- Helper used: `tp_agent/problem_io.py:load_problem(path)`

## API Keys and Real LLM
- Put your API keys and defaults in a JSON config file.
- Example: copy `tp_agent_config.example.json` to one of the supported locations and fill values:
  - `./tp_agent_config.json`
  - `./config/tp_agent_config.json`
  - `~/.config/tp_agent/config.json`
  - Or set `TP_AGENT_CONFIG=/absolute/path/to/your_config.json`

Example content:
```
{
  "providers": {
    "openai": {
      "api_key": "sk-...",
      "base_url": "https://api.openai.com/v1",
      "model": "gpt-4o-mini"
    }
  },
  "default_provider": "openai"
}
```

`LLMInterface` loads config by default. Explicit constructor args override config, which override env vars.

Quick CLI example:
```
python examples/run_problem.py --file problem.md --use-config
```

Sample problems included:
- `examples/problem_sho.md`
- `examples/problem_quantum.md`

Examples:
```
python examples/run_problem.py --file examples/problem_sho.md --use-config
python examples/run_problem.py --file examples/problem_quantum.md --use-config
```
