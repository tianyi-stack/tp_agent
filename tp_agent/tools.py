import subprocess
import tempfile
import os
import sys
from typing import Dict, Any

try:
    import resource  # type: ignore
except Exception:  # pragma: no cover - not available on non-Unix
    resource = None  # type: ignore


class BaseExecutor:
    def execute(self, code: str, timeout: int = 10) -> Dict[str, Any]:
        raise NotImplementedError


class PythonExecutor(BaseExecutor):
    def execute(self, code: str, timeout: int = 10) -> Dict[str, Any]:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        def _limit_resources() -> None:
            if resource is None:
                return
            # Best-effort lightweight sandboxing on Unix-like systems
            try:
                # CPU time limit (seconds)
                resource.setrlimit(resource.RLIMIT_CPU, (timeout + 1, timeout + 1))
            except Exception:
                pass
            try:
                # Address space / memory limit (soft cap ~512MB)
                mem_bytes = 512 * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
            except Exception:
                pass

        try:
            cmd = [sys.executable, temp_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                preexec_fn=_limit_resources if resource is not None else None,
            )
            return {
                "role": "tool",
                "tool": "python_exec",
                "ok": result.returncode == 0,
                "out": result.stdout,
                "err": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "role": "tool",
                "tool": "python_exec",
                "ok": False,
                "out": "",
                "err": f"Timeout after {timeout} seconds"
            }
        except Exception as e:
            return {
                "role": "tool",
                "tool": "python_exec",
                "ok": False,
                "out": "",
                "err": str(e)
            }
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class MathematicaExecutor(BaseExecutor):
    def execute(self, code: str, timeout: int = 10) -> Dict[str, Any]:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.wl', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            result = subprocess.run(
                ['wolframscript', '-file', temp_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "role": "tool",
                "tool": "mathematica_exec",
                "ok": result.returncode == 0,
                "out": result.stdout,
                "err": result.stderr
            }
        except FileNotFoundError:
            return {
                "role": "tool",
                "tool": "mathematica_exec",
                "ok": False,
                "out": "",
                "err": "wolframscript not found. Please install Mathematica."
            }
        except subprocess.TimeoutExpired:
            return {
                "role": "tool",
                "tool": "mathematica_exec",
                "ok": False,
                "out": "",
                "err": f"Timeout after {timeout} seconds"
            }
        except Exception as e:
            return {
                "role": "tool",
                "tool": "mathematica_exec",
                "ok": False,
                "out": "",
                "err": str(e)
            }
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
