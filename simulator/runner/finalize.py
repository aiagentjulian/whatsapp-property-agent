#!/usr/bin/env python3
"""Merge a successful single-scenario retry into a full run and rebuild reports."""
import argparse, json, shutil, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_v1 as sim

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--run",required=True,help="full-run directory name under simulator/reports"); ap.add_argument("--retry",required=True,help="single-scenario retry directory name under simulator/reports")
    args=ap.parse_args(); target=sim.SIM/"reports"/args.run; retry=sim.SIM/"reports"/args.retry
    if not target.is_dir() or not retry.is_dir(): raise SystemExit("run/retry directory not found")
    before=json.loads((target/"aggregate.json").read_text()); retry_aggregate=json.loads((retry/"aggregate.json").read_text())
    retry_reports=list(retry.glob("PEA-*.report.json"))
    if len(retry_reports)!=1 or retry_aggregate.get("completed_scenarios")!=1 or retry_aggregate.get("failed_runs"):
        raise SystemExit("retry directory must contain exactly one successfully judged scenario")
    sid=retry_reports[0].name.removesuffix(".report.json")
    for suffix in ("transcript.json","report.json","report.md"):
        shutil.copy2(retry/f"{sid}.{suffix}",target/f"{sid}.{suffix}")
    reports=[]
    for p in sorted(target.glob("PEA-*.report.json")):
        r=json.loads(p.read_text()); r["appointment_state"]=sim.normalize_appointment_state(r.get("appointment_state")); j=r.get("judge") or {}; j["appointment_state"]=r["appointment_state"]
        if r["appointment_state"]=="APPOINTMENT_CONFIRMED": outcome="CONFIRMED_APPOINTMENT"
        elif r["appointment_state"] in ("VIEWING_SUGGESTED","VIEWING_INTEREST","APPOINTMENT_IN_PROGRESS"): outcome="APPOINTMENT_INTEREST"
        elif not r["convertible"] and j.get("good_judgment"): outcome="BAD_FIT_CORRECTLY_IDENTIFIED"
        elif j.get("critical_flags"): outcome="CRITICAL_FAILURE"
        elif j.get("good_judgment"): outcome="NO_APPOINTMENT_BUT_GOOD_JUDGMENT"
        else: outcome="LOST_CONVERSION"
        r["appointment_outcome"]=outcome
        p.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
        scenario=json.loads((sim.SIM/"scenarios/pearlmont"/f"{r['scenario_id']}.json").read_text())
        (target/f"{r['scenario_id']}.report.md").write_text(sim.render_scenario(r,scenario))
        reports.append(r)
    provider=sim.Provider(dry=True); provider.calls=before.get("provider_calls",0)+retry_aggregate.get("provider_calls",0); provider.retries=before.get("provider_retries",[])+retry_aggregate.get("provider_retries",[])
    current={"brain":sim.digest_tree(ROOT/"brain"),"knowledge":sim.digest_tree(ROOT/"knowledge")}
    result=sim.aggregate(reports,target,provider,current)
    result["implementation_bugs_fixed"]=["The Agent now responds after the Customer Simulator marks a buyer message terminal.","Judge appointment labels are normalized to the five spec states.","JSON extraction accepts trailing text after the first valid JSON object."]
    result["reruns_required"]=["All 12 scenarios rerun after terminal-turn handling changed.",f"PEA-009 retried after its first rerun returned valid JSON followed by trailing text; successful retry merged from {retry.name}."]
    result["source_runs"]={"full_rerun":args.run,"scenario_retry":args.retry,"superseded_first_pass":"RUN-20261007T005135Z"}
    result["executive_summary"]=(f"Completed {result['completed_scenarios']}/{result['total_scenarios']} scenarios; confirmed {result['confirmed_appointments']} appointments among {result['genuinely_convertible_scenarios']} convertible scenarios ({result['appointment_conversion_rate_among_convertible']}). Good judgment {result['good_judgment_rate']}; critical flags {result['critical_failure_count']}. All scenario transcripts and Judge reports are present.")
    (target/"aggregate.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    md=(target/"aggregate.md").read_text()
    md=md.replace("## Run totals", "## Rerun notes\n\n"+"\n".join("- "+x for x in result["reruns_required"])+"\n\nSource runs: `"+args.run+"`, retry `"+args.retry+"`; superseded pass `RUN-20261007T005135Z`.\n\n## Run totals",1)
    (target/"aggregate.md").write_text(md)
    print(json.dumps({"report_dir":str(target),"attempted":result["total_scenarios"],"completed":result["completed_scenarios"],"failed":result["failed_runs"],"appointment_conversion_rate_among_convertible":result["appointment_conversion_rate_among_convertible"],"critical_failures":result["critical_failure_count"]},indent=2))

if __name__=="__main__": main()
