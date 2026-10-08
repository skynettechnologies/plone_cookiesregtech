# -*- coding: utf-8 -*-
"""The CookiesRegTech settings page: connect, pending, and connected
screens, reached from Site Setup (controlpanel.xml)."""
import re
from urllib.parse import urlparse

from plone.protect.utils import addTokenToUrl
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.utils import safe_text
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getUtility

from plone_cookiesregtech.api import (
    DEFAULT_SERVER,
    SETTINGS_PREFIX,
    VERSION,
    api_post,
    unexpected_reply,
)
from plone_cookiesregtech.interfaces import ICookiesRegTechSettings

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class SettingsView(BrowserView):

    def settings(self):
        registry = getUtility(IRegistry)
        return registry.forInterface(
            ICookiesRegTechSettings, check=False, prefix=SETTINGS_PREFIX
        )

    def save(self, **changes):
        settings = self.settings()
        for key, value in changes.items():
            setattr(settings, key, value)

    def server(self):
        return (getattr(self.settings(), "server", "") or DEFAULT_SERVER).rstrip("/")

    # ------------------------------------------------------------ state

    def state(self):
        settings = self.settings()
        if (settings.secret or "") and (settings.domain_id or ""):
            return "connected"
        if settings.pending_token or "":
            return "pending"
        return "connect"

    def overview(self):
        settings = self.settings()
        if not (settings.secret or ""):
            return None
        result = api_post(self.server(), "/api/plugin/overview", {"secret": settings.secret})
        return result if result.get("_status") == 200 else None

    def admin_email(self):
        try:
            from plone import api as plone_api
            member = plone_api.user.get_current()
            return member.getProperty("email", "") or ""
        except Exception:
            return ""

    def version(self):
        return VERSION

    def category_label(self, value):
        labels = {
            "ESSENTIAL": "Essential",
            "FUNCTIONALITY": "Functionality",
            "ANALYTICS": "Analytics",
            "ADS": "Ads",
            "UNCATEGORISED": "Uncategorised",
        }
        return labels.get(value, value)

    # ----------------------------------------------------------- actions

    def __call__(self):
        if self.request.method == "POST":
            redirect = self.handle_action(safe_text(self.request.form.get("crt_action", "")))
            if redirect is not None:
                return redirect
        return super(SettingsView, self).__call__()

    def _flash(self, message, kind="info"):
        IStatusMessage(self.request).addStatusMessage(message, type=kind)

    def _back(self):
        self.request.response.redirect(
            addTokenToUrl("%s/@@cookiesregtech-settings" % self.context.absolute_url())
        )
        return ""

    def handle_action(self, action):
        settings = self.settings()
        form = self.request.form

        if action == "connect":
            email = safe_text(form.get("email", "")).strip()
            consent = bool(form.get("consent"))
            if not _EMAIL_RE.match(email) or not consent:
                self._flash("Enter a valid email address and accept the terms to continue.", "error")
                return self._back()
            hostname = urlparse(self.context.absolute_url()).hostname or ""
            result = api_post(self.server(), "/api/plugin/provision", {
                "email": email,
                "hostname": hostname,
                "platform": "plone",
                "consent": True,
            })
            if result.get("status") == "connected":
                self.save(
                    domain_id=result.get("domainId", ""),
                    secret=result.get("secret", ""),
                    email=result.get("email") or email,
                    pending_token="",
                    banner_enabled=True,
                )
                self._flash(
                    "The free account is ready and the consent banner is live on the site. "
                    "A sign-in link was emailed to %s." % email
                )
            elif result.get("status") == "confirmation_sent":
                self.save(pending_token=result.get("requestToken", ""), email=email)
                self._flash(
                    "That email already has an account. We sent it a confirmation link. "
                    'Click the link, then press "Check status" here.'
                )
            else:
                self._flash(result.get("error") or unexpected_reply(result), "error")
            return self._back()

        if action == "check":
            result = api_post(self.server(), "/api/plugin/status", {"requestToken": settings.pending_token})
            if result.get("status") == "connected":
                self.save(
                    domain_id=result.get("domainId", ""),
                    secret=result.get("secret", ""),
                    pending_token="",
                    banner_enabled=True,
                )
                self._flash("Connected. The consent banner is live on this site.")
            elif result.get("status") == "pending":
                self._flash("Not confirmed yet. Click the link in the email first.", "warning")
            else:
                self.save(pending_token="")
                self._flash(result.get("error") or "The request expired. Start again.", "error")
            return self._back()

        if action == "reset":
            self.save(pending_token="")
            return self._back()

        if action == "save":
            enabled = bool(form.get("banner_enabled"))
            self.save(banner_enabled=enabled)
            self._flash(
                "Cookie consent banner is enabled." if enabled else "Cookie consent banner is disabled."
            )
            return self._back()

        if action in ("dashboard", "upgrade"):
            payload = {"secret": settings.secret}
            if action == "upgrade":
                payload["intent"] = "upgrade"
            result = api_post(self.server(), "/api/plugin/login-link", payload)
            if result.get("url"):
                self.request.response.redirect(result["url"])
                return ""
            self._flash(result.get("error") or "Could not create a sign-in link. Try again.", "error")
            return self._back()

        if action == "disconnect":
            if settings.secret or "":
                api_post(self.server(), "/api/plugin/disconnect", {"secret": settings.secret})
            self.save(domain_id="", secret="", pending_token="", email="")
            self._flash(
                "Disconnected. The banner is off. The CookiesRegTech account and its data are unchanged."
            )
            return self._back()

        return None
