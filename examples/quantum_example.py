#!/usr/bin/env python3
from tp_agent import TPAgent
from tp_agent.llm_interface import MockLLMInterface


def run_quantum_example():
    llm = MockLLMInterface()

    llm.add_response({
        "role": "llm",
        "say": "Let me verify the commutation relation [x, p] = iℏ",
        "tool": "python_exec",
        "code": """import numpy as np
from scipy.linalg import expm

hbar = 1.0
n = 10
a = np.diag(np.sqrt(np.arange(1, n)), k=1)
a_dag = np.diag(np.sqrt(np.arange(1, n)), k=-1)

x = np.sqrt(hbar/2) * (a + a_dag)
p = 1j * np.sqrt(hbar/2) * (a_dag - a)

commutator = x @ p - p @ x
expected = 1j * hbar * np.eye(n)

diff = np.linalg.norm(commutator - expected)
print(f"Commutator difference from iℏ: {diff:.10f}")
assert diff < 1e-10
print('OK_QUANTUM')""",
        "timeout": 10
    })

    llm.add_response({
        "role": "llm",
        "say": "Commutation relation [x, p] = iℏ verified numerically.",
        "done": True
    })

    agent = TPAgent(llm_interface=llm)
    context = agent.run()

    for msg in context:
        print(f"Role: {msg['role']}")
        if 'say' in msg:
            print(f"  Say: {msg['say']}")
        if 'tool' in msg:
            print(f"  Tool: {msg['tool']}")
        if 'out' in msg:
            print(f"  Output: {msg['out']}")
        print()


if __name__ == "__main__":
    run_quantum_example()