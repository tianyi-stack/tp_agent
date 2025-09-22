"""
Wolfram Engine Container Manager

This module provides an elegant solution for managing Wolfram Engine containers
with persistent activation and automatic lifecycle management.
"""

import subprocess
import os
import json
import time
from typing import Optional, Dict, Any
from pathlib import Path


class WolframContainerManager:
    """Manages a persistent Wolfram Engine container with activation."""

    CONTAINER_NAME = "tp-wolfram-engine"
    IMAGE_NAME = "wolframresearch/wolframengine"
    STATE_FILE = Path.home() / ".tp_agent" / "wolfram_state.json"

    def __init__(self):
        """Initialize the Wolfram container manager."""
        self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        self._load_state()

    def _load_state(self) -> None:
        """Load the container state from file."""
        if self.STATE_FILE.exists():
            with open(self.STATE_FILE, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {"activated": False, "container_id": None}

    def _save_state(self) -> None:
        """Save the container state to file."""
        with open(self.STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)

    def _container_exists(self) -> bool:
        """Check if the container exists."""
        try:
            result = subprocess.run(
                ["docker", "inspect", self.CONTAINER_NAME],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False

    def _container_running(self) -> bool:
        """Check if the container is running."""
        try:
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Running}}", self.CONTAINER_NAME],
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and result.stdout.strip() == "true"
        except:
            return False

    def _create_container(self) -> bool:
        """Create a new container."""
        try:
            # Remove any existing container with the same name
            subprocess.run(
                ["docker", "rm", "-f", self.CONTAINER_NAME],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Create new container with persistent storage
            result = subprocess.run(
                [
                    "docker", "run", "-d",
                    "--name", self.CONTAINER_NAME,
                    "-v", f"{Path.home()}/.wolfram_engine:/root/.Wolfram",
                    "-v", f"{Path.home()}/.wolfram_engine:/root/.Mathematica",
                    self.IMAGE_NAME,
                    "tail", "-f", "/dev/null"
                ],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                self.state["container_id"] = result.stdout.strip()
                self._save_state()
                return True
            return False
        except Exception as e:
            print(f"Error creating container: {e}")
            return False

    def _activate_container(self, email: str, password: str) -> bool:
        """Activate Wolfram Engine in the container."""
        try:
            activation_input = f"{email}\n{password}\n"
            result = subprocess.run(
                ["docker", "exec", "-i", self.CONTAINER_NAME, "wolframscript", "-activate"],
                input=activation_input,
                text=True,
                capture_output=True,
                timeout=60
            )

            if "successfully" in result.stdout.lower() or "activated" in result.stdout.lower():
                self.state["activated"] = True
                self._save_state()
                return True
            return False
        except Exception as e:
            print(f"Error activating container: {e}")
            return False

    def _test_container(self) -> bool:
        """Test if the container can execute Wolfram code."""
        try:
            result = subprocess.run(
                ["docker", "exec", self.CONTAINER_NAME, "wolframscript", "-code", "2+2"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0 and "4" in result.stdout
        except:
            return False

    def ensure_ready(self, email: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        Ensure the container is ready to execute Wolfram code.

        Args:
            email: Wolfram ID email (required for first-time activation)
            password: Wolfram ID password (required for first-time activation)

        Returns:
            True if container is ready, False otherwise
        """
        # Check if container exists and is running
        if not self._container_exists():
            print("Creating Wolfram Engine container...")
            if not self._create_container():
                return False
            time.sleep(2)

        if not self._container_running():
            print("Starting Wolfram Engine container...")
            subprocess.run(["docker", "start", self.CONTAINER_NAME], capture_output=True)
            time.sleep(2)

        # Test if already activated
        if self._test_container():
            self.state["activated"] = True
            self._save_state()
            return True

        # Need activation
        if not self.state.get("activated", False):
            if not email or not password:
                # Try to get credentials from environment
                email = email or os.getenv("WOLFRAM_EMAIL")
                password = password or os.getenv("WOLFRAM_PASSWORD")

                if not email or not password:
                    print("Wolfram Engine requires activation.")
                    print("Please provide credentials via environment variables:")
                    print("  export WOLFRAM_EMAIL='your-email@example.com'")
                    print("  export WOLFRAM_PASSWORD='your-password'")
                    return False

            print(f"Activating Wolfram Engine for {email}...")
            if not self._activate_container(email, password):
                print("Activation failed. Please check your credentials.")
                return False

            # Verify activation
            if not self._test_container():
                print("Activation completed but verification failed.")
                return False

        return True

    def execute_code(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Execute Wolfram code in the container.

        Args:
            code: Wolfram Language code to execute
            timeout: Maximum execution time in seconds

        Returns:
            Dictionary with execution results
        """
        if not self.ensure_ready():
            return {
                "ok": False,
                "out": "",
                "err": "Container not ready. Please ensure activation."
            }

        try:
            result = subprocess.run(
                ["docker", "exec", self.CONTAINER_NAME, "wolframscript", "-code", code],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "ok": result.returncode == 0,
                "out": result.stdout,
                "err": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "out": "",
                "err": f"Timeout after {timeout} seconds"
            }
        except Exception as e:
            return {
                "ok": False,
                "out": "",
                "err": str(e)
            }

    def cleanup(self) -> None:
        """Stop and remove the container."""
        try:
            subprocess.run(
                ["docker", "stop", self.CONTAINER_NAME],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            subprocess.run(
                ["docker", "rm", self.CONTAINER_NAME],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.state = {"activated": False, "container_id": None}
            self._save_state()
        except:
            pass


# Global instance for singleton pattern
_manager_instance: Optional[WolframContainerManager] = None


def get_wolfram_manager() -> WolframContainerManager:
    """Get or create the global Wolfram container manager instance."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = WolframContainerManager()
    return _manager_instance