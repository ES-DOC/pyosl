import uuid
from datetime import date
from copy import deepcopy
import re

from pyosl import Factory


def make_time(astring, is_offset=False):
    ok1 = re.match(r'^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}$', astring)
    ok2 = re.match(r'^\d{4}-\d{2}-\d{2}$', astring)
    if ok1 or ok2:
        k = Factory.build('time.date_time')
        k.is_offset = is_offset
        k.value = astring
        return k
    raise ValueError(f'Attempt to set date_time with {astring}')


def named_build(klass, name):
    """ Minimise effort for building a class """
    k = Factory.build(klass)
    k.name = name
    return k


def new_document(klass, name=None, author=None):
    """ Convenience method for starting new documents"""
    doc = Factory.new_document(klass, author)
    doc.name = name
    doc._osl.id = uuid.uuid4()
    return doc


def calendar_period(sdate, edate):
    """ Create a time period object, using a normal date of form yyyy-mm-dd format.
    If dd doesn't appear, uses 1st of month. Calendar must be Gregorian!"""
    s2d = lambda x: [int(j) for j in x.split('-')]
    p = Factory.build('time.time_period')
    p.calender = 'gregorian'
    d = Factory.build('time.date_time')
    d.value = sdate
    d1 = date(*s2d(sdate))
    d2 = date(*s2d(edate))
    td = d2 - d1
    p.units = 'days'
    p.length = float(td.days)
    p.date = d
    p.date_type = 'from'
    return p


def osl_fill_from(self, other):
    """ FIll non-present-attributes in self, from other"""
    #TODO: What about inherited properties?
    for p in self._osl.properties:
        conditional_copy(other, self, p[0])
    return self


def online(url, name, **kw):
    """ Convenience class for building a shared online reference"""
    k = Factory.build('shared.online_resource')
    k.linkage = url
    k.name = name
    for key,val in kw.items():
        setattr(k, key, kw[val])
    return k


def numeric_value(number, units):
    """ Convenience class for building a numeric instance"""
    k = Factory.build('shared.numeric')
    k.value = number
    k.units = units
    return k


def conditional_copy(self, other, key, altkey=None):
    """If [[self]] has attribute [[key]] and if
    the value of that attribute is not None, AND,
    the value of that attribute in [[other]] is None,
    assign that value to that attribute in [[other]].
    If [[altkey]] is not None, use that value for
    the key we look for in [[other]].

    """
    if hasattr(self, key):
        possible = getattr(self, key)
        if possible:
            usekey = {True: altkey, False: key}[altkey is not None]
            if hasattr(other, usekey):
                exists = getattr(other, usekey)
                if exists:
                    return
            setattr(other, usekey, deepcopy(possible))

def get_reference_for(document):
    """ Returns a doc_reference instance for a document"""
    k = Factory.build('shared.doc_reference')
    for key in ('name', 'canonical_name'):
        conditional_copy(document, k, key)
    if not getattr(k, 'canonical_name'):
        if getattr(k,'name'):
            setattr(k,'canonical_name',getattr(k,'name'))
    for key in ('version',):
        conditional_copy(document._meta, k, key)
    for inkey, outkey in [('uid','id'),]:
        conditional_copy(document._meta, k, inkey, outkey)
    for inkey, outkey in [('type_key','type'),]:
        setattr(k, outkey, getattr(document._osl,inkey))
    return k

