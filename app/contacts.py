import re


def normalize_contact(value):
    return " ".join(re.findall(r"[a-z0-9]+", (value or "").lower()))


def is_allowlisted(contact, allowlist):
    target = normalize_contact(contact)
    if not target:
        return False
    return any(target == normalize_contact(entry) for entry in allowlist)
