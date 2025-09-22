import subprocess
import tempfile
import os
import sys
import shutil
from typing import Dict, Any, Optional

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
                # preexec_fn=_limit_resources if resource is not None else None,  # Disabled due to NumPy issues
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
    _manager: Optional[Any] = None

    @classmethod
    def get_manager(cls):
        """Get or create the Wolfram container manager."""
        if cls._manager is None:
            try:
                from .wolfram_manager import get_wolfram_manager
                cls._manager = get_wolfram_manager()
            except ImportError:
                cls._manager = None
        return cls._manager
    def execute(self, code: str, timeout: int = 10) -> Dict[str, Any]:
        # First, try to use the managed container approach
        manager = self.get_manager()
        if manager is not None:
            # Set credentials from environment if available
            email = os.getenv('WOLFRAM_EMAIL', 'tianyi.phys@gmail.com')
            password = os.getenv('WOLFRAM_PASSWORD', 'Lty@19980822')

            if manager.ensure_ready(email, password):
                result = manager.execute_code(code, timeout)
                return {
                    "role": "tool",
                    "tool": "mathematica_exec",
                    "ok": result["ok"],
                    "out": result["out"],
                    "err": result["err"]
                }

        # Fallback to original implementation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.wl', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            wolfram_bin = shutil.which('wolframscript')
            if wolfram_bin:
                result = subprocess.run(
                    [wolfram_bin, '-file', temp_path],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
            else:
                # Docker fallback
                use_docker = os.getenv('USE_WOLFRAMENGINE_DOCKER', '0') == '1' or bool(
                    os.getenv('WOLFRAMENGINE_DOCKER_IMAGE')
                )
                if not use_docker:
                    raise FileNotFoundError("wolframscript not found. Please install Mathematica or set USE_WOLFRAMENGINE_DOCKER=1.")

                docker = shutil.which('docker')
                if not docker:
                    raise FileNotFoundError("docker not found. Please install Docker to use Wolfram Engine container.")

                image = os.getenv('WOLFRAMENGINE_DOCKER_IMAGE', 'wolframresearch/wolframengine')

                host_userbase_w = os.path.expanduser('~/.Wolfram')
                host_userbase_m = os.path.expanduser('~/.Mathematica')
                host_config = os.path.expanduser('~/.config/Wolfram')
                os.makedirs(host_userbase_w, exist_ok=True)
                os.makedirs(host_userbase_m, exist_ok=True)
                os.makedirs(host_config, exist_ok=True)

                container_userbase = '/home/wolframengine/.Wolfram'

                cmd = [
                    docker, 'run', '--rm',
                    # Mount common user base/license locations for both possible users
                    '-v', f'{host_userbase_w}:/home/wolframengine/.Wolfram',
                    '-v', f'{host_userbase_w}:/root/.Wolfram',
                    '-v', f'{host_userbase_m}:/home/wolframengine/.Mathematica',
                    '-v', f'{host_userbase_m}:/root/.Mathematica',
                    '-v', f'{host_config}:/home/wolframengine/.config/Wolfram',
                    '-v', f'{host_config}:/root/.config/Wolfram',
                    '-e', f'WOLFRAM_USERBASE={container_userbase}',
                    image,
                    'wolframscript', '-code', code,
                ]

                result = subprocess.run(
                    cmd,
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
        except FileNotFoundError as e:
            return {
                "role": "tool",
                "tool": "mathematica_exec",
                "ok": False,
                "out": "",
                "err": str(e)
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
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
