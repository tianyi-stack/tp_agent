import json
from typing import Dict, List, Any, Optional
from ..executors.tools import PythonExecutor, MathematicaExecutor
from .llm_interface import LLMInterface
from .problem_io import load_problem
from ..utils.prompts import get_system_prompt


class TPAgent:
    def __init__(self, llm_interface: Optional[LLMInterface] = None):
        self.llm = llm_interface or LLMInterface()
        self.tools = {
            "python_exec": PythonExecutor(),
            "mathematica_exec": MathematicaExecutor()
        }
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
                    timeout = llm_response.get("timeout", 10)

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