from factory import Factory
from ontology import OntoBase


class Base(OntoBase):
    """ This is the ontology base class, used to ensure that the properties
    defined in the ontology are respected."""

    def __init__(self):
        super().__init__()
        if self._osl.is_document:
            self._meta = Factory.build('shared.doc_meta_info')

    def __str__(self):
        if hasattr(self._osl, 'pstr'):
            values = [getattr(self, s) for s in self._osl.pstr[1]]
            return self._osl.pstr[0].format(*values)
        else:
            return super().__str__()

    def __eq__(self, other):
        if not isinstance(other, Base):
            return False
        if self._osl != other._osl:
            return False
        for p in self._osl.properties + self._osl.inherited_properties:
            if getattr(self, p[0]) != getattr(other, p[0]):
                return False
        return True

    def __ne__(self, other):
        return not self == other




