from pyosl.tools import Triples
from pyosl.tools import NAMESPACE
import pygraphviz as pgv
import uuid


class TriplesDelux(Triples):
    """ A class to do more than just create and list PYOSL triples """
    # Sits in uml so that the wider dependencies can be avoided if the functionality is not needed.

    def __init__(self, *args, **kwargs):
        """ Initialise with superclass (Triples) arguments"""
        super().__init__(*args, **kwargs)
        self.initial_graph_properties = {'rankdir':'LR'}

    def __getnode(self, n, relationship=None):
        """ Get a node from graph, or add a node if necessary"""
        n = str(n)

        # For resources, make shape rectangles.
        # For esdoc literals, make shape ellipse.

        if n.startswith(NAMESPACE):
            n = n[len(NAMESPACE):]

        # First deal with python literals.
        # Make shape ellipse dotted
        literal_trigger = '^^http://www.w3.org'
        nfind = n.find(literal_trigger)
        if nfind != -1 or relationship in ['rdf:type',  'rdf:parseType']:
            # Make sure it's a new node, don't reuse.
            u = uuid.uuid4()
            if nfind != -1:
                label = n[0:n.find(literal_trigger)]
            else:
                label = n
            self.G.add_node(u, label=label, shape='ellipse', style='dotted')
            return self.G.get_node(u)

        # Blank nodes should be blank
        if n.startswith('_:'):
            self.G.add_node(n, label='', shape='ellipse')
            return self.G.get_node(n)

        if self.G.has_node(n):
            return self.G.get_node(n)
        else:
            self.G.add_node(n, shape='ellipse')
            return self.G.get_node(n)

    def __build(self):
        self.G = pgv.AGraph(**self.initial_graph_properties)
        for a, b, c in self.triples:
            an = self.__getnode(a)
            cn = self.__getnode(c, b)
            print(f'Adding {a}({an}) {b} {c}({cn})')
            if b == 'rdf:parseType' and c == 'resource':
                an.attr['shape'] = 'rectangle'
            try:
                self.G.get_edge(an, cn, str(b))
            except KeyError:
                self.G.add_edge(an, cn, str(b), label=str(b))

    def make_graph(self, dot_required=False, filename="triples.dot"):
        """ Generate dot file"""
        self.__build()
        if dot_required:
            self.G.write(filename)

    def make_pdf(self, filename="triples.pdf"):
        """ Generate PDF file """
        self.make_graph(dot_required=False)
        self.G.draw(filename, prog='dot')