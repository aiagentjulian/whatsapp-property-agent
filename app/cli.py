import argparse
import json
import os
import sys
from pathlib import Path

from .config import ROOT, get_config
from .db import Store
from .knowledge import retrieve
from .service import Runtime
from .whatsapp import WhatsAppWeb


def output(value):
    print(json.dumps(value, ensure_ascii=False, indent=2, default=str))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("login")
    start = sub.add_parser("start")
    start.add_argument("--send-replies", action="store_true", help="explicitly authorize automated replies during this run")
    sub.add_parser("stop")
    sub.add_parser("leads")
    lead = sub.add_parser("lead"); lead.add_argument("lead_id")
    history = sub.add_parser("history"); history.add_argument("lead_id")
    sub.add_parser("support")
    resolve = sub.add_parser("resolve-support"); resolve.add_argument("request_id"); resolve.add_argument("--result", required=True)
    sub.add_parser("handoffs")
    sub.add_parser("usage")
    knowledge = sub.add_parser("knowledge-check"); knowledge.add_argument("query")
    args = parser.parse_args(argv)
    config = get_config()
    store = Store(config["database"])
    if args.command == "status":
        profile = config["profile_dir"] if config["profile_dir"].is_absolute() else ROOT / config["profile_dir"]
        pid_file = ROOT / "data/lead/runtime.pid"
        output({"provider": config["provider"], "model": config["model"], "reasoning": config["reasoning"],
                "api_key_configured": bool(config["api_key"]), "allowlisted_contacts": len(config["allowlist"]),
                "database_exists": store.path.exists(), "browser_profile_exists": profile.exists(),
                "runtime_pid": pid_file.read_text().strip() if pid_file.exists() else None})
    elif args.command == "login":
        WhatsAppWeb(config, Runtime(config, store=store)).login()
    elif args.command == "start":
        pid_file = ROOT / "data/lead/runtime.pid"
        stop_file = ROOT / "data/lead/runtime.stop"
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        if pid_file.exists():
            raise SystemExit("Runtime already has a PID file; inspect status and stop it before starting.")
        pid_file.write_text(str(os.getpid()))
        stop_file.unlink(missing_ok=True)
        try:
            WhatsAppWeb(config, Runtime(config, store=store)).run(args.send_replies, stop_file)
        finally:
            pid_file.unlink(missing_ok=True)
            stop_file.unlink(missing_ok=True)
    elif args.command == "stop":
        stop_file = ROOT / "data/lead/runtime.stop"
        pid_file = ROOT / "data/lead/runtime.pid"
        if not pid_file.exists():
            print("Runtime is not running.")
        else:
            stop_file.write_text("stop")
            print("Stop requested.")
    elif args.command == "leads":
        output([{key: row[key] for key in ("lead_id", "phone", "lead_source", "owner", "ai_session_status", "updated_at")} for row in store.leads()])
    elif args.command == "lead":
        output(store.get(args.lead_id) or {"error": "Lead not found"})
    elif args.command == "history":
        output(store.history(args.lead_id))
    elif args.command == "support":
        output(store.pending_support())
    elif args.command == "resolve-support":
        output(store.resolve_support(args.request_id, args.result))
    elif args.command == "handoffs":
        output(store.handoffs())
    elif args.command == "usage":
        output(store.usage())
    elif args.command == "knowledge-check":
        output(retrieve(args.query))
    return 0


if __name__ == "__main__":
    sys.exit(main())
