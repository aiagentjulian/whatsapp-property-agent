#!/usr/bin/env python3
"""Pearlmont Simulator V1.2: score buyer understanding and appointment-ready handoffs."""
from __future__ import annotations
import argparse, datetime as dt, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SIM=ROOT/"simulator"; KNOW=ROOT/"knowledge/project/pearlmont"
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_v1 as common

CONFIG=json.loads((SIM/"config.json").read_text())
READINESS=("NOT_READY","EMERGING","READY_FOR_APPOINTMENT","APPOINTMENT_IN_PROGRESS","APPOINTMENT_CONFIRMED")
HANDOFF=("NO_HANDOFF","HANDOFF_RECOMMENDED","HANDOFF_REQUIRED","HANDOFF_COMPLETED")
REASONS=("OPERATIONAL_BOOKING","UNIT_AVAILABILITY_VERIFICATION","PRICING_OR_PACKAGE_VERIFICATION","FINANCING_OR_ELIGIBILITY_REQUIRES_HUMAN","SALES_OWNERSHIP_CONFLICT","EXPLICIT_HUMAN_REQUEST","COMPLAINT_OR_DISPUTE","HIGH_RISK_FACTUAL_UNCERTAINTY","OTHER")
ATTRIBUTION=("AI_DIRECT_CONVERSION","AI_ASSISTED_HUMAN_CONFIRMATION","HUMAN_LED_CONVERSION","NO_CONVERSION","BAD_FIT_NO_CONVERSION")
AI_OUTCOMES=("AI_APPOINTMENT_READY_SUCCESS","AI_APPOINTMENT_HANDOFF_SUCCESS","AI_DIRECT_APPOINTMENT_SUCCESS","AI_PROGRESS_BUT_NOT_READY","AI_EARLY_HANDOFF","AI_MISSED_READY_BUYER","AI_LOST_CONVERSION","BAD_FIT_CORRECTLY_IDENTIFIED")
SCORES=common.DIMENSIONS+["appointment_readiness_detection","handoff_timing","handoff_reason_correctness","post_handoff_suppression","conversion_attribution","useful_information_capture","appointment_ready_progression","retrieved_knowledge_utilization"]

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
    paths=["brain/AGENT.md","brain/SALES_FLOW.md","brain/INTENT_MODEL.md","brain/LEAD_PROFILE.md","brain/RESPONSE_RULES.md","brain/HANDOFF_RULES.md","skills/decide-next-action.md","skills/retrieve-project-knowledge.md","skills/update-lead-profile.md","skills/handoff-to-human.md"]
    return "\n\n".join(f"--- {p} ---\n{(ROOT/p).read_text()}" for p in paths)

class Provider(common.Provider):
    def ask(self,role,system,user):
        if self.dry:
            self.calls+=1
            if role=="sales_agent": return json.dumps({"action":"HANDOFF","message":"I’ll have a colleague verify this and continue with you.","lead_context":{},"assessment":{"appointment_readiness":"EMERGING","handoff_state":"HANDOFF_COMPLETED","handoff_reason":"OPERATIONAL_BOOKING"}})
            if role=="customer_simulator": return json.dumps({"message":"Okay, I’ll wait for the colleague.","done":True,"appointment_state":"NO_VIEWING_INTENT","final_intent":"medium"})
            if role=="human_handoff_executor": return json.dumps({"message":"I’ll check the available simulator fixture and confirm what it establishes.","operational_action":"NO_ACTION","sales_work_level":"LOW","appointment_state":"NO_VIEWING_INTENT","operational_task_completed":False})
            return json.dumps(dry_judgment())
        return super().ask(role,system,user)

def dry_judgment():
    return {"appointment_state":"NO_VIEWING_INTENT","appointment_readiness_final":"EMERGING","ready_for_appointment":False,"first_ready_turn":None,"readiness_detection_correct":True,"readiness_state_at_handoff":"EMERGING","handoff_state":"HANDOFF_COMPLETED","handoff_reason":"OPERATIONAL_BOOKING","handoff_turn":1,"handoff_timing":"APPROPRIATE","handoff_reason_correct":True,"handoff_quality_score":3,"ai_final_sales_state":"EMERGING","human_handoff_executor_used":True,"appointment_final_state":"NO_VIEWING_INTENT","conversion_attribution":"NO_CONVERSION","ai_outcome":"AI_PROGRESS_BUT_NOT_READY","sales_work_remaining_at_handoff":"LOW","human_sales_work_required":"LOW","human_operational_task_completed":False,"human_operational_task":"OPERATIONAL_BOOKING","ai_finished_sales_job_before_handoff":False,"human_merely_completed_logistics":False,"human_rescued_conversion":False,"post_handoff_ai_reply_violation":False,"buyer_primary_need":"dry-run","key_information_learned":[],"important_information_missed":[],"retrieved_knowledge_utilized":True,"scores":{k:3 for k in SCORES},"critical_flags":[],"conversion_analysis":{"what_moved_buyer_forward":[],"what_reduced_conversion_probability":[],"where_conversion_was_won_or_lost":"dry-run"},"what_agent_did_well":[],"weak_or_wrong_sales_move":"dry-run","better_next_move":"dry-run","missed_buying_signals":[],"unnecessary_qualification":[],"unsupported_factual_claims":[],"retrieval_misses":[],"likely_issue_sources":[],"recommended_improvement":{"category":"none","target_file":None,"reason":"dry-run"},"remaining_knowledge_gaps":[],"summary":"transport smoke test"}

def prompts():
    agent=("You are the Pearlmont WhatsApp Expert Property Sales Agent. Follow the accepted Brain and Skills context:\n"+brain_context()+"\n\nYour job is to understand the buyer, use relevant sourced facts, answer what you can, handle reasonable concerns, and progress a genuinely suitable buyer to a viewing. Appointment-ready handoff is a successful AI outcome when only live operational verification remains. Do not hand off a general question before doing useful sales work. Answer general price questions with supportable retrieved context and caveats; explain sourced LPPSA references before referring only individual eligibility for verification. Readiness does not require every profile field or exact price/availability. Once ready, avoid more generic qualification. Keep the customer experience continuous and natural: do not announce AI or say 'my boss'; use a brief natural pause/confirmation phrase when handing off. If asked directly whether you are AI/bot, answer truthfully. Never invent live price, package validity, inventory, financing approval, safety assurance, legal eligibility, or availability. Internal-only source content must never be exposed. On HANDOFF, state the reason; runner records HUMAN owner and pauses AI. Return JSON only: {\"action\":\"ASK|ANSWER|POSITION|HANDLE_OBJECTION|NARROW_UNIT|CLOSE_VIEWING|HANDOFF|ACKNOWLEDGE / MAINTAIN\",\"message\":\"customer-facing text\",\"lead_context\":{},\"assessment\":{\"appointment_readiness\":\"NOT_READY|EMERGING|READY_FOR_APPOINTMENT|APPOINTMENT_IN_PROGRESS|APPOINTMENT_CONFIRMED\",\"handoff_state\":\"NO_HANDOFF|HANDOFF_RECOMMENDED|HANDOFF_REQUIRED|HANDOFF_COMPLETED\",\"handoff_reason\":\"OPERATIONAL_BOOKING|UNIT_AVAILABILITY_VERIFICATION|PRICING_OR_PACKAGE_VERIFICATION|FINANCING_OR_ELIGIBILITY_REQUIRES_HUMAN|SALES_OWNERSHIP_CONFLICT|EXPLICIT_HUMAN_REQUEST|COMPLAINT_OR_DISPUTE|HIGH_RISK_FACTUAL_UNCERTAINTY|OTHER|null\"}}. Assessment is internal only; the hidden scenario is not available to you.")
    return agent,(SIM/"prompts/customer-simulator-v1.1.md").read_text(),(SIM/"prompts/human-handoff-executor.md").read_text(),(SIM/"prompts/judge-v1.2.md").read_text()

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
    transcript=[{"turn":0,"speaker":"customer","message":s["starting_message"]}]
    retrieval_trace=[]; agent_actions=[]; readiness_trace=[]; human_trace=[]; system_events=[]
    owner="AI"; ai_status="ACTIVE"; handoff_state="NO_HANDOFF"; handoff_reason=None; handoff_turn=None
    lead_context={}; customer_intent=s["buyer"].get("initial_intent","unknown"); customer_app="NO_VIEWING_INTENT"; terminal_customer=False; customer_turns=1; status="COMPLETED"; error=None; first_api_call=provider.calls
    max_customers=min(CONFIG.get("max_customer_turns",12),s["conversion"]["reasonable_max_turn_limit"],15)
    max_steps=max_customers*2+4
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
                u=json.dumps({"lead_context":lead,"history":transcript,"retrieved_project_knowledge":retrieved},ensure_ascii=False)
                ans=common.extract_json(provider.ask("sales_agent",agent_sys,u)); action=str(ans.get("action","ACKNOWLEDGE / MAINTAIN")).upper(); msg=str(ans.get("message","")).strip(); assessment=ans.get("assessment",{}) or {}
                rd=readiness(assessment.get("appointment_readiness")); reported_hs=enum(assessment.get("handoff_state"),HANDOFF,"NO_HANDOFF"); hs=reported_hs; hr=reason(assessment.get("handoff_reason"))
                if action=="HANDOFF":
                    handoff_state="HANDOFF_COMPLETED"; handoff_reason=hr or infer_reason(latest,retrieved); handoff_turn=turn; owner="HUMAN"; ai_status="PAUSED"
                    hs="HANDOFF_COMPLETED"
                elif hs in ("HANDOFF_RECOMMENDED","HANDOFF_REQUIRED"): handoff_state=hs; handoff_reason=hr or handoff_reason
                readiness_trace.append({"turn":turn,"appointment_readiness":rd,"handoff_state_reported":reported_hs,"handoff_state_effective":hs,"handoff_reason_reported":hr,"owner":"AI","ai_status":"ACTIVE"})
                lead_context=ans.get("lead_context",lead_context)
                event={"turn":turn,"action":action,"appointment_readiness":rd,"handoff_state_reported":reported_hs,"handoff_state":hs,"handoff_reason":handoff_reason,"owner_after_turn":owner,"ai_status_after_turn":ai_status}
                agent_actions.append(event); transcript.append({"turn":turn,"speaker":"agent","action":action,"message":msg,"assessment":{"appointment_readiness":rd,"handoff_state":hs,"handoff_reason":handoff_reason}})
                if action=="HANDOFF":
                    ev={"turn":turn,"speaker":"system","event":"HANDOFF_COMPLETED","owner":"HUMAN","ai_status":"PAUSED","handoff_reason":handoff_reason}
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
            cinput=json.dumps({"scenario":customer_scenario,"transcript":transcript,"turn":turn,"owner":owner,"ai_status":ai_status,"handoff_state":handoff_state,"handoff_reason":handoff_reason,"max_customer_turns":max_customers,"previous_appointment_state":customer_app},ensure_ascii=False)
            c=common.extract_json(provider.ask("customer_simulator",customer_sys,cinput)); cmsg=str(c.get("message","")).strip(); customer_app=app_state(c.get("appointment_state",customer_app)); customer_intent=c.get("final_intent",customer_intent); customer_turns+=1
            transcript.append({"turn":turn,"speaker":"customer","message":cmsg,"appointment_state":customer_app,"final_intent":customer_intent})
            terminal_customer=bool(c.get("done")) or customer_app=="APPOINTMENT_CONFIRMED" or customer_turns>=max_customers
            # The executor performs one bounded operational response. It does not become a second sales agent or repeat unavailable checks.
            if response_role=="HUMAN": break
        except Exception as e:
            status="RUN_FAILED"; error=f"{type(e).__name__}: {e}"; break
    # Deterministic suppression audit: no Agent message may occur after the handoff event.
    handoff_index=next((i for i,m in enumerate(transcript) if m.get("event")=="HANDOFF_COMPLETED"),None)
    violations=[m for i,m in enumerate(transcript) if handoff_index is not None and i>handoff_index and m.get("speaker")=="agent"]
    if violations: status="RUN_FAILED"; error="AI auto-send occurred after HANDOFF_COMPLETED"
    ai_final=readiness(readiness_trace[-1]["appointment_readiness"]) if readiness_trace else "NOT_READY"
    final_state=customer_app
    trace={"scenario_id":s["scenario_id"],"version":"1.2","model_config":CONFIG["models"],"attempted_at_utc":start,"status":status,"turns":{"customer":customer_turns,"ai":len(agent_actions),"human_handoff_executor":len(human_trace)},"owner_final":owner,"ai_status_final":ai_status,"handoff_state":handoff_state,"handoff_reason":handoff_reason,"handoff_turn":handoff_turn,"appointment_state_customer":final_state,"appointment_readiness_trace":readiness_trace,"agent_actions":agent_actions,"human_handoff_executor_trace":human_trace,"retrieval_trace":retrieval_trace,"system_events":system_events,"post_handoff_ai_reply_violations":len(violations),"transcript":transcript,"provider_calls":provider.calls-first_api_call,"retries":provider.retries,"error":error}
    transcript_path=outdir/f"{s['scenario_id']}.transcript.json"; transcript_path.write_text(json.dumps(trace,indent=2,ensure_ascii=False)+"\n")
    judge=None
    if status=="COMPLETED":
        try:
            source_paths=sorted({p for t in retrieval_trace for p in t["files"]}|{p for t in human_trace for p in t["retrieved_files"]})
            sources=[{"path":p,"content":(ROOT/p).read_text()} for p in source_paths]
            ju=json.dumps({"scenario":s,"transcript":transcript,"final_lead_state":{"owner":owner,"ai_status":ai_status,"handoff_state":handoff_state,"handoff_reason":handoff_reason,"customer_intent":customer_intent,"appointment_state":final_state,"ai_final_sales_state":ai_final,"human_sales_work":human_trace},"retrieval_trace":retrieval_trace,"agent_action_trace":agent_actions,"human_handoff_executor_trace":human_trace,"retrieved_source_material":sources},ensure_ascii=False)
            judge=common.extract_json(provider.ask("judge",judge_sys,ju))
        except Exception as e: status="RUN_FAILED"; error=f"Judge {type(e).__name__}: {e}"
    judge=judge or {}
    judge["appointment_state"]=app_state(judge.get("appointment_final_state",judge.get("appointment_state",final_state)))
    judge["appointment_readiness_final"]=readiness(judge.get("appointment_readiness_final")); judge["ready_for_appointment"]=bool(judge.get("ready_for_appointment",judge["appointment_readiness_final"] in READINESS[2:]))
    judge["handoff_timing"]=enum(judge.get("handoff_timing"),("TOO_EARLY","APPROPRIATE","TOO_LATE","NOT_NEEDED"),"NOT_NEEDED")
    judge["conversion_attribution"]=enum(judge.get("conversion_attribution"),ATTRIBUTION,"NO_CONVERSION")
    judge["sales_work_remaining_at_handoff"]=enum(judge.get("sales_work_remaining_at_handoff"),("NONE","LOW","MEDIUM","HIGH"),"LOW")
    judge["human_sales_work_required"]=enum(judge.get("human_sales_work_required"),("NONE","LOW","MEDIUM","HIGH"),human_trace[-1]["sales_work_level"] if human_trace else "NONE")
    judge["human_handoff_executor_used"]=bool(human_trace)
    judge["human_operational_task_completed"]=any(h.get("operational_task_completed") for h in human_trace)
    judge["buyer_primary_need"]=str(judge.get("buyer_primary_need",s.get("buyer",{}).get("hidden_motivation","Unspecified")))
    for key in ("key_information_learned","important_information_missed","missed_buying_signals","unnecessary_qualification","missed_selling_opportunity","retrieval_misses","retrieved_knowledge_not_used","factual_or_operational_overpromises","remaining_knowledge_gaps"):
        value=judge.get(key,[]); judge[key]=value if isinstance(value,list) else [str(value)]
    confirmed=judge["appointment_state"]=="APPOINTMENT_CONFIRMED"
    handoff_event_index=next((i for i,m in enumerate(transcript) if m.get("event")=="HANDOFF_COMPLETED"),None)
    ai_confirmed_before_handoff=any(m.get("speaker")=="customer" and app_state(m.get("appointment_state"))=="APPOINTMENT_CONFIRMED" and (handoff_event_index is None or i<handoff_event_index) for i,m in enumerate(transcript))
    ready_at_handoff=readiness(judge.get("readiness_state_at_handoff",readiness_trace[-1]["appointment_readiness"] if readiness_trace else "NOT_READY"))
    judge["readiness_state_at_handoff"]=ready_at_handoff
    if confirmed and (handoff_state!="HANDOFF_COMPLETED" or ai_confirmed_before_handoff): attribution="AI_DIRECT_CONVERSION"
    elif confirmed and handoff_state=="HANDOFF_COMPLETED" and ready_at_handoff in READINESS[2:] and bool(judge.get("ai_finished_sales_job_before_handoff")) and not bool(judge.get("human_rescued_conversion")) and handoff_reason in ("OPERATIONAL_BOOKING","UNIT_AVAILABILITY_VERIFICATION","PRICING_OR_PACKAGE_VERIFICATION"): attribution="AI_ASSISTED_HUMAN_CONFIRMATION"
    elif confirmed: attribution="HUMAN_LED_CONVERSION"
    elif not s["conversion"]["convertible"]: attribution="BAD_FIT_NO_CONVERSION"
    else: attribution="NO_CONVERSION"
    judge["conversion_attribution"]=attribution
    ai_outcome=classify_ai_outcome(judge,s,handoff_state,confirmed,ai_confirmed_before_handoff)
    judge["ai_outcome"]=ai_outcome
    judge["handoff_state"]=handoff_state; judge["handoff_reason"]=handoff_reason; judge["handoff_turn"]=handoff_turn
    judge["ai_final_sales_state"]=ai_final; judge["appointment_final_state"]=judge["appointment_state"]
    judge["post_handoff_ai_reply_violation"]=bool(violations)
    judge.setdefault("scores",{}); judge["scores"].setdefault("post_handoff_suppression",5 if not violations else 0)
    r={"scenario_id":s["scenario_id"],"title":s["title"],"convertible":s["conversion"]["convertible"],"buyer_primary_need":judge["buyer_primary_need"],"key_information_learned":judge["key_information_learned"],"important_information_missed":judge["important_information_missed"],"status":status,"transcript":transcript,"transcript_file":transcript_path.name,"retrieval_trace":retrieval_trace,"agent_actions":agent_actions,"appointment_readiness_trace":readiness_trace,"appointment_readiness_final":judge["appointment_readiness_final"],"ready_for_appointment":judge["ready_for_appointment"],"first_ready_turn":judge.get("first_ready_turn"),"handoff_state":handoff_state,"handoff_reason":handoff_reason,"handoff_turn":handoff_turn,"handoff_timing":judge["handoff_timing"],"ai_final_sales_state":ai_final,"ai_outcome":ai_outcome,"human_handoff_executor_used":bool(human_trace),"human_operational_task":judge.get("human_operational_task","NONE"),"human_sales_work_required":judge["human_sales_work_required"],"human_operational_task_completed":judge["human_operational_task_completed"],"human_handoff_executor_trace":human_trace,"appointment_final_state":judge["appointment_final_state"],"conversion_attribution":attribution,"sales_work_remaining_at_handoff":judge["sales_work_remaining_at_handoff"],"ai_handoff_too_early":judge["handoff_timing"]=="TOO_EARLY","ai_handoff_appropriate":judge["handoff_timing"]=="APPROPRIATE","ai_finished_sales_job_before_handoff":bool(judge.get("ai_finished_sales_job_before_handoff")),"human_merely_completed_logistics":bool(judge.get("human_merely_completed_logistics")),"human_rescued_conversion":bool(judge.get("human_rescued_conversion")),"judge":judge,"error":error}
    r["version"]="1.2"
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
    j=r["judge"]; lines=[f"# {r['scenario_id']} — {r['title']}","",f"- Convertible: {r['convertible']}",f"- Run: {r['status']}",f"- Buyer primary need: {r['buyer_primary_need']}",f"- Key information learned: {json.dumps(r['key_information_learned'],ensure_ascii=False)}",f"- Important information missed: {json.dumps(r['important_information_missed'],ensure_ascii=False)}",f"- Appointment readiness: {r['appointment_readiness_final']} (ready={r['ready_for_appointment']}, first ready turn={r['first_ready_turn']})",f"- Handoff: {r['handoff_state']} / {r['handoff_reason']} / turn {r['handoff_turn']} / {r['handoff_timing']}",f"- AI outcome: {r['ai_outcome']}",f"- Sales work remaining at handoff: {r['sales_work_remaining_at_handoff']}",f"- Human Handoff Executor used: {r['human_handoff_executor_used']}",f"- Human operational task/completed: {r['human_operational_task']} / {r['human_operational_task_completed']}",f"- Human sales work required: {r['human_sales_work_required']}",f"- Final appointment state: {r['appointment_final_state']}",f"- Conversion attribution: {r['conversion_attribution']}",f"- Post-handoff AI replies: {j['post_handoff_ai_reply_violation']}","","## Sales diagnosis",f"- Strongest AI move: {j.get('strongest_ai_move') or 'Not specified'}",f"- Weakest AI move: {j.get('weakest_ai_move') or 'Not specified'}",f"- Missed selling opportunity: {json.dumps(j.get('missed_selling_opportunity',[]),ensure_ascii=False)}",f"- Retrieved Knowledge not used: {json.dumps(j.get('retrieved_knowledge_not_used',[]),ensure_ascii=False)}",f"- Operational overpromises: {json.dumps(j.get('factual_or_operational_overpromises',[]),ensure_ascii=False)}",f"- Improvement recommendation: {j.get('improvement_recommendation') or 'Not specified'}","","## Judge scores",""]
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
    premature=counts["AI_EARLY_HANDOFF"]
    confirmed=[r for r in completed if r["appointment_final_state"]=="APPOINTMENT_CONFIRMED"]
    direct=[r for r in completed if r["ai_outcome"]=="AI_DIRECT_APPOINTMENT_SUCCESS"]
    ready_correct=sum(bool(r["judge"].get("readiness_detection_correct")) for r in completed)
    avg={k:round(sum(float(r["judge"].get("scores",{}).get(k,0)) for r in completed)/len(completed),2) if completed else None for k in SCORES}
    levels={"NONE":0,"LOW":1,"MEDIUM":2,"HIGH":3}; work_reports=[r for r in hand if r.get("sales_work_remaining_at_handoff") in levels]
    avg_work=round(sum(levels[r["sales_work_remaining_at_handoff"]] for r in work_reports)/len(work_reports),2) if work_reports else None
    retrieval_misses=[f"{r['scenario_id']}: {x}" for r in completed for x in r["judge"].get("retrieval_misses",[])]
    retrieval_unused=[f"{r['scenario_id']}: {x}" for r in completed for x in r["judge"].get("retrieved_knowledge_not_used",[])]
    gaps=[f"{r['scenario_id']}: {x}" for r in completed for x in r["judge"].get("remaining_knowledge_gaps",[])]
    flags=[{"scenario_id":r["scenario_id"],**f} for r in completed for f in r["judge"].get("critical_flags",[]) if isinstance(f,dict)]
    suppressed=sum(r["judge"].get("post_handoff_ai_reply_violation",False) for r in completed)
    v11=load_v11_comparison()
    op_completed=sum(r["human_operational_task_completed"] for r in successful_handoffs)
    obj={"version":"1.2","run_id":outdir.name,"models":CONFIG["models"],"scenario_count_attempted":len(reports),"scenario_count_completed":len(completed),"failed_runs":[r["scenario_id"] for r in reports if r["status"]!="COMPLETED"],"convertible_scenarios":len(conv),"ai_outcome_counts":counts,"appointment_ready_ai_successes":success,"appointment_ready_ai_success_rate":rate(success,len(conv)),"appointment_ready_handoff_count":counts["AI_APPOINTMENT_HANDOFF_SUCCESS"],"appointment_ready_handoff_rate":rate(counts["AI_APPOINTMENT_HANDOFF_SUCCESS"],len(conv)),"handoff_count":len(hand),"premature_handoffs":premature,"premature_handoff_rate":rate(premature,len(hand)),"missed_ready_buyers":counts["AI_MISSED_READY_BUYER"],"missed_ready_buyer_rate":rate(counts["AI_MISSED_READY_BUYER"],len(conv)),"lost_conversions":counts["AI_LOST_CONVERSION"],"progress_but_not_ready":counts["AI_PROGRESS_BUT_NOT_READY"],"ai_direct_confirmed_appointments":len(direct),"ai_direct_confirmed_appointment_rate":rate(len(direct),len(conv)),"end_to_end_confirmed_appointments":len(confirmed),"end_to_end_confirmed_appointment_rate":rate(len(confirmed),len(conv)),"human_operational_tasks_completed_after_successful_handoff":op_completed,"human_operational_completion_rate_after_successful_handoff":rate(op_completed,len(successful_handoffs)),"bad_fit_correctly_identified":counts["BAD_FIT_CORRECTLY_IDENTIFIED"],"bad_fit_identification_rate":rate(counts["BAD_FIT_CORRECTLY_IDENTIFIED"],len(nonconv)),"average_useful_information_capture_score":avg.get("useful_information_capture"),"readiness_detection_accuracy":rate(ready_correct,len(completed)),"readiness_detection_correct_count":ready_correct,"average_sales_work_remaining_at_handoff_level_0_none_1_low_2_medium_3_high":avg_work,"average_judge_scores":avg,"retrieval_misses":retrieval_misses,"retrieved_knowledge_not_used":retrieval_unused,"retrieval_quality_score":avg.get("retrieved_knowledge_utilization"),"retrieval_utilization_score":avg.get("retrieved_knowledge_utilization"),"critical_failure_count":len(flags),"critical_failures":flags,"remaining_knowledge_gaps":gaps,"remaining_sales_weaknesses":aggregate_weaknesses(completed),"post_handoff_ai_reply_violations":suppressed,"per_scenario_outcomes":{r["scenario_id"]:{"ai_outcome":r["ai_outcome"],"readiness":r["appointment_readiness_final"],"handoff":r["handoff_state"],"work_remaining":r["sales_work_remaining_at_handoff"]} for r in completed},"v1_1_comparison":compare_v11(v11,completed),"provider_calls":provider.calls,"provider_retries":provider.retries,"brain_and_sales_knowledge_unchanged":verify_protected_files(),"simulator_fixture_notice":"Human operational facts are synthetic fixtures, separate from Pearlmont Knowledge and not claims of real-world connected-system capability."}
    obj["executive_summary"]=(f"No—this run does not demonstrate reliable early-stage sales performance: appointment-ready AI success was {success}/{len(conv)} convertible scenarios ({obj['appointment_ready_ai_success_rate']}), with {premature}/{len(hand)} formal handoffs classified as premature and a missed-ready count of {counts['AI_MISSED_READY_BUYER']}. Successful operational handoffs were {counts['AI_APPOINTMENT_HANDOFF_SUCCESS']}/{len(conv)}. This KPI measures the AI's sales work, not completed property sales. Human completed {op_completed}/{len(successful_handoffs)} operational tasks after successful handoff. The per-scenario weaknesses and useful-information findings are detailed below.")
    (outdir/"aggregate.json").write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")
    (outdir/"aggregate.md").write_text(render_aggregate(obj))
    return obj

def rate(n,d): return round(n/d,3) if d else None
def aggregate_weaknesses(reports): return [f"{r['scenario_id']}: {r['judge'].get('weakest_ai_move')}" for r in reports if r['judge'].get('weakest_ai_move')]
def load_v11_comparison():
    p=SIM/"reports/RUN-V11-20261007T004245Z/aggregate.json"
    return json.loads(p.read_text()) if p.is_file() else {}
def compare_v11(old,reports):
    old_scores=old.get("average_judge_scores",{})
    current_scores={k:round(sum(float(r["judge"].get("scores",{}).get(k,0)) for r in reports)/len(reports),2) if reports else None for k in SCORES}
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
            early+=int(r.get("handoff_state")=="HANDOFF_COMPLETED" and not hready and r.get("handoff_timing")=="TOO_EARLY")
        except Exception: pass
    new_counts={k:sum(r["ai_outcome"]==k for r in reports) for k in AI_OUTCOMES}
    new_success=sum(new_counts[k] for k in ("AI_APPOINTMENT_READY_SUCCESS","AI_APPOINTMENT_HANDOFF_SUCCESS","AI_DIRECT_APPOINTMENT_SUCCESS"))
    return {"baseline_run":"RUN-V11-20261007T004245Z","baseline_metrics":{"appointment_ready_ai_successes_estimated_from_v1_1_fields":ready,"appointment_ready_handoff_successes_estimated_from_v1_1_fields":successful_handoff,"premature_handoffs":old.get("premature_handoffs"),"confirmed_appointments":old.get("end_to_end_confirmed_appointments"),"commercial_progression":old_scores.get("commercial_progression"),"naturalness":old_scores.get("sales_naturalness"),"handoff_judgment":old_scores.get("handoff_judgment"),"useful_information_capture":"not scored in V1.1","retrieved_knowledge_utilization":"not scored in V1.1"},"v1_2_metrics":{"appointment_ready_ai_successes":new_success,"appointment_ready_ai_success_rate":rate(new_success,len(conv)),"successful_appointment_ready_handoffs":new_counts["AI_APPOINTMENT_HANDOFF_SUCCESS"],"premature_handoffs":new_counts["AI_EARLY_HANDOFF"],"confirmed_appointments":sum(r["appointment_final_state"]=="APPOINTMENT_CONFIRMED" for r in reports),"commercial_progression":current_scores.get("commercial_progression"),"naturalness":current_scores.get("sales_naturalness"),"handoff_judgment":current_scores.get("handoff_judgment"),"useful_information_capture":current_scores.get("useful_information_capture"),"retrieved_knowledge_utilization":current_scores.get("retrieved_knowledge_utilization")},"note":"V1.1 did not classify appointment-ready AI outcomes; its baseline handoff-success estimate is reconstructed from saved readiness/work/timing fields and is not directly comparable to the V1.2 Judge classification."}

def verify_protected_files():
    import subprocess
    protected=["brain/AGENT.md","brain/SALES_FLOW.md","brain/INTENT_MODEL.md","brain/RESPONSE_RULES.md","knowledge/project/pearlmont/03_sales"]
    p=subprocess.run(["git","diff","--quiet","HEAD","--",*protected],cwd=ROOT)
    new=subprocess.run(["git","ls-files","--others","--exclude-standard","--",*protected],cwd=ROOT,capture_output=True,text=True)
    return p.returncode==0 and not new.stdout.strip()

def render_aggregate(o):
    lines=["# Simulator V1.2 Aggregate Diagnostic","",f"**Executive summary:** {o['executive_summary']}","","## Primary appointment-ready metrics","","| Metric | Count | Rate |","|---|---:|---:|",f"| Convertible scenarios | {o['convertible_scenarios']} | — |",f"| Appointment-ready AI successes | {o['appointment_ready_ai_successes']} | {o['appointment_ready_ai_success_rate']} |",f"| Successful appointment-ready handoffs | {o['appointment_ready_handoff_count']} | {o['appointment_ready_handoff_rate']} |",f"| Premature handoffs | {o['premature_handoffs']} | {o['premature_handoff_rate']} of handoffs |",f"| Missed-ready buyers | {o['missed_ready_buyers']} | {o['missed_ready_buyer_rate']} |",f"| AI direct appointments | {o['ai_direct_confirmed_appointments']} | {o['ai_direct_confirmed_appointment_rate']} |",f"| End-to-end confirmed appointments | {o['end_to_end_confirmed_appointments']} | {o['end_to_end_confirmed_appointment_rate']} |",f"| Human operational completion after successful handoff | {o['human_operational_tasks_completed_after_successful_handoff']} | {o['human_operational_completion_rate_after_successful_handoff']} |",f"| Bad-fit correctly identified | {o['bad_fit_correctly_identified']} | {o['bad_fit_identification_rate']} of non-convertible |","","## AI outcome classification","",json.dumps(o["ai_outcome_counts"],ensure_ascii=False,indent=2),"","## V1.1 comparison","",json.dumps(o["v1_1_comparison"],ensure_ascii=False,indent=2),"","## Diagnostic quality","",f"- Average useful information capture: {o['average_useful_information_capture_score']}/5",f"- Readiness detection accuracy: {o['readiness_detection_accuracy']}",f"- Average sales work remaining at handoff (NONE=0, LOW=1, MEDIUM=2, HIGH=3): {o['average_sales_work_remaining_at_handoff_level_0_none_1_low_2_medium_3_high']}",f"- Retrieval quality/utilization: {o['retrieval_quality_score']}/5",f"- Critical failures: {o['critical_failure_count']}",f"- Post-handoff AI reply violations: {o['post_handoff_ai_reply_violations']}",f"- All scenarios completed: {o['scenario_count_completed']}/{o['scenario_count_attempted']}","","## Average Judge scores",""]
    lines += [f"- {k}: {v}/5" for k,v in o["average_judge_scores"].items()]
    lines += ["","## Retrieval misses",""]+(["- "+x for x in o["retrieval_misses"]] if o["retrieval_misses"] else ["- None identified."])
    lines += ["","## Retrieved Knowledge not used",""]+(["- "+x for x in o["retrieved_knowledge_not_used"]] if o["retrieved_knowledge_not_used"] else ["- None identified."])
    lines += ["","## Remaining Knowledge gaps",""]+(["- "+x for x in o["remaining_knowledge_gaps"]] if o["remaining_knowledge_gaps"] else ["- None identified."])
    lines += ["","## Remaining sales weaknesses",""]+["- "+x for x in o["remaining_sales_weaknesses"]]
    lines += ["","## Critical failures","",json.dumps(o["critical_failures"],ensure_ascii=False,indent=2),"","## Fixture and integrity notes","",o["simulator_fixture_notice"],f"- Brain and protected 03_sales files unchanged: {o['brain_and_sales_knowledge_unchanged']}",""]
    return "\n".join(lines)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--dry-run",action="store_true"); ap.add_argument("--scenario",action="append"); ap.add_argument("--output")
    a=ap.parse_args(); stamp=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"); out=SIM/"reports"/(a.output or ("DRYRUN-V12-" if a.dry_run else "RUN-V12-")+stamp); out.mkdir(parents=True,exist_ok=False)
    files=sorted((SIM/"scenarios/pearlmont").glob("PEA-*.json")); selected=set(a.scenario or []); files=[p for p in files if not selected or p.stem in selected]
    if not files: raise SystemExit("No scenarios selected")
    provider=Provider(a.dry_run); reports=[]
    for p in files:
        print(f"[{p.stem}] starting",flush=True); r=run_scenario(p,provider,out); reports.append(r); print(f"[{p.stem}] {r['status']} handoff={r['handoff_state']} ai_outcome={r['ai_outcome']}",flush=True)
    ag=aggregate(reports,out,provider); print(json.dumps({"report_dir":str(out),"total":ag["scenario_count_attempted"],"completed":ag["scenario_count_completed"],"failed":ag["failed_runs"],"handoffs":ag["handoff_count"],"post_handoff_violations":ag["post_handoff_ai_reply_violations"]},indent=2))
    return 2 if a.dry_run and (ag["scenario_count_completed"]!=ag["scenario_count_attempted"] or ag["post_handoff_ai_reply_violations"]>0) else (1 if ag["failed_runs"] else 0)

if __name__=="__main__": sys.exit(main())
