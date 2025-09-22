import json
from typing import Dict, List, Any, Optional
from ..executors.tools import PythonExecutor, MathematicaExecutor
from .llm_interface import LLMInterface
from .problem_io import load_problem
from ..utils.prompts import get_system_prompt
from ..utils.config import load_config, get_agent_settings


class TPAgent:
    def __init__(self, llm_interface: Optional[LLMInterface] = None, config: Optional[Dict[str, Any]] = None):
        self.config = config or load_config()
        self.agent_settings = get_agent_settings(self.config)

        self.llm = llm_interface or LLMInterface(config_path=None)

        # Initialize tools with configured timeouts
        python_timeout = self.agent_settings.get('python_timeout', 10)
        mathematica_timeout = self.agent_settings.get('mathematica_timeout', 10)

        self.tools = {
            "python_exec": PythonExecutor(),
            "mathematica_exec": MathematicaExecutor()
        }
        self.default_timeout = self.agent_settings.get('default_timeout', 10)
        self.context: List[Dict[str, Any]] = []
        self.system_prompt = get_system_prompt()

    def run(self, initial_context: Optional[List[Dict]] = None, max_rounds: int = 10) -> List[Dict]:
        if initial_context:
            self.context = initial_context

        for round_num in range(max_rounds):
            input_json = {
                "sys": self.system_prompt,
                "ctx": self.context
            }

            llm_response = self.llm.query(input_json)

            if not isinstance(llm_response, dict) or "role" not in llm_response:
                raise ValueError(f"Invalid LLM response: {llm_response}")

            self.context.append(llm_response)

            if "tool" in llm_response:
                tool_name = llm_response["tool"]
                if tool_name in self.tools:
                    code = llm_response.get("code", "")
                    timeout = llm_response.get("timeout", self.default_timeout)

                    tool_result = self.tools[tool_name].execute(code, timeout)
                    self.context.append(tool_result)

            if llm_response.get("done", False):
                break

        return self.context

    def reset(self):
        self.context = []

    def run_with_problem(
        self,
        problem_path: str,
        max_rounds: int = 10,
    ) -> List[Dict]:
        """
        Convenience wrapper to load a problem from file or raw text,
        convert it into initial context, and execute the agent loop.
        """
        initial_ctx = load_problem(problem_path)
        return self.run(initial_context=initial_ctx, max_rounds=max_rounds)


# Keep alias for backward compatibility
AgentHost = TPAgent