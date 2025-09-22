#!/usr/bin/env python3
import argparse
from tp_agent import TPAgent
from tp_agent.llm_interface import LLMInterface


def main():
    parser = argparse.ArgumentParser(description="Run TP-Agent on a problem text file (.txt/.md).")
    parser.add_argument("--file", type=str, required=True, help="Path to problem file (.txt/.md)")
    parser.add_argument("--rounds", type=int, default=10, help="Max dialogue rounds")
    parser.add_argument("--use-config", action="store_true", help="Use config file for API keys and model")
    args = parser.parse_args()

    llm = LLMInterface(use_config=args.use_config)
    agent = TPAgent(llm_interface=llm)
    context = agent.run_with_problem(problem_path=args.file, max_rounds=args.rounds)

    for msg in context:
        print(f"Role: {msg.get('role')}")
        if 'say' in msg:
            print(f"  Say: {msg['say']}")
        if 'tool' in msg:
            print(f"  Tool: {msg['tool']}")
        if 'out' in msg:
            print(f"  Output: {msg['out']}")
        if 'err' in msg and msg['err']:
            print(f"  Error: {msg['err']}")
        print()


if __name__ == "__main__":
    main()
