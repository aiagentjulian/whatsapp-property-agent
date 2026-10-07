"""Strict role schemas shared by the Codex CLI and local response validation."""

def _object(properties):
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}


def _nullable(schema):
    return {"anyOf": [schema, {"type": "null"}]}


def _string():
    return {"type": "string"}


def _string_array():
    return {"type": "array", "items": {"type": "string"}}


SALES_SCORES = [
    "customer_understanding", "latest_message_responsiveness", "qualification_discipline",
    "selling_angle_relevance", "objection_handling", "unit_fit_judgment",
    "buying_signal_detection", "appointment_judgment", "factual_accuracy",
    "sales_naturalness", "handoff_judgment", "commercial_progression",
    "appointment_readiness_detection", "handoff_timing", "handoff_reason_correctness",
    "post_handoff_suppression", "conversion_attribution", "useful_information_capture",
    "appointment_ready_progression", "retrieved_knowledge_utilization",
    "support_request_judgment", "support_result_utilization", "support_resume_quality",
]
APPOINTMENT_STATES = [
    "NO_VIEWING_INTENT", "VIEWING_SUGGESTED", "VIEWING_INTEREST",
    "APPOINTMENT_IN_PROGRESS", "APPOINTMENT_CONFIRMED",
]
READINESS_STATES = [
    "NOT_READY", "EMERGING", "READY_FOR_APPOINTMENT",
    "APPOINTMENT_IN_PROGRESS", "APPOINTMENT_CONFIRMED",
]
HANDOFF_STATES = ["NO_HANDOFF", "HANDOFF_RECOMMENDED", "HANDOFF_REQUIRED", "HANDOFF_COMPLETED"]
HANDOFF_REASONS = [
    "OPERATIONAL_BOOKING", "UNIT_AVAILABILITY_VERIFICATION", "PRICING_OR_PACKAGE_VERIFICATION",
    "FINANCING_OR_ELIGIBILITY_REQUIRES_HUMAN", "SALES_OWNERSHIP_CONFLICT", "EXPLICIT_HUMAN_REQUEST",
    "COMPLAINT_OR_DISPUTE", "HIGH_RISK_FACTUAL_UNCERTAINTY", "OTHER",
]

LEAD_CONTEXT_FIELDS = (
    "lead_id", "name", "phone", "preferred_language", "lead_source", "source_detail",
    "campaign_source", "first_message_context", "purchase_purpose", "purchase_reason",
    "preferred_location", "preferred_property_type", "size_or_layout_preference", "important_features",
    "budget_range", "financing_context", "current_property_status", "purchase_timeline",
    "viewing_interest", "appointment_readiness", "primary_motivations", "decision_factors",
    "decision_participants", "active_concerns", "resolved_concerns", "competitor_or_comparison_projects",
    "sales_stage", "intent_level", "fit_assessment", "next_objective", "owner", "handoff_status",
    "handoff_reason", "last_progress", "next_action", "follow_up_needed", "follow_up_context",
    "conversation_summary", "last_customer_intent", "last_agent_action",
)
LEAD_CONTEXT_ARRAY_FIELDS = {
    "important_features", "primary_motivations", "decision_factors", "decision_participants",
    "active_concerns", "resolved_concerns", "competitor_or_comparison_projects",
}
LEAD_CONTEXT_SCHEMA = _object({
    field: _nullable({"type": "boolean"} if field == "follow_up_needed" else
                     _string_array() if field in LEAD_CONTEXT_ARRAY_FIELDS else _string())
    for field in LEAD_CONTEXT_FIELDS
})

ROLE_SCHEMAS = {
    "sales_agent": _object({
        "action": {"type": "string", "enum": [
            "ASK", "ANSWER", "POSITION", "HANDLE_OBJECTION", "NARROW_UNIT", "CLOSE_VIEWING",
            "SUPPORT_REQUEST", "HANDOFF", "MANDATORY_HANDOFF", "ACKNOWLEDGE / MAINTAIN",
        ]},
        "message": _string(),
        "support_request": _nullable(_string()),
        "support_context": _nullable(_object({
            "resume_stage": _string(), "resume_objective": _string(),
            "unresolved_customer_need": _string(), "sales_stage": _nullable(_string()),
        })),
        "lead_context": LEAD_CONTEXT_SCHEMA,
        "assessment": _object({
            "appointment_readiness": {"type": "string", "enum": READINESS_STATES},
            "handoff_state": {"type": "string", "enum": HANDOFF_STATES},
            "handoff_reason": _nullable({"type": "string", "enum": HANDOFF_REASONS}),
        }),
    }),
    "customer_simulator": _object({
        "message": _string(), "done": {"type": "boolean"},
        "appointment_state": {"type": "string", "enum": APPOINTMENT_STATES},
        "final_intent": {"type": "string", "enum": ["low", "medium", "high", "unknown"]},
    }),
    "human_handoff_executor": _object({
        "message": _string(),
        "operational_action": {"type": "string", "enum": [
            "VERIFY_OWNERSHIP", "VERIFY_AVAILABILITY", "VERIFY_SLOT", "VERIFY_PACKAGE",
            "ANSWER_FROM_SOURCE", "CONTINUE_SELLING", "NO_ACTION",
        ]},
        "sales_work_level": {"type": "string", "enum": ["NONE", "LOW", "MEDIUM", "HIGH"]},
        "operational_task_completed": {"type": "boolean"},
        "appointment_state": {"type": "string", "enum": APPOINTMENT_STATES},
    }),
}

JUDGE_SCHEMA_REQUIRED = (
    "scenario_id", "buyer_primary_need", "key_information_learned", "important_information_missed",
    "appointment_state", "appointment_final_state", "appointment_readiness_final", "ready_for_appointment",
    "first_ready_turn", "readiness_detection_correct", "readiness_state_at_handoff", "handoff_state",
    "handoff_type", "handoff_reason", "handoff_turn", "handoff_timing", "sales_work_remaining_at_handoff",
    "ai_outcome", "human_handoff_executor_used", "human_operational_task", "human_sales_work_required",
    "human_operational_task_completed", "support_requests", "support_requests_resolved",
    "support_resume_success_count", "support_results_used", "support_result_only_relayed",
    "failed_to_resume_selling", "appointment_ready_after_support", "support_unnecessary", "support_failure_modes",
    "commercial_progression", "scores", "strongest_ai_move", "weakest_ai_move", "unnecessary_qualification",
    "missed_buying_signals", "missed_selling_opportunity", "retrieval_misses", "retrieved_knowledge_not_used",
    "factual_or_operational_overpromises", "remaining_knowledge_gaps", "critical_flags", "summary",
    "improvement_recommendation", "appointment_confirmation", "conversion_attribution", "support_request_count",
    "support_resolved_count", "ai_final_sales_state", "post_handoff_ai_reply_violation", "handoff_reason_correct",
    "handoff_quality_score", "ai_finished_sales_job_before_handoff", "human_merely_completed_logistics",
    "human_rescued_conversion", "retrieved_knowledge_utilized", "conversion_analysis", "what_agent_did_well",
    "weak_or_wrong_sales_move", "better_next_move", "unsupported_factual_claims", "likely_issue_sources",
    "recommended_improvement",
)
JUDGE_ARRAY_FIELDS = {
    "key_information_learned", "important_information_missed", "support_failure_modes",
    "unnecessary_qualification", "missed_buying_signals", "missed_selling_opportunity",
    "retrieval_misses", "retrieved_knowledge_not_used", "factual_or_operational_overpromises",
    "remaining_knowledge_gaps", "what_agent_did_well", "unsupported_factual_claims", "likely_issue_sources",
}
JUDGE_PROPERTIES = {key: _string() for key in JUDGE_SCHEMA_REQUIRED}
for key in JUDGE_ARRAY_FIELDS:
    JUDGE_PROPERTIES[key] = _string_array()
for key in (
    "ready_for_appointment", "readiness_detection_correct", "human_handoff_executor_used",
    "human_operational_task_completed", "support_results_used", "support_result_only_relayed",
    "failed_to_resume_selling", "appointment_ready_after_support", "support_unnecessary",
    "appointment_confirmation", "post_handoff_ai_reply_violation", "handoff_reason_correct",
    "ai_finished_sales_job_before_handoff", "human_merely_completed_logistics", "human_rescued_conversion",
    "retrieved_knowledge_utilized",
):
    JUDGE_PROPERTIES[key] = {"type": "boolean"}
for key in ("first_ready_turn", "handoff_turn"):
    JUDGE_PROPERTIES[key] = _nullable({"type": "integer"})
for key in ("support_requests", "support_requests_resolved", "support_resume_success_count", "support_request_count", "support_resolved_count", "handoff_quality_score"):
    JUDGE_PROPERTIES[key] = {"type": "integer", "minimum": 0}
if "handoff_quality_score" in JUDGE_PROPERTIES:
    JUDGE_PROPERTIES["handoff_quality_score"]["maximum"] = 5
for key in ("appointment_state", "appointment_final_state"):
    JUDGE_PROPERTIES[key] = {"type": "string", "enum": APPOINTMENT_STATES}
JUDGE_PROPERTIES["appointment_readiness_final"] = {"type": "string", "enum": READINESS_STATES}
JUDGE_PROPERTIES["readiness_state_at_handoff"] = {"type": "string", "enum": READINESS_STATES}
JUDGE_PROPERTIES["handoff_state"] = {"type": "string", "enum": HANDOFF_STATES}
JUDGE_PROPERTIES["handoff_type"] = {"type": "string", "enum": ["APPOINTMENT_HANDOFF", "MANDATORY_OPERATIONAL_HANDOFF", "NO_FORMAL_HANDOFF"]}
JUDGE_PROPERTIES["handoff_timing"] = {"type": "string", "enum": ["TOO_EARLY", "APPROPRIATE", "TOO_LATE", "NOT_NEEDED"]}
JUDGE_PROPERTIES["sales_work_remaining_at_handoff"] = {"type": "string", "enum": ["NONE", "LOW", "MEDIUM", "HIGH"]}
JUDGE_PROPERTIES["human_sales_work_required"] = {"type": "string", "enum": ["NONE", "LOW", "MEDIUM", "HIGH"]}
JUDGE_PROPERTIES["ai_outcome"] = {"type": "string", "enum": [
    "AI_APPOINTMENT_READY_SUCCESS", "AI_APPOINTMENT_HANDOFF_SUCCESS", "AI_DIRECT_APPOINTMENT_SUCCESS",
    "AI_PROGRESS_BUT_NOT_READY", "AI_EARLY_HANDOFF", "AI_MISSED_READY_BUYER", "AI_LOST_CONVERSION",
    "MANDATORY_OPERATIONAL_HANDOFF", "BAD_FIT_CORRECTLY_IDENTIFIED",
]}
JUDGE_PROPERTIES["handoff_reason"] = _nullable({"type": "string", "enum": HANDOFF_REASONS})
JUDGE_PROPERTIES["conversion_attribution"] = {"type": "string", "enum": [
    "AI_DIRECT_CONVERSION", "AI_ASSISTED_HUMAN_CONFIRMATION", "HUMAN_LED_CONVERSION", "NO_CONVERSION", "BAD_FIT_NO_CONVERSION",
]}
JUDGE_PROPERTIES["commercial_progression"] = _object({"evidence": _string(), "assessment": _string()})
JUDGE_PROPERTIES["conversion_analysis"] = _object({
    "what_moved_buyer_forward": _string_array(),
    "what_reduced_conversion_probability": _string_array(),
    "where_conversion_was_won_or_lost": _string(),
})
JUDGE_PROPERTIES["recommended_improvement"] = _object({
    "category": _string(), "target_file": _nullable(_string()), "reason": _string(),
})
JUDGE_PROPERTIES["scores"] = _object({key: {"type": "integer", "minimum": 0, "maximum": 5} for key in SALES_SCORES})
JUDGE_PROPERTIES["critical_flags"] = {"type": "array", "items": _object({
    "flag": _string(), "evidence": _string(), "turn": _nullable({"type": "integer"}),
})}
ROLE_SCHEMAS["judge"] = _object(JUDGE_PROPERTIES)
