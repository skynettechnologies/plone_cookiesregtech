# -*- coding: utf-8 -*-
"""Registry schema for the CookiesRegTech connection.

Stored in plone.registry under the prefix "plone_cookiesregtech" — the
prefix is passed explicitly everywhere (registry.forInterface(...,
prefix=...)), because the default full-dotted-path prefix would not match
the records in profiles/default/registry.xml and every field would
silently read as its default.
"""
from zope import schema
from zope.interface import Interface


class ICookiesRegTechSettings(Interface):

    server = schema.TextLine(
        title="Server URL",
        default="https://www.cookiesregtech.com",
        required=False,
    )

    domain_id = schema.TextLine(title="Domain ID", default="", required=False)

    secret = schema.TextLine(title="Connection secret", default="", required=False)

    pending_token = schema.TextLine(title="Pending request token", default="", required=False)

    email = schema.TextLine(title="Account email", default="", required=False)

    banner_enabled = schema.Bool(title="Show the consent banner", default=True, required=False)
