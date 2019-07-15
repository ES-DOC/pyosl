
from pathlib import Path

from pyosl import Factory, Base
from pyosl import esd_decode
import pygraphviz as pgv
import uuid

from jinja2 import Template

import json, textwrap


def find_interesting_properties(instance):
    """ Find all the interesting (non None) properties for a pysosl instance """
    props = [k for k in instance.__dict__ if not k.startswith('_')]
    props = [k for k in props if getattr(instance, k) and getattr(instance, k) != 'n/a']
    return props


def label(x, properties):
    n = name(x)
    r = f'{textwrap.fill(n,70)}\n'
    r += "\n".join([f'{i}:{j}' for i,j in properties])
    return r


def more(text, wrap=70, maximum=200):
    copy = str(text)[0:maximum]
    if copy != text:
        copy += '...'
    return textwrap.fill(copy, wrap)


def name(klass_instance):
    """ Need to handle klasses with no names"""

    def useable(attr):
        """ If exists as an attribute and has value"""
        if hasattr(klass_instance, attr):
            myname = getattr(klass_instance, attr)
            if myname:
                return myname
        return False

    options = [str(klass_instance),
               useable('name'), useable('short_name'), useable('canonical_name'), useable('description')]

    if options[0] == 'None':
        del options[0]
    for i in options:
        if i:
            return i

    return uuid.uuid4()


class InstanceUML:
    """ Representation of one or more OSL instances in UML"""
    def __init__(self, filestem, option='bubble', **kwargs):

        """ Set up with output filename, and any default graph properties"""

        self.filestem = filestem
        self.viewing_option = option

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
            self.default_node_attributes = {'shape': 'plain'}
        elif option == 'name_only':
            self.default_node_attributes = {'shape': 'ellipse', 'style': 'filled'}
        elif option == 'box':
            self.default_node_attributes = {'shape': 'box'}

        self.G = pgv.AGraph(**initial_graph_properties)


    def add_json(self, json_content):
        """ Add some json content to the canvas"""
        mypy = esd_decode(Factory, json_content)
        self.name = name(mypy)
        self.__render(mypy)

    def __render(self, klass_instance, depth=1, maxdepth=2):
        """ Parse an instance and add nodes"""
        props = find_interesting_properties(klass_instance)
        properties = []
        linked_properties = []
        nodes = []
        myname = name(klass_instance)

        def __makelink(value):
            if isinstance(value, Base) and depth < maxdepth:
                target = self.__render(value, depth + 1, maxdepth)
                linked_properties.append([k, target])
            else:
                if isinstance(value,str):
                    properties.append((k, more(value)))
                else:
                    properties.append((k, more(name(value))))

        for k in props:
            value = getattr(klass_instance, k)
            if isinstance(value, list):
                for v in value:
                    __makelink(v)
            else:
                __makelink(value)


        self.__add_node(myname, klass_instance, properties, depth)
        for lp in linked_properties:
            print(f'edge {myname} -> {lp[1]} label={lp[0]}')
            self.G.add_edge(myname, lp[1], label=lp[0])

        nwidth = 3
        if len(linked_properties) > nwidth:
            for i, v in enumerate(linked_properties[:-nwidth]):
                n1, n2 = linked_properties[i][1], linked_properties[i + nwidth][1]
                print(f'edge {n1} -> {n2} invis')
                self.G.add_edge(n1, n2, style='invis')

        return myname


    def __add_node(self, myname, klass_instance, properties, depth):
        print(f'node {myname} (depth{depth})')
        label = Templates.render(klass_instance, properties=properties)
        self.G.add_node(myname, label=label)


    def output(self, dot_out_please=False):

        if dot_out_please:
            self.G.write(f'{self.filestem}.dot')

        self.G.draw(f'{self.filestem}-{self.name}.pdf',  prog='dot')


class BaseTemplate:
    """ Interface template for diagrams"""
    def __init__(self, klass, html):
        print('initialised', klass)
        self.klass = klass
        self.template = Template(html)

    def render(self, instance):
        cname = name(instance)
        print(f'Rendering {str(instance)} ({instance._osl.type_key})as node {cname}')
        return self.template.render(k=instance, name=cname)


class SimpleComponent(BaseTemplate):
    """ Simple Model Component Example"""
    def __init__(self):
        html = """<<table border="0">
        <tr><td>{{ name }}</td></tr>
        <tr><td>({{k.model_type}}, {% for r in k.realms %} {{r | escape}} {% endfor %})</td></tr>
        </table>>"""
        super().__init__('cim.2.science.model', html)


class SimpleTopic(BaseTemplate):
    """ Simple Key Topic representation"""
    def __init__(self):
        html = """<<table border="0">
        <tr><td>{{name}}</td></tr>
        </table>>"""
        super().__init__('cim.2.science.topic', html)


class SimpleRealm(BaseTemplate):
    """ Simple realm"""
    def __init__(self):
        html = """<<table border="0">
        <tr><td>{{name}}</td></tr>
        {% for p in k.processes %} <tr><td>{{ p.name | string }}</td></tr> {% endfor %}
        </table>>"""
        super().__init__('cim.2.science.realm', html)


class Templates:
    """ Interface to template registration and selection"""

    templates = {}

    @staticmethod
    def register(template):
        Templates.templates[template.klass] = template

    @staticmethod
    def render(instance, properties=None):
        if instance._osl.type_key in Templates.templates:
            t = Templates.templates[instance._osl.type_key]
            h = t.render(instance)
            return h
        else:
            print(f' defaulting for {instance._osl.type_key}')
            if properties:
                return label(instance, properties)
            else:
                return str(instance)


if __name__ == "__main__":

    esd_archive_base = 'Code/esdoc19/esdoc-archive/esdoc/cmip6'
    esd_archive_dirs = ['spreadsheet-models']
    mdir = Path.home() / esd_archive_base / esd_archive_dirs[0]
    models = mdir.glob('*.json')
    index = 0
    instances = []
    for model in models:
        with model.open() as f:
            json_version = json.load(f)
            instances.append(json_version)

    Templates.register(SimpleComponent())
    Templates.register(SimpleTopic())
    Templates.register(SimpleRealm())
    for n, i in enumerate(instances):
        d = InstanceUML(f'mytest-{n}')
        d.add_json(i)
        d.output()
