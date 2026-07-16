"""Convert >> title / ---- separator format to CSM [NOMBRE]/[PASOS] format."""

from __future__ import annotations

import re
from pathlib import Path

from process_parser import format_new_process

RAW = Path(__file__).parent / "data" / "procesos" / "_import_raw.txt"
OUT = Path(__file__).parent / "data" / "procesos" / "csm_procesos.txt"


def parse_raw(text: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    parts = re.split(r"\n(?=>> )", text)

    for part in parts:
        part = part.strip()
        if not part.startswith(">>"):
            continue

        lines = part.splitlines()
        nombre = lines[0].replace(">>", "", 1).strip()
        body: list[str] = []

        for line in lines[1:]:
            stripped = line.strip()
            if re.match(r"^-{40,}\s*$", stripped):
                break
            if re.match(r"^@c-{10,}\s*$", stripped):
                break
            body.append(line.rstrip())

        pasos = "\n".join(body).strip()
        if nombre and pasos:
            entries.append((nombre, pasos))

    return entries


def main() -> None:
    text = RAW.read_text(encoding="utf-8")
    entries = parse_raw(text)

    header = (
        "# CSM Procesos - Documentación operativa\n"
        "# Formato: [NOMBRE], [PASOS]\n"
        "# Separador entre entradas: ---\n\n"
    )

    blocks = [format_new_process(nombre, pasos) for nombre, pasos in entries]
    OUT.write_text(header + "".join(blocks), encoding="utf-8")
    print(f"Converted {len(entries)} processes -> {OUT}")


if __name__ == "__main__":
    main()
