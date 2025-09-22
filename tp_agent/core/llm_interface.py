import json
import os
from typing import Dict, Any, Optional, List, Tuple

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
        config_path: Optional[str] = None,
    ):
        """
        A minimal OpenAI-compatible interface that returns a single JSON object.

        - Uses the Responses API for maximum model compatibility (gpt-5, o-series, gpt-4o).
        - httpx is optional; without it, the interface returns a graceful error.
        - Defaults to a modern, JSON-capable model name.
    """
        cfg = load_config(config_path)
        defaults = get_openai_settings(cfg)

        self.api_key = api_key or defaults.get("api_key", "")
        self.model = model or defaults.get("model", "gpt-4o-mini")
        self.base_url = base_url or defaults.get("base_url", "https://api.openai.com/v1")
        self.timeout_sec = timeout_sec
        self.client = httpx.Client(timeout=timeout_sec) if httpx is not None else None
        # Keep a reference to provider-specific raw config for optional parameters
        try:
            providers = cfg.get("providers", {}) if isinstance(cfg, dict) else {}
            self._openai_cfg = providers.get("openai", {}) if isinstance(providers, dict) else {}
        except Exception:
            self._openai_cfg = {}

    def query(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Build inputs for Responses API
        instructions, input_items = self._format_responses_input(input_data)

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

        # Always use Responses API
        resp_payload: Dict[str, Any] = {
            "model": self.model,
            "instructions": instructions,
            "input": input_items,
            # Request structured JSON output
            "text": {"format": {"type": "json_object"}},
        }

        # Optional: temperature from config (only include when supported by model)
        try:
            temp = self._openai_cfg.get("temperature")
            if (
                (isinstance(temp, (int, float)))
                and self._model_supports_temperature(self.model)
            ):
                resp_payload["temperature"] = float(temp)
        except Exception:
            pass

        # Optional: max_output_tokens from config
        try:
            mot = self._openai_cfg.get("max_output_tokens")
            if isinstance(mot, int) and mot > 0:
                resp_payload["max_output_tokens"] = mot
        except Exception:
            pass

        # Optional: reasoning parameters (gpt-5 and o-series models only)
        try:
            if self._model_supports_reasoning(self.model):
                reasoning_cfg = self._openai_cfg.get("reasoning")
                if isinstance(reasoning_cfg, dict) and reasoning_cfg:
                    resp_payload["reasoning"] = reasoning_cfg
        except Exception:
            pass

        try:
            response = self.client.post(
                f"{self.base_url}/responses",
                headers=headers,
                json=resp_payload,
            )
            response.raise_for_status()

            result = response.json()
            content_text = self._extract_output_text_from_responses(result)
            return json.loads(content_text)

        except json.JSONDecodeError as e:
            return {
                "role": "llm",
                "say": f"Error parsing LLM response: {str(e)}",
                "done": True
            }
        except Exception as e:
            # Include server response body when available for easier debugging
            body = ""
            try:
                if hasattr(e, "response") and e.response is not None:
                    body = f"\nResponse body: {e.response.text}"
            except Exception:
                pass
            return {
                "role": "llm",
                "say": f"Error communicating with LLM: {str(e)}{body}",
                "done": True
            }

    def _format_responses_input(self, input_data: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
        sys_prompt = input_data.get("sys", "")
        context = input_data.get("ctx", [])

        user_text = (
            "Context as JSON follows. Reply with a single JSON object "
            "using only fields: role, say, tool, code, timeout, done.\n\n"
            + json.dumps(context, ensure_ascii=False, indent=2)
        )

        input_items: List[Dict[str, Any]] = [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": user_text}
                ],
            }
        ]
        return sys_prompt, input_items

    def _model_supports_reasoning(self, model: str) -> bool:
        m = (model or "").strip().lower()
        if not m:
            return False
        # gpt-5 family
        if m.startswith("gpt-5"):
            return True
        # o-series models (e.g., o1, o3, o4, o4-mini, etc.)
        if m.startswith("o"):
            return True
        return False

    def _extract_output_text_from_responses(self, result: Dict[str, Any]) -> str:
        # Try the SDK-like convenience property if present
        if isinstance(result, dict) and isinstance(result.get("output_text"), str):
            return result["output_text"]

        # Raw extraction from output array
        output = result.get("output") if isinstance(result, dict) else None
        if isinstance(output, list):
            for item in output:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "message":
                    content_list = item.get("content")
                    if isinstance(content_list, list):
                        for content in content_list:
                            if (
                                isinstance(content, dict)
                                and content.get("type") == "output_text"
                                and isinstance(content.get("text"), str)
                            ):
                                return content["text"]

        # If we cannot find a text block, fall back to the entire JSON string
        return json.dumps(result, ensure_ascii=False)

    def _model_supports_temperature(self, model: str) -> bool:
        m = (model or "").strip().lower()
        if not m:
            return False
        # Known families that DO NOT support temperature in Responses API
        if m.startswith("o"):
            return False
        if m.startswith("gpt-5"):
            return False
        # Most chat models (gpt-4o, gpt-4, gpt-3.5) support temperature
        return True

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
