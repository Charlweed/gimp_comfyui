#  Copyright (c) 2024. Charles Hymes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from workflow.workflow_2_py_generator import *


class AccessorGenerator(Workflow2PythonGenerator):

    IMPORTS = """from enum import Enum
from workflow.node_accessor import NodesAccessor"""

    INNER_XTOR = """        def __init__(self, outer):
            self._outer = outer\n\n"""

    def __init__(self):
        super().__init__()
        self._clazzes_indexes_dict: Dict[str, str] = {}
        self._node_field_names: List[str] = []
        self._field_indexes_dict: Dict[str, str] = {}

    @property
    def field_instances(self) -> Dict[str, str]:
        return self._field_indexes_dict

    @property
    def inner_clazzes(self) -> Dict[str, str]:
        return self._clazzes_indexes_dict

    @property
    def python_class_file_name(self) -> str:
        mangled = self.workflow_filename.replace(Workflow2PythonGenerator.WORKFLOW_TAG, "_accessor")
        mangled = re.sub(CRUDE_VERSION_REGEX, r"\g<1>dot\g<2>", mangled)
        mangled = mangled.replace(".json", ".py")
        return mangled

    def field_identifier(self, node_title: str):
        tw = re.sub(ID_BREAKERS_REGEX, "", node_title)
        if starts_with_digits(tw):
            tw = "zz" + tw
        field_id = tw.lower().replace(" ", "_")
        return unique_id(field_id, self._node_field_names)

    def enum_text(self) -> str:
        text: str = "\n    class NodeIndexes(Enum):\n"
        for item in self.nodes_dictionary.items():
            node: Dict = item[1]
            enum_title: str = title(node_dict=node)
            enum_id = self.enum_identifier(node_title=enum_title)
            self.enum_instances[item[0]] = enum_id
            line = SP08 + "%s = \"%s\"\n" % (enum_id, item[0])
            text += line
        text += "\n"
        return text

    def node_input_getter_text(self, input_key: str, enum_id: str, type_name: str):
        return (SP08 + "@property\n%sdef %s(self) -> %s:\n%sreturn self._outer.nodes_dict[%s.NodeIndexes.%s.value]"
                "[\"inputs\"][\"%s\"]  # noqa\n\n"
                % (SP08, input_key, type_name, SP12, self.python_class_name, enum_id, input_key))

    def node_input_setter_text(self, input_key: str, enum_id: str, type_name: str):
        return (SP08 + "@%s.setter\n%sdef %s(self, value: %s):\n%sself._outer.nodes_dict[%s.NodeIndexes.%s.value]"
                "[\"inputs\"][\"%s\"] = value  # noqa\n\n"
                % (input_key, SP08, input_key, type_name, SP12, self.python_class_name, enum_id, input_key))

    def node_class_text(self, node_dict: Dict, index_str: str, enum_id: str) -> str:
        # node internals are not unique, but our internal classes must be,
        # because they define the external properties
        class_name_xt = class_name_external(index_str=index_str, node_dict=node_dict)
        self.inner_clazzes[index_str] = class_name_xt
        text: str = "    class %s:\n\n" % class_name_xt
        text += AccessorGenerator.INNER_XTOR
        inputs: Dict = node_dict["inputs"]
        for input_item in inputs.items():
            input_key = input_item[0]
            input_val = input_item[1]
            type_name = type(input_val).__name__
            # logging.warning("type of property is %s" % type_name)
            # Only process singletons as properties
            if isinstance(input_val, (bool, int, float, str)):
                text += self.node_input_getter_text(input_key=input_key, enum_id=enum_id, type_name=type_name)
                text += self.node_input_setter_text(input_key=input_key, enum_id=enum_id, type_name=type_name)
        return text

    def node_classes_text(self):
        text = ""
        if not self.enum_instances:
            raise ValueError("enum_instances dict is empty.")
        for item in self.nodes_dictionary.items():
            enum_id = self.enum_instances[item[0]]  # enum_instances was previously populated by enum_text
            node: Dict = item[1]
            text += self.node_class_text(node_dict=node, index_str=item[0], enum_id=enum_id)
        return text

    def constructor_text(self):
        text: str = (f"{SP04}def __init__(self):\n"
                     f"{SP08}super().__init__({self.python_class_name}.WORKFLOW_FILE)\n"
                     )
        for item in self.nodes_dictionary.items():
            node = item[1]
            node_title: str = node["_meta"]["title"]
            field_id = self.field_identifier(node_title=node_title)
            self.field_instances[item[0]] = field_id
            inner_class_name = self.inner_clazzes[item[0]]
            declaration = ("%sself._%s: %s.%s = %s.%s(self)  # noqa\n" %
                           (SP08, field_id,
                            self.python_class_name, inner_class_name, self.python_class_name, inner_class_name))
            text += declaration
        return text

    def main_properties_text(self):
        text = "\n"
        for field_name in self.field_instances.values():
            getter = "%s@property\n%sdef %s(self):\n%sreturn self._%s\n\n" % (SP04, SP04, field_name, SP08, field_name)
            setter = ("%s@%s.setter\n%sdef %s(self, value):\n%sself._%s = value\n\n" %
                      (SP04, field_name, SP04, field_name, SP08, field_name))
            text += "%s%s" % (getter, setter)
        return text

    def write_source_file(self):
        LOGGER_WF2PY.info(f"Writing node accessor python source file \"{self.python_class_file_path}\"")
        with open(self.python_class_file_path, "w") as class_source_file:
            class_source_file.write(AccessorGenerator.IMPORTS + "\n")
            class_source_file.write("\n\nclass " + self.python_class_name + "(NodesAccessor):\n")
            class_source_file.write("    WORKFLOW_FILE = \"%s\"\n" % self.workflow_filename)
            class_source_file.write(self.enum_text())
            class_source_file.write(self.node_classes_text())
            class_source_file.write(self.constructor_text())
            class_source_file.write(self.main_properties_text().rstrip('\r*\n'))
            class_source_file.write("\n")


def main() -> int:
    generator_instance = AccessorGenerator()
    generator_instance.write_source_file()
    return 0


# L:\projects\hymerfania\gimp_scripts\two_nintynine\plug-ins_available\gimp_comfyui\assets\comfyui_default_workflow_api.json
# L:\projects\hymerfania\gimp_scripts\two_nintynine\plug-ins_available\gimp_comfyui\assets\img2img_sdxl_0.3_workflow_api.json
# L:\projects\hymerfania\gimp_scripts\two_nintynine\plug-ins_available\gimp_comfyui\assets\sytan_sdxl_1.0_workflow_api.json
if __name__ == '__main__':
    sys.exit(main())
