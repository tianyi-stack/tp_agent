import json
import os
from typing import Dict, Any, Optional, List

try:  # Lazy/optional import to allow tests without httpx installed
    import httpx  # type: ignore
except Exception:  # pragma: no cover - handled at runtime
    httpx = None  # type: ignore


from ..utils.config import load_config, get_openai_settings


class LLMInterface:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_sec: int = 30,
        use_config: bool = True,
        config_path: Optional[str] = None,
    ):
        """
        A minimal OpenAI-compatible chat interface that returns a single JSON object.

        - httpx is optional; without it, the interface returns a graceful error.
        - Defaults to a modern, JSON-capable model name.
        - Uses JSON mode via response_format={"type":"json_object"}.
        """
        cfg = load_config(config_path) if use_config else {}
        defaults = get_openai_settings(cfg)

        self.api_key = api_key or defaults.get("api_key", os.getenv("OPENAI_API_KEY", ""))
        self.model = (model or defaults.get("model") or "gpt-4o-mini")
        self.base_url = base_url or defaults.get("base_url") or "https://api.openai.com/v1"
        self.timeout_sec = timeout_sec
        self.client = httpx.Client(timeout=timeout_sec) if httpx is not None else None

    def query(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        messages = self._format_messages(input_data)

        if self.client is None:
            return {
                "role": "llm",
                "say": "HTTP client not available. Install httpx to use real LLM.",
                "done": True,
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

        try:
            response = self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return json.loads(content)

        except json.JSONDecodeError as e:
            return {
                "role": "llm",
                "say": f"Error parsing LLM response: {str(e)}",
                "done": True
            }
        except Exception as e:
            return {
                "role": "llm",
                "say": f"Error communicating with LLM: {str(e)}",
                "done": True
            }

    def _format_messages(self, input_data: Dict[str, Any]) -> List[Dict[str, str]]:
        sys_prompt = input_data.get("sys", "")
        context = input_data.get("ctx", [])

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": sys_prompt},
            {
                "role": "user",
                "content": (
                    "Context as JSON follows. Reply with a single JSON object "
                    "using only fields: role, say, tool, code, timeout, done.\n\n"
                    + json.dumps(context, ensure_ascii=False, indent=2)
                ),
            },
        ]
        return messages

    def __del__(self):
        if hasattr(self, 'client') and self.client is not None:
            try:
                self.client.close()
            except Exception:
                pass


class MockLLMInterface(LLMInterface):
    def __init__(self):
        super().__init__()
        self.responses = []
        self.current = 0

    def add_response(self, response: Dict[str, Any]):
        self.responses.append(response)

    def query(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if self.current < len(self.responses):
            response = self.responses[self.current]
            self.current += 1
            return response
        return {"role": "llm", "say": "No more responses", "done": True}
