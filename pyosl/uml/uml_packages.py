from jinja2 import Template
import pygraphviz as pgv

from ..factory import Factory


def package_label(package_name, package_contents):

    template = """<<TABLE BGCOLOR="{{bg_col}}" BORDER="0" CELLBORDER="0" CELLSPACING="0">
       <TR><TD ALIGN="CENTER" BGCOLOR="{{hdr_col}}" COLSPAN="2">
       <FONT FACE="Helvetica Bold" COLOR="white">{{name}}</FONT></TD></TR>
       {% for t,k in contents %}<TR><TD>{% if t=="class" %}C{% else %}E{% endif %}</TD><TD ALIGN="left">{{k}}</TD></TR>
       {% endfor %}</TABLE>>"""

    t = Template(template)
    bg_col = 'white'
    hdr_col = 'black'
    contents = [(package_contents[k]['type'], k.split('.')[1].replace('_',' ')) for k in package_contents]
    label = t.render(name=package_name, contents=contents, bg_col=bg_col, hdr_col=hdr_col)

    return label

class PackageUML:
    """ provides view of entire ontology and individual package lists"""

    def __init__(self, filestem, package_dict=None):

        """ Initialise with a dictionary of packages with classes and enums.
        If none is provided, the default facteory is used."""

        self.filestem = filestem

        if package_dict is None:
            self.package_dict = Factory.ontology.constructors
        else:
            self.package_dict = package_dict

        initial_graph_properties = {
            'splines': True,
            'fontsize': 8,
            'directed': True,
            'ranksep': 0.3}

        self.G = pgv.AGraph(**initial_graph_properties)

    def generate_pdf(self, autolayout=True):

        self.lengths = [(len(items), p) for p, items in self.package_dict.items()]
        self.lengths.sort(key=lambda x: x[0], reverse=True)

        for l, p in self.lengths:
            items = self.package_dict[p]
            self.G.add_node(p, label=package_label(p, items), shape='tab')

        if autolayout:
            self.__autolayout()

        self.G.write('{}.dot'.format(self.filestem))
        self.G.draw('{}.pdf'.format(self.filestem), prog='dot')


    def __autolayout(self):
        """ Adds invisible edges to control layout"""

        n_lengths = len(self.lengths)

        if not n_lengths % 2:
            # pair up
            for i in range(int(n_lengths/2)):
                self.G.add_edge(self.lengths[i][1], self.lengths[n_lengths-1-i][1], style='invis')
        else:
            # use the first one, and pair up the rest
            for i in range(int(n_lengths / 2)):
                print(self.lengths[i+1][1], self.lengths[n_lengths-i-1][1])
                self.G.add_edge(self.lengths[i+1][1], self.lengths[n_lengths - 1 - i][1], style='invis')






