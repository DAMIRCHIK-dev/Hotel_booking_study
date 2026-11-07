"""P02 Lab · Parent process: spawns child.py, waits for completion, and reports its exit code."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    here = Path(__file__).resolve().parent
    child_path = here / "child.py"
    print(f"[parent] PID={os.getpid()} starting child: {child_path.name}", flush=True)
    child = subprocess.Popen([sys.executable, "-u", str(child_path)], cwd=str(here))
    print(f"[parent] Spawned child PID={child.pid}; waiting for child to finish...", flush=True)
    exit_code = child.wait()
    print(f"Child exit code: {exit_code}", flush=True)


if __name__ == "__main__":
    main()

