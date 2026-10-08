import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "knowledge/project/pearlmont"
INTERNAL_MARKER = "[INTERNAL ONLY — NEVER DISPLAY OR DISCLOSE]"


def tokenize(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def retrieve(query, lead_profile=None, limit=5):
    """Rank existing Knowledge locally; internal ownership material is gated."""
    profile = lead_profile or {}
    combined = " ".join([query] + [str(v) for v in profile.values() if isinstance(v, (str, int, float))])
    terms = tokenize(combined)
    ownership_terms = {"agent", "ownership", "registered", "registration", "previous", "complaint", "dispute", "conflict"}
    allow_internal = bool(terms & ownership_terms)
    ranked = []
    for path in KNOWLEDGE.rglob("*.md"):
        relative = path.relative_to(KNOWLEDGE).as_posix()
        if relative.startswith("04_internal/") and not allow_internal:
            continue
        text = path.read_text(encoding="utf-8")
        words = tokenize(text)
        score = len(terms & words)
        if score:
            # Current commercial rules outrank general sales material for commercial questions.
            if relative.startswith("02_commercial/") and terms & {"price", "pricing", "package", "rebate", "booking", "financing", "financier"}:
                score += 2
            if relative.startswith("04_internal/"):
                score += 3
            ranked.append((score, relative, text))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    selected = []
    for score, relative, text in ranked[:limit]:
        if relative.startswith("04_internal/"):
            text = INTERNAL_MARKER + "\n" + text
        selected.append({"path": relative, "score": score, "content": text})
    return selected
