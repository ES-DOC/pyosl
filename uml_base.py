from pyosl.factory import Ontology, OntoBase
from pyosl.uml_utils import uml_bubble, uml_simple_box, uml_enum_box_label, uml_class_box_label
import unittest

#
# TODO: Really the UMLFactory could be subsumed into justing Ontology initialising with
# with the UMLBase class ...
#


class UmlBase(OntoBase):

    def label(self, option='bubble', **kwargs):
        if option == 'name_only':
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
        if self.type == 'class':
            if show_inherited:
                show_inherited = []
                for b in self.base_hierarchy:
                    base = UMLFactory.build(b)
                    show_inherited += base.properties
            return uml_class_box_label(self, show_base, show_properties, show_linked, omit_attributes, show_inherited)
        else:
            return uml_enum_box_label(self, **kwargs)


class UMLFactory:

    known_subclasses = {}
    ontology = Ontology(UmlBase)

    @staticmethod
    def build(klass_name, *args, **kwargs):

        if klass_name in UMLFactory.ontology.builtins:
            return UMLFactory.ontology.builtins[klass_name]

        if klass_name not in UMLFactory.known_subclasses:

            if klass_name not in UMLFactory.ontology.klasses:
                raise ValueError('Unknown class "{}" requested from {} Ontology'.format(
                    klass_name, UMLFactory.ontology.name))

            klass = type(klass_name, (UMLFactory.ontology.klasses[klass_name],),{})
            UMLFactory.known_subclasses[klass_name] = klass

        return UMLFactory.known_subclasses[klass_name](*args, **kwargs)


class TestUMLFactory(unittest.TestCase):

    def test_experiment(self):

        e = UMLFactory.build('designing.numerical_experiment')
        assert e.type_key == 'cim.designing.numerical_experiment'

    def test_int(self):
        i = UMLFactory.build('int')
        y = i()



if __name__=="__main__":
    unittest.main()
