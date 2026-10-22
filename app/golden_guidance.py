"""Select a small stage-relevant Golden Conversation excerpt for Luna.

The bank contains draft fictional examples. It guides *sales decisions*, never
provides an approved customer-facing script or evidence of real conversion.
No LLM/network call, database access, or persistent learning occurs here.
"""

import re
from functools import lru_cache

from .golden_cases import load_goldens

STOPWORDS = {
    "a", "an", "and", "the", "or", "is", "it", "this", "that", "about",
    "i", "im", "we", "our", "my", "me", "you", "your", "can", "could", "would",
    "please", "do", "does", "for", "in", "on", "at", "of", "to", "are", "be",
    "what", "where", "how", "more", "want", "like", "looking", "considering",
    "hi", "hello", "own", "stay", "investment", "pearl", "residences",
}


@lru_cache(maxsize=1)
def _beats():
    bank = load_goldens()
    return tuple(
        {"id": case["id"], "route": case["route"], "stage": beat["stage"],
         "buyer": beat["buyer"], "seller": beat["seller"], "why": beat["why"]}
        for case in bank["cases"] for beat in case["beats"]
    )


def _terms(text):
    return set(re.findall(r"[a-z0-9]+", str(text).lower())) - STOPWORDS


def select_golden_guidance(latest_message, profile, history, workflow, max_examples=2):
    """Return at most two matching examples without injecting the whole corpus.

    Stage is the hard gate. For established purposes the route is another hard
    gate. Only a strongly context-matched second beat may be included.
    """
    stage = workflow.get("stage")
    route = workflow.get("route")
    if max_examples < 1 or not stage:
        return {"policy": "no_script_or_guarantee", "examples": []}
    latest_terms = _terms(latest_message)
    recent_customer = " ".join(
        str(row.get("body", "")) for row in history[-8:]
        if row.get("direction") == "INBOUND"
    )
    context_terms = _terms(recent_customer)
    ranked = []
    for beat in _beats():
        if beat["stage"] != stage:
            continue
        if route in ("OWN_STAY", "INVESTMENT") and beat["route"] != route:
            continue
        query_terms = _terms(beat["buyer"])
        score = 4 * len(query_terms & latest_terms) + len(query_terms & context_terms)
        # First beat by bank order is a reasonable fallback when no example
        # shares vocabulary, but do not add multiple loosely related examples.
        ranked.append((score, beat))
    ranked.sort(key=lambda pair: -pair[0])  # stable ties preserve curated order
    selected = []
    for score, beat in ranked:
        if selected and score < 3:
            break
        selected.append({
            "case_id": beat["id"],
            "stage": beat["stage"],
            "illustrative_customer": beat["buyer"][:340],
            "illustrative_seller": beat["seller"][:650],
            "sales_reasoning": beat["why"][:340],
        })
        if len(selected) >= min(max_examples, 2):
            break
    return {
        "policy": (
            "Draft fictional examples of SELLING JUDGMENT, not fixed scripts, "
            "customer facts, or verified results. Adapt to the actual buyer and "
            "current Knowledge, do not copy phrases, infer unknown details, or "
            "override workflow, factual safeguards or handoff rules."
        ),
        "examples": selected,
    }
