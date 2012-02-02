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
from zope.component import getUtility
from zope.cachedescriptors.property import Lazy
from zope.security.proxy import removeSecurityProxy
from zope.security import checkPermission
from zope.proxy import removeAllProxies
from zope.traversing.browser import absoluteURL
from zope.app.intid.interfaces import IIntIds

from zojax.layoutform import button
from zojax.statusmessage.interfaces import IStatusMessage

from zojax.askexpert.browser.form import Form
from zojax.askexpert.interfaces import _


class PortletForm(Form):

    def __init__(self, context, request):
        self.portlet = context
        super(PortletForm, self).__init__(context.formObject, request)

    @property
    def action(self):
        """See interfaces.IInputForm"""
        if self.portlet.redirectToForm:
            return '%s/'%absoluteURL(self.context, self.request)
        else:
            return self.request.getURL()

    @Lazy
    def fields(self):
        ids = getUtility(IIntIds)
        fields = []
        for i in self.portlet.fields:
            try:
                fields.append(ids.getObject(i).__name__)
            except (TypeError, KeyError):
                continue
        return super(PortletForm, self).fields.select(*fields)

    @Lazy
    def groups(self):
        res = super(PortletForm, self).groups
        ids = getUtility(IIntIds)
        fields = []
        for i in self.portlet.fields:
            try:
                fields.append(ids.getObject(i).__name__)
            except (TypeError, KeyError):
                continue
        for i in res:
            i.fields = i.fields.select(*fields)
        return res

    @button.buttonAndHandler(_(u'Submit'), name='submit.portlet')
    def handleSubmit(self, action):
        data, errors = self.extractData()
        if errors:
            IStatusMessage(self.request).add(self.formErrorsMessage, 'warning')
            return
        if not self.portlet.redirectToForm:
            removeSecurityProxy(self.context).processData(data, self.request)
            IStatusMessage(self.request).add(_(u'Request has been processed.'))

            if self.context.confirm:
                self.confirm = True


def getSubmitTitle(adapter):
    if adapter.form.portlet.submitLabel is not None and adapter.form.portlet.submitLabel:
        return adapter.form.portlet.submitLabel
    elif adapter.form.context.submitLabel is not None and adapter.form.context.submitLabel:
        return adapter.form.context.submitLabel
    return adapter.widget.label

ApplyLabel = button.ComputedButtonActionAttribute(getSubmitTitle, button=PortletForm.buttons['submit.portlet'])


class FormPortlet(object):

    formObject = None

    def update(self):
        super(FormPortlet, self).update()
        ids = getUtility(IIntIds)
        if self.form is not None:
            self.formObject = ids.queryObject(self.form)
        self.visibleTitle = (self.label is not None and self.label) and self.label or \
        (self.formObject is not None and self.formObject.title or '')

    def isAvailable(self):
        return self.formObject is not None and \
        ('form.buttons.submit' not in self.request) \
        and ((self.redirectToForm and 'form.buttons.submit.portlet' not in self.request) \
        or not self.redirectToForm) \
        and checkPermission('zojax.askexpert.SubmitForm', self.formObject)
