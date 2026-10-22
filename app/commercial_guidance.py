"""Dated commercial evidence for buyer pricing questions.

This file DOES NOT calculate or confirm a current customer quote. The dated
developer sales package is a historical reference until newer verification.
Do not replace the usual project Knowledge retrieval or Support Request.
"""

import re
from .knowledge import KNOWLEDGE

PRICE_INTENT = re.compile(
    r"\b(?:price|prices|pricing|how\s+much|starting\s+from|starts?\s+from|"
    r"rebate|discount|promo(?:tion)?|package|loan|mortgage|financ(?:e|ing)|"
    r"instal?ments?|installments?|down\s*payment|monthly\s+(?:payment|"
    r"commitment|costs?|repayment)|after\s+rebate|total\s+cost)\b",
    re.IGNORECASE,
)


def commercial_price_context(latest_message):
    """Offer historical price context on demand, never a live package claim.

    Read from project Knowledge so future updates to the source are inherited.
    """
    latest = latest_message or ""
    if not PRICE_INTENT.search(latest):
        return None
    # Maintenance alone is already a verified, separate ownership charge.
    # "How much is maintenance?" is not a request for a current sales package.
    if re.search(r"\b(?:maintenance|sinking\s+fund)\b", latest, re.IGNORECASE) and not re.search(
        r"\b(?:price|pricing|rebate|package|loan|mortgage|financ(?:e|ing)|"
        r"down\s*payment|instal?ments?|installments?|monthly\s+costs?|total\s+cost)\b",
        latest, re.IGNORECASE,
    ):
        return None

    package_path = KNOWLEDGE / "02_commercial/sales-package.md"
    base_path = KNOWLEDGE / "02_commercial/pricing.md"
    package_text = package_path.read_text(encoding="utf-8")
    base_text = base_path.read_text(encoding="utf-8")

    dated = re.search(r"^Current package date:\s*(.+)$", package_text, re.MULTILINE)
    if not dated:
        raise ValueError("Sales package source must identify its document date")
    date_label = dated.group(1).strip()
    base_values = [int(n) for n in re.findall(r"\bRM(\d+)k\s+base\b", base_text)]
    if not base_values:
        raise ValueError("Base pricing source has no usable historical figures")
    rebate_bands = list(dict.fromkeys(
        re.findall(r"^###\s+(\d+%)\s+rebate\s*$", package_text, re.MULTILINE)
    ))
    if not rebate_bands:
        raise ValueError("Sales package source has no rebate category headings")

    return {
        "status": "DATED_REFERENCE_NOT_VERIFIED_CURRENT",
        "documented_package_date": date_label,
        "package_source": package_path.relative_to(KNOWLEDGE).as_posix(),
        "base_source": base_path.relative_to(KNOWLEDGE).as_posix(),
        "documented_base_price_range": "RM%sk–RM%sk (original/base only)" %
                                       (min(base_values), max(base_values)),
        "documented_rebate_bands": rebate_bands,
        "sales_use": (
            "The package source is dated and NOT confirmed as today's active "
            "package. This is evidence of previous price/rebate structure, "
            "NOT a verified current effective starting price, active promotion, "
            "available unit or approved financing quote. Different blocks, "
            "floors, views and car parks carry different base/premium/eligibility. "
            "Answer the customer's actual price or financing question with "
            "clearly labelled historical base context where useful, then say "
            "the latest effective package/unit quote must be checked via "
            "SUPPORT_REQUEST when material. Do not over-defer facts already "
            "in verified Knowledge, and do not invent a post-rebate price by "
            "blindly applying a rebate percentage to the base range. "
            "Maintenance fee is separate from loan instalments."
        ),
    }
