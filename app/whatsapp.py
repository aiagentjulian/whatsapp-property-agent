import json
import os
import re
import time

from .config import ROOT


def normalize_contact(value):
    return " ".join(re.findall(r"[a-z0-9]+", (value or "").lower()))


def is_allowlisted(contact, allowlist):
    target = normalize_contact(contact)
    if not target:
        return False
    for entry in allowlist:
        candidate = normalize_contact(entry)
        if target == candidate:
            return True
    return False


class WhatsAppWeb:
    """Small headed Playwright adapter. UI uncertainty fails closed; no retry after uncertain send."""
    def __init__(self, config, runtime):
        self.config = config
        self.runtime = runtime

    def _playwright(self):
        try:
            from playwright.sync_api import sync_playwright
            return sync_playwright()
        except ImportError as exc:
            raise RuntimeError("Install Playwright first: python -m pip install -r requirements.txt") from exc

    @staticmethod
    def _find_search(page):
        for selector in ('[aria-label="Search input textbox"]', '[data-tab="3"]', 'div[contenteditable="true"][role="textbox"]'):
            locator = page.locator(selector)
            if locator.count() and locator.first.is_visible():
                return locator.first
        raise RuntimeError("WhatsApp Web search control is unavailable; stopping safely.")

    def _open_contact(self, page, contact):
        # Numeric contacts use a direct, exact-phone URL so a missing thread or a
        # saved display name cannot cause selection of another chat.
        digits = re.sub(r"\D", "", contact)
        if digits:
            page.goto("https://web.whatsapp.com/send?phone=" + digits, wait_until="domcontentloaded")
            composer = page.locator('footer div[contenteditable="true"][role="textbox"], footer [data-tab="10"]').first
            try:
                composer.wait_for(state="visible", timeout=20000)
            except Exception:
                return False
            header = page.locator('header').last
            if not header.count() or not header.is_visible():
                raise RuntimeError("Unknown WhatsApp chat state; stopping safely.")
            return True

        # Named contacts are searched exactly; no new conversation is sent.
        search_button = page.locator('button[aria-label="Search"], span[data-icon="search"]').first
        if search_button.count() and search_button.is_visible():
            try:
                search_button.click(timeout=1200)
            except Exception:
                pass
        search = self._find_search(page)
        search.fill(contact)
        page.wait_for_timeout(600)
        rows = page.locator('[role="listitem"]')
        selected = None
        for idx in range(min(rows.count(), 20)):
            row = rows.nth(idx)
            text = row.inner_text(timeout=1000)
            titles = [el.get_attribute("title") for el in row.locator("[title]").all()]
            names = [value for value in titles if value] + [text.splitlines()[0] if text.splitlines() else ""]
            if any(normalize_contact(contact) == normalize_contact(name) for name in names):
                selected = row
                break
        if selected is None:
            # Some WhatsApp Web builds expose results as spans with title instead of listitems.
            for candidate in page.locator('span[title]').all():
                title = candidate.get_attribute("title")
                if title and normalize_contact(title) == normalize_contact(contact) and candidate.is_visible():
                    selected = candidate
                    break
        if selected is None:
            return False
        selected.click(timeout=2500)
        page.wait_for_timeout(350)
        header = page.locator('header').last
        if not header.count() or not header.is_visible():
            raise RuntimeError("Unknown WhatsApp chat state; stopping safely.")
        return True

    @staticmethod
    def _incoming(page):
        found = []
        for message in page.locator(".message-in").all():
            external_id = message.get_attribute("data-id")
            if not external_id:
                continue
            text = message.locator(".copyable-text").inner_text() if message.locator(".copyable-text").count() else ""
            if text.strip():
                found.append((external_id, text.strip()))
        return found

    @staticmethod
    def _qr_visible(page):
        for selector in ('canvas[aria-label*="Scan"]', 'div[data-ref]'):
            for locator in page.locator(selector).all():
                if locator.is_visible():
                    return True
        return False

    def _wait_authenticated(self, page, stop_file=None, timeout=300):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if stop_file and stop_file.exists():
                return False
            if self._qr_visible(page):
                raise RuntimeError("WhatsApp Web session is not authenticated; run the login command and retry. Runtime stopped safely.")
            try:
                self._find_search(page)
                downloading = page.get_by_text("Your messages are downloading", exact=False)
                if not downloading.count() or not downloading.first.is_visible():
                    return True
            except RuntimeError:
                pass
            page.wait_for_timeout(1000)
        raise RuntimeError("WhatsApp Web did not finish loading its messages within 300 seconds; Runtime stopped safely.")

    def _send(self, page, body):
        current = page.locator('.message-out').count()
        composer = page.locator('footer div[contenteditable="true"][role="textbox"], footer [data-tab="10"]').first
        if not composer.count() or not composer.is_visible():
            raise RuntimeError("WhatsApp composer is unavailable; send status will be marked uncertain.")
        composer.fill(body)
        composer.press("Enter")
        try:
            page.wait_for_function("n => document.querySelectorAll('.message-out').length > n", arg=current, timeout=5000)
        except Exception as exc:
            raise RuntimeError("WhatsApp send result is uncertain; operator review required and message will not be retried.") from exc

    def login(self):
        """Open persistent headed profile for manual login; never read or send messages."""
        profile = self.config["profile_dir"]
        if not profile.is_absolute():
            profile = ROOT / profile
        profile.mkdir(parents=True, exist_ok=True)
        with self._playwright() as p:
            context = p.chromium.launch_persistent_context(str(profile), headless=False, args=["--start-maximized"], no_viewport=True)
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")
            print("WhatsApp Web is open. Scan the QR code in the local browser; no messages will be read or sent. Press Ctrl+C when login is complete.", flush=True)
            try:
                while True:
                    page.wait_for_timeout(1000)
            except KeyboardInterrupt:
                pass
            finally:
                context.close()

    def send_outbound(self, contact, body):
        """Send one operator-approved message from an existing allowlisted chat."""
        if not is_allowlisted(contact, self.config.get("outbound_allowlist", [])):
            raise RuntimeError("Contact is not in WHATSAPP_OUTBOUND_ALLOWLIST")
        profile = self.config["profile_dir"]
        if not profile.is_absolute():
            profile = ROOT / profile
        with self._playwright() as p:
            context = p.chromium.launch_persistent_context(str(profile), headless=False, args=["--start-maximized"], no_viewport=True)
            try:
                page = context.pages[0] if context.pages else context.new_page()
                page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")
                page.wait_for_timeout(1200)
                if page.locator('canvas[aria-label*="Scan"], div[data-ref]').count():
                    raise RuntimeError("WhatsApp Web is not authenticated in the existing browser profile")
                self._open_contact(page, contact)
                self._send(page, body)
            finally:
                context.close()

    def run(self, send_replies=False, stop_file=None, ready_file=None):
        if not self.config["allowlist"]:
            raise RuntimeError("Set WHATSAPP_ALLOWLIST before starting the message listener.")
        profile = self.config["profile_dir"]
        if not profile.is_absolute():
            profile = ROOT / profile
        profile.mkdir(parents=True, exist_ok=True)
        with self._playwright() as p:
            context = p.chromium.launch_persistent_context(str(profile), headless=False, args=["--start-maximized"], no_viewport=True)
            try:
                page = context.pages[0] if context.pages else context.new_page()
                page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")
                if not self._wait_authenticated(page, stop_file):
                    return
                print("Allowlisted listener started; replies %s." % ("ENABLED" if send_replies else "DISABLED"), flush=True)
                crm_result = self.runtime.sync_crm()
                if crm_result["status"] != "SYNCED":
                    print("CRM sync status: %s (%s pending)." % (crm_result["status"], crm_result.get("pending", len(crm_result.get("results", [])))), flush=True)
                outbound_prospects = [p["phone"] for p in self.runtime.store.prospects() if p["outbound_status"] in ("SENT", "REPLIED")]
                contacts = list(dict.fromkeys(self.config["allowlist"] + outbound_prospects))
                contact_pages = {}
                for index, contact in enumerate(contacts):
                    contact_page = page if index == 0 else context.new_page()
                    contact_pages[contact] = contact_page
                    if not self._open_contact(contact_page, contact):
                        print("An allowlisted chat is still loading; keeping its browser tab open without re-navigation.", flush=True)
                    state_key = "seen:" + normalize_contact(contact)
                    if self.runtime.store.adapter_value(state_key) is None:
                        # No thread existed at startup. Any later first inbound
                        # message should be processed, not baselined.
                        self.runtime.store.set_adapter_value(state_key, "[]")
                if ready_file:
                    ready_file.parent.mkdir(parents=True, exist_ok=True)
                    ready_file.write_text(str(os.getpid()), encoding="utf-8")
                try:
                    while not (stop_file and stop_file.exists()):
                        for contact, contact_page in contact_pages.items():
                            if self._qr_visible(contact_page):
                                raise RuntimeError("WhatsApp Web session expired; Runtime stopped safely. Run the login command before restarting.")
                            composer = contact_page.locator('footer div[contenteditable="true"][role="textbox"], footer [data-tab="10"]').first
                            if not composer.count() or not composer.is_visible():
                                # Give WhatsApp time to finish opening this chat;
                                # repeating goto here can trap it on "Starting chat".
                                contact_page.wait_for_timeout(300)
                                continue
                            incoming = self._incoming(contact_page)
                            state_key = "seen:" + normalize_contact(contact)
                            seen_raw = self.runtime.store.adapter_value(state_key)
                            seen = set(json.loads(seen_raw)) if seen_raw else set()
                            # First observation is only a history baseline. Never replay old chat messages.
                            if seen_raw is None:
                                seen.update(mid for mid, _ in incoming)
                            else:
                                for external_id, body in incoming:
                                    if external_id in seen:
                                        continue
                                    seen.add(external_id)
                                    if self.runtime.allowed(contact) and send_replies:
                                        self.runtime.process_inbound(contact, external_id, body, True, lambda _c, reply: self._send(contact_page, reply))
                                        crm_result = self.runtime.sync_crm()
                                        if crm_result["status"] not in ("SYNCED", "AUTH_REQUIRED"):
                                            print("CRM sync remains pending for retry.", flush=True)
                                    elif send_replies is False:
                                        print("New allowlisted inbound observed; message handling is disabled until --send-replies is authorized.", flush=True)
                            self.runtime.store.set_adapter_value(state_key, json.dumps(sorted(seen)[-5000:]))
                            contact_page.wait_for_timeout(200)
                        page.wait_for_timeout(1800)
                except KeyboardInterrupt:
                    pass
                except Exception as exc:
                    raise RuntimeError("WhatsApp adapter stopped safely: %s" % exc) from exc
            finally:
                context.close()
