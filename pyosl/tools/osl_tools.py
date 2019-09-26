import uuid
from datetime import date
from copy import deepcopy

from pyosl import Factory


def named_build(klass, name):
    """ Minimise effort for building a class """
    k = Factory.build(klass)
    k.name = name
    return k


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
    p.time_unit = 'days'
    #FIXME: Why is this a string?
    p.length = str(td.days)
    p.date = d
    p.date_type = 'date is start'
    return p


def osl_fill_from(self, other):
    """ FIll non-present-attributes in self, from other"""
    for p in self._osl.properties:
        conditional_copy(self, other, p[0])
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
    the value of that attribute is not None, assign
    it to [[other]], using [[altkey]] if present
    otherwise [[key]] for the attribute name"""
    if hasattr(self, key):
        possible = getattr(self,key)
        if possible:
            if altkey:
                setattr(other, altkey, deepcopy(possible))
            else:
                setattr(other, key, deepcopy(possible))


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


