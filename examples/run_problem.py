#!/usr/bin/env python3
"""Enhanced version of run_problem.py with save functionality"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from tp_agent import TPAgent
from tp_agent.core.llm_interface import LLMInterface


def save_context(context, problem_file, output_dir="outputs", model_name="unknown"):
    """Save the conversation context to a JSON file"""
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Generate filename based on problem, model, and timestamp
    problem_name = Path(problem_file).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{output_dir}/{problem_name}_{model_name}_{timestamp}.json"

    # Save context with metadata
    output_data = {
        "problem_file": problem_file,
        "timestamp": timestamp,
        "context": context,
        "summary": {
            "total_messages": len(context),
            "llm_messages": sum(1 for msg in context if msg.get("role") == "llm"),
            "tool_executions": sum(1 for msg in context if msg.get("role") == "tool"),
            "successful_executions": sum(1 for msg in context if msg.get("role") == "tool" and msg.get("ok")),
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    return output_file


def save_readable_log(context, problem_file, output_dir="outputs", model_name="unknown"):
    """Save a human-readable log file"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    problem_name = Path(problem_file).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{output_dir}/{problem_name}_{model_name}_{timestamp}.log"

    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"=== TP-Agent Execution Log ===\n")
        f.write(f"Problem: {problem_file}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write("=" * 50 + "\n\n")

        for i, msg in enumerate(context, 1):
            f.write(f"[{i}] Role: {msg.get('role')}\n")

            if 'say' in msg:
                f.write(f"    Say: {msg['say']}\n")

            if 'tool' in msg:
                f.write(f"    Tool: {msg['tool']}\n")
                if 'code' in msg:
                    f.write(f"    Code:\n")
                    for line in msg['code'].split('\n'):
                        f.write(f"        {line}\n")

            if 'out' in msg:
                f.write(f"    Output:\n")
                for line in msg['out'].split('\n'):
                    f.write(f"        {line}\n")

            if 'err' in msg and msg['err']:
                f.write(f"    Error:\n")
                for line in msg['err'].split('\n'):
                    f.write(f"        {line}\n")

            f.write("\n")

        f.write("=" * 50 + "\n")
        f.write(f"Total messages: {len(context)}\n")
        f.write(f"Completed: {'Yes' if any(msg.get('done') for msg in context) else 'No'}\n")

    return log_file


def main():
    parser = argparse.ArgumentParser(description="Run TP-Agent with automatic save functionality")
    parser.add_argument("--file", type=str, required=True, help="Path to problem file (.txt/.md)")
    parser.add_argument("--rounds", type=int, default=10, help="Max dialogue rounds")
    parser.add_argument("--no-save", action="store_true", help="Disable automatic saving to files")
    parser.add_argument("--output-dir", type=str, default="outputs", help="Directory for saved outputs")
    parser.add_argument("--quiet", action="store_true", help="Don't print to console")
    args = parser.parse_args()

    # Run the agent
    llm = LLMInterface()
    agent = TPAgent(llm_interface=llm)
    context = agent.run_with_problem(problem_path=args.file, max_rounds=args.rounds)

    # Print to console unless quiet mode
    if not args.quiet:
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

    # Save outputs by default (unless --no-save is specified)
    if not args.no_save:
        json_file = save_context(context, args.file, args.output_dir, llm.model)
        log_file = save_readable_log(context, args.file, args.output_dir, llm.model)

        print(f"\n=== Files Saved ===")
        print(f"JSON: {json_file}")
        print(f"Log:  {log_file}")

        # Print summary
        summary = {
            "total_messages": len(context),
            "llm_messages": sum(1 for msg in context if msg.get("role") == "llm"),
            "tool_executions": sum(1 for msg in context if msg.get("role") == "tool"),
            "successful": sum(1 for msg in context if msg.get("role") == "tool" and msg.get("ok")),
            "failed": sum(1 for msg in context if msg.get("role") == "tool" and not msg.get("ok")),
            "completed": any(msg.get("done") for msg in context)
        }

        print(f"\n=== Execution Summary ===")
        for key, value in summary.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()