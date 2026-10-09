import argparse
import json
import sys

from .contacts import is_allowlisted
from .config import get_config
from .db import Store
from .knowledge import retrieve
from .service import Runtime
from .sheets import SheetsCRM, authorize, sync_pending


def output(value):
    print(json.dumps(value, ensure_ascii=False, indent=2, default=str))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
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
    reset = sub.add_parser("reset-test-lead", help="Reset one explicitly configured test contact (stop the Runtime first)")
    reset.add_argument("--phone", required=True)
    reset.add_argument("--confirm-phone", required=True, help="Repeat the exact test phone to authorize the reset")
    sub.add_parser("prospects", help="List local Outbound Prospects")
    create = sub.add_parser("create-prospect", help="Create a NOT_SENT Prospect; does not create a Lead or send")
    create.add_argument("phone"); create.add_argument("--name", default=""); create.add_argument("--campaign", default=""); create.add_argument("--source-detail", default="")
    args = parser.parse_args(argv)
    config = get_config()
    store = Store(config["database"])
    if args.command == "status":
        output({"provider": config["provider"], "model": config["model"], "reasoning": config["reasoning"],
                "api_key_configured": bool(config["api_key"]), "allowlisted_contacts": len(config["allowlist"]),
                "database_exists": store.path.exists()})
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
    elif args.command == "reset-test-lead":
        if args.phone != args.confirm_phone:
            raise SystemExit("Confirmation does not exactly match --phone; nothing was reset.")
        if args.phone not in config["test_contacts"]:
            raise SystemExit("Phone must exactly match WHATSAPP_TEST_CONTACTS; nothing was reset.")
        result = store.reset_test_lead(args.phone, config["test_contacts"])
        lead = store.by_phone(args.phone)
        if lead:
            if store.history(lead["lead_id"]) or store.support_context(lead["lead_id"]):
                raise RuntimeError("Test reset verification failed: conversational records remain")
            result["verified_fresh"] = lead["profile"] == store._initial_profile(lead["lead_id"], args.phone)
        else:
            result["verified_fresh"] = True
        output(result)
    elif args.command == "prospects":
        output(store.prospects())
    elif args.command == "create-prospect":
        if not is_allowlisted(args.phone, config["outbound_allowlist"]):
            raise SystemExit("Contact must exactly match WHATSAPP_OUTBOUND_ALLOWLIST; no Prospect was created.")
        prospect, created = store.create_prospect(args.phone, args.name, args.campaign, args.source_detail)
        crm = Runtime(config, store=store).sync_crm()
        output({"created": created, "prospect": prospect, "lead_created": False, "message_sent": False, "crm_sync": crm})
    return 0


if __name__ == "__main__":
    sys.exit(main())
