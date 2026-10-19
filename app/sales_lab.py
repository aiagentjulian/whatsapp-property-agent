"""One real SalesAgent turn at a time; Codex coordinates customers and judges.

No runtime services, database, Meta or Sheets imports. A failed live attempt
consumes budget and stops the entire experiment. No automatic retries.
"""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

from .agent import SalesAgent
from .config import load_env_file
from .provider import PROFILE_FIELDS

MODEL = 'gpt-6-luna'
LIMIT = 24
SCENARIOS = ('own_stay', 'couple_home_office', 'investment', 'genuine_interest', 'early_exploration', 'holdout')


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def fingerprint():
    root = Path(__file__).resolve().parents[1]
    files = [root / p for p in ('app/agent.py', 'app/knowledge.py', 'app/provider.py', 'app/sales_lab.py', 'brain/AGENT.md')]
    files += sorted((root / 'knowledge').rglob('*.md'))
    return hashlib.sha256(b''.join(p.read_bytes() for p in files)).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--trial', required=True)
    parser.add_argument('--scenario', choices=SCENARIOS, required=True)
    parser.add_argument('--customer', required=True)
    parser.add_argument('--api-limit', type=int, default=None,
                        help='maximum live calls for this new run (default: 24; persisted in ledger)')
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args(argv)
    if not args.trial.replace('-', '').replace('_', '').isalnum():
        parser.error('trial must be a simple label')
    if args.api_limit is not None and not 1 <= args.api_limit <= LIMIT:
        parser.error('api-limit must be between 1 and %d' % LIMIT)
    args.run_dir.mkdir(parents=True, exist_ok=True)
    with (args.run_dir / '.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.error('another turn is running; live calls must be serial')
        run_turn(args, parser)


def run_turn(args, parser):
    ledger_path = args.run_dir / 'ledger.json'
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {
        'limit': args.api_limit or LIMIT, 'attempts': [], 'stopped': False}
    if args.api_limit is not None and ledger.get('limit', LIMIT) != args.api_limit:
        parser.error('api-limit differs from the run ledger; do not change a started experiment budget')
    if ledger['stopped']:
        parser.error('experiment stopped after an error; inspect ledger, do not retry live')
    path = args.run_dir / (args.trial + '-' + args.scenario + '.json')
    digest = fingerprint()
    state = json.loads(path.read_text()) if path.exists() else {
        'trial': args.trial, 'scenario': args.scenario, 'source_sha256': digest,
        'model': MODEL, 'reasoning': 'high', 'transport': 'live' if args.live else 'fake',
        'profile': {'purchase_purpose': 'UNKNOWN'}, 'history': [], 'support_context': [], 'turns': [], 'closed': False}
    if state['source_sha256'] != digest or state['transport'] != ('live' if args.live else 'fake'):
        parser.error('source/transport changed within a dialogue; start another trial')
    if state['closed'] or len(state['turns']) >= 3:
        parser.error('dialogue ended or three customer turns reached')
    config = {'model': MODEL, 'reasoning': 'high', 'api_key': 'fake'}
    if args.live:
        proof = args.run_dir / 'dry_run.json'
        if not proof.exists() or json.loads(proof.read_text()).get('source_sha256') != digest:
            parser.error('run the same entrypoint with fake transport for this source before live')
        import os
        if args.env_file:
            load_env_file(args.env_file)
        config['api_key'] = os.getenv('OPENAI_API_KEY', '')
        if not config['api_key']:
            parser.error('OPENAI_API_KEY required; no fallback')
        if len(ledger['attempts']) >= ledger.get('limit', LIMIT):
            parser.error('%d-call experiment budget exhausted' % ledger.get('limit', LIMIT))
        attempt = {'trial': args.trial, 'scenario': args.scenario, 'turn': len(state['turns']) + 1, 'status': 'started'}
        ledger['attempts'].append(attempt)
        # Reserve before transport: timeout/crash must never silently refund a call.
        ledger['stopped'] = True
        save(ledger_path, ledger)
    history = state['history'] + [{'direction': 'INBOUND', 'body': args.customer}]
    agent = SalesAgent(config)
    captured = {}

    def fake_urlopen(request, timeout):
        payload = json.loads(request.data)
        assert payload['model'] == MODEL and payload['reasoning']['effort'] == 'high'
        assert payload['text']['format']['strict']
        context = json.loads(payload['input'][1]['content'][0]['text'])
        assert context['brain_and_skills'] and context['current_project_unit_offering']
        assert 'focused_sales_evidence' in context and 'relevant_project_knowledge' in context
        assert context['latest_customer_message'] == args.customer
        captured['context'] = context
        decision = {'action': 'REPLY', 'sales_move': 'POSITION', 'buyer_signal': 'QUESTION',
                    'reply': 'FAKE transport validation only.', 'lead_updates': {k: None for k in PROFILE_FIELDS},
                    'support_request': None, 'handoff_reason': None, 'handoff_details': None}
        class Response:
            def __enter__(self): return self
            def __exit__(self, *exc): pass
            def read(self): return json.dumps({'status': 'completed', 'output_text': json.dumps(decision), 'usage': {}}).encode()
        return Response()

    try:
        # Intercept the real OpenAIProvider HTTP transport, not SalesAgent.decide.
        if args.live:
            decision, usage = agent.decide(args.customer, state['profile'], history, state.get('support_context', []))
        else:
            with patch('app.provider.urllib.request.urlopen', fake_urlopen):
                decision, usage = agent.decide(args.customer, state['profile'], history, state.get('support_context', []))
    except Exception as exc:
        if args.live:
            attempt['status'] = 'failed'
            attempt['error_type'] = type(exc).__name__
            save(ledger_path, ledger)
        raise SystemExit('Sales Lab stopped: ' + type(exc).__name__ + '; inspect provider failure locally, no retry') from None
    if decision['action'] == 'SUPPORT_REQUEST':
        from .service import support_signature
        request = decision['support_request']
        signature = support_signature(request)
        duplicate = next((item for item in state.get('support_context', [])
                          if item.get('signature') == signature and item.get('status') in ('OPEN', 'RESOLVED')), None)
        if not duplicate:
            state.setdefault('support_context', []).append({
                'request_id': 'sales-lab-support-%d' % (len(state.get('support_context', [])) + 1),
                'status': 'OPEN', 'support_type': request.get('support_type', 'OTHER'),
                'requested_fact': request.get('requested_fact', ''), 'subject': request.get('subject', ''),
                'customer_need': request.get('customer_need', ''), 'reason': request.get('reason', ''),
                'resume_stage': request.get('resume_stage', ''), 'resume_objective': request.get('resume_objective', ''),
                'signature': signature, 'support_result': None, 'created_at': 'SALES_LAB', 'resolved_at': None,
            })
    state['profile'].update({k: v for k, v in decision['lead_updates'].items() if k in PROFILE_FIELDS and v is not None})
    history.append({'direction': 'OUTBOUND', 'body': decision['reply']})
    state['history'] = history
    state['turns'].append({'customer': args.customer, 'decision': decision, 'usage': usage})
    state['closed'] = decision['action'] in ('APPOINTMENT_HANDOFF', 'MANDATORY_HANDOFF')
    if captured:
        state['dry_run_context'] = captured['context']
    save(path, state)
    if not args.live:
        save(args.run_dir / 'dry_run.json', {'source_sha256': digest, 'status': 'passed', 'entrypoint': 'python3 -m app.sales_lab', 'transport': 'fake HTTP through real OpenAIProvider'})
    if args.live:
        attempt.update(status='completed', usage=usage)
        ledger['stopped'] = False
        save(ledger_path, ledger)
    print(json.dumps({'file': str(path), 'turn': len(state['turns']), 'decision': decision, 'usage': usage}, ensure_ascii=False))


if __name__ == '__main__':
    main()
