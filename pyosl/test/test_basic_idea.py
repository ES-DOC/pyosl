import unittest

from pyosl import PropertyDescriptor, Property


def square():
    """ Square class definition"""
    return {'name':'square','properties':[('side_length','int','1.1','length of side'),]}


def circle():
    """ Circle class definition"""
    return {'name': 'circle','properties':[('radius','int','1.1','circle radius'),]}


class Base:
    """ A base class to provide the core interface"""
    def __init__(self):
        self.ontology = 'toy test ontology'


class Ontology:
    """ Provides the ontology to the factory"""
    def __init__(self):
        self.available = {'square': square(), 'circle': circle()}


def cheap_validator(value, target):
    """ Checks that value is of type target.
    This validator only knows about integers and strings, for this toy example.
    """
    try:
        return isinstance(value, {'int':int, 'str': str}[target])
    except KeyError:
        print(f'Cheap validator ignores {target}')
        raise



class Factory:
    """ The factory for building classes and providing class instances"""

    ontology = Ontology()
    known_classes = {}

    @staticmethod
    def build(klass):
        """ Provide a class instance to a client"""
        if klass not in Factory.known_classes:
            if klass in Factory.ontology.available:
                newclass = Factory._build(klass)
                Factory.known_classes[klass] = newclass
            else:
                raise ValueError(f"Factory doesn't know about {klass}")
        candidate = Factory.known_classes[klass]()

        return candidate

    def _build(klass):
        """ Builds a class definition for the factory"""
        properties = Factory.ontology.available[klass]
        newclass = type(klass, (Base,), {'name':properties['name'],'_osl':properties,'__doc__':'my doc string'})
        for p in properties['properties']:
            setattr(newclass, p[0], PropertyDescriptor(p))
        return newclass


class TestCase(unittest.TestCase):

    def setUp(self):
        """ Build me a couple of square instances to play with"""
        # if we don't set a validator to the property, the
        # mechanism just passes anything as allowable.
        Property.set_validator(cheap_validator)
        self.s = Factory.build('square')
        self.s2 = Factory.build('square')

    def test_structure(self):
        """ Make sure the class instances respect the structure and properties"""
        assert self.s.name == 'square'
        self.s.side_length = 1
        with self.assertRaises(ValueError):
            # the property definition says it has to be an integer
            self.s.side_length = 'one'
            print(self.s.side_length)

    def test_class_isolation(self):
        """ Make sure our properties are bound to instances not the classes"""
        self.s.side_length = 1
        self.s2.side_length = 2
        assert self.s.side_length == 1
        assert self.s2.side_length == 2

    def test_docstring(self):
        assert self.s.__doc__=='my doc string'
        self.s.__doc__


if __name__ == "__main__":
   unittest.main()
