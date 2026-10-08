# -*- coding: utf-8 -*-
"""CookiesRegTech API client (stdlib only, no extra dependencies)."""
import json
import urllib.error
import urllib.request

VERSION = "1.0.0"
DEFAULT_SERVER = "https://www.cookiesregtech.com"
SETTINGS_PREFIX = "plone_cookiesregtech"


def api_post(server, path, payload):
    """POST JSON to the consent server; returns dict with _status added."""
    request = urllib.request.Request(
        (server or DEFAULT_SERVER).rstrip("/") + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "CookiesRegTech-Plone/%s (+https://www.cookiesregtech.com)" % VERSION,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8") or "{}")
            status = response.status
    except urllib.error.HTTPError as error:
        try:
            body = json.loads(error.read().decode("utf-8") or "{}")
        except Exception:
            body = {}
        status = error.code
    except Exception:
        body = {}
        status = 0
    if not isinstance(body, dict):
        body = {}
    body["_status"] = status
    return body


def unexpected_reply(result):
    return (
        "Unexpected reply from the consent server (HTTP %d). "
        "If this repeats, the request may be blocked by a firewall."
        % (result.get("_status") or 0)
    )
