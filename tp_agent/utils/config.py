import json
import os
from typing import Any, Dict, Optional


DEFAULT_CONFIG_FILES = [
    "tp_agent_config.json",
    os.path.join("config", "tp_agent_config.json"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "tp_agent_config.json"),
    os.path.expanduser(os.path.join("~", ".config", "tp_agent", "config.json")),
]

DEFAULT_API_KEY_FILES = [
    "api_key.json",
    os.path.join("config", "api_key.json"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "api_key.json"),
    os.path.expanduser(os.path.join("~", ".config", "tp_agent", "api_key.json")),
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


def load_api_key() -> Optional[str]:
    """
    Load API key from separate file or environment variable.
    Precedence: $OPENAI_API_KEY > api_key.json locations.
    """
    # Check environment variable first
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return env_key

    # Check API key files
    for p in DEFAULT_API_KEY_FILES:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "api_key" in data:
                        return data["api_key"]
            except Exception:
                continue

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
    Extract OpenAI settings from config with defaults.
    API key is loaded from separate file or environment variable.
    """
    cfg = config or {}
    providers = cfg.get("providers", {}) if isinstance(cfg, dict) else {}
    openai_cfg = providers.get("openai", {}) if isinstance(providers, dict) else {}

    # Load API key from separate file or env var
    api_key = load_api_key() or ""

    base_url = (
        openai_cfg.get("base_url") if isinstance(openai_cfg, dict)
        else "https://api.openai.com/v1"
    )
    model = (
        openai_cfg.get("model") if isinstance(openai_cfg, dict)
        else "gpt-4o-mini"
    )

    return {"api_key": api_key, "base_url": base_url, "model": model}

