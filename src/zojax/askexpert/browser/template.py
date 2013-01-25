##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from email.Utils import formataddr

from zope import interface, component, i18n
from zope.app.component.hooks import getSite
from zope.component import queryUtility, getMultiAdapter
from zope.traversing.browser import absoluteURL

from z3c.breadcrumb.interfaces import IBreadcrumb

from zojax.mail.interfaces import IFromAddress

from interfaces import IFormResults
from zojax.askexpert.interfaces import _


class MessageTemplate(object):

    contentType = 'text/html'

    @property
    def subject(self):
        msg = u'Form has been processed'

        title = getattr(self.context, 'title', u'')
        if title:
            return u'%s: %s'%(msg, title)
        else:
            return msg

    def update(self):
        super(MessageTemplate, self).update()

        request, context = self.request, self.context

        self.portal_title = getMultiAdapter((getSite(), request), IBreadcrumb).name
        self.portal_url = '%s/' % absoluteURL(getSite(), request)
        self.url = '%s/' % absoluteURL(context, request)

        self.form = getMultiAdapter((context, request), IFormResults)
        self.form.update(self.record)


class DefaultFromAddress(object):

    component.adapts(MessageTemplate)
    interface.implements(IFromAddress)

    def __init__(self, template):
        self.template = template
        self.from_address = i18n.translate(_(u"${name} <${email}>", mapping=dict(name=template.storage.fromname,
                                                                  email=template.storage.fromaddr)))
