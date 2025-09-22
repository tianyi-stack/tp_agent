import os
import pkgutil
from typing import Optional


def get_system_prompt(path: Optional[str] = None) -> str:
    """
    Load the system prompt from a file.

    Order of precedence:
    1) Explicit path arg
    2) Env var TP_AGENT_SYSTEM_PROMPT_PATH
    3) Packaged default: tp_agent/system_prompt.txt
    """
    env_path = path or os.getenv("TP_AGENT_SYSTEM_PROMPT_PATH")
    if env_path and os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            return f.read()

    # Try config directory
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "system_prompt.txt")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return f.read()

    data = pkgutil.get_data("tp_agent", "system_prompt.txt")
    if data is not None:
        return data.decode("utf-8")

    # Fallback minimal prompt
    return (
        "You are a reasoning-first assistant. Output JSON only. "
        "If you need a tool, set tool/code fields; otherwise provide `say` and `done`."
    )

