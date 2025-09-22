import json
import os
from typing import Any, Dict, Optional


DEFAULT_CONFIG_FILES = [
    "tp_agent_config.json",
    os.path.join("config", "tp_agent_config.json"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "tp_agent_config.json"),
    os.path.expanduser(os.path.join("~", ".config", "tp_agent", "config.json")),
]


def find_config_path(explicit_path: Optional[str] = None) -> Optional[str]:
    """
    Resolve a config file path.
    Precedence: explicit_path > $TP_AGENT_CONFIG > default locations.
    Returns None if nothing is found.
    """
    if explicit_path:
        return explicit_path if os.path.exists(explicit_path) else None

    env_path = os.getenv("TP_AGENT_CONFIG")
    if env_path and os.path.exists(env_path):
        return env_path

    for p in DEFAULT_CONFIG_FILES:
        if os.path.exists(p):
            return p

    return None


def load_config(path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration JSON. Returns empty dict if not found or invalid.
    """
    cfg_path = find_config_path(path)
    if not cfg_path:
        return {}
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_openai_settings(config: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """
    Extract OpenAI settings from config/env with sane defaults.
    Priority: config > env > defaults.
    """
    cfg = config or {}
    providers = cfg.get("providers", {}) if isinstance(cfg, dict) else {}
    openai_cfg = providers.get("openai", {}) if isinstance(providers, dict) else {}

    api_key = (
        (openai_cfg.get("api_key") if isinstance(openai_cfg, dict) else None)
        or os.getenv("OPENAI_API_KEY")
        or ""
    )
    base_url = (
        (openai_cfg.get("base_url") if isinstance(openai_cfg, dict) else None)
        or os.getenv("OPENAI_BASE_URL")
        or "https://api.openai.com/v1"
    )
    model = (
        (openai_cfg.get("model") if isinstance(openai_cfg, dict) else None)
        or os.getenv("OPENAI_MODEL")
        or "gpt-4o-mini"
    )

    return {"api_key": api_key, "base_url": base_url, "model": model}

