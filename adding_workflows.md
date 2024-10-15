# Adding Workflows
Adding, or updating a new ConfyUI workflow to couple to GIMP requires some computing and python 3 skills. You need to
complete or edit the source dode of the dialog that GIMP opens for the workflow. Also, when the nodes within
ComfyUI change, i.e. if inputs or outputs are added, moved or renamed, the generated prompt might fail validation. In
those cases, the accessors and dialogs will need to be re-generated. The difficulty depends upon the size
and complexity of the workflow, and the datatypes that workflow processes. Basically, the steps are:
## ComfyUI
- In the Advanced Options dialog in ComfyUI, enable API mode
-  Open, create or customize the workflow in ComfyUI.
-  Choose the base name of workflow. Use lowercase, and underscores. For example "inpainting_sdxl_0.2" No hyphens/dashes.
-  Save the workflow json file in **api mode** into the "assets" directory of this project
-  Rename the workflow json file your basename plus the suffix "*_workflow_api.json*":
≪your_base_name≫_workflow_api.json. For example "inpainting_sdxl_0.2_workflow_api.json"
- In a terminal, set the `PYTHONPATH` environment variable to this project directory: ``$ENV:PYTHONPATH="L:\\projects\\gimp_comfyui"``
- In the same terminal, run the python program "workflow/generate_node_accessor.py" with your workflow json file as the
argument. This will create a new python source file in the "workflow" directory. The file name will be ≪your_base_name≫,
with a suffix of "*_accessor.py*", munged into a form that's a bit safer for machine processing.  For example,
"inpainting_sdxl_0dot4_accessor.py"
"inpainting_sdxl_0dot4_accessor.py"
-  Also from a command line, run the python program "workflow/generate_inputs_dialog.py" with your workflow json file as
the argument. This will create a new python source file in the "workflow" directory. The file name will be ≪your_base_name≫,
   with a suffix of "*_inputs_dialog.py*", again, munged into a form that's a bit safer for machine processing. For example,
   "inpainting_sdxl_0dot4_inputs_dialog.py"
## Updating gimp_comfyui.py
-  In the main plugin source file "*gimp_comfyui.py*" add imports for your new workflows. i.e.
```python
from workflow.inpainting_sdxl_0dot4_accessor import InpaintingSdxl0Dot4Accessor
from workflow.inpainting_sdxl_0dot4_dialogs import InpaintingSdxl0Dot4Dialogs
```
- Add a procedure name as a class variable for the GimpComfyUI plugin class. Use "PROCEDURE_INVOKE_" as a 
prefix, and choose a name and value from the workflow base name. Not that the value CANNOT have underscores, 
only hyphens/dashes. Otherwise, GIMP will flag a "assertion 'gimp_is_canonical_identifier (procedure_name)' failed" error.
```python
    PROCEDURE_INVOKE_INPAINTING_WF = "inpainting-sdxl"
```
- Add the new procedure name to the PROCEDURE_NAMES array.
```python
PROCEDURE_NAMES = [
    PROCEDURE_WATCH_LAYER,
    PROCEDURE_INVOKE_DEFAULT_WF,
    PROCEDURE_INVOKE_SYTAN_WF,
    PROCEDURE_INVOKE_INPAINTING_WF,
]
```
-  Add a field for the accessor in the constructor for the GimpComfyUI plugin class:
```python
        self._inpainting_sdxl_accessor: InpaintingSdxl0Dot4Accessor = InpaintingSdxl0Dot4Accessor()
```
-  Add a property for the accessor. Name the property for the workflow.
```python
    @property
    def inpaint_accessor(self) -> InpaintingSdxl0Dot4Accessor:
        return self._inpainting_sdxl_accessor
```
-  Add an invoker for the workflow. Name the function from your workflow.
```python
    def inpaint_workflow(self, procedure: Gimp.ImageProcedure,
                       run_mode,  # noqa
                       image,  # noqa
                       n_drawables,  # noqa
                       drawables,  # noqa
                       args,  # noqa
                       run_data  # noqa
                       ) -> Gimp.ValueArray:
        factory: InpaintingSdxl0Dot4Dialogs = InpaintingSdxl0Dot4Dialogs(accessor=self.inpaint_accessor)
        ret_values = self.invoke_workflow(procedure=procedure,
                                          factory=factory,
                                          title_in="Inpainting SDXL",
                                          role_in="workflow",
                                          blurb_in="Some dialog values need to be duplicated."
                                          )
        return ret_values
```
- Add a case for your workflow in the plug-ins `do_create_procedure()` method, in the `match name` block: 
```python
            case GimpComfyUI.PROCEDURE_INVOKE_INPAINTING_WF:
                procedure = self.create_procedure(name_raw=name,
                                                  docs="Inpainting SDXL Workflow",
                                                  usage_hint="Keep duplicate fields synchronized. Sorry",
                                                  run_func_in=self.inpaint_workflow,
                                                  is_image_optional=True,  # Redundant with SubjectType.ANYTHING
                                                  proc_category=ProcedureCategory.WORKFLOW,
                                                  subject_type=SubjectType.ANYTHING)
```
At this point, your workflow will appear under the "Workflows" menu option in the GimpComfyUI plugin, and the dialog 
will open when you select it.
## Modifying the Dialog (and Accessor)
Assuming the python files were generated without error, you will still probably want to modify the generated python
code so that the dialog shows that values you want, with the widgets and labels you want. The details of that process 
are out-of-scope for this document.