from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path


def find_orca() -> Path | None:
    configured = os.environ.get("ORCA_EXE")
    if configured and Path(configured).exists():
        return Path(configured)
    from shutil import which
    found = which("orca")
    return Path(found) if found else None


def run_orca(input_file: str | Path, output_file: str | Path | None = None) -> subprocess.CompletedProcess:
    exe = find_orca()
    if exe is None:
        raise FileNotFoundError("ORCA executable not found. Set ORCA_EXE to the full path.")
    inp = Path(input_file).resolve()
    out = Path(output_file).resolve() if output_file else inp.with_suffix(".out")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        proc = subprocess.run(
            [str(exe), inp.name],
            cwd=inp.parent,
            stdout=handle,
            stderr=subprocess.STDOUT,
            check=False,
        )
    return proc


def shell_command(input_file: str | Path, output_file: str | Path | None = None) -> str:
    inp = Path(input_file)
    out = Path(output_file) if output_file else inp.with_suffix(".out")
    exe = os.environ.get("ORCA_EXE", "/full/path/to/orca")
    return f"{shlex.quote(exe)} {shlex.quote(inp.name)} > {shlex.quote(out.name)}"
