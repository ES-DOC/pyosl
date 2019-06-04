import uuid
from datetime import date
from factory import Factory
from copy import deepcopy


def volume(value, units):
    v = Factory.build('platform.storage_volume')
    v.volume = value
    v.units = units
    return v


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
        if not getattr(self,p[0]):
            setattr(self, p[0], deepcopy(getattr(other, p[0])))
    return self


def online(url, name, **kw):
    k = Factory.build('shared.online_resource')
    k.linkage = url
    k.name = name
    for key,val in kw.items():
        setattr(k, key, kw[val])
    return k

def numeric_value(number, units):
    k = Factory.build('shared.numeric')
    k.value = number
    k.units = units
    return k
