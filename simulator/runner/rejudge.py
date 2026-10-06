#!/usr/bin/env python3
"""Rescore saved transcripts with retrieved source text available to the Judge."""
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run as sim

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--run",required=True,help="report directory name under simulator/reports"); args=ap.parse_args()
    out=sim.SIM/"reports"/args.run
    if not out.is_dir(): raise SystemExit("run directory not found")
    old=json.loads((out/"aggregate.json").read_text()); judge_system=(sim.SIM/"prompts/judge.md").read_text()
    reports=sorted(out.glob("PEA-*.report.json")); provider=sim.Provider(); scenario_dir=sim.SIM/"scenarios/pearlmont"
    for rp in reports:
        report=json.loads(rp.read_text())
        if report.get("status")!="COMPLETED": continue
        scenario=json.loads((scenario_dir/f"{report['scenario_id']}.json").read_text())
        paths=sorted({p for t in report.get("retrieval_trace",[]) for p in t.get("files",[])})
        sources=[{"path":p,"content":(ROOT/p).read_text()} for p in paths if (ROOT/p).is_file()]
        user=json.dumps({"scenario":scenario,"transcript":report["transcript"],"final_lead_state":report.get("final_lead_intent"),"retrieval_trace":report.get("retrieval_trace"),"agent_actions":report.get("agent_actions"),"retrieved_source_material":sources},ensure_ascii=False)
        raw=provider.ask("judge",judge_system,user); judge=sim.extract_json(raw)
        judge["appointment_state"]=sim.normalize_appointment_state(judge.get("appointment_state"))
        report.setdefault("judge_history",[]).append(report.get("judge"))
        report["judge"]=judge; state=judge["appointment_state"]; report["appointment_state"]=state
        flags=judge.get("critical_flags",[])
        if state=="APPOINTMENT_CONFIRMED": outcome="CONFIRMED_APPOINTMENT"
        elif state in ("VIEWING_SUGGESTED","VIEWING_INTEREST","APPOINTMENT_IN_PROGRESS"): outcome="APPOINTMENT_INTEREST"
        elif not report["convertible"] and judge.get("good_judgment"): outcome="BAD_FIT_CORRECTLY_IDENTIFIED"
        elif flags: outcome="CRITICAL_FAILURE"
        elif judge.get("good_judgment"): outcome="NO_APPOINTMENT_BUT_GOOD_JUDGMENT"
        else: outcome="LOST_CONVERSION"
        report["appointment_outcome"]=outcome
        rp.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
        (out/f"{report['scenario_id']}.report.md").write_text(sim.render_scenario(report,scenario))
        print(f"[{report['scenario_id']}] judged with {len(sources)} source files",flush=True)
    provider.calls+=int(old.get("provider_calls",0)); provider.retries=old.get("provider_retries",[])+provider.retries
    complete=[json.loads(p.read_text()) for p in sorted(out.glob("PEA-*.report.json"))]
    current={"brain":sim.digest_tree(ROOT/"brain"),"knowledge":sim.digest_tree(ROOT/"knowledge")}
    result=sim.aggregate(complete,out,provider,current)
    result["implementation_bugs_fixed"]=old.get("implementation_bugs_fixed",[])+["Judge now receives the actual retrieved Knowledge source text for factual scoring."]
    result["reruns_required"]=old.get("reruns_required",[])+["Judge rescored all saved transcripts with source-grounded factual evaluation; Agent and Customer turns were not rerun."]
    result["source_runs"]=old.get("source_runs",{})
    result["executive_summary"]=(f"Completed {result['completed_scenarios']}/{result['total_scenarios']} scenarios; confirmed {result['confirmed_appointments']} appointments among {result['genuinely_convertible_scenarios']} convertible scenarios ({result['appointment_conversion_rate_among_convertible']}). Good judgment {result['good_judgment_rate']}; critical flags {result['critical_failure_count']}. Judge scores use the source material retrieved for each conversation.")
    (out/"aggregate.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    md=(out/"aggregate.md").read_text(); md=md.replace("## Rerun notes", "**Executive summary:** "+result["executive_summary"]+"\n\n## Rerun notes",1)
    md += "\nJudge rescore: actual retrieved Knowledge source text was supplied for factual evaluation; no Agent or Customer turns were rerun.\n"
    (out/"aggregate.md").write_text(md)
    print(json.dumps({"completed":result["completed_scenarios"],"failed":result["failed_runs"],"critical_flags":result["critical_failure_count"],"provider_calls":provider.calls},indent=2))

if __name__=="__main__": main()
