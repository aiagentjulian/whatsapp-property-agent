import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "knowledge/project/pearlmont"
INTERNAL_MARKER = "[INTERNAL ONLY — NEVER DISPLAY OR DISCLOSE]"
STOPWORDS = {
    "a", "about", "an", "and", "are", "can", "could", "do", "does", "for", "hi", "how",
    "i", "is", "it", "know", "may", "me", "more", "of", "please", "tell", "the", "there",
    "this", "to", "what", "when", "where", "which", "would", "you",
}


def tokenize(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _passages(text):
    """Split Markdown into heading-scoped passages, keeping lists with their heading."""
    sections = []
    heading = ""
    lines = []
    for line in text.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            if heading and "".join(lines).strip():
                sections.append((heading, "\n".join(lines).strip()))
            heading = match.group(1).strip()
            lines = []
        elif heading:
            lines.append(line)
    if heading and "".join(lines).strip():
        sections.append((heading, "\n".join(lines).strip()))

    passages = []
    for heading, body in sections:
        # Split unusually long sections at paragraph boundaries, preserving the heading.
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", body) if part.strip()]
        current = []
        size = 0
        for paragraph in paragraphs:
            if current and size + len(paragraph) > 1600:
                passages.append((heading, "\n\n".join(current)))
                current, size = [], 0
            current.append(paragraph)
            size += len(paragraph)
        if current:
            passages.append((heading, "\n\n".join(current)))
    return passages


def retrieve(query, lead_profile=None, limit=3):
    """Return the most relevant short Knowledge passages; gate internal ownership material."""
    profile = lead_profile or {}
    raw_terms = tokenize(query)
    terms = raw_terms - STOPWORDS
    lower_query = (query or "").lower()
    general_intro = "project" in raw_terms and any(
        phrase in lower_query for phrase in ("more about", "tell me about", "know more", "about this project")
    )
    profile_text = " ".join(
        str(profile.get(key, "")) for key in ("active_concerns", "conversation_summary", "next_objective")
    )
    gate_terms = raw_terms | tokenize(profile_text)
    ownership_terms = {"agent", "ownership", "registered", "registration", "previous", "complaint", "dispute", "conflict"}
    allow_internal = bool(gate_terms & ownership_terms)
    # A direct project/developer identification question is different from a
    # general enquiry. Answer the former truthfully; keep the latter discreet.
    identity_request = bool(raw_terms & {"skyworld", "pearlmont"}) or any(
        phrase in lower_query for phrase in (
            "which project", "what project", "project name", "name of the project",
            "who is the developer", "who's the developer", "which developer",
            "developer name", "name of the developer", "who developed",
        )
    )
    if identity_request:
        path = KNOWLEDGE / "01_facts/overview.md"
        for heading, content in _passages(path.read_text(encoding="utf-8")):
            if heading.lower() == "project identity":
                return [{"path": path.relative_to(KNOWLEDGE).as_posix(),
                         "heading": heading, "score": 1, "content": content}]
    if general_intro:
        path = KNOWLEDGE / "01_facts/overview.md"
        for heading, content in _passages(path.read_text(encoding="utf-8")):
            if heading.lower() == "project identity":
                # Supply only introductory property facts, not identifiers the customer
                # has not asked for. Explicit identity questions use normal retrieval.
                labels = ("- Location:", "- Tenure:", "- Property type for Phase 1 residential:")
                facts = [line for line in content.splitlines() if line.strip().startswith(labels)]
                return [{"path": path.relative_to(KNOWLEDGE).as_posix(),
                         "heading": "General property facts", "score": 1, "content": "\n".join(facts)}]
    if not terms or ("?" not in (query or "") and not terms & {"project", "layout", "bedroom", "room", "price", "cost", "location", "facility", "facilities", "freehold", "tenure", "developer", "completion", "maintenance", "package", "rebate", "floor", "facing", "balcony", "unit", "transport", "school", "financing", "loan", "booking", "view", "viewing", "safety", "flood", "pylon", "cable"}):
        return []

    ranked = []
    sales_query = bool(terms & {"concern", "concerns", "objection", "small", "suit", "suitable", "fit", "invest", "investment", "yield", "view", "viewing", "priority", "recommend", "compare", "comparison"})
    for path in KNOWLEDGE.rglob("*.md"):
        relative = path.relative_to(KNOWLEDGE).as_posix()
        if relative.startswith("04_internal/") and not allow_internal:
            continue
        if relative.startswith("03_sales/") and not sales_query:
            continue
        text = path.read_text(encoding="utf-8")
        for heading, content in _passages(text):
            heading_terms = tokenize(heading)
            overlap = terms & (heading_terms | tokenize(content))
            if not overlap:
                continue
            score = len(overlap) + 3 * len(terms & heading_terms)
            if relative.startswith("02_commercial/") and terms & {"price", "pricing", "package", "rebate", "booking", "financing", "financier"}:
                score += 2
            if relative.startswith("04_internal/"):
                score += 3
            ranked.append((score, relative, heading, content))
    ranked.sort(key=lambda item: (-item[0], item[1], item[2]))
    if not ranked:
        return []
    # Keep only close matches. A specific one-word question can still use its best passage.
    best_score = ranked[0][0]
    relevant = [item for item in ranked if item[0] >= max(2, best_score - 1)]
    if not relevant:
        relevant = ranked[:1]
    selected = []
    files_seen = {}
    for score, relative, heading, content in relevant:
        if files_seen.get(relative, 0) >= 2:
            continue
        if relative.startswith("04_internal/"):
            content = INTERNAL_MARKER + "\n" + content
        selected.append({"path": relative, "heading": heading, "score": score, "content": content})
        files_seen[relative] = files_seen.get(relative, 0) + 1
        if len(selected) >= min(limit, 2):
            break
    return selected
