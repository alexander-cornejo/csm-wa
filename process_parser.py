"""Parser for CSM process text documents."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ENTRY_SEPARATOR = re.compile(r"^---\s*$", re.MULTILINE)

SEARCH_SKIP_TERMS = frozenset(
    {"a", "an", "and", "in", "on", "or", "to", "for", "the", "is", "at", "by", "of", "it", "de", "el", "la", "los", "las"}
)


@dataclass
class ProcessEntry:
    nombre: str
    pasos: str
    source_file: str
    line_number: int


def _strip_comment_lines(text: str) -> str:
    lines = [line for line in text.splitlines() if not line.strip().startswith("#")]
    return "\n".join(lines).strip()


def _extract_section(block: str, section: str) -> str | None:
    pattern = rf"\[{section}\]\s*\n(.*?)(?=\n\[|\Z)"
    match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None


def parse_process_file(path: Path) -> list[ProcessEntry]:
    text = path.read_text(encoding="utf-8")
    entries: list[ProcessEntry] = []

    for block in ENTRY_SEPARATOR.split(text):
        block = _strip_comment_lines(block.strip())
        if not block:
            continue

        entry = _parse_block(block, path.name)
        if entry:
            entries.append(entry)

    return entries


def _parse_block(block: str, source_file: str) -> ProcessEntry | None:
    nombre = _extract_section(block, "NOMBRE")
    pasos = _extract_section(block, "PASOS")

    if not nombre or not pasos:
        return None

    line_number = block[: block.index("[NOMBRE]")].count("\n") + 1 if "[NOMBRE]" in block else 1

    return ProcessEntry(
        nombre=nombre.strip(),
        pasos=pasos.strip(),
        source_file=source_file,
        line_number=line_number,
    )


def load_all_processes(data_dir: Path) -> list[ProcessEntry]:
    entries: list[ProcessEntry] = []
    if not data_dir.exists():
        return entries

    for path in sorted(data_dir.glob("*.txt")):
        entries.extend(parse_process_file(path))

    return entries


def _meaningful_terms(query: str) -> list[str]:
    terms = query.lower().split()
    meaningful = [t for t in terms if t not in SEARCH_SKIP_TERMS or len(t) > 2]
    return meaningful if meaningful else terms


def search_processes(entries: list[ProcessEntry], query: str) -> list[ProcessEntry]:
    if not query.strip():
        return []

    query_lower = query.lower().strip()
    terms = _meaningful_terms(query_lower)
    results: list[tuple[int, ProcessEntry]] = []

    for entry in entries:
        nombre_l = entry.nombre.lower()
        pasos_l = entry.pasos.lower()
        searchable = f"{nombre_l} {pasos_l}"

        if not all(term in searchable for term in terms):
            continue

        score = 0
        if query_lower in nombre_l:
            score += 100
        elif query_lower in pasos_l:
            score += 40

        for term in terms:
            if term in nombre_l:
                score += 15
            score += searchable.count(term)

        results.append((score, entry))

    results.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in results]


def format_new_process(nombre: str, pasos: str) -> str:
    return "\n".join(
        [
            "[NOMBRE]",
            nombre.strip(),
            "",
            "[PASOS]",
            pasos.strip(),
            "",
            "---",
            "",
        ]
    )


def append_process_to_file(data_dir: Path, filename: str, entry_text: str) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    target = data_dir / filename

    if not target.exists():
        header = (
            "# CSM Processes\n"
            "# Format: [NOMBRE], [PASOS]\n"
            "# Entry separator: ---\n\n"
        )
        target.write_text(header, encoding="utf-8")

    with target.open("a", encoding="utf-8") as f:
        f.write(entry_text)

    return target
