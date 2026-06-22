from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass
class OrcaInput:
    """Build a simple, auditable ORCA input file.

    The class intentionally covers only common tutorial inputs. Advanced users
    should edit the rendered text or use native ORCA blocks directly.
    """

    method_line: str
    charge: int
    multiplicity: int
    xyzfile: str | None = None
    coordinates: Iterable[str] | None = None
    blocks: dict[str, list[str]] = field(default_factory=dict)
    comments: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.method_line.strip():
            raise ValueError("method_line cannot be empty")
        if self.multiplicity < 1:
            raise ValueError("multiplicity must be a positive integer")
        if (self.xyzfile is None) == (self.coordinates is None):
            raise ValueError("provide exactly one of xyzfile or coordinates")

    def render(self) -> str:
        self.validate()
        lines: list[str] = []
        lines.extend(f"# {c}" for c in self.comments)
        lines.append("! " + self.method_line.strip().removeprefix("!").strip())
        lines.append("")
        scalar_directives = {"maxcore", "base", "moinp"}
        for name, values in self.blocks.items():
            normalized = name.lower().lstrip("%")
            if normalized in scalar_directives:
                if len(values) != 1:
                    raise ValueError(f"%{name} expects exactly one value")
                lines.append(f"%{name} {values[0]}")
                lines.append("")
                continue
            lines.append(f"%{name}")
            lines.extend(f"  {v}" for v in values)
            lines.append("end")
            lines.append("")
        if self.xyzfile is not None:
            lines.append(f"* xyzfile {self.charge} {self.multiplicity} {self.xyzfile}")
        else:
            lines.append(f"* xyz {self.charge} {self.multiplicity}")
            lines.extend(str(x).rstrip() for x in self.coordinates or [])
            lines.append("*")
        return "\n".join(lines) + "\n"

    def write(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.render(), encoding="utf-8")
        return target
