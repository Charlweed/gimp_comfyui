
import gi

gi.require_version('Gimp', '3.0')  # noqa: E402
gi.require_version('GimpUi', '3.0')  # noqa: E402
gi.require_version("Gtk", "3.0")  # noqa: E402
gi.require_version('Gdk', '3.0')  # noqa: E402
gi.require_version("Gegl", "0.4")  # noqa: E402
from gi.repository import Gdk, Gio, Gimp, GimpUi, Gtk, GLib, GObject, Gegl  # noqa
from typing import Set
from utilities.cui_resources_utils import *
from utilities.heterogeneous import *
from utilities.persister_petite import *
from utilities.sd_gui_utils import *
from workflow.node_accessor import NodesAccessor
from workflow.workflow_dialog_factory import WorkflowDialogFactory


class InpaintingSdxl0Dot4Dialogs(WorkflowDialogFactory):

    WORKFLOW_FILE = "inpainting_sdxl_0.4_workflow_api.json"

    def __init__(self, accessor: NodesAccessor):
        super().__init__(
            accessor=accessor,
            api_workflow=InpaintingSdxl0Dot4Dialogs.WORKFLOW_FILE,
            dialog_config_chassis_name="InpaintingSdxl0Dot4Dialogs_dialog_config",
            wf_data_chassis_name="InpaintingSdxl0Dot4Dialogs_wf_data",
        )

    # GIMP is preventing subclassing GimpUI.Dialog by preventing access to the constructors. This might be accidental.
    def new_workflow_dialog(self, 
                            title_in: str,
                            role_in: str,
                            blurb_in: str,
                            gimp_icon_name: str = GimpUi.ICON_DIALOG_INFORMATION
                            ) -> GimpUi.Dialog:

        widgets_invalid_set: Set[str] = set()

        # noinspection PyMethodMayBeStatic
        def validate_dialog(invalidated: bool):
            nonlocal button_apply
            nonlocal button_ok

            if invalidated:
                LOGGER_SDGUIU.info("Invalidating dialog")
                button_apply.set_sensitive(False)
                button_ok.set_sensitive(False)
            else:
                LOGGER_SDGUIU.info("Validating dialog")
                button_apply.set_sensitive(True)
                button_ok.set_sensitive(True)

        def track_invalid_widgets(my_widget: Gtk.Widget, is_invalid: bool):
            nonlocal widgets_invalid_set
            widget_name: str = my_widget.get_name()
            if widget_name is None:
                raise ValueError("Widget does not have a name")
            if not widget_name.strip():
                raise ValueError("Widget name cannot be empty nor whitespace.")
            if re.search(r"\s", widget_name):
                raise ValueError("Widget name cannot contain whitespace")
            if widget_name in WIDGET_NAME_DEFAULTS:
                raise ValueError(f"Widget name cannot be default name \"{widget_name}\"")
            orig_size = len(widgets_invalid_set)
            if is_invalid:
                if widget_name not in widgets_invalid_set:
                    widgets_invalid_set.add(widget_name)
                    LOGGER_SDGUIU.info(f"Added {widget_name} as INVALID")
            else:
                # LOGGER_SDGUIU.info(f"Discarding {widget_name} from invalid")
                widgets_invalid_set.discard(widget_name)
            new_size = len(widgets_invalid_set)
            delta_size = new_size - orig_size
            if delta_size != 0:
                validate_dialog(new_size > 0)

        dialog = GimpUi.Dialog(use_header_bar=True, title=title_in, role=role_in)
        fallback_path = os.path.join(super().asset_dir, "model_dirs.json")
        persister: PersisterPetite = PersisterPetite(chassis=dialog,
                                                     chassis_name="inpainting_sdxl_0dot4_dialog",
                                                     fallback_path=fallback_path)
        dialog_data: Dict = dict(persister.load_config())
        widget_getters: Dict[str, Callable[[], Any]] = {}
        widget_setters: Dict[str, Callable[[Any], None]] = {}

        def fill_widget_values():
            for consumers in widget_setters.items():
                key_name: str = consumers[0]
                setter = consumers[1]
                try:
                    if key_name in dialog_data:
                        arg_value = dialog_data[key_name]
                        if arg_value is None:
                            err_msg: str = f"Value for key \"{key_name}\" is None."
                            LOGGER_SDGUIU.debug(err_msg)
                            # raise ValueError(err_msg)
                        setter(arg_value)
                    else:
                        err_msg: str = f"Key \"{key_name}\" not present in dialog_data."
                        dd_data_str: str = json.dumps(dialog_data, indent=2, sort_keys=True)
                        LOGGER_SDGUIU.debug(err_msg)
                        LOGGER_SDGUIU.debug(dd_data_str)
                        # raise KeyError(err_msg)
                except KeyError as k_err:  # Not an exception if data not persisted.
                    LOGGER_SDGUIU.debug(k_err)
                    # raise k_err  # For debugging new workflows.
                except ValueError as v_err:  # Not an exception if data not persisted.
                    LOGGER_SDGUIU.debug(v_err)
                    # raise v_err  # For debugging new workflows.
        
        dialog_box = dialog.get_content_area()
        if blurb_in:
            label_and_icon_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            icon_image = Gtk.Image.new_from_icon_name(gimp_icon_name, Gtk.IconSize.DIALOG)  # noqa
            blurb_label: Gtk.Label = Gtk.Label.new(blurb_in)
            label_and_icon_box.pack_start(child=icon_image, expand=False, fill=False, padding=0)  # noqa
            label_and_icon_box.pack_start(child=blurb_label, expand=False, fill=False, padding=0)  # noqa
            label_and_icon_box.show_all()  # noqa
            dialog_box.add(label_and_icon_box)

        dialog.add_button(i8_text("_Cancel"), Gtk.ResponseType.CANCEL)
        dialog.add_button(i8_text("_Apply"), Gtk.ResponseType.APPLY)
        dialog.add_button(i8_text("_OK"), Gtk.ResponseType.OK)

        button_cancel: Gtk.Button = dialog.get_widget_for_response(Gtk.ResponseType.CANCEL)
        button_apply: Gtk.Button = dialog.get_widget_for_response(Gtk.ResponseType.APPLY)
        button_ok: Gtk.Button = dialog.get_widget_for_response(Gtk.ResponseType.OK)

        def delete_results(subject: Any):  # noqa
            pass

        def assign_results(subject: Any):  # noqa
            for providers in widget_getters.items():
                key_name: str = providers[0]
                getter = providers[1]
                gotten = getter()  # blob_getters return the full path, then the leaf
                if re.fullmatch(r"treeview_.+_image", key_name):
                    self.add_image_tuple(gotten)
                    dialog_data[key_name] = gotten[1]  # the leaf. We use the full path elsewhere.
                else:
                    if re.fullmatch(r"treeview_.+_mask", key_name):  # Not yet implemented.
                        self.add_mask_tuple(gotten)
                        dialog_data[key_name] = gotten[1]  # the leaf. We use the full path elsewhere.
                    else:
                        dialog_data[key_name] = gotten
            persister.update_config(dialog_data)
            # persister.log_config()
            persister.store_config()
            self.put_inputs(dialog_data=dialog_data)

        # New Frame
        frame_loadimage_001base_image: Gtk.Frame = Gtk.Frame.new(label="Base Image: (select layer)        #1")  # noqa
        frame_loadimage_001base_image.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_1_image: Gtk.Label = Gtk.Label.new("Layer")
        treeview_1_image: LayerTreeView = LayerTreeView()
        treeview_1_image.set_name("treeview_1_image")
        treeview_1_image.set_hexpand(True)
        prev_selected_route = self._installation_persister.configuration.get('treeview_1_image_selection_route', None)
        if prev_selected_route is not None:
            treeview_1_image.select_path = ids_to_treepath(model=treeview_1_image.get_model(),
                                                           image_id=prev_selected_route[0],
                                                           layer_id=prev_selected_route[1])

        def selection_handler_1_image(selection: Gtk.TreeSelection):
            model, treeiter = selection.get_selected()
            if treeiter is not None:
                sel_path: Gtk.TreePath = model.get_path(treeiter)
                sel_route: tuple[int, int] = treepath_to_ids(model=model, layer_path=sel_path)
                self._installation_persister.update_config({'treeview_1_image_selection_route': sel_route})
                self._installation_persister.store_config()

        treeview_1_image.get_selection().connect("changed", selection_handler_1_image)
        widget_getters[treeview_1_image.get_name()] = treeview_1_image.get_selected_png_leaf  # noqa

        grid_1: Gtk.Grid = Gtk.Grid.new()
        grid_1.attach(label_1_image,    left=0, top=0, width=1, height=1)  # noqa
        grid_1.attach(treeview_1_image, left=1, top=0, width=3, height=1)  # noqa
        grid_1.set_column_homogeneous(False)
        grid_1.set_row_homogeneous(False)
        frame_loadimage_001base_image.add(widget=grid_1)  # noqa

        # New Frame
        frame_loadimage_002mask_image: Gtk.Frame = Gtk.Frame.new(label="Mask Image: (select layer)        #2")  # noqa
        frame_loadimage_002mask_image.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_2_image: Gtk.Label = Gtk.Label.new("Layer")
        treeview_2_image: LayerTreeView = LayerTreeView()
        treeview_2_image.set_name("treeview_2_image")
        treeview_2_image.set_hexpand(True)
        prev_selected_route = self._installation_persister.configuration.get('treeview_2_image_selection_route', None)
        if prev_selected_route is not None:
            treeview_2_image.select_path = ids_to_treepath(model=treeview_2_image.get_model(),
                                                           image_id=prev_selected_route[0],
                                                           layer_id=prev_selected_route[1])

        def selection_handler_2_image(selection: Gtk.TreeSelection):
            model, treeiter = selection.get_selected()
            if treeiter is not None:
                sel_path: Gtk.TreePath = model.get_path(treeiter)
                sel_route: tuple[int, int] = treepath_to_ids(model=model, layer_path=sel_path)
                self._installation_persister.update_config({'treeview_2_image_selection_route': sel_route})
                self._installation_persister.store_config()

        treeview_2_image.get_selection().connect("changed", selection_handler_2_image)
        widget_getters[treeview_2_image.get_name()] = treeview_2_image.get_selected_png_leaf  # noqa

        grid_2: Gtk.Grid = Gtk.Grid.new()
        grid_2.attach(label_2_image,    left=0, top=0, width=1, height=1)  # noqa
        grid_2.attach(treeview_2_image, left=1, top=0, width=3, height=1)  # noqa
        grid_2.set_column_homogeneous(False)
        grid_2.set_row_homogeneous(False)
        frame_loadimage_002mask_image.add(widget=grid_2)  # noqa

        # New Frame
        frame_vaeencodeforinpaint_004vae_encode_for_inpainting: Gtk.Frame = Gtk.Frame.new(label="VAE Encode (for Inpainting)        #4")  # noqa
        frame_vaeencodeforinpaint_004vae_encode_for_inpainting.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_4_grow_mask_by: Gtk.Label = Gtk.Label.new("Grow_Mask_By")
        label_4_grow_mask_by.set_margin_start(8)
        label_4_grow_mask_by.set_alignment(0.95, 0)
        adjustment_4_grow_mask_by: Gtk.Adjustment = Gtk.Adjustment(value=12.00000,
                                                                   lower=1.00000,
                                                                   upper=16.00000,
                                                                   step_increment=1.000,
                                                                   page_increment=4.000,
                                                                   page_size=0)
        scale_4_grow_mask_by: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_4_grow_mask_by)  # noqa
        scale_4_grow_mask_by.set_name("scale_4_grow_mask_by")
        scale_4_grow_mask_by.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_4_grow_mask_by.set_hexpand(True)

        def change_handler_4_grow_mask_by(source, **args):  # noqa
            pass
        scale_4_grow_mask_by.connect(SIG_VALUE_CHANGED, change_handler_4_grow_mask_by)
        widget_getters[scale_4_grow_mask_by.get_name()] = scale_4_grow_mask_by.get_value
        widget_setters[scale_4_grow_mask_by.get_name()] = scale_4_grow_mask_by.set_value

        grid_4: Gtk.Grid = Gtk.Grid.new()
        grid_4.attach(label_4_grow_mask_by, left=0, top=0, width=1, height=1)  # noqa
        grid_4.attach(scale_4_grow_mask_by, left=1, top=0, width=3, height=1)  # noqa
        grid_4.set_column_homogeneous(False)
        grid_4.set_row_homogeneous(False)
        frame_vaeencodeforinpaint_004vae_encode_for_inpainting.add(widget=grid_4)  # noqa

        # New Frame
        frame_checkpointloadersimple_005load_checkpoint: Gtk.Frame = Gtk.Frame.new(label="Load Checkpoint        #5")  # noqa
        frame_checkpointloadersimple_005load_checkpoint.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_5_ckpt_name: Gtk.Label = Gtk.Label.new("Ckpt_Name")
        comboboxtext_5_ckpt_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_5_ckpt_name: list[str] = get_models_filenames(
            model_type=ModelType.CHECKPOINTS,
            cu_origin=self.comfy_svr_origin)
        if combo_values_5_ckpt_name is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_5_ckpt_name:
            raise ValueError(fr"No models retrieved from ComfyUI")
        for combo_item_path in combo_values_5_ckpt_name:
            comboboxtext_5_ckpt_name.append_text(combo_item_path)
        comboboxtext_5_ckpt_name.set_name("comboboxtext_5_ckpt_name")
        comboboxtext_5_ckpt_name.set_hexpand(True)
        comboboxtext_5_ckpt_name.set_active(4)

        def change_handler_5_ckpt_name(source, **args):  # noqa
            pass
        comboboxtext_5_ckpt_name.connect(SIG_CHANGED, change_handler_5_ckpt_name)

        def setter_5_ckpt_name(a_val: str):
            nonlocal combo_values_5_ckpt_name
            selected_index = combo_values_5_ckpt_name.index(a_val)
            comboboxtext_5_ckpt_name.set_active(selected_index)
        widget_getters[comboboxtext_5_ckpt_name.get_name()] = comboboxtext_5_ckpt_name.get_active_text  # noqa
        widget_setters[comboboxtext_5_ckpt_name.get_name()] = setter_5_ckpt_name  # noqa

        grid_5: Gtk.Grid = Gtk.Grid.new()
        grid_5.attach(label_5_ckpt_name,        left=0, top=0, width=1, height=1)  # noqa
        grid_5.attach(comboboxtext_5_ckpt_name, left=1, top=0, width=3, height=1)  # noqa
        grid_5.set_column_homogeneous(False)
        grid_5.set_row_homogeneous(False)
        frame_checkpointloadersimple_005load_checkpoint.add(widget=grid_5)  # noqa

        # New Frame
        frame_unetloader_006load_diffusion_model: Gtk.Frame = Gtk.Frame.new(label="Load Diffusion Model        #6")  # noqa
        frame_unetloader_006load_diffusion_model.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_6_unet_name: Gtk.Label = Gtk.Label.new("Unet_Name")
        comboboxtext_6_unet_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_6_unet_name: list[str] = get_models_filenames(
            model_type=ModelType.UNET,
            cu_origin=self.comfy_svr_origin)
        if combo_values_6_unet_name is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_6_unet_name:
            raise ValueError(fr"No models retrieved from ComfyUI")
        for combo_item_path in combo_values_6_unet_name:
            comboboxtext_6_unet_name.append_text(combo_item_path)
        comboboxtext_6_unet_name.set_name("comboboxtext_6_unet_name")
        comboboxtext_6_unet_name.set_hexpand(True)
        comboboxtext_6_unet_name.set_active(0)

        def change_handler_6_unet_name(source, **args):  # noqa
            pass
        comboboxtext_6_unet_name.connect(SIG_CHANGED, change_handler_6_unet_name)

        def setter_6_unet_name(a_val: str):
            nonlocal combo_values_6_unet_name
            selected_index = combo_values_6_unet_name.index(a_val)
            comboboxtext_6_unet_name.set_active(selected_index)
        widget_getters[comboboxtext_6_unet_name.get_name()] = comboboxtext_6_unet_name.get_active_text  # noqa
        widget_setters[comboboxtext_6_unet_name.get_name()] = setter_6_unet_name  # noqa

        label_6_weight_dtype: Gtk.Label = Gtk.Label.new("Weight_Dtype")
        comboboxtext_6_weight_dtype: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_6_weight_dtype: list[str] = ["default", "fp8_e4m3fn", "fp8_e5m2"]  # noqa
        for combo_item_path in combo_values_6_weight_dtype:
            comboboxtext_6_weight_dtype.append_text(combo_item_path)
        comboboxtext_6_weight_dtype.set_name("comboboxtext_6_weight_dtype")
        comboboxtext_6_weight_dtype.set_hexpand(True)
        comboboxtext_6_weight_dtype.set_active(0)

        def change_handler_6_weight_dtype(source, **args):  # noqa
            pass
        comboboxtext_6_weight_dtype.connect(SIG_CHANGED, change_handler_6_weight_dtype)

        def setter_6_weight_dtype(a_val: str):
            nonlocal combo_values_6_weight_dtype
            selected_index = combo_values_6_weight_dtype.index(a_val)
            comboboxtext_6_weight_dtype.set_active(selected_index)
        widget_getters[comboboxtext_6_weight_dtype.get_name()] = comboboxtext_6_weight_dtype.get_active_text  # noqa
        widget_setters[comboboxtext_6_weight_dtype.get_name()] = setter_6_weight_dtype  # noqa

        grid_6: Gtk.Grid = Gtk.Grid.new()
        grid_6.attach(label_6_unet_name,           left=0, top=0, width=1, height=1)  # noqa
        grid_6.attach(comboboxtext_6_unet_name,    left=1, top=0, width=3, height=1)  # noqa
        grid_6.attach(label_6_weight_dtype,        left=4, top=0, width=1, height=1)  # noqa
        grid_6.attach(comboboxtext_6_weight_dtype, left=5, top=0, width=3, height=1)  # noqa
        grid_6.set_column_homogeneous(False)
        grid_6.set_row_homogeneous(False)
        frame_unetloader_006load_diffusion_model.add(widget=grid_6)  # noqa

        # New Frame
        frame_loraloader_007load_lora: Gtk.Frame = Gtk.Frame.new(label="Load LoRA        #7")  # noqa
        frame_loraloader_007load_lora.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_7_lora_name: Gtk.Label = Gtk.Label.new("Lora_Name")
        comboboxtext_7_lora_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_7_lora_name: list[str] = get_models_filenames(
            model_type=ModelType.LORAS,
            cu_origin=self.comfy_svr_origin)
        if combo_values_7_lora_name is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_7_lora_name:
            raise ValueError(fr"No models retrieved from ComfyUI")
        combo_values_7_lora_name = ['None'] + combo_values_7_lora_name
        for combo_item_path in combo_values_7_lora_name:
            comboboxtext_7_lora_name.append_text(combo_item_path)
        comboboxtext_7_lora_name.set_name("comboboxtext_7_lora_name")
        comboboxtext_7_lora_name.set_hexpand(True)
        comboboxtext_7_lora_name.set_active(3)

        def change_handler_7_lora_name(source, **args):  # noqa
            pass
        comboboxtext_7_lora_name.connect(SIG_CHANGED, change_handler_7_lora_name)

        def setter_7_lora_name(a_val: str):
            nonlocal combo_values_7_lora_name
            selected_index = combo_values_7_lora_name.index(a_val)
            comboboxtext_7_lora_name.set_active(selected_index)
        widget_getters[comboboxtext_7_lora_name.get_name()] = comboboxtext_7_lora_name.get_active_text  # noqa
        widget_setters[comboboxtext_7_lora_name.get_name()] = setter_7_lora_name  # noqa

        label_7_strength_model: Gtk.Label = Gtk.Label.new("Strength_Model")
        label_7_strength_model.set_margin_start(8)
        label_7_strength_model.set_alignment(0.95, 0)
        adjustment_7_strength_model: Gtk.Adjustment = Gtk.Adjustment(value=1.00000,
                                                                     lower=0.00000,
                                                                     upper=20.00000,
                                                                     step_increment=1.000,
                                                                     page_increment=5.000,
                                                                     page_size=0)
        scale_7_strength_model: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_7_strength_model)  # noqa
        scale_7_strength_model.set_name("scale_7_strength_model")
        scale_7_strength_model.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_7_strength_model.set_hexpand(True)

        def change_handler_7_strength_model(source, **args):  # noqa
            pass
        scale_7_strength_model.connect(SIG_VALUE_CHANGED, change_handler_7_strength_model)
        widget_getters[scale_7_strength_model.get_name()] = scale_7_strength_model.get_value
        widget_setters[scale_7_strength_model.get_name()] = scale_7_strength_model.set_value

        label_7_strength_clip: Gtk.Label = Gtk.Label.new("Strength_Clip")
        label_7_strength_clip.set_margin_start(8)
        label_7_strength_clip.set_alignment(0.95, 0)
        adjustment_7_strength_clip: Gtk.Adjustment = Gtk.Adjustment(value=1.00000,
                                                                    lower=0.00000,
                                                                    upper=20.00000,
                                                                    step_increment=1.000,
                                                                    page_increment=5.000,
                                                                    page_size=0)
        scale_7_strength_clip: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_7_strength_clip)  # noqa
        scale_7_strength_clip.set_name("scale_7_strength_clip")
        scale_7_strength_clip.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_7_strength_clip.set_hexpand(True)

        def change_handler_7_strength_clip(source, **args):  # noqa
            pass
        scale_7_strength_clip.connect(SIG_VALUE_CHANGED, change_handler_7_strength_clip)
        widget_getters[scale_7_strength_clip.get_name()] = scale_7_strength_clip.get_value
        widget_setters[scale_7_strength_clip.get_name()] = scale_7_strength_clip.set_value

        grid_7: Gtk.Grid = Gtk.Grid.new()
        grid_7.attach(label_7_lora_name,        left=0, top=0, width=1, height=1)  # noqa
        grid_7.attach(comboboxtext_7_lora_name, left=1, top=0, width=3, height=1)  # noqa
        grid_7.attach(label_7_strength_model,   left=0, top=1, width=1, height=1)  # noqa
        grid_7.attach(scale_7_strength_model,   left=1, top=1, width=3, height=1)  # noqa
        grid_7.attach(label_7_strength_clip,    left=0, top=2, width=1, height=1)  # noqa
        grid_7.attach(scale_7_strength_clip,    left=1, top=2, width=3, height=1)  # noqa
        grid_7.set_column_homogeneous(False)
        grid_7.set_row_homogeneous(False)
        frame_loraloader_007load_lora.add(widget=grid_7)  # noqa

        # New Frame
        frame_cliptextencode_009positive_prompt: Gtk.Frame = Gtk.Frame.new(label="Positive Prompt        #9")  # noqa
        frame_cliptextencode_009positive_prompt.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_9_text: Gtk.Label = Gtk.Label.new("Text")
        textview_9_text: Gtk.TextView = Gtk.TextView.new()
        textview_9_text.get_buffer().set_text("Portrait of Mr Spock, Vulcan science officer from Star Trek TOS, played by Leonard Nemoy,  driving a red 1963 Triumph TR3b roadster.")  # noqa
        textview_9_text.set_name("textview_9_text")
        textview_9_text.set_hexpand(True)
        textview_9_text.set_vexpand(True)
        textview_9_text.set_valign(Gtk.Align.FILL)
        # Create a ScrolledWindow to hold the TextView
        scrolled_window_9_text = Gtk.ScrolledWindow()
        scrolled_window_9_text.add(textview_9_text)  # noqa
        scrolled_window_9_text.set_size_request(864, 288)

        def preedit_handler_9_text(source, **args):  # noqa
            pass
        textview_9_text.connect(SIG_PREEDIT_CHANGED, preedit_handler_9_text)

        def getter_9_text():
            buffer: Gtk.TextBuffer = textview_9_text.get_buffer()
            start: Gtk.TextIter = buffer.get_start_iter()
            end: Gtk.TextIter = buffer.get_end_iter()
            return buffer.get_text(start, end, False)

        def setter_9_text(a_val: str):
            textview_9_text.get_buffer().set_text(str(a_val))

        widget_getters[textview_9_text.get_name()] = getter_9_text
        widget_setters[textview_9_text.get_name()] = setter_9_text

        grid_9: Gtk.Grid = Gtk.Grid.new()
        grid_9.attach(label_9_text,           left=0, top=0, width=1, height=1)  # noqa
        grid_9.attach(scrolled_window_9_text, left=1, top=0, width=3, height=1)  # noqa
        grid_9.set_column_homogeneous(False)
        grid_9.set_row_homogeneous(False)
        frame_cliptextencode_009positive_prompt.add(widget=grid_9)  # noqa

        # New Frame
        frame_cliptextencode_010negative_prompt: Gtk.Frame = Gtk.Frame.new(label="Negative Prompt        #10")  # noqa
        frame_cliptextencode_010negative_prompt.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_10_text: Gtk.Label = Gtk.Label.new("Text")
        textview_10_text: Gtk.TextView = Gtk.TextView.new()
        textview_10_text.get_buffer().set_text("low quality, distorted, deformed, slouching, ugly, noise")  # noqa
        textview_10_text.set_name("textview_10_text")
        textview_10_text.set_hexpand(True)
        textview_10_text.set_vexpand(True)
        textview_10_text.set_valign(Gtk.Align.FILL)
        # Create a ScrolledWindow to hold the TextView
        scrolled_window_10_text = Gtk.ScrolledWindow()
        scrolled_window_10_text.add(textview_10_text)  # noqa
        scrolled_window_10_text.set_size_request(288, 96)

        def preedit_handler_10_text(source, **args):  # noqa
            pass
        textview_10_text.connect(SIG_PREEDIT_CHANGED, preedit_handler_10_text)

        def getter_10_text():
            buffer: Gtk.TextBuffer = textview_10_text.get_buffer()
            start: Gtk.TextIter = buffer.get_start_iter()
            end: Gtk.TextIter = buffer.get_end_iter()
            return buffer.get_text(start, end, False)

        def setter_10_text(a_val: str):
            textview_10_text.get_buffer().set_text(str(a_val))

        widget_getters[textview_10_text.get_name()] = getter_10_text
        widget_setters[textview_10_text.get_name()] = setter_10_text

        grid_10: Gtk.Grid = Gtk.Grid.new()
        grid_10.attach(label_10_text,           left=0, top=0, width=1, height=1)  # noqa
        grid_10.attach(scrolled_window_10_text, left=1, top=0, width=3, height=1)  # noqa
        grid_10.set_column_homogeneous(False)
        grid_10.set_row_homogeneous(False)
        frame_cliptextencode_010negative_prompt.add(widget=grid_10)  # noqa

        # New Frame
        frame_modelsamplingdiscrete_011modelsamplingdiscrete: Gtk.Frame = Gtk.Frame.new(label="ModelSamplingDiscrete        #11")  # noqa
        frame_modelsamplingdiscrete_011modelsamplingdiscrete.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_11_sampling: Gtk.Label = Gtk.Label.new("Sampling")
        comboboxtext_11_sampling: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_11_sampling: list[str] = ["eps", "lcm", "v_prediction", "x0"]  # noqa
        for combo_item_path in combo_values_11_sampling:
            comboboxtext_11_sampling.append_text(combo_item_path)
        comboboxtext_11_sampling.set_name("comboboxtext_11_sampling")
        comboboxtext_11_sampling.set_hexpand(True)
        comboboxtext_11_sampling.set_active(1)

        def change_handler_11_sampling(source, **args):  # noqa
            pass
        comboboxtext_11_sampling.connect(SIG_CHANGED, change_handler_11_sampling)

        def setter_11_sampling(a_val: str):
            nonlocal combo_values_11_sampling
            selected_index = combo_values_11_sampling.index(a_val)
            comboboxtext_11_sampling.set_active(selected_index)
        widget_getters[comboboxtext_11_sampling.get_name()] = comboboxtext_11_sampling.get_active_text  # noqa
        widget_setters[comboboxtext_11_sampling.get_name()] = setter_11_sampling  # noqa

        checkbutton_11_zsnr: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Zsnr")  # noqa
        checkbutton_11_zsnr.set_active(False)
        checkbutton_11_zsnr.set_name("checkbutton_11_zsnr")
        checkbutton_11_zsnr.set_hexpand(False)

        def toggled_handler_11_zsnr(source, **args):  # noqa
            pass
        checkbutton_11_zsnr.connect(SIG_TOGGLED, toggled_handler_11_zsnr)

        def getter_11_zsnr():
            return checkbutton_11_zsnr.get_active()
        widget_getters[checkbutton_11_zsnr.get_name()] = getter_11_zsnr  # noqa

        grid_11: Gtk.Grid = Gtk.Grid.new()
        grid_11.attach(label_11_sampling,        left=0, top=0, width=1, height=1)  # noqa
        grid_11.attach(comboboxtext_11_sampling, left=1, top=0, width=3, height=1)  # noqa
        grid_11.attach(checkbutton_11_zsnr,      left=0, top=1, width=4, height=1)  # noqa
        grid_11.set_column_homogeneous(False)
        grid_11.set_row_homogeneous(False)
        frame_modelsamplingdiscrete_011modelsamplingdiscrete.add(widget=grid_11)  # noqa

        # New Frame
        frame_ksampler_012ksampler: Gtk.Frame = Gtk.Frame.new(label="KSampler        #12")  # noqa
        frame_ksampler_012ksampler.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_12_seed: Gtk.Label = Gtk.Label.new("Seed")
        label_12_seed.set_margin_start(8)
        label_12_seed.set_alignment(0.95, 0)
        entry_12_seed: Gtk.Entry = Gtk.Entry.new()
        entry_12_seed.set_text(str(175199165615730))
        entry_12_seed.set_name("entry_12_seed")
        entry_12_seed.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_12_seed,
                           minimum=-1, maximum=18446744073709519872,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_12_seed(source, **args):  # noqa
            pass
        entry_12_seed.connect(SIG_CHANGED, change_handler_12_seed)

        def getter_12_seed() -> int:
            return int(entry_12_seed.get_text())

        def setter_12_seed(a_val: int):
            entry_12_seed.set_text(str(a_val))
        widget_getters[entry_12_seed.get_name()] = getter_12_seed  # noqa
        widget_setters[entry_12_seed.get_name()] = setter_12_seed  # noqa

        label_12_steps: Gtk.Label = Gtk.Label.new("Steps")
        label_12_steps.set_margin_start(8)
        label_12_steps.set_alignment(0.95, 0)
        entry_12_steps: Gtk.Entry = Gtk.Entry.new()
        entry_12_steps.set_text(str(40))
        entry_12_steps.set_name("entry_12_steps")
        entry_12_steps.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_12_steps,
                           minimum=1, maximum=128,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_12_steps(source, **args):  # noqa
            pass
        entry_12_steps.connect(SIG_CHANGED, change_handler_12_steps)

        def getter_12_steps() -> int:
            return int(entry_12_steps.get_text())

        def setter_12_steps(a_val: int):
            entry_12_steps.set_text(str(a_val))
        widget_getters[entry_12_steps.get_name()] = getter_12_steps  # noqa
        widget_setters[entry_12_steps.get_name()] = setter_12_steps  # noqa

        label_12_cfg: Gtk.Label = Gtk.Label.new("Cfg")
        label_12_cfg.set_margin_start(8)
        adjustment_12_cfg: Gtk.Adjustment = Gtk.Adjustment(value=6.10000,
                                                           lower=1.00000,
                                                           upper=25.00000,
                                                           step_increment=0.100,
                                                           page_increment=2.000,
                                                           page_size=0)
        scale_12_cfg: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_12_cfg)  # noqa
        scale_12_cfg.set_name("scale_12_cfg")
        scale_12_cfg.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_12_cfg.set_hexpand(True)

        def change_handler_12_cfg(source, **args):  # noqa
            pass
        scale_12_cfg.connect(SIG_VALUE_CHANGED, change_handler_12_cfg)
        widget_getters[scale_12_cfg.get_name()] = scale_12_cfg.get_value
        widget_setters[scale_12_cfg.get_name()] = scale_12_cfg.set_value

        label_12_sampler_name: Gtk.Label = Gtk.Label.new("Sampler_Name")
        comboboxtext_12_sampler_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_12_sampler_name: list[str] = ["euler", "euler_ancestral", "heun", "heunpp2", "dpm_2", "dpm_2_ancestral", "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_sde", "dpmpp_sde_gpu", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu", "ddpm", "lcm", "ddim", "uni_pc", "uni_pc_bh2"]  # noqa
        for combo_item_path in combo_values_12_sampler_name:
            comboboxtext_12_sampler_name.append_text(combo_item_path)
        comboboxtext_12_sampler_name.set_name("comboboxtext_12_sampler_name")
        comboboxtext_12_sampler_name.set_hexpand(True)
        comboboxtext_12_sampler_name.set_active(18)

        def change_handler_12_sampler_name(source, **args):  # noqa
            pass
        comboboxtext_12_sampler_name.connect(SIG_CHANGED, change_handler_12_sampler_name)

        def setter_12_sampler_name(a_val: str):
            nonlocal combo_values_12_sampler_name
            selected_index = combo_values_12_sampler_name.index(a_val)
            comboboxtext_12_sampler_name.set_active(selected_index)
        widget_getters[comboboxtext_12_sampler_name.get_name()] = comboboxtext_12_sampler_name.get_active_text  # noqa
        widget_setters[comboboxtext_12_sampler_name.get_name()] = setter_12_sampler_name  # noqa

        label_12_scheduler: Gtk.Label = Gtk.Label.new("Scheduler")
        comboboxtext_12_scheduler: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_12_scheduler: list[str] = ["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"]  # noqa
        for combo_item_path in combo_values_12_scheduler:
            comboboxtext_12_scheduler.append_text(combo_item_path)
        comboboxtext_12_scheduler.set_name("comboboxtext_12_scheduler")
        comboboxtext_12_scheduler.set_hexpand(True)
        comboboxtext_12_scheduler.set_active(1)

        def change_handler_12_scheduler(source, **args):  # noqa
            pass
        comboboxtext_12_scheduler.connect(SIG_CHANGED, change_handler_12_scheduler)

        def setter_12_scheduler(a_val: str):
            nonlocal combo_values_12_scheduler
            selected_index = combo_values_12_scheduler.index(a_val)
            comboboxtext_12_scheduler.set_active(selected_index)
        widget_getters[comboboxtext_12_scheduler.get_name()] = comboboxtext_12_scheduler.get_active_text  # noqa
        widget_setters[comboboxtext_12_scheduler.get_name()] = setter_12_scheduler  # noqa

        label_12_denoise: Gtk.Label = Gtk.Label.new("Denoise")
        label_12_denoise.set_margin_start(8)
        label_12_denoise.set_alignment(0.95, 0)
        adjustment_12_denoise: Gtk.Adjustment = Gtk.Adjustment(value=1.00000,
                                                               lower=0.00001,
                                                               upper=1.00000,
                                                               step_increment=0.001,
                                                               page_increment=0.010,
                                                               page_size=0)
        scale_12_denoise: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_12_denoise)  # noqa
        scale_12_denoise.set_name("scale_12_denoise")
        scale_12_denoise.set_digits(3)
        scale_12_denoise.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_12_denoise.set_hexpand(True)

        def change_handler_12_denoise(source, **args):  # noqa
            pass
        scale_12_denoise.connect(SIG_VALUE_CHANGED, change_handler_12_denoise)
        widget_getters[scale_12_denoise.get_name()] = scale_12_denoise.get_value
        widget_setters[scale_12_denoise.get_name()] = scale_12_denoise.set_value

        grid_12: Gtk.Grid = Gtk.Grid.new()
        grid_12.attach(label_12_seed,                left=0, top=0, width=1, height=1)  # noqa
        grid_12.attach(entry_12_seed,                left=1, top=0, width=3, height=1)  # noqa
        grid_12.attach(label_12_steps,               left=0, top=1, width=1, height=1)  # noqa
        grid_12.attach(entry_12_steps,               left=1, top=1, width=3, height=1)  # noqa
        grid_12.attach(label_12_cfg,                 left=0, top=2, width=1, height=1)  # noqa
        grid_12.attach(scale_12_cfg,                 left=1, top=2, width=3, height=1)  # noqa
        grid_12.attach(label_12_sampler_name,        left=0, top=3, width=1, height=1)  # noqa
        grid_12.attach(comboboxtext_12_sampler_name, left=1, top=3, width=3, height=1)  # noqa
        grid_12.attach(label_12_scheduler,           left=0, top=4, width=1, height=1)  # noqa
        grid_12.attach(comboboxtext_12_scheduler,    left=1, top=4, width=3, height=1)  # noqa
        grid_12.attach(label_12_denoise,             left=0, top=5, width=1, height=1)  # noqa
        grid_12.attach(scale_12_denoise,             left=1, top=5, width=3, height=1)  # noqa
        grid_12.set_column_homogeneous(False)
        grid_12.set_row_homogeneous(False)
        frame_ksampler_012ksampler.add(widget=grid_12)  # noqa

        # New Frame
        frame_saveimage_014save_image: Gtk.Frame = Gtk.Frame.new(label="Save Image        #14")  # noqa
        frame_saveimage_014save_image.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_14_filename_prefix: Gtk.Label = Gtk.Label.new("Filename_Prefix")
        entry_14_filename_prefix: Gtk.Entry = Gtk.Entry.new()
        entry_14_filename_prefix.set_text("gimp_generated")
        entry_14_filename_prefix.set_name("entry_14_filename_prefix")
        entry_14_filename_prefix.set_hexpand(True)
        widget_getters[entry_14_filename_prefix.get_name()] = entry_14_filename_prefix.get_text
        widget_setters[entry_14_filename_prefix.get_name()] = entry_14_filename_prefix.set_text

        grid_14: Gtk.Grid = Gtk.Grid.new()
        grid_14.attach(label_14_filename_prefix, left=0, top=0, width=1, height=1)  # noqa
        grid_14.attach(entry_14_filename_prefix, left=1, top=0, width=3, height=1)  # noqa
        grid_14.set_column_homogeneous(False)
        grid_14.set_row_homogeneous(False)
        frame_saveimage_014save_image.add(widget=grid_14)  # noqa

        content_area: Gtk.Box = dialog.get_content_area()
        main_scrollable: Gtk.ScrolledWindow = Gtk.ScrolledWindow()
        subject_box: Gtk.Box = Gtk.Box()
        subject_box.set_orientation(Gtk.Orientation.VERTICAL)

        subject_box.pack_start(child=frame_loadimage_001base_image, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_loadimage_002mask_image, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_vaeencodeforinpaint_004vae_encode_for_inpainting, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_checkpointloadersimple_005load_checkpoint, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_unetloader_006load_diffusion_model, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_loraloader_007load_lora, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_cliptextencode_009positive_prompt, expand=True, fill=True, padding=0)  # noqa
        subject_box.pack_start(child=frame_cliptextencode_010negative_prompt, expand=True, fill=True, padding=0)  # noqa
        subject_box.pack_start(child=frame_modelsamplingdiscrete_011modelsamplingdiscrete, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_ksampler_012ksampler, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_saveimage_014save_image, expand=False, fill=False, padding=0)  # noqa

        subject_box.set_vexpand(True)
        subject_box.set_hexpand(True)
        main_scrollable.add(subject_box)  # noqa
        main_scrollable.set_size_request(1280, 928)
        main_scrollable.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        content_area.add(main_scrollable)  # noqa

        button_cancel.connect("clicked", delete_results)
        button_apply.connect("clicked", assign_results)
        button_ok.connect("clicked", assign_results)

        progress_bar: GimpUi.ProgressBar = GimpUi.ProgressBar.new()
        progress_bar.set_hexpand(True)
        progress_bar.set_show_text(True)
        dialog_box.add(progress_bar)
        progress_bar.show()

        geometry = Gdk.Geometry()  # noqa
        geometry.min_aspect = 0.5
        geometry.max_aspect = 1.0
        dialog.set_geometry_hints(None, geometry, Gdk.WindowHints.ASPECT)  # noqa
        fill_widget_values()
        dialog.show_all()
        return dialog
