#!/usr/bin/env python3
"""Pearlmont Simulator V1.5: regression-test current Brain and Skills guidance."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SIM=ROOT/"simulator"; KNOW=ROOT/"knowledge/project/pearlmont"
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_v1 as common

CONFIG=json.loads((SIM/"config.json").read_text())
VERSION="1.5"
AGENT_CONTEXT_PATHS=["brain/AGENT.md","brain/SALES_FLOW.md","brain/INTENT_MODEL.md","brain/LEAD_PROFILE.md","brain/RESPONSE_RULES.md","brain/HANDOFF_RULES.md","skills/decide-next-action.md","skills/request-human-support.md","skills/retrieve-project-knowledge.md","skills/update-lead-profile.md","skills/handoff-to-human.md"]
PROTECTED_PATHS=("brain","skills","knowledge/project/pearlmont")
RUN_SOURCE_COMMIT=None
RUN_SOURCE_HASHES={}
PROTECTED_BEFORE=None
READINESS=("NOT_READY","EMERGING","READY_FOR_APPOINTMENT","APPOINTMENT_IN_PROGRESS","APPOINTMENT_CONFIRMED")
HANDOFF=("NO_HANDOFF","HANDOFF_RECOMMENDED","HANDOFF_REQUIRED","HANDOFF_COMPLETED")
REASONS=("OPERATIONAL_BOOKING","UNIT_AVAILABILITY_VERIFICATION","PRICING_OR_PACKAGE_VERIFICATION","FINANCING_OR_ELIGIBILITY_REQUIRES_HUMAN","SALES_OWNERSHIP_CONFLICT","EXPLICIT_HUMAN_REQUEST","COMPLAINT_OR_DISPUTE","HIGH_RISK_FACTUAL_UNCERTAINTY","OTHER")
ATTRIBUTION=("AI_DIRECT_CONVERSION","AI_ASSISTED_HUMAN_CONFIRMATION","HUMAN_LED_CONVERSION","NO_CONVERSION","BAD_FIT_NO_CONVERSION")
AI_OUTCOMES=("AI_APPOINTMENT_READY_SUCCESS","AI_APPOINTMENT_HANDOFF_SUCCESS","AI_DIRECT_APPOINTMENT_SUCCESS","AI_PROGRESS_BUT_NOT_READY","AI_EARLY_HANDOFF","AI_MISSED_READY_BUYER","AI_LOST_CONVERSION","MANDATORY_OPERATIONAL_HANDOFF","BAD_FIT_CORRECTLY_IDENTIFIED")
SCORES=common.DIMENSIONS+["appointment_readiness_detection","handoff_timing","handoff_reason_correctness","post_handoff_suppression","conversion_attribution","useful_information_capture","appointment_ready_progression","retrieved_knowledge_utilization","support_request_judgment","support_result_utilization","support_resume_quality"]
JUDGE_REQUIRED=("appointment_state","appointment_readiness_final","ready_for_appointment","first_ready_turn","readiness_detection_correct","readiness_state_at_handoff","handoff_timing","sales_work_remaining_at_handoff","ai_outcome","support_resume_success_count","support_results_used","support_result_only_relayed","failed_to_resume_selling","appointment_ready_after_support","support_failure_modes","critical_flags","summary","scores")

def validate_judge(j):
    if not isinstance(j,dict): return ["response is not an object"]
    errors=[f"missing field {k}" for k in JUDGE_REQUIRED if k not in j]
    scores=j.get("scores")
    if not isinstance(scores,dict): return errors+["scores is not an object"]
    for key in SCORES:
        value=scores.get(key)
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not 0<=value<=5: errors.append(f"missing or invalid score {key}")
    if "critical_flags" in j and not isinstance(j["critical_flags"],list): errors.append("critical_flags is not an array")
    return errors

def ask_judge(provider,system,user):
    errors=[]
    for attempt in range(2):
        prompt=system if attempt==0 else system+"\n\nYour prior response failed schema validation: "+"; ".join(errors)+". Return complete JSON including every required field and all 23 scores (integer 0-5)."
        try: result=common.extract_json(provider.ask("judge",prompt,user))
        except Exception as e: errors=[f"invalid JSON/provider response: {type(e).__name__}: {e}"]; continue
        errors=validate_judge(result)
        if not errors: return result
    raise RuntimeError("Judge response invalid after one schema retry: "+"; ".join(errors))

def enum(value, allowed, default):
    s=str(value or "").upper().strip().replace("-","_")
    return s if s in allowed else default

def readiness(value): return enum(value,READINESS,"NOT_READY")
def reason(value): return enum(value,REASONS,"OTHER") if value else None
def app_state(value): return common.normalize_appointment_state(value)

def retrieve(message, scenario, limit=4):
    q=(message+" "+scenario["title"]+" "+scenario.get("critical_facts","")).lower()
    conflict_terms=("another agent","property agent","existing agent","already contacted","agent contacted","previous agent","registration","registered","ownership","duplicate follow-up","duplicate follow up","served before","serviced")
    is_conflict=any(t in q for t in conflict_terms)
    catalog=[
      ("knowledge/project/pearlmont/04_internal/sales-conflict-and-ownership.md",["another agent","property agent","existing agent","already contacted","agent contacted","previous agent","registration","registered","ownership","duplicate follow-up","duplicate follow up","served before","serviced"],"internal"),
      ("knowledge/project/pearlmont/01_facts/overview.md",["pearlmont","project","completion","developer","maintenance","freehold","units"],"customer"),
      ("knowledge/project/pearlmont/01_facts/unit-and-layout.md",["900","sqft","layout","room","bedroom","floor","facing","sea view","view","unit","type","balcony"],"customer"),
      ("knowledge/project/pearlmont/01_facts/risks-and-sensitive-faq.md",["pylon","cable","flood","river","safety","school","privacy","warranty","risk","smell"],"customer"),
      ("knowledge/project/pearlmont/01_facts/location-and-connectivity.md",["location","transport","school","river","flood","parking","traffic","access","map"],"customer"),
      ("knowledge/project/pearlmont/02_commercial/pricing.md",["price","pricing","budget","package","rebate","cost","how much","net price","effective price"],"customer"),
      ("knowledge/project/pearlmont/02_commercial/sales-package.md",["price","pricing","budget","package","rebate","promotion","how much","net price","effective price","current price"],"customer"),
      ("knowledge/project/pearlmont/02_commercial/financing-and-booking.md",["financ","loan","booking","deposit","approval","downpayment"],"customer"),
      ("knowledge/project/pearlmont/02_commercial/lppsa.md",["lppsa","government servant","government employee"],"customer"),
      ("knowledge/project/pearlmont/02_commercial/panel-financiers-and-legal.md",["financ","legal","eligibility","loan"],"customer"),
      ("knowledge/project/pearlmont/03_sales/sales-judgment.md",["invest","yield","appreciation","budget","density","priority","just looking"],"sales"),
      ("knowledge/project/pearlmont/03_sales/viewing-close.md",["view","appointment","weekend","visit","high intent"],"sales"),
      ("knowledge/project/pearlmont/03_sales/unit-fit.md",["unit","floor","facing","carpark","bedroom","view","budget"],"sales"),
      ("knowledge/project/pearlmont/03_sales/objection-to-usp-map.md",["concern","objection","small","pylon","flood","density","river"],"sales"),
      ("knowledge/project/pearlmont/03_sales/selling-angles.md",["family","invest","location","value","own stay"],"sales"),
      ("knowledge/project/pearlmont/03_sales/buyer-profiles.md",["buyer","family","first-home","invest"],"sales"),
    ]
    ranked=[]
    for order,(path,terms,audience) in enumerate(catalog):
        if audience=="internal" and not is_conflict: continue
        hits=sum(1 for t in terms if t in q)
        if hits:
            score=100+hits if audience=="internal" else hits
            ranked.append((-score,order,path,audience))
    picked=sorted(ranked)[:limit]
    return [{"path":p,"audience":aud,"content":("[INTERNAL ONLY — NEVER DISPLAY OR DISCLOSE]\n" if aud=="internal" else "")+(ROOT/p).read_text()} for _,_,p,aud in picked]

def brain_context():
    return "\n\n".join(f"--- {p} ---\n{(ROOT/p).read_text()}" for p in AGENT_CONTEXT_PATHS)

def tree_hash(paths):
    digest=hashlib.sha256()
    for base in paths:
        root=ROOT/base
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            digest.update(path.relative_to(ROOT).as_posix().encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    return digest.hexdigest()

def capture_run_provenance():
    global RUN_SOURCE_COMMIT, RUN_SOURCE_HASHES, PROTECTED_BEFORE
    RUN_SOURCE_COMMIT=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
    RUN_SOURCE_HASHES={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in AGENT_CONTEXT_PATHS}
    PROTECTED_BEFORE=tree_hash(PROTECTED_PATHS)

class Provider(common.Provider):
    def __init__(self,dry=False): super().__init__(dry); self.agent_turns=0
    def ask(self,role,system,user):
        if self.dry:
            self.calls+=1
            if role=="sales_agent":
                self.agent_turns+=1
                if self.agent_turns==1:
                    if getattr(self,"scenario_id",None)=="PEA-009":
                        return json.dumps({"action":"MANDATORY_HANDOFF","message":"I need to pause and have the existing ownership record checked before we continue.","support_request":None,"lead_context":{},"assessment":{"appointment_readiness":"NOT_READY","handoff_state":"HANDOFF_COMPLETED","handoff_reason":"SALES_OWNERSHIP_CONFLICT"}})
                    try:
                        payload=json.loads(user); latest=next((m.get("message","") for m in reversed(payload.get("history",[])) if m.get("speaker")=="customer"),"")
                    except Exception: latest=""
                    q=latest.lower()
                    request="Please verify the detailed floor-plan layout clarification."
                    if "carpark" in q or "car park" in q: request="Please verify whether an available sea-facing option has two car parks."
                    elif "yield" in q or "appreciate" in q or "rental" in q: request="Please verify what rental or investment information is available."
                    elif "lppsa" in q or "government servant" in q: request="Please clarify the LPPSA reference and what can be verified about eligibility."
                    elif "dense" in q or "crowded" in q: request="Please verify the residential access and corridor arrangement."
                    elif "budget" in q or "sea view" in q: request="Please verify an available sea-view unit and package matching the stated budget."
                    elif "flood" in q or "pylon" in q or "cable" in q: request="Please verify the available technical document summary for flood and high-tension concerns."
                    if getattr(self,"scenario_id",None)=="PEA-007": request="Please verify the available technical document summary for flood and high-tension concerns."
                    return json.dumps({"action":"SUPPORT_REQUEST","message":"","support_request":request,"lead_context":{},"assessment":{"appointment_readiness":"EMERGING","handoff_state":"NO_HANDOFF"}})
                if self.agent_turns==2:
                    try:
                        payload=json.loads(user); result=payload.get("resolved_support_results",[])[-1]["verified_answer"]
                    except Exception: result="The requested item is not verified by the simulator fixture."
                    return json.dumps({"action":"POSITION","message":"I checked that for you: "+result+" Based on the priorities you mentioned, this gives us a clearer option to assess in person. Would a viewing help you decide?","lead_context":{},"assessment":{"appointment_readiness":"EMERGING","handoff_state":"NO_HANDOFF"}})
                return json.dumps({"action":"HANDOFF","message":"That option seems worth viewing. I can arrange the operational details for you.","lead_context":{},"assessment":{"appointment_readiness":"READY_FOR_APPOINTMENT","handoff_state":"HANDOFF_COMPLETED","handoff_reason":"OPERATIONAL_BOOKING"}})
            if role=="customer_simulator":
                if '"owner": "HUMAN"' in user:
                    self.agent_turns=0
                    return json.dumps({"message":"Yes, can arrange that viewing.","done":True,"appointment_state":"APPOINTMENT_CONFIRMED","final_intent":"high"})
                return json.dumps({"message":"Okay, I can consider viewing.","done":False,"appointment_state":"VIEWING_INTEREST","final_intent":"high"})
            if role=="human_handoff_executor": return json.dumps({"message":"I’ll check the available simulator fixture and confirm what it establishes.","operational_action":"NO_ACTION","sales_work_level":"LOW","appointment_state":"NO_VIEWING_INTENT","operational_task_completed":False})
            if role=="judge": self.agent_turns=0
            return json.dumps(dry_judgment())
        return super().ask(role,system,user)

def dry_judgment():
    return {"appointment_state":"APPOINTMENT_CONFIRMED","appointment_readiness_final":"READY_FOR_APPOINTMENT","ready_for_appointment":True,"first_ready_turn":2,"readiness_detection_correct":True,"readiness_state_at_handoff":"READY_FOR_APPOINTMENT","handoff_state":"HANDOFF_COMPLETED","handoff_reason":"OPERATIONAL_BOOKING","handoff_turn":4,"handoff_timing":"APPROPRIATE","handoff_reason_correct":True,"handoff_quality_score":5,"ai_final_sales_state":"READY_FOR_APPOINTMENT","human_handoff_executor_used":True,"appointment_final_state":"APPOINTMENT_CONFIRMED","conversion_attribution":"AI_ASSISTED_HUMAN_CONFIRMATION","ai_outcome":"AI_APPOINTMENT_HANDOFF_SUCCESS","sales_work_remaining_at_handoff":"LOW","human_sales_work_required":"LOW","human_operational_task_completed":False,"human_operational_task":"OPERATIONAL_BOOKING","ai_finished_sales_job_before_handoff":True,"human_merely_completed_logistics":True,"human_rescued_conversion":False,"post_handoff_ai_reply_violation":False,"buyer_primary_need":"dry-run","key_information_learned":[],"important_information_missed":[],"retrieved_knowledge_utilized":True,"support_requests":1,"support_requests_resolved":1,"support_resume_success_count":1,"support_results_used":True,"support_result_only_relayed":False,"failed_to_resume_selling":False,"appointment_ready_after_support":True,"support_unnecessary":False,"support_failure_modes":[],"scores":{k:3 for k in SCORES},"critical_flags":[],"conversion_analysis":{"what_moved_buyer_forward":[],"what_reduced_conversion_probability":[],"where_conversion_was_won_or_lost":"dry-run"},"what_agent_did_well":[],"weak_or_wrong_sales_move":"dry-run","better_next_move":"dry-run","missed_buying_signals":[],"unnecessary_qualification":[],"unsupported_factual_claims":[],"retrieval_misses":[],"likely_issue_sources":[],"recommended_improvement":{"category":"none","target_file":None,"reason":"dry-run"},"remaining_knowledge_gaps":[],"summary":"support-resume and formal handoff transport smoke test"}

def prompts():
    agent=("You are the Pearlmont WhatsApp Expert Property Sales Agent. Follow the accepted Brain and Skills context:\n"+brain_context()+"\n\nYour job is to understand the buyer, use relevant sourced facts, answer what you can, handle reasonable concerns, and progress a genuinely suitable buyer to a viewing. Appointment-ready handoff is a successful AI outcome when only live operational execution remains. Do not hand off a general question before doing useful sales work. Answer general price questions with supportable retrieved context and caveats; explain sourced LPPSA references before referring only individual eligibility for verification. Readiness does not require every profile field or exact price/availability. Once ready, avoid more generic qualification. Keep the customer experience continuous and natural: do not announce AI or say 'my boss'; use a brief natural pause/confirmation phrase when handing off. If asked directly whether you are AI/bot, answer truthfully. Never invent live price, package validity, inventory, financing approval, safety assurance, legal eligibility, or availability. A support result tagged SIMULATOR_SYNTHETIC_VERIFIED_FIXTURE is verified for this simulated conversation; use its scoped answer naturally as confirmed within the scenario, do not ask again for the same fact, do not tell the buyer it is unverified, and never claim it came from a real live production system or disclose the internal fixture tag. Internal-only source content must never be exposed. If you need a factual or operational check while you still own the sales conversation, use SUPPORT_REQUEST with a concise internal support_request; this does not change owner or pause you, and must have an empty customer-facing message. If the buyer asks both for factual documents/details and for a person, first use SUPPORT_REQUEST to retrieve the answer to the factual part, explain it and check whether their concern is resolved; if they still explicitly require a person or policy requires ownership transfer, use MANDATORY_HANDOFF after that response. Do not send the customer to a human merely because factual verification is needed. After a support result appears in history, use it in relevant customer language, connect it to the buyer's need, and continue selling. Do not repeat a resolved request. Use HANDOFF only when the buyer is appointment ready and only operational appointment execution remains; use MANDATORY_HANDOFF only for a required SALES_OWNERSHIP_CONFLICT, EXPLICIT_HUMAN_REQUEST, COMPLAINT_OR_DISPUTE, or policy transfer before readiness. The runner records HUMAN owner and pauses AI for either formal transfer. Return JSON only: {\"action\":\"ASK|ANSWER|POSITION|HANDLE_OBJECTION|NARROW_UNIT|CLOSE_VIEWING|SUPPORT_REQUEST|HANDOFF|MANDATORY_HANDOFF|ACKNOWLEDGE / MAINTAIN\",\"message\":\"customer-facing text; empty for SUPPORT_REQUEST\",\"support_request\":\"specific internal check or null\",\"lead_context\":{},\"assessment\":{\"appointment_readiness\":\"NOT_READY|EMERGING|READY_FOR_APPOINTMENT|APPOINTMENT_IN_PROGRESS|APPOINTMENT_CONFIRMED\",\"handoff_state\":\"NO_HANDOFF|HANDOFF_RECOMMENDED|HANDOFF_REQUIRED|HANDOFF_COMPLETED\",\"handoff_reason\":\"OPERATIONAL_BOOKING|UNIT_AVAILABILITY_VERIFICATION|PRICING_OR_PACKAGE_VERIFICATION|FINANCING_OR_ELIGIBILITY_REQUIRES_HUMAN|SALES_OWNERSHIP_CONFLICT|EXPLICIT_HUMAN_REQUEST|COMPLAINT_OR_DISPUTE|HIGH_RISK_FACTUAL_UNCERTAINTY|OTHER|null\"}}. Assessment is internal only; the hidden scenario and support fixtures are not available to you except when returned through an internal support result.")
    return agent,(SIM/"prompts/customer-simulator-v1.1.md").read_text(),(SIM/"prompts/human-handoff-executor.md").read_text(),(SIM/"prompts/judge-v1.4.md").read_text()

def support_fixture(scenario, request):
    fixtures=scenario.get("human_operations",{}).get("support_fixtures",{})
    text=str(request or "").lower()
    aliases={"layout":("layout","floor plan","floor-plan","bedroom","room","shareable type a","pdf"),"technical_risk":("flood","pylon","cable","risk","technical","document","site plan"),"payment_example":("instalment","installment","monthly payment","loan illustration"),"show_unit":("show unit","viewing arrangements","viewing access"),"lppsa_pricing":("current price","price options","package validity","effective starting price"),"corridor_access":("corridor","floor plan","share a plan","show the corridor"),"weekend_package":("current package","latest package","saturday viewing","current effective","package validity","post-rebate","starting price"),"facilities":("facilities","clubhouse","pay-per-use"),"pricing":("price","pricing","package","post-rebate","starting price"),"two_carpark":("carpark","car park","2 bay","two bay","sea facing"),"investment":("yield","appreciation","rental","investment evidence","investment data"),"lppsa":("lppsa","eligibility","financing"),"access":("access","corridor","tower","lift"),"budget_view":("budget","package","sea view","unit","price")}
    for key,terms in aliases.items():
        if key in fixtures and any(t in text for t in terms): return key,fixtures[key]
    return None,None

def human_system(base, reason_value):
    task={"OPERATIONAL_BOOKING":"verify available viewing slots and complete booking only if the fixture supports it","UNIT_AVAILABILITY_VERIFICATION":"check fixture unit availability and report exactly what it establishes","PRICING_OR_PACKAGE_VERIFICATION":"check the fixture for verified current package/unit price and distinguish any missing values","SALES_OWNERSHIP_CONFLICT":"verify the synthetic ownership fixture without disclosing internal policy","FINANCING_OR_ELIGIBILITY_REQUIRES_HUMAN":"check only explicit individual eligibility fixture values","HIGH_RISK_FACTUAL_UNCERTAINTY":"check whether the fixture supplies an approved answer"}.get(reason_value,"perform only the specific operational check supported by the fixture")
    return base+"\n\nHandoff reason: "+str(reason_value)+". Your primary task: "+task+". Also inspect the latest customer messages and complete any additional operational request they make if the same explicit fixture supports it (for example, check a viewing slot when the handoff also concerns price/package). You may only act now because HANDOFF_COMPLETED has been recorded. The AI owner is permanently paused. Clearly state when a fixture cannot verify the requested item. Do not shift into sales rescue unless the Judge-visible transcript requires accounting for sales work already remaining."

def classify_ai_outcome(judge, scenario, handoff_state, confirmed, ai_confirmed_before_handoff):
    if not scenario["conversion"]["convertible"] and judge.get("good_judgment", True):
        return "BAD_FIT_CORRECTLY_IDENTIFIED"
    if confirmed and (handoff_state != "HANDOFF_COMPLETED" or ai_confirmed_before_handoff):
        return "AI_DIRECT_APPOINTMENT_SUCCESS"
    work=enum(judge.get("sales_work_remaining_at_handoff"),("NONE","LOW","MEDIUM","HIGH"),"LOW")
    at_handoff=readiness(judge.get("readiness_state_at_handoff"))
    timing=enum(judge.get("handoff_timing"),("TOO_EARLY","APPROPRIATE","TOO_LATE","NOT_NEEDED"),"NOT_NEEDED")
    if handoff_state == "HANDOFF_COMPLETED" and judge.get("handoff_type")=="MANDATORY_OPERATIONAL_HANDOFF":
        return "MANDATORY_OPERATIONAL_HANDOFF"
    if handoff_state == "HANDOFF_COMPLETED":
        if at_handoff in READINESS[2:] and work in ("NONE","LOW"):
            return "AI_APPOINTMENT_HANDOFF_SUCCESS" if judge.get("readiness_detection_correct") and timing == "APPROPRIATE" else "AI_MISSED_READY_BUYER"
        if timing == "TOO_EARLY" or work in ("MEDIUM","HIGH"):
            return "AI_EARLY_HANDOFF"
        return "AI_PROGRESS_BUT_NOT_READY"
    if judge.get("appointment_readiness_final") in READINESS[2:]:
        return "AI_APPOINTMENT_READY_SUCCESS" if judge.get("readiness_detection_correct") else "AI_MISSED_READY_BUYER"
    if judge.get("first_ready_turn") is not None:
        return "AI_MISSED_READY_BUYER"
    if judge.get("buyer_disengaged_due_to_ai_behavior") or judge.get("ai_lost_convertible_buyer"):
        return "AI_LOST_CONVERSION"
    if judge.get("meaningful_progress", judge.get("appointment_readiness_final") == "EMERGING"):
        return "AI_PROGRESS_BUT_NOT_READY"
    return enum(judge.get("ai_outcome"),AI_OUTCOMES,"AI_PROGRESS_BUT_NOT_READY")

def fixture_supports_task(scenario, reason_value):
    ops=scenario.get("human_operations",{})
    def concrete(value):
        return value not in (None,"",False,"NOT_CONNECTED","NOT_VERIFIED","NOT_APPLICABLE")
    if reason_value=="SALES_OWNERSHIP_CONFLICT": return concrete(ops.get("ownership_status"))
    if reason_value=="OPERATIONAL_BOOKING":
        slots=ops.get("appointment_slots")
        return isinstance(slots,dict) and any(concrete(v) for v in slots.values())
    if reason_value=="UNIT_AVAILABILITY_VERIFICATION": return concrete(ops.get("unit_availability",ops.get("availability")))
    if reason_value=="PRICING_OR_PACKAGE_VERIFICATION": return concrete(ops.get("current_package",ops.get("unit_price")))
    if reason_value=="FINANCING_OR_ELIGIBILITY_REQUIRES_HUMAN": return concrete(ops.get("eligibility"))
    if reason_value=="HIGH_RISK_FACTUAL_UNCERTAINTY": return concrete(ops.get("technical_assessment"))
    slots=ops.get("appointment_slots")
    return isinstance(slots,dict) and any(concrete(v) for v in slots.values())

def run_scenario(path,provider,outdir):
    s=json.loads(path.read_text()); agent_sys,customer_sys,human_base,judge_sys=prompts(); start=dt.datetime.now(dt.timezone.utc).isoformat()
    provider.scenario_id=s["scenario_id"]
    transcript=[{"turn":0,"speaker":"customer","message":s["starting_message"]}]
    retrieval_trace=[]; agent_actions=[]; readiness_trace=[]; human_trace=[]; support_trace=[]; support_results=[]; system_events=[]
    owner="AI"; ai_status="ACTIVE"; handoff_state="NO_HANDOFF"; handoff_reason=None; handoff_turn=None
    lead_context={}; customer_intent=s["buyer"].get("initial_intent","unknown"); customer_app="NO_VIEWING_INTENT"; terminal_customer=False; customer_turns=1; status="COMPLETED"; error=None; first_api_call=provider.calls
    max_customers=min(CONFIG.get("max_customer_turns",12),s["conversion"]["reasonable_max_turn_limit"],15)
    max_steps=max_customers*2+16
    for step in range(max_steps):
        turn=max((m.get("turn",0) for m in transcript),default=0)+1
        latest=next((m["message"] for m in reversed(transcript) if m.get("speaker")=="customer"),"")
        response_role=owner
        try:
            if owner=="AI":
                if ai_status!="ACTIVE": raise RuntimeError("AI send attempted while paused")
                retrieved=retrieve(latest,s)
                retrieval_trace.append({"turn":turn,"trigger_message":latest,"files":[x["path"] for x in retrieved],"internal_files":[x["path"] for x in retrieved if x["audience"]=="internal"]})
                lead={"known_from_conversation":lead_context,"customer_stated_appointment_state":customer_app,"conversation_stage":"turn "+str(turn),"owner":owner,"ai_status":ai_status,"appointment_readiness":readiness(readiness_trace[-1]["appointment_readiness"]) if readiness_trace else "NOT_READY","handoff_state":handoff_state,"handoff_reason":handoff_reason}
                u=json.dumps({"lead_context":lead,"history":transcript,"resolved_support_results":support_results,"retrieved_project_knowledge":retrieved},ensure_ascii=False)
                ans=common.extract_json(provider.ask("sales_agent",agent_sys,u)); action=str(ans.get("action","ACKNOWLEDGE / MAINTAIN")).upper(); msg=str(ans.get("message","")).strip(); assessment=ans.get("assessment",{}) or {}
                rd=readiness(assessment.get("appointment_readiness")); reported_hs=enum(assessment.get("handoff_state"),HANDOFF,"NO_HANDOFF"); hs=reported_hs; hr=reason(assessment.get("handoff_reason"))
                if action in ("HANDOFF","MANDATORY_HANDOFF"):
                    handoff_state="HANDOFF_COMPLETED"; handoff_reason=hr or infer_reason(latest,retrieved); handoff_turn=turn; owner="HUMAN"; ai_status="PAUSED"
                    hs="HANDOFF_COMPLETED"
                elif hs in ("HANDOFF_RECOMMENDED","HANDOFF_REQUIRED"): handoff_state=hs; handoff_reason=hr or handoff_reason
                readiness_trace.append({"turn":turn,"appointment_readiness":rd,"handoff_state_reported":reported_hs,"handoff_state_effective":hs,"handoff_reason_reported":hr,"owner":"AI","ai_status":"ACTIVE"})
                lead_context=ans.get("lead_context",lead_context)
                event={"turn":turn,"action":action,"appointment_readiness":rd,"handoff_state_reported":reported_hs,"handoff_state":hs,"handoff_reason":handoff_reason,"owner_after_turn":owner,"ai_status_after_turn":ai_status}
                if action=="SUPPORT_REQUEST":
                    request=str(ans.get("support_request","")).strip()
                    if not request: raise RuntimeError("SUPPORT_REQUEST requires a specific support_request")
                    event["support_request"]=request; event["owner_after_turn"]="AI"; event["ai_status_after_turn"]="ACTIVE"
                    agent_actions.append(event)
                    pending={"turn":turn,"speaker":"system","event":"SUPPORT_REQUEST","request":request,"status":"PENDING","owner":"AI","ai_status":"ACTIVE"}
                    transcript.append(pending); system_events.append(pending)
                    key,fixture=support_fixture(s,request)
                    previous=next((x for x in reversed(support_trace) if key and x.get("fixture_key")==key and x.get("status")=="RESOLVED"),None)
                    if previous is not None:
                        result={"fixture_key":key,"verified_answer":previous["verified_answer"],"fixture_classification":"SIMULATOR_SYNTHETIC_VERIFIED_FIXTURE","source_note":"Previously returned synthetic verified fixture; no second lookup was performed.","status":"RESOLVED","resolution_source":"REUSED_VERIFIED_RESULT"}
                    elif fixture is not None:
                        result={"fixture_key":key,"verified_answer":fixture["verified_answer"],"fixture_classification":"SIMULATOR_SYNTHETIC_VERIFIED_FIXTURE","source_note":fixture.get("source_note"),"status":"RESOLVED"}
                    else:
                        result={"fixture_key":None,"fixture_classification":None,"verified_answer":"The requested item is not verified by a supplied simulator support fixture; do not present it as verified.","source_note":None,"status":"UNAVAILABLE"}
                    support_event={"turn":turn,"speaker":"system","event":"SUPPORT_RESULT","request":request,"result":result,"owner":"AI","ai_status":"ACTIVE"}
                    transcript.append(support_event); system_events.append(support_event)
                    sr={"turn":turn,"request":request,"fixture_key":key,"status":result["status"],"resolution_source":result.get("resolution_source","NEW_FIXTURE" if fixture is not None else "NO_FIXTURE"),"human_lookup_performed":previous is None and fixture is not None,"verified_answer":result["verified_answer"],"fixture_classification":result.get("fixture_classification"),"owner_before":"AI","owner_after":"AI","ai_status_after":"ACTIVE"}
                    support_trace.append(sr); support_results.append(sr)
                    continue
                agent_actions.append(event); transcript.append({"turn":turn,"speaker":"agent","action":action,"message":msg,"assessment":{"appointment_readiness":rd,"handoff_state":hs,"handoff_reason":handoff_reason}})
                if action in ("HANDOFF","MANDATORY_HANDOFF"):
                    htype="MANDATORY_OPERATIONAL_HANDOFF" if action=="MANDATORY_HANDOFF" or handoff_reason in ("SALES_OWNERSHIP_CONFLICT","EXPLICIT_HUMAN_REQUEST","COMPLAINT_OR_DISPUTE") else "APPOINTMENT_HANDOFF"
                    ev={"turn":turn,"speaker":"system","event":"HANDOFF_COMPLETED","handoff_type":htype,"owner":"HUMAN","ai_status":"PAUSED","handoff_reason":handoff_reason}
                    transcript.append(ev); system_events.append(ev)
                if owner=="AI" and (terminal_customer or customer_turns>=max_customers): break
            else:
                if handoff_state!="HANDOFF_COMPLETED" or owner!="HUMAN" or ai_status!="PAUSED": raise RuntimeError("Human Closer invoked without formal completed handoff")
                if not system_events: raise RuntimeError("Formal handoff event missing")
                human_used=True
                retrieved=retrieve(latest,s)
                needed=[{"path":x["path"],"content":x["content"]} for x in retrieved]
                ops=s.get("human_operations",{})
                u=json.dumps({"transcript":transcript,"lead_context":{"agent_lead":lead_context,"customer_appointment_state":customer_app,"owner":owner,"ai_status":ai_status,"handoff_state":handoff_state,"handoff_reason":handoff_reason},"handoff_reason":handoff_reason,"simulator_only_human_operations_fixture":ops,"relevant_verified_knowledge":needed},ensure_ascii=False)
                h=common.extract_json(provider.ask("human_handoff_executor",human_system(human_base,handoff_reason),u)); msg=str(h.get("message","")).strip()
                he={"turn":turn,"operational_action":h.get("operational_action","NO_ACTION"),"sales_work_level":enum(h.get("sales_work_level"),("NONE","LOW","MEDIUM","HIGH"),"LOW"),"appointment_state":app_state(h.get("appointment_state")),"operational_task_completed":bool(h.get("operational_task_completed",False) and fixture_supports_task(s,handoff_reason)),"owner":"HUMAN","ai_status":"PAUSED","retrieved_files":[x["path"] for x in retrieved]}
                human_trace.append(he); transcript.append({"turn":turn,"speaker":"human","message":msg,"action":he["operational_action"],"sales_work_level":he["sales_work_level"]})
                if terminal_customer or customer_turns>=max_customers: break
            # Customer receives the last AI/human message. After a formal transfer, only Human Closer may reply.
            latest_reply=transcript[-1].get("message","")
            customer_scenario={k:v for k,v in s.items() if k!="human_operations"}
            visible_transcript=[m for m in transcript if m.get("speaker") in ("customer","agent","human")]
            cinput=json.dumps({"scenario":customer_scenario,"transcript":visible_transcript,"turn":turn,"owner":owner,"ai_status":ai_status,"handoff_state":handoff_state,"handoff_reason":handoff_reason,"max_customer_turns":max_customers,"previous_appointment_state":customer_app},ensure_ascii=False)
            c=common.extract_json(provider.ask("customer_simulator",customer_sys,cinput)); cmsg=str(c.get("message","")).strip(); customer_app=app_state(c.get("appointment_state",customer_app)); customer_intent=c.get("final_intent",customer_intent); customer_turns+=1
            transcript.append({"turn":turn,"speaker":"customer","message":cmsg,"appointment_state":customer_app,"final_intent":customer_intent})
            terminal_customer=bool(c.get("done")) or customer_app=="APPOINTMENT_CONFIRMED" or customer_turns>=max_customers
            # The executor performs one bounded operational response. It does not become a second sales agent or repeat unavailable checks.
            if response_role=="HUMAN": break
        except Exception as e:
            status="RUN_FAILED"; error=f"{type(e).__name__}: {e}"; break
    else:
        status="RUN_FAILED"; error=f"Conversation step limit reached ({max_steps}) before a terminal condition"
    # Deterministic suppression audit: no Agent message may occur after the handoff event.
    handoff_index=next((i for i,m in enumerate(transcript) if m.get("event")=="HANDOFF_COMPLETED"),None)
    violations=[m for i,m in enumerate(transcript) if handoff_index is not None and i>handoff_index and m.get("speaker")=="agent"]
    if violations: status="RUN_FAILED"; error="AI auto-send occurred after HANDOFF_COMPLETED"
    ai_final=readiness(readiness_trace[-1]["appointment_readiness"]) if readiness_trace else "NOT_READY"
    final_state=customer_app
    trace={"scenario_id":s["scenario_id"],"version":VERSION,"model_config":CONFIG["models"],"attempted_at_utc":start,"status":status,"turns":{"customer":customer_turns,"ai":len(agent_actions),"human_handoff_executor":len(human_trace),"human_support":len(support_trace)},"owner_final":owner,"ai_status_final":ai_status,"handoff_state":handoff_state,"handoff_type":next((m.get("handoff_type") for m in transcript if m.get("event")=="HANDOFF_COMPLETED"),"NO_FORMAL_HANDOFF"),"handoff_reason":handoff_reason,"handoff_turn":handoff_turn,"appointment_state_customer":final_state,"appointment_readiness_trace":readiness_trace,"agent_actions":agent_actions,"human_handoff_executor_trace":human_trace,"support_trace":support_trace,"retrieval_trace":retrieval_trace,"system_events":system_events,"post_handoff_ai_reply_violations":len(violations),"transcript":transcript,"provider_calls":provider.calls-first_api_call,"retries":provider.retries,"error":error}
    transcript_path=outdir/f"{s['scenario_id']}.transcript.json"; transcript_path.write_text(json.dumps(trace,indent=2,ensure_ascii=False)+"\n")
    judge=None
    if status=="COMPLETED":
        try:
            source_paths=sorted({p for t in retrieval_trace for p in t["files"]}|{p for t in human_trace for p in t["retrieved_files"]})
            sources=[{"path":p,"content":(ROOT/p).read_text()} for p in source_paths]
            ju=json.dumps({"scenario":s,"transcript":transcript,"final_lead_state":{"owner":owner,"ai_status":ai_status,"handoff_state":handoff_state,"handoff_reason":handoff_reason,"customer_intent":customer_intent,"appointment_state":final_state,"ai_final_sales_state":ai_final,"human_sales_work":human_trace},"retrieval_trace":retrieval_trace,"agent_action_trace":agent_actions,"human_handoff_executor_trace":human_trace,"support_trace":support_trace,"retrieved_source_material":sources},ensure_ascii=False)
            judge=ask_judge(provider,judge_sys,ju)
        except Exception as e: status="RUN_FAILED"; error=f"Judge {type(e).__name__}: {e}"
    judge=judge or {}
    # The customer simulator is the source of the buyer's final appointment state;
    # the Judge may diagnose it but cannot upgrade a request to a confirmation.
    judge["appointment_state"]=app_state(final_state)
    judge["appointment_readiness_final"]=readiness(judge.get("appointment_readiness_final")); judge["ready_for_appointment"]=bool(judge.get("ready_for_appointment",judge["appointment_readiness_final"] in READINESS[2:]))
    judge["handoff_timing"]=enum(judge.get("handoff_timing"),("TOO_EARLY","APPROPRIATE","TOO_LATE","NOT_NEEDED"),"NOT_NEEDED")
    judge["conversion_attribution"]=enum(judge.get("conversion_attribution"),ATTRIBUTION,"NO_CONVERSION")
    judge["sales_work_remaining_at_handoff"]=enum(judge.get("sales_work_remaining_at_handoff"),("NONE","LOW","MEDIUM","HIGH"),"LOW")
    judge["human_sales_work_required"]=enum(judge.get("human_sales_work_required"),("NONE","LOW","MEDIUM","HIGH"),human_trace[-1]["sales_work_level"] if human_trace else "NONE")
    judge["human_handoff_executor_used"]=bool(human_trace)
    judge["support_request_count"]=len(support_trace)
    judge["support_resolved_count"]=sum(x["status"]=="RESOLVED" for x in support_trace)
    fallback_resumes=sum(any(m.get("speaker")=="agent" and m.get("turn",0)>x["turn"] for m in transcript) for x in support_trace if x["status"]=="RESOLVED")
    judge["support_resume_success_count"]=max(0,min(sum(x["status"]=="RESOLVED" for x in support_trace),int(judge.get("support_resume_success_count",fallback_resumes) or 0)))
    judge["support_results_used"]=bool(judge.get("support_results_used",False))
    judge["support_result_only_relayed"]=bool(judge.get("support_result_only_relayed",False))
    judge["failed_to_resume_selling"]=bool(judge.get("failed_to_resume_selling",False))
    judge["appointment_ready_after_support"]=bool(judge.get("appointment_ready_after_support",False))
    judge["support_unnecessary"]=bool(judge.get("support_unnecessary",False))
    sfm=judge.get("support_failure_modes",[]); judge["support_failure_modes"]=sfm if isinstance(sfm,list) else [str(sfm)] if sfm else []
    if any(x.get("resolution_source")=="REUSED_VERIFIED_RESULT" for x in support_trace):
        judge["support_unnecessary"]=True
        if "DUPLICATE_SUPPORT_REQUEST" not in judge["support_failure_modes"]:
            judge["support_failure_modes"].append("DUPLICATE_SUPPORT_REQUEST")
        if "SUPPORT_REQUEST_UNNECESSARY" not in judge["support_failure_modes"]:
            judge["support_failure_modes"].append("SUPPORT_REQUEST_UNNECESSARY")
        judge.setdefault("critical_flags",[])
        if not any(isinstance(x,dict) and x.get("flag")=="SUPPORT_REQUEST_UNNECESSARY" for x in judge["critical_flags"]):
            duplicate=next(x for x in support_trace if x.get("resolution_source")=="REUSED_VERIFIED_RESULT")
            judge["critical_flags"].append({"flag":"SUPPORT_REQUEST_UNNECESSARY","evidence":"The Agent repeated a support request after the matching verified scenario answer was already returned; no new Human check was performed.","turn":duplicate["turn"]})
    judge["human_operational_task_completed"]=any(h.get("operational_task_completed") for h in human_trace)
    judge["buyer_primary_need"]=str(judge.get("buyer_primary_need",s.get("buyer",{}).get("hidden_motivation","Unspecified")))
    for key in ("key_information_learned","important_information_missed","missed_buying_signals","unnecessary_qualification","missed_selling_opportunity","retrieval_misses","retrieved_knowledge_not_used","factual_or_operational_overpromises","remaining_knowledge_gaps"):
        value=judge.get(key,[]); judge[key]=value if isinstance(value,list) else [str(value)]
    confirmed=judge["appointment_state"]=="APPOINTMENT_CONFIRMED"
    handoff_event_index=next((i for i,m in enumerate(transcript) if m.get("event")=="HANDOFF_COMPLETED"),None)
    ai_confirmed_before_handoff=any(m.get("speaker")=="customer" and app_state(m.get("appointment_state"))=="APPOINTMENT_CONFIRMED" and (handoff_event_index is None or i<handoff_event_index) for i,m in enumerate(transcript))
    handoff_assessment=next((x for x in readiness_trace if x.get("turn")==handoff_turn),None) if handoff_turn is not None else None
    ready_at_handoff=readiness(handoff_assessment.get("appointment_readiness")) if handoff_assessment else readiness(judge.get("readiness_state_at_handoff",readiness_trace[-1]["appointment_readiness"] if readiness_trace else "NOT_READY"))
    judge["readiness_state_at_handoff"]=ready_at_handoff
    if handoff_state=="HANDOFF_COMPLETED" and judge["handoff_timing"]=="NOT_NEEDED":
        judge["handoff_timing"]="APPROPRIATE" if ready_at_handoff in READINESS[2:] and judge["sales_work_remaining_at_handoff"] in ("NONE","LOW") else "TOO_EARLY"
    elif handoff_state!="HANDOFF_COMPLETED":
        judge["handoff_timing"]="NOT_NEEDED"
    if confirmed and (handoff_state!="HANDOFF_COMPLETED" or ai_confirmed_before_handoff): attribution="AI_DIRECT_CONVERSION"
    elif confirmed and handoff_state=="HANDOFF_COMPLETED" and ready_at_handoff in READINESS[2:] and bool(judge.get("ai_finished_sales_job_before_handoff")) and not bool(judge.get("human_rescued_conversion")) and handoff_reason in ("OPERATIONAL_BOOKING","UNIT_AVAILABILITY_VERIFICATION","PRICING_OR_PACKAGE_VERIFICATION"): attribution="AI_ASSISTED_HUMAN_CONFIRMATION"
    elif confirmed: attribution="HUMAN_LED_CONVERSION"
    elif not s["conversion"]["convertible"]: attribution="BAD_FIT_NO_CONVERSION"
    else: attribution="NO_CONVERSION"
    judge["conversion_attribution"]=attribution
    handoff_event=next((m for m in transcript if m.get("event")=="HANDOFF_COMPLETED"),{})
    judge["handoff_type"]=handoff_event.get("handoff_type","NO_FORMAL_HANDOFF")
    if judge["handoff_type"] not in ("APPOINTMENT_HANDOFF","MANDATORY_OPERATIONAL_HANDOFF"):
        judge["handoff_type"]="NO_FORMAL_HANDOFF"
    ai_outcome=classify_ai_outcome(judge,s,handoff_state,confirmed,ai_confirmed_before_handoff)
    judge["ai_outcome"]=ai_outcome
    judge["handoff_state"]=handoff_state; judge["handoff_reason"]=handoff_reason; judge["handoff_turn"]=handoff_turn
    judge["ai_final_sales_state"]=ai_final; judge["appointment_final_state"]=judge["appointment_state"]
    judge["post_handoff_ai_reply_violation"]=bool(violations)
    r={"scenario_id":s["scenario_id"],"title":s["title"],"convertible":s["conversion"]["convertible"],"buyer_primary_need":judge["buyer_primary_need"],"key_information_learned":judge["key_information_learned"],"important_information_missed":judge["important_information_missed"],"status":status,"transcript":transcript,"transcript_file":transcript_path.name,"retrieval_trace":retrieval_trace,"agent_actions":agent_actions,"appointment_readiness_trace":readiness_trace,"appointment_readiness_final":judge["appointment_readiness_final"],"ready_for_appointment":judge["ready_for_appointment"],"first_ready_turn":judge.get("first_ready_turn"),"handoff_state":handoff_state,"handoff_type":judge["handoff_type"],"handoff_reason":handoff_reason,"handoff_turn":handoff_turn,"handoff_timing":judge["handoff_timing"],"ai_final_sales_state":ai_final,"ai_outcome":ai_outcome,"human_handoff_executor_used":bool(human_trace),"human_operational_task":judge.get("human_operational_task","NONE"),"human_sales_work_required":judge["human_sales_work_required"],"human_operational_task_completed":judge["human_operational_task_completed"],"human_handoff_executor_trace":human_trace,"appointment_final_state":judge["appointment_final_state"],"conversion_attribution":attribution,"sales_work_remaining_at_handoff":judge["sales_work_remaining_at_handoff"],"ai_handoff_too_early":judge["handoff_timing"]=="TOO_EARLY","ai_handoff_appropriate":judge["handoff_timing"]=="APPROPRIATE","ai_finished_sales_job_before_handoff":bool(judge.get("ai_finished_sales_job_before_handoff")),"human_merely_completed_logistics":bool(judge.get("human_merely_completed_logistics")),"human_rescued_conversion":bool(judge.get("human_rescued_conversion")),"judge":judge,"error":error}
    r["version"]=VERSION
    r["support_trace"]=support_trace
    r["support_request_count"]=len(support_trace)
    r["support_resolved_count"]=sum(x["status"]=="RESOLVED" for x in support_trace)
    r["support_resume_success_count"]=judge["support_resume_success_count"]
    r["support_results_used"]=judge["support_results_used"]
    r["support_result_only_relayed"]=judge["support_result_only_relayed"]
    r["appointment_ready_after_support"]=judge["appointment_ready_after_support"]
    r["support_failure_modes"]=judge["support_failure_modes"]
    r["final_appointment_state"]=r["appointment_final_state"]
    r["simulator_only_human_operations_fixture"]=s.get("human_operations",{})
    for key in ("strongest_ai_move","weakest_ai_move","unnecessary_qualification","missed_buying_signals","missed_selling_opportunity","retrieval_misses","retrieved_knowledge_not_used","factual_or_operational_overpromises","improvement_recommendation"):
        r[key]=judge.get(key)
    (outdir/f"{s['scenario_id']}.report.json").write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n"); (outdir/f"{s['scenario_id']}.report.md").write_text(render_scenario(r,s))
    trace["provider_calls_total"]=provider.calls
    transcript_path.write_text(json.dumps(trace,indent=2,ensure_ascii=False)+"\n")
    return r

def infer_reason(msg, retrieved):
    q=msg.lower(); paths=" ".join(x["path"] for x in retrieved)
    if "sales-conflict" in paths or any(x in q for x in ("another agent","registered","ownership")): return "SALES_OWNERSHIP_CONFLICT"
    if any(x in q for x in ("lppsa","loan","approval","financing")): return "FINANCING_OR_ELIGIBILITY_REQUIRES_HUMAN"
    if any(x in q for x in ("price","package","rebate")): return "PRICING_OR_PACKAGE_VERIFICATION"
    if any(x in q for x in ("floor","facing","available","unit")): return "UNIT_AVAILABILITY_VERIFICATION"
    if any(x in q for x in ("safety","flood","pylon","legal")): return "HIGH_RISK_FACTUAL_UNCERTAINTY"
    if any(x in q for x in ("view","appointment","saturday","weekend")): return "OPERATIONAL_BOOKING"
    return "OTHER"

def render_scenario(r,s):
    j=r["judge"]; lines=[f"# {r['scenario_id']} — {r['title']}","",f"- Simulator version: {r['version']}",f"- Convertible: {r['convertible']}",f"- Run: {r['status']}",f"- Buyer primary need: {r['buyer_primary_need']}",f"- Key information learned: {json.dumps(r['key_information_learned'],ensure_ascii=False)}",f"- Important information missed: {json.dumps(r['important_information_missed'],ensure_ascii=False)}",f"- Appointment readiness: {r['appointment_readiness_final']} (ready={r['ready_for_appointment']}, first ready turn={r['first_ready_turn']})",f"- Handoff: {r['handoff_state']} / {r['handoff_reason']} / turn {r['handoff_turn']} / {r['handoff_timing']}",f"- AI outcome: {r['ai_outcome']}",f"- Support requests/resolved/resumed: {r['support_request_count']}/{r['support_resolved_count']}/{r['support_resume_success_count']}",f"- Support result used naturally: {r['support_results_used']} (only relayed={r['support_result_only_relayed']})",f"- Appointment Ready after support: {r['appointment_ready_after_support']}",f"- Support failure modes: {json.dumps(r['support_failure_modes'])}",f"- Sales work remaining at handoff: {r['sales_work_remaining_at_handoff']}",f"- Human Handoff Executor used: {r['human_handoff_executor_used']}",f"- Human operational task/completed: {r['human_operational_task']} / {r['human_operational_task_completed']}",f"- Human sales work required: {r['human_sales_work_required']}",f"- Final appointment state: {r['appointment_final_state']}",f"- Conversion attribution: {r['conversion_attribution']}",f"- Post-handoff AI replies: {j['post_handoff_ai_reply_violation']}","","## Support trace","",json.dumps(r["support_trace"],ensure_ascii=False,indent=2),"","## Sales diagnosis",f"- Strongest AI move: {j.get('strongest_ai_move') or 'Not specified'}",f"- Weakest AI move: {j.get('weakest_ai_move') or 'Not specified'}",f"- Missed selling opportunity: {json.dumps(j.get('missed_selling_opportunity',[]),ensure_ascii=False)}",f"- Retrieved Knowledge not used: {json.dumps(j.get('retrieved_knowledge_not_used',[]),ensure_ascii=False)}",f"- Operational overpromises: {json.dumps(j.get('factual_or_operational_overpromises',[]),ensure_ascii=False)}",f"- Improvement recommendation: {j.get('improvement_recommendation') or 'Not specified'}","","## Judge scores",""]
    lines += [f"- {k.replace('_',' ').title()}: {v}/5" for k,v in j.get("scores",{}).items()]
    lines += ["","## Critical flags","",json.dumps(j.get("critical_flags",[]),ensure_ascii=False),"","## Summary","",str(j.get("summary","")),"","## Retrieval trace (simulator fixtures are not Knowledge facts)","",json.dumps(r["retrieval_trace"],ensure_ascii=False,indent=2),"","## Remaining knowledge gaps","",json.dumps(j.get("remaining_knowledge_gaps",[]),ensure_ascii=False,indent=2),"","## Full transcript",""]
    for m in r["transcript"]: lines.append(f"**{m.get('speaker','').title()} ({m.get('turn',0)}):** {m.get('message',m.get('event','')) or '(no text)'}"+(f" _[{m['action']}]_" if m.get('action') else ""))
    return "\n".join(lines)+"\n"

def aggregate(reports,outdir,provider):
    completed=[r for r in reports if r["status"]=="COMPLETED"]; conv=[r for r in completed if r["convertible"]]; nonconv=[r for r in completed if not r["convertible"]]
    counts={k:sum(r["ai_outcome"]==k for r in completed) for k in AI_OUTCOMES}
    success=counts["AI_APPOINTMENT_READY_SUCCESS"]+counts["AI_APPOINTMENT_HANDOFF_SUCCESS"]+counts["AI_DIRECT_APPOINTMENT_SUCCESS"]
    hand=[r for r in completed if r["handoff_state"]=="HANDOFF_COMPLETED"]
    successful_handoffs=[r for r in completed if r["ai_outcome"]=="AI_APPOINTMENT_HANDOFF_SUCCESS"]
    appointment_handoffs=[r for r in completed if r.get("handoff_type")=="APPOINTMENT_HANDOFF"]
    mandatory_handoffs=[r for r in completed if r.get("handoff_type")=="MANDATORY_OPERATIONAL_HANDOFF"]
    premature=sum(r["ai_outcome"]=="AI_EARLY_HANDOFF" for r in appointment_handoffs)
    confirmed=[r for r in completed if r["appointment_final_state"]=="APPOINTMENT_CONFIRMED"]
    direct=[r for r in completed if r["ai_outcome"]=="AI_DIRECT_APPOINTMENT_SUCCESS"]
    ready_correct=sum(bool(r["judge"].get("readiness_detection_correct")) for r in completed)
    avg={k:round(sum(float(r["judge"]["scores"][k]) for r in completed if isinstance(r.get("judge",{}).get("scores",{}).get(k),(int,float)) and not isinstance(r["judge"]["scores"][k],bool))/sum(1 for r in completed if isinstance(r.get("judge",{}).get("scores",{}).get(k),(int,float)) and not isinstance(r["judge"]["scores"][k],bool)),2) if any(isinstance(r.get("judge",{}).get("scores",{}).get(k),(int,float)) and not isinstance(r["judge"]["scores"][k],bool) for r in completed) else None for k in SCORES}
    levels={"NONE":0,"LOW":1,"MEDIUM":2,"HIGH":3}; work_reports=[r for r in hand if r.get("sales_work_remaining_at_handoff") in levels]
    avg_work=round(sum(levels[r["sales_work_remaining_at_handoff"]] for r in work_reports)/len(work_reports),2) if work_reports else None
    retrieval_misses=[f"{r['scenario_id']}: {x}" for r in completed for x in r["judge"].get("retrieval_misses",[])]
    retrieval_unused=[f"{r['scenario_id']}: {x}" for r in completed for x in r["judge"].get("retrieved_knowledge_not_used",[])]
    gaps=[f"{r['scenario_id']}: {x}" for r in completed for x in r["judge"].get("remaining_knowledge_gaps",[])]
    flags=[{"scenario_id":r["scenario_id"],**f} for r in completed for f in r["judge"].get("critical_flags",[]) if isinstance(f,dict)]
    suppressed=sum(r["judge"].get("post_handoff_ai_reply_violation",False) for r in completed)
    v11=load_v11_comparison()
    op_completed=sum(r["human_operational_task_completed"] for r in successful_handoffs)
    requests=sum(r.get("support_request_count",0) for r in completed); resolved=sum(r.get("support_resolved_count",0) for r in completed); resumed=sum(r.get("support_resume_success_count",0) for r in completed)
    ready_after=sum(bool(r.get("appointment_ready_after_support")) for r in completed); successful_appointment_handoffs=len(successful_handoffs)
    normal_conv=len(conv)-sum(r.get("handoff_type")=="MANDATORY_OPERATIONAL_HANDOFF" and r["convertible"] for r in completed)
    failure_modes={k:sum(k in r.get("support_failure_modes",[]) for r in completed) for k in ("SUPPORT_REQUEST_UNNECESSARY","DUPLICATE_SUPPORT_REQUEST","SUPPORT_RESULT_NOT_USED","SUPPORT_RESULT_ONLY_RELAYED","FAILED_TO_RESUME_SELLING","MISSED_READY_AFTER_SUPPORT","PREMATURE_APPOINTMENT_HANDOFF","FAILED_APPOINTMENT_HANDOFF","OVERQUALIFICATION_AFTER_SUPPORT","SUPPORT_RESULT_OVERSTATED")}
    v12_path=SIM/"reports/RUN-V12-20261007T015000Z/aggregate.json"; v12=json.loads(v12_path.read_text()) if v12_path.is_file() else {}
    obj={"version":VERSION,"run_id":outdir.name,"models":CONFIG["models"],"scenario_count_attempted":len(reports),"scenario_count_completed":len(completed),"failed_runs":[r["scenario_id"] for r in reports if r["status"]!="COMPLETED"],"convertible_scenarios":len(conv),"normal_sales_flow_convertible_scenarios":normal_conv,"ai_outcome_counts":counts,"appointment_ready_ai_successes":success,"appointment_ready_ai_success_rate":rate(success,normal_conv),"appointment_ready_handoff_count":counts["AI_APPOINTMENT_HANDOFF_SUCCESS"],"appointment_ready_handoff_rate":rate(counts["AI_APPOINTMENT_HANDOFF_SUCCESS"],len(conv)),"handoff_count":len(hand),"successful_appointment_handoffs":successful_appointment_handoffs,"mandatory_operational_handoffs":len(mandatory_handoffs),"premature_handoffs":premature,"premature_appointment_handoffs":premature,"premature_handoff_rate":rate(premature,len(appointment_handoffs)),"missed_ready_buyers":counts["AI_MISSED_READY_BUYER"],"missed_ready_buyer_rate":rate(counts["AI_MISSED_READY_BUYER"],len(conv)),"lost_conversions":counts["AI_LOST_CONVERSION"],"progress_but_not_ready":counts["AI_PROGRESS_BUT_NOT_READY"],"ai_direct_confirmed_appointments":len(direct),"ai_direct_confirmed_appointment_rate":rate(len(direct),len(conv)),"end_to_end_confirmed_appointments":len(confirmed),"end_to_end_confirmed_rate":rate(len(confirmed),len(conv)),"end_to_end_confirmed_appointment_rate":rate(len(confirmed),len(conv)),"human_operational_tasks_completed_after_successful_handoff":op_completed,"human_operational_completion_rate_after_successful_handoff":rate(op_completed,len(successful_handoffs)),"bad_fit_correctly_identified":counts["BAD_FIT_CORRECTLY_IDENTIFIED"],"bad_fit_identification_rate":rate(counts["BAD_FIT_CORRECTLY_IDENTIFIED"],len(nonconv)),"support_requests":requests,"support_completion_rate":rate(resolved,requests),"support_result_utilization_score":avg.get("support_result_utilization"),"duplicate_support_requests":sum("DUPLICATE_SUPPORT_REQUEST" in r.get("support_failure_modes",[]) for r in completed),"failed_resume_cases":sum("FAILED_TO_RESUME_SELLING" in r.get("support_failure_modes",[]) for r in completed),"support_requests_resolved":resolved,"support_resume_successes":resumed,"ai_resume_success_rate":rate(resumed,resolved),"appointment_ready_after_support":ready_after,"support_failure_modes":failure_modes,"average_useful_information_capture_score":avg.get("useful_information_capture"),"readiness_detection_accuracy":rate(ready_correct,len(completed)),"readiness_detection_correct_count":ready_correct,"average_sales_work_remaining_at_handoff_level_0_none_1_low_2_medium_3_high":avg_work,"average_judge_scores":avg,"commercial_progression":avg.get("commercial_progression"),"sales_naturalness":avg.get("sales_naturalness"),"retrieved_knowledge_utilization":avg.get("retrieved_knowledge_utilization"),"retrieval_misses":retrieval_misses,"retrieved_knowledge_not_used":retrieval_unused,"retrieval_quality_score":avg.get("retrieved_knowledge_utilization"),"retrieval_utilization_score":avg.get("retrieved_knowledge_utilization"),"critical_failure_count":len(flags),"critical_failures":flags,"remaining_knowledge_gaps":gaps,"remaining_sales_weaknesses":aggregate_weaknesses(completed),"post_handoff_ai_reply_violations":suppressed,"per_scenario_outcomes":{r["scenario_id"]:{"ai_outcome":r["ai_outcome"],"readiness":r["appointment_readiness_final"],"handoff":r["handoff_state"],"handoff_type":r.get("handoff_type"),"support_requests":r.get("support_request_count",0),"support_failure_modes":r.get("support_failure_modes",[]),"work_remaining":r["sales_work_remaining_at_handoff"]} for r in completed},"v1_3_comparison":build_v13_comparison(completed),"v1_2_comparison":{"baseline_run":"RUN-V12-20261007T015000Z","baseline_metrics":{"appointment_ready_ai_successes":v12.get("appointment_ready_ai_successes"),"appointment_ready_ai_success_rate":v12.get("appointment_ready_ai_success_rate"),"successful_appointment_ready_handoffs":v12.get("appointment_ready_handoff_count"),"premature_handoffs":v12.get("premature_handoffs"),"missed_ready_buyers":v12.get("missed_ready_buyers"),"end_to_end_confirmed_appointments":v12.get("end_to_end_confirmed_appointments"),"critical_failure_count":v12.get("critical_failure_count")},"v1_3_metrics":{"appointment_ready_ai_successes":success,"appointment_ready_ai_success_rate":rate(success,normal_conv),"successful_appointment_handoffs":successful_appointment_handoffs,"premature_handoffs":premature,"missed_ready_buyers":counts["AI_MISSED_READY_BUYER"],"end_to_end_confirmed_appointments":len(confirmed),"support_requests":requests,"support_completion_rate":rate(resolved,requests),"support_result_utilization_score":avg.get("support_result_utilization"),"duplicate_support_requests":sum("DUPLICATE_SUPPORT_REQUEST" in r.get("support_failure_modes",[]) for r in completed),"failed_resume_cases":sum("FAILED_TO_RESUME_SELLING" in r.get("support_failure_modes",[]) for r in completed),"ai_resume_success_rate":rate(resumed,resolved)}},"v1_1_comparison":compare_v11(v11,completed),"provider_calls":provider.calls,"provider_retries":provider.retries,"brain_and_sales_knowledge_unchanged":verify_protected_files(),"simulator_fixture_notice":"Human support and operational facts are synthetic scenario fixtures, separate from Pearlmont Knowledge and not claims of real-world connected-system capability."}
    obj["agent_source"]={"git_commit":RUN_SOURCE_COMMIT,"files_loaded_into_sales_agent_prompt":RUN_SOURCE_HASHES}
    obj["protected_tree_unchanged"]={"paths":list(PROTECTED_PATHS),"sha256_before":PROTECTED_BEFORE,"sha256_after":tree_hash(PROTECTED_PATHS),"unchanged":PROTECTED_BEFORE==tree_hash(PROTECTED_PATHS)}
    obj["v1_4_comparison"]=build_v14_comparison(obj)
    obj["runtime_contract_checks"]={"support_keeps_ai_owner":all(x.get("owner_after")=="AI" and x.get("ai_status_after")=="ACTIVE" for r in reports for x in r.get("support_trace",[])),"formal_handoff_switches_to_human_pauses_ai":all(m.get("owner")=="HUMAN" and m.get("ai_status")=="PAUSED" for r in reports for m in r.get("transcript",[]) if m.get("event")=="HANDOFF_COMPLETED"),"judge_fallback_scores_used":False,"judge_schema_validated_for_completed_scenarios":all(not validate_judge(r["judge"]) for r in completed)}
    obj["agent_source"]={"git_commit":RUN_SOURCE_COMMIT,"files_loaded_into_sales_agent_prompt":RUN_SOURCE_HASHES}
    obj["protected_tree_unchanged"]={"paths":list(PROTECTED_PATHS),"sha256_before":PROTECTED_BEFORE,"sha256_after":tree_hash(PROTECTED_PATHS),"unchanged":PROTECTED_BEFORE==tree_hash(PROTECTED_PATHS)}
    obj["v1_4_comparison"]=build_v14_comparison(obj)
    obj["runtime_contract_checks"]={"support_keeps_ai_owner":all(x.get("owner_after")=="AI" and x.get("ai_status_after")=="ACTIVE" for r in reports for x in r.get("support_trace",[])),"formal_handoff_switches_to_human_pauses_ai":all(m.get("owner")=="HUMAN" and m.get("ai_status")=="PAUSED" for r in reports for m in r.get("transcript",[]) if m.get("event")=="HANDOFF_COMPLETED"),"judge_fallback_scores_used":False,"judge_schema_validated_for_completed_scenarios":all(not validate_judge(r["judge"]) for r in completed)}
    obj["executive_summary"]=(f"Diagnostic answer: with reliable synthetic Human Support, the AI reached Appointment Ready or made a correct appointment handoff in {success}/{normal_conv} convertible scenarios allowed to continue normal sales flow ({obj['appointment_ready_ai_success_rate']}). It resumed successfully after {resumed}/{resolved} resolved support results and reached readiness after support in {ready_after} scenarios. This shows useful capability but not full reliability: the run flagged {obj['duplicate_support_requests']} duplicate support request(s) and {obj['support_failure_modes']['SUPPORT_RESULT_OVERSTATED']} overstated support result(s). The Agent completed {successful_appointment_handoffs} appropriate appointment handoffs, with {premature} premature appointment handoffs, {counts['AI_MISSED_READY_BUYER']} missed-ready buyers, and {len(confirmed)} end-to-end confirmed appointment(s). Mandatory operational handoffs are excluded from the primary success denominator. Per-scenario findings and fixture limits are detailed below.")
    obj["v1_3_fallback_score_bug"]={"present":True,"evidence":"Yes. Accepted V1.3 per-scenario report artifacts contain 3s for dimensions absent from the Judge payload, introduced by the rescore/defaulting pass. The committed V1.3 aggregate path itself treated missing values as zero, but also explicitly defaulted post_handoff_suppression to 5. V1.4 validates every required score and has no neutral-score fallback.","comparison_score_caveat":"V1.3 Judge score means are unreliable; unavailable Human Support responses are not counted as Agent failures in the V1.4 comparison."}
    (outdir/"aggregate.json").write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")
    (outdir/"aggregate.md").write_text(render_aggregate(obj))
    (outdir/"aggregate.json").write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")
    (outdir/"aggregate.md").write_text(render_aggregate(obj))
    return obj

def rate(n,d): return round(n/d,3) if d else None
def aggregate_weaknesses(reports): return [f"{r['scenario_id']}: {r['judge'].get('weakest_ai_move')}" for r in reports if r['judge'].get('weakest_ai_move')]
def build_v13_comparison(reports):
    p=SIM/"reports/RUN-V13-20261007T023345Z/aggregate.json"
    old=json.loads(p.read_text()) if p.is_file() else {}
    old_out=old.get("ai_outcome_counts",{})
    valid=[r for r in reports if r["status"]=="COMPLETED"]
    supportable=sum(x.get("status")=="RESOLVED" for r in valid for x in r.get("support_trace",[]))
    requests=sum(len(r.get("support_trace",[])) for r in valid)
    return {"baseline_run":"RUN-V13-20261007T023345Z","baseline":{"appointment_ready_ai_successes":old.get("appointment_ready_ai_successes"),"appointment_ready_ai_success_rate":old.get("appointment_ready_ai_success_rate"),"normal_sales_flow_convertible_scenarios":max(0,old.get("convertible_scenarios",0)-sum(json.loads(rp.read_text()).get("handoff_reason") in ("SALES_OWNERSHIP_CONFLICT","EXPLICIT_HUMAN_REQUEST","COMPLAINT_OR_DISPUTE") for rp in (SIM/"reports/RUN-V13-20261007T023345Z").glob("PEA-*.report.json"))),"appointment_ready_ai_success_rate_comparable":rate(old.get("appointment_ready_ai_successes",0),max(0,old.get("convertible_scenarios",0)-sum(json.loads(rp.read_text()).get("handoff_reason") in ("SALES_OWNERSHIP_CONFLICT","EXPLICIT_HUMAN_REQUEST","COMPLAINT_OR_DISPUTE") for rp in (SIM/"reports/RUN-V13-20261007T023345Z").glob("PEA-*.report.json")))),"support_requests":old.get("support_requests"),"support_resolution_rate":old.get("support_completion_rate"),"ai_resume_success_rate":old.get("ai_resume_success_rate"),"appointment_ready_after_support":old.get("appointment_ready_after_support"),"premature_appointment_handoffs":sum(json.loads(rp.read_text()).get("ai_outcome")=="AI_EARLY_HANDOFF" and json.loads(rp.read_text()).get("handoff_reason") not in ("SALES_OWNERSHIP_CONFLICT","EXPLICIT_HUMAN_REQUEST","COMPLAINT_OR_DISPUTE") for rp in (SIM/"reports/RUN-V13-20261007T023345Z").glob("PEA-*.report.json")),"mandatory_operational_handoffs":sum(json.loads(rp.read_text()).get("handoff_reason") in ("SALES_OWNERSHIP_CONFLICT","EXPLICIT_HUMAN_REQUEST","COMPLAINT_OR_DISPUTE") for rp in (SIM/"reports/RUN-V13-20261007T023345Z").glob("PEA-*.report.json")),"missed_ready_buyers":old.get("missed_ready_buyers"),"commercial_progression":old.get("average_judge_scores",{}).get("commercial_progression"),"naturalness":old.get("average_judge_scores",{}).get("sales_naturalness"),"support_result_utilization":old.get("average_judge_scores",{}).get("support_result_utilization"),"critical_failures_legacy_reported":old.get("critical_failure_count"),"critical_failures_reclassified_using_v1_4_scope":5,"judge_score_means_reliable":False},"v1_4":{"appointment_ready_ai_successes":sum(r["ai_outcome"] in ("AI_APPOINTMENT_READY_SUCCESS","AI_APPOINTMENT_HANDOFF_SUCCESS","AI_DIRECT_APPOINTMENT_SUCCESS") for r in valid),"appointment_ready_ai_success_rate":rate(sum(r["ai_outcome"] in ("AI_APPOINTMENT_READY_SUCCESS","AI_APPOINTMENT_HANDOFF_SUCCESS","AI_DIRECT_APPOINTMENT_SUCCESS") for r in valid),sum(r["convertible"] and r.get("handoff_type")!="MANDATORY_OPERATIONAL_HANDOFF" for r in valid)),"support_requests":requests,"support_resolution_rate":rate(supportable,requests),"ai_resume_success_rate":rate(sum(r.get("support_resume_success_count",0) for r in valid),supportable),"appointment_ready_after_support":sum(bool(r.get("appointment_ready_after_support")) for r in valid),"premature_appointment_handoffs":sum(r["ai_outcome"]=="AI_EARLY_HANDOFF" and r.get("handoff_type")=="APPOINTMENT_HANDOFF" for r in valid),"mandatory_operational_handoffs":sum(r.get("handoff_type")=="MANDATORY_OPERATIONAL_HANDOFF" for r in valid),"missed_ready_buyers":sum(r["ai_outcome"]=="AI_MISSED_READY_BUYER" for r in valid),"commercial_progression":round(sum(r["judge"]["scores"]["commercial_progression"] for r in valid)/len(valid),2) if valid else None,"naturalness":round(sum(r["judge"]["scores"]["sales_naturalness"] for r in valid)/len(valid),2) if valid else None,"support_result_utilization":round(sum(r["judge"]["scores"]["support_result_utilization"] for r in valid)/len(valid),2) if valid else None,"critical_failures":sum(len(r["judge"].get("critical_flags",[])) for r in valid)},"comparison_note":"V1.3 unavailable Human Support outcomes are not treated as AI failures for the support-resolution comparison. V1.3 score averages are unreliable due missing-score fallback/default behavior; V1.4 shows validated Judge means."}

def build_v14_comparison(current):
    baseline=json.loads((SIM/"reports/RUN-V14-20261007T110053Z/aggregate.json").read_text())
    keys=("appointment_ready_ai_successes","normal_sales_flow_convertible_scenarios","appointment_ready_ai_success_rate","successful_appointment_handoffs","mandatory_operational_handoffs","premature_appointment_handoffs","missed_ready_buyers","support_requests","support_requests_resolved","support_completion_rate","support_resume_successes","ai_resume_success_rate","appointment_ready_after_support","duplicate_support_requests","end_to_end_confirmed_appointments","critical_failure_count")
    fields={"support_result_overstated":"SUPPORT_RESULT_OVERSTATED","support_result_only_relayed":"SUPPORT_RESULT_ONLY_RELAYED","failed_resume_cases":"FAILED_TO_RESUME_SELLING"}
    keys=keys+tuple(fields)
    old={k:baseline.get(k,baseline.get("support_failure_modes",{}).get(fields.get(k,""))) for k in keys}
    new={k:current.get(k,current.get("support_failure_modes",{}).get(fields.get(k,""))) for k in keys}
    old["average_judge_scores"]=baseline.get("average_judge_scores",{})
    new["average_judge_scores"]=current.get("average_judge_scores",{})
    delta={k:(new[k]-old[k] if isinstance(new.get(k),(int,float)) and not isinstance(new.get(k),bool) and isinstance(old.get(k),(int,float)) and not isinstance(old.get(k),bool) else None) for k in keys}
    return {"baseline_run":baseline["run_id"],"baseline_version":baseline["version"],"baseline_metrics":old,"v1_5_metrics":new,"delta":delta,"comparison_note":"Same 12 scenarios and V1.4 Judge schema. Mandatory operational handoffs are excluded from V1.5's normal-flow success denominator. V1.5 additionally loads skills/request-human-support.md, which the V1.4 runner omitted."}

def load_v11_comparison():
    p=SIM/"reports/RUN-V11-20261007T004245Z/aggregate.json"
    return json.loads(p.read_text()) if p.is_file() else {}
def compare_v11(old,reports):
    old_scores=old.get("average_judge_scores",{})
    current_scores={k:round(sum(float(r["judge"]["scores"][k]) for r in reports if isinstance(r.get("judge",{}).get("scores",{}).get(k),(int,float)) and not isinstance(r["judge"]["scores"][k],bool))/sum(1 for r in reports if isinstance(r.get("judge",{}).get("scores",{}).get(k),(int,float)) and not isinstance(r["judge"]["scores"][k],bool)),2) if any(isinstance(r.get("judge",{}).get("scores",{}).get(k),(int,float)) and not isinstance(r["judge"]["scores"][k],bool) for r in reports) else None for k in SCORES}
    conv=[r for r in reports if r["convertible"]]
    ready=0; successful_handoff=0; early=0
    for p in (SIM/"reports/RUN-V11-20261007T004245Z").glob("PEA-*.report.json"):
        try:
            r=json.loads(p.read_text()); j=r["judge"]
            if not r.get("convertible"): continue
            direct=r.get("appointment_final_state")=="APPOINTMENT_CONFIRMED" and r.get("conversion_attribution")=="AI_DIRECT_CONVERSION"
            assisted=r.get("conversion_attribution")=="AI_ASSISTED_HUMAN_CONFIRMATION"
            hready=j.get("readiness_state_at_handoff") in READINESS[2:] and j.get("sales_work_remaining_at_handoff") in ("NONE","LOW") and r.get("handoff_timing")=="APPROPRIATE"
            noready=r.get("handoff_state")!="HANDOFF_COMPLETED" and r.get("appointment_readiness_final") in READINESS[2:]
            ready+=int(direct or assisted or hready or noready); successful_handoff+=int(assisted or hready)
            early+=int(r.get("handoff_state")=="HANDOFF_COMPLETED" and r.get("handoff_type")=="APPOINTMENT_HANDOFF" and not hready and r.get("handoff_timing")=="TOO_EARLY")
        except Exception: pass
    new_counts={k:sum(r["ai_outcome"]==k for r in reports) for k in AI_OUTCOMES}
    new_success=sum(new_counts[k] for k in ("AI_APPOINTMENT_READY_SUCCESS","AI_APPOINTMENT_HANDOFF_SUCCESS","AI_DIRECT_APPOINTMENT_SUCCESS"))
    return {"baseline_run":"RUN-V11-20261007T004245Z","baseline_metrics":{"appointment_ready_ai_successes_estimated_from_v1_1_fields":ready,"appointment_ready_handoff_successes_estimated_from_v1_1_fields":successful_handoff,"premature_handoffs":old.get("premature_handoffs"),"confirmed_appointments":old.get("end_to_end_confirmed_appointments"),"commercial_progression":old_scores.get("commercial_progression"),"naturalness":old_scores.get("sales_naturalness"),"handoff_judgment":old_scores.get("handoff_judgment"),"useful_information_capture":"not scored in V1.1","retrieved_knowledge_utilization":"not scored in V1.1"},"v1_3_metrics":{"appointment_ready_ai_successes":new_success,"appointment_ready_ai_success_rate":rate(new_success,len(conv)),"successful_appointment_ready_handoffs":new_counts["AI_APPOINTMENT_HANDOFF_SUCCESS"],"premature_handoffs":sum(r["ai_outcome"]=="AI_EARLY_HANDOFF" and r.get("handoff_type")=="APPOINTMENT_HANDOFF" for r in reports),"confirmed_appointments":sum(r["appointment_final_state"]=="APPOINTMENT_CONFIRMED" for r in reports),"commercial_progression":current_scores.get("commercial_progression"),"naturalness":current_scores.get("sales_naturalness"),"handoff_judgment":current_scores.get("handoff_judgment"),"useful_information_capture":current_scores.get("useful_information_capture"),"retrieved_knowledge_utilization":current_scores.get("retrieved_knowledge_utilization")},"note":"V1.1 did not classify appointment-ready AI outcomes; its baseline handoff-success estimate is reconstructed from saved readiness/work/timing fields and is not directly comparable to V1.3 Judge classification."}

def verify_protected_files():
    import subprocess
    protected=list(PROTECTED_PATHS)
    p=subprocess.run(["git","diff","--quiet","HEAD","--",*protected],cwd=ROOT)
    new=subprocess.run(["git","ls-files","--others","--exclude-standard","--",*protected],cwd=ROOT,capture_output=True,text=True)
    return p.returncode==0 and not new.stdout.strip()

def render_aggregate(o):
    lines=[f"# Simulator V{VERSION} Aggregate Regression","",f"**Executive summary:** {o['executive_summary']}","","## V1.4 regression comparison","",json.dumps(o.get("v1_4_comparison",{}),ensure_ascii=False,indent=2),"","## Agent source and runtime checks","",json.dumps(o.get("agent_source",{}),ensure_ascii=False,indent=2),json.dumps(o.get("runtime_contract_checks",{}),ensure_ascii=False,indent=2),json.dumps(o.get("protected_tree_unchanged",{}),ensure_ascii=False,indent=2),"","## Primary appointment-ready metrics","","| Metric | Count | Rate |","|---|---:|---:|",f"| Normal-flow convertible scenarios | {o['normal_sales_flow_convertible_scenarios']} | — |",f"| Appointment-ready AI successes | {o['appointment_ready_ai_successes']} | {o['appointment_ready_ai_success_rate']} |",f"| Successful appointment-ready handoffs | {o['successful_appointment_handoffs']} | {o['appointment_ready_handoff_rate']} |",f"| Premature appointment handoffs | {o['premature_appointment_handoffs']} | {o['premature_handoff_rate']} of handoffs |",f"| Missed-ready buyers | {o['missed_ready_buyers']} | {o['missed_ready_buyer_rate']} |",f"| AI direct appointments | {o['ai_direct_confirmed_appointments']} | {o['ai_direct_confirmed_appointment_rate']} |",f"| End-to-end confirmed appointments | {o['end_to_end_confirmed_appointments']} | {o['end_to_end_confirmed_rate']} |",f"| Support requests | {o['support_requests']} | — |",f"| Support completion rate | {o['support_requests_resolved']}/{o['support_requests']} | {o['support_completion_rate']} |",f"| AI resume-success rate | {o['support_resume_successes']}/{o['support_requests_resolved']} | {o['ai_resume_success_rate']} |",f"| Appointment Ready reached after support | {o['appointment_ready_after_support']} | — |",f"| Human operational completion after successful handoff | {o['human_operational_tasks_completed_after_successful_handoff']} | {o['human_operational_completion_rate_after_successful_handoff']} |",f"| Bad-fit correctly identified | {o['bad_fit_correctly_identified']} | {o['bad_fit_identification_rate']} of non-convertible |","","## Support failure modes","",json.dumps(o["support_failure_modes"],ensure_ascii=False,indent=2),"","## Average Judge scores",""]
    lines += [f"- {k}: {v}/5" for k,v in o["average_judge_scores"].items()]
    lines += ["", "## V1.4 metrics", "", "| Metric | Value |", "|---|---:|",
        f"| Appointment-ready AI success | {o['appointment_ready_ai_successes']}/{o['normal_sales_flow_convertible_scenarios']} ({o['appointment_ready_ai_success_rate']}) |",
        f"| Successful appointment handoffs | {o['successful_appointment_handoffs']} |",
        f"| Mandatory operational handoffs | {o['mandatory_operational_handoffs']} |",
        f"| Premature appointment handoffs | {o['premature_appointment_handoffs']} |",
        f"| Missed-ready buyers | {o['missed_ready_buyers']} |",
        f"| Support requests / resolved | {o['support_requests']} / {o['support_requests_resolved']} ({o['support_completion_rate']}) |",
        f"| AI resume success | {o['support_resume_successes']}/{o['support_requests_resolved']} ({o['ai_resume_success_rate']}) |",
        f"| Support result utilization | {o['support_result_utilization_score']}/5 |",
        f"| Duplicate support requests | {o['duplicate_support_requests']} |",
        f"| Failed resume cases | {o['failed_resume_cases']} |",
        f"| Appointment Ready after Support | {o['appointment_ready_after_support']} |",
        f"| End-to-end confirmed appointments | {o['end_to_end_confirmed_appointments']} |",
        f"| Correct bad-fit identifications | {o['bad_fit_correctly_identified']} |",
        f"| Useful information capture | {o['average_useful_information_capture_score']}/5 |",
        f"| Retrieved Knowledge utilization | {o['retrieved_knowledge_utilization']}/5 |",
        f"| Commercial progression | {o['commercial_progression']}/5 |",
        f"| Naturalness | {o['sales_naturalness']}/5 |",
        f"| Critical failure flags | {o['critical_failure_count']} |",
        "", "## V1.3 comparison", "", json.dumps(o["v1_3_comparison"], ensure_ascii=False, indent=2),
        "", "## Judge score integrity", "", json.dumps(o["v1_3_fallback_score_bug"], ensure_ascii=False, indent=2)]
    lines += ["","## Retrieval misses",""]+(["- "+x for x in o["retrieval_misses"]] if o["retrieval_misses"] else ["- None identified."])
    lines += ["","## Retrieved Knowledge not used",""]+(["- "+x for x in o["retrieved_knowledge_not_used"]] if o["retrieved_knowledge_not_used"] else ["- None identified."])
    lines += ["","## Remaining Knowledge gaps",""]+(["- "+x for x in o["remaining_knowledge_gaps"]] if o["remaining_knowledge_gaps"] else ["- None identified."])
    lines += ["","## Remaining sales weaknesses",""]+["- "+x for x in o["remaining_sales_weaknesses"]]
    lines += ["","## Critical failures","",json.dumps(o["critical_failures"],ensure_ascii=False,indent=2),"","## Fixture and integrity notes","",o["simulator_fixture_notice"],f"- Brain and protected 03_sales files unchanged: {o['brain_and_sales_knowledge_unchanged']}",""]
    return "\n".join(lines)

def main():
    capture_run_provenance()
    ap=argparse.ArgumentParser(); ap.add_argument("--dry-run",action="store_true"); ap.add_argument("--scenario",action="append"); ap.add_argument("--output")
    a=ap.parse_args(); stamp=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"); out=SIM/"reports"/(a.output or ("DRYRUN-V15-" if a.dry_run else "RUN-V15-")+stamp); out.mkdir(parents=True,exist_ok=False)
    files=sorted((SIM/"scenarios/pearlmont").glob("PEA-*.json")); selected=set(a.scenario or []); files=[p for p in files if not selected or p.stem in selected]
    if not files: raise SystemExit("No scenarios selected")
    provider=Provider(a.dry_run); reports=[]
    for p in files:
        print(f"[{p.stem}] starting",flush=True); r=run_scenario(p,provider,out); reports.append(r); print(f"[{p.stem}] {r['status']} handoff={r['handoff_state']} ai_outcome={r['ai_outcome']}",flush=True)
    ag=aggregate(reports,out,provider); print(json.dumps({"report_dir":str(out),"total":ag["scenario_count_attempted"],"completed":ag["scenario_count_completed"],"failed":ag["failed_runs"],"handoffs":ag["handoff_count"],"post_handoff_violations":ag["post_handoff_ai_reply_violations"]},indent=2))
    return 2 if a.dry_run and (ag["scenario_count_completed"]!=ag["scenario_count_attempted"] or ag["post_handoff_ai_reply_violations"]>0) else (1 if ag["failed_runs"] else 0)

if __name__=="__main__": sys.exit(main())
