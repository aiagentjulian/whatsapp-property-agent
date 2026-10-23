"""Small, explicit sales-direction controller for the WhatsApp property agent.

This module chooses the sales objective and permissible move categories, not
customer-facing wording. It is deliberately read-only: the existing Lead
Profile and conversation history are the source of truth, so resetting a test
Lead also resets its workflow without a new database migration.
"""

import re


def _contains(text, patterns):
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _inbound_texts(latest_message, history):
    turns = [str(row.get("body", "")) for row in history[-28:]
             if row.get("direction") == "INBOUND"]
    if not turns or turns[-1] != latest_message:
        turns.append(latest_message)
    return turns


def _route(profile, customer_turns):
    # BOTH is intentionally not a third sales branch. When an old Lead has
    # that value, ask about the current primary purpose instead.
    purpose = profile.get("purchase_purpose")
    latest = customer_turns[-1] if customer_turns else ""
    simple_answer = latest.strip().lower().strip(".! ")
    if simple_answer in ("own stay", "for own stay", "self stay"):
        return "OWN_STAY"
    if simple_answer in ("investment", "for investment", "invest"):
        return "INVESTMENT"
    if _contains(latest, (r"\b(?:actually|instead|mainly|primarily|rather)\b",)):
        if _contains(latest, (r"\bown\s*stay\b", r"\blive\s+(?:there|in\s+it)\b")):
            return "OWN_STAY"
        if _contains(latest, (r"\binvest(?:ment|ing)?\b",)):
            return "INVESTMENT"
    if purpose in ("OWN_STAY", "INVESTMENT"):
        return purpose
    for text in reversed(customer_turns):
        if _contains(text, (r"\bown\s*stay\b", r"\bfor\s+(?:my|our)\s+(?:own\s+)?(?:home|stay)\b",
                            r"\blive\s+(?:there|in\s+it)\b")):
            return "OWN_STAY"
        if _contains(text, (r"\binvest(?:ment|ing)?\b", r"\brental\s+(?:income|yield)\b",
                            r"\bcapital\s+(?:gain|appreciation)\b")):
            return "INVESTMENT"
    return "UNKNOWN"


def _has_household(customer_turns):
    return any(_contains(text, (
        r"\b(?:wife|husband|spouse|partner|girlfriend|boyfriend|parents?|children|kids|family|couple)\b",
        r"\b(?:alone|myself|just me|two of us|both of us|only me|three of us|four of us)\b",
    )) for text in customer_turns)


def _has_investment_goal(customer_turns, profile):
    fields = " ".join(str(profile.get(key) or "") for key in
                      ("purchase_reason", "primary_motivations", "decision_factors"))
    return any(_contains(text, (
        r"\brental\b", r"\brent(?:ing|al)?\s+(?:income|yield|return|out)\b",
        r"\bcapital\s+(?:gain|appreciation)\b", r"\bresell\b",
        r"\bprice\s+appreciation\b",
    )) for text in customer_turns + [fields])


def _has_purchase_reason(customer_turns, profile):
    if profile.get("purchase_reason"):
        return True
    return any(_contains(text, (
        r"\bupgrad(?:e|ing)\b", r"\bfirst\s+(?:home|property)\b",
        r"\brelocat(?:e|ion|ing)\b", r"\bmoving\s+(?:to|closer|out)\b",
    )) for text in customer_turns)


def _buying_question(message):
    return _contains(message, (
        r"\b(?:price|pricing|how much|budget|monthly|instalment|installment|loan|financing|mortgage)\b",
        r"\b(?:floor\s*plan|floorplan|show\s*unit|parking|car\s*park|rebate|booking\s*fee)\b",
        r"\b(?:available|availability|maintenance\s*fee|completion|handover|deposit)\b",
    ))


def _viewing_request(message, history):
    if _contains(message, (
        r"\b(?:viewing|showroom|show\s*unit|visit|site\s*visit|appointment)\b",
        r"\b(?:come\s+(?:see|look)|see\s+(?:the\s+)?(?:unit|showroom))\b",
    )):
        return True
    prior = next((str(row.get("body") or "") for row in reversed(history[-8:])
                  if row.get("direction") == "OUTBOUND"), "")
    return bool(_contains(prior, (
        r"\b(?:viewing|showroom|come\s+see|arrange\s+a\s+visit)\b",
    )) and (_contains(message, (
        r"^(?:yes|yeah|sure|okay|ok|can|sounds\s+good)(?:\b|[.!])",
    )) or _contains(message, (
        # Buyers often answer a salesperson's date-choice question directly
        # ("Saturday would suit us") instead of repeating "yes" or "viewing".
        # Only treat a positive preference as acceptance when the prior
        # salesperson turn was itself about arranging a visit.
        r"\b(?:saturday|sunday|weekdays?|weekends?)\s+(?:works?|suits?|would\s+(?:work|suit)|"
        r"is\s+(?:good|fine|better|best))\b",
        r"\b(?:prefer|free|available)\s+(?:on\s+)?(?:saturday|sunday|weekdays?|weekends?)\b",
    ))))


def _specific_property_question(message):
    return _contains(message, (
        r"\b(?:where\s+is|location|address|how\s+far|how\s+near|which\s+area)\b",
        r"\b(?:commut(?:e|ing)|how\s+long|travel\s+time|driving\s+time|drive\s+to)\b",
        r"\b(?:freehold|leasehold|tenure|facilities|facility|pool|gym|school|floor\s*plan|layout|balcony)\b",
        r"\b(?:how\s+big|sq\s*ft|sqft|rooms|bedrooms|car\s*park|parking|quality|developer)\b",
    ))


def _objection(message):
    return _contains(message, (
        r"\b(?:too\s+(?:small|expensive|far)|don't\s+like|not\s+interested|worried|concerned)\b",
        r"\b(?:seems\s+(?:small|expensive)|can't\s+afford)\b",
    ))


def _warm_interest(customer_turns):
    # A material purchase enquiry or volunteered positive interest can justify
    # inviting a viewing. A bare "own stay"/"investment" answer cannot.
    return any(_buying_question(text) or _contains(text, (
        r"\b(?:sounds\s+good|looks\s+good|i\s+like|interested\s+in|quite\s+interested)\b",
    )) for text in customer_turns)


def _purchase_topics(customer_turns):
    """Qualitative signs of serious consideration, not a conversion score."""
    patterns = {
        "price_package": r"\b(?:price|pricing|rebate|package|discount|starting\s+from)\b",
        "monthly_financing": r"\b(?:monthly|loan|mortgage|instal?ments?|installments?|financing|maintenance)\b",
        "unit_details": r"\b(?:floor\s*plan|layout|floor|facing|car\s*park|parking|bedrooms?)\b",
        "location_commute": r"\b(?:location|commute|workplace|nearby|seberang\s+jaya|perai)\b",
    }
    return [name for name, pattern in patterns.items()
            if any(re.search(pattern, message, flags=re.IGNORECASE)
                   for message in customer_turns)]


def plan_sales_turn(latest_message, profile, history):
    """Direct the next sales turn without deciding the customer's exact words.

    Buyer questions, objections and viewing requests override stage ordering.
    The structured output schema uses `allowed_moves` to limit the model's
    sales-move category; the model still writes the natural reply and may
    handle a buyer's actual questions.
    """
    customer_turns = _inbound_texts(latest_message, history)
    route = _route(profile, customer_turns)
    latest = str(latest_message or "")
    purchase_topics = _purchase_topics(customer_turns)
    if _viewing_request(latest, history):
        return {
            "route": route, "stage": "VIEWING",
            "objective": ("Respond to the buyer's real viewing interest. Invite or progress "
                          "arrangement naturally. Only hand off for booking when they have "
                          "agreed to a viewing; an invitation is not a booking."),
            "allowed_moves": ["VIEWING", "ANSWER", "HANDLE", "GIVE_SPACE"],
        }
    if _objection(latest):
        return {
            "route": route, "stage": "OBJECTION",
            "objective": ("Acknowledge and handle the buyer's actual concern with verified "
                          "project evidence, without arguing or returning to discovery."),
            "allowed_moves": ["HANDLE", "ANSWER", "POSITION", "GIVE_SPACE"],
        }
    if _specific_property_question(latest) and not _buying_question(latest):
        return {
            "route": route, "stage": "DIRECT_QUESTION",
            "objective": ("Answer the buyer's specific project question truthfully first. "
                          "Do not insist on household or investment discovery to provide facts."),
            "allowed_moves": ["ANSWER", "HANDLE", "POSITION", "GIVE_SPACE"],
        }
    if _buying_question(latest):
        serious = len(purchase_topics) >= 2 and route != "UNKNOWN"
        return {
            "route": route, "stage": "BUYING_CONSIDERATION",
            "purchase_topics": purchase_topics,
            "objective": ("Answer the buyer's specific purchasing question FIRST using verified "
                          "facts and dated commercial context. Never present an older price, "
                          "rebate or promotion as a current confirmed package. If their exact "
                          "current quote is unavailable, clearly separate useful documented "
                          "base-price context from the still-required current package check, "
                          "and make the verification step concrete. Do not restart discovery, "
                          "or promise loan eligibility or returns. "
                          + ("This buyer has engaged with multiple practical purchase topics. "
                             "AFTER providing a useful answer or concrete quote-resolution "
                             "step, consider a brief low-pressure viewing invitation as an "
                             "OPTION, rather than endlessly waiting for the buyer to ask. "
                             "Do NOT claim a booking or use viewing to evade unanswered "
                             "cost questions." if serious else
                             "A single buying question does not prove viewing readiness; "
                             "keep the focus on answering it.")),
            "allowed_moves": ["ANSWER", "POSITION", "HANDLE", "VIEWING", "GIVE_SPACE"],
        }
    if route == "UNKNOWN":
        return {
            "route": route, "stage": "PURPOSE",
            "objective": ("Give a concise orientation to the real development. Discover "
                          "whether the main buying purpose is OWN_STAY or INVESTMENT "
                          "without offering BOTH as a third route. Do not survey "
                          "features or list unrelated facilities."),
            "allowed_moves": ["ANSWER", "EXPLORE", "HANDLE", "GIVE_SPACE"],
        }
    if route == "INVESTMENT" and not _has_investment_goal(customer_turns, profile):
        return {
            "route": route, "stage": "INVESTMENT_OBJECTIVE",
            "objective": ("Understand the investor's primary goal: rental income or "
                          "capital gain. Do not speculate about returns. Ask one "
                          "relevant question; do not run a full investor questionnaire."),
            "allowed_moves": ["ANSWER", "EXPLORE", "HANDLE", "GIVE_SPACE"],
        }
    if route == "OWN_STAY" and not (_has_household(customer_turns) or
                                    _has_purchase_reason(customer_turns, profile)):
        return {
            "route": route, "stage": "HOUSEHOLD",
            "objective": ("Find out who would actually live in the home (self, couple "
                          "or family) so you can make relevant selling points. Do "
                          "NOT ask first home versus upgrade; first-time ownership "
                          "belongs in financing discussion when it matters."),
            "allowed_moves": ["ANSWER", "EXPLORE", "HANDLE", "GIVE_SPACE"],
        }
    warm = _warm_interest(customer_turns)
    serious = warm and len(purchase_topics) >= 2
    return {
        "route": route, "stage": "WARM_INTEREST" if warm else "PRESENT_VALUE",
        "purchase_topics": purchase_topics,
        "objective": ("The buyer has supplied a usable motivation or household "
                      "detail. Advance the sale: choose a truthful, specific property "
                      "benefit relevant to it, explain a realistic personal benefit, "
                      "or give a concrete buying-comparison step. Do not ask another "
                      "broad preference/upgrade question as a substitute for selling. "
                      "An 'upgrade' is not proof that 900 sqft offers more room. "
                      "A first-time buyer question is appropriate only when "
                      "financing is being considered. Respond to objections "
                      "and customer questions directly. "
                      + ("They have considered several concrete purchase factors. "
                         "If their essential questions are answered or a specific "
                         "commercial verification step is underway, naturally OFFER a "
                         "low-pressure viewing as one possible next step now. Do not "
                         "automatically arrange it or claim any slot confirmed." if serious
                         else "Their engagement permits a low-pressure viewing invitation, "
                         "not an assumed booking." if warm else
                         "Their buying interest is not yet established; do not push "
                         "a viewing simply because they disclosed a household or purpose.")),
        "allowed_moves": (["POSITION", "HANDLE", "VIEWING", "GIVE_SPACE"]
                          if warm else ["POSITION", "HANDLE", "GIVE_SPACE"]),
    }
