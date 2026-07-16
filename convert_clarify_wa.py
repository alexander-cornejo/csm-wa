"""Convert Clarify Tickets 1.txt (>> blocks) to CSM-WA format."""

from __future__ import annotations

import re
from pathlib import Path

SOURCE = Path(r"C:\Users\jhonnalc\Downloads\Clarify Tickets 1.txt")
OUTPUT = Path(__file__).parent / "data" / "workarounds" / "clarify_tickets_wa_TEMP.txt"

DASH_SEP = re.compile(r"^-{5,}\s*$")
STAR_SEP = re.compile(r"^\*{5,}\s*$")
WA_START = re.compile(r"^(Proceso|Procedure|FIX|Workaround)\s*:?\s*(.*)?$", re.IGNORECASE)
STRUCTURED = re.compile(r"^(Mkt:|Ban:|Ctn:|Request:|Error|Notes:|Case ID:)", re.I)


def is_title_line(line: str) -> bool:
    return line.lstrip().startswith(">>")


def get_title(line: str) -> str:
    return line.lstrip()[2:].strip()


def is_separator(line: str) -> bool:
    s = line.strip()
    return bool(DASH_SEP.match(s) or STAR_SEP.match(s))


def next_non_empty_is_title(lines: list[str], idx: int) -> bool:
    j = idx + 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    return j < len(lines) and is_title_line(lines[j])


def split_wa_blocks(text: str) -> list[tuple[str, list[str]]]:
    lines = text.splitlines()
    blocks: list[tuple[str, list[str]]] = []
    i = 0
    n = len(lines)

    while i < n:
        if not is_title_line(lines[i]):
            i += 1
            continue

        title = get_title(lines[i])
        body: list[str] = []
        i += 1

        while i < n:
            if is_title_line(lines[i]):
                break
            if is_separator(lines[i]) and next_non_empty_is_title(lines, i):
                break
            body.append(lines[i])
            i += 1

        while body and not body[-1].strip():
            body.pop()

        blocks.append((title, body))

    return blocks


def _find_wa_start(lines: list[str]) -> int | None:
    for idx, line in enumerate(lines):
        if WA_START.match(line.strip()):
            return idx
    return None


def _is_tuxedo_start(lines: list[str], i: int) -> bool:
    s = lines[i].strip()
    if re.search(r"Error logged at:", s, re.I):
        return True
    if re.search(r"(?i)tuxedo", s):
        return True
    if DASH_SEP.match(s) and i + 1 < len(lines) and re.search(r"Error logged at:", lines[i + 1], re.I):
        return True
    if re.search(r"Stack [Ii]d:", s) and re.search(r"csmU", s, re.I):
        return True
    if re.match(r"^\d+\)\s*Msg:\s*Trace Failure", s, re.I):
        return True
    return False


def _looks_like_tuxedo_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    return bool(
        re.search(
            r"Error logged at:|Stack [Ii]d:|tuxedo|^\d+\)\s*Msg:|^Code:|^File:|"
            r"ERR_TRACE_FAILURE|FML (get|error)|DATABASE ERROR",
            s,
            re.I,
        )
        or DASH_SEP.match(s)
    )


def _extract_tuxedo(lines: list[str]) -> tuple[str, list[str]]:
    tuxedo_parts: list[str] = []
    remaining: list[str] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if WA_START.match(stripped):
            remaining.extend(lines[i:])
            break

        if stripped.lower() == "error:" and _error_section_has_tuxedo(lines, i):
            chunk: list[str] = []
            while i < n and not WA_START.match(lines[i].strip()):
                chunk.append(lines[i])
                i += 1
            tuxedo_parts.extend(chunk)
            continue

        if _is_tuxedo_start(lines, i):
            chunk = []
            while i < n:
                cur = lines[i]
                cur_s = cur.strip()
                if chunk and WA_START.match(cur_s):
                    break
                if chunk and not cur_s:
                    j = i + 1
                    while j < n and not lines[j].strip():
                        j += 1
                    if j < n and not _looks_like_tuxedo_line(lines[j]) and not WA_START.match(
                        lines[j].strip()
                    ):
                        break
                chunk.append(cur)
                i += 1
                if re.search(r"(?i)tuxedo", chunk[0]) and i < n and WA_START.match(lines[i].strip()):
                    break
            tuxedo_parts.extend(chunk)
            continue

        remaining.append(line)
        i += 1

    return "\n".join(tuxedo_parts).strip(), remaining


def _error_section_has_tuxedo(lines: list[str], start: int) -> bool:
    for j in range(start + 1, min(start + 30, len(lines))):
        s = lines[j].strip()
        if WA_START.match(s):
            break
        if _looks_like_tuxedo_line(lines[j]):
            return True
    return False


def _build_tags(title: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", title)
    key = [w for w in words if len(w) > 2][:6]
    return ", ".join(dict.fromkeys(["clarify"] + key))


def parse_entry(title: str, body: list[str]) -> dict[str, str]:
    wa_idx = _find_wa_start(body)
    pre_wa = body[:wa_idx] if wa_idx is not None else body[:]
    wa_lines = body[wa_idx:] if wa_idx is not None else []

    tuxedo, pre_wa = _extract_tuxedo(pre_wa)

    description_lines: list[str] = []
    idx = 0
    while idx < len(pre_wa) and not pre_wa[idx].strip():
        idx += 1

    if idx < len(pre_wa):
        first = pre_wa[idx].strip()
        if not WA_START.match(first) and not STRUCTURED.match(first):
            description_lines.append(pre_wa[idx])
            idx += 1

    description_lines.extend(pre_wa[idx:])
    description = "\n".join(description_lines).strip() or "Sin descripción adicional."

    if wa_lines:
        first = wa_lines[0].strip()
        m = WA_START.match(first)
        extra = (m.group(2) or "").strip() if m else ""
        content_lines = wa_lines[1:] if m and not extra else wa_lines
        if m and extra:
            content_lines = [extra] + wa_lines[1:]
        workaround = "\n".join(content_lines).strip()
    else:
        workaround = "Sin workaround documentado."

    return {
        "error": title,
        "description": description,
        "tuxedo_error": tuxedo,
        "workaround": workaround,
        "tags": _build_tags(title),
    }


def format_entry(entry: dict[str, str]) -> str:
    parts = [
        "[ERROR]",
        entry["error"],
        "",
        "[DESCRIPTION]",
        entry["description"],
        "",
    ]
    if entry["tuxedo_error"]:
        parts.extend(["[TUXEDO_ERROR]", entry["tuxedo_error"], ""])
    parts.extend(
        [
            "[WORKAROUND]",
            entry["workaround"],
            "",
            "[TAGS]",
            entry["tags"],
            "",
            "---",
            "",
        ]
    )
    return "\n".join(parts)


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    blocks = split_wa_blocks(text)
    entries = [parse_entry(title, body) for title, body in blocks if title]

    header = (
        "# CSM-WA TEMP — Importado desde Clarify Tickets 1.txt\n"
        "# REVISAR ANTES DE MERGE\n"
        "# Reglas: titulos >>, fin en --- o *** cuando sigue otro >>\n"
        "# Formato: [ERROR], [DESCRIPTION], [TUXEDO_ERROR], [WORKAROUND], [TAGS]\n"
        f"# Total entradas: {len(entries)}\n\n"
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(header + "".join(format_entry(e) for e in entries), encoding="utf-8")

    with_tux = sum(1 for e in entries if e["tuxedo_error"])
    print(f"Blocks (>>): {len(blocks)}")
    print(f"Entries written: {len(entries)}")
    print(f"With TUXEDO_ERROR: {with_tux}")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()
