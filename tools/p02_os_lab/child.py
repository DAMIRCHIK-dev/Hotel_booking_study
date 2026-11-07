"""P02 Lab · Child process: user-mode calculation, blocking stdin wait, OS file write, and exit code."""
from __future__ import annotations

import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

EXIT_CODE = 7
ITERATIONS = 50_000


def main() -> int:
    pid = os.getpid()
    ppid = os.getppid()
    print(f"[child] PID={pid} PPID={ppid} platform={platform.platform()}", flush=True)

    # Pure user-mode CPU + RAM calculation (no OS file/network syscalls inside the loop)
    checksum = sum(i * i for i in range(ITERATIONS))
    print(f"[child] Calculated synthetic checksum={checksum} over {ITERATIONS} iterations.", flush=True)

    # Blocks in OS waiting state until stdin receives a newline (Enter)
    input("[child] Waiting for Enter so you can inspect this PID... ")

    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    result_file = output_dir / "child-result.txt"
    timestamp = datetime.now(timezone.utc).isoformat()
    result_file.write_text(
        f"timestamp={timestamp}\n"
        f"pid={pid}\n"
        f"ppid={ppid}\n"
        f"platform={platform.platform()}\n"
        f"python={sys.version.split()[0]}\n"
        f"iterations={ITERATIONS}\n"
        f"checksum={checksum}\n"
        f"exit_code={EXIT_CODE}\n",
        encoding="utf-8",
    )
    print(f"[child] Wrote {result_file.relative_to(Path(__file__).resolve().parent)}; exiting with {EXIT_CODE}.", flush=True)
    return EXIT_CODE


if __name__ == "__main__":
    raise SystemExit(main())
