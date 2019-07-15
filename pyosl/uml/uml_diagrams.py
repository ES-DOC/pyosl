import math
import pygraphviz as pgv
from copy import copy

from .uml_utils import PackageColour
from .uml_base  import UmlBase

from ..factory import Factory


class BasicUML:

    """ Draws a basic UML diagram for the chosen set of classes """

    def __init__(self, filestem, option='uml', **kwargs):

        """ Set up with output filename, and any default graph properties"""

        assert Factory.ontology.BaseClass == UmlBase

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
        self.hidden_properties={}

        self.singleton_width = 4
        self.bottom_nodes = []

        initial_graph_properties = {
            'strict': False,
            'splines': True,
            'fontsize': 8,
            'directed': True,
            'ranksep': 0.3,
            }

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
                            show_base_links=True, omit_classes=[]):
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
                self.classes2view[c] = Factory.build(c)
        self.allup = copy(self.classes2view)

        # find all the extra ones that are in the properties of the ones we
        # asked for
        if expand_associated or expand_base:
            for c in self.classes2view:
                associated = self.__find_associated_classes(self.classes2view[c],
                                                            associations=expand_associated,
                                                            bases=expand_base)
                for k, v in associated.items():
                    if k not in self.allup and k not in Factory.ontology.builtins:
                        self.allup[k] = v

        # Now remove anything we don't want to see
        for c in omit_classes:
            if c in self.allup:
                del self.allup[c]
            else:
                print('%%Warning - omit_classes list includes one not found - ',c)

        self.__find_class_edges(show_links=show_base_links)

    def set_visible_package(self, package, omit_classes=[], restrict=False, show_base_links=True):
        """" Choose all classes from one package. By default this will
        also include any base classes from other packages, and any
        classes from other packages which are properties. These
        can be removed in one go, using restrict=True, or handled
        individually via omit_classes."""

        packages = Factory.ontology.get_package_contents(package)
        kw = {}
        if restrict:
            kw = {'expand_associated': False, 'expand_base': False}
        self.set_visible_classes(packages, omit_classes=omit_classes, show_base_links=show_base_links, **kw)


    def set_association_edges(self, multiline=False):

        """Find the associations internal to a set of classes
        and pull them out of the labels"""

        self.multiline = multiline

        for c in self.allup:
            if hasattr(self.allup[c]._osl, 'properties'):
                self.hidden_properties[c] = self.__get_hidden_properties(c, add_edges=True)

    def __get_hidden_properties(self, c, add_edges=True):
        """ Get properties to hide (because they exist as
        links on the diagram, and add edges if appropriate.
        """
        hidden_properties=[]
        for p in self.allup[c]._osl.properties:
            target = p[1]
            if target.startswith('linked_to'):
                target = target[10:-1]
            if target in self.allup:
                if add_edges:
                    self.associations.append(target)
                    self.assoc_edges.append(
                        (c, target, p[0], p[2]))
                hidden_properties.append(p[0])
        return hidden_properties


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

    def generate_dot(self, dot_out_please=False):
        """ Generate the actual dot file """

        self.__add_nodes()
        self.__add_edges()
        self.__fix_layout()

        if dot_out_please:
            self.G.write('{}.dot'.format(self.filestem))

    def generate_pdf(self, dot_out_please=False):

        """ Generates the output PDF file """

        self.generate_dot(dot_out_please)
        self.G.draw('{}.pdf'.format(self.filestem), prog='dot')

    def __find_associated_classes(self, klass, associations=True, bases =True):

        """ For a given class, find all the associated classes,
        possibly including base classes, but not all hierarchy """

        extras = {}

        if hasattr(klass, '_osl'):
            meta = klass._osl
            if associations:
                if hasattr(meta, 'properties'):
                    candidates = [p[1] for p in meta.properties]
                    for candidate in candidates:
                        if candidate.startswith('linked_to'):
                            candidate = candidate[10:-1]
                        if candidate not in extras:
                            k = Factory.build(candidate)
                            extras[candidate] = k

            if bases and hasattr(meta, 'base'):
                if meta.base:
                    if meta.base not in extras:
                        extras[meta.base] = Factory.build(meta.base)

        return extras

    def __find_class_edges(self, show_links=True):

        """Now parse the classes we've got, and if show_links
        and they have baseclasses in the set to be shown, collect the edges
        and remove the baseclass decoration (via baseControl)
        """

        topset = {}

        # Now set the default for base class visibilty in the label
        # We set these false for a subclass when there is an edge to the superclass
        def base_visible(k):
            if not show_links: return True
            if hasattr(k._osl, 'base'):
                return not k._osl.base in self.allup
            return True

        self.baseControl = {k: base_visible(v) for k, v in self.allup.items()}

        if show_links:
            for c in self.allup:
                if hasattr(self.allup[c]._osl,'base'):
                    if self.allup[c]._osl.base:
                        # we only care about the first one
                        if self.allup[c]._osl.base in self.allup:
                            self.class_edges.append((self.allup[c]._osl.base, c))

        # now we have to do something about ranking
        # otherwise we're all at sea.
        # so at this point, we'll get information for grapher
        # first parse, get all the top classes

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

        packages = Factory.ontology.constructors.keys()
        contents = {p: Factory.ontology.get_package_contents(p) for p in packages}
        picker = PackageColour(contents)

        for c in self.allup:

            if c in self.hidden_properties:
                hidden_properties = self.hidden_properties[c]
            else:
                hidden_properties = []

            inherited = []
            if self.baseControl[c]:
                # the base is not directly linked ...
                if self.allup[c]._osl.base not in self.allup:
                    # It's not on the diagram either, so
                    # we should show inherited properties that
                    # are not otherwise present as links.
                    # start by just showing them ...
                    # FIXME, remove properties for any links present
                    inherited = self.allup[c]._osl.inherited_properties

            label = self.allup[c].label(option=self.viewing_option,
                                        omit_attributes=hidden_properties,
                                        show_inherited=inherited,
                                        show_base=self.baseControl[c])
            self.G.add_node(c, label=label)
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
                edge_key = 'edge_{}'.format(eindex)
                edge_key = None
                # we can't currently use edge keys, see https://github.com/pygraphviz/pygraphviz/issues/162
                if composition:
                    self.G.add_edge(e, f, edge_key, label=edge_label, headlabel=edge_head_label,
                               labeldistance=2.2, labelfloat=False, labelangle=45., arrowtail='diamond',
                               arrowhead='vee', dir='both', headport=headport, tailport=tailport)
                else:
                    self.G.add_edge(e, f, edge_key, label=edge_label, headlabel=edge_head_label,
                               labeldistance=2.2, labelfloat=False, labelangle=30., arrowhead='vee',
                               headport=headport, tailport=tailport)
                # edge_head_label = ' %s\n%s' % (m, g)
                # G.add_edge(e, f, 'named%s'%str(eindex), headlabel=edge_head_label)
                #print(edge_key, e, f, edge_label.replace('\n', ' '))
                #print(len(self.G.edges(keys=True)))

        # now the invisible edges, if any:
        for e, f in self.invisible_edges:
            if e not in self.allup:
                self.G.add_node(e, label='', shape='none')
            if f not in self.allup:
                self.G.add_node(f, label='', shape='none')
            self.G.add_edge(e, f, style='invis')

    def fix_layout(self, nwidth, bottom_nodes=[]):

        """ Fix layout by putting singletons at the bottom using nxwidth to
          put them in a grid. This assumes that "the bottom" is defined
          by bottom_nodes provided by the user. Some future version
          might be able to calculate them."""

        if not bottom_nodes:
            return NotImplementedError

        self.bottom_nodes = bottom_nodes
        self.singleton_width = nwidth


    def __fix_layout(self):
        """ Implements the fix_layouts after the rest of the graph is
        drawn so that the singletons can be identifed."""

        def add_ranks(nodes, bottom, width=4):

            """ Take as set of nodes which would otherwise be singletons at the top
            and arrange them at the bottom of the graph """

            # no point constraining to less than the existing bottom width
            width = max(len(bottom), width)

            done = 0
            for node in nodes:
                for bn in bottom:
                    self.G.add_edge(bn, node, style='invis')
                    print('Adding singleton edge', bn, node)
                done += 1
                if done >= width:
                    bottom = nodes[done-width:done-1]

        # Handle layouts drifting too wide
        # All we can really do automatically is find singletons
        # and move them to the bottom - if the user has
        # told us where the bottom is.

        singletons = []
        for n in self.G.nodes():
            successors = self.G.successors(n)
            predecessors = self.G.predecessors(n)
            if len(predecessors) == 0 and len(successors) == 0:
                singletons.append(n)

        if singletons:
            try:
                bottom_nodes = [self.G.get_node(n) for n in self.bottom_nodes]
            except KeyError as e:
                raise ValueError(e)
            add_ranks(singletons, bottom_nodes, self.singleton_width)
