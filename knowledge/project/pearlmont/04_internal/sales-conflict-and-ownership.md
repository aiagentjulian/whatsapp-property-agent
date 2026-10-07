# Pearlmont Sales Conflict & Ownership (Internal Only)

## Purpose

Operational guidance for cases where a customer may already have been contacted, served, registered, walked through, or appointed by another salesperson. This is internal support, not a customer qualification checklist or sales pitch.

## Customer-facing conduct

- Keep the interaction simple and professional. Never accuse or disparage another agent.
- Do not explain agency ownership, commission, protection windows, or internal conflict rules unless a human explicitly authorizes that disclosure.
- Questions that may help when naturally relevant include: “Has anyone contacted you before?”, “Has anyone served you before?”, and “How did you hear about the project?” They are optional, not a script. Do not ask all three mechanically.
- Do not block a genuine viewing merely because these details have not been collected.
- A suitable customer-facing response is: “I’ll help check the existing registration first so we don’t duplicate anything. Once that’s confirmed, we’ll continue from there.”

## Internal handling concepts

- A confirmed posted appointment has priority. Appointment recognition requires customer acknowledgement or acceptance through WhatsApp or equivalent accepted evidence.
- A missed or postponed appointment has a 3-calendar-day grace period.
- Walkthrough protection is 7 days.
- Sale cancellation / rebooking for the same project has a 14-day cooling-off period.

These are internal operational concepts. Do not turn them into customer-facing claims or infer ownership from partial information.

## Escalation and record safety

- If actual ownership cannot be verified by AI, require a human handoff with reason `SALES_OWNERSHIP_CONFLICT`.
- Once the handoff is complete, pause duplicate AI follow-up until a human or system explicitly returns ownership to AI.
- Do not create duplicate Lead Profiles or customer records.
- The human sales process must verify current CRM/registration evidence before resolving ownership or confirming a conflicting appointment.
