"""
Cloudflare Workers AI -- one place for every Cloudflare call, with a SECOND account as backup.

  Account 1: CLOUDFLARE_ACCOUNT_ID   + CLOUDFLARE_API_TOKEN     (main)
  Account 2: CLOUDFLARE_ACCOUNT_ID_2 + CLOUDFLARE_API_TOKEN_2   (optional backup)

Both accounts run the SAME models, so meaning-numbers from either account are identical and work with the
saved files. When account 1 says "daily free allocation used up" (error 4006), it is rested until the daily
reset (00:00 UTC = 5:30 AM IST) and account 2 is used. Other errors (timeout, 5xx, 429) rest an account for
60 seconds and the other account is tried at once.

Used by: meaning search (bge-m3), the senior librarian (bge-reranker-base), the Cloudflare answer backup
and the Cloudflare spare judge (Llama 3.3 70B).
"""
import os
import threading
import time
from datetime import datetime, timezone

import requests

from backend.services.reqlog import log

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

SHORT_REST = 60
_lock = threading.Lock()
_rest_until = {}          # account label -> unix time until which it is skipped
_exhausted_day = {}       # account label -> "YYYY-MM-DD" (UTC) when its daily units ran out
_http = requests.Session()


def accounts():
    """[(label, account_id, token)] for every configured account, main first."""
    out = []
    for label, suffix in (("account 1", ""), ("account 2", "_2")):
        a = os.getenv(f"CLOUDFLARE_ACCOUNT_ID{suffix}", "").strip()
        t = os.getenv(f"CLOUDFLARE_API_TOKEN{suffix}", "").strip()
        if a and t:
            out.append((label, a, t))
    return out


def configured() -> bool:
    return bool(accounts())


def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _usable(label):
    with _lock:
        if _exhausted_day.get(label) == _today():
            return False
        return time.time() >= _rest_until.get(label, 0)


def available() -> bool:
    """True if at least one account is configured and not resting."""
    return any(_usable(lbl) for lbl, _, _ in accounts())


def status():
    """For logs / the scoreboard: which accounts are configured and which ran out today."""
    return [{"account": lbl, "used_up_today": _exhausted_day.get(lbl) == _today()} for lbl, _, _ in accounts()]


class CloudflareError(RuntimeError):
    pass


def run(model: str, payload: dict, timeout: float, what: str = "call"):
    """POST to Workers AI. Returns the parsed "result" (dict or list). Tries account 1, then account 2.
    Raises CloudflareError when no account could do it."""
    accs = accounts()
    if not accs:
        raise CloudflareError("no CLOUDFLARE_ACCOUNT_ID / CLOUDFLARE_API_TOKEN")
    errors = []
    tried = 0
    for label, acct, token in accs:
        if not _usable(label):
            errors.append(f"{label}: resting")
            continue
        if errors:
            log("CLOUDFLARE", f"🔀 HANDOVER [cloudflare {what}] {errors[-1][:140]} → {label} takes charge")
        tried += 1
        try:
            r = _http.post(f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/{model}",
                           headers={"Authorization": f"Bearer {token}"}, json=payload, timeout=timeout)
            try:
                body = r.json()
            except ValueError:
                body = {}
            if not isinstance(body, dict):              # a bare list/str body: treat it as the result
                body = {"result": body}
            if r.status_code == 200 and body.get("success", True) is not False:
                return body.get("result")
            text = str(body.get("errors") if isinstance(body, dict) and body.get("errors") else (r.text or ""))[:300]
            low = text.lower()
            daily = "4006" in text or "daily free allocation" in low or ("neurons" in low and r.status_code == 429)
            with _lock:
                if daily:
                    _exhausted_day[label] = _today()
                elif r.status_code != 400:            # 400 = this request's problem, the account is fine
                    _rest_until[label] = time.time() + SHORT_REST
            if daily:
                log("CLOUDFLARE", f"🪫 {label}: today's free units are used up -- resting it until 5:30 AM IST")
            errors.append(f"{label}: HTTP {r.status_code} {text}")
            if r.status_code == 400 and not daily:
                break                                   # the other account would say the same
        except requests.RequestException as e:
            with _lock:
                _rest_until[label] = time.time() + SHORT_REST
            errors.append(f"{label}: {type(e).__name__} {str(e)[:120]}")
    if tried == 0 and not errors:
        errors.append("no account available")
    log("CLOUDFLARE", f"❌ every Cloudflare account failed for {what} ({'; '.join(errors)[:200]})")
    raise CloudflareError(f"Cloudflare {what} failed ({'; '.join(errors)[:400]})")
