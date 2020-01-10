import unittest
from pyosl import Factory
from pyosl.tools import named_build, calendar_period, osl_fill_from, online, numeric_value, get_reference_for, \
    new_document, conditional_copy

NORMAL='Normal Nodes'
HIGH='High Memory Nodes'
NORMAL_N, HIGH_N = 4544, 376
CPU_TYPE = 'Ivy Bridge'


def make_examples():
    """ Make some examples for testing."""

    # now build some class instances
    highmem_nodes = named_build('platform.compute_pool', HIGH)
    normal_nodes = named_build('platform.compute_pool', NORMAL)

    # flesh out some of the class instances using copy
    highmem_nodes.compute_cores_per_node = 24
    highmem_nodes.cpu_type = CPU_TYPE
    highmem_nodes.memory_per_node = numeric_value(128., 'GB')
    highmem_nodes.number_of_nodes = HIGH_N
    highmem_nodes.model_number = 'E5-2697 v2'
    highmem_nodes.clock_speed = numeric_value(2.7,'GHz')
    normal_nodes.memory_per_node = numeric_value(64., 'GB')
    normal_nodes.number_of_nodes = NORMAL_N
    return normal_nodes, highmem_nodes


class TestTools(unittest.TestCase):

    def setUp(self):
        self.n, self.h = make_examples()

    def test_conditional_copy_new(self):
        """ test we create the correct attribute when it doesn't exist"""
        conditional_copy(self.h, self.n, 'cpu_type')
        self.assertEqual(self.n.cpu_type, CPU_TYPE)

    def test_conditional_copy_avoid(self):
        """ test we don't overwrite something already defined"""
        conditional_copy(self.h, self.n, 'name')
        self.assertEqual(self.n.name, NORMAL)
        self.assertEqual(self.h.name, HIGH)

    def test_osl_fill_from_copy(self):
        """ Test the fill from example"""
        osl_fill_from(self.n, self.h)
        self.assertEqual(self.n.cpu_type, self.h.cpu_type)
        self.assertEqual(self.n.name, NORMAL)
        self.assertEqual(self.h.name, HIGH)
        self.assertEqual(self.n.number_of_nodes, NORMAL_N)
        self.assertEqual(self.h.number_of_nodes, HIGH_N)

    def test_period(self):
        period = calendar_period('2013-11-01', '2020-01-16')
        print(period)

if __name__ == "__main__":
    unittest.main()
