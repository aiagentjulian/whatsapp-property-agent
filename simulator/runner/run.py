#!/usr/bin/env python3
"""Pearlmont Simulator V1.1: separate sales readiness, operational handoff and human closure."""
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
SCORES=common.DIMENSIONS+["appointment_readiness_detection","handoff_timing","handoff_reason_correctness","post_handoff_suppression","conversion_attribution"]

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
            if role=="human_closer": return json.dumps({"message":"I’ll check the details and follow up with you.","operational_action":"NO_ACTION","sales_work_level":"LOW","appointment_state":"NO_VIEWING_INTENT"})
            return json.dumps(dry_judgment())
        return super().ask(role,system,user)

def dry_judgment():
    return {"appointment_state":"NO_VIEWING_INTENT","appointment_readiness_final":"EMERGING","ready_for_appointment":False,"first_ready_turn":None,"readiness_detection_correct":True,"readiness_state_at_handoff":"EMERGING","handoff_state":"HANDOFF_COMPLETED","handoff_reason":"OPERATIONAL_BOOKING","handoff_turn":1,"handoff_timing":"APPROPRIATE","handoff_reason_correct":True,"handoff_quality_score":3,"ai_final_sales_state":"EMERGING","human_closer_used":True,"appointment_final_state":"NO_VIEWING_INTENT","conversion_attribution":"NO_CONVERSION","sales_work_remaining_at_handoff":"LOW","ai_finished_sales_job_before_handoff":False,"human_merely_completed_logistics":False,"human_rescued_conversion":False,"post_handoff_ai_reply_violation":False,"scores":{k:3 for k in SCORES},"critical_flags":[],"conversion_analysis":{"what_moved_buyer_forward":[],"what_reduced_conversion_probability":[],"where_conversion_was_won_or_lost":"dry-run"},"what_agent_did_well":[],"weak_or_wrong_sales_move":"dry-run","better_next_move":"dry-run","missed_buying_signals":[],"unnecessary_qualification":[],"unsupported_factual_claims":[],"retrieval_misses":[],"likely_issue_sources":[],"recommended_improvement":{"category":"none","target_file":None,"reason":"dry-run"},"remaining_knowledge_gaps":[],"summary":"transport smoke test"}

def prompts():
    agent=("You are the Pearlmont WhatsApp Sales Agent. Follow this accepted Brain and Skills context:\n"+brain_context()+"\n\nUse only the latest message and selectively retrieved Knowledge. Never invent live price, package validity, inventory, financing approval, safety assurance, legal eligibility, or availability. Internal-only source content must never be exposed. Continue selling when useful; appointment readiness is separate from human handoff. A human is needed only for specific operational/sensitive work. Once you choose HANDOFF, state the correct reason; runner will formally set owner HUMAN and pause AI. Return JSON only: {\"action\":\"ASK|ANSWER|POSITION|HANDLE_OBJECTION|NARROW_UNIT|CLOSE_VIEWING|HANDOFF|ACKNOWLEDGE / MAINTAIN\",\"message\":\"customer-facing text\",\"lead_context\":{},\"assessment\":{\"appointment_readiness\":\"NOT_READY|EMERGING|READY_FOR_APPOINTMENT|APPOINTMENT_IN_PROGRESS|APPOINTMENT_CONFIRMED\",\"handoff_state\":\"NO_HANDOFF|HANDOFF_RECOMMENDED|HANDOFF_REQUIRED|HANDOFF_COMPLETED\",\"handoff_reason\":\"OPERATIONAL_BOOKING|UNIT_AVAILABILITY_VERIFICATION|PRICING_OR_PACKAGE_VERIFICATION|FINANCING_OR_ELIGIBILITY_REQUIRES_HUMAN|SALES_OWNERSHIP_CONFLICT|EXPLICIT_HUMAN_REQUEST|COMPLAINT_OR_DISPUTE|HIGH_RISK_FACTUAL_UNCERTAINTY|OTHER|null\"}}. This readiness and handoff assessment is internal only. The hidden scenario is not available to you.")
    return agent,(SIM/"prompts/customer-simulator-v1.1.md").read_text(),(SIM/"prompts/human-closer.md").read_text(),(SIM/"prompts/judge.md").read_text()

def human_system(base, reason_value):
    return base+"\n\nHandoff reason: "+str(reason_value)+". You may only act now because HANDOFF_COMPLETED has been recorded. The AI owner is permanently paused for this scenario."

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
                u=json.dumps({"transcript":transcript,"lead_context":{"agent_lead":lead_context,"customer_appointment_state":customer_app,"owner":owner,"ai_status":ai_status,"handoff_state":handoff_state,"handoff_reason":handoff_reason},"handoff_reason":handoff_reason,"verified_scenario_truth":{"human_operations":ops,"buyer_truth":s["buyer"],"critical_facts":s.get("critical_facts")},"relevant_verified_knowledge":needed},ensure_ascii=False)
                h=common.extract_json(provider.ask("human_closer",human_system(human_base,handoff_reason),u)); msg=str(h.get("message","")).strip()
                he={"turn":turn,"operational_action":h.get("operational_action","NO_ACTION"),"sales_work_level":enum(h.get("sales_work_level"),("NONE","LOW","MEDIUM","HIGH"),"LOW"),"appointment_state":app_state(h.get("appointment_state")),"owner":"HUMAN","ai_status":"PAUSED","retrieved_files":[x["path"] for x in retrieved]}
                human_trace.append(he); transcript.append({"turn":turn,"speaker":"human","message":msg,"action":he["operational_action"],"sales_work_level":he["sales_work_level"]})
                if terminal_customer or customer_turns>=max_customers: break
            # Customer receives the last AI/human message. After a formal transfer, only Human Closer may reply.
            latest_reply=transcript[-1].get("message","")
            customer_scenario={k:v for k,v in s.items() if k!="human_operations"}
            cinput=json.dumps({"scenario":customer_scenario,"transcript":transcript,"turn":turn,"owner":owner,"ai_status":ai_status,"handoff_state":handoff_state,"handoff_reason":handoff_reason,"max_customer_turns":max_customers,"previous_appointment_state":customer_app},ensure_ascii=False)
            c=common.extract_json(provider.ask("customer_simulator",customer_sys,cinput)); cmsg=str(c.get("message","")).strip(); customer_app=app_state(c.get("appointment_state",customer_app)); customer_intent=c.get("final_intent",customer_intent); customer_turns+=1
            transcript.append({"turn":turn,"speaker":"customer","message":cmsg,"appointment_state":customer_app,"final_intent":customer_intent})
            terminal_customer=bool(c.get("done")) or customer_app=="APPOINTMENT_CONFIRMED" or customer_turns>=max_customers
            if response_role=="HUMAN" and terminal_customer: break
        except Exception as e:
            status="RUN_FAILED"; error=f"{type(e).__name__}: {e}"; break
    # Deterministic suppression audit: no Agent message may occur after the handoff event.
    handoff_index=next((i for i,m in enumerate(transcript) if m.get("event")=="HANDOFF_COMPLETED"),None)
    violations=[m for i,m in enumerate(transcript) if handoff_index is not None and i>handoff_index and m.get("speaker")=="agent"]
    if violations: status="RUN_FAILED"; error="AI auto-send occurred after HANDOFF_COMPLETED"
    ai_final=readiness(readiness_trace[-1]["appointment_readiness"]) if readiness_trace else "NOT_READY"
    final_state=customer_app
    trace={"scenario_id":s["scenario_id"],"version":"1.1","model_config":CONFIG["models"],"attempted_at_utc":start,"status":status,"turns":{"customer":customer_turns,"ai":len(agent_actions),"human_closer":len(human_trace)},"owner_final":owner,"ai_status_final":ai_status,"handoff_state":handoff_state,"handoff_reason":handoff_reason,"handoff_turn":handoff_turn,"appointment_state_customer":final_state,"appointment_readiness_trace":readiness_trace,"agent_actions":agent_actions,"human_closer_trace":human_trace,"retrieval_trace":retrieval_trace,"system_events":system_events,"post_handoff_ai_reply_violations":len(violations),"transcript":transcript,"provider_calls":provider.calls-first_api_call,"retries":provider.retries,"error":error}
    transcript_path=outdir/f"{s['scenario_id']}.transcript.json"; transcript_path.write_text(json.dumps(trace,indent=2,ensure_ascii=False)+"\n")
    judge=None
    if status=="COMPLETED":
        try:
            source_paths=sorted({p for t in retrieval_trace for p in t["files"]}|{p for t in human_trace for p in t["retrieved_files"]})
            sources=[{"path":p,"content":(ROOT/p).read_text()} for p in source_paths]
            ju=json.dumps({"scenario":s,"transcript":transcript,"final_lead_state":{"owner":owner,"ai_status":ai_status,"handoff_state":handoff_state,"handoff_reason":handoff_reason,"customer_intent":customer_intent,"appointment_state":final_state,"ai_final_sales_state":ai_final,"human_sales_work":human_trace},"retrieval_trace":retrieval_trace,"agent_action_trace":agent_actions,"human_closer_trace":human_trace,"retrieved_source_material":sources},ensure_ascii=False)
            judge=common.extract_json(provider.ask("judge",judge_sys,ju))
        except Exception as e: status="RUN_FAILED"; error=f"Judge {type(e).__name__}: {e}"
    judge=judge or {}
    judge["appointment_state"]=app_state(judge.get("appointment_final_state",judge.get("appointment_state",final_state)))
    judge["appointment_readiness_final"]=readiness(judge.get("appointment_readiness_final")); judge["ready_for_appointment"]=bool(judge.get("ready_for_appointment",judge["appointment_readiness_final"] in READINESS[2:]))
    judge["handoff_timing"]=enum(judge.get("handoff_timing"),("TOO_EARLY","APPROPRIATE","TOO_LATE","NOT_NEEDED"),"NOT_NEEDED")
    judge["conversion_attribution"]=enum(judge.get("conversion_attribution"),ATTRIBUTION,"NO_CONVERSION")
    judge["sales_work_remaining_at_handoff"]=enum(judge.get("sales_work_remaining_at_handoff"),("NONE","LOW","MEDIUM","HIGH"),"LOW")
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
    judge["handoff_state"]=handoff_state; judge["handoff_reason"]=handoff_reason; judge["handoff_turn"]=handoff_turn
    judge["human_closer_used"]=bool(human_trace); judge["ai_final_sales_state"]=ai_final; judge["appointment_final_state"]=judge["appointment_state"]
    judge["post_handoff_ai_reply_violation"]=bool(violations)
    judge.setdefault("scores",{}); judge["scores"].setdefault("post_handoff_suppression",5 if not violations else 0)
    r={"scenario_id":s["scenario_id"],"title":s["title"],"convertible":s["conversion"]["convertible"],"status":status,"transcript":transcript,"transcript_file":transcript_path.name,"retrieval_trace":retrieval_trace,"agent_actions":agent_actions,"appointment_readiness_trace":readiness_trace,"appointment_readiness_final":judge["appointment_readiness_final"],"ready_for_appointment":judge["ready_for_appointment"],"first_ready_turn":judge.get("first_ready_turn"),"handoff_state":handoff_state,"handoff_reason":handoff_reason,"handoff_turn":handoff_turn,"handoff_timing":judge["handoff_timing"],"ai_final_sales_state":ai_final,"human_closer_used":bool(human_trace),"human_closer_trace":human_trace,"appointment_final_state":judge["appointment_final_state"],"conversion_attribution":attribution,"sales_work_remaining_at_handoff":judge["sales_work_remaining_at_handoff"],"ai_handoff_too_early":judge["handoff_timing"]=="TOO_EARLY","ai_handoff_appropriate":judge["handoff_timing"]=="APPROPRIATE","ai_finished_sales_job_before_handoff":bool(judge.get("ai_finished_sales_job_before_handoff")),"human_merely_completed_logistics":bool(judge.get("human_merely_completed_logistics")),"human_rescued_conversion":bool(judge.get("human_rescued_conversion")),"judge":judge,"error":error}
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
    j=r["judge"]; lines=[f"# {r['scenario_id']} — {r['title']}","",f"- Convertible: {r['convertible']}",f"- Run: {r['status']}",f"- Appointment readiness: {r['appointment_readiness_final']} (ready={r['ready_for_appointment']}, first ready turn={r['first_ready_turn']})",f"- Handoff: {r['handoff_state']} / {r['handoff_reason']} / turn {r['handoff_turn']} / {r['handoff_timing']}",f"- AI final sales state: {r['ai_final_sales_state']}",f"- Human Closer used: {r['human_closer_used']}",f"- Appointment final state: {r['appointment_final_state']}",f"- Conversion attribution: {r['conversion_attribution']}",f"- Sales work remaining at handoff: {r['sales_work_remaining_at_handoff']}",f"- AI finished sales before handoff: {r['ai_finished_sales_job_before_handoff']}",f"- Human only completed logistics: {r['human_merely_completed_logistics']}",f"- Human rescued conversion: {r['human_rescued_conversion']}",f"- Post-handoff AI replies: {j['post_handoff_ai_reply_violation']}","","## Judge scores",""]
    lines += [f"- {k.replace('_',' ').title()}: {v}/5" for k,v in j.get("scores",{}).items()]
    lines += ["","## Critical flags","",json.dumps(j.get("critical_flags",[]),ensure_ascii=False),"","## Summary","",str(j.get("summary","")),"","## Handoff and attribution assessment","",str(j.get("handoff_timing_reason","")),str(j.get("conversion_analysis",{})),"","## Retrieval trace","",json.dumps(r["retrieval_trace"],ensure_ascii=False,indent=2),"","## Remaining knowledge gaps","",json.dumps(j.get("remaining_knowledge_gaps",[]),ensure_ascii=False,indent=2),"","## Full transcript",""]
    for m in r["transcript"]: lines.append(f"**{m.get('speaker','').title()} ({m.get('turn',0)}):** {m.get('message',m.get('event',''))}"+(f" _[{m['action']}]_" if m.get('action') else ""))
    return "\n".join(lines)+"\n"

def aggregate(reports,outdir,provider):
    completed=[r for r in reports if r["status"]=="COMPLETED"]; conv=[r for r in completed if r["convertible"]]; nonconv=[r for r in completed if not r["convertible"]]
    confirmed=[r for r in completed if r["appointment_final_state"]=="APPOINTMENT_CONFIRMED"]
    direct=[r for r in confirmed if r["conversion_attribution"]=="AI_DIRECT_CONVERSION"]
    assisted=[r for r in confirmed if r["conversion_attribution"]=="AI_ASSISTED_HUMAN_CONFIRMATION"]
    human_led=[r for r in confirmed if r["conversion_attribution"]=="HUMAN_LED_CONVERSION"]
    app_interest=[r for r in completed if r["appointment_final_state"] in ("VIEWING_SUGGESTED","VIEWING_INTEREST","APPOINTMENT_IN_PROGRESS")]
    avg={k:round(sum(float(r["judge"].get("scores",{}).get(k,0)) for r in completed)/len(completed),2) if completed else None for k in SCORES}
    hand=[r for r in completed if r["handoff_state"]=="HANDOFF_COMPLETED"]
    timing=lambda t:sum(r["handoff_timing"]==t for r in hand)
    ready_correct=sum(bool(r["judge"].get("readiness_detection_correct")) for r in completed)
    outcomes={}
    for r in completed: outcomes[r["conversion_attribution"]]=outcomes.get(r["conversion_attribution"],0)+1
    retrieval_misses=[f"{r['scenario_id']}: {x}" for r in completed for x in r["judge"].get("retrieval_misses",[])]
    gaps=[f"{r['scenario_id']}: {x}" for r in completed for x in r["judge"].get("remaining_knowledge_gaps",[])]
    flags=[{"scenario_id":r["scenario_id"],**f} for r in completed for f in r["judge"].get("critical_flags",[]) if isinstance(f,dict)]
    suppressed=sum(r["judge"].get("post_handoff_ai_reply_violation",False) for r in completed)
    v1=load_v1_comparison()
    obj={"version":"1.1","run_id":outdir.name,"models":CONFIG["models"],"total_scenarios":len(reports),"completed_scenarios":len(completed),"failed_runs":[r["scenario_id"] for r in reports if r["status"]!="COMPLETED"],"convertible_scenarios":len(conv),"ai_direct_confirmed_appointments":len(direct),"ai_assisted_human_confirmations":len(assisted),"human_led_confirmations":len(human_led),"end_to_end_confirmed_appointments":len(confirmed),"ai_direct_conversion_rate":rate(len(direct),len(conv)),"ai_sales_success_count":len(direct)+len(assisted),"ai_sales_success_rate":rate(len(direct)+len(assisted),len(conv)),"end_to_end_conversion_rate":rate(len(confirmed),len(conv)),"human_led_conversion_count":len(human_led),"human_led_conversion_rate":rate(len(human_led),len(conv)),"appointment_interest_only_cases":len(app_interest),"bad_fit_correctly_rejected":sum(r["conversion_attribution"]=="BAD_FIT_NO_CONVERSION" for r in nonconv),"appointment_outcome_counts":outcomes,"handoff_count":len(hand),"appropriate_handoffs":timing("APPROPRIATE"),"premature_handoffs":timing("TOO_EARLY"),"late_handoffs":timing("TOO_LATE"),"unnecessary_handoffs":sum(r["handoff_timing"]=="NOT_NEEDED" for r in hand),"post_handoff_ai_reply_violations":suppressed,"readiness_detection_accuracy":rate(ready_correct,len(completed)),"readiness_detection_correct_count":ready_correct,"critical_failure_count":len(flags),"critical_failures":flags,"average_judge_scores":avg,"retrieval_misses":retrieval_misses,"remaining_knowledge_gaps":gaps,"remaining_sales_weaknesses":aggregate_weaknesses(completed),"per_scenario_outcomes":{r["scenario_id"]:{"ready":r["appointment_readiness_final"],"handoff":r["handoff_state"],"attribution":r["conversion_attribution"]} for r in completed},"v1_comparison":compare(v1,completed),"provider_calls":provider.calls,"provider_retries":provider.retries,"brain_and_sales_knowledge_unchanged":verify_protected_files(),"internal_ownership_knowledge_created":"knowledge/project/pearlmont/04_internal/sales-conflict-and-ownership.md"}
    obj["executive_summary"]=(f"V1.1 completed {len(completed)}/{len(reports)} scenarios. {len(direct)} AI-direct, {len(assisted)} AI-assisted human, and {len(human_led)} human-led confirmed appointments; {len(confirmed)} end-to-end total among {len(conv)} convertible buyers. {len(hand)} formal handoffs; post-handoff AI reply violations: {suppressed}.")
    (outdir/"aggregate.json").write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")
    (outdir/"aggregate.md").write_text(render_aggregate(obj))
    return obj

def rate(n,d): return round(n/d,3) if d else None
def aggregate_weaknesses(reports): return [f"{r['scenario_id']}: {r['judge'].get('weak_or_wrong_sales_move')}" for r in reports if r['judge'].get('weak_or_wrong_sales_move')]
def load_v1_comparison():
    p=SIM/"reports/RUN-20261007T010756Z/aggregate.json"
    return json.loads(p.read_text()) if p.is_file() else {}
def compare(v1,reports):
    scores=v1.get("average_judge_scores",{}); current={k:round(sum(float(r["judge"].get("scores",{}).get(k,0)) for r in reports)/len(reports),2) if reports else None for k in SCORES}
    old_run=SIM/"reports/RUN-20261007T010756Z"; old_interest=v1.get("appointment_interest_cases")
    old_repeated=0
    for p in old_run.glob("PEA-*.transcript.json"):
        try:
            tr=json.loads(p.read_text())["transcript"]; handed=False
            for m in tr:
                if m.get("speaker")=="agent" and m.get("action")=="HANDOFF": handed=True
                elif handed and m.get("speaker")=="agent": old_repeated+=1
        except Exception: pass
    return {"v1_run":"RUN-20261007T010756Z","metrics":{"confirmed_appointments":{"v1":v1.get("confirmed_appointments",0),"v1_1":sum(r["appointment_final_state"]=="APPOINTMENT_CONFIRMED" for r in reports)},"appointment_interest":{"v1":old_interest,"v1_1":sum(r["appointment_final_state"] in ("VIEWING_SUGGESTED","VIEWING_INTEREST","APPOINTMENT_IN_PROGRESS") for r in reports)},"commercial_progression":{"v1":scores.get("commercial_progression"),"v1_1":current.get("commercial_progression")},"naturalness":{"v1":scores.get("sales_naturalness"),"v1_1":current.get("sales_naturalness")},"handoff_judgment":{"v1":scores.get("handoff_judgment"),"v1_1":current.get("handoff_judgment")},"retrieval_quality":{"v1_misses":v1.get("retrieval_misses",[]),"v1_1_misses":sum((r["judge"].get("retrieval_misses") or [] for r in reports),[])},"post_handoff_repetition":{"v1_formal_tracking":"not implemented; proxy counts agent messages after an Agent action tagged HANDOFF","v1_proxy_agent_replies_after_handoff":old_repeated,"v1_1_violations":sum(bool(r["judge"].get("post_handoff_ai_reply_violation")) for r in reports)},"conversion_attribution":{"v1":"not tracked","v1_1":{k:sum(r["conversion_attribution"]==k for r in reports) for k in ATTRIBUTION}}}}

def verify_protected_files():
    import subprocess
    protected=["brain/AGENT.md","brain/SALES_FLOW.md","brain/INTENT_MODEL.md","brain/RESPONSE_RULES.md","knowledge/project/pearlmont/03_sales"]
    p=subprocess.run(["git","diff","--quiet","HEAD","--",*protected],cwd=ROOT)
    new=subprocess.run(["git","ls-files","--others","--exclude-standard","--",*protected],cwd=ROOT,capture_output=True,text=True)
    return p.returncode==0 and not new.stdout.strip()

def render_aggregate(o):
    lines=["# Simulator V1.1 Aggregate & V1 Comparison","",f"**Executive summary:** {o['executive_summary']}","","## Conversion attribution","","| Metric | Count | Rate among convertible |","|---|---:|---:|",f"| AI direct | {o['ai_direct_confirmed_appointments']} | {o['ai_direct_conversion_rate']} |",f"| AI-assisted human confirmation | {o['ai_assisted_human_confirmations']} | — |",f"| Human-led conversion | {o['human_led_confirmations']} | {o['human_led_conversion_rate']} |",f"| End-to-end confirmed | {o['end_to_end_confirmed_appointments']} | {o['end_to_end_conversion_rate']} |",f"| AI sales success (direct + assisted) | {o['ai_sales_success_count']} | {o['ai_sales_success_rate']} |","",f"Scenarios: {o['completed_scenarios']}/{o['total_scenarios']}; convertible: {o['convertible_scenarios']}; interest-only: {o['appointment_interest_only_cases']}; bad-fit correctly rejected: {o['bad_fit_correctly_rejected']}. Handoffs: {o['handoff_count']} (appropriate {o['appropriate_handoffs']}, too early {o['premature_handoffs']}, too late {o['late_handoffs']}, unnecessary {o['unnecessary_handoffs']}). Readiness accuracy: {o['readiness_detection_accuracy']}. Post-handoff AI reply violations: {o['post_handoff_ai_reply_violations']}. Critical failures: {o['critical_failure_count']}.","","## V1 comparison","",json.dumps(o["v1_comparison"],ensure_ascii=False,indent=2),"","## Average Judge scores",""]
    lines += [f"- {k}: {v}/5" for k,v in o["average_judge_scores"].items()]
    lines += ["","## Remaining Knowledge gaps",""]
    lines += ["- "+x for x in o["remaining_knowledge_gaps"]] if o["remaining_knowledge_gaps"] else ["- None identified by Judge."]
    lines += ["","## Remaining Sales Agent weaknesses",""]+["- "+x for x in o["remaining_sales_weaknesses"]]
    lines += ["","## Retrieval misses",""]
    lines += ["- "+x for x in o["retrieval_misses"]] if o["retrieval_misses"] else ["- None identified."]
    lines += ["","## Critical failures","",json.dumps(o["critical_failures"],ensure_ascii=False,indent=2),"","## Integrity","",f"- Brain and protected 03_sales files unchanged: {o['brain_and_sales_knowledge_unchanged']}","- Internal ownership guide created; internal audience only.",""]
    return "\n".join(lines)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--dry-run",action="store_true"); ap.add_argument("--scenario",action="append"); ap.add_argument("--output")
    a=ap.parse_args(); stamp=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"); out=SIM/"reports"/(a.output or ("DRYRUN-V11-" if a.dry_run else "RUN-V11-")+stamp); out.mkdir(parents=True,exist_ok=False)
    files=sorted((SIM/"scenarios/pearlmont").glob("PEA-*.json")); selected=set(a.scenario or []); files=[p for p in files if not selected or p.stem in selected]
    if not files: raise SystemExit("No scenarios selected")
    provider=Provider(a.dry_run); reports=[]
    for p in files:
        print(f"[{p.stem}] starting",flush=True); r=run_scenario(p,provider,out); reports.append(r); print(f"[{p.stem}] {r['status']} owner={r['judge'].get('handoff_state')} attribution={r['conversion_attribution']}",flush=True)
    ag=aggregate(reports,out,provider); print(json.dumps({"report_dir":str(out),"total":ag["total_scenarios"],"completed":ag["completed_scenarios"],"failed":ag["failed_runs"],"handoffs":ag["handoff_count"],"post_handoff_violations":ag["post_handoff_ai_reply_violations"]},indent=2))
    return 2 if a.dry_run and (ag["completed_scenarios"]!=ag["total_scenarios"] or ag["post_handoff_ai_reply_violations"]>0) else (1 if ag["failed_runs"] else 0)

if __name__=="__main__": sys.exit(main())
