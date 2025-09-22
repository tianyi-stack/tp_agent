#!/usr/bin/env python3
from tp_agent import TPAgent
from tp_agent.llm_interface import MockLLMInterface


def run_sho_example():
    llm = MockLLMInterface()

    llm.add_response({
        "role": "llm",
        "tool": "python_exec",
        "code": """from sympy import symbols, Function, diff
t = symbols('t')
x = Function('x')(t)
L = 0.5*diff(x,t)**2 - 0.5*x**2
EL = diff(diff(L, diff(x,t)), t) - diff(L, x)
simplified = EL.simplify()
print(f"Euler-Lagrange equation: {simplified}")
assert simplified == diff(x,t,2) + x
print('OK_EL')""",
        "timeout": 10
    })

    llm.add_response({
        "role": "llm",
        "say": "EL verified: ẍ + x = 0 for the simple harmonic oscillator.",
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
    run_sho_example()