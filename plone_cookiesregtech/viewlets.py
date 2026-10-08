# -*- coding: utf-8 -*-
"""Injects the CookiesRegTech consent bootstrap into <head> on every site
page. Registered in the plone.htmlhead viewlet manager and ordered first
(profiles/default/viewlets.xml), because the consent script must run
before analytics and tag managers to block trackers and signal Google
Consent Mode in time.
"""
import re

from plone.app.layout.viewlets.common import ViewletBase
from plone.registry.interfaces import IRegistry
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility

from plone_cookiesregtech.api import DEFAULT_SERVER, SETTINGS_PREFIX
from plone_cookiesregtech.interfaces import ICookiesRegTechSettings

_DOMAIN_ID_RE = re.compile(r"^[a-z0-9]{10,40}$", re.IGNORECASE)


class ConsentScriptViewlet(ViewletBase):

    render = ViewPageTemplateFile("browser/templates/head_viewlet.pt")

    def script_url(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ICookiesRegTechSettings, check=False, prefix=SETTINGS_PREFIX
        )
        if not getattr(settings, "banner_enabled", True):
            return None
        domain_id = (getattr(settings, "domain_id", "") or "").strip()
        if not _DOMAIN_ID_RE.match(domain_id):
            return None
        server = (getattr(settings, "server", "") or DEFAULT_SERVER).rstrip("/")
        return "%s/embed/boot/%s.js" % (server, domain_id)
