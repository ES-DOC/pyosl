import unittest


class Property:
    """ Simple property """
    def __init__(self, value=None):
        print('initialising property')
        self.value = value


class Descriptor:
    """
    Toy Descriptor showing how we use the instance dict to park the property, which
    in the real deal, will hold all the validation magic.
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


class Foo(list):
    x = Descriptor('x')
    y = Descriptor('y')


class TestBasic(unittest.TestCase):

    def test_simple(self):
        g = Foo()
        f = Foo()
        f.x = 6
        f.x = 5
        g.y = 6
        assert f.x == 5
        assert g.x == None
        assert f.x * g.y == 30

    def test_listiness(self):
        g = Foo()
        g.append(1)
        print(g)


if __name__ == "__main__":
    unittest.main()
