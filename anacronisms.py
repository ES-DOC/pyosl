# This module provides routines which deal with anacronisms in the way we do things.
# Things which are "wrong" in some sense, and for which hacks are necessary.
# The goal is to remove the need for any of these.

def group_hack(klass_name):
    """ Handles the pyeseoc method of dealing with the
    issue outlined in https://github.com/ES-DOC/esdoc-cim-v2-schema/issues/30"""
    group_hack = klass_name.split(':')
    if len(group_hack) > 1:
        print(f'Ignoring type hint in {klass_name}, for now')
        klass_name = group_hack[0]
    return klass_name