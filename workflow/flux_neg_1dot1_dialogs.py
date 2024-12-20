
import gi

gi.require_version("Gegl", "0.4")  # noqa: E402
gi.require_version('Gimp', '3.0')  # noqa: E402
gi.require_version('GimpUi', '3.0')  # noqa: E402

# noinspection PyUnresolvedReferences
from gi.repository import Gegl, Gimp, GimpUi
from typing import Set
from utilities.cui_resources_utils import *
from utilities.heterogeneous import *
from utilities.persister_petite import *
from utilities.sd_gui_utils import *
from workflow.node_accessor import NodesAccessor
from workflow.workflow_dialog_factory import WorkflowDialogFactory


class FluxNeg1Dot1Dialogs(WorkflowDialogFactory):

    WORKFLOW_FILE = "flux_neg_1.1_workflow_api.json"

    def __init__(self, accessor: NodesAccessor):
        super().__init__(
            accessor=accessor,
            api_workflow=FluxNeg1Dot1Dialogs.WORKFLOW_FILE,
            dialog_config_chassis_name="FluxNeg1Dot1Dialogs_dialog_config",
            wf_data_chassis_name="FluxNeg1Dot1Dialogs_wf_data",
        )

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
                                                     chassis_name="flux_neg_1dot1_dialog",
                                                     fallback_path=fallback_path)
        dialog_data: Dict = dict(persister.load_config())
        widget_getters: Dict[str, Callable[[], Any]] = {}
        widget_setters: Dict[str, Callable[[Any], None]] = {}

        @gtk_idle_add
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

        @gtk_idle_add
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
        frame_cliptextencode_006positive_prompt: Gtk.Frame = Gtk.Frame.new(label="Positive Prompt        #6")  # noqa
        frame_cliptextencode_006positive_prompt.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_6_text: Gtk.Label = Gtk.Label.new("Text")
        textview_6_text: Gtk.TextView = Gtk.TextView.new()
        textview_6_text.get_buffer().set_text("photograph of a street")  # noqa
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
        frame_vaeloader_010load_vae: Gtk.Frame = Gtk.Frame.new(label="Load VAE        #10")  # noqa
        frame_vaeloader_010load_vae.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_10_vae_name: Gtk.Label = Gtk.Label.new("Vae_Name")
        comboboxtext_10_vae_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_10_vae_name: list[str] = get_models_filenames(
            model_type=ModelType.VAE,
            cu_origin=self.comfy_svr_origin)
        if combo_values_10_vae_name is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_10_vae_name:
            raise ValueError(fr"No models retrieved from ComfyUI")
        combo_values_10_vae_name = ['Baked VAE'] + combo_values_10_vae_name
        for combo_item_path in combo_values_10_vae_name:
            comboboxtext_10_vae_name.append_text(combo_item_path)
        comboboxtext_10_vae_name.set_name("comboboxtext_10_vae_name")
        comboboxtext_10_vae_name.set_hexpand(True)
        comboboxtext_10_vae_name.set_active(1)

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
        frame_dualcliploader_011dualcliploader: Gtk.Frame = Gtk.Frame.new(label="DualCLIPLoader        #11")  # noqa
        frame_dualcliploader_011dualcliploader.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_11_clip_name1: Gtk.Label = Gtk.Label.new("Clip_Name1")
        comboboxtext_11_clip_name1: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_11_clip_name1: list[str] = get_models_filenames(
            model_type=ModelType.CLIP,
            cu_origin=self.comfy_svr_origin)
        if combo_values_11_clip_name1 is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_11_clip_name1:
            raise ValueError(fr"No models retrieved from ComfyUI")
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
            raise ValueError(fr"No models retrieved from ComfyUI")
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
        frame_unetloader_012load_diffusion_model: Gtk.Frame = Gtk.Frame.new(label="Load Diffusion Model        #12")  # noqa
        frame_unetloader_012load_diffusion_model.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_12_unet_name: Gtk.Label = Gtk.Label.new("Unet_Name")
        comboboxtext_12_unet_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_12_unet_name: list[str] = get_models_filenames(
            model_type=ModelType.UNET,
            cu_origin=self.comfy_svr_origin)
        if combo_values_12_unet_name is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_12_unet_name:
            raise ValueError(fr"No models retrieved from ComfyUI")
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
        frame_emptylatentimage_049empty_latent_image: Gtk.Frame = Gtk.Frame.new(label="Empty Latent Image        #49")  # noqa
        frame_emptylatentimage_049empty_latent_image.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_49_width: Gtk.Label = Gtk.Label.new("Width")
        label_49_width.set_margin_start(8)
        label_49_width.set_alignment(0.95, 0)  # noqa
        entry_49_width: Gtk.Entry = Gtk.Entry.new()
        entry_49_width.set_text(str(1040))
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
        label_49_height.set_alignment(0.95, 0)  # noqa
        entry_49_height: Gtk.Entry = Gtk.Entry.new()
        entry_49_height.set_text(str(1200))
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
        label_49_batch_size.set_alignment(0.95, 0)  # noqa
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
        frame_impactksampleradvancedbasicpipe_097ksampler_advancedpipe: Gtk.Frame = Gtk.Frame.new(label="KSampler (Advanced/pipe)        #97")  # noqa
        frame_impactksampleradvancedbasicpipe_097ksampler_advancedpipe.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        checkbutton_97_add_noise: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Add Noise")  # noqa
        checkbutton_97_add_noise.set_active(False)
        checkbutton_97_add_noise.set_name("checkbutton_97_add_noise")
        checkbutton_97_add_noise.set_hexpand(False)

        def toggled_handler_97_add_noise(source, **args):  # noqa
            pass
        checkbutton_97_add_noise.connect(SIG_TOGGLED, toggled_handler_97_add_noise)

        def getter_97_add_noise():
            return checkbutton_97_add_noise.get_active()
        widget_getters[checkbutton_97_add_noise.get_name()] = getter_97_add_noise  # noqa

        label_97_noise_seed: Gtk.Label = Gtk.Label.new("Noise_Seed")
        label_97_noise_seed.set_margin_start(8)
        label_97_noise_seed.set_alignment(0.95, 0)  # noqa
        entry_97_noise_seed: Gtk.Entry = Gtk.Entry.new()
        entry_97_noise_seed.set_text(str(101))
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
        label_97_steps.set_alignment(0.95, 0)  # noqa
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
        adjustment_97_cfg: Gtk.Adjustment = Gtk.Adjustment(value=3.50000,
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
        label_97_start_at_step.set_alignment(0.95, 0)  # noqa
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
        label_97_end_at_step.set_alignment(0.95, 0)  # noqa
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
            return checkbutton_97_return_with_leftover_noise.get_active()
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
        frame_impactksampleradvancedbasicpipe_097ksampler_advancedpipe.add(widget=grid_97)  # noqa

        # New Frame
        frame_impactksampleradvancedbasicpipe_098ksampler_advancedpipe: Gtk.Frame = Gtk.Frame.new(label="KSampler (Advanced/pipe)        #98")  # noqa
        frame_impactksampleradvancedbasicpipe_098ksampler_advancedpipe.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        checkbutton_98_add_noise: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Add Noise")  # noqa
        checkbutton_98_add_noise.set_active(True)
        checkbutton_98_add_noise.set_name("checkbutton_98_add_noise")
        checkbutton_98_add_noise.set_hexpand(False)

        def toggled_handler_98_add_noise(source, **args):  # noqa
            pass
        checkbutton_98_add_noise.connect(SIG_TOGGLED, toggled_handler_98_add_noise)

        def getter_98_add_noise():
            return checkbutton_98_add_noise.get_active()
        widget_getters[checkbutton_98_add_noise.get_name()] = getter_98_add_noise  # noqa

        label_98_noise_seed: Gtk.Label = Gtk.Label.new("Noise_Seed")
        label_98_noise_seed.set_margin_start(8)
        label_98_noise_seed.set_alignment(0.95, 0)  # noqa
        entry_98_noise_seed: Gtk.Entry = Gtk.Entry.new()
        entry_98_noise_seed.set_text(str(101))
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
        label_98_steps.set_alignment(0.95, 0)  # noqa
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
        adjustment_98_cfg: Gtk.Adjustment = Gtk.Adjustment(value=3.50000,
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
        label_98_start_at_step.set_alignment(0.95, 0)  # noqa
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
        label_98_end_at_step.set_alignment(0.95, 0)  # noqa
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
            return checkbutton_98_return_with_leftover_noise.get_active()
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
        frame_impactksampleradvancedbasicpipe_098ksampler_advancedpipe.add(widget=grid_98)  # noqa

        # New Frame
        frame_dynamicthresholdingfull_100dynamicthresholdingfull: Gtk.Frame = Gtk.Frame.new(label="DynamicThresholdingFull        #100")  # noqa
        frame_dynamicthresholdingfull_100dynamicthresholdingfull.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_100_mimic_scale: Gtk.Label = Gtk.Label.new("Mimic_Scale")
        label_100_mimic_scale.set_margin_start(8)
        label_100_mimic_scale.set_alignment(0.95, 0)  # noqa
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
        label_100_threshold_percentile.set_alignment(0.95, 0)  # noqa
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
        label_100_mimic_scale_min.set_alignment(0.95, 0)  # noqa
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
        label_100_cfg_scale_min.set_alignment(0.95, 0)  # noqa
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
        label_100_sched_val.set_alignment(0.95, 0)  # noqa
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
        label_100_separate_feature_channels.set_alignment(0.95, 0)  # noqa
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
        label_100_interpolate_phi.set_alignment(0.95, 0)  # noqa
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
        frame_cliptextencode_101negative_prompt: Gtk.Frame = Gtk.Frame.new(label="Negative Prompt        #101")  # noqa
        frame_cliptextencode_101negative_prompt.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_101_text: Gtk.Label = Gtk.Label.new("Text")
        textview_101_text: Gtk.TextView = Gtk.TextView.new()
        textview_101_text.get_buffer().set_text("car cars autos man men woman women pedestrians people")  # noqa
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
        frame_saveimage_111save_image: Gtk.Frame = Gtk.Frame.new(label="Save Image        #111")  # noqa
        frame_saveimage_111save_image.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_111_filename_prefix: Gtk.Label = Gtk.Label.new("Filename_Prefix")
        entry_111_filename_prefix: Gtk.Entry = Gtk.Entry.new()
        entry_111_filename_prefix.set_text("gimp_generated")
        entry_111_filename_prefix.set_name("entry_111_filename_prefix")
        entry_111_filename_prefix.set_hexpand(True)
        widget_getters[entry_111_filename_prefix.get_name()] = entry_111_filename_prefix.get_text
        widget_setters[entry_111_filename_prefix.get_name()] = entry_111_filename_prefix.set_text

        grid_111: Gtk.Grid = Gtk.Grid.new()
        grid_111.attach(label_111_filename_prefix, left=0, top=0, width=1, height=1)  # noqa
        grid_111.attach(entry_111_filename_prefix, left=1, top=0, width=3, height=1)  # noqa
        grid_111.set_column_homogeneous(False)
        grid_111.set_row_homogeneous(False)
        frame_saveimage_111save_image.add(widget=grid_111)  # noqa

        content_area: Gtk.Box = dialog.get_content_area()
        main_scrollable: Gtk.ScrolledWindow = Gtk.ScrolledWindow()
        subject_box: Gtk.Box = Gtk.Box()
        subject_box.set_orientation(Gtk.Orientation.VERTICAL)

        subject_box.pack_start(child=frame_cliptextencode_006positive_prompt, expand=True, fill=True, padding=0)  # noqa
        subject_box.pack_start(child=frame_vaeloader_010load_vae, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_dualcliploader_011dualcliploader, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_unetloader_012load_diffusion_model, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_emptylatentimage_049empty_latent_image, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_impactksampleradvancedbasicpipe_097ksampler_advancedpipe, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_impactksampleradvancedbasicpipe_098ksampler_advancedpipe, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_dynamicthresholdingfull_100dynamicthresholdingfull, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_cliptextencode_101negative_prompt, expand=True, fill=True, padding=0)  # noqa
        subject_box.pack_start(child=frame_saveimage_111save_image, expand=False, fill=False, padding=0)  # noqa

        subject_box.set_vexpand(True)
        subject_box.set_hexpand(True)
        main_scrollable.add(subject_box)  # noqa
        main_scrollable.set_size_request(1280, 928)
        main_scrollable.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        content_area.add(main_scrollable)  # noqa

        button_cancel.connect("clicked", delete_results)
        button_apply.connect("clicked", assign_results)
        button_ok.connect("clicked", assign_results)

        fill_widget_values()
        dialog.show_all()
        return dialog
