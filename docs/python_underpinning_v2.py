import unittest


class Property:
    """ Simple property """
    def __init__(self, value=None):
        """
        We use properties to do type and cardinality checking according to the UML definition.
        :param value: an initial value if there is one when the property is set up.
        In real life there are useful __get and __set methods.
        """
        self.__value = value

    def getx(self):
        return self.__value

    def setx(self, x):
        self.__value = x

    def delx(self):
        print ('deleted')

    value = property(getx, setx, delx)


class Descriptor:
    """
    Toy Descriptor showing how we use the instance dict to park the property, which
    in the real deal, will hold all the validation magic. The thing we are trying
    to do here is ensure that the properties are on instance attributes, not
    class attributes.
    """

    def __init__(self, label):
        self.label = label

    def __get__(self, instance, owner):
        print('__get__ toy', instance, owner)
        p = instance.__dict__.get(self.label, Property())
        return p.value

    def __set__(self, instance, value):
        print('__set__ toy ')
        instance.__dict__[self.label] = Property(value)

    def __delete__(self, instance):
        print ('delete')


class Foo(list):
    """ A toy, unhashable, class with a couple of static descriptors on the class."""
    x = Descriptor('x')
    y = Descriptor('y')


class TestBasic(unittest.TestCase):

    def test_simple(self):
        """ Test that assignments work, and that the classes don't interact"""
        g = Foo()
        f = Foo()
        f.x = 6
        f.x = 5
        g.y = 6
        assert f.x == 5
        assert g.x == None
        assert f.x * g.y == 30
        help(f.x)

    def test_listiness(self):
        """ Make sure it still behaves like a list, although in real life
        we handle lists a little differently."""
        g = Foo()
        g.append(1)
        assert g[0] == 1

    def test_delete(self):
        g = Foo()
        g.x = 5
        del (g.x)


if __name__ == "__main__":
    unittest.main()
