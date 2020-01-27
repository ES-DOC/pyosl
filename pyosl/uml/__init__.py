from distutils.version import LooseVersion

# Check pygraphviz
minimum_vn = '1.3'
try:
    import pygraphviz
except ImportError as error:
    raise ImportError('pysol requires the module pygraphviz (version '+minimum_vn+' or newer) to produce UML. '+str(error))

if LooseVersion(pygraphviz.__version__) < LooseVersion(minimum_vn):
    raise ValueError(
        "Bad version of pygraphviz: pyosl requires pygraphviz version {} or later. Got version {} at {}".format(
            minimum_vn, pygraphviz.__version__, pygraphviz.__file__))

from .uml_utils import (PackageColour, Palette, camel_split,
                        uml_bubble, uml_class_box_label,
                        uml_simple_box, uml_enum_box_label,
                        limit_width)

from .uml_base import UmlBase

from .uml_packages import package_label, PackageUML

from .uml_diagrams import BasicUML

from .triples_to_dot import TriplesDelux

from .uml4_packages import (uml4_software, uml4_shared, uml4_science, uml4_platform, uml4_activity,
                            uml4_cmip, uml4_data, uml4_design, uml4_drs, uml4_iso, uml4_time)
