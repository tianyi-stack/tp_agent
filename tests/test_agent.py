import pytest
from tp_agent import TPAgent, PythonExecutor
from tp_agent.llm_interface import MockLLMInterface


def test_python_executor():
    executor = PythonExecutor()
    result = executor.execute("print('OK_TEST')")

    assert result["role"] == "tool"
    assert result["tool"] == "python_exec"
    assert result["ok"] is True
    assert "OK_TEST" in result["out"]


def test_python_executor_error():
    executor = PythonExecutor()
    result = executor.execute("1/0")

    assert result["role"] == "tool"
    assert result["tool"] == "python_exec"
    assert result["ok"] is False
    assert "ZeroDivisionError" in result["err"]


def test_agent_flow():
    llm = MockLLMInterface()

    llm.add_response({
        "role": "llm",
        "tool": "python_exec",
        "code": "x = 2 + 2; print(f'Result: {x}'); print('OK_CALC')",
        "timeout": 5
    })

    llm.add_response({
        "role": "llm",
        "say": "Calculation complete: 2 + 2 = 4",
        "done": True
    })

    agent = TPAgent(llm_interface=llm)
    context = agent.run()

    assert len(context) == 4
    assert context[0]["role"] == "llm"
    assert context[0]["tool"] == "python_exec"
    assert context[1]["role"] == "tool"
    assert context[1]["ok"] is True
    assert "OK_CALC" in context[1]["out"]
    assert context[2]["role"] == "llm"
    assert context[2]["done"] is True


def test_agent_reset():
    agent = TPAgent(llm_interface=MockLLMInterface())
    agent.context = [{"role": "llm", "say": "test"}]
    agent.reset()
    assert len(agent.context) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
