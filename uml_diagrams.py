import math
import pygraphviz as pgv
from pyosl.uml_utils import PackageColour
from pyosl.uml_base import UMLFactory
from copy import copy
import unittest


class BasicUML:

    """ Draws a basic UML diagram for the chosen set of classes """

    def __init__(self, filestem, option='uml', **kwargs):

        """ Set up with output filename, and any default graph properties"""

        self.filestem = filestem
        self.viewing_option = option

        # nodes
        self.classes2view = {}
        self.allup = {}

        # edges (between class and base class, and regular associations)
        self.class_edges = []
        self.assoc_edges = []
        self.associations = []

        # use this to understand whether we are showing bases for a given class
        self.baseControl = {}

        # layout related
        self.invisible_edges = []
        self.fixed_ports = {}
        self.multiline = False
        self.enum_definitions = False
        self.default_node_attributes = []
        self.topset = {}
        self.multiline = False
        self.baseControl={}

        initial_graph_properties = {
            'splines': True,
            'fontsize': 8,
            'directed': True,
            'ranksep': 0.3}

        for k in kwargs:
            initial_graph_properties[k] = kwargs[k]

        if option == 'uml':
            self.default_node_attributes = {'shape':'plain'}
        elif option == 'name_only':
            self.default_node_attributes = {'shape': 'ellipse', 'style': 'filled'}
        elif option == 'box':
            self.default_node_attributes = {'shape': 'box'}

        self.G = pgv.AGraph(**initial_graph_properties)

    def set_visible_classes(self, classes2view, expand_associated=True, expand_base=True,
                            omit_classes=[]):
        """
        :param classes2view: A list of classes to be shown in the diagram
        :param expand_associated: Boolean. If True, find all classes referred
        to any class selected, and add that to the ones to be shown.
        Default is True.
        :return: None
        """

        # use a dictionary of class instances keyed by class name
        for c in classes2view:
            if c not in omit_classes:
                self.classes2view[c] = UMLFactory.build(c)
        self.allup = copy(self.classes2view)

        # find all the extra ones that are in the properties of the ones we
        # asked for
        if expand_associated:
            for c in self.classes2view:
                associated = self.__find_associated_classes(self.classes2view[c], expand_base=expand_base)
                for k, v in associated.items():
                    if k not in self.allup:
                        self.allup[k] = v
                        print('..adding {} for {}'.format(k,c))

        # Now remove anything we don't want to see
        for c in omit_classes:
            if c in self.allup:
                del self.allup[c]
            else:
                print('%%Warning - omit_classes list includes one not found - ',c)

        # Now set the default for base class visibilty in the label
        # We set these false for a subclass when there is an edge to the superclass
        self.baseControl = {k:True for k,v in self.allup.items()}

        print('removal')
        print(self.classes2view.keys())
        print(self.allup.keys())

        self.__find_class_edges()

    def set_visible_package(self, package, omit_classes=[]):
        """" Choose all classes from one package"""

        packages = UMLFactory.ontology.get_package_contents(package)
        self.set_visible_classes(packages, omit_classes=omit_classes)


    def set_association_edges(self, multiline=False):

        """Find the associations internal to a set of classes
        and pull them out of the labels"""

        self.multiline = multiline

        for c in self.allup:
            if hasattr(self.allup[c]._osl, 'properties'):
                for p in self.allup[c]._osl.properties:
                    target = p[1]
                    if target.startswith('linked_to'):
                        target = target[10:-1]
                    if target in self.allup:
                        self.associations.append(str(p[1]))
                        self.assoc_edges.append(
                            (c, target, p[0], p[2]))

    def direct_edge_ports(self, edges):

        """ Adds direct control over the position of a particular edge, or edges, to control situations where
        the defaults don't do the business.
        :param edges: A list of tuples of the form [(source, destination, relationship, source_port, destination_port)...]
        """
        for s, d, r, sp, dp in edges:
            assert s in self.allup, "Missing source class"
            assert d in self.allup, "Missing destination class"
            self.fixed_ports[(s, d, r)] = s, d, r, sp, dp

    def direct_layout(self, relationships):
        """ Adds direct control over the layout by providing a set of invisible edge relationships
        that can be used to provide additional control over layout. Primarily used for manually adjusting
        layouts that are too wide. Typically called last before generation.
        :param relationships: A list of tuples of the form [(higherclass, lowerclass), (lowerclass, bottomclass) ...]
        """

        self.invisible_edges = relationships

    def generate_dot(self, label_type='uml', nwidth=0):
        """ Generate the actual dot file """

        self.__add_nodes()
        self.__add_edges()
        self.__fix_layout(nwidth)
        self.G.write('{}.dot'.format(self.filestem))

    def generate_pdf(self):

        """ Generates the output PDF file """

        self.generate_dot()
        self.G.draw('{}.pdf'.format(self.filestem),prog='dot')

    def __find_associated_classes(self, klass, expand_base=True):

        """ For a given class, find all the associated classes,
        possibly including base classes, but not all hierarchy """

        extras = {}

        if hasattr(klass, '_osl'):
            meta = klass._osl
            if hasattr(meta, 'properties'):
                candidates = [p[1] for p in meta.properties]
                for candidate in candidates:
                    if candidate.startswith('linked_to'):
                        candidate = candidate[10:-1]
                    k = UMLFactory.build(candidate)
                    if hasattr(k,'_osl'):
                        if k not in extras:
                            extras[candidate] = k

            if expand_base and hasattr(meta, 'base'):
                if meta.base:
                    if meta.base not in extras:
                        extras[meta.base] = UMLFactory.build(meta.base)

        return extras

    def __find_class_edges(self):

        """Now parse the classes we've got, and if they have
        baseclasses in the set to be shown, collect the edges
        and remove the baseclass decoration (via baseControl)"""

        # baseControl is initialised as True for all classes
        for c in self.allup:
            if self.allup[c]._osl.type == 'enum':
                continue
            if self.allup[c]._osl.base:
                # we only care about the first one
                if self.allup[c]._osl.base in self.allup:
                    self.baseControl[c] = False
                    self.class_edges.append((self.allup[c]._osl.base, c))


        # now we have to do something about ranking
        # otherwise we're all at sea.
        # so at this point, we'll get information for grapher
        # first parse, get all the top classes

        topset = {}
        for e, f in self.class_edges:
            if f in topset: del topset[f]
            if e not in topset: topset[e] = {'n': 0, 'u': 0}
        # second parse, count number of children
        for e, f in self.class_edges:
            if e in topset:
                topset[e]['n'] += 1
        self.topset = topset

    def __add_nodes(self):

        """ Adds all the nodes that are currently in the allup list of classes
        to the plot. Called as part of generating the final dot file."""

        packages = UMLFactory.ontology.constructors.keys()
        contents = {p: UMLFactory.ontology.get_package_contents(p) for p in packages}
        picker = PackageColour(contents)

        for c in self.allup:

            self.G.add_node(c, label=self.allup[c].label(option=self.viewing_option, show_base=self.baseControl[c]))
            node = self.G.get_node(c)
            for a in self.default_node_attributes:
                node.attr[a] = self.default_node_attributes[a]
            if self.viewing_option == "bubble":
                if self.allup[c]._osl.type == 'enum':
                    node.attr['shape'] = "tab"
                node.attr['fillcolor'] = picker.colourise(c)


    def __add_edges(self):

        """ Draws all the currently understood edges """

        for e, f in self.class_edges:
            if e in self.allup and f in self.allup:
                self.G.add_edge(e, f, dir='back', arrowtail='empty')

        # We'd better deal with labeled association edges:
        if self.associations:
            # dealing with: c, target, name, cardinality
            eindex = 0
            for e, f, g, m in self.assoc_edges:
                eindex += 1
                # is this a fixed port?
                if (e, f, g) in self.fixed_ports:
                    port_constraint = self.fixed_ports[(e, f, g)]
                    headport = port_constraint[4]
                    tailport = port_constraint[3]
                else:
                    headport = 'c'
                    tailport = 'c'
                if self.multiline:
                    edge_label = ' {}\n({})'.format(g.replace('_', '\n '), m)
                    edge_head_label = ''
                else:
                    edge_label = ' %s ' % g
                    edge_head_label = '  %s   ' % m
                # add extra spacing to avoid labels overlapping lines

                composition = self.allup[f]._osl.is_document
                # if self.multiline:
                #    edge_label = '<<table cellpadding="10" border="0"><tr><td>%s</td></tr></table>>' % g.replace('\n','<br/>')
                # attempt to find a likely distance at which cardinality labels don't overlap edges
                # using distance and angle
                # distance, angle = 3., 30.
                if composition:
                    self.G.add_edge(e, f, 'named%s' % str(eindex), label=edge_label, headlabel=edge_head_label,
                               labeldistance=2.2, labelfloat=False, labelangle=45., arrowtail='diamond',
                               arrowhead='vee', dir='both', headport=headport, tailport=tailport)
                else:
                    self.G.add_edge(e, f, 'named%s' % str(eindex), label=edge_label, headlabel=edge_head_label,
                               labeldistance=2.2, labelfloat=False, labelangle=30., arrowhead='vee',
                               headport=headport, tailport=tailport)
                # edge_head_label = ' %s\n%s' % (m, g)
                # G.add_edge(e, f, 'named%s'%str(eindex), headlabel=edge_head_label)

        # now the invisible edges, if any:
        for e, f in self.invisible_edges:
            if e not in self.allup:
                self.G.add_node(e, label='', shape='none')
            if f not in self.allup:
                self.G.add_node(f, label='', shape='none')
            self.G.add_edge(e, f, style='invis')

    def __fix_layout(self, nwidth):

        """ Fix other aspects of the layout """

        def __add_ranks(nodes, width=4):
            """ Take as set of nodes which would otherwise have the same row rank
            on the graph and add some invisible edges to make them flow down the
            page rather than across the page """
            stride = int(math.ceil(len(nodes) / float(width)))
            rank = nodes[0:width]
            for row in range(1, stride):
                si = row * width
                ei = min(si + width, len(nodes))
                under = nodes[si:ei]
                for i in range(len(under)):
                    self.G.add_edge(rank[i], under[i], style='invis')
                rank = under

        # handle layouts drifting too wide
        if nwidth !=0:
            singletons = []
            for n in self.G.nodes():
                successors = self.G.successors(n)
                predecessors = self.G.predecessors(n)
                if len(predecessors) <= 1 and len(successors) > nwidth:
                    fix_edges = []
                    for nn in successors:
                        ns = self.G.successors(nn)
                        if ns == 0:
                            fix_edges.append(nn)
                    __add_ranks(successors, nwidth)
                elif len(predecessors) == 0 and len(successors) == 0:
                    singletons.append(n)

            if len(singletons) > nwidth:
                __add_ranks(singletons, nwidth)


class PackageUML:
    """ provides view of entire ontology and individual package lists"""

    def __init__(self):
        raise NotImplementedError

    def set_packages(self, package_list=None):
        if package_list is None:
            package_list = UMLFactory.ontology.constructors.keys()
        raise NotImplementedError

    def generate_pdf(self):
        raise NotImplementedError


class TestGraphCases(unittest.TestCase):

    def test_makediagrams(self):
        """ Simply makes activity diagrams """
        d = BasicUML('test_output/testing', option='bubble')
        d.set_visible_classes(['designing.numerical_experiment', ], expand_base=False)
        d.set_association_edges(multiline=True)
        d.generate_pdf()
        # TODO currently not showing multiple links that exist ... only showing one if to the same target
        #  in this case governing mips and related mips

    def test_makediagrams_and_omit(self):
        """ Simply makes activity diagrams """
        d = BasicUML('test_output/testing1', option='uml')
        d.set_visible_classes(['designing.numerical_experiment', ], expand_base=False, omit_classes=['designing.project',])
        d.set_association_edges(multiline=True)
        d.generate_pdf()
        # TODO currently not showing multiple links that exist ... only showing one if to the same target
        #  in this case governing mips and related mips

    def test_makediagrams_and_omit_BOX(self):
        """ Simply makes activity diagrams """
        d = BasicUML('test_output/testing3', option='box')
        d.set_visible_classes(['designing.numerical_experiment', ], expand_base=False, omit_classes=['designing.project',])
        d.set_association_edges(multiline=True)
        d.generate_pdf()
        # TODO currently not showing multiple links that exist ... only showing one if to the same target
        #  in this case governing mips and related mips


    def test_explain_requirements(makedot=False):
        """ A diagram to explain numerical requirements. Exercises direct_layout and direct_edge_ports"""
        d = BasicUML('test_output/testing2', option='bubble')
        d.set_visible_package('designing',
                              omit_classes=['activity.axis_member', 'designing.project', 'activity.activity',
                                            'designing.numerical_experiment', 'designing.simulation_plan',
                                            'designing.experimental_relationships',
                                            ])
        d.direct_layout([('designing.numerical_requirement', 'Hidden'),
                         ('Hidden', 'designing.initialisation_requirement'),
                         ('designing.initialisation_requirement', 'designing.output_requirement'),
                         ('Hidden', 'designing.domain_requirements'),
                         ('Hidden', 'designing.temporal_constraint'),
                         ('designing.multi_ensemble', 'designing.start_date_ensemble'),
                         ('Hidden', 'designing.forcing_constraint')])
        d.direct_edge_ports([('designing.numerical_requirement', 'designing.numerical_requirement', 'additional_requirements', 'nw', 'ne'), ])
        d.set_association_edges(multiline=True)
        d.generate_pdf()

class TestPackages(unittest.TestCase):

    def test_packages(self):
        d = PackageUML()
        d.set_packages()
        d.generate_pdf()


if __name__ == "__main__":
    unittest.main()
