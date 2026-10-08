import argparse
import json
import os
import sys
from pathlib import Path

from .config import ROOT, get_config
from .db import Store
from .knowledge import retrieve
from .service import Runtime
from .sheets import SheetsCRM, authorize, sync_pending
from .whatsapp import WhatsAppWeb, is_allowlisted


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
    sub.add_parser("sheets-auth", help="Authorize local Runtime access to the existing CRM spreadsheet")
    sub.add_parser("sync-sheets", help="Retry pending SQLite CRM synchronization")
    prospects = sub.add_parser("prospects", help="List local Outbound Prospects")
    create = sub.add_parser("create-prospect", help="Create a NOT_SENT Prospect; does not create a Lead or send")
    create.add_argument("phone"); create.add_argument("--name", default=""); create.add_argument("--campaign", default=""); create.add_argument("--source-detail", default="")
    send = sub.add_parser("send-outbound", help="Send one reviewed opening message to one eligible Prospect")
    send.add_argument("prospect_id"); send.add_argument("--message", help="Opening copy; if omitted, use OUTBOUND_OPENING_MESSAGE")
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
        result = store.resolve_support(args.request_id, args.result)
        crm = Runtime(config, store=store).sync_crm()
        output({"support_request": result, "crm_sync": crm})
    elif args.command == "handoffs":
        output(store.handoffs())
    elif args.command == "usage":
        output(store.usage())
    elif args.command == "knowledge-check":
        output(retrieve(args.query))
    elif args.command == "sheets-auth":
        token_path = authorize(config)
        output({"status": "AUTHORIZED", "token_path": str(token_path)})
    elif args.command == "sync-sheets":
        client = SheetsCRM.from_token(config)
        if client is None:
            raise SystemExit("Google Sheets authorization is not ready. Configure the OAuth Desktop client and run sheets-auth.")
        results = sync_pending(store, client)
        output({"status": "SYNCED" if all(item["status"] == "SYNCED" for item in results) else "PENDING", "results": results})
    elif args.command == "prospects":
        output(store.prospects())
    elif args.command == "create-prospect":
        if not is_allowlisted(args.phone, config["outbound_allowlist"]):
            raise SystemExit("Contact must exactly match WHATSAPP_OUTBOUND_ALLOWLIST; no Prospect was created.")
        prospect, created = store.create_prospect(args.phone, args.name, args.campaign, args.source_detail)
        crm = Runtime(config, store=store).sync_crm()
        output({"created": created, "prospect": prospect, "lead_created": False, "message_sent": False, "crm_sync": crm})
    elif args.command == "send-outbound":
        prospect = store.get_prospect(args.prospect_id)
        if not prospect:
            raise SystemExit("Prospect not found.")
        if prospect["outbound_status"] != "NOT_SENT":
            raise SystemExit("Prospect is not eligible for a first send; uncertain sends are never retried automatically.")
        if not is_allowlisted(prospect["phone"], config["outbound_allowlist"]):
            raise SystemExit("Prospect phone is not in WHATSAPP_OUTBOUND_ALLOWLIST.")
        body = (args.message if args.message is not None else config["outbound_opening_message"]).strip()
        if not body:
            raise SystemExit("Set the user-approved OUTBOUND_OPENING_MESSAGE or pass --message for review; nothing was sent.")
        print("Recipient: %s\nOpening message:\n%s" % (prospect["phone"], body))
        if input("Type SEND to authorize this one WhatsApp message: ").strip() != "SEND":
            raise SystemExit("Not sent; operator confirmation did not match.")
        store.mark_prospect_send(args.prospect_id, "SENDING")
        try:
            WhatsAppWeb(config, Runtime(config, store=store)).send_outbound(prospect["phone"], body)
        except Exception as exc:
            store.mark_prospect_send(args.prospect_id, "UNCERTAIN", str(exc))
            raise SystemExit("Send status is uncertain; Prospect is locked against resend and requires operator review: %s" % exc)
        store.mark_prospect_send(args.prospect_id, "SENT")
        crm = Runtime(config, store=store).sync_crm()
        output({"prospect_id": prospect["prospect_id"], "outbound_status": "SENT", "message_sent": True, "crm_sync": crm})
    return 0


if __name__ == "__main__":
    sys.exit(main())
