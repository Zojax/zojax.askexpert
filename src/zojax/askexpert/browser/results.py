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
from zope import interface, component
from zope.security.proxy import removeSecurityProxy
from zope.cachedescriptors.property import Lazy
from zope.app.intid.interfaces import IIntIds

from z3c.form import group

from zojax.content.type.interfaces import IOrder
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.layoutform import button, Fields, PageletForm, PageletDisplayForm
from zojax.persistent.fields.interfaces import IField, IRichText

from zojax.askexpert.interfaces import _, IGroup, IForm

from interfaces import IFormResults


class FormResults(object):

    component.adapts(IForm, None)
    interface.implements(IFormResults)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def update(self, record):
        form = self.context
        record = dict(record)
        order = IOrder(form)
        ids = component.getUtility(IIntIds)

        groups = []

        def getFieldData(field, fields):
            fieldId = field.__name__
            if fieldId not in record:
                return
            if IRichText.providedBy(field):
                fields.append((field.title, record.pop(fieldId).text))
            elif IField.providedBy(field):
                fields.append((field.title, record.pop(fieldId)))
                
        fields_nogroup = []

        for grp in order.values():
            if IGroup.providedBy(grp):
                fields = []
                for id in grp.fields:
                    try:
                        field = ids.getObject(id)
                    except (TypeError, KeyError), e:
                        continue
                    fieldId = field.__name__
                    getFieldData(field, fields)
                groups.append((grp.title, fields))
            else:
                getFieldData(grp, fields_nogroup)
        if fields_nogroup:
            groups.append((u'', fields_nogroup))
        self.dictionary = groups
