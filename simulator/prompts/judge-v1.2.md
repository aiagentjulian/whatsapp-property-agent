Evaluate the AI Expert Property Sales Agent's actual early-stage job, then report end-to-end operations separately. This is not a property-sale completion test. Main AI success is reaching genuine APPOINTMENT READY and, when live execution is needed, handing off at the correct time with NONE/LOW sales work remaining. A suitable buyer can be ready even if exact unit, current price, or viewing slot still needs verification. Do not require every profile field. Do not reward weak early handoff or human sales rescue.

Use the transcript, per-turn AI readiness assessments, lead context, action/retrieval traces, retrieved Knowledge, and explicitly labeled `human_operations` fixture. Synthetic fixtures are not Pearlmont factual Knowledge and never imply real production capability. Evaluate whether the AI used useful retrieved information, not only whether retrieval found it. Do not penalize honest handling of missing sources. The Agent is not required to announce it is AI; if the customer asks directly, it must answer truthfully. A formal handoff pauses AI, and no AI response may follow it.

For this buyer, identify what mattered, what useful information the AI learned, and important information it missed. Judge whether the AI answered what it could and handled sourced context before handing off. Appointment readiness means enough fit, trust, and meaningful viewing/purchase intent that viewing is an appropriate next step; exact availability/pricing can remain operational. Strong signals include unit/floor/facing/carpark selection, conditional willingness to view if a concern is resolved, show-unit requests, weekend/time requests, and a suitable unit/package check tied to genuine intent. Don't equate any generic price question with readiness. Human Executor is bounded to one operational response per formal handoff. It may report a NOT_CONNECTED check result but that does not mean the requested operation was successfully completed. Mark `human_operational_task_completed` true only when a concrete fixture value actually supplied the requested task result.

Classify `sales_work_remaining_at_handoff`: NONE/LOW means operational execution is all or nearly all that remains; MEDIUM/HIGH means substantial AI-level sales work remains. The separate `human_sales_work_required` assesses what Human actually had to do after takeover. Don't let Human completion erase an early handoff. A successful appointment-ready handoff must have readiness at handoff, appropriate timing, and NONE/LOW sales work remaining. A non-convertible buyer correctly screened out is a good result.

Return only valid JSON with these required fields:
- buyer_primary_need: concise statement
- key_information_learned: array of useful facts actually learned from the conversation
- important_information_missed: array of relevant facts/blockers not learned; do not list irrelevant profile fields
- appointment_state and appointment_final_state: exact one of NO_VIEWING_INTENT, VIEWING_SUGGESTED, VIEWING_INTEREST, APPOINTMENT_IN_PROGRESS, APPOINTMENT_CONFIRMED; confirmation requires explicit customer acceptance of an available specific time/window
- appointment_readiness_final: NOT_READY, EMERGING, READY_FOR_APPOINTMENT, APPOINTMENT_IN_PROGRESS, APPOINTMENT_CONFIRMED
- ready_for_appointment: boolean
- first_ready_turn: earliest customer-visible transcript turn when viewing became a commercially appropriate next step, or null
- readiness_detection_correct: boolean; did AI identify that point in its per-turn assessment?
- readiness_state_at_handoff: readiness state at formal handoff, or null
- handoff_state, handoff_reason, handoff_turn, handoff_timing (TOO_EARLY, APPROPRIATE, TOO_LATE, NOT_NEEDED)
- sales_work_remaining_at_handoff: NONE, LOW, MEDIUM, HIGH
- ai_outcome: one of AI_APPOINTMENT_READY_SUCCESS, AI_APPOINTMENT_HANDOFF_SUCCESS, AI_DIRECT_APPOINTMENT_SUCCESS, AI_PROGRESS_BUT_NOT_READY, AI_EARLY_HANDOFF, AI_MISSED_READY_BUYER, AI_LOST_CONVERSION, BAD_FIT_CORRECTLY_IDENTIFIED
- human_handoff_executor_used: boolean
- human_operational_task: concise task or NONE
- human_sales_work_required: NONE, LOW, MEDIUM, HIGH
- human_operational_task_completed: boolean, true only when supported fixture task was completed
- appointment_readiness_detection, appointment_ready_progression, useful_information_capture, retrieved_knowledge_utilization scores: integer 0-5
- `scores`: all 20 integer 0-5 dimensions: customer_understanding, latest_message_responsiveness, qualification_discipline, selling_angle_relevance, objection_handling, unit_fit_judgment, buying_signal_detection, appointment_judgment, factual_accuracy, sales_naturalness, handoff_judgment, commercial_progression, appointment_readiness_detection, handoff_timing, handoff_reason_correctness, post_handoff_suppression, conversion_attribution, useful_information_capture, appointment_ready_progression, retrieved_knowledge_utilization
- strongest_ai_move, weakest_ai_move, unnecessary_qualification, missed_buying_signals, missed_selling_opportunity, retrieval_misses, retrieved_knowledge_not_used, factual_or_operational_overpromises, remaining_knowledge_gaps, critical_flags (array of {flag,evidence,turn}), summary, and a concrete improvement_recommendation

Use the eight AI outcome definitions exactly: `AI_APPOINTMENT_READY_SUCCESS` means AI recognized readiness and no formal handoff was needed yet; `AI_APPOINTMENT_HANDOFF_SUCCESS` means AI reached READY_FOR_APPOINTMENT or APPOINTMENT_IN_PROGRESS, handed off appropriately, and left NONE/LOW sales work; `AI_DIRECT_APPOINTMENT_SUCCESS` means AI obtained accepted appointment confirmation before handoff; `AI_PROGRESS_BUT_NOT_READY` means useful progress but not ready; `AI_EARLY_HANDOFF` means formal handoff before readiness or while MEDIUM/HIGH sales work remained; `AI_MISSED_READY_BUYER` means buyer became ready but AI failed to recognize or act on it; `AI_LOST_CONVERSION` means a convertible buyer disengaged/lost because of poor AI behavior; `BAD_FIT_CORRECTLY_IDENTIFIED` means a real mismatch was correctly not pushed to viewing.

Use only repository paths present in supplied retrieved material for any source recommendation; otherwise mark MISSING_SOURCE. Report the AI outcome even if Human later made progress. Clearly distinguish real Knowledge from simulator-only operations fixtures.
