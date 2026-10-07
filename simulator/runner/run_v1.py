#!/usr/bin/env python3
"""Small multi-role Pearlmont simulator. Uses only stdlib plus OpenAI Responses API."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, re, sys, time, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SIM = ROOT / "simulator"
KNOW = ROOT / "knowledge/project/pearlmont"
CONFIG = json.loads((SIM / "config.json").read_text())
DIMENSIONS = ["customer_understanding", "latest_message_responsiveness", "qualification_discipline", "selling_angle_relevance", "objection_handling", "unit_fit_judgment", "buying_signal_detection", "appointment_judgment", "factual_accuracy", "sales_naturalness", "handoff_judgment", "commercial_progression"]
ACTION = "ASK|ANSWER|POSITION|HANDLE_OBJECTION|NARROW_UNIT|CLOSE_VIEWING|HANDOFF|ACKNOWLEDGE / MAINTAIN"

def digest_tree(path: Path) -> str:
    h=hashlib.sha256()
    for p in sorted(path.rglob("*")):
        if p.is_file(): h.update(str(p.relative_to(path)).encode()); h.update(p.read_bytes())
    return h.hexdigest()

def extract_json(s: str):
    s=s.strip()
    try: return json.loads(s)
    except json.JSONDecodeError:
        decoder=json.JSONDecoder()
        for i,ch in enumerate(s):
            if ch!="{": continue
            try:
                value,_=decoder.raw_decode(s,i)
                if isinstance(value,dict): return value
            except json.JSONDecodeError:
                continue
        raise

def response_text(data):
    if isinstance(data, str): return data
    if isinstance(data, dict) and "output_text" in data: return data["output_text"]
    chunks=[]
    for item in data.get("output",[]):
        for c in item.get("content",[]):
            if c.get("type") in ("output_text","text"): chunks.append(c.get("text",""))
    if not chunks: raise ValueError("Responses API returned no output text")
    return "\n".join(chunks)

def normalize_appointment_state(value):
    s=str(value or "").strip().upper().replace("-","_")
    if "APPOINTMENT_CONFIRMED" in s or "CONFIRMED_APPOINTMENT" in s or ("CONFIRMED" in s and "NOT CONFIRMED" not in s): return "APPOINTMENT_CONFIRMED"
    if "APPOINTMENT_IN_PROGRESS" in s or "IN_PROGRESS" in s: return "APPOINTMENT_IN_PROGRESS"
    if "VIEWING_INTEREST" in s or "APPOINTMENT_INTEREST" in s or "INTEREST" in s: return "VIEWING_INTEREST"
    if "VIEWING_SUGGESTED" in s or "SUGGESTED" in s: return "VIEWING_SUGGESTED"
    return "NO_VIEWING_INTENT"

class Provider:
    def __init__(self,dry=False): self.dry=dry; self.calls=0; self.retries=[]
    def ask(self,role,system,user):
        self.calls+=1
        if self.dry:
            if role=="sales_agent": return json.dumps({"action":"ANSWER","message":"Thanks for asking. I can help check the current details for you.","lead_context":{}})
            if role=="customer_simulator": return json.dumps({"message":"Okay, thanks.","done":True,"appointment_state":"NO_VIEWING_INTENT","final_intent":"low"})
            return json.dumps({"appointment_state":"NO_VIEWING_INTENT","scenario_success":True,"good_judgment":True,"final_lead_intent":"low","scores":{k:3 for k in DIMENSIONS},"critical_flags":[],"conversion_analysis":{"what_moved_buyer_forward":[],"what_reduced_conversion_probability":[],"where_conversion_was_won_or_lost":"dry-run"},"what_agent_did_well":[],"weak_or_wrong_sales_move":"dry-run","better_next_move":"dry-run","close_timing":"not_applicable","missed_buying_signals":[],"unnecessary_qualification":[],"unsupported_factual_claims":[],"retrieval_misses":[],"likely_issue_sources":[],"recommended_improvement":{"category":"none","target_file":None,"reason":"dry-run"},"summary":"transport smoke test"})
        key=os.environ.get("OPENAI_API_KEY")
        if not key: raise RuntimeError("OPENAI_API_KEY is required")
        cfg=CONFIG["models"][role]
        payload={"model":cfg["model"],"reasoning":{"effort":cfg["reasoning"]},"instructions":system,"input":user,"store":False}
        req=urllib.request.Request("https://api.openai.com/v1/responses",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
        for attempt in range(CONFIG.get("retry_count",2)+1):
            try:
                with urllib.request.urlopen(req,timeout=180) as res: return response_text(json.load(res))
            except (urllib.error.URLError,TimeoutError,ValueError) as e:
                self.retries.append({"role":role,"attempt":attempt+1,"error":str(e)[:500]})
                if attempt>=CONFIG.get("retry_count",2): raise
                time.sleep(2**attempt)

def retrieve(message, scenario, limit=4):
    q=(message+" "+scenario["title"]+" "+scenario["critical_facts"]).lower()
    catalog=[
      ("knowledge/project/pearlmont/01_facts/overview.md",["pearlmont","project","completion","developer","maintenance","freehold","units"]),
      ("knowledge/project/pearlmont/01_facts/unit-and-layout.md",["900","sqft","layout","room","bedroom","floor","facing","sea view","view","unit","type","balcony"]),
      ("knowledge/project/pearlmont/01_facts/risks-and-sensitive-faq.md",["pylon","cable","flood","river","safety","school","privacy","warranty","risk","smell"]),
      ("knowledge/project/pearlmont/01_facts/location-and-connectivity.md",["location","transport","school","river","flood","parking","traffic","access"]),
      ("knowledge/project/pearlmont/02_commercial/pricing.md",["price","pricing","budget","package","rebate","cost"]),
      ("knowledge/project/pearlmont/02_commercial/sales-package.md",["package","rebate","promotion","price"]),
      ("knowledge/project/pearlmont/02_commercial/financing-and-booking.md",["financ","loan","booking","deposit","approval","downpayment"]),
      ("knowledge/project/pearlmont/02_commercial/lppsa.md",["lppsa","government servant"]),
      ("knowledge/project/pearlmont/02_commercial/panel-financiers-and-legal.md",["financ","legal","eligibility","loan"]),
      ("knowledge/project/pearlmont/03_sales/sales-judgment.md",["invest","yield","appreciation","budget","density","priority","just looking"]),
      ("knowledge/project/pearlmont/03_sales/viewing-close.md",["view","appointment","weekend","visit","high intent"]),
      ("knowledge/project/pearlmont/03_sales/unit-fit.md",["unit","floor","facing","carpark","bedroom","view","budget"]),
      ("knowledge/project/pearlmont/03_sales/objection-to-usp-map.md",["concern","objection","small","pylon","flood","density","river"]),
      ("knowledge/project/pearlmont/03_sales/selling-angles.md",["family","invest","location","value","own stay"]),
      ("knowledge/project/pearlmont/03_sales/buyer-profiles.md",["buyer","family","first-home","invest"]),
    ]
    ranked=[]
    for order,(path,terms) in enumerate(catalog):
        score=sum(2 if term in q else 0 for term in terms)
        if score: ranked.append((-score,order,path))
    # Stage-appropriate minimal context; cap at four and never send the whole KB.
    paths=[x[2] for x in sorted(ranked)[:limit]]
    return [{"path":p,"content":(ROOT/p).read_text()} for p in paths]

def brain_context():
    paths=["brain/AGENT.md","brain/SALES_FLOW.md","brain/INTENT_MODEL.md","brain/LEAD_PROFILE.md","brain/RESPONSE_RULES.md","brain/HANDOFF_RULES.md","skills/decide-next-action.md","skills/retrieve-project-knowledge.md","skills/update-lead-profile.md","skills/handoff-to-human.md"]
    return "\n\n".join(f"--- {p} ---\n{(ROOT/p).read_text()}" for p in paths)

def initial_report(scenario, transcript, traces, actions, provider, error=None):
    agent_system=("You are the Pearlmont WhatsApp sales agent. Follow this accepted Brain/Skills context.\n\n"+brain_context()+"\n\nUse retrieved factual knowledge as the source of truth. Never invent availability, current price/package, financing approval, yields, appreciation, legal eligibility, travel time, safety guarantees or completion promises. Never expose internal-only notes. Respond naturally and briefly in WhatsApp style, answer latest question first, usually one useful question at most. Use one primary action from "+ACTION+". Return only JSON: {\"action\":\"...\",\"message\":\"...\",\"lead_context\":{...}}. The hidden scenario is not available to you.")
    customer_system=(SIM/"prompts/customer-simulator.md").read_text()
    judge_system=(SIM/"prompts/judge.md").read_text()
    return agent_system,customer_system,judge_system

def run_scenario(path, provider, outdir, dry=False):
    s=json.loads(path.read_text()); started=dt.datetime.now(dt.timezone.utc).isoformat()
    transcript=[{"turn":0,"speaker":"customer","message":s["starting_message"]}]; traces=[]; actions=[]; retries_before=len(provider.retries)
    agent_sys,customer_sys,judge_sys=initial_report(s,transcript,traces,actions,provider)
    buyer_state="unknown"; final_intent=s["buyer"].get("initial_intent","unknown"); status="COMPLETED"; error=None; terminal_customer_message=False
    max_turns=min(CONFIG.get("max_customer_turns",12),s["conversion"]["reasonable_max_turn_limit"],15)
    for turn in range(1,max_turns+1):
        latest=transcript[-1]["message"]
        retrieved=retrieve(latest,s)
        traces.append({"turn":turn,"trigger_message":latest,"files":[x["path"] for x in retrieved]})
        lead={"known_facts":buyer_state,"latest_customer_intent":final_intent,"stage":"turn "+str(turn)}
        user=json.dumps({"lead_context":lead,"history":transcript,"retrieved_project_knowledge":retrieved},ensure_ascii=False)
        try:
            raw=provider.ask("sales_agent",agent_sys,user); ans=extract_json(raw)
            msg=str(ans.get("message",raw)).strip(); act=str(ans.get("action","ACKNOWLEDGE / MAINTAIN")); buyer_state=ans.get("lead_context",buyer_state)
            actions.append({"turn":turn,"action":act})
            transcript.append({"turn":turn,"speaker":"agent","message":msg,"action":act})
            # Customer `done` means no further buyer turn after this Agent reply.
            if terminal_customer_message or turn>=max_turns: break
            cust_input=json.dumps({"scenario":s,"transcript":transcript,"turn":turn,"max_turns":max_turns,"previous_appointment_state":buyer_state},ensure_ascii=False)
            cr=extract_json(provider.ask("customer_simulator",customer_sys,cust_input))
            cmsg=str(cr.get("message","")).strip()
            transcript.append({"turn":turn,"speaker":"customer","message":cmsg,"appointment_state":cr.get("appointment_state")})
            buyer_state=normalize_appointment_state(cr.get("appointment_state",buyer_state)); final_intent=cr.get("final_intent",final_intent)
            terminal_customer_message=bool(cr.get("done")) or turn==max_turns
        except Exception as e:
            status="RUN_FAILED"; error=f"{type(e).__name__}: {e}"; break
    trace={"scenario_id":s["scenario_id"],"model_config":CONFIG["models"],"attempted_at_utc":started,"status":status,"turns":len(actions),"transcript":transcript,"agent_actions":actions,"retrieval_trace":traces,"retries":provider.retries[retries_before:],"error":error}
    (outdir/f"{s['scenario_id']}.transcript.json").write_text(json.dumps(trace,indent=2,ensure_ascii=False)+"\n")
    judge=None
    if status=="COMPLETED":
        try:
            source_paths=sorted({p for t in traces for p in t["files"]})
            source_material=[{"path":p,"content":(ROOT/p).read_text()} for p in source_paths]
            jinput=json.dumps({"scenario":s,"transcript":transcript,"final_lead_state":buyer_state,"retrieval_trace":traces,"agent_actions":actions,"retrieved_source_material":source_material},ensure_ascii=False)
            judge=extract_json(provider.ask("judge",judge_sys,jinput))
        except Exception as e:
            status="RUN_FAILED"; error=f"Judge {type(e).__name__}: {e}"
    trace["retries"]=provider.retries[retries_before:]
    (outdir/f"{s['scenario_id']}.transcript.json").write_text(json.dumps(trace,indent=2,ensure_ascii=False)+"\n")
    state=normalize_appointment_state((judge or {}).get("appointment_state",buyer_state))
    flags=(judge or {}).get("critical_flags",[])
    if state=="APPOINTMENT_CONFIRMED": outcome="CONFIRMED_APPOINTMENT"
    elif state in ("VIEWING_SUGGESTED","VIEWING_INTEREST","APPOINTMENT_IN_PROGRESS"): outcome="APPOINTMENT_INTEREST"
    elif not s["conversion"]["convertible"] and (judge or {}).get("good_judgment"): outcome="BAD_FIT_CORRECTLY_IDENTIFIED"
    elif flags: outcome="CRITICAL_FAILURE"
    elif (judge or {}).get("good_judgment"): outcome="NO_APPOINTMENT_BUT_GOOD_JUDGMENT"
    else: outcome="LOST_CONVERSION"
    report={"scenario_id":s["scenario_id"],"title":s["title"],"convertible":s["conversion"]["convertible"],"status":status,"transcript_file":f"{s['scenario_id']}.transcript.json","transcript":transcript,"agent_actions":actions,"retrieval_trace":traces,"appointment_state":state,"appointment_outcome":outcome,"final_lead_intent":(judge or {}).get("final_lead_intent",final_intent),"judge":judge,"error":error}
    (outdir/f"{s['scenario_id']}.report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    (outdir/f"{s['scenario_id']}.report.md").write_text(render_scenario(report,s))
    return report

def render_scenario(r,s):
    j=r.get("judge") or {}; scores=j.get("scores",{})
    lines=[f"# {r['scenario_id']} — {r['title']}","",f"- Buyer type / hidden situation: {s['buyer']['hidden_profile']}",f"- Convertible: {'YES' if r['convertible'] else 'NO'}",f"- Run: {r['status']}",f"- Appointment state: {r['appointment_state']}",f"- Scenario success: {j.get('scenario_success','not judged')}",f"- Final intent: {r['final_lead_intent']}","", "## Key scores", ""]
    lines += [f"- {k.replace('_',' ').title()}: {v}/5" for k,v in scores.items()]
    lines += ["", "## Critical flags", "", json.dumps(j.get("critical_flags",[]),ensure_ascii=False),"", "## Conversation summary", "",str(j.get("summary",r.get("error") or "")),"", "## What the Agent did well", ""]
    lines += [f"- {x}" for x in j.get("what_agent_did_well",[])] or ["- No judge findings."]
    lines += ["", "## Where conversion was lost or weakened", "", json.dumps(j.get("conversion_analysis",{}),ensure_ascii=False,indent=2),"", "## Better next move", "", str(j.get("better_next_move","")),"", "## Close timing", "", str(j.get("close_timing","")),"", "## Retrieval assessment", "", json.dumps(j.get("retrieval_misses",[]),ensure_ascii=False),"", "Retrieved: "+", ".join(sorted({p for t in r['retrieval_trace'] for p in t['files']})),"", "## Suggested improvement", "", json.dumps(j.get("recommended_improvement",{}),ensure_ascii=False,indent=2),"", "## Transcript", ""]
    for m in r["transcript"]: lines.append(f"**{m['speaker'].title()} ({m['turn']}):** {m['message']}"+(f" _[{m['action']}]_" if m.get('action') else ""))
    return "\n".join(lines)+"\n"

def aggregate(reports, outdir, provider, hashes_before):
    done=[r for r in reports if r["status"]=="COMPLETED"]; judged=[r for r in done if r.get("judge")]
    convertible=[r for r in judged if r["convertible"]]; nonconv=[r for r in judged if not r["convertible"]]
    scores={k:round(sum(float(r["judge"].get("scores",{}).get(k,0)) for r in judged)/len(judged),2) if judged else None for k in DIMENSIONS}
    flags=[f for r in judged for f in r["judge"].get("critical_flags",[])]
    appt=lambda r: r.get("appointment_state") in ("APPOINTMENT_CONFIRMED","CONFIRMED_APPOINTMENT")
    interest=lambda r: r.get("appointment_state") in ("VIEWING_INTEREST","APPOINTMENT_IN_PROGRESS","APPOINTMENT_INTEREST","VIEWING_SUGGESTED")
    confirmed=sum(appt(r) for r in convertible); interested=sum(interest(r) for r in convertible)
    outcome_counts={}
    for r in judged:
        outcome=r.get("appointment_outcome","LOST_CONVERSION")
        outcome_counts[outcome]=outcome_counts.get(outcome,0)+1
    good=sum(bool(r["judge"].get("good_judgment")) for r in judged)
    categories={}
    for r in judged:
        for x in r["judge"].get("likely_issue_sources",[]): categories[x]=categories.get(x,0)+1
    findings={k:[] for k in ["weakest_behaviors","unnecessary_qualification","missed_buying_signals","premature_close_cases","delayed_close_cases","unsupported_factual_claims","retrieval_misses","handoff_errors","unit_fit_mistakes"]}
    fields={"weakest_behaviors":"weak_or_wrong_sales_move","unnecessary_qualification":"unnecessary_qualification","missed_buying_signals":"missed_buying_signals","unsupported_factual_claims":"unsupported_factual_claims","retrieval_misses":"retrieval_misses"}
    for r in judged:
        j=r["judge"]
        for dest,src in fields.items():
            v=j.get(src,[]); findings[dest].extend([f"{r['scenario_id']}: {x}" for x in (v if isinstance(v,list) else [v]) if x])
        if j.get("close_timing")=="too_early": findings["premature_close_cases"].append(r["scenario_id"])
        if j.get("close_timing")=="too_late": findings["delayed_close_cases"].append(r["scenario_id"])
        fs=[str(x.get("flag","")) for x in j.get("critical_flags",[])]
        if any("HANDOFF" in f for f in fs): findings["handoff_errors"].append(r["scenario_id"])
        if any("UNIT_FIT" in f for f in fs): findings["unit_fit_mistakes"].append(r["scenario_id"])
    obj={"run_id":outdir.name,"models":CONFIG["models"],"total_scenarios":len(reports),"completed_scenarios":len(done),"failed_runs":[r["scenario_id"] for r in reports if r["status"]!="COMPLETED"],"genuinely_convertible_scenarios":len(convertible),"confirmed_appointments":confirmed,"appointment_interest_cases":interested,"appointment_outcome_counts":outcome_counts,"appointment_conversion_rate_among_convertible":round(confirmed/len(convertible),3) if convertible else None,"good_judgment_rate":round(good/len(judged),3) if judged else None,"bad_fit_correctly_identified_count":sum(bool(r["judge"].get("good_judgment")) and not appt(r) for r in nonconv),"critical_failure_count":len(flags),"critical_failures":flags,"average_judge_scores":scores,"strongest_agent_behaviors":sorted(((k,v) for k,v in scores.items()),key=lambda x:x[1] or 0,reverse=True)[:3],"weakest_agent_behaviors":sorted(((k,v) for k,v in scores.items()),key=lambda x:x[1] or 0)[:3],"common_failure_patterns":categories,**findings,"implementation_bugs_fixed":[],"reruns_required":[],"provider_calls":provider.calls,"provider_retries":provider.retries,"brain_knowledge_unchanged":hashes_before=={"brain":digest_tree(ROOT/"brain"),"knowledge":digest_tree(ROOT/"knowledge")}}
    obj["top_recommended_improvement_priorities"]=[]
    for r in judged:
        rec=r["judge"].get("recommended_improvement",{}); reason=rec.get("reason")
        if reason: obj["top_recommended_improvement_priorities"].append({"scenario_id":r["scenario_id"],**rec})
    obj["executive_summary"]=(f"Completed {len(done)}/{len(reports)} scenarios; confirmed {confirmed} appointments among {len(convertible)} convertible scenarios ({obj['appointment_conversion_rate_among_convertible'] if convertible else 'n/a'}). Good judgment {obj['good_judgment_rate'] if judged else 'n/a'}; critical flags {len(flags)}. Review scenario reports for buyer-fit and accuracy findings.")
    (outdir/"aggregate.json").write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")
    lines=["# Simulator V1 Aggregate Report","",f"**Executive summary:** {obj['executive_summary']}","", "## Run totals", "", "| Metric | Result |","|---|---:|",f"| Scenarios attempted | {obj['total_scenarios']} |",f"| Completed | {obj['completed_scenarios']} |",f"| Failed | {len(obj['failed_runs'])} |",f"| Convertible | {obj['genuinely_convertible_scenarios']} |",f"| Confirmed appointments | {confirmed} |",f"| Appointment interest cases | {interested} |",f"| Conversion / convertible | {obj['appointment_conversion_rate_among_convertible']} |",f"| Good judgment rate | {obj['good_judgment_rate']} |",f"| Good fit rejections | {obj['bad_fit_correctly_identified_count']} |",f"| Critical flags | {len(flags)} |","", "## Appointment outcome classifications", "", json.dumps(outcome_counts,ensure_ascii=False),"", "## Average Judge scores", ""]
    lines += [f"- {k}: {v}/5" for k,v in scores.items()]
    lines += ["", "## Findings", ""]
    for k,v in findings.items(): lines += [f"### {k.replace('_',' ').title()}",""]+[f"- {x}" for x in v] or ["- None recorded."]
    lines += ["", "## Top priorities", "",json.dumps(obj["top_recommended_improvement_priorities"],ensure_ascii=False,indent=2),"", "## Critical failures", "",json.dumps(flags,ensure_ascii=False,indent=2),"", "## Run integrity", "",f"- Brain/Knowledge unchanged: {obj['brain_knowledge_unchanged']}",f"- Model config: `{json.dumps(CONFIG['models'])}`", f"- Calls: {provider.calls}; retries: {len(provider.retries)}",""]
    (outdir/"aggregate.md").write_text("\n".join(lines))
    return obj

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--dry-run",action="store_true",help="exercise the full operator path with a fake provider transport"); ap.add_argument("--scenario",action="append",help="scenario ID; default runs all"); ap.add_argument("--output",help="existing output directory name")
    args=ap.parse_args(); stamp=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"); outdir=SIM/"reports"/(args.output or (("DRYRUN-" if args.dry_run else "RUN-")+stamp)); outdir.mkdir(parents=True,exist_ok=False)
    before={"brain":digest_tree(ROOT/"brain"),"knowledge":digest_tree(ROOT/"knowledge")}
    files=sorted((SIM/"scenarios/pearlmont").glob("PEA-*.json")); selected=set(args.scenario or [])
    if selected: files=[p for p in files if p.stem in selected]
    if not files: raise SystemExit("No scenarios selected")
    provider=Provider(args.dry_run); reports=[]
    for p in files:
        print(f"[{p.stem}] starting",flush=True)
        r=run_scenario(p,provider,outdir,args.dry_run); reports.append(r)
        print(f"[{p.stem}] {r['status']} turns={len(r['agent_actions'])}",flush=True)
    obj=aggregate(reports,outdir,provider,before)
    print(json.dumps({"report_dir":str(outdir),"total":obj['total_scenarios'],"completed":obj['completed_scenarios'],"failed":obj['failed_runs'],"critical_failures":obj['critical_failure_count']},indent=2))
    if args.dry_run and (obj["completed_scenarios"]!=obj["total_scenarios"] or not obj["brain_knowledge_unchanged"]): return 2
    return 1 if obj["failed_runs"] else 0

if __name__=="__main__": sys.exit(main())
