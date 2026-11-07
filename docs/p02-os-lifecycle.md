# P02 · OS Introduction, Kernels and Process Lifecycle Worksheet

## 1. My Environment (`environment`)

- **Student**: Damir
- **Operating System**: Windows 11 (`Windows-11-10.0.26300-SP0`)
- **Python Runtime**: Python `3.12.10` (`.venv\Scripts\python.exe`)
- **Inspection Tool**: PowerShell `Get-Process` (`Id`, `ProcessName`, `Threads.Count`, `WorkingSet64`, `PrivateMemorySize64`)
- **Evidence Type**: **Observed** on local machine (`2026-11-07T06:00:45Z` and `2026-11-07T06:01:31Z`)

---

## 2. My Execution Path (`boundary`)

```text
[User Mode]   child.py: sum(i * i for i in range(50_000))
                  └── Executes purely on CPU registers + private process RAM (no kernel transition per iteration)

[User Mode]   child.py: result_file.write_text(...)
                  │
                  ▼  Python standard library / C runtime (pathlib -> io.open / write / close)
[OS API]      Win32 API (CreateFileW / WriteFile / CloseHandle via ntdll.dll)
                  │
                  ▼  System call boundary (User Mode -> Kernel Mode transition)
[Kernel Mode] Windows NT Kernel I/O Manager + NTFS Filesystem Driver + Cache Manager
                  │
                  ▼  Buffered / flushed block write
[Hardware]    NVMe Storage Device -> tools/p02_os_lab/output/child-result.txt
```

---

## 3. My Process Observation (`inspection`)

Observed live while `child.py` was paused at `input("[child] Waiting for Enter...")`:

| Field | Observed Value (Run 1 · `EXIT_CODE = 7`) | Observed Value (Run 2 · `EXIT_CODE = 0`) |
|---|---|---|
| **Timestamp (UTC)** | `2026-11-07T06:00:45Z` | `2026-11-07T06:01:31Z` |
| **Parent Script PID** | `11092` (`.venv` launcher child `18384`) | `2860` (`.venv` launcher child `6736`) |
| **Child Interpreter PID** | `12624` (`PPID = 18384`) | `13756` (`PPID = 6736`) |
| **Process Name** | `python` (`python.exe`) | `python` (`python.exe`) |
| **Thread Count** | `7` threads | `7` threads |
| **Working Set Memory (`WorkingSet64`)** | `19,992,576 bytes` (`19.07 MiB`) | `20,033,536 bytes` (`19.11 MiB`) |
| **Private Memory (`PrivateMemorySize64`)** | `10,096,640 bytes` (`9.63 MiB`) | `10,203,136 bytes` (`9.73 MiB`) |

> **Windows venv launcher note**: On Windows, `.venv\Scripts\python.exe` is a lightweight launcher shim (`PID=18384`) that spawns the base `python.exe` interpreter (`PID=12624`) and forwards its exit code back to `parent.py` (`PID=11092`).

---

## 4. My Parent/Child Timeline (`lifecycle`)

1. **Creation (`Observed` + `Inferred`)**: `parent.py` (`PID=11092`) calls `subprocess.Popen(...)`. The OS allocates a new private virtual address space and process control block for the child (`PID=12624`). `parent.py` calls `child.wait()`, entering a **Blocked/Waiting** state until the child terminates.
2. **User-Mode Calculation (`Inferred Ready/Running`)**: `PID=12624` is scheduled onto a CPU core (**Running**), computes `checksum=41665416675000` across `50,000` iterations in private RAM, and prints its PID/PPID.
3. **Waiting for Input (`Observed` + `Inferred Blocked`)**: `child.py` calls `input(...)`. Because stdin has no newline yet, the kernel places `PID=12624`'s main thread into the **Blocked/Waiting** state (`0%` CPU) while we inspect its memory (`19.07 MiB` working set).
4. **Input Arrives & File Saved (`Observed`)**: Sending `\n` wakes `PID=12624` (**Blocked → Ready → Running**). It requests file creation and writes `output/child-result.txt` through the OS filesystem interface.
5. **Child Exits & Parent Reaps Code (`Observed`)**: `child.py` raises `SystemExit(7)`. The kernel reclaims `PID=12624`'s private RAM and unblocks `parent.py`'s `wait()` call, which prints `Child exit code: 7`.

---

## 5. Windows and POSIX Comparison (`comparison`)

- **POSIX (Linux / macOS — teacher-supplied model)**:
  - `fork()` duplicates the calling process, creating a child with its own new PID and copy-on-write address space.
  - `exec()` replaces the child process's memory image with a new program (`python3 child.py`) while keeping the child's PID.
  - `wait()` / `waitpid()` blocks the parent until the child terminates and collects its exit status so no zombie entry remains.
- **Windows (Observed locally)**:
  - Windows does **not** use `fork() + exec()`. Instead, Python's `subprocess.Popen` invokes Win32 `CreateProcessW`, which creates a new process and loads the target executable (`python.exe`) directly in a single OS operation, then waits on the process handle (`WaitForSingleObject` / `GetExitCodeProcess`).

---

## 6. My Changed-Code Experiment (`experiment`)

- **Single Change**: Edited `EXIT_CODE = 7` → `EXIT_CODE = 0` in `tools/p02_os_lab/child.py`.
- **Prediction before running**: `parent.py` will print `Child exit code: 0` instead of `7`, and `output/child-result.txt` will **not** disappear — it will be overwritten with the new run's PID, timestamp, and `exit_code=0`.
- **Command Run**: `.\.venv\Scripts\python.exe tools\p02_os_lab\parent.py`
- **Actual Output**:
  ```text
  [parent] PID=2860 starting child: child.py
  [parent] Spawned child PID=6736; waiting for child to finish...
  [child] PID=13756 PPID=6736 platform=Windows-11-10.0.26300-SP0
  [child] Calculated synthetic checksum=41665416675000 over 50000 iterations.
  [child] Waiting for Enter so you can inspect this PID...
  [child] Wrote output\child-result.txt; exiting with 0.
  Child exit code: 0
  ```
- **Saved-File Result**: `output/child-result.txt` remained on disk containing `pid=13756`, `checksum=41665416675000`, and `exit_code=0`.
- **Limitation**: A normal `write_text()` proves persistence after process termination, not power-loss durability (which requires explicit `fsync` / database WAL commit, studied in P07/L05).

---

## 7. My Runtime Decision (`adr`)

- **Requirement**: Confirmed bookings must survive process restarts and be visible consistently across requests.
- **Options Considered**:
  1. Keep reservations in an in-process Python `list` in RAM (used in P03–P06 for fast prototyping and unit tests).
  2. Persist reservations in an external relational database process (`PostgreSQL`, introduced in P07).
- **Provisional Choice**: Use an in-memory list behind a `ReservationStore` interface during domain modeling (P03–P06), then switch wiring to PostgreSQL in P07.
- **Evidence**: P02 showed that private process memory (`~9.63 MiB`) is reclaimed immediately by the kernel when `python.exe` exits, whereas OS-persisted storage survives process exit.
- **Cost / Revisit Trigger**: Revisit in-memory storage as soon as bookings must survive server restarts or multiple application instances run concurrently (L04 / P07).

---

## 8. My Individual Exit Answer (`reflection`)

- **Ready vs. Blocked**: A **Ready** process has everything it needs to execute and is only waiting for the OS scheduler to assign a CPU core; a **Blocked** process cannot proceed until an external event completes (such as `PID=12624` waiting for Enter on `stdin` or `parent.py` waiting in `child.wait()`).
- **One Kernel Job**: Memory isolation and privilege enforcement — preventing one user-space process from reading or corrupting another process's private memory or writing raw disk blocks directly.
- **Why Process Exit Keeps Saved Files**: Working variables live in the process's virtual address space (destroyed at exit), whereas a completed file write has already crossed the system-call boundary into the kernel's filesystem/storage subsystem, whose lifetime is independent of the exiting process.

