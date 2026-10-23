"""Small deterministic evidence-precedence policy for sales decisions.

Only a *resolved and affirmatively verified* specific quote can supersede
historical price context. Merely mentioning a price or having a closed Support
record is not sufficient. This module imports no simulation/test fixture.
"""

import re


_MONEY = re.compile(r"\bRM\s*\d[\d,]*(?:\.\d{2})?\b", re.IGNORECASE)
_POSITIVE = re.compile(r"\b(?:confirmed|verified)\b", re.IGNORECASE)
_UNCONFIRMED_PRICE = re.compile(
    r"(?:\b(?:price|package|quote|net\s+price)\b.{0,65}"
    r"\b(?:not\s+confirmed|unconfirmed|not\s+verified|unknown|pending)\b)"
    r"|(?:\b(?:cannot|can't|unable\s+to)\s+(?:confirm|verify)\b.{0,65}"
    r"\b(?:price|package|quote)\b)",
    re.IGNORECASE,
)
_PRICE_QUERY = re.compile(
    r"\b(?:price|pricing|package|rebate|discount|how\s+much|"
    r"monthly\s+(?:instalment|installment|payment|repayment)|"
    r"instalments?|installments?|loan|mortgage)\b",
    re.IGNORECASE,
)
_COMMUTE_QUERY = re.compile(
    r"\b(?:commut(?:e|ing)|drive|driving|travel\s+time|"
    r"minutes?|journey|traffic|distance|how\s+far|how\s+long)\b",
    re.IGNORECASE,
)


def resolved_price_quote(support_results):
    """Find a positively confirmed price; reject tentative/cancelled records."""
    # Runtime support_context returns newest entries first. An OPEN or an
    # inconclusive newer price check must not be overridden by an older quote.
    for item in support_results or []:
        if str(item.get("support_type", "")).upper() not in ("PRICING", "PACKAGE"):
            continue
        if str(item.get("status", "")).upper() != "RESOLVED":
            return None
        result = str(item.get("support_result") or "")
        if not (_MONEY.search(result) and _POSITIVE.search(result)):
            return None
        if _UNCONFIRMED_PRICE.search(result):
            return None
        return item
    return None


def price_request_pending(support_results):
    return any(
        str(item.get("status", "")).upper() == "OPEN"
        and str(item.get("support_type", "")).upper() in ("PRICING", "PACKAGE")
        for item in (support_results or [])
    )


def apply_evidence_priorities(workflow, latest_message, support_results):
    """Attach sales objectives and limited structured-output constraints.

    This NEVER turns a proposed viewing into an accepted appointment.
    Direct questions/objections always retain their existing stage and moves.
    """
    workflow = dict(workflow)
    quote = resolved_price_quote(support_results)
    question = str(latest_message or "")

    if quote:
        workflow["commercial_evidence_state"] = "PRICE_CONFIRMED"
        workflow["commercial_evidence_objective"] = (
            "An affirmative, resolved quote for this buyer is already available "
            "in verified_support_results. It takes precedence over older "
            "historical base price or rebate files. State the resolved amount "
            "directly when price is relevant; NEVER promise another price or "
            "package check. Use the known price to sell relevant real benefits, "
            "discuss budget, and if justified offer a low-pressure viewing. "
            "A viewing invitation is not a booking."
        )
        if _PRICE_QUERY.search(question):
            # Don't allow the model to relabel the *same* settled price as
            # another PRICING/PACKAGE Support Request. Other support types
            # remain available for genuinely different unknowns.
            workflow["blocked_support_types"] = ["PRICING", "PACKAGE"]
    elif price_request_pending(support_results):
        workflow["commercial_evidence_state"] = "PRICE_CHECK_PENDING"
        workflow["commercial_evidence_objective"] = (
            "A PRICING/PACKAGE support request is already OPEN. Do not create "
            "or promise a duplicate price check. Be clear about what is known, "
            "offer grounded comparison information, and avoid an unsupported "
            "current quote. Move the conversation forward where possible."
        )
        if _PRICE_QUERY.search(question):
            workflow["blocked_support_types"] = ["PRICING", "PACKAGE"]

    if _COMMUTE_QUERY.search(question):
        workflow["commute_answer_objective"] = (
            "Answer known Seberang Jaya location/connectivity facts NOW. "
            "Do not invent drive times, walking times, traffic or exact distances. "
            "If exact timing isn't available, give a useful qualitative "
            "comparison and invite checking the route from the customer's "
            "already stated origin/destination or suggest judging the site "
            "on a viewing. Do not repeatedly promise to 'check and get back' "
            "on the same commute question; no endless support loop."
        )
    return workflow
