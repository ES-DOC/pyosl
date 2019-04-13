from pyosl.factory import Ontology, OntoBase, Factory
from pyosl.uml_utils import uml_bubble, uml_simple_box, uml_enum_box_label, uml_class_box_label
import unittest


class UmlBase(OntoBase):

    def label(self, option='bubble', **kwargs):
        if option == 'bubble':
            return self.__bubble()
        elif option == 'box':
            return self.__box(**kwargs)
        elif option == 'uml':
            return self.__uml(**kwargs)
        else:
            raise ValueError('Unknown label type requested [{}]'.format(option))

    def __bubble(self):
        """ Return representation as graphviz node label string"""
        return uml_bubble(self)

    def __box(self, **kwargs):
        """ Return representation as graphviz node with name
        padded to the left and right with blanks and decorated with the package name"""
        return uml_simple_box(self, **kwargs)

    def __uml(self, show_base=True, show_properties=True, show_linked=True, omit_attributes=[], show_inherited=False,
              **kwargs):
        """ Create a typical UML node shape, including linked and base classes as
        requested, and omitting attributes in the list """
        if self._osl.type == 'class':
            if show_inherited:
                show_inherited = self._osl.inherited_properties
            return uml_class_box_label(self, show_base, show_properties, show_linked, omit_attributes, show_inherited)
        else:
            return uml_enum_box_label(self, **kwargs)


class UMLFactory(Factory):
    Factory.register(Ontology(UmlBase))


class TestUMLFactory(unittest.TestCase):

    def test_experiment(self):

        """ Test that we can build a klass, and that it has the correct typekey
        (i.e. it's come from the ontology), and that it has one of the new
        attributes (i.e. it is a proper subclass)."""

        e = UMLFactory.build('designing.numerical_experiment')
        assert e._osl.type_key == 'cim.designing.numerical_experiment'
        assert e.label() == 'numerical\nexperiment'


if __name__=="__main__":
    unittest.main()
