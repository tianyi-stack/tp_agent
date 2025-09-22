import json
import os
from typing import Any, Dict, List


def _wrap_text_as_context(text: str) -> List[Dict[str, Any]]:
    text = text.strip()
    if not text:
        return []
    return [{"role": "llm", "say": f"Problem: {text}"}]


def load_problem(path: str) -> List[Dict[str, Any]]:
    """
    Load a physics problem from a text file and convert it
    into the agent's initial context (ctx list).

    Requirements: path must point to a .txt or .md file.
    """
    if not path:
        raise ValueError("Problem path is required and must be a text/markdown file.")

    if not os.path.exists(path):
        raise FileNotFoundError(f"Problem file not found: {path}")

    _, ext = os.path.splitext(path.lower())
    if ext not in (".txt", ".md"):
        raise ValueError("Problem file must be .txt or .md")

    with open(path, "r", encoding="utf-8") as f:
        return _wrap_text_as_context(f.read())
