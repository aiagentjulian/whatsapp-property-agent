#!/usr/bin/env python3
"""Small multi-role Pearlmont simulator. Uses only stdlib plus OpenAI Responses API."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, re, subprocess, sys, tempfile, time, urllib.error, urllib.request
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

from provider_schemas import JUDGE_SCHEMA_REQUIRED, LEAD_CONTEXT_FIELDS, ROLE_SCHEMAS

class ProviderError(RuntimeError):
    def __init__(self,kind,message):
        super().__init__(message); self.kind=kind

def validate_schema(value,schema,path="$",errors=None):
    errors=[] if errors is None else errors
    if "anyOf" in schema:
        if not any(not validate_schema(value,variant,path,[]) for variant in schema["anyOf"]): errors.append(f"{path}: no anyOf schema matched")
        return errors
    expected=schema.get("type")
    matches={"object":lambda x:isinstance(x,dict),"array":lambda x:isinstance(x,list),"string":lambda x:isinstance(x,str),"boolean":lambda x:isinstance(x,bool),"integer":lambda x:isinstance(x,int) and not isinstance(x,bool),"number":lambda x:isinstance(x,(int,float)) and not isinstance(x,bool),"null":lambda x:x is None}
    expected_types=expected if isinstance(expected,list) else [expected] if expected else []
    if expected_types and not any(matches[t](value) for t in expected_types):
        errors.append(f"{path}: expected {' or '.join(expected_types)}")
        return errors
    if "enum" in schema and value not in schema["enum"]: errors.append(f"{path}: value is outside the allowed enum")
    if isinstance(value,dict):
        for key in schema.get("required",[]):
            if key not in value: errors.append(f"{path}: missing required field {key}")
        props=schema.get("properties",{})
        for key,item in value.items():
            if key in props: validate_schema(item,props[key],f"{path}.{key}",errors)
            elif schema.get("additionalProperties") is False: errors.append(f"{path}: unexpected field {key}")
    if isinstance(value,list) and "items" in schema:
        for index,item in enumerate(value): validate_schema(item,schema["items"],f"{path}[{index}]",errors)
    if isinstance(value,int) and not isinstance(value,bool):
        if "minimum" in schema and value<schema["minimum"]: errors.append(f"{path}: below minimum")
        if "maximum" in schema and value>schema["maximum"]: errors.append(f"{path}: above maximum")
    return errors

def redact_error(text):
    cleaned=re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._-]+",r"\1[redacted]",str(text))
    return cleaned[-1600:]

def classify_failure(text,default="CLI_EXIT"):
    low=str(text).lower()
    if "unexpected argument" in low or "usage: codex exec" in low: return "CLI_CONFIGURATION"
    if any(x in low for x in ("usage limit", "usage exhausted", "usage_limit_reached", "quota exceeded", "current quota", "insufficient_quota", "billing hard limit", "credits exhausted", "out of credits")): return "USAGE_EXHAUSTED"
    if any(x in low for x in ("rate limit", "rate_limit_exceeded", "too many requests", "status 429", "http 429")): return "RATE_LIMIT"
    if any(x in low for x in ("not supported when using codex", "model not found", "unknown model", "unsupported model")): return "MODEL_UNAVAILABLE"
    if any(x in low for x in ("unauthorized", "authentication failed", "invalid api key", "token expired", "status 401", "http 401")): return "AUTHENTICATION"
    if any(x in low for x in ("schema", "structured output", "json schema")): return "SCHEMA_FAILURE"
    return default

class Provider:
    def __init__(self,dry=False):
        self.dry=dry; self.name=CONFIG.get("provider","codex_cli"); self.calls=0; self.logical_requests=0; self.retries=[]; self.call_records=[]; self.calls_by_role={}; self.blocking_error=None; self.scenario_id=None
        if self.name not in ("codex_cli","openai_api"): raise ProviderError("CONFIGURATION",f"unsupported simulator provider: {self.name}")
        self.settings=CONFIG.get("provider_settings",{}).get(self.name,{})

    def schema(self,role):
        if role not in ROLE_SCHEMAS: raise ProviderError("CONFIGURATION",f"unsupported simulator role: {role}")
        return ROLE_SCHEMAS[role]

    def snapshot(self): return {"calls":len(self.call_records),"retries":len(self.retries),"logical_requests":self.logical_requests}

    def usage_summary(self,records):
        keys=("input_tokens","output_tokens","cached_tokens","total_tokens")
        available=[r.get("usage") for r in records if r.get("usage")]
        exact={k:sum(int(u[k]) for u in available if isinstance(u.get(k),int)) if any(isinstance(u.get(k),int) for u in available) else None for k in keys}
        exact["reported_call_count"]=len(available); exact["total_model_call_count"]=len(records)
        exact["complete_for_all_calls"]=bool(records) and len(available)==len(records) and all(isinstance(u.get("input_tokens"),int) and isinstance(u.get("output_tokens"),int) for u in available)
        if exact["complete_for_all_calls"]: exact["total_tokens"]=exact["input_tokens"]+exact["output_tokens"]
        else: exact["total_tokens"]=None
        return exact

    def metrics_since(self,snapshot,duration_seconds=None):
        records=self.call_records[snapshot["calls"]:]; retries=self.retries[snapshot["retries"]:]; roles={}
        for record in records: roles[record["role"]]=roles.get(record["role"],0)+1
        result={"provider":self.name,"model_config":CONFIG["models"],"number_of_model_calls":len(records),"logical_requests":self.logical_requests-snapshot["logical_requests"],"calls_by_role":roles,"retry_count":len(retries),"retries":retries,"usage":self.usage_summary(records)}
        if duration_seconds is not None: result["scenario_duration_seconds"]=round(duration_seconds,3)
        return result

    def _fake_response(self,role,system,user):
        if role=="sales_agent": return json.dumps({"action":"ANSWER","message":"Thanks for asking. I can help check the current details for you.","support_request":None,"support_context":None,"lead_context":{},"assessment":{"appointment_readiness":"NOT_READY","handoff_state":"NO_HANDOFF","handoff_reason":None}})
        if role=="customer_simulator": return json.dumps({"message":"Okay, thanks.","done":True,"appointment_state":"NO_VIEWING_INTENT","final_intent":"low"})
        if role=="human_handoff_executor": return json.dumps({"message":"I’ll check the available simulator fixture and confirm what it establishes.","operational_action":"NO_ACTION","sales_work_level":"LOW","operational_task_completed":False,"appointment_state":"NO_VIEWING_INTENT"})
        return json.dumps({"appointment_state":"NO_VIEWING_INTENT","appointment_readiness_final":"NOT_READY","ready_for_appointment":False,"first_ready_turn":None,"readiness_detection_correct":True,"readiness_state_at_handoff":"NOT_READY","handoff_timing":"NOT_NEEDED","sales_work_remaining_at_handoff":"NONE","ai_outcome":"AI_PROGRESS_BUT_NOT_READY","support_resume_success_count":0,"support_results_used":False,"support_result_only_relayed":False,"failed_to_resume_selling":False,"appointment_ready_after_support":False,"support_failure_modes":[],"critical_flags":[],"summary":"transport smoke test","scores":{k:3 for k in ROLE_SCHEMAS["judge"]["properties"]["scores"]["required"]}})

    def _schema_default(self,schema):
        if "anyOf" in schema:
            null_branch=next((branch for branch in schema["anyOf"] if branch.get("type")=="null"),None)
            if null_branch: return None
            for branch in schema["anyOf"]:
                if branch.get("type")!="null": return self._schema_default(branch)
            return None
        kind=schema.get("type")
        if kind=="object": return {key:self._schema_default(value) for key,value in schema.get("properties",{}).items()}
        if kind=="array": return []
        if kind=="boolean": return False
        if kind=="integer" or kind=="number": return 0
        if kind=="null": return None
        if kind=="string": return schema.get("enum",[""])[0]
        return None

    def _complete_fake_response(self,role,payload):
        def complete(value,schema):
            if "anyOf" in schema:
                if value is None: return None
                branch=next((item for item in schema["anyOf"] if item.get("type")=="object"),None)
                return complete(value,branch) if branch else value
            if schema.get("type")=="object" and isinstance(value,dict):
                props=schema.get("properties",{})
                for key,child in props.items():
                    if key not in value: value[key]=self._schema_default(child)
                    else: value[key]=complete(value[key],child)
            if schema.get("type")=="array" and isinstance(value,list) and "items" in schema:
                return [complete(item,schema["items"]) for item in value]
            return value
        return complete(payload,self.schema(role))

    def _role_system(self,role,system):
        if role=="sales_agent":
            return system+"\n\nFor lead_context, return the complete Lead Profile object defined by the structured schema. Carry forward known values from the supplied lead context and conversation; use null for unknown fields, and do not infer facts the customer did not state."
        return system

    def _codex_response(self,role,system,user):
        cfg=CONFIG["models"][role]; command=self.settings.get("command","codex"); timeout=float(self.settings.get("timeout_seconds",180)); prompt="You are a JSON-only simulator role. Do not use tools or run commands. Follow the role instructions and input below, then return exactly one JSON object matching the required schema.\n\nROLE INSTRUCTIONS:\n"+self._role_system(role,system)+"\n\nINPUT:\n"+user
        with tempfile.TemporaryDirectory(prefix="pearlmont-codex-cli-") as tmp:
            schema_path=Path(tmp)/"output.schema.json"; output_path=Path(tmp)/"output.json"
            schema_path.write_text(json.dumps(self.schema(role),ensure_ascii=False))
            args=[command,"--ask-for-approval","never","exec","--ephemeral","--model",cfg["model"],"-c",f"model_reasoning_effort={cfg['reasoning']}","--sandbox","read-only","--output-schema",str(schema_path),"--output-last-message",str(output_path),"--json","-"]
            env=os.environ.copy(); env.pop("OPENAI_API_KEY",None)
            try: proc=subprocess.run(args,input=prompt,text=True,capture_output=True,timeout=timeout,cwd=ROOT,env=env)
            except subprocess.TimeoutExpired as e: raise ProviderError("TIMEOUT",f"Codex CLI exceeded {timeout:g}s timeout") from e
            except FileNotFoundError as e: raise ProviderError("CLI_UNAVAILABLE",f"Codex CLI executable not found: {command}") from e
            events=[]
            for line in proc.stdout.splitlines():
                try:
                    event=json.loads(line)
                    if isinstance(event,dict): events.append(event)
                except json.JSONDecodeError: pass
            usage={}
            for event in events:
                if event.get("type")=="turn.completed" and isinstance(event.get("usage"),dict):
                    raw=event["usage"]; usage={"input_tokens":raw.get("input_tokens"),"output_tokens":raw.get("output_tokens"),"cached_tokens":raw.get("cached_input_tokens")}
                    if isinstance(usage.get("input_tokens"),int) and isinstance(usage.get("output_tokens"),int): usage["total_tokens"]=usage["input_tokens"]+usage["output_tokens"]
            if proc.returncode!=0:
                raw_detail=(proc.stderr+"\n"+proc.stdout).strip() or f"Codex CLI exited with status {proc.returncode}"
                raise ProviderError(classify_failure(raw_detail),redact_error(raw_detail))
            if not output_path.is_file(): raise ProviderError("INVALID_JSON","Codex CLI produced no last-message output")
            raw=output_path.read_text().strip()
            try: payload=json.loads(raw)
            except json.JSONDecodeError as e: raise ProviderError("INVALID_JSON",f"Codex CLI output was invalid JSON: {e}") from e
            errors=validate_schema(payload,self.schema(role))
            if errors: raise ProviderError("SCHEMA_FAILURE","Codex CLI output failed schema validation: "+"; ".join(errors))
            return raw,usage

    def _openai_response(self,role,system,user):
        key=os.environ.get("OPENAI_API_KEY")
        if not key: raise ProviderError("AUTHENTICATION","OPENAI_API_KEY is required when provider=openai_api")
        cfg=CONFIG["models"][role]; payload={"model":cfg["model"],"reasoning":{"effort":cfg["reasoning"]},"instructions":self._role_system(role,system),"input":user,"store":False,"text":{"format":{"type":"json_object"}}}
        req=urllib.request.Request("https://api.openai.com/v1/responses",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
        try:
            with urllib.request.urlopen(req,timeout=float(self.settings.get("timeout_seconds",180))) as res: data=json.load(res)
        except urllib.error.HTTPError as e:
            detail=redact_error(e.read().decode("utf-8","replace")); raise ProviderError(classify_failure(f"HTTP {e.code} {detail}","API_ERROR"),f"OpenAI API HTTP {e.code}: {detail}") from e
        except (urllib.error.URLError,TimeoutError) as e: raise ProviderError("TIMEOUT" if isinstance(e,TimeoutError) else "API_ERROR",redact_error(e)) from e
        raw=response_text(data).strip()
        try: payload=json.loads(raw)
        except json.JSONDecodeError as e: raise ProviderError("INVALID_JSON",f"OpenAI API output was invalid JSON: {e}") from e
        errors=validate_schema(payload,self.schema(role))
        if errors: raise ProviderError("SCHEMA_FAILURE","OpenAI API output failed schema validation: "+"; ".join(errors))
        usage=data.get("usage",{}); raw_details=usage.get("input_tokens_details",{})
        counts={"input_tokens":usage.get("input_tokens"),"output_tokens":usage.get("output_tokens"),"cached_tokens":raw_details.get("cached_tokens")}
        if isinstance(counts.get("input_tokens"),int) and isinstance(counts.get("output_tokens"),int): counts["total_tokens"]=counts["input_tokens"]+counts["output_tokens"]
        return raw,counts

    def ask(self,role,system,user):
        if self.blocking_error: raise ProviderError(self.blocking_error["kind"],self.blocking_error["message"])
        self.logical_requests+=1
        retries=int(self.settings.get("retry_count",CONFIG.get("retry_count",1)))
        for attempt in range(retries+1):
            self.calls+=1; self.calls_by_role[role]=self.calls_by_role.get(role,0)+1; started=time.monotonic(); usage=None; error=None
            try:
                raw=self._fake_response(role,system,user) if self.dry else None
                if self.dry:
                    usage=None
                    try: payload=json.loads(raw)
                    except (TypeError,json.JSONDecodeError) as e: raise ProviderError("INVALID_JSON",f"Fake provider output was invalid JSON: {e}") from e
                    payload=self._complete_fake_response(role,payload); raw=json.dumps(payload,ensure_ascii=False)
                    errors=validate_schema(payload,self.schema(role))
                    if errors: raise ProviderError("SCHEMA_FAILURE","Fake provider output failed schema validation: "+"; ".join(errors))
                else:
                    raw,usage=self._codex_response(role,system,user) if self.name=="codex_cli" else self._openai_response(role,system,user)
                self.call_records.append({"role":role,"scenario_id":self.scenario_id,"provider":self.name,"model":CONFIG["models"][role]["model"],"reasoning":CONFIG["models"][role]["reasoning"],"elapsed_seconds":round(time.monotonic()-started,3),"status":"COMPLETED","usage":usage})
                return raw
            except Exception as exc:
                kind=exc.kind if isinstance(exc,ProviderError) else "PROVIDER_ERROR"; error=redact_error(exc)
                self.call_records.append({"role":role,"scenario_id":self.scenario_id,"provider":self.name,"model":CONFIG["models"][role]["model"],"reasoning":CONFIG["models"][role]["reasoning"],"elapsed_seconds":round(time.monotonic()-started,3),"status":"FAILED","error_kind":kind,"usage":usage})
                if kind in ("RATE_LIMIT","USAGE_EXHAUSTED","AUTHENTICATION","MODEL_UNAVAILABLE","CONFIGURATION","CLI_UNAVAILABLE","CLI_CONFIGURATION"):
                    self.blocking_error={"kind":kind,"message":error,"role":role,"scenario_id":self.scenario_id}
                if self.blocking_error or attempt>=retries: raise ProviderError(kind,error) from exc
                retry={"role":role,"scenario_id":self.scenario_id,"attempt":attempt+1,"error_kind":kind,"error":error}; self.retries.append(retry); time.sleep(2**attempt)
        raise ProviderError("PROVIDER_ERROR","provider retries exhausted")

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
