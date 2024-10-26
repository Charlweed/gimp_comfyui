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

WORKFLOW_IMPORTS: str = "# Insert WORKFLOW_IMPORTS→"
PROCEDURE_NAME_VARS: str = "# Insert PROCEDURE_NAME_VARS→"
PROCEDURE_NAME_ITEMS: str = "# Insert PROCEDURE_NAME_ITEMS→"
WORKFLOW_ACCESSOR_PROPERTY: str = "# Insert WORKFLOW_ACCESSOR_PROPERTY→"
WORKFLOW_ACCESSOR_DECLARATION: str = "# Insert WORKFLOW_ACCESSOR_DECLARATION→"
WORKFLOW_PROCEDURE_CASE: str = "# Insert WORKFLOW_PROCEDURE_CASE→"
WORKFLOW_INVOCATION_FUNCTION: str = "# Insert WORKFLOW_INVOCATION_FUNCTION→"

GLUE_REPLACEMENT_TAGS: List[str] = [
    WORKFLOW_IMPORTS,
    PROCEDURE_NAME_VARS,
    PROCEDURE_NAME_ITEMS,
    WORKFLOW_ACCESSOR_PROPERTY,
    WORKFLOW_ACCESSOR_DECLARATION,
    WORKFLOW_PROCEDURE_CASE,
    WORKFLOW_INVOCATION_FUNCTION,
]


class PluginGlueGenerator(Workflow2PythonGenerator):

    def __init__(self):
        super().__init__()

    @property
    def python_class_file_path(self):
        return os.path.join(f"{self.script_dir_path}/..", self.python_class_file_name)

    @property
    def python_class_file_name(self) -> str:
        return "gimp_comfyui.py"

    def insert_workflow_imports(self, plugin_source: str) -> str:
        a_name: str = self.accessor_source_basename
        d_name: str = self.dialog_source_basename
        import_accessor: str = f"from workflow.{a_name} import {self.accessor_class_name}"
        import_dialog: str = f"from workflow.{d_name} import {self.dialog_class_name}"
        replacement: str = f"{import_accessor}\n{import_dialog}\n{WORKFLOW_IMPORTS}\n"
        edited_source: str = plugin_source.replace(WORKFLOW_IMPORTS, replacement)
        return edited_source

    def insert_procedure_name_vars(self, plugin_source: str) -> str:
        undecorated: str = undecorated_raised(self.base_class_name)
        proc_name_identifier: str = f"PROCEDURE_INVOKE_{undecorated}_WF"
        replacement: str = f"{proc_name_identifier} = \"{self.base_class_name}\"\n{SP04}{PROCEDURE_NAME_VARS}"
        edited_source: str = plugin_source.replace(PROCEDURE_NAME_VARS, replacement)
        return edited_source

    def insert_procedure_name_items(self, plugin_source: str) -> str:
        undecorated: str = undecorated_raised(self.base_class_name)
        proc_name_identifier: str = f"PROCEDURE_INVOKE_{undecorated}_WF"
        replacement: str = f"{proc_name_identifier},\n{SP08}{PROCEDURE_NAME_ITEMS}"
        edited_source: str = plugin_source.replace(PROCEDURE_NAME_ITEMS, replacement)
        return edited_source

    def insert_workflow_accessor_property(self, plugin_source: str) -> str:
        replacement: str = (f"@property\n{SP04}def {self.base_class_name}_accessor(self) -> {self.accessor_class_name}:\n"  # noqa
                            f"{SP08}return self._{self.base_class_name}_accessor\n"
                            f"{SP04}{WORKFLOW_ACCESSOR_PROPERTY}")
        edited_source: str = plugin_source.replace(WORKFLOW_ACCESSOR_PROPERTY, replacement)
        return edited_source

    def insert_workflow_accessor_declaration(self, plugin_source: str) -> str:
        replacement: str = f"self._{self.base_class_name}_accessor: {self.accessor_class_name} = {self.accessor_class_name}()\n{SP08}{WORKFLOW_ACCESSOR_DECLARATION}" # noqa
        edited_source: str = plugin_source.replace(WORKFLOW_ACCESSOR_DECLARATION, replacement)
        return edited_source

    def insert_workflow_evocation_function(self, plugin_source: str) -> str:
        shorter: str = self.workflow_filename.replace(Workflow2PythonGenerator.WORKFLOW_TAG, "")
        f_name = fat_name(shorter)
        replacement: str = f"""def {self.base_class_name}_workflow(self, procedure: Gimp.ImageProcedure,
                       run_mode,  # noqa
                       image,  # noqa
                       n_drawables,  # noqa
                       drawables,  # noqa
                       args,  # noqa
                       run_data  # noqa
                       ) -> Gimp.ValueArray:
        factory: {self.dialog_class_name} = {self.dialog_class_name}(accessor=self._{self.base_class_name}_accessor)  # noqa
        ret_values = self.invoke_workflow(procedure=procedure,
                                          factory=factory,
                                          title_in="{f_name}",
                                          role_in="workflow",
                                          blurb_in="This dialog was machine-written."
                                          )
        return ret_values

    {WORKFLOW_INVOCATION_FUNCTION}"""
        edited_source: str = plugin_source.replace(WORKFLOW_INVOCATION_FUNCTION, replacement)
        return edited_source

    def insert_workflow_procedure_case(self, plugin_source: str) -> str:
        undecorated: str = undecorated_raised(self.base_class_name)
        proc_name_identifier: str = f"PROCEDURE_INVOKE_{undecorated}_WF"
        shorter: str = self.workflow_filename.replace(Workflow2PythonGenerator.WORKFLOW_TAG, "")
        f_name = fat_name(shorter)
        replacement: str = f"""
            case GimpComfyUI.{proc_name_identifier}:
                procedure = self.create_procedure(name_raw=name,
                                                  docs="I{f_name}",
                                                  usage_hint="This dialog was machine-written.",
                                                  run_func_in=self.{self.base_class_name}_workflow,
                                                  is_image_optional=True,  # Redundant with SubjectType.ANYTHING
                                                  proc_category=ProcedureCategory.WORKFLOW,
                                                  subject_type=SubjectType.ANYTHING)
            {WORKFLOW_PROCEDURE_CASE}"""
        edited_source: str = plugin_source.replace(WORKFLOW_PROCEDURE_CASE, replacement)
        return edited_source

    def write_source_file(self):
        plugin_source: str
        with open(self.python_class_file_path, "r", encoding='utf-8') as plugin_source_file:
            plugin_source = plugin_source_file.read()

        if not plugin_source:
            raise IOError(f"Error reading {self.python_class_file_path}")
        plugin_source = self.insert_workflow_imports(plugin_source)
        plugin_source = self.insert_procedure_name_vars(plugin_source)
        plugin_source = self.insert_procedure_name_items(plugin_source)
        plugin_source = self.insert_workflow_accessor_property(plugin_source)
        plugin_source = self.insert_workflow_accessor_declaration(plugin_source)
        plugin_source = self.insert_workflow_evocation_function(plugin_source)
        plugin_source = self.insert_workflow_procedure_case(plugin_source)
        # dest_path = self.python_class_file_path.replace(".py", "_new.py")
        dest_path = self.python_class_file_path  # change suffixes for testing.
        LOGGER_WF2PY.info(f"Writing node accessor python source file \"{dest_path}\"")
        with open(dest_path, "w", encoding='utf-8') as plugin_source_file:
            plugin_source_file.write(plugin_source)


def main() -> int:
    generator_instance = PluginGlueGenerator()
    generator_instance.write_source_file()
    return 0


# L:\projects\hymerfania\gimp_scripts\two_nintynine\plug-ins_available\gimp_comfyui\assets\flux_neg_upscale_sdxl_0.4_workflow_api.json

if __name__ == '__main__':
    sys.exit(main())
