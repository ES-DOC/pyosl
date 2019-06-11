import re, textwrap
from jinja2 import Template


class PackageColour(object):
    """ Set of pastel colours and methods for colourising
    package classes.
    """
    def __init__(self, packages):
        """
        :param packages: list of packages to colour
        """
        self.palette = ['darkseagreen','palegoldenrod','lightsalmon','thistle',
                        'lightsteelblue','burlywood','lightgray','seashell',
                        'navajowhite3','powderblue']
#                       wheat', 'sandybrown', 'darkkhaki', 'aliceblue', 'seashell', 'plum1',
#                       'lightgoldenrodyellow', 'lightgrey', 'rosybrown', 'lightcyan']
        assert len(packages) <= len(self.palette), "Too many packages (%s) to colour" % len(packages)
        self.packages = packages
        self.colours = {}
        for i, p in enumerate(packages):
            self.colours[p] = self.palette[i]

    def colourise(self,klass):
        """ Given a klass return the appropriate package colour"""
        for p in self.colours:
            if klass in self.packages[p]:
                break
        return self.colours[p]


class Palette(object):
    """ Used to hold label colour palette """
    orig = (105, 139, 34), (238, 232, 170),   # olivedrab4, palegoldenrod
    brown = (139, 125, 107),  (238, 232, 170),  # bisque3, palegoldenrod
    purple = (162, 142, 188), (224, 216, 232)
    choices = ['abs','doc','def']

    def __htmlhex(self,rgb):

        #return str(b'#' + b16encode(bytes(rgb)))
        #return '#'+"".join(map(chr, rgb)).encode('hex')
        return "#%02x%02x%02x" % rgb

    def top(self, choice):
        """ Colour for top of choice """
        assert choice in self.choices
        return self.__htmlhex({'abs': self.purple[0],
                'doc': self.orig[0],
                'def': self.brown[0]}[choice])

    def main(self, choice):
        """ Colour for background of choice"""
        assert choice in self.choices
        return self.__htmlhex({'abs': self.purple[1],
                'doc': self.orig[1],
                'def': self.brown[1]}[choice])


def camel_split(c):
    """ Convenience method for shortening camel case names by adding line split
    :param c: A camel case name
    :return: Camels with line splits
    """
    words = re.findall('[A-Z][^A-Z]*', c)
    return '\n'.join(words)


def uml_bubble(klass, **kw):
    """
    :param klass: klass for which a bubble label is required
    :param kwargs: Ignored
    :return:
    """
    name = klass._osl.class_name.replace('_', ' ')
    words = textwrap.wrap(name, 12, break_long_words=False)
    return '\n'.join(words)


def uml_class_box_label(klass,
                        show_base=True,
                        show_properties=True,
                        show_linked_properties=True,
                        omit_attributes=[],
                        show_inheritance=[],
                        bw=True,
                        ):
    """ Provides an html label suitable for use in graphviz as a UML class box.
    If show_base then include the base class in the label (typically we wouldn't do that if there was
    an edge on the graph linking to the base class).
    """

    template = """<<TABLE BGCOLOR="{{bg_col}}" BORDER="1" CELLBORDER="0" CELLSPACING="0">
    {% if base %}<TR><TD ALIGN="right" BGCOLOR="{{hdr_col}}"><FONT FACE="Helvetica Italic" COLOR="{{hdr_fc}}">{{base}}</FONT></TD></TR>{% endif %}
    {% if is_abstract %} <TR><TD ALIGN="CENTER" BGCOLOR="{{hdr_col}}">
    <FONT FACE="Helvetica Bold" COLOR="white">&lt;&lt;abstract&gt;&gt;</FONT></TD></TR>{% endif %}
    <TR><TD ALIGN="CENTER" BORDER="1" SIDES="B" BGCOLOR="{{hdr_col}}">
    <FONT FACE="Helvetica Bold" COLOR="{{hdr_fc}}">{{ontology_class}}</FONT></TD></TR>
    {% if inherited %}<TR><TD ALIGN="center" CELLPADDING="2" BORDER="1" SIDES="T" >
    <FONT FACE="Times-Roman Italic" POINT-SIZE="10">inherited properties</FONT></TD></TR>
    {% for ip in inherited%}<TR><TD ALIGN="LEFT" CELLPADDING="2">{{ip}}</TD></TR>{% endfor %} {% endif %}
    {% if properties and inherited %}<TR><TD ALIGN="center" CELLPADDING="2" BORDER="1" SIDES="T" >
    <FONT FACE="Times-Roman Italic" POINT-SIZE="10">properties</FONT></TD></TR>{% endif %}
    {% for p in properties %}<TR><TD ALIGN="LEFT" CELLPADDING="2">{{p}}</TD></TR>{% endfor %} 
    {% if constraints %}<TR><TD ALIGN="center" CELLPADDING="2" BORDER="1" SIDES="T" >
    <FONT FACE="Times-Roman Italic" POINT-SIZE="10">constraints</FONT></TD></TR>
    {% for c in constraints %}<TR><TD ALIGN="LEFT" CELLPADDING="2">{{c}}</TD></TR>{% endfor %}{% endif %}
    </TABLE>>"""

    def show(p):
        """ Accept a property for display, or not """
        if not show_properties:
            return False
        if not show_linked_properties and p[1].starts_with('linked'):
            return False
        if p[0] in omit_attributes:
            return False
        return True

    def fix(p):
        """ Deal with linked_to"""
        a, b, c, d = p
        if b.startswith('linked_to'):
            b = b[10:-1]
        return a, b, c

    properties = ['{}: {} &#91;{}&#93;'.format(*fix(p)) for p in klass._osl.properties if show(p)]

    palette = Palette()

    if klass._osl.is_abstract:
        colour_choice = 'abs'
    elif klass._osl.is_document:
        colour_choice = 'doc'
    else:
        colour_choice = 'def'

    bg_col = {0: palette.main(colour_choice), 1: 'white'}[bw]
    hdr_col = {0: palette.top(colour_choice), 1: 'black'}[bw]
    if show_base:
        base = klass._osl.base
    else:
        base = False
    hdr_fc = 'white'

    inherited = []
    if show_inheritance:
        inherited = ['{}: {} &#91;{}&#93;'.format(*fix(p)) for p in reversed(show_inheritance) if show(p)]

    constraints = []
    if hasattr(klass._osl, 'constraints'):
        for c in klass._osl.constraints:
            c = list(c)
            if c[1] == 'include':
                constraints.append(' {}: {{{}'.format(c[0], c[1]))
                for cc in c[2][0:-1]:
                    fmt1 = '      {}'
                    fmt2 = '      {}}}'
                    constraints.append(fmt1.format(cc))
                constraints.append(fmt2.format(c[2][-1]))
            else:
                actual_constraint = [str(b) for b in c[1:]]
                constraints.append(' %s: {%s}' % (c[0], '='.join(actual_constraint)))

    # if no properties and no constraints, add a blank line to make it look right
    if not properties and not constraints and not inherited:
        properties = [' ', ]

    t = Template(template)

    label = t.render(k=klass, ontology_class=klass._osl.class_name, is_abstract=klass._osl.is_abstract, bg_col=bg_col, hdr_col=hdr_col,
                     hdr_fc=hdr_fc, base=base, properties=properties, constraints=constraints, inherited=inherited)

    return label


def uml_simple_box(klass, package_font_size=10, left_pad=3, right_pad=3, **kw):

    """ Simple labeled box with package name in the corner.
    Extra keywords are ignored """

    #template = """<<font point-size="{{fontsize}}"><i>{{k.package_name}}</i></font><br align="right"/>
    #{% for w in words %}{{left}}{{w}}{{right}}<br align="center"/>{% endfor %}>"""

    #template = """<<TABLE BORDER="0" CELLBORDER="0" CELLPADDING="0" CELLSPACING="0">
    #<TR><TD ALIGN="RIGHT"><font point-size="{{fontsize}}"><i>{{k.package_name}}</i></font></TD></TR>
    #{% for w in words %}<TR><TD ALIGN="CENTER">{{left}}{{w}}{{right}}</TD></TR>\n{% endfor %}</TABLE>>"""

    template = """<<TABLE BORDER="0" CELLBORDER="0" CELLPADDING="0" CELLSPACING="0">
    #<TR><TD ALIGN="CENTER"><font point-size="{{fontsize}}">{{k._osl.package}}::</font></TD></TR>
    #{% for w in words %}<TR><TD ALIGN="CENTER">{{left}}{{w}}{{right}}</TD></TR>\n{% endfor %}</TABLE>>"""

    name = klass._osl.class_name.replace('_',' ')
    words = textwrap.wrap(name, 12, break_long_words=False)
    leftpad, rightpad = ''.join([' ' for i in range(left_pad)]), ''.join([' ' for i in range(right_pad)])

    t = Template(template)
    label = t.render(k=klass, fontsize=package_font_size, words=words, left=leftpad, right=rightpad)

    return label

def uml_enum_box_label(klass, with_definitions=False, definition_nchars=60, header_nchars=90, bw=True):

    """ Return an enum label, with definitions if approriate, and using
    definition_nchars for the width of the definitions, given header_nchars
    for the enum description definition."""

    template = """<<TABLE BGCOLOR="{{bg_col}}" BORDER="1" CELLBORDER="0" CELLSPACING="0">
    <TR><TD ALIGN="CENTER" BGCOLOR="{{hdr_col}}" {{colspan}}>
    <FONT FACE="Helvetica Bold" COLOR="white">{{k._osl.class_name}}</FONT></TD></TR>
    {% if definition %}<TR><TD COLSPAN="2" BORDER="1" SIDES="B" BALIGN="LEFT">{{definition}}</TD></TR>{% endif %}
    {% for p in members %}{% if definition %} <TR><TD ALIGN="LEFT" VALIGN="TOP">{{p[0]}}</TD>
    <TD ALIGN="LEFT" BALIGN="LEFT" VALIGN="TOP">{{p[1]}}</TD></TR>{% else %}
    <TR><TD ALIGN="left" CELLPADDING="2" BORDER="0"> {{p}}</TD></TR> {% endif %} {% endfor %}
    </TABLE>>"""

    palette = Palette()
    colspan = {0: '', 1: 'COLSPAN="2"'}[with_definitions]

    bg_col = {0: palette.main('def'), 1: 'gainsboro'}[bw]
    hdr_col = {0: palette.top('def'), 1: 'black'}[bw]

    definitions = with_definitions
    if with_definitions:
        definitions = limit_width(k.doc, header_nchars)

    members = []
    for p in klass._osl.members:
        if with_definitions:
            rhs = limit_width(p[1], definition_nchars)
            members.append((p[0], rhs))
        else:
            members.append(p[0])

    t = Template(template)
    label = t.render(k=klass, bg_col=bg_col, hdr_col=hdr_col, members=members, definitions=definitions, colspan=colspan)
    return label


def limit_width(text, charlimit):
    """ Unfortunately it seems difficult to get graphviz html labels to limit their width
    sensibly, so this is a hack to limit widths manually.
    It adds html <br/> at roughly the designated character size
    :param text: Text to limit.
    :param charlimit: Approximate width in characters.
    :return: text with <br/> in it at the appropriate places
    """
    lines = textwrap.wrap(text, charlimit, break_long_words=False)
    return '<BR/>'.join(lines)

#    nchars = len(text)
#    n1, n2 = 0, charlimit
#    text = text.replace('\n',' ').replace('\r',' ')
#    output = text
#    if nchars > charlimit:
#        output = ''
#        while n2 < nchars:
#            n2 = text[:n2].rfind(' ')
#            chunk = text[n1:n2]
#            output += chunk + '<BR/>'
#            n1 = n2+1
#            n2 = n2 + charlimit
#        output += text[n1:]
#    return output


