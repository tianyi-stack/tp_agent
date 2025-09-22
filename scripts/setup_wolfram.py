#!/usr/bin/env python3
"""
Setup and manage Wolfram Engine for tp_agent

This script provides a simple interface to setup, test, and manage
the Wolfram Engine container for the tp_agent project.
"""

import os
import sys
from pathlib import Path

# Add tp_agent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tp_agent.executors.wolfram_manager import WolframContainerManager


def load_env():
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key] = value


def main():
    """Main setup function."""
    print("Wolfram Engine Setup for tp_agent")
    print("=" * 50)

    # Load environment
    load_env()

    # Get credentials
    email = os.getenv("WOLFRAM_EMAIL")
    password = os.getenv("WOLFRAM_PASSWORD")

    if not email or not password:
        print("\n⚠️  Credentials not found in .env file")
        print("Please create a .env file with:")
        print("  WOLFRAM_EMAIL=your-email@example.com")
        print("  WOLFRAM_PASSWORD=your-password")
        return 1

    print(f"\nUsing Wolfram ID: {email}")

    # Create manager
    manager = WolframContainerManager()

    # Setup container
    print("\n🚀 Setting up Wolfram Engine container...")
    if manager.ensure_ready(email, password):
        print("✅ Container is ready and activated!")

        # Test execution
        print("\n🧪 Running test calculations...")
        tests = [
            ("2 + 2", "Basic arithmetic"),
            ("N[Pi, 20]", "High precision Pi"),
            ("Integrate[x^2, x]", "Symbolic integration"),
        ]

        for code, desc in tests:
            print(f"\n  {desc}: {code}")
            result = manager.execute_code(code)
            if result["ok"]:
                print(f"  → {result['out'].strip()}")
            else:
                print(f"  ❌ {result['err'].strip()}")

        print("\n✅ Wolfram Engine is fully configured!")
        print("\nYou can now use MathematicaExecutor in your code:")
        print("  from tp_agent.tools import MathematicaExecutor")
        print("  executor = MathematicaExecutor()")
        print("  result = executor.execute('2 + 2')")

        return 0
    else:
        print("❌ Failed to setup container")
        return 1


if __name__ == "__main__":
    sys.exit(main())