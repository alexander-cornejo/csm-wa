"""Parser for CSM-WA workaround text documents."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class WorkaroundEntry:
    error: str
    tuxedo_error: str
    description: str
    workaround: str
    tags: list[str]
    source_file: str
    line_number: int


ENTRY_SEPARATOR = re.compile(r"^---\s*$", re.MULTILINE)


def _strip_comment_lines(text: str) -> str:
    """Remove leading comment lines so file headers don't block the first entry."""
    lines = [line for line in text.splitlines() if not line.strip().startswith("#")]
    return "\n".join(lines).strip()


def parse_workaround_file(path: Path) -> list[WorkaroundEntry]:
    """Parse a single workaround document into structured entries."""
    text = path.read_text(encoding="utf-8")
    entries: list[WorkaroundEntry] = []

    blocks = ENTRY_SEPARATOR.split(text)
    for block in blocks:
        block = _strip_comment_lines(block.strip())
        if not block:
            continue

        entry = _parse_block(block, path.name)
        if entry:
            entries.append(entry)

    return entries


def _parse_block(block: str, source_file: str) -> WorkaroundEntry | None:
    error = _extract_section(block, "ERROR")
    workaround = _extract_section(block, "WORKAROUND")

    if not error or not workaround:
        return None

    tuxedo_error = _extract_section(block, "TUXEDO_ERROR") or ""
    description = _extract_section(block, "DESCRIPTION") or ""
    tags_raw = _extract_section(block, "TAGS") or ""
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    line_number = block[: block.index("[ERROR]")].count("\n") + 1 if "[ERROR]" in block else 1

    return WorkaroundEntry(
        error=error.strip(),
        tuxedo_error=tuxedo_error.strip(),
        description=description.strip(),
        workaround=workaround.strip(),
        tags=tags,
        source_file=source_file,
        line_number=line_number,
    )


def _extract_section(block: str, section: str) -> str | None:
    pattern = rf"\[{section}\]\s*\n(.*?)(?=\n\[|\Z)"
    match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None


def load_all_workarounds(data_dir: Path) -> list[WorkaroundEntry]:
    """Load every .txt file in the workarounds directory."""
    entries: list[WorkaroundEntry] = []
    if not data_dir.exists():
        return entries

    for path in sorted(data_dir.glob("*.txt")):
        entries.extend(parse_workaround_file(path))

    return entries


SEARCH_SKIP_TERMS = frozenset(
    {"a", "an", "and", "in", "on", "or", "to", "for", "the", "is", "at", "by", "of", "it"}
)

TUXEDO_QUERY_MARKERS = re.compile(
    r"Error logged at:|Stack [Ii]d:|^\s*\d+\)\s*Msg:|^\s*Msg:|Code:\s*\S|"
    r"ERR_TRACE_FAILURE|ERR_\w+|ORA-\d+|SQL-\d+|File:\s*/",
    re.I | re.M,
)

# Too generic alone; still useful when combined with other signals.
WEAK_SIGNALS = frozenset(
    {
        "trace failure",
        "no data found",
        "key was not found",
        "ora-00100",
        "err_trace_failure",
        "returned status",
        "user value",
    }
)

NOISE_SIGNAL_PATTERNS = (
    re.compile(r"^\d{5,}$"),
    re.compile(r"^line:\s*\d+$", re.I),
    re.compile(r"^user\s+value", re.I),
    re.compile(r"^returned\s+status", re.I),
    re.compile(r"^input\s+parameter", re.I),
    re.compile(r"^/opt/", re.I),
    re.compile(r"^\d{1,2}:\d{2}:\d{2}$"),
)


def _normalize_signal(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _is_noise_signal(signal: str) -> bool:
    if not signal or len(signal) < 3:
        return True
    for pattern in NOISE_SIGNAL_PATTERNS:
        if pattern.search(signal):
            return True
    if re.fullmatch(r"[\d.,:]+", signal):
        return True
    return False


def _looks_like_tuxedo_query(query: str) -> bool:
    text = query.strip()
    if not text:
        return False
    if TUXEDO_QUERY_MARKERS.search(text):
        if text.count("\n") >= 2 or len(text) >= 120:
            return True
    return False


def _extract_tuxedo_signals_weighted(query: str) -> list[tuple[str, str]]:
    """Same as extract but keeps high/normal/low weights for scoring."""
    signals: list[tuple[str, str]] = []
    seen: set[str] = set()

    def add(raw: str, weight: str = "normal") -> None:
        norm = _normalize_signal(raw)
        if _is_noise_signal(norm) or norm in seen:
            return
        seen.add(norm)
        signals.append((norm, weight))

    for match in re.finditer(r"Stack [Ii]d:\s*(\S+)", query):
        add(match.group(1), "high")

    for match in re.finditer(r"Code:\s*([^,\n]+)", query, re.I):
        code = match.group(1).strip()
        if code and code not in {"0", "4"}:
            add(code, "high")

    for match in re.finditer(r"File:.*?\((\w+)\)", query, re.I):
        add(match.group(1), "high")

    for match in re.finditer(r"(?:Msg:\s*|^\s*\d+\)\s*)(.+)$", query, re.I | re.M):
        msg = match.group(1).strip()
        msg = re.split(r"\s+Code:", msg, maxsplit=1)[0].strip()
        if len(msg) >= 12:
            add(msg, "high")

    for match in re.finditer(r"\b(ORA-\d+)\b", query, re.I):
        add(match.group(1), "low")

    for match in re.finditer(r"\b(SQL-\d+)\b", query, re.I):
        add(match.group(1), "high")

    for match in re.finditer(r"\b(ERR_[A-Z0-9_]+)\b", query, re.I):
        add(match.group(1), "normal")

    for match in re.finditer(r"\b([A-Z][A-Z0-9_]{3,})\b", query):
        token = match.group(1)
        if token not in {"FILE", "CODE", "LINE", "USER", "VALUE", "INPUT", "BAN"}:
            add(token, "normal")

    for match in re.finditer(r"\b([a-z][a-z0-9_]{2,})\b", query):
        token = match.group(1)
        if "_" in token and not token.startswith("opt"):
            add(token, "normal")

    return signals


def _score_tuxedo_match(entry: WorkaroundEntry, signals: list[tuple[str, str]], query_lower: str) -> int:
    error_l = entry.error.lower()
    tags_l = " ".join(entry.tags).lower()
    tuxedo_l = entry.tuxedo_error.lower()
    desc_l = entry.description.lower()
    wa_l = entry.workaround.lower()
    searchable = " ".join([error_l, tuxedo_l, desc_l, wa_l, tags_l])

    if query_lower in tuxedo_l:
        return 1000
    if query_lower in error_l:
        return 900

    weight_points = {"high": 40, "normal": 15, "low": 5}
    score = 0
    matched = 0
    strong_matches = 0

    for signal, weight in signals:
        if signal in searchable:
            matched += 1
            pts = weight_points.get(weight, 10)
            if signal not in WEAK_SIGNALS:
                strong_matches += 1
            if signal in tuxedo_l:
                pts += 20
            elif signal in error_l:
                pts += 12
            elif signal in desc_l:
                pts += 6
            score += pts

    if matched == 0:
        return 0

    min_strong = 2 if len(signals) >= 6 else 1
    min_matched = max(2, int(len(signals) * 0.15))
    if strong_matches < min_strong or matched < min_matched:
        return 0

    score += matched * 5
    return score


def _meaningful_terms(query: str) -> list[str]:
    """Drop very common short words that cause false-positive matches."""
    terms = query.lower().split()
    meaningful = [t for t in terms if t not in SEARCH_SKIP_TERMS or len(t) > 2]
    return meaningful if meaningful else terms


def search_workarounds(entries: list[WorkaroundEntry], query: str) -> list[WorkaroundEntry]:
    """Find entries matching the query (case-insensitive partial match)."""
    if not query.strip():
        return []

    query_lower = query.lower().strip()

    if _looks_like_tuxedo_query(query):
        signals = _extract_tuxedo_signals_weighted(query)
        if signals:
            results: list[tuple[int, WorkaroundEntry]] = []
            for entry in entries:
                score = _score_tuxedo_match(entry, signals, query_lower)
                if score > 0:
                    results.append((score, entry))
            results.sort(key=lambda x: x[0], reverse=True)
            if results:
                return [entry for _, entry in results]

    terms = _meaningful_terms(query_lower)
    results: list[tuple[int, WorkaroundEntry]] = []

    for entry in entries:
        error_l = entry.error.lower()
        tags_l = " ".join(entry.tags).lower()
        tuxedo_l = entry.tuxedo_error.lower()
        desc_l = entry.description.lower()
        wa_l = entry.workaround.lower()
        searchable = " ".join([error_l, tuxedo_l, desc_l, wa_l, tags_l])

        if not all(term in searchable for term in terms):
            continue

        score = 0

        if query_lower in error_l:
            score += 100
        elif query_lower in tags_l:
            score += 80
        elif query_lower in tuxedo_l:
            score += 60
        elif query_lower in desc_l:
            score += 40

        for term in terms:
            if term in error_l:
                score += 15
            if term in tags_l:
                score += 12
            if term in tuxedo_l:
                score += 8
            score += searchable.count(term)

        results.append((score, entry))

    results.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in results]


def format_new_entry(
    error: str,
    tuxedo_error: str,
    description: str,
    workaround: str,
    tags: str,
) -> str:
    """Build a new entry block in the standard format."""
    lines = [
        "[ERROR]",
        error.strip(),
        "",
        "[DESCRIPTION]",
        description.strip() or "No additional description.",
        "",
        "[TUXEDO_ERROR]",
        tuxedo_error.strip(),
        "",
        "[WORKAROUND]",
        workaround.strip(),
        "",
        "[TAGS]",
        tags.strip() or "general",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def append_entry_to_file(data_dir: Path, filename: str, entry_text: str) -> Path:
    """Append a new workaround entry to the specified file."""
    data_dir.mkdir(parents=True, exist_ok=True)
    target = data_dir / filename

    if not target.exists():
        header = (
            "# CSM-WA Workarounds\n"
            "# Format: [ERROR], [DESCRIPTION], [TUXEDO_ERROR], [WORKAROUND], [TAGS]\n"
            "# Entry separator: ---\n\n"
        )
        target.write_text(header, encoding="utf-8")

    with target.open("a", encoding="utf-8") as f:
        f.write(entry_text)

    return target
