
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


class FluxNegUpscaleSdxl0Dot5Dialogs(WorkflowDialogFactory):

    WORKFLOW_FILE = "flux_neg_upscale_sdxl_0.5_workflow_api.json"

    def __init__(self, accessor: NodesAccessor):
        super().__init__(
            accessor=accessor,
            api_workflow=FluxNegUpscaleSdxl0Dot5Dialogs.WORKFLOW_FILE,
            dialog_config_chassis_name="FluxNegUpscaleSdxl0Dot5Dialogs_dialog_config",
            wf_data_chassis_name="FluxNegUpscaleSdxl0Dot5Dialogs_wf_data",
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
                                                     chassis_name="flux_neg_upscale_sdxl_0dot5_dialog",
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
        frame_cliptextencode_006positive_prompt: Gtk.Frame = Gtk.Frame.new(label="Positive Prompt")  # noqa
        frame_cliptextencode_006positive_prompt.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_6_text: Gtk.Label = Gtk.Label.new("Text")
        textview_6_text: Gtk.TextView = Gtk.TextView.new()
        textview_6_text.get_buffer().set_text("photograph of a street where women ride scooters")  # noqa
        textview_6_text.set_name("textview_6_text")
        textview_6_text.set_hexpand(True)
        textview_6_text.set_vexpand(True)
        textview_6_text.set_valign(Gtk.Align.FILL)
        # Create a ScrolledWindow to hold the TextView
        scrolled_window_6_text = Gtk.ScrolledWindow()
        scrolled_window_6_text.add(textview_6_text)  # noqa
        scrolled_window_6_text.set_size_request(864, 288)

        def preedit_handler_6_text(source, **args):  # noqa
            pass
        textview_6_text.connect(SIG_PREEDIT_CHANGED, preedit_handler_6_text)

        def getter_6_text():
            buffer: Gtk.TextBuffer = textview_6_text.get_buffer()
            start: Gtk.TextIter = buffer.get_start_iter()
            end: Gtk.TextIter = buffer.get_end_iter()
            return buffer.get_text(start, end, False)

        def setter_6_text(a_val: str):
            textview_6_text.get_buffer().set_text(str(a_val))

        widget_getters[textview_6_text.get_name()] = getter_6_text
        widget_setters[textview_6_text.get_name()] = setter_6_text

        grid_6: Gtk.Grid = Gtk.Grid.new()
        grid_6.attach(label_6_text,           left=0, top=0, width=1, height=1)  # noqa
        grid_6.attach(scrolled_window_6_text, left=1, top=0, width=3, height=1)  # noqa
        grid_6.set_column_homogeneous(False)
        grid_6.set_row_homogeneous(False)
        frame_cliptextencode_006positive_prompt.add(widget=grid_6)  # noqa

        # New Frame
        frame_vaeloader_010load_vae: Gtk.Frame = Gtk.Frame.new(label="Load VAE")  # noqa
        frame_vaeloader_010load_vae.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_10_vae_name: Gtk.Label = Gtk.Label.new("Vae_Name")
        comboboxtext_10_vae_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_10_vae_name: list[str] = get_models_filenames(
            model_type=ModelType.VAE,
            cu_origin=self.comfy_svr_origin)
        if combo_values_10_vae_name is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_10_vae_name:
            raise ValueError(fr"No models retrieved from ComfyUI")  # noqa
        for combo_item_path in combo_values_10_vae_name:
            comboboxtext_10_vae_name.append_text(combo_item_path)
        comboboxtext_10_vae_name.set_name("comboboxtext_10_vae_name")
        comboboxtext_10_vae_name.set_hexpand(True)
        comboboxtext_10_vae_name.set_active(0)

        def change_handler_10_vae_name(source, **args):  # noqa
            pass
        comboboxtext_10_vae_name.connect(SIG_CHANGED, change_handler_10_vae_name)

        def setter_10_vae_name(a_val: str):
            nonlocal combo_values_10_vae_name
            selected_index = combo_values_10_vae_name.index(a_val)
            comboboxtext_10_vae_name.set_active(selected_index)
        widget_getters[comboboxtext_10_vae_name.get_name()] = comboboxtext_10_vae_name.get_active_text  # noqa
        widget_setters[comboboxtext_10_vae_name.get_name()] = setter_10_vae_name  # noqa

        grid_10: Gtk.Grid = Gtk.Grid.new()
        grid_10.attach(label_10_vae_name,        left=0, top=0, width=1, height=1)  # noqa
        grid_10.attach(comboboxtext_10_vae_name, left=1, top=0, width=3, height=1)  # noqa
        grid_10.set_column_homogeneous(False)
        grid_10.set_row_homogeneous(False)
        frame_vaeloader_010load_vae.add(widget=grid_10)  # noqa

        # New Frame
        frame_dualcliploader_011dualcliploader: Gtk.Frame = Gtk.Frame.new(label="DualCLIPLoader")  # noqa
        frame_dualcliploader_011dualcliploader.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_11_clip_name1: Gtk.Label = Gtk.Label.new("Clip_Name1")
        comboboxtext_11_clip_name1: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_11_clip_name1: list[str] = get_models_filenames(
            model_type=ModelType.CLIP,
            cu_origin=self.comfy_svr_origin)
        if combo_values_11_clip_name1 is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_11_clip_name1:
            raise ValueError(fr"No models retrieved from ComfyUI")  # noqa
        for combo_item_path in combo_values_11_clip_name1:
            comboboxtext_11_clip_name1.append_text(combo_item_path)
        comboboxtext_11_clip_name1.set_name("comboboxtext_11_clip_name1")
        comboboxtext_11_clip_name1.set_hexpand(True)
        comboboxtext_11_clip_name1.set_active(1)

        def change_handler_11_clip_name1(source, **args):  # noqa
            pass
        comboboxtext_11_clip_name1.connect(SIG_CHANGED, change_handler_11_clip_name1)

        def setter_11_clip_name1(a_val: str):
            nonlocal combo_values_11_clip_name1
            selected_index = combo_values_11_clip_name1.index(a_val)
            comboboxtext_11_clip_name1.set_active(selected_index)
        widget_getters[comboboxtext_11_clip_name1.get_name()] = comboboxtext_11_clip_name1.get_active_text  # noqa
        widget_setters[comboboxtext_11_clip_name1.get_name()] = setter_11_clip_name1  # noqa

        label_11_clip_name2: Gtk.Label = Gtk.Label.new("Clip_Name2")
        comboboxtext_11_clip_name2: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_11_clip_name2: list[str] = get_models_filenames(
            model_type=ModelType.CLIP,
            cu_origin=self.comfy_svr_origin)
        if combo_values_11_clip_name2 is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_11_clip_name2:
            raise ValueError(fr"No models retrieved from ComfyUI")  # noqa
        for combo_item_path in combo_values_11_clip_name2:
            comboboxtext_11_clip_name2.append_text(combo_item_path)
        comboboxtext_11_clip_name2.set_name("comboboxtext_11_clip_name2")
        comboboxtext_11_clip_name2.set_hexpand(True)
        comboboxtext_11_clip_name2.set_active(0)

        def change_handler_11_clip_name2(source, **args):  # noqa
            pass
        comboboxtext_11_clip_name2.connect(SIG_CHANGED, change_handler_11_clip_name2)

        def setter_11_clip_name2(a_val: str):
            nonlocal combo_values_11_clip_name2
            selected_index = combo_values_11_clip_name2.index(a_val)
            comboboxtext_11_clip_name2.set_active(selected_index)
        widget_getters[comboboxtext_11_clip_name2.get_name()] = comboboxtext_11_clip_name2.get_active_text  # noqa
        widget_setters[comboboxtext_11_clip_name2.get_name()] = setter_11_clip_name2  # noqa

        label_11_type: Gtk.Label = Gtk.Label.new("Type")
        comboboxtext_11_type: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_11_type: list[str] = ["sdxl", "sd3", "flux", "sd3.5"]  # noqa
        for combo_item_path in combo_values_11_type:
            comboboxtext_11_type.append_text(combo_item_path)
        comboboxtext_11_type.set_name("comboboxtext_11_type")
        comboboxtext_11_type.set_hexpand(True)
        comboboxtext_11_type.set_active(2)

        def change_handler_11_type(source, **args):  # noqa
            pass
        comboboxtext_11_type.connect(SIG_CHANGED, change_handler_11_type)

        def setter_11_type(a_val: str):
            nonlocal combo_values_11_type
            selected_index = combo_values_11_type.index(a_val)
            comboboxtext_11_type.set_active(selected_index)
        widget_getters[comboboxtext_11_type.get_name()] = comboboxtext_11_type.get_active_text  # noqa
        widget_setters[comboboxtext_11_type.get_name()] = setter_11_type  # noqa

        grid_11: Gtk.Grid = Gtk.Grid.new()
        grid_11.attach(label_11_clip_name1,        left=0, top=0, width=1, height=1)  # noqa
        grid_11.attach(comboboxtext_11_clip_name1, left=1, top=0, width=3, height=1)  # noqa
        grid_11.attach(label_11_clip_name2,        left=4, top=0, width=1, height=1)  # noqa
        grid_11.attach(comboboxtext_11_clip_name2, left=5, top=0, width=3, height=1)  # noqa
        grid_11.attach(label_11_type,              left=0, top=1, width=1, height=1)  # noqa
        grid_11.attach(comboboxtext_11_type,       left=1, top=1, width=7, height=1)  # noqa
        grid_11.set_column_homogeneous(False)
        grid_11.set_row_homogeneous(False)
        frame_dualcliploader_011dualcliploader.add(widget=grid_11)  # noqa

        # New Frame
        frame_unetloader_012load_diffusion_model: Gtk.Frame = Gtk.Frame.new(label="Load Diffusion Model")  # noqa
        frame_unetloader_012load_diffusion_model.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_12_unet_name: Gtk.Label = Gtk.Label.new("Unet_Name")
        comboboxtext_12_unet_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_12_unet_name: list[str] = get_models_filenames(
            model_type=ModelType.UNET,
            cu_origin=self.comfy_svr_origin)
        if combo_values_12_unet_name is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_12_unet_name:
            raise ValueError(fr"No models retrieved from ComfyUI")  # noqa
        for combo_item_path in combo_values_12_unet_name:
            comboboxtext_12_unet_name.append_text(combo_item_path)
        comboboxtext_12_unet_name.set_name("comboboxtext_12_unet_name")
        comboboxtext_12_unet_name.set_hexpand(True)
        comboboxtext_12_unet_name.set_active(1)

        def change_handler_12_unet_name(source, **args):  # noqa
            pass
        comboboxtext_12_unet_name.connect(SIG_CHANGED, change_handler_12_unet_name)

        def setter_12_unet_name(a_val: str):
            nonlocal combo_values_12_unet_name
            selected_index = combo_values_12_unet_name.index(a_val)
            comboboxtext_12_unet_name.set_active(selected_index)
        widget_getters[comboboxtext_12_unet_name.get_name()] = comboboxtext_12_unet_name.get_active_text  # noqa
        widget_setters[comboboxtext_12_unet_name.get_name()] = setter_12_unet_name  # noqa

        label_12_weight_dtype: Gtk.Label = Gtk.Label.new("Weight_Dtype")
        comboboxtext_12_weight_dtype: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_12_weight_dtype: list[str] = ["default", "fp8_e4m3fn", "fp8_e5m2"]  # noqa
        for combo_item_path in combo_values_12_weight_dtype:
            comboboxtext_12_weight_dtype.append_text(combo_item_path)
        comboboxtext_12_weight_dtype.set_name("comboboxtext_12_weight_dtype")
        comboboxtext_12_weight_dtype.set_hexpand(True)
        comboboxtext_12_weight_dtype.set_active(1)

        def change_handler_12_weight_dtype(source, **args):  # noqa
            pass
        comboboxtext_12_weight_dtype.connect(SIG_CHANGED, change_handler_12_weight_dtype)

        def setter_12_weight_dtype(a_val: str):
            nonlocal combo_values_12_weight_dtype
            selected_index = combo_values_12_weight_dtype.index(a_val)
            comboboxtext_12_weight_dtype.set_active(selected_index)
        widget_getters[comboboxtext_12_weight_dtype.get_name()] = comboboxtext_12_weight_dtype.get_active_text  # noqa
        widget_setters[comboboxtext_12_weight_dtype.get_name()] = setter_12_weight_dtype  # noqa

        grid_12: Gtk.Grid = Gtk.Grid.new()
        grid_12.attach(label_12_unet_name,           left=0, top=0, width=1, height=1)  # noqa
        grid_12.attach(comboboxtext_12_unet_name,    left=1, top=0, width=3, height=1)  # noqa
        grid_12.attach(label_12_weight_dtype,        left=4, top=0, width=1, height=1)  # noqa
        grid_12.attach(comboboxtext_12_weight_dtype, left=5, top=0, width=3, height=1)  # noqa
        grid_12.set_column_homogeneous(False)
        grid_12.set_row_homogeneous(False)
        frame_unetloader_012load_diffusion_model.add(widget=grid_12)  # noqa

        # New Frame
        frame_tobasicpipe_047tobasicpipe: Gtk.Frame = Gtk.Frame.new(label="ToBasicPipe")  # noqa
        frame_tobasicpipe_047tobasicpipe.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        grid_47: Gtk.Grid = Gtk.Grid.new()
        grid_47.set_column_homogeneous(False)
        grid_47.set_row_homogeneous(False)
        frame_tobasicpipe_047tobasicpipe.add(widget=grid_47)  # noqa

        # New Frame
        frame_emptylatentimage_049empty_latent_image: Gtk.Frame = Gtk.Frame.new(label="Empty Latent Image")  # noqa
        frame_emptylatentimage_049empty_latent_image.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_49_width: Gtk.Label = Gtk.Label.new("Width")
        label_49_width.set_margin_start(8)
        label_49_width.set_alignment(0.95, 0)
        entry_49_width: Gtk.Entry = Gtk.Entry.new()
        entry_49_width.set_text(str(1024))
        entry_49_width.set_name("entry_49_width")
        entry_49_width.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_49_width,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_49_width(source, **args):  # noqa
            pass
        entry_49_width.connect(SIG_CHANGED, change_handler_49_width)

        def getter_49_width() -> int:
            return int(entry_49_width.get_text())

        def setter_49_width(a_val: int):
            entry_49_width.set_text(str(a_val))
        widget_getters[entry_49_width.get_name()] = getter_49_width  # noqa
        widget_setters[entry_49_width.get_name()] = setter_49_width  # noqa

        label_49_height: Gtk.Label = Gtk.Label.new("Height")
        label_49_height.set_margin_start(8)
        label_49_height.set_alignment(0.95, 0)
        entry_49_height: Gtk.Entry = Gtk.Entry.new()
        entry_49_height.set_text(str(1024))
        entry_49_height.set_name("entry_49_height")
        entry_49_height.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_49_height,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_49_height(source, **args):  # noqa
            pass
        entry_49_height.connect(SIG_CHANGED, change_handler_49_height)

        def getter_49_height() -> int:
            return int(entry_49_height.get_text())

        def setter_49_height(a_val: int):
            entry_49_height.set_text(str(a_val))
        widget_getters[entry_49_height.get_name()] = getter_49_height  # noqa
        widget_setters[entry_49_height.get_name()] = setter_49_height  # noqa

        label_49_batch_size: Gtk.Label = Gtk.Label.new("Batch_Size")
        label_49_batch_size.set_margin_start(8)
        label_49_batch_size.set_alignment(0.95, 0)
        entry_49_batch_size: Gtk.Entry = Gtk.Entry.new()
        entry_49_batch_size.set_text(str(1))
        entry_49_batch_size.set_name("entry_49_batch_size")
        entry_49_batch_size.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_49_batch_size,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_49_batch_size(source, **args):  # noqa
            pass
        entry_49_batch_size.connect(SIG_CHANGED, change_handler_49_batch_size)

        def getter_49_batch_size() -> int:
            return int(entry_49_batch_size.get_text())

        def setter_49_batch_size(a_val: int):
            entry_49_batch_size.set_text(str(a_val))
        widget_getters[entry_49_batch_size.get_name()] = getter_49_batch_size  # noqa
        widget_setters[entry_49_batch_size.get_name()] = setter_49_batch_size  # noqa

        grid_49: Gtk.Grid = Gtk.Grid.new()
        grid_49.attach(label_49_width,      left=0, top=0, width=1, height=1)  # noqa
        grid_49.attach(entry_49_width,      left=1, top=0, width=3, height=1)  # noqa
        grid_49.attach(label_49_height,     left=4, top=0, width=1, height=1)  # noqa
        grid_49.attach(entry_49_height,     left=5, top=0, width=3, height=1)  # noqa
        grid_49.attach(label_49_batch_size, left=8, top=0, width=1, height=1)  # noqa
        grid_49.attach(entry_49_batch_size, left=9, top=0, width=3, height=1)  # noqa
        grid_49.set_column_homogeneous(False)
        grid_49.set_row_homogeneous(False)
        frame_emptylatentimage_049empty_latent_image.add(widget=grid_49)  # noqa

        # New Frame
        frame_impactksampleradvancedbasicpipe_097ksampler_pass2_advancedpipe: Gtk.Frame = Gtk.Frame.new(label="KSampler Pass2 (Advanced/pipe)")  # noqa
        frame_impactksampleradvancedbasicpipe_097ksampler_pass2_advancedpipe.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        checkbutton_97_add_noise: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Add Noise")  # noqa
        checkbutton_97_add_noise.set_active(False)
        checkbutton_97_add_noise.set_name("checkbutton_97_add_noise")
        checkbutton_97_add_noise.set_hexpand(False)

        def toggled_handler_97_add_noise(source, **args):  # noqa
            pass
        checkbutton_97_add_noise.connect(SIG_TOGGLED, toggled_handler_97_add_noise)

        def getter_97_add_noise():
            return "enable" if checkbutton_97_add_noise.get_active() else "disable"
        widget_getters[checkbutton_97_add_noise.get_name()] = getter_97_add_noise  # noqa

        label_97_noise_seed: Gtk.Label = Gtk.Label.new("Noise_Seed")
        label_97_noise_seed.set_margin_start(8)
        label_97_noise_seed.set_alignment(0.95, 0)
        entry_97_noise_seed: Gtk.Entry = Gtk.Entry.new()
        entry_97_noise_seed.set_text(str(197))
        entry_97_noise_seed.set_name("entry_97_noise_seed")
        entry_97_noise_seed.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_97_noise_seed,
                           minimum=-1, maximum=18446744073709519872,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_97_noise_seed(source, **args):  # noqa
            pass
        entry_97_noise_seed.connect(SIG_CHANGED, change_handler_97_noise_seed)

        def getter_97_noise_seed() -> int:
            return int(entry_97_noise_seed.get_text())

        def setter_97_noise_seed(a_val: int):
            entry_97_noise_seed.set_text(str(a_val))
        widget_getters[entry_97_noise_seed.get_name()] = getter_97_noise_seed  # noqa
        widget_setters[entry_97_noise_seed.get_name()] = setter_97_noise_seed  # noqa

        label_97_steps: Gtk.Label = Gtk.Label.new("Steps")
        label_97_steps.set_margin_start(8)
        label_97_steps.set_alignment(0.95, 0)
        entry_97_steps: Gtk.Entry = Gtk.Entry.new()
        entry_97_steps.set_text(str(20))
        entry_97_steps.set_name("entry_97_steps")
        entry_97_steps.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_97_steps,
                           minimum=1, maximum=128,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_97_steps(source, **args):  # noqa
            pass
        entry_97_steps.connect(SIG_CHANGED, change_handler_97_steps)

        def getter_97_steps() -> int:
            return int(entry_97_steps.get_text())

        def setter_97_steps(a_val: int):
            entry_97_steps.set_text(str(a_val))
        widget_getters[entry_97_steps.get_name()] = getter_97_steps  # noqa
        widget_setters[entry_97_steps.get_name()] = setter_97_steps  # noqa

        label_97_cfg: Gtk.Label = Gtk.Label.new("Cfg")
        label_97_cfg.set_margin_start(8)
        label_97_cfg.set_alignment(0.95, 0)
        adjustment_97_cfg: Gtk.Adjustment = Gtk.Adjustment(value=8.00000,
                                                           lower=1.00000,
                                                           upper=25.00000,
                                                           step_increment=0.100,
                                                           page_increment=2.000,
                                                           page_size=0)
        scale_97_cfg: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_97_cfg)  # noqa
        scale_97_cfg.set_name("scale_97_cfg")
        scale_97_cfg.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_97_cfg.set_hexpand(True)

        def change_handler_97_cfg(source, **args):  # noqa
            pass
        scale_97_cfg.connect(SIG_VALUE_CHANGED, change_handler_97_cfg)
        widget_getters[scale_97_cfg.get_name()] = scale_97_cfg.get_value
        widget_setters[scale_97_cfg.get_name()] = scale_97_cfg.set_value

        label_97_sampler_name: Gtk.Label = Gtk.Label.new("Sampler_Name")
        comboboxtext_97_sampler_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_97_sampler_name: list[str] = ["euler", "euler_ancestral", "heun", "heunpp2", "dpm_2", "dpm_2_ancestral", "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_sde", "dpmpp_sde_gpu", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu", "ddpm", "lcm", "ddim", "uni_pc", "uni_pc_bh2"]  # noqa
        for combo_item_path in combo_values_97_sampler_name:
            comboboxtext_97_sampler_name.append_text(combo_item_path)
        comboboxtext_97_sampler_name.set_name("comboboxtext_97_sampler_name")
        comboboxtext_97_sampler_name.set_hexpand(True)
        comboboxtext_97_sampler_name.set_active(0)

        def change_handler_97_sampler_name(source, **args):  # noqa
            pass
        comboboxtext_97_sampler_name.connect(SIG_CHANGED, change_handler_97_sampler_name)

        def setter_97_sampler_name(a_val: str):
            nonlocal combo_values_97_sampler_name
            selected_index = combo_values_97_sampler_name.index(a_val)
            comboboxtext_97_sampler_name.set_active(selected_index)
        widget_getters[comboboxtext_97_sampler_name.get_name()] = comboboxtext_97_sampler_name.get_active_text  # noqa
        widget_setters[comboboxtext_97_sampler_name.get_name()] = setter_97_sampler_name  # noqa

        label_97_scheduler: Gtk.Label = Gtk.Label.new("Scheduler")
        comboboxtext_97_scheduler: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_97_scheduler: list[str] = ["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"]  # noqa
        for combo_item_path in combo_values_97_scheduler:
            comboboxtext_97_scheduler.append_text(combo_item_path)
        comboboxtext_97_scheduler.set_name("comboboxtext_97_scheduler")
        comboboxtext_97_scheduler.set_hexpand(True)
        comboboxtext_97_scheduler.set_active(0)

        def change_handler_97_scheduler(source, **args):  # noqa
            pass
        comboboxtext_97_scheduler.connect(SIG_CHANGED, change_handler_97_scheduler)

        def setter_97_scheduler(a_val: str):
            nonlocal combo_values_97_scheduler
            selected_index = combo_values_97_scheduler.index(a_val)
            comboboxtext_97_scheduler.set_active(selected_index)
        widget_getters[comboboxtext_97_scheduler.get_name()] = comboboxtext_97_scheduler.get_active_text  # noqa
        widget_setters[comboboxtext_97_scheduler.get_name()] = setter_97_scheduler  # noqa

        label_97_start_at_step: Gtk.Label = Gtk.Label.new("Start_At_Step")
        label_97_start_at_step.set_margin_start(8)
        label_97_start_at_step.set_alignment(0.95, 0)
        entry_97_start_at_step: Gtk.Entry = Gtk.Entry.new()
        entry_97_start_at_step.set_text(str(3))
        entry_97_start_at_step.set_name("entry_97_start_at_step")
        entry_97_start_at_step.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_97_start_at_step,
                           minimum=0, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_97_start_at_step(source, **args):  # noqa
            pass
        entry_97_start_at_step.connect(SIG_CHANGED, change_handler_97_start_at_step)

        def getter_97_start_at_step() -> int:
            return int(entry_97_start_at_step.get_text())

        def setter_97_start_at_step(a_val: int):
            entry_97_start_at_step.set_text(str(a_val))
        widget_getters[entry_97_start_at_step.get_name()] = getter_97_start_at_step  # noqa
        widget_setters[entry_97_start_at_step.get_name()] = setter_97_start_at_step  # noqa

        label_97_end_at_step: Gtk.Label = Gtk.Label.new("End_At_Step")
        label_97_end_at_step.set_margin_start(8)
        label_97_end_at_step.set_alignment(0.95, 0)
        entry_97_end_at_step: Gtk.Entry = Gtk.Entry.new()
        entry_97_end_at_step.set_text(str(10000))
        entry_97_end_at_step.set_name("entry_97_end_at_step")
        entry_97_end_at_step.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_97_end_at_step,
                           minimum=0, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_97_end_at_step(source, **args):  # noqa
            pass
        entry_97_end_at_step.connect(SIG_CHANGED, change_handler_97_end_at_step)

        def getter_97_end_at_step() -> int:
            return int(entry_97_end_at_step.get_text())

        def setter_97_end_at_step(a_val: int):
            entry_97_end_at_step.set_text(str(a_val))
        widget_getters[entry_97_end_at_step.get_name()] = getter_97_end_at_step  # noqa
        widget_setters[entry_97_end_at_step.get_name()] = setter_97_end_at_step  # noqa

        checkbutton_97_return_with_leftover_noise: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Return With Leftover Noise")  # noqa
        checkbutton_97_return_with_leftover_noise.set_active(False)
        checkbutton_97_return_with_leftover_noise.set_name("checkbutton_97_return_with_leftover_noise")
        checkbutton_97_return_with_leftover_noise.set_hexpand(False)

        def toggled_handler_97_return_with_leftover_noise(source, **args):  # noqa
            pass
        checkbutton_97_return_with_leftover_noise.connect(SIG_TOGGLED, toggled_handler_97_return_with_leftover_noise)

        def getter_97_return_with_leftover_noise():
            return "enable" if checkbutton_97_return_with_leftover_noise.get_active() else "disable"
        widget_getters[checkbutton_97_return_with_leftover_noise.get_name()] = getter_97_return_with_leftover_noise  # noqa

        grid_97: Gtk.Grid = Gtk.Grid.new()
        grid_97.attach(checkbutton_97_add_noise,                  left=0, top=0, width=4, height=1)  # noqa
        grid_97.attach(label_97_noise_seed,                       left=0, top=1, width=1, height=1)  # noqa
        grid_97.attach(entry_97_noise_seed,                       left=1, top=1, width=3, height=1)  # noqa
        grid_97.attach(label_97_steps,                            left=0, top=2, width=1, height=1)  # noqa
        grid_97.attach(entry_97_steps,                            left=1, top=2, width=3, height=1)  # noqa
        grid_97.attach(label_97_cfg,                              left=0, top=3, width=1, height=1)  # noqa
        grid_97.attach(scale_97_cfg,                              left=1, top=3, width=3, height=1)  # noqa
        grid_97.attach(label_97_sampler_name,                     left=0, top=4, width=1, height=1)  # noqa
        grid_97.attach(comboboxtext_97_sampler_name,              left=1, top=4, width=3, height=1)  # noqa
        grid_97.attach(label_97_scheduler,                        left=0, top=5, width=1, height=1)  # noqa
        grid_97.attach(comboboxtext_97_scheduler,                 left=1, top=5, width=3, height=1)  # noqa
        grid_97.attach(label_97_start_at_step,                    left=0, top=6, width=1, height=1)  # noqa
        grid_97.attach(entry_97_start_at_step,                    left=1, top=6, width=3, height=1)  # noqa
        grid_97.attach(label_97_end_at_step,                      left=0, top=7, width=1, height=1)  # noqa
        grid_97.attach(entry_97_end_at_step,                      left=1, top=7, width=3, height=1)  # noqa
        grid_97.attach(checkbutton_97_return_with_leftover_noise, left=0, top=8, width=4, height=1)  # noqa
        grid_97.set_column_homogeneous(False)
        grid_97.set_row_homogeneous(False)
        frame_impactksampleradvancedbasicpipe_097ksampler_pass2_advancedpipe.add(widget=grid_97)  # noqa

        # New Frame
        frame_impactksampleradvancedbasicpipe_098ksampler_pass1_advancedpipe: Gtk.Frame = Gtk.Frame.new(label="KSampler Pass1 (Advanced/pipe)")  # noqa
        frame_impactksampleradvancedbasicpipe_098ksampler_pass1_advancedpipe.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        checkbutton_98_add_noise: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Add Noise")  # noqa
        checkbutton_98_add_noise.set_active(True)
        checkbutton_98_add_noise.set_name("checkbutton_98_add_noise")
        checkbutton_98_add_noise.set_hexpand(False)

        def toggled_handler_98_add_noise(source, **args):  # noqa
            pass
        checkbutton_98_add_noise.connect(SIG_TOGGLED, toggled_handler_98_add_noise)

        def getter_98_add_noise():
            return "enable" if checkbutton_98_add_noise.get_active() else "disable"
        widget_getters[checkbutton_98_add_noise.get_name()] = getter_98_add_noise  # noqa

        label_98_noise_seed: Gtk.Label = Gtk.Label.new("Noise_Seed")
        label_98_noise_seed.set_margin_start(8)
        label_98_noise_seed.set_alignment(0.95, 0)
        entry_98_noise_seed: Gtk.Entry = Gtk.Entry.new()
        entry_98_noise_seed.set_text(str(197))
        entry_98_noise_seed.set_name("entry_98_noise_seed")
        entry_98_noise_seed.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_98_noise_seed,
                           minimum=-1, maximum=18446744073709519872,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_98_noise_seed(source, **args):  # noqa
            pass
        entry_98_noise_seed.connect(SIG_CHANGED, change_handler_98_noise_seed)

        def getter_98_noise_seed() -> int:
            return int(entry_98_noise_seed.get_text())

        def setter_98_noise_seed(a_val: int):
            entry_98_noise_seed.set_text(str(a_val))
        widget_getters[entry_98_noise_seed.get_name()] = getter_98_noise_seed  # noqa
        widget_setters[entry_98_noise_seed.get_name()] = setter_98_noise_seed  # noqa

        label_98_steps: Gtk.Label = Gtk.Label.new("Steps")
        label_98_steps.set_margin_start(8)
        label_98_steps.set_alignment(0.95, 0)
        entry_98_steps: Gtk.Entry = Gtk.Entry.new()
        entry_98_steps.set_text(str(20))
        entry_98_steps.set_name("entry_98_steps")
        entry_98_steps.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_98_steps,
                           minimum=1, maximum=128,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_98_steps(source, **args):  # noqa
            pass
        entry_98_steps.connect(SIG_CHANGED, change_handler_98_steps)

        def getter_98_steps() -> int:
            return int(entry_98_steps.get_text())

        def setter_98_steps(a_val: int):
            entry_98_steps.set_text(str(a_val))
        widget_getters[entry_98_steps.get_name()] = getter_98_steps  # noqa
        widget_setters[entry_98_steps.get_name()] = setter_98_steps  # noqa

        label_98_cfg: Gtk.Label = Gtk.Label.new("Cfg")
        label_98_cfg.set_margin_start(8)
        label_98_cfg.set_alignment(0.95, 0)
        adjustment_98_cfg: Gtk.Adjustment = Gtk.Adjustment(value=8.00000,
                                                           lower=1.00000,
                                                           upper=25.00000,
                                                           step_increment=0.100,
                                                           page_increment=2.000,
                                                           page_size=0)
        scale_98_cfg: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_98_cfg)  # noqa
        scale_98_cfg.set_name("scale_98_cfg")
        scale_98_cfg.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_98_cfg.set_hexpand(True)

        def change_handler_98_cfg(source, **args):  # noqa
            pass
        scale_98_cfg.connect(SIG_VALUE_CHANGED, change_handler_98_cfg)
        widget_getters[scale_98_cfg.get_name()] = scale_98_cfg.get_value
        widget_setters[scale_98_cfg.get_name()] = scale_98_cfg.set_value

        label_98_sampler_name: Gtk.Label = Gtk.Label.new("Sampler_Name")
        comboboxtext_98_sampler_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_98_sampler_name: list[str] = ["euler", "euler_ancestral", "heun", "heunpp2", "dpm_2", "dpm_2_ancestral", "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_sde", "dpmpp_sde_gpu", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu", "ddpm", "lcm", "ddim", "uni_pc", "uni_pc_bh2"]  # noqa
        for combo_item_path in combo_values_98_sampler_name:
            comboboxtext_98_sampler_name.append_text(combo_item_path)
        comboboxtext_98_sampler_name.set_name("comboboxtext_98_sampler_name")
        comboboxtext_98_sampler_name.set_hexpand(True)
        comboboxtext_98_sampler_name.set_active(0)

        def change_handler_98_sampler_name(source, **args):  # noqa
            pass
        comboboxtext_98_sampler_name.connect(SIG_CHANGED, change_handler_98_sampler_name)

        def setter_98_sampler_name(a_val: str):
            nonlocal combo_values_98_sampler_name
            selected_index = combo_values_98_sampler_name.index(a_val)
            comboboxtext_98_sampler_name.set_active(selected_index)
        widget_getters[comboboxtext_98_sampler_name.get_name()] = comboboxtext_98_sampler_name.get_active_text  # noqa
        widget_setters[comboboxtext_98_sampler_name.get_name()] = setter_98_sampler_name  # noqa

        label_98_scheduler: Gtk.Label = Gtk.Label.new("Scheduler")
        comboboxtext_98_scheduler: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_98_scheduler: list[str] = ["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"]  # noqa
        for combo_item_path in combo_values_98_scheduler:
            comboboxtext_98_scheduler.append_text(combo_item_path)
        comboboxtext_98_scheduler.set_name("comboboxtext_98_scheduler")
        comboboxtext_98_scheduler.set_hexpand(True)
        comboboxtext_98_scheduler.set_active(0)

        def change_handler_98_scheduler(source, **args):  # noqa
            pass
        comboboxtext_98_scheduler.connect(SIG_CHANGED, change_handler_98_scheduler)

        def setter_98_scheduler(a_val: str):
            nonlocal combo_values_98_scheduler
            selected_index = combo_values_98_scheduler.index(a_val)
            comboboxtext_98_scheduler.set_active(selected_index)
        widget_getters[comboboxtext_98_scheduler.get_name()] = comboboxtext_98_scheduler.get_active_text  # noqa
        widget_setters[comboboxtext_98_scheduler.get_name()] = setter_98_scheduler  # noqa

        label_98_start_at_step: Gtk.Label = Gtk.Label.new("Start_At_Step")
        label_98_start_at_step.set_margin_start(8)
        label_98_start_at_step.set_alignment(0.95, 0)
        entry_98_start_at_step: Gtk.Entry = Gtk.Entry.new()
        entry_98_start_at_step.set_text(str(0))
        entry_98_start_at_step.set_name("entry_98_start_at_step")
        entry_98_start_at_step.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_98_start_at_step,
                           minimum=0, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_98_start_at_step(source, **args):  # noqa
            pass
        entry_98_start_at_step.connect(SIG_CHANGED, change_handler_98_start_at_step)

        def getter_98_start_at_step() -> int:
            return int(entry_98_start_at_step.get_text())

        def setter_98_start_at_step(a_val: int):
            entry_98_start_at_step.set_text(str(a_val))
        widget_getters[entry_98_start_at_step.get_name()] = getter_98_start_at_step  # noqa
        widget_setters[entry_98_start_at_step.get_name()] = setter_98_start_at_step  # noqa

        label_98_end_at_step: Gtk.Label = Gtk.Label.new("End_At_Step")
        label_98_end_at_step.set_margin_start(8)
        label_98_end_at_step.set_alignment(0.95, 0)
        entry_98_end_at_step: Gtk.Entry = Gtk.Entry.new()
        entry_98_end_at_step.set_text(str(3))
        entry_98_end_at_step.set_name("entry_98_end_at_step")
        entry_98_end_at_step.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_98_end_at_step,
                           minimum=0, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_98_end_at_step(source, **args):  # noqa
            pass
        entry_98_end_at_step.connect(SIG_CHANGED, change_handler_98_end_at_step)

        def getter_98_end_at_step() -> int:
            return int(entry_98_end_at_step.get_text())

        def setter_98_end_at_step(a_val: int):
            entry_98_end_at_step.set_text(str(a_val))
        widget_getters[entry_98_end_at_step.get_name()] = getter_98_end_at_step  # noqa
        widget_setters[entry_98_end_at_step.get_name()] = setter_98_end_at_step  # noqa

        checkbutton_98_return_with_leftover_noise: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Return With Leftover Noise")  # noqa
        checkbutton_98_return_with_leftover_noise.set_active(True)
        checkbutton_98_return_with_leftover_noise.set_name("checkbutton_98_return_with_leftover_noise")
        checkbutton_98_return_with_leftover_noise.set_hexpand(False)

        def toggled_handler_98_return_with_leftover_noise(source, **args):  # noqa
            pass
        checkbutton_98_return_with_leftover_noise.connect(SIG_TOGGLED, toggled_handler_98_return_with_leftover_noise)

        def getter_98_return_with_leftover_noise():
            return "enable" if checkbutton_98_return_with_leftover_noise.get_active() else "disable"
        widget_getters[checkbutton_98_return_with_leftover_noise.get_name()] = getter_98_return_with_leftover_noise  # noqa

        grid_98: Gtk.Grid = Gtk.Grid.new()
        grid_98.attach(checkbutton_98_add_noise,                  left=0, top=0, width=4, height=1)  # noqa
        grid_98.attach(label_98_noise_seed,                       left=0, top=1, width=1, height=1)  # noqa
        grid_98.attach(entry_98_noise_seed,                       left=1, top=1, width=3, height=1)  # noqa
        grid_98.attach(label_98_steps,                            left=0, top=2, width=1, height=1)  # noqa
        grid_98.attach(entry_98_steps,                            left=1, top=2, width=3, height=1)  # noqa
        grid_98.attach(label_98_cfg,                              left=0, top=3, width=1, height=1)  # noqa
        grid_98.attach(scale_98_cfg,                              left=1, top=3, width=3, height=1)  # noqa
        grid_98.attach(label_98_sampler_name,                     left=0, top=4, width=1, height=1)  # noqa
        grid_98.attach(comboboxtext_98_sampler_name,              left=1, top=4, width=3, height=1)  # noqa
        grid_98.attach(label_98_scheduler,                        left=0, top=5, width=1, height=1)  # noqa
        grid_98.attach(comboboxtext_98_scheduler,                 left=1, top=5, width=3, height=1)  # noqa
        grid_98.attach(label_98_start_at_step,                    left=0, top=6, width=1, height=1)  # noqa
        grid_98.attach(entry_98_start_at_step,                    left=1, top=6, width=3, height=1)  # noqa
        grid_98.attach(label_98_end_at_step,                      left=0, top=7, width=1, height=1)  # noqa
        grid_98.attach(entry_98_end_at_step,                      left=1, top=7, width=3, height=1)  # noqa
        grid_98.attach(checkbutton_98_return_with_leftover_noise, left=0, top=8, width=4, height=1)  # noqa
        grid_98.set_column_homogeneous(False)
        grid_98.set_row_homogeneous(False)
        frame_impactksampleradvancedbasicpipe_098ksampler_pass1_advancedpipe.add(widget=grid_98)  # noqa

        # New Frame
        frame_dynamicthresholdingfull_100dynamicthresholdingfull: Gtk.Frame = Gtk.Frame.new(label="DynamicThresholdingFull")  # noqa
        frame_dynamicthresholdingfull_100dynamicthresholdingfull.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_100_mimic_scale: Gtk.Label = Gtk.Label.new("Mimic_Scale")
        label_100_mimic_scale.set_margin_start(8)
        label_100_mimic_scale.set_alignment(0.95, 0)
        adjustment_100_mimic_scale: Gtk.Adjustment = Gtk.Adjustment(value=1.00000,
                                                                    lower=0.00000,
                                                                    upper=100.00000,
                                                                    step_increment=1.000,
                                                                    page_increment=10.000,
                                                                    page_size=0)
        scale_100_mimic_scale: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_100_mimic_scale)  # noqa
        scale_100_mimic_scale.set_name("scale_100_mimic_scale")
        scale_100_mimic_scale.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_100_mimic_scale.set_hexpand(True)

        def change_handler_100_mimic_scale(source, **args):  # noqa
            pass
        scale_100_mimic_scale.connect(SIG_VALUE_CHANGED, change_handler_100_mimic_scale)
        widget_getters[scale_100_mimic_scale.get_name()] = scale_100_mimic_scale.get_value
        widget_setters[scale_100_mimic_scale.get_name()] = scale_100_mimic_scale.set_value

        label_100_threshold_percentile: Gtk.Label = Gtk.Label.new("Threshold_Percentile")
        label_100_threshold_percentile.set_margin_start(8)
        label_100_threshold_percentile.set_alignment(0.95, 0)
        adjustment_100_threshold_percentile: Gtk.Adjustment = Gtk.Adjustment(value=1.00000,
                                                                             lower=0.00000,
                                                                             upper=1.00000,
                                                                             step_increment=0.010,
                                                                             page_increment=0.100,
                                                                             page_size=0)
        scale_100_threshold_percentile: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_100_threshold_percentile)  # noqa
        scale_100_threshold_percentile.set_name("scale_100_threshold_percentile")
        scale_100_threshold_percentile.set_digits(3)
        scale_100_threshold_percentile.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_100_threshold_percentile.set_hexpand(True)

        def change_handler_100_threshold_percentile(source, **args):  # noqa
            pass
        scale_100_threshold_percentile.connect(SIG_VALUE_CHANGED, change_handler_100_threshold_percentile)
        widget_getters[scale_100_threshold_percentile.get_name()] = scale_100_threshold_percentile.get_value
        widget_setters[scale_100_threshold_percentile.get_name()] = scale_100_threshold_percentile.set_value

        label_100_mimic_mode: Gtk.Label = Gtk.Label.new("Mimic_Mode")
        comboboxtext_100_mimic_mode: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_100_mimic_mode: list[str] = ["Constant", "Linear Down", "Cosine Down", "Half Cosine Down", "Linear Up", "Cosine Up", "Half Cosine Up", "Power Up", "Power Down", "Linear Repeating", "Cosine Repeating", "Sawtooth"]  # noqa
        for combo_item_path in combo_values_100_mimic_mode:
            comboboxtext_100_mimic_mode.append_text(combo_item_path)
        comboboxtext_100_mimic_mode.set_name("comboboxtext_100_mimic_mode")
        comboboxtext_100_mimic_mode.set_hexpand(True)
        comboboxtext_100_mimic_mode.set_active(11)

        def change_handler_100_mimic_mode(source, **args):  # noqa
            pass
        comboboxtext_100_mimic_mode.connect(SIG_CHANGED, change_handler_100_mimic_mode)

        def setter_100_mimic_mode(a_val: str):
            nonlocal combo_values_100_mimic_mode
            selected_index = combo_values_100_mimic_mode.index(a_val)
            comboboxtext_100_mimic_mode.set_active(selected_index)
        widget_getters[comboboxtext_100_mimic_mode.get_name()] = comboboxtext_100_mimic_mode.get_active_text  # noqa
        widget_setters[comboboxtext_100_mimic_mode.get_name()] = setter_100_mimic_mode  # noqa

        label_100_mimic_scale_min: Gtk.Label = Gtk.Label.new("Mimic_Scale_Min")
        label_100_mimic_scale_min.set_margin_start(8)
        label_100_mimic_scale_min.set_alignment(0.95, 0)
        adjustment_100_mimic_scale_min: Gtk.Adjustment = Gtk.Adjustment(value=0.00000,
                                                                        lower=0.00000,
                                                                        upper=1.00000,
                                                                        step_increment=0.010,
                                                                        page_increment=0.100,
                                                                        page_size=0)
        scale_100_mimic_scale_min: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_100_mimic_scale_min)  # noqa
        scale_100_mimic_scale_min.set_name("scale_100_mimic_scale_min")
        scale_100_mimic_scale_min.set_digits(3)
        scale_100_mimic_scale_min.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_100_mimic_scale_min.set_hexpand(True)

        def change_handler_100_mimic_scale_min(source, **args):  # noqa
            pass
        scale_100_mimic_scale_min.connect(SIG_VALUE_CHANGED, change_handler_100_mimic_scale_min)
        widget_getters[scale_100_mimic_scale_min.get_name()] = scale_100_mimic_scale_min.get_value
        widget_setters[scale_100_mimic_scale_min.get_name()] = scale_100_mimic_scale_min.set_value

        label_100_cfg_mode: Gtk.Label = Gtk.Label.new("Cfg_Mode")
        comboboxtext_100_cfg_mode: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_100_cfg_mode: list[str] = ["Constant", "Linear Down", "Cosine Down", "Half Cosine Down", "Linear Up", "Cosine Up", "Half Cosine Up", "Power Up", "Power Down", "Linear Repeating", "Cosine Repeating", "Sawtooth"]  # noqa
        for combo_item_path in combo_values_100_cfg_mode:
            comboboxtext_100_cfg_mode.append_text(combo_item_path)
        comboboxtext_100_cfg_mode.set_name("comboboxtext_100_cfg_mode")
        comboboxtext_100_cfg_mode.set_hexpand(True)
        comboboxtext_100_cfg_mode.set_active(0)

        def change_handler_100_cfg_mode(source, **args):  # noqa
            pass
        comboboxtext_100_cfg_mode.connect(SIG_CHANGED, change_handler_100_cfg_mode)

        def setter_100_cfg_mode(a_val: str):
            nonlocal combo_values_100_cfg_mode
            selected_index = combo_values_100_cfg_mode.index(a_val)
            comboboxtext_100_cfg_mode.set_active(selected_index)
        widget_getters[comboboxtext_100_cfg_mode.get_name()] = comboboxtext_100_cfg_mode.get_active_text  # noqa
        widget_setters[comboboxtext_100_cfg_mode.get_name()] = setter_100_cfg_mode  # noqa

        label_100_cfg_scale_min: Gtk.Label = Gtk.Label.new("Cfg_Scale_Min")
        label_100_cfg_scale_min.set_margin_start(8)
        label_100_cfg_scale_min.set_alignment(0.95, 0)
        adjustment_100_cfg_scale_min: Gtk.Adjustment = Gtk.Adjustment(value=0.00000,
                                                                      lower=0.00000,
                                                                      upper=1.00000,
                                                                      step_increment=0.010,
                                                                      page_increment=0.100,
                                                                      page_size=0)
        scale_100_cfg_scale_min: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_100_cfg_scale_min)  # noqa
        scale_100_cfg_scale_min.set_name("scale_100_cfg_scale_min")
        scale_100_cfg_scale_min.set_digits(3)
        scale_100_cfg_scale_min.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_100_cfg_scale_min.set_hexpand(True)

        def change_handler_100_cfg_scale_min(source, **args):  # noqa
            pass
        scale_100_cfg_scale_min.connect(SIG_VALUE_CHANGED, change_handler_100_cfg_scale_min)
        widget_getters[scale_100_cfg_scale_min.get_name()] = scale_100_cfg_scale_min.get_value
        widget_setters[scale_100_cfg_scale_min.get_name()] = scale_100_cfg_scale_min.set_value

        label_100_sched_val: Gtk.Label = Gtk.Label.new("Sched_Val")
        label_100_sched_val.set_margin_start(8)
        label_100_sched_val.set_alignment(0.95, 0)
        adjustment_100_sched_val: Gtk.Adjustment = Gtk.Adjustment(value=1.00000,
                                                                  lower=0.00000,
                                                                  upper=1.00000,
                                                                  step_increment=0.010,
                                                                  page_increment=0.100,
                                                                  page_size=0)
        scale_100_sched_val: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_100_sched_val)  # noqa
        scale_100_sched_val.set_name("scale_100_sched_val")
        scale_100_sched_val.set_digits(3)
        scale_100_sched_val.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_100_sched_val.set_hexpand(True)

        def change_handler_100_sched_val(source, **args):  # noqa
            pass
        scale_100_sched_val.connect(SIG_VALUE_CHANGED, change_handler_100_sched_val)
        widget_getters[scale_100_sched_val.get_name()] = scale_100_sched_val.get_value
        widget_setters[scale_100_sched_val.get_name()] = scale_100_sched_val.set_value

        label_100_separate_feature_channels: Gtk.Label = Gtk.Label.new("Separate_Feature_Channels")
        label_100_separate_feature_channels.set_margin_start(8)
        label_100_separate_feature_channels.set_alignment(0.95, 0)
        comboboxtext_100_separate_feature_channels: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_100_separate_feature_channels: list[str] = ["enable", "disable"]  # noqa
        for combo_item_path in combo_values_100_separate_feature_channels:
            comboboxtext_100_separate_feature_channels.append_text(combo_item_path)
        comboboxtext_100_separate_feature_channels.set_name("comboboxtext_100_separate_feature_channels")
        comboboxtext_100_separate_feature_channels.set_hexpand(True)
        comboboxtext_100_separate_feature_channels.set_active(0)

        def change_handler_100_separate_feature_channels(source, **args):  # noqa
            pass
        comboboxtext_100_separate_feature_channels.connect(SIG_CHANGED, change_handler_100_separate_feature_channels)

        def setter_100_separate_feature_channels(a_val: str):
            nonlocal combo_values_100_separate_feature_channels
            selected_index = combo_values_100_separate_feature_channels.index(a_val)
            comboboxtext_100_separate_feature_channels.set_active(selected_index)
        widget_getters[comboboxtext_100_separate_feature_channels.get_name()] = comboboxtext_100_separate_feature_channels.get_active_text  # noqa
        widget_setters[comboboxtext_100_separate_feature_channels.get_name()] = setter_100_separate_feature_channels  # noqa

        label_100_scaling_startpoint: Gtk.Label = Gtk.Label.new("Scaling_Startpoint")
        comboboxtext_100_scaling_startpoint: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_100_scaling_startpoint: list[str] = ["MEAN", "ZERO"]  # noqa
        for combo_item_path in combo_values_100_scaling_startpoint:
            comboboxtext_100_scaling_startpoint.append_text(combo_item_path)
        comboboxtext_100_scaling_startpoint.set_name("comboboxtext_100_scaling_startpoint")
        comboboxtext_100_scaling_startpoint.set_hexpand(True)
        comboboxtext_100_scaling_startpoint.set_active(1)

        def change_handler_100_scaling_startpoint(source, **args):  # noqa
            pass
        comboboxtext_100_scaling_startpoint.connect(SIG_CHANGED, change_handler_100_scaling_startpoint)

        def setter_100_scaling_startpoint(a_val: str):
            nonlocal combo_values_100_scaling_startpoint
            selected_index = combo_values_100_scaling_startpoint.index(a_val)
            comboboxtext_100_scaling_startpoint.set_active(selected_index)
        widget_getters[comboboxtext_100_scaling_startpoint.get_name()] = comboboxtext_100_scaling_startpoint.get_active_text  # noqa
        widget_setters[comboboxtext_100_scaling_startpoint.get_name()] = setter_100_scaling_startpoint  # noqa

        label_100_variability_measure: Gtk.Label = Gtk.Label.new("Variability_Measure")
        comboboxtext_100_variability_measure: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_100_variability_measure: list[str] = ["AD", "STD"]  # noqa
        for combo_item_path in combo_values_100_variability_measure:
            comboboxtext_100_variability_measure.append_text(combo_item_path)
        comboboxtext_100_variability_measure.set_name("comboboxtext_100_variability_measure")
        comboboxtext_100_variability_measure.set_hexpand(True)
        comboboxtext_100_variability_measure.set_active(1)

        def change_handler_100_variability_measure(source, **args):  # noqa
            pass
        comboboxtext_100_variability_measure.connect(SIG_CHANGED, change_handler_100_variability_measure)

        def setter_100_variability_measure(a_val: str):
            nonlocal combo_values_100_variability_measure
            selected_index = combo_values_100_variability_measure.index(a_val)
            comboboxtext_100_variability_measure.set_active(selected_index)
        widget_getters[comboboxtext_100_variability_measure.get_name()] = comboboxtext_100_variability_measure.get_active_text  # noqa
        widget_setters[comboboxtext_100_variability_measure.get_name()] = setter_100_variability_measure  # noqa

        label_100_interpolate_phi: Gtk.Label = Gtk.Label.new("Interpolate_Phi")
        label_100_interpolate_phi.set_margin_start(8)
        label_100_interpolate_phi.set_alignment(0.95, 0)
        adjustment_100_interpolate_phi: Gtk.Adjustment = Gtk.Adjustment(value=1.00000,
                                                                        lower=0.00000,
                                                                        upper=1.00000,
                                                                        step_increment=0.010,
                                                                        page_increment=0.100,
                                                                        page_size=0)
        scale_100_interpolate_phi: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_100_interpolate_phi)  # noqa
        scale_100_interpolate_phi.set_name("scale_100_interpolate_phi")
        scale_100_interpolate_phi.set_digits(3)
        scale_100_interpolate_phi.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_100_interpolate_phi.set_hexpand(True)

        def change_handler_100_interpolate_phi(source, **args):  # noqa
            pass
        scale_100_interpolate_phi.connect(SIG_VALUE_CHANGED, change_handler_100_interpolate_phi)
        widget_getters[scale_100_interpolate_phi.get_name()] = scale_100_interpolate_phi.get_value
        widget_setters[scale_100_interpolate_phi.get_name()] = scale_100_interpolate_phi.set_value

        grid_100: Gtk.Grid = Gtk.Grid.new()
        grid_100.attach(label_100_mimic_scale,                      left=0, top=0, width=1, height=1)  # noqa
        grid_100.attach(scale_100_mimic_scale,                      left=1, top=0, width=11, height=1)  # noqa
        grid_100.attach(label_100_threshold_percentile,             left=0, top=1, width=1, height=1)  # noqa
        grid_100.attach(scale_100_threshold_percentile,             left=1, top=1, width=11, height=1)  # noqa
        grid_100.attach(label_100_mimic_mode,                       left=0, top=2, width=1, height=1)  # noqa
        grid_100.attach(comboboxtext_100_mimic_mode,                left=1, top=2, width=3, height=1)  # noqa
        grid_100.attach(label_100_mimic_scale_min,                  left=4, top=2, width=1, height=1)  # noqa
        grid_100.attach(scale_100_mimic_scale_min,                  left=5, top=2, width=7, height=1)  # noqa
        grid_100.attach(label_100_cfg_mode,                         left=0, top=3, width=1, height=1)  # noqa
        grid_100.attach(comboboxtext_100_cfg_mode,                  left=1, top=3, width=3, height=1)  # noqa
        grid_100.attach(label_100_cfg_scale_min,                    left=4, top=3, width=1, height=1)  # noqa
        grid_100.attach(scale_100_cfg_scale_min,                    left=5, top=3, width=7, height=1)  # noqa
        grid_100.attach(label_100_sched_val,                        left=0, top=4, width=1, height=1)  # noqa
        grid_100.attach(scale_100_sched_val,                        left=1, top=4, width=11, height=1)  # noqa
        grid_100.attach(label_100_separate_feature_channels,        left=0, top=5, width=1, height=1)  # noqa
        grid_100.attach(comboboxtext_100_separate_feature_channels, left=1, top=5, width=3, height=1)  # noqa
        grid_100.attach(label_100_scaling_startpoint,               left=4, top=5, width=1, height=1)  # noqa
        grid_100.attach(comboboxtext_100_scaling_startpoint,        left=5, top=5, width=3, height=1)  # noqa
        grid_100.attach(label_100_variability_measure,              left=8, top=5, width=1, height=1)  # noqa
        grid_100.attach(comboboxtext_100_variability_measure,       left=9, top=5, width=3, height=1)  # noqa
        grid_100.attach(label_100_interpolate_phi,                  left=0, top=6, width=1, height=1)  # noqa
        grid_100.attach(scale_100_interpolate_phi,                  left=1, top=6, width=11, height=1)  # noqa
        grid_100.set_column_homogeneous(False)
        grid_100.set_row_homogeneous(False)
        frame_dynamicthresholdingfull_100dynamicthresholdingfull.add(widget=grid_100)  # noqa

        # New Frame
        frame_cliptextencode_101negative_prompt: Gtk.Frame = Gtk.Frame.new(label="Negative Prompt")  # noqa
        frame_cliptextencode_101negative_prompt.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_101_text: Gtk.Label = Gtk.Label.new("Text")
        textview_101_text: Gtk.TextView = Gtk.TextView.new()
        textview_101_text.get_buffer().set_text("car, cars, autos, bicycles")  # noqa
        textview_101_text.set_name("textview_101_text")
        textview_101_text.set_hexpand(True)
        textview_101_text.set_vexpand(True)
        textview_101_text.set_valign(Gtk.Align.FILL)
        # Create a ScrolledWindow to hold the TextView
        scrolled_window_101_text = Gtk.ScrolledWindow()
        scrolled_window_101_text.add(textview_101_text)  # noqa
        scrolled_window_101_text.set_size_request(288, 96)

        def preedit_handler_101_text(source, **args):  # noqa
            pass
        textview_101_text.connect(SIG_PREEDIT_CHANGED, preedit_handler_101_text)

        def getter_101_text():
            buffer: Gtk.TextBuffer = textview_101_text.get_buffer()
            start: Gtk.TextIter = buffer.get_start_iter()
            end: Gtk.TextIter = buffer.get_end_iter()
            return buffer.get_text(start, end, False)

        def setter_101_text(a_val: str):
            textview_101_text.get_buffer().set_text(str(a_val))

        widget_getters[textview_101_text.get_name()] = getter_101_text
        widget_setters[textview_101_text.get_name()] = setter_101_text

        grid_101: Gtk.Grid = Gtk.Grid.new()
        grid_101.attach(label_101_text,           left=0, top=0, width=1, height=1)  # noqa
        grid_101.attach(scrolled_window_101_text, left=1, top=0, width=3, height=1)  # noqa
        grid_101.set_column_homogeneous(False)
        grid_101.set_row_homogeneous(False)
        frame_cliptextencode_101negative_prompt.add(widget=grid_101)  # noqa

        # New Frame
        frame_editbasicpipe_103edit_basicpipe: Gtk.Frame = Gtk.Frame.new(label="Edit BasicPipe")  # noqa
        frame_editbasicpipe_103edit_basicpipe.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        grid_103: Gtk.Grid = Gtk.Grid.new()
        grid_103.set_column_homogeneous(False)
        grid_103.set_row_homogeneous(False)
        frame_editbasicpipe_103edit_basicpipe.add(widget=grid_103)  # noqa

        # New Frame
        frame_frombasicpipe_v2_104frombasicpipe_v2: Gtk.Frame = Gtk.Frame.new(label="FromBasicPipe_v2")  # noqa
        frame_frombasicpipe_v2_104frombasicpipe_v2.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        grid_104: Gtk.Grid = Gtk.Grid.new()
        grid_104.set_column_homogeneous(False)
        grid_104.set_row_homogeneous(False)
        frame_frombasicpipe_v2_104frombasicpipe_v2.add(widget=grid_104)  # noqa

        # New Frame
        frame_vaedecode_111vae_decode: Gtk.Frame = Gtk.Frame.new(label="VAE Decode")  # noqa
        frame_vaedecode_111vae_decode.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        grid_111: Gtk.Grid = Gtk.Grid.new()
        grid_111.set_column_homogeneous(False)
        grid_111.set_row_homogeneous(False)
        frame_vaedecode_111vae_decode.add(widget=grid_111)  # noqa

        # New Frame
        frame_sd_4xupscale_conditioning_121sd_4xupscale_conditioning: Gtk.Frame = Gtk.Frame.new(label="SD_4XUpscale_Conditioning")  # noqa
        frame_sd_4xupscale_conditioning_121sd_4xupscale_conditioning.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_121_scale_ratio: Gtk.Label = Gtk.Label.new("Scale_Ratio")
        label_121_scale_ratio.set_margin_start(8)
        adjustment_121_scale_ratio: Gtk.Adjustment = Gtk.Adjustment(value=1.50000,
                                                                    lower=0.00001,
                                                                    upper=10.00000,
                                                                    step_increment=0.100,
                                                                    page_increment=1.000,
                                                                    page_size=0)
        scale_121_scale_ratio: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_121_scale_ratio)  # noqa
        scale_121_scale_ratio.set_name("scale_121_scale_ratio")
        scale_121_scale_ratio.set_digits(3)
        scale_121_scale_ratio.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_121_scale_ratio.set_hexpand(True)

        def change_handler_121_scale_ratio(source, **args):  # noqa
            pass
        scale_121_scale_ratio.connect(SIG_VALUE_CHANGED, change_handler_121_scale_ratio)
        widget_getters[scale_121_scale_ratio.get_name()] = scale_121_scale_ratio.get_value
        widget_setters[scale_121_scale_ratio.get_name()] = scale_121_scale_ratio.set_value

        label_121_noise_augmentation: Gtk.Label = Gtk.Label.new("Noise_Augmentation")
        label_121_noise_augmentation.set_margin_start(8)
        adjustment_121_noise_augmentation: Gtk.Adjustment = Gtk.Adjustment(value=0.35000,
                                                                           lower=0.00001,
                                                                           upper=1.00000,
                                                                           step_increment=0.001,
                                                                           page_increment=0.010,
                                                                           page_size=0)
        scale_121_noise_augmentation: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_121_noise_augmentation)  # noqa
        scale_121_noise_augmentation.set_name("scale_121_noise_augmentation")
        scale_121_noise_augmentation.set_digits(3)
        scale_121_noise_augmentation.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_121_noise_augmentation.set_hexpand(True)

        def change_handler_121_noise_augmentation(source, **args):  # noqa
            pass
        scale_121_noise_augmentation.connect(SIG_VALUE_CHANGED, change_handler_121_noise_augmentation)
        widget_getters[scale_121_noise_augmentation.get_name()] = scale_121_noise_augmentation.get_value
        widget_setters[scale_121_noise_augmentation.get_name()] = scale_121_noise_augmentation.set_value

        grid_121: Gtk.Grid = Gtk.Grid.new()
        grid_121.attach(label_121_scale_ratio,        left=0, top=0, width=1, height=1)  # noqa
        grid_121.attach(scale_121_scale_ratio,        left=1, top=0, width=3, height=1)  # noqa
        grid_121.attach(label_121_noise_augmentation, left=0, top=1, width=1, height=1)  # noqa
        grid_121.attach(scale_121_noise_augmentation, left=1, top=1, width=3, height=1)  # noqa
        grid_121.set_column_homogeneous(False)
        grid_121.set_row_homogeneous(False)
        frame_sd_4xupscale_conditioning_121sd_4xupscale_conditioning.add(widget=grid_121)  # noqa

        # New Frame
        frame_efficient_loader_122efficient_loader: Gtk.Frame = Gtk.Frame.new(label="Efficient Loader")  # noqa
        frame_efficient_loader_122efficient_loader.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_122_ckpt_name: Gtk.Label = Gtk.Label.new("Ckpt_Name")
        comboboxtext_122_ckpt_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_122_ckpt_name: list[str] = get_models_filenames(
            model_type=ModelType.CHECKPOINTS,
            cu_origin=self.comfy_svr_origin)
        if combo_values_122_ckpt_name is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_122_ckpt_name:
            raise ValueError(fr"No models retrieved from ComfyUI")  # noqa
        for combo_item_path in combo_values_122_ckpt_name:
            comboboxtext_122_ckpt_name.append_text(combo_item_path)
        comboboxtext_122_ckpt_name.set_name("comboboxtext_122_ckpt_name")
        comboboxtext_122_ckpt_name.set_hexpand(True)
        comboboxtext_122_ckpt_name.set_active(8)

        def change_handler_122_ckpt_name(source, **args):  # noqa
            pass
        comboboxtext_122_ckpt_name.connect(SIG_CHANGED, change_handler_122_ckpt_name)

        def setter_122_ckpt_name(a_val: str):
            nonlocal combo_values_122_ckpt_name
            selected_index = combo_values_122_ckpt_name.index(a_val)
            comboboxtext_122_ckpt_name.set_active(selected_index)
        widget_getters[comboboxtext_122_ckpt_name.get_name()] = comboboxtext_122_ckpt_name.get_active_text  # noqa
        widget_setters[comboboxtext_122_ckpt_name.get_name()] = setter_122_ckpt_name  # noqa

        label_122_vae_name: Gtk.Label = Gtk.Label.new("Vae_Name")
        comboboxtext_122_vae_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_122_vae_name: list[str] = get_models_filenames(
            model_type=ModelType.VAE,
            cu_origin=self.comfy_svr_origin)
        if combo_values_122_vae_name is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_122_vae_name:
            raise ValueError(fr"No models retrieved from ComfyUI")  # noqa
        for combo_item_path in combo_values_122_vae_name:
            comboboxtext_122_vae_name.append_text(combo_item_path)
        comboboxtext_122_vae_name.set_name("comboboxtext_122_vae_name")
        comboboxtext_122_vae_name.set_hexpand(True)
        comboboxtext_122_vae_name.set_active(2)

        def change_handler_122_vae_name(source, **args):  # noqa
            pass
        comboboxtext_122_vae_name.connect(SIG_CHANGED, change_handler_122_vae_name)

        def setter_122_vae_name(a_val: str):
            nonlocal combo_values_122_vae_name
            selected_index = combo_values_122_vae_name.index(a_val)
            comboboxtext_122_vae_name.set_active(selected_index)
        widget_getters[comboboxtext_122_vae_name.get_name()] = comboboxtext_122_vae_name.get_active_text  # noqa
        widget_setters[comboboxtext_122_vae_name.get_name()] = setter_122_vae_name  # noqa

        label_122_clip_skip: Gtk.Label = Gtk.Label.new("Clip_Skip")
        label_122_clip_skip.set_margin_start(8)
        label_122_clip_skip.set_alignment(0.95, 0)
        entry_122_clip_skip: Gtk.Entry = Gtk.Entry.new()
        entry_122_clip_skip.set_text(str(-1))
        entry_122_clip_skip.set_name("entry_122_clip_skip")
        entry_122_clip_skip.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_122_clip_skip,
                           minimum=-1, maximum=18446744073709519872,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_122_clip_skip(source, **args):  # noqa
            pass
        entry_122_clip_skip.connect(SIG_CHANGED, change_handler_122_clip_skip)

        def getter_122_clip_skip() -> int:
            return int(entry_122_clip_skip.get_text())

        def setter_122_clip_skip(a_val: int):
            entry_122_clip_skip.set_text(str(a_val))
        widget_getters[entry_122_clip_skip.get_name()] = getter_122_clip_skip  # noqa
        widget_setters[entry_122_clip_skip.get_name()] = setter_122_clip_skip  # noqa

        label_122_lora_name: Gtk.Label = Gtk.Label.new("Lora_Name")
        comboboxtext_122_lora_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_122_lora_name: list[str] = get_models_filenames(
            model_type=ModelType.LORAS,
            cu_origin=self.comfy_svr_origin)
        if combo_values_122_lora_name is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_122_lora_name:
            raise ValueError(fr"No models retrieved from ComfyUI")  # noqa
        for combo_item_path in combo_values_122_lora_name:
            comboboxtext_122_lora_name.append_text(combo_item_path)
        comboboxtext_122_lora_name.set_name("comboboxtext_122_lora_name")
        comboboxtext_122_lora_name.set_hexpand(True)
        comboboxtext_122_lora_name.set_active(18)

        def change_handler_122_lora_name(source, **args):  # noqa
            pass
        comboboxtext_122_lora_name.connect(SIG_CHANGED, change_handler_122_lora_name)

        def setter_122_lora_name(a_val: str):
            nonlocal combo_values_122_lora_name
            selected_index = combo_values_122_lora_name.index(a_val)
            comboboxtext_122_lora_name.set_active(selected_index)
        widget_getters[comboboxtext_122_lora_name.get_name()] = comboboxtext_122_lora_name.get_active_text  # noqa
        widget_setters[comboboxtext_122_lora_name.get_name()] = setter_122_lora_name  # noqa

        label_122_lora_model_strength: Gtk.Label = Gtk.Label.new("Lora_Model_Strength")
        label_122_lora_model_strength.set_margin_start(8)
        label_122_lora_model_strength.set_alignment(0.95, 0)
        adjustment_122_lora_model_strength: Gtk.Adjustment = Gtk.Adjustment(value=1.00000,
                                                                            lower=0.00000,
                                                                            upper=20.00000,
                                                                            step_increment=1.000,
                                                                            page_increment=5.000,
                                                                            page_size=0)
        scale_122_lora_model_strength: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_122_lora_model_strength)  # noqa
        scale_122_lora_model_strength.set_name("scale_122_lora_model_strength")
        scale_122_lora_model_strength.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_122_lora_model_strength.set_hexpand(True)

        def change_handler_122_lora_model_strength(source, **args):  # noqa
            pass
        scale_122_lora_model_strength.connect(SIG_VALUE_CHANGED, change_handler_122_lora_model_strength)
        widget_getters[scale_122_lora_model_strength.get_name()] = scale_122_lora_model_strength.get_value
        widget_setters[scale_122_lora_model_strength.get_name()] = scale_122_lora_model_strength.set_value

        label_122_lora_clip_strength: Gtk.Label = Gtk.Label.new("Lora_Clip_Strength")
        label_122_lora_clip_strength.set_margin_start(8)
        label_122_lora_clip_strength.set_alignment(0.95, 0)
        adjustment_122_lora_clip_strength: Gtk.Adjustment = Gtk.Adjustment(value=1.00000,
                                                                           lower=0.00000,
                                                                           upper=20.00000,
                                                                           step_increment=1.000,
                                                                           page_increment=5.000,
                                                                           page_size=0)
        scale_122_lora_clip_strength: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_122_lora_clip_strength)  # noqa
        scale_122_lora_clip_strength.set_name("scale_122_lora_clip_strength")
        scale_122_lora_clip_strength.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_122_lora_clip_strength.set_hexpand(True)

        def change_handler_122_lora_clip_strength(source, **args):  # noqa
            pass
        scale_122_lora_clip_strength.connect(SIG_VALUE_CHANGED, change_handler_122_lora_clip_strength)
        widget_getters[scale_122_lora_clip_strength.get_name()] = scale_122_lora_clip_strength.get_value
        widget_setters[scale_122_lora_clip_strength.get_name()] = scale_122_lora_clip_strength.set_value

        label_122_positive: Gtk.Label = Gtk.Label.new("Positive")
        textview_122_positive: Gtk.TextView = Gtk.TextView.new()
        textview_122_positive.get_buffer().set_text("high quality photography")  # noqa
        textview_122_positive.set_name("textview_122_positive")
        textview_122_positive.set_hexpand(True)
        textview_122_positive.set_vexpand(True)
        textview_122_positive.set_valign(Gtk.Align.FILL)
        # Create a ScrolledWindow to hold the TextView
        scrolled_window_122_positive = Gtk.ScrolledWindow()
        scrolled_window_122_positive.add(textview_122_positive)  # noqa
        scrolled_window_122_positive.set_size_request(864, 288)

        def preedit_handler_122_positive(source, **args):  # noqa
            pass
        textview_122_positive.connect(SIG_PREEDIT_CHANGED, preedit_handler_122_positive)

        def getter_122_positive():
            buffer: Gtk.TextBuffer = textview_122_positive.get_buffer()
            start: Gtk.TextIter = buffer.get_start_iter()
            end: Gtk.TextIter = buffer.get_end_iter()
            return buffer.get_text(start, end, False)

        def setter_122_positive(a_val: str):
            textview_122_positive.get_buffer().set_text(str(a_val))

        widget_getters[textview_122_positive.get_name()] = getter_122_positive
        widget_setters[textview_122_positive.get_name()] = setter_122_positive

        label_122_negative: Gtk.Label = Gtk.Label.new("Negative")
        textview_122_negative: Gtk.TextView = Gtk.TextView.new()
        textview_122_negative.get_buffer().set_text("(octane render, render, drawing, anime, bad photo, bad photography:1.3), (worst quality, low quality, blurry:1.2), (bad teeth, deformed teeth, deformed lips), (bad anatomy, bad proportions:1.1), (deformed iris, deformed pupils), (deformed eyes, bad eyes), (deformed face, ugly face, bad face), (deformed hands, bad hands, fused fingers), morbid, mutilated, mutation, disfigured")  # noqa
        textview_122_negative.set_name("textview_122_negative")
        textview_122_negative.set_hexpand(True)
        textview_122_negative.set_vexpand(True)
        textview_122_negative.set_valign(Gtk.Align.FILL)
        # Create a ScrolledWindow to hold the TextView
        scrolled_window_122_negative = Gtk.ScrolledWindow()
        scrolled_window_122_negative.add(textview_122_negative)  # noqa
        scrolled_window_122_negative.set_size_request(288, 96)

        def preedit_handler_122_negative(source, **args):  # noqa
            pass
        textview_122_negative.connect(SIG_PREEDIT_CHANGED, preedit_handler_122_negative)

        def getter_122_negative():
            buffer: Gtk.TextBuffer = textview_122_negative.get_buffer()
            start: Gtk.TextIter = buffer.get_start_iter()
            end: Gtk.TextIter = buffer.get_end_iter()
            return buffer.get_text(start, end, False)

        def setter_122_negative(a_val: str):
            textview_122_negative.get_buffer().set_text(str(a_val))

        widget_getters[textview_122_negative.get_name()] = getter_122_negative
        widget_setters[textview_122_negative.get_name()] = setter_122_negative

        label_122_token_normalization: Gtk.Label = Gtk.Label.new("Token_Normalization")
        comboboxtext_122_token_normalization: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_122_token_normalization: list[str] = ["none", "mean", "length", "length+mean"]  # noqa
        for combo_item_path in combo_values_122_token_normalization:
            comboboxtext_122_token_normalization.append_text(combo_item_path)
        comboboxtext_122_token_normalization.set_name("comboboxtext_122_token_normalization")
        comboboxtext_122_token_normalization.set_hexpand(True)
        comboboxtext_122_token_normalization.set_active(0)

        def change_handler_122_token_normalization(source, **args):  # noqa
            pass
        comboboxtext_122_token_normalization.connect(SIG_CHANGED, change_handler_122_token_normalization)

        def setter_122_token_normalization(a_val: str):
            nonlocal combo_values_122_token_normalization
            selected_index = combo_values_122_token_normalization.index(a_val)
            comboboxtext_122_token_normalization.set_active(selected_index)
        widget_getters[comboboxtext_122_token_normalization.get_name()] = comboboxtext_122_token_normalization.get_active_text  # noqa
        widget_setters[comboboxtext_122_token_normalization.get_name()] = setter_122_token_normalization  # noqa

        label_122_weight_interpretation: Gtk.Label = Gtk.Label.new("Weight_Interpretation")
        comboboxtext_122_weight_interpretation: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_122_weight_interpretation: list[str] = ["comfy", "A1111", "compel", "comfy++", "down_weight"]  # noqa
        for combo_item_path in combo_values_122_weight_interpretation:
            comboboxtext_122_weight_interpretation.append_text(combo_item_path)
        comboboxtext_122_weight_interpretation.set_name("comboboxtext_122_weight_interpretation")
        comboboxtext_122_weight_interpretation.set_hexpand(True)
        comboboxtext_122_weight_interpretation.set_active(0)

        def change_handler_122_weight_interpretation(source, **args):  # noqa
            pass
        comboboxtext_122_weight_interpretation.connect(SIG_CHANGED, change_handler_122_weight_interpretation)

        def setter_122_weight_interpretation(a_val: str):
            nonlocal combo_values_122_weight_interpretation
            selected_index = combo_values_122_weight_interpretation.index(a_val)
            comboboxtext_122_weight_interpretation.set_active(selected_index)
        widget_getters[comboboxtext_122_weight_interpretation.get_name()] = comboboxtext_122_weight_interpretation.get_active_text  # noqa
        widget_setters[comboboxtext_122_weight_interpretation.get_name()] = setter_122_weight_interpretation  # noqa

        label_122_empty_latent_width: Gtk.Label = Gtk.Label.new("Empty_Latent_Width")
        label_122_empty_latent_width.set_margin_start(8)
        label_122_empty_latent_width.set_alignment(0.95, 0)
        entry_122_empty_latent_width: Gtk.Entry = Gtk.Entry.new()
        entry_122_empty_latent_width.set_text(str(512))
        entry_122_empty_latent_width.set_name("entry_122_empty_latent_width")
        entry_122_empty_latent_width.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_122_empty_latent_width,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_122_empty_latent_width(source, **args):  # noqa
            pass
        entry_122_empty_latent_width.connect(SIG_CHANGED, change_handler_122_empty_latent_width)

        def getter_122_empty_latent_width() -> int:
            return int(entry_122_empty_latent_width.get_text())

        def setter_122_empty_latent_width(a_val: int):
            entry_122_empty_latent_width.set_text(str(a_val))
        widget_getters[entry_122_empty_latent_width.get_name()] = getter_122_empty_latent_width  # noqa
        widget_setters[entry_122_empty_latent_width.get_name()] = setter_122_empty_latent_width  # noqa

        label_122_empty_latent_height: Gtk.Label = Gtk.Label.new("Empty_Latent_Height")
        label_122_empty_latent_height.set_margin_start(8)
        label_122_empty_latent_height.set_alignment(0.95, 0)
        entry_122_empty_latent_height: Gtk.Entry = Gtk.Entry.new()
        entry_122_empty_latent_height.set_text(str(512))
        entry_122_empty_latent_height.set_name("entry_122_empty_latent_height")
        entry_122_empty_latent_height.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_122_empty_latent_height,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_122_empty_latent_height(source, **args):  # noqa
            pass
        entry_122_empty_latent_height.connect(SIG_CHANGED, change_handler_122_empty_latent_height)

        def getter_122_empty_latent_height() -> int:
            return int(entry_122_empty_latent_height.get_text())

        def setter_122_empty_latent_height(a_val: int):
            entry_122_empty_latent_height.set_text(str(a_val))
        widget_getters[entry_122_empty_latent_height.get_name()] = getter_122_empty_latent_height  # noqa
        widget_setters[entry_122_empty_latent_height.get_name()] = setter_122_empty_latent_height  # noqa

        label_122_batch_size: Gtk.Label = Gtk.Label.new("Batch_Size")
        label_122_batch_size.set_margin_start(8)
        label_122_batch_size.set_alignment(0.95, 0)
        entry_122_batch_size: Gtk.Entry = Gtk.Entry.new()
        entry_122_batch_size.set_text(str(1))
        entry_122_batch_size.set_name("entry_122_batch_size")
        entry_122_batch_size.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_122_batch_size,
                           minimum=1, maximum=256,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_122_batch_size(source, **args):  # noqa
            pass
        entry_122_batch_size.connect(SIG_CHANGED, change_handler_122_batch_size)

        def getter_122_batch_size() -> int:
            return int(entry_122_batch_size.get_text())

        def setter_122_batch_size(a_val: int):
            entry_122_batch_size.set_text(str(a_val))
        widget_getters[entry_122_batch_size.get_name()] = getter_122_batch_size  # noqa
        widget_setters[entry_122_batch_size.get_name()] = setter_122_batch_size  # noqa

        grid_122: Gtk.Grid = Gtk.Grid.new()
        grid_122.attach(label_122_ckpt_name,                    left=0, top=0, width=1, height=1)  # noqa
        grid_122.attach(comboboxtext_122_ckpt_name,             left=1, top=0, width=3, height=1)  # noqa
        grid_122.attach(label_122_vae_name,                     left=0, top=1, width=1, height=1)  # noqa
        grid_122.attach(comboboxtext_122_vae_name,              left=1, top=1, width=3, height=1)  # noqa
        grid_122.attach(label_122_clip_skip,                    left=0, top=2, width=1, height=1)  # noqa
        grid_122.attach(entry_122_clip_skip,                    left=1, top=2, width=3, height=1)  # noqa
        grid_122.attach(label_122_lora_name,                    left=0, top=3, width=1, height=1)  # noqa
        grid_122.attach(comboboxtext_122_lora_name,             left=1, top=3, width=3, height=1)  # noqa
        grid_122.attach(label_122_lora_model_strength,          left=0, top=4, width=1, height=1)  # noqa
        grid_122.attach(scale_122_lora_model_strength,          left=1, top=4, width=3, height=1)  # noqa
        grid_122.attach(label_122_lora_clip_strength,           left=0, top=5, width=1, height=1)  # noqa
        grid_122.attach(scale_122_lora_clip_strength,           left=1, top=5, width=3, height=1)  # noqa
        grid_122.attach(label_122_positive,                     left=0, top=6, width=1, height=1)  # noqa
        grid_122.attach(scrolled_window_122_positive,           left=1, top=6, width=3, height=1)  # noqa
        grid_122.attach(label_122_negative,                     left=0, top=7, width=1, height=1)  # noqa
        grid_122.attach(scrolled_window_122_negative,           left=1, top=7, width=3, height=1)  # noqa
        grid_122.attach(label_122_token_normalization,          left=0, top=8, width=1, height=1)  # noqa
        grid_122.attach(comboboxtext_122_token_normalization,   left=1, top=8, width=3, height=1)  # noqa
        grid_122.attach(label_122_weight_interpretation,        left=0, top=9, width=1, height=1)  # noqa
        grid_122.attach(comboboxtext_122_weight_interpretation, left=1, top=9, width=3, height=1)  # noqa
        grid_122.attach(label_122_empty_latent_width,           left=0, top=10, width=1, height=1)  # noqa
        grid_122.attach(entry_122_empty_latent_width,           left=1, top=10, width=3, height=1)  # noqa
        grid_122.attach(label_122_empty_latent_height,          left=0, top=11, width=1, height=1)  # noqa
        grid_122.attach(entry_122_empty_latent_height,          left=1, top=11, width=3, height=1)  # noqa
        grid_122.attach(label_122_batch_size,                   left=0, top=12, width=1, height=1)  # noqa
        grid_122.attach(entry_122_batch_size,                   left=1, top=12, width=3, height=1)  # noqa
        grid_122.set_column_homogeneous(False)
        grid_122.set_row_homogeneous(False)
        frame_efficient_loader_122efficient_loader.add(widget=grid_122)  # noqa

        # New Frame
        frame_ultimatesdupscale_123ultimate_sd_upscale: Gtk.Frame = Gtk.Frame.new(label="Ultimate SD Upscale")  # noqa
        frame_ultimatesdupscale_123ultimate_sd_upscale.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_123_upscale_by: Gtk.Label = Gtk.Label.new("Upscale_By")
        label_123_upscale_by.set_margin_start(8)
        label_123_upscale_by.set_alignment(0.95, 0)
        adjustment_123_upscale_by: Gtk.Adjustment = Gtk.Adjustment(value=2.00000,
                                                                   lower=0.00001,
                                                                   upper=10.00000,
                                                                   step_increment=0.100,
                                                                   page_increment=1.000,
                                                                   page_size=0)
        scale_123_upscale_by: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_123_upscale_by)  # noqa
        scale_123_upscale_by.set_name("scale_123_upscale_by")
        scale_123_upscale_by.set_digits(3)
        scale_123_upscale_by.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_123_upscale_by.set_hexpand(True)

        def change_handler_123_upscale_by(source, **args):  # noqa
            pass
        scale_123_upscale_by.connect(SIG_VALUE_CHANGED, change_handler_123_upscale_by)
        widget_getters[scale_123_upscale_by.get_name()] = scale_123_upscale_by.get_value
        widget_setters[scale_123_upscale_by.get_name()] = scale_123_upscale_by.set_value

        label_123_seed: Gtk.Label = Gtk.Label.new("Seed")
        label_123_seed.set_margin_start(8)
        label_123_seed.set_alignment(0.95, 0)
        entry_123_seed: Gtk.Entry = Gtk.Entry.new()
        entry_123_seed.set_text(str(587444286529169))
        entry_123_seed.set_name("entry_123_seed")
        entry_123_seed.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_123_seed,
                           minimum=0, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_123_seed(source, **args):  # noqa
            pass
        entry_123_seed.connect(SIG_CHANGED, change_handler_123_seed)

        def getter_123_seed() -> int:
            return int(entry_123_seed.get_text())

        def setter_123_seed(a_val: int):
            entry_123_seed.set_text(str(a_val))
        widget_getters[entry_123_seed.get_name()] = getter_123_seed  # noqa
        widget_setters[entry_123_seed.get_name()] = setter_123_seed  # noqa

        label_123_steps: Gtk.Label = Gtk.Label.new("Steps")
        label_123_steps.set_margin_start(8)
        label_123_steps.set_alignment(0.95, 0)
        entry_123_steps: Gtk.Entry = Gtk.Entry.new()
        entry_123_steps.set_text(str(10))
        entry_123_steps.set_name("entry_123_steps")
        entry_123_steps.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_123_steps,
                           minimum=1, maximum=128,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_123_steps(source, **args):  # noqa
            pass
        entry_123_steps.connect(SIG_CHANGED, change_handler_123_steps)

        def getter_123_steps() -> int:
            return int(entry_123_steps.get_text())

        def setter_123_steps(a_val: int):
            entry_123_steps.set_text(str(a_val))
        widget_getters[entry_123_steps.get_name()] = getter_123_steps  # noqa
        widget_setters[entry_123_steps.get_name()] = setter_123_steps  # noqa

        label_123_cfg: Gtk.Label = Gtk.Label.new("Cfg")
        label_123_cfg.set_margin_start(8)
        label_123_cfg.set_alignment(0.95, 0)
        adjustment_123_cfg: Gtk.Adjustment = Gtk.Adjustment(value=2.00000,
                                                            lower=1.00000,
                                                            upper=25.00000,
                                                            step_increment=0.100,
                                                            page_increment=2.000,
                                                            page_size=0)
        scale_123_cfg: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_123_cfg)  # noqa
        scale_123_cfg.set_name("scale_123_cfg")
        scale_123_cfg.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_123_cfg.set_hexpand(True)

        def change_handler_123_cfg(source, **args):  # noqa
            pass
        scale_123_cfg.connect(SIG_VALUE_CHANGED, change_handler_123_cfg)
        widget_getters[scale_123_cfg.get_name()] = scale_123_cfg.get_value
        widget_setters[scale_123_cfg.get_name()] = scale_123_cfg.set_value

        label_123_sampler_name: Gtk.Label = Gtk.Label.new("Sampler_Name")
        comboboxtext_123_sampler_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_123_sampler_name: list[str] = ["euler", "euler_ancestral", "heun", "heunpp2", "dpm_2", "dpm_2_ancestral", "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_sde", "dpmpp_sde_gpu", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu", "ddpm", "lcm", "ddim", "uni_pc", "uni_pc_bh2"]  # noqa
        for combo_item_path in combo_values_123_sampler_name:
            comboboxtext_123_sampler_name.append_text(combo_item_path)
        comboboxtext_123_sampler_name.set_name("comboboxtext_123_sampler_name")
        comboboxtext_123_sampler_name.set_hexpand(True)
        comboboxtext_123_sampler_name.set_active(14)

        def change_handler_123_sampler_name(source, **args):  # noqa
            pass
        comboboxtext_123_sampler_name.connect(SIG_CHANGED, change_handler_123_sampler_name)

        def setter_123_sampler_name(a_val: str):
            nonlocal combo_values_123_sampler_name
            selected_index = combo_values_123_sampler_name.index(a_val)
            comboboxtext_123_sampler_name.set_active(selected_index)
        widget_getters[comboboxtext_123_sampler_name.get_name()] = comboboxtext_123_sampler_name.get_active_text  # noqa
        widget_setters[comboboxtext_123_sampler_name.get_name()] = setter_123_sampler_name  # noqa

        label_123_scheduler: Gtk.Label = Gtk.Label.new("Scheduler")
        comboboxtext_123_scheduler: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_123_scheduler: list[str] = ["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"]  # noqa
        for combo_item_path in combo_values_123_scheduler:
            comboboxtext_123_scheduler.append_text(combo_item_path)
        comboboxtext_123_scheduler.set_name("comboboxtext_123_scheduler")
        comboboxtext_123_scheduler.set_hexpand(True)
        comboboxtext_123_scheduler.set_active(3)

        def change_handler_123_scheduler(source, **args):  # noqa
            pass
        comboboxtext_123_scheduler.connect(SIG_CHANGED, change_handler_123_scheduler)

        def setter_123_scheduler(a_val: str):
            nonlocal combo_values_123_scheduler
            selected_index = combo_values_123_scheduler.index(a_val)
            comboboxtext_123_scheduler.set_active(selected_index)
        widget_getters[comboboxtext_123_scheduler.get_name()] = comboboxtext_123_scheduler.get_active_text  # noqa
        widget_setters[comboboxtext_123_scheduler.get_name()] = setter_123_scheduler  # noqa

        label_123_denoise: Gtk.Label = Gtk.Label.new("Denoise")
        label_123_denoise.set_margin_start(8)
        adjustment_123_denoise: Gtk.Adjustment = Gtk.Adjustment(value=0.20000,
                                                                lower=0.00001,
                                                                upper=1.00000,
                                                                step_increment=0.001,
                                                                page_increment=0.010,
                                                                page_size=0)
        scale_123_denoise: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_123_denoise)  # noqa
        scale_123_denoise.set_name("scale_123_denoise")
        scale_123_denoise.set_digits(3)
        scale_123_denoise.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_123_denoise.set_hexpand(True)

        def change_handler_123_denoise(source, **args):  # noqa
            pass
        scale_123_denoise.connect(SIG_VALUE_CHANGED, change_handler_123_denoise)
        widget_getters[scale_123_denoise.get_name()] = scale_123_denoise.get_value
        widget_setters[scale_123_denoise.get_name()] = scale_123_denoise.set_value

        label_123_mode_type: Gtk.Label = Gtk.Label.new("Mode_Type")
        comboboxtext_123_mode_type: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_123_mode_type: list[str] = ["Linear", "Chess", "None"]  # noqa
        for combo_item_path in combo_values_123_mode_type:
            comboboxtext_123_mode_type.append_text(combo_item_path)
        comboboxtext_123_mode_type.set_name("comboboxtext_123_mode_type")
        comboboxtext_123_mode_type.set_hexpand(True)
        comboboxtext_123_mode_type.set_active(1)

        def change_handler_123_mode_type(source, **args):  # noqa
            pass
        comboboxtext_123_mode_type.connect(SIG_CHANGED, change_handler_123_mode_type)

        def setter_123_mode_type(a_val: str):
            nonlocal combo_values_123_mode_type
            selected_index = combo_values_123_mode_type.index(a_val)
            comboboxtext_123_mode_type.set_active(selected_index)
        widget_getters[comboboxtext_123_mode_type.get_name()] = comboboxtext_123_mode_type.get_active_text  # noqa
        widget_setters[comboboxtext_123_mode_type.get_name()] = setter_123_mode_type  # noqa

        label_123_mask_blur: Gtk.Label = Gtk.Label.new("Mask_Blur")
        label_123_mask_blur.set_margin_start(8)
        label_123_mask_blur.set_alignment(0.95, 0)
        entry_123_mask_blur: Gtk.Entry = Gtk.Entry.new()
        entry_123_mask_blur.set_text(str(8))
        entry_123_mask_blur.set_name("entry_123_mask_blur")
        entry_123_mask_blur.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_123_mask_blur,
                           minimum=0, maximum=128,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_123_mask_blur(source, **args):  # noqa
            pass
        entry_123_mask_blur.connect(SIG_CHANGED, change_handler_123_mask_blur)

        def getter_123_mask_blur() -> int:
            return int(entry_123_mask_blur.get_text())

        def setter_123_mask_blur(a_val: int):
            entry_123_mask_blur.set_text(str(a_val))
        widget_getters[entry_123_mask_blur.get_name()] = getter_123_mask_blur  # noqa
        widget_setters[entry_123_mask_blur.get_name()] = setter_123_mask_blur  # noqa

        label_123_tile_padding: Gtk.Label = Gtk.Label.new("Tile_Padding")
        label_123_tile_padding.set_margin_start(8)
        label_123_tile_padding.set_alignment(0.95, 0)
        entry_123_tile_padding: Gtk.Entry = Gtk.Entry.new()
        entry_123_tile_padding.set_text(str(32))
        entry_123_tile_padding.set_name("entry_123_tile_padding")
        entry_123_tile_padding.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_123_tile_padding,
                           minimum=0, maximum=128,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_123_tile_padding(source, **args):  # noqa
            pass
        entry_123_tile_padding.connect(SIG_CHANGED, change_handler_123_tile_padding)

        def getter_123_tile_padding() -> int:
            return int(entry_123_tile_padding.get_text())

        def setter_123_tile_padding(a_val: int):
            entry_123_tile_padding.set_text(str(a_val))
        widget_getters[entry_123_tile_padding.get_name()] = getter_123_tile_padding  # noqa
        widget_setters[entry_123_tile_padding.get_name()] = setter_123_tile_padding  # noqa

        label_123_seam_fix_mode: Gtk.Label = Gtk.Label.new("Seam_Fix_Mode")
        comboboxtext_123_seam_fix_mode: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_123_seam_fix_mode: list[str] = ["None", "Band Pass", "Half Tile", "Half Tile + Intersections"]  # noqa
        for combo_item_path in combo_values_123_seam_fix_mode:
            comboboxtext_123_seam_fix_mode.append_text(combo_item_path)
        comboboxtext_123_seam_fix_mode.set_name("comboboxtext_123_seam_fix_mode")
        comboboxtext_123_seam_fix_mode.set_hexpand(True)
        comboboxtext_123_seam_fix_mode.set_active(0)

        def change_handler_123_seam_fix_mode(source, **args):  # noqa
            pass
        comboboxtext_123_seam_fix_mode.connect(SIG_CHANGED, change_handler_123_seam_fix_mode)

        def setter_123_seam_fix_mode(a_val: str):
            nonlocal combo_values_123_seam_fix_mode
            selected_index = combo_values_123_seam_fix_mode.index(a_val)
            comboboxtext_123_seam_fix_mode.set_active(selected_index)
        widget_getters[comboboxtext_123_seam_fix_mode.get_name()] = comboboxtext_123_seam_fix_mode.get_active_text  # noqa
        widget_setters[comboboxtext_123_seam_fix_mode.get_name()] = setter_123_seam_fix_mode  # noqa

        label_123_seam_fix_denoise: Gtk.Label = Gtk.Label.new("Seam_Fix_Denoise")
        label_123_seam_fix_denoise.set_margin_start(8)
        label_123_seam_fix_denoise.set_alignment(0.95, 0)
        adjustment_123_seam_fix_denoise: Gtk.Adjustment = Gtk.Adjustment(value=1.00000,
                                                                         lower=0.00001,
                                                                         upper=1.00000,
                                                                         step_increment=0.001,
                                                                         page_increment=0.010,
                                                                         page_size=0)
        scale_123_seam_fix_denoise: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_123_seam_fix_denoise)  # noqa
        scale_123_seam_fix_denoise.set_name("scale_123_seam_fix_denoise")
        scale_123_seam_fix_denoise.set_digits(3)
        scale_123_seam_fix_denoise.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_123_seam_fix_denoise.set_hexpand(True)

        def change_handler_123_seam_fix_denoise(source, **args):  # noqa
            pass
        scale_123_seam_fix_denoise.connect(SIG_VALUE_CHANGED, change_handler_123_seam_fix_denoise)
        widget_getters[scale_123_seam_fix_denoise.get_name()] = scale_123_seam_fix_denoise.get_value
        widget_setters[scale_123_seam_fix_denoise.get_name()] = scale_123_seam_fix_denoise.set_value

        label_123_seam_fix_width: Gtk.Label = Gtk.Label.new("Seam_Fix_Width")
        label_123_seam_fix_width.set_margin_start(8)
        label_123_seam_fix_width.set_alignment(0.95, 0)
        entry_123_seam_fix_width: Gtk.Entry = Gtk.Entry.new()
        entry_123_seam_fix_width.set_text(str(64))
        entry_123_seam_fix_width.set_name("entry_123_seam_fix_width")
        entry_123_seam_fix_width.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_123_seam_fix_width,
                           minimum=0, maximum=128,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_123_seam_fix_width(source, **args):  # noqa
            pass
        entry_123_seam_fix_width.connect(SIG_CHANGED, change_handler_123_seam_fix_width)

        def getter_123_seam_fix_width() -> int:
            return int(entry_123_seam_fix_width.get_text())

        def setter_123_seam_fix_width(a_val: int):
            entry_123_seam_fix_width.set_text(str(a_val))
        widget_getters[entry_123_seam_fix_width.get_name()] = getter_123_seam_fix_width  # noqa
        widget_setters[entry_123_seam_fix_width.get_name()] = setter_123_seam_fix_width  # noqa

        label_123_seam_fix_mask_blur: Gtk.Label = Gtk.Label.new("Seam_Fix_Mask_Blur")
        label_123_seam_fix_mask_blur.set_margin_start(8)
        label_123_seam_fix_mask_blur.set_alignment(0.95, 0)
        entry_123_seam_fix_mask_blur: Gtk.Entry = Gtk.Entry.new()
        entry_123_seam_fix_mask_blur.set_text(str(8))
        entry_123_seam_fix_mask_blur.set_name("entry_123_seam_fix_mask_blur")
        entry_123_seam_fix_mask_blur.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_123_seam_fix_mask_blur,
                           minimum=0, maximum=128,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_123_seam_fix_mask_blur(source, **args):  # noqa
            pass
        entry_123_seam_fix_mask_blur.connect(SIG_CHANGED, change_handler_123_seam_fix_mask_blur)

        def getter_123_seam_fix_mask_blur() -> int:
            return int(entry_123_seam_fix_mask_blur.get_text())

        def setter_123_seam_fix_mask_blur(a_val: int):
            entry_123_seam_fix_mask_blur.set_text(str(a_val))
        widget_getters[entry_123_seam_fix_mask_blur.get_name()] = getter_123_seam_fix_mask_blur  # noqa
        widget_setters[entry_123_seam_fix_mask_blur.get_name()] = setter_123_seam_fix_mask_blur  # noqa

        label_123_seam_fix_padding: Gtk.Label = Gtk.Label.new("Seam_Fix_Padding")
        label_123_seam_fix_padding.set_margin_start(8)
        label_123_seam_fix_padding.set_alignment(0.95, 0)
        entry_123_seam_fix_padding: Gtk.Entry = Gtk.Entry.new()
        entry_123_seam_fix_padding.set_text(str(16))
        entry_123_seam_fix_padding.set_name("entry_123_seam_fix_padding")
        entry_123_seam_fix_padding.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_123_seam_fix_padding,
                           minimum=0, maximum=128,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_123_seam_fix_padding(source, **args):  # noqa
            pass
        entry_123_seam_fix_padding.connect(SIG_CHANGED, change_handler_123_seam_fix_padding)

        def getter_123_seam_fix_padding() -> int:
            return int(entry_123_seam_fix_padding.get_text())

        def setter_123_seam_fix_padding(a_val: int):
            entry_123_seam_fix_padding.set_text(str(a_val))
        widget_getters[entry_123_seam_fix_padding.get_name()] = getter_123_seam_fix_padding  # noqa
        widget_setters[entry_123_seam_fix_padding.get_name()] = setter_123_seam_fix_padding  # noqa

        checkbutton_123_force_uniform_tiles: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Force Uniform Tiles")  # noqa
        checkbutton_123_force_uniform_tiles.set_active(True)
        checkbutton_123_force_uniform_tiles.set_name("checkbutton_123_force_uniform_tiles")
        checkbutton_123_force_uniform_tiles.set_hexpand(False)

        def toggled_handler_123_force_uniform_tiles(source, **args):  # noqa
            pass
        checkbutton_123_force_uniform_tiles.connect(SIG_TOGGLED, toggled_handler_123_force_uniform_tiles)

        def getter_123_force_uniform_tiles():
            return "enable" if checkbutton_123_force_uniform_tiles.get_active() else "disable"
        widget_getters[checkbutton_123_force_uniform_tiles.get_name()] = getter_123_force_uniform_tiles  # noqa

        checkbutton_123_tiled_decode: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Tiled Decode")  # noqa
        checkbutton_123_tiled_decode.set_active(False)
        checkbutton_123_tiled_decode.set_name("checkbutton_123_tiled_decode")
        checkbutton_123_tiled_decode.set_hexpand(False)

        def toggled_handler_123_tiled_decode(source, **args):  # noqa
            pass
        checkbutton_123_tiled_decode.connect(SIG_TOGGLED, toggled_handler_123_tiled_decode)

        def getter_123_tiled_decode():
            return "enable" if checkbutton_123_tiled_decode.get_active() else "disable"
        widget_getters[checkbutton_123_tiled_decode.get_name()] = getter_123_tiled_decode  # noqa

        grid_123: Gtk.Grid = Gtk.Grid.new()
        grid_123.attach(label_123_upscale_by,                left=0, top=0, width=1, height=1)  # noqa
        grid_123.attach(scale_123_upscale_by,                left=1, top=0, width=3, height=1)  # noqa
        grid_123.attach(label_123_seed,                      left=0, top=1, width=1, height=1)  # noqa
        grid_123.attach(entry_123_seed,                      left=1, top=1, width=3, height=1)  # noqa
        grid_123.attach(label_123_steps,                     left=0, top=2, width=1, height=1)  # noqa
        grid_123.attach(entry_123_steps,                     left=1, top=2, width=3, height=1)  # noqa
        grid_123.attach(label_123_cfg,                       left=0, top=3, width=1, height=1)  # noqa
        grid_123.attach(scale_123_cfg,                       left=1, top=3, width=3, height=1)  # noqa
        grid_123.attach(label_123_sampler_name,              left=0, top=4, width=1, height=1)  # noqa
        grid_123.attach(comboboxtext_123_sampler_name,       left=1, top=4, width=3, height=1)  # noqa
        grid_123.attach(label_123_scheduler,                 left=0, top=5, width=1, height=1)  # noqa
        grid_123.attach(comboboxtext_123_scheduler,          left=1, top=5, width=3, height=1)  # noqa
        grid_123.attach(label_123_denoise,                   left=0, top=6, width=1, height=1)  # noqa
        grid_123.attach(scale_123_denoise,                   left=1, top=6, width=3, height=1)  # noqa
        grid_123.attach(label_123_mode_type,                 left=0, top=7, width=1, height=1)  # noqa
        grid_123.attach(comboboxtext_123_mode_type,          left=1, top=7, width=3, height=1)  # noqa
        grid_123.attach(label_123_mask_blur,                 left=0, top=8, width=1, height=1)  # noqa
        grid_123.attach(entry_123_mask_blur,                 left=1, top=8, width=3, height=1)  # noqa
        grid_123.attach(label_123_tile_padding,              left=0, top=9, width=1, height=1)  # noqa
        grid_123.attach(entry_123_tile_padding,              left=1, top=9, width=3, height=1)  # noqa
        grid_123.attach(label_123_seam_fix_mode,             left=0, top=10, width=1, height=1)  # noqa
        grid_123.attach(comboboxtext_123_seam_fix_mode,      left=1, top=10, width=3, height=1)  # noqa
        grid_123.attach(label_123_seam_fix_denoise,          left=0, top=11, width=1, height=1)  # noqa
        grid_123.attach(scale_123_seam_fix_denoise,          left=1, top=11, width=3, height=1)  # noqa
        grid_123.attach(label_123_seam_fix_width,            left=0, top=12, width=1, height=1)  # noqa
        grid_123.attach(entry_123_seam_fix_width,            left=1, top=12, width=3, height=1)  # noqa
        grid_123.attach(label_123_seam_fix_mask_blur,        left=0, top=13, width=1, height=1)  # noqa
        grid_123.attach(entry_123_seam_fix_mask_blur,        left=1, top=13, width=3, height=1)  # noqa
        grid_123.attach(label_123_seam_fix_padding,          left=0, top=14, width=1, height=1)  # noqa
        grid_123.attach(entry_123_seam_fix_padding,          left=1, top=14, width=3, height=1)  # noqa
        grid_123.attach(checkbutton_123_force_uniform_tiles, left=0, top=15, width=4, height=1)  # noqa
        grid_123.attach(checkbutton_123_tiled_decode,        left=0, top=16, width=4, height=1)  # noqa
        grid_123.set_column_homogeneous(False)
        grid_123.set_row_homogeneous(False)
        frame_ultimatesdupscale_123ultimate_sd_upscale.add(widget=grid_123)  # noqa

        # New Frame
        frame_upscalemodelloader_124load_upscale_model: Gtk.Frame = Gtk.Frame.new(label="Load Upscale Model")  # noqa
        frame_upscalemodelloader_124load_upscale_model.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_124_model_name: Gtk.Label = Gtk.Label.new("Model_Name")
        comboboxtext_124_model_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_124_model_name: list[str] = get_models_filenames(
            model_type=ModelType.UPSCALE_MODELS,
            cu_origin=self.comfy_svr_origin)
        if combo_values_124_model_name is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_124_model_name:
            raise ValueError(fr"No models retrieved from ComfyUI")  # noqa
        for combo_item_path in combo_values_124_model_name:
            comboboxtext_124_model_name.append_text(combo_item_path)
        comboboxtext_124_model_name.set_name("comboboxtext_124_model_name")
        comboboxtext_124_model_name.set_hexpand(True)
        comboboxtext_124_model_name.set_active(0)

        def change_handler_124_model_name(source, **args):  # noqa
            pass
        comboboxtext_124_model_name.connect(SIG_CHANGED, change_handler_124_model_name)

        def setter_124_model_name(a_val: str):
            nonlocal combo_values_124_model_name
            selected_index = combo_values_124_model_name.index(a_val)
            comboboxtext_124_model_name.set_active(selected_index)
        widget_getters[comboboxtext_124_model_name.get_name()] = comboboxtext_124_model_name.get_active_text  # noqa
        widget_setters[comboboxtext_124_model_name.get_name()] = setter_124_model_name  # noqa

        grid_124: Gtk.Grid = Gtk.Grid.new()
        grid_124.attach(label_124_model_name,        left=0, top=0, width=1, height=1)  # noqa
        grid_124.attach(comboboxtext_124_model_name, left=1, top=0, width=3, height=1)  # noqa
        grid_124.set_column_homogeneous(False)
        grid_124.set_row_homogeneous(False)
        frame_upscalemodelloader_124load_upscale_model.add(widget=grid_124)  # noqa

        # New Frame
        frame_getimagesizeandcount_125get_image_size__count: Gtk.Frame = Gtk.Frame.new(label="Get Image Size & Count")  # noqa
        frame_getimagesizeandcount_125get_image_size__count.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        grid_125: Gtk.Grid = Gtk.Grid.new()
        grid_125.set_column_homogeneous(False)
        grid_125.set_row_homogeneous(False)
        frame_getimagesizeandcount_125get_image_size__count.add(widget=grid_125)  # noqa

        # New Frame
        frame_saveimage_128save_upscaled: Gtk.Frame = Gtk.Frame.new(label="Save Upscaled")  # noqa
        frame_saveimage_128save_upscaled.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_128_filename_prefix: Gtk.Label = Gtk.Label.new("Filename_Prefix")
        entry_128_filename_prefix: Gtk.Entry = Gtk.Entry.new()
        entry_128_filename_prefix.set_text("generated")
        entry_128_filename_prefix.set_name("entry_128_filename_prefix")
        entry_128_filename_prefix.set_hexpand(True)
        widget_getters[entry_128_filename_prefix.get_name()] = entry_128_filename_prefix.get_text
        widget_setters[entry_128_filename_prefix.get_name()] = entry_128_filename_prefix.set_text

        grid_128: Gtk.Grid = Gtk.Grid.new()
        grid_128.attach(label_128_filename_prefix, left=0, top=0, width=1, height=1)  # noqa
        grid_128.attach(entry_128_filename_prefix, left=1, top=0, width=3, height=1)  # noqa
        grid_128.set_column_homogeneous(False)
        grid_128.set_row_homogeneous(False)
        frame_saveimage_128save_upscaled.add(widget=grid_128)  # noqa

        # New Frame
        frame_saveimage_129save_original_scale: Gtk.Frame = Gtk.Frame.new(label="Save Original Scale")  # noqa
        frame_saveimage_129save_original_scale.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_129_filename_prefix: Gtk.Label = Gtk.Label.new("Filename_Prefix")
        entry_129_filename_prefix: Gtk.Entry = Gtk.Entry.new()
        entry_129_filename_prefix.set_text("generated")
        entry_129_filename_prefix.set_name("entry_129_filename_prefix")
        entry_129_filename_prefix.set_hexpand(True)
        widget_getters[entry_129_filename_prefix.get_name()] = entry_129_filename_prefix.get_text
        widget_setters[entry_129_filename_prefix.get_name()] = entry_129_filename_prefix.set_text

        grid_129: Gtk.Grid = Gtk.Grid.new()
        grid_129.attach(label_129_filename_prefix, left=0, top=0, width=1, height=1)  # noqa
        grid_129.attach(entry_129_filename_prefix, left=1, top=0, width=3, height=1)  # noqa
        grid_129.set_column_homogeneous(False)
        grid_129.set_row_homogeneous(False)
        frame_saveimage_129save_original_scale.add(widget=grid_129)  # noqa

        content_area: Gtk.Box = dialog.get_content_area()
        main_scrollable: Gtk.ScrolledWindow = Gtk.ScrolledWindow()
        subject_box: Gtk.Box = Gtk.Box()
        subject_box.set_orientation(Gtk.Orientation.VERTICAL)

        subject_box.pack_start(child=frame_cliptextencode_006positive_prompt, expand=True, fill=True, padding=0)  # noqa
        subject_box.pack_start(child=frame_vaeloader_010load_vae, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_dualcliploader_011dualcliploader, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_unetloader_012load_diffusion_model, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_tobasicpipe_047tobasicpipe, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_emptylatentimage_049empty_latent_image, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_impactksampleradvancedbasicpipe_097ksampler_pass2_advancedpipe, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_impactksampleradvancedbasicpipe_098ksampler_pass1_advancedpipe, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_dynamicthresholdingfull_100dynamicthresholdingfull, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_cliptextencode_101negative_prompt, expand=True, fill=True, padding=0)  # noqa
        subject_box.pack_start(child=frame_editbasicpipe_103edit_basicpipe, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_frombasicpipe_v2_104frombasicpipe_v2, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_vaedecode_111vae_decode, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_sd_4xupscale_conditioning_121sd_4xupscale_conditioning, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_efficient_loader_122efficient_loader, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_ultimatesdupscale_123ultimate_sd_upscale, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_upscalemodelloader_124load_upscale_model, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_getimagesizeandcount_125get_image_size__count, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_saveimage_128save_upscaled, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_saveimage_129save_original_scale, expand=False, fill=False, padding=0)  # noqa

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
