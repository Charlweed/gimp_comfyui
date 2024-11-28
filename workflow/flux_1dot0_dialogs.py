
import gi

gi.require_version("Gegl", "0.4")  # noqa: E402
gi.require_version('Gimp', '3.0')  # noqa: E402
gi.require_version('GimpUi', '3.0')  # noqa: E402
# gi.require_version('Gdk', '3.0')  # noqa: E402
# gi.require_version("Gtk", "3.0")  # noqa: E402

# noinspection PyUnresolvedReferences
from gi.repository import Gegl, Gimp, GimpUi
# from gi.repository import Gdk, Gio, Gtk, GLib, GObject
from typing import Set
from utilities.cui_resources_utils import *
from utilities.heterogeneous import *
from utilities.persister_petite import *
from utilities.sd_gui_utils import *
from workflow.node_accessor import NodesAccessor
from workflow.workflow_dialog_factory import WorkflowDialogFactory


class Flux1Dot0Dialogs(WorkflowDialogFactory):

    WORKFLOW_FILE = "flux_1.0_workflow_api.json"

    def __init__(self, accessor: NodesAccessor):
        super().__init__(
            accessor=accessor,
            api_workflow=Flux1Dot0Dialogs.WORKFLOW_FILE,
            dialog_config_chassis_name="Flux1Dot0Dialogs_dialog_config",
            wf_data_chassis_name="Flux1Dot0Dialogs_wf_data",
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
                                                     chassis_name="flux_1dot0_dialog",
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
        frame_cliptextencode_006clip_text_encode_positive_prompt: Gtk.Frame = Gtk.Frame.new(label="CLIP Text Encode (Positive Prompt)        #6")  # noqa
        frame_cliptextencode_006clip_text_encode_positive_prompt.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_6_text: Gtk.Label = Gtk.Label.new("Text")
        textview_6_text: Gtk.TextView = Gtk.TextView.new()
        textview_6_text.get_buffer().set_text("cute anime girl with massive fluffy fennec ears and a big fluffy tail blonde messy long hair blue eyes wearing a maid outfit with a long black gold leaf pattern dress and a white apron mouth open holding a fancy black forest cake with candles on top in the kitchen of an old dark Victorian mansion lit by candlelight with a bright window to the foggy forest and very expensive stuff everywhere")  # noqa
        textview_6_text.set_name("textview_6_text")
        textview_6_text.set_hexpand(True)
        textview_6_text.set_vexpand(True)
        textview_6_text.set_valign(Gtk.Align.FILL)
        # Create a ScrolledWindow to hold the TextView
        scrolled_window_6_text = Gtk.ScrolledWindow()
        scrolled_window_6_text.add(textview_6_text)  # noqa
        scrolled_window_6_text.set_size_request(288, 96)

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
        frame_cliptextencode_006clip_text_encode_positive_prompt.add(widget=grid_6)  # noqa

        # New Frame
        frame_saveimage_009save_image: Gtk.Frame = Gtk.Frame.new(label="Save Image        #9")  # noqa
        frame_saveimage_009save_image.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_9_filename_prefix: Gtk.Label = Gtk.Label.new("Filename_Prefix")
        entry_9_filename_prefix: Gtk.Entry = Gtk.Entry.new()
        entry_9_filename_prefix.set_text("gimp_generated")
        entry_9_filename_prefix.set_name("entry_9_filename_prefix")
        entry_9_filename_prefix.set_hexpand(True)
        widget_getters[entry_9_filename_prefix.get_name()] = entry_9_filename_prefix.get_text
        widget_setters[entry_9_filename_prefix.get_name()] = entry_9_filename_prefix.set_text

        grid_9: Gtk.Grid = Gtk.Grid.new()
        grid_9.attach(label_9_filename_prefix, left=0, top=0, width=1, height=1)  # noqa
        grid_9.attach(entry_9_filename_prefix, left=1, top=0, width=3, height=1)  # noqa
        grid_9.set_column_homogeneous(False)
        grid_9.set_row_homogeneous(False)
        frame_saveimage_009save_image.add(widget=grid_9)  # noqa

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
        comboboxtext_12_weight_dtype.set_active(0)

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
        frame_ksamplerselect_016ksamplerselect: Gtk.Frame = Gtk.Frame.new(label="KSamplerSelect        #16")  # noqa
        frame_ksamplerselect_016ksamplerselect.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_16_sampler_name: Gtk.Label = Gtk.Label.new("Sampler_Name")
        comboboxtext_16_sampler_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_16_sampler_name: list[str] = ["euler", "euler_ancestral", "heun", "heunpp2", "dpm_2", "dpm_2_ancestral", "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_sde", "dpmpp_sde_gpu", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu", "ddpm", "lcm", "ddim", "uni_pc", "uni_pc_bh2"]  # noqa
        for combo_item_path in combo_values_16_sampler_name:
            comboboxtext_16_sampler_name.append_text(combo_item_path)
        comboboxtext_16_sampler_name.set_name("comboboxtext_16_sampler_name")
        comboboxtext_16_sampler_name.set_hexpand(True)
        comboboxtext_16_sampler_name.set_active(0)

        def change_handler_16_sampler_name(source, **args):  # noqa
            pass
        comboboxtext_16_sampler_name.connect(SIG_CHANGED, change_handler_16_sampler_name)

        def setter_16_sampler_name(a_val: str):
            nonlocal combo_values_16_sampler_name
            selected_index = combo_values_16_sampler_name.index(a_val)
            comboboxtext_16_sampler_name.set_active(selected_index)
        widget_getters[comboboxtext_16_sampler_name.get_name()] = comboboxtext_16_sampler_name.get_active_text  # noqa
        widget_setters[comboboxtext_16_sampler_name.get_name()] = setter_16_sampler_name  # noqa

        grid_16: Gtk.Grid = Gtk.Grid.new()
        grid_16.attach(label_16_sampler_name,        left=0, top=0, width=1, height=1)  # noqa
        grid_16.attach(comboboxtext_16_sampler_name, left=1, top=0, width=3, height=1)  # noqa
        grid_16.set_column_homogeneous(False)
        grid_16.set_row_homogeneous(False)
        frame_ksamplerselect_016ksamplerselect.add(widget=grid_16)  # noqa

        # New Frame
        frame_basicscheduler_017basicscheduler: Gtk.Frame = Gtk.Frame.new(label="BasicScheduler        #17")  # noqa
        frame_basicscheduler_017basicscheduler.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_17_scheduler: Gtk.Label = Gtk.Label.new("Scheduler")
        comboboxtext_17_scheduler: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_17_scheduler: list[str] = ["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"]  # noqa
        for combo_item_path in combo_values_17_scheduler:
            comboboxtext_17_scheduler.append_text(combo_item_path)
        comboboxtext_17_scheduler.set_name("comboboxtext_17_scheduler")
        comboboxtext_17_scheduler.set_hexpand(True)
        comboboxtext_17_scheduler.set_active(4)

        def change_handler_17_scheduler(source, **args):  # noqa
            pass
        comboboxtext_17_scheduler.connect(SIG_CHANGED, change_handler_17_scheduler)

        def setter_17_scheduler(a_val: str):
            nonlocal combo_values_17_scheduler
            selected_index = combo_values_17_scheduler.index(a_val)
            comboboxtext_17_scheduler.set_active(selected_index)
        widget_getters[comboboxtext_17_scheduler.get_name()] = comboboxtext_17_scheduler.get_active_text  # noqa
        widget_setters[comboboxtext_17_scheduler.get_name()] = setter_17_scheduler  # noqa

        label_17_steps: Gtk.Label = Gtk.Label.new("Steps")
        label_17_steps.set_margin_start(8)
        label_17_steps.set_alignment(0.95, 0)  # noqa
        entry_17_steps: Gtk.Entry = Gtk.Entry.new()
        entry_17_steps.set_text(str(20))
        entry_17_steps.set_name("entry_17_steps")
        entry_17_steps.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_17_steps,
                           minimum=1, maximum=128,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_17_steps(source, **args):  # noqa
            pass
        entry_17_steps.connect(SIG_CHANGED, change_handler_17_steps)

        def getter_17_steps() -> int:
            return int(entry_17_steps.get_text())

        def setter_17_steps(a_val: int):
            entry_17_steps.set_text(str(a_val))
        widget_getters[entry_17_steps.get_name()] = getter_17_steps  # noqa
        widget_setters[entry_17_steps.get_name()] = setter_17_steps  # noqa

        label_17_denoise: Gtk.Label = Gtk.Label.new("Denoise")
        label_17_denoise.set_margin_start(8)
        label_17_denoise.set_alignment(0.95, 0)  # noqa
        adjustment_17_denoise: Gtk.Adjustment = Gtk.Adjustment(value=1.00000,
                                                               lower=0.00001,
                                                               upper=1.00000,
                                                               step_increment=0.001,
                                                               page_increment=0.010,
                                                               page_size=0)
        scale_17_denoise: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_17_denoise)  # noqa
        scale_17_denoise.set_name("scale_17_denoise")
        scale_17_denoise.set_digits(3)
        scale_17_denoise.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_17_denoise.set_hexpand(True)

        def change_handler_17_denoise(source, **args):  # noqa
            pass
        scale_17_denoise.connect(SIG_VALUE_CHANGED, change_handler_17_denoise)
        widget_getters[scale_17_denoise.get_name()] = scale_17_denoise.get_value
        widget_setters[scale_17_denoise.get_name()] = scale_17_denoise.set_value

        grid_17: Gtk.Grid = Gtk.Grid.new()
        grid_17.attach(label_17_scheduler,        left=0, top=0, width=1, height=1)  # noqa
        grid_17.attach(comboboxtext_17_scheduler, left=1, top=0, width=3, height=1)  # noqa
        grid_17.attach(label_17_steps,            left=0, top=1, width=1, height=1)  # noqa
        grid_17.attach(entry_17_steps,            left=1, top=1, width=3, height=1)  # noqa
        grid_17.attach(label_17_denoise,          left=0, top=2, width=1, height=1)  # noqa
        grid_17.attach(scale_17_denoise,          left=1, top=2, width=3, height=1)  # noqa
        grid_17.set_column_homogeneous(False)
        grid_17.set_row_homogeneous(False)
        frame_basicscheduler_017basicscheduler.add(widget=grid_17)  # noqa

        # New Frame
        frame_randomnoise_025randomnoise: Gtk.Frame = Gtk.Frame.new(label="RandomNoise        #25")  # noqa
        frame_randomnoise_025randomnoise.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_25_noise_seed: Gtk.Label = Gtk.Label.new("Noise_Seed")
        label_25_noise_seed.set_margin_start(8)
        label_25_noise_seed.set_alignment(0.95, 0)  # noqa
        entry_25_noise_seed: Gtk.Entry = Gtk.Entry.new()
        entry_25_noise_seed.set_text(str(219670278747233))
        entry_25_noise_seed.set_name("entry_25_noise_seed")
        entry_25_noise_seed.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_25_noise_seed,
                           minimum=-1, maximum=18446744073709519872,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_25_noise_seed(source, **args):  # noqa
            pass
        entry_25_noise_seed.connect(SIG_CHANGED, change_handler_25_noise_seed)

        def getter_25_noise_seed() -> int:
            return int(entry_25_noise_seed.get_text())

        def setter_25_noise_seed(a_val: int):
            entry_25_noise_seed.set_text(str(a_val))
        widget_getters[entry_25_noise_seed.get_name()] = getter_25_noise_seed  # noqa
        widget_setters[entry_25_noise_seed.get_name()] = setter_25_noise_seed  # noqa

        grid_25: Gtk.Grid = Gtk.Grid.new()
        grid_25.attach(label_25_noise_seed, left=0, top=0, width=1, height=1)  # noqa
        grid_25.attach(entry_25_noise_seed, left=1, top=0, width=3, height=1)  # noqa
        grid_25.set_column_homogeneous(False)
        grid_25.set_row_homogeneous(False)
        frame_randomnoise_025randomnoise.add(widget=grid_25)  # noqa

        # New Frame
        frame_fluxguidance_026fluxguidance: Gtk.Frame = Gtk.Frame.new(label="FluxGuidance        #26")  # noqa
        frame_fluxguidance_026fluxguidance.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_26_guidance: Gtk.Label = Gtk.Label.new("Guidance")
        label_26_guidance.set_margin_start(8)
        adjustment_26_guidance: Gtk.Adjustment = Gtk.Adjustment(value=3.50000,
                                                                lower=0.00000,
                                                                upper=10.00000,
                                                                step_increment=1.000,
                                                                page_increment=2.000,
                                                                page_size=0)
        scale_26_guidance: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_26_guidance)  # noqa
        scale_26_guidance.set_name("scale_26_guidance")
        scale_26_guidance.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_26_guidance.set_hexpand(True)

        def change_handler_26_guidance(source, **args):  # noqa
            pass
        scale_26_guidance.connect(SIG_VALUE_CHANGED, change_handler_26_guidance)
        widget_getters[scale_26_guidance.get_name()] = scale_26_guidance.get_value
        widget_setters[scale_26_guidance.get_name()] = scale_26_guidance.set_value

        grid_26: Gtk.Grid = Gtk.Grid.new()
        grid_26.attach(label_26_guidance, left=0, top=0, width=1, height=1)  # noqa
        grid_26.attach(scale_26_guidance, left=1, top=0, width=3, height=1)  # noqa
        grid_26.set_column_homogeneous(False)
        grid_26.set_row_homogeneous(False)
        frame_fluxguidance_026fluxguidance.add(widget=grid_26)  # noqa

        # New Frame
        frame_emptysd3latentimage_027emptysd3latentimage: Gtk.Frame = Gtk.Frame.new(label="EmptySD3LatentImage        #27")  # noqa
        frame_emptysd3latentimage_027emptysd3latentimage.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_27_width: Gtk.Label = Gtk.Label.new("Width")
        label_27_width.set_margin_start(8)
        label_27_width.set_alignment(0.95, 0)  # noqa
        entry_27_width: Gtk.Entry = Gtk.Entry.new()
        entry_27_width.set_text(str(1024))
        entry_27_width.set_name("entry_27_width")
        entry_27_width.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_27_width,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_27_width(source, **args):  # noqa
            pass
        entry_27_width.connect(SIG_CHANGED, change_handler_27_width)

        def getter_27_width() -> int:
            return int(entry_27_width.get_text())

        def setter_27_width(a_val: int):
            entry_27_width.set_text(str(a_val))
        widget_getters[entry_27_width.get_name()] = getter_27_width  # noqa
        widget_setters[entry_27_width.get_name()] = setter_27_width  # noqa

        label_27_height: Gtk.Label = Gtk.Label.new("Height")
        label_27_height.set_margin_start(8)
        label_27_height.set_alignment(0.95, 0)  # noqa
        entry_27_height: Gtk.Entry = Gtk.Entry.new()
        entry_27_height.set_text(str(1024))
        entry_27_height.set_name("entry_27_height")
        entry_27_height.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_27_height,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_27_height(source, **args):  # noqa
            pass
        entry_27_height.connect(SIG_CHANGED, change_handler_27_height)

        def getter_27_height() -> int:
            return int(entry_27_height.get_text())

        def setter_27_height(a_val: int):
            entry_27_height.set_text(str(a_val))
        widget_getters[entry_27_height.get_name()] = getter_27_height  # noqa
        widget_setters[entry_27_height.get_name()] = setter_27_height  # noqa

        label_27_batch_size: Gtk.Label = Gtk.Label.new("Batch_Size")
        label_27_batch_size.set_margin_start(8)
        label_27_batch_size.set_alignment(0.95, 0)  # noqa
        entry_27_batch_size: Gtk.Entry = Gtk.Entry.new()
        entry_27_batch_size.set_text(str(1))
        entry_27_batch_size.set_name("entry_27_batch_size")
        entry_27_batch_size.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_27_batch_size,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_27_batch_size(source, **args):  # noqa
            pass
        entry_27_batch_size.connect(SIG_CHANGED, change_handler_27_batch_size)

        def getter_27_batch_size() -> int:
            return int(entry_27_batch_size.get_text())

        def setter_27_batch_size(a_val: int):
            entry_27_batch_size.set_text(str(a_val))
        widget_getters[entry_27_batch_size.get_name()] = getter_27_batch_size  # noqa
        widget_setters[entry_27_batch_size.get_name()] = setter_27_batch_size  # noqa

        grid_27: Gtk.Grid = Gtk.Grid.new()
        grid_27.attach(label_27_width,      left=0, top=0, width=1, height=1)  # noqa
        grid_27.attach(entry_27_width,      left=1, top=0, width=3, height=1)  # noqa
        grid_27.attach(label_27_height,     left=4, top=0, width=1, height=1)  # noqa
        grid_27.attach(entry_27_height,     left=5, top=0, width=3, height=1)  # noqa
        grid_27.attach(label_27_batch_size, left=8, top=0, width=1, height=1)  # noqa
        grid_27.attach(entry_27_batch_size, left=9, top=0, width=3, height=1)  # noqa
        grid_27.set_column_homogeneous(False)
        grid_27.set_row_homogeneous(False)
        frame_emptysd3latentimage_027emptysd3latentimage.add(widget=grid_27)  # noqa

        # New Frame
        frame_modelsamplingflux_030modelsamplingflux: Gtk.Frame = Gtk.Frame.new(label="ModelSamplingFlux        #30")  # noqa
        frame_modelsamplingflux_030modelsamplingflux.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_30_max_shift: Gtk.Label = Gtk.Label.new("Max_Shift")
        label_30_max_shift.set_margin_start(8)
        adjustment_30_max_shift: Gtk.Adjustment = Gtk.Adjustment(value=1.15000,
                                                                 lower=0.00001,
                                                                 upper=3.00000,
                                                                 step_increment=0.001,
                                                                 page_increment=0.010,
                                                                 page_size=0)
        scale_30_max_shift: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_30_max_shift)  # noqa
        scale_30_max_shift.set_name("scale_30_max_shift")
        scale_30_max_shift.set_digits(3)
        scale_30_max_shift.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_30_max_shift.set_hexpand(True)

        def change_handler_30_max_shift(source, **args):  # noqa
            pass
        scale_30_max_shift.connect(SIG_VALUE_CHANGED, change_handler_30_max_shift)
        widget_getters[scale_30_max_shift.get_name()] = scale_30_max_shift.get_value
        widget_setters[scale_30_max_shift.get_name()] = scale_30_max_shift.set_value

        label_30_base_shift: Gtk.Label = Gtk.Label.new("Base_Shift")
        label_30_base_shift.set_margin_start(8)
        adjustment_30_base_shift: Gtk.Adjustment = Gtk.Adjustment(value=0.50000,
                                                                  lower=0.00001,
                                                                  upper=3.00000,
                                                                  step_increment=0.001,
                                                                  page_increment=0.010,
                                                                  page_size=0)
        scale_30_base_shift: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_30_base_shift)  # noqa
        scale_30_base_shift.set_name("scale_30_base_shift")
        scale_30_base_shift.set_digits(3)
        scale_30_base_shift.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_30_base_shift.set_hexpand(True)

        def change_handler_30_base_shift(source, **args):  # noqa
            pass
        scale_30_base_shift.connect(SIG_VALUE_CHANGED, change_handler_30_base_shift)
        widget_getters[scale_30_base_shift.get_name()] = scale_30_base_shift.get_value
        widget_setters[scale_30_base_shift.get_name()] = scale_30_base_shift.set_value

        label_30_width: Gtk.Label = Gtk.Label.new("Width")
        label_30_width.set_margin_start(8)
        label_30_width.set_alignment(0.95, 0)  # noqa
        entry_30_width: Gtk.Entry = Gtk.Entry.new()
        entry_30_width.set_text(str(1024))
        entry_30_width.set_name("entry_30_width")
        entry_30_width.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_30_width,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_30_width(source, **args):  # noqa
            pass
        entry_30_width.connect(SIG_CHANGED, change_handler_30_width)

        def getter_30_width() -> int:
            return int(entry_30_width.get_text())

        def setter_30_width(a_val: int):
            entry_30_width.set_text(str(a_val))
        widget_getters[entry_30_width.get_name()] = getter_30_width  # noqa
        widget_setters[entry_30_width.get_name()] = setter_30_width  # noqa

        label_30_height: Gtk.Label = Gtk.Label.new("Height")
        label_30_height.set_margin_start(8)
        label_30_height.set_alignment(0.95, 0)  # noqa
        entry_30_height: Gtk.Entry = Gtk.Entry.new()
        entry_30_height.set_text(str(1024))
        entry_30_height.set_name("entry_30_height")
        entry_30_height.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_30_height,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_30_height(source, **args):  # noqa
            pass
        entry_30_height.connect(SIG_CHANGED, change_handler_30_height)

        def getter_30_height() -> int:
            return int(entry_30_height.get_text())

        def setter_30_height(a_val: int):
            entry_30_height.set_text(str(a_val))
        widget_getters[entry_30_height.get_name()] = getter_30_height  # noqa
        widget_setters[entry_30_height.get_name()] = setter_30_height  # noqa

        grid_30: Gtk.Grid = Gtk.Grid.new()
        grid_30.attach(label_30_max_shift,  left=0, top=0, width=1, height=1)  # noqa
        grid_30.attach(scale_30_max_shift,  left=1, top=0, width=7, height=1)  # noqa
        grid_30.attach(label_30_base_shift, left=0, top=1, width=1, height=1)  # noqa
        grid_30.attach(scale_30_base_shift, left=1, top=1, width=7, height=1)  # noqa
        grid_30.attach(label_30_width,      left=0, top=2, width=1, height=1)  # noqa
        grid_30.attach(entry_30_width,      left=1, top=2, width=3, height=1)  # noqa
        grid_30.attach(label_30_height,     left=4, top=2, width=1, height=1)  # noqa
        grid_30.attach(entry_30_height,     left=5, top=2, width=3, height=1)  # noqa
        grid_30.set_column_homogeneous(False)
        grid_30.set_row_homogeneous(False)
        frame_modelsamplingflux_030modelsamplingflux.add(widget=grid_30)  # noqa

        content_area: Gtk.Box = dialog.get_content_area()
        main_scrollable: Gtk.ScrolledWindow = Gtk.ScrolledWindow()
        subject_box: Gtk.Box = Gtk.Box()
        subject_box.set_orientation(Gtk.Orientation.VERTICAL)

        subject_box.pack_start(child=frame_cliptextencode_006clip_text_encode_positive_prompt, expand=True, fill=True, padding=0)  # noqa
        subject_box.pack_start(child=frame_saveimage_009save_image, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_vaeloader_010load_vae, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_dualcliploader_011dualcliploader, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_unetloader_012load_diffusion_model, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_ksamplerselect_016ksamplerselect, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_basicscheduler_017basicscheduler, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_randomnoise_025randomnoise, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_fluxguidance_026fluxguidance, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_emptysd3latentimage_027emptysd3latentimage, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_modelsamplingflux_030modelsamplingflux, expand=False, fill=False, padding=0)  # noqa

        subject_box.set_vexpand(True)
        subject_box.set_hexpand(True)
        main_scrollable.add(subject_box)  # noqa
        main_scrollable.set_size_request(1280, 928)
        main_scrollable.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        content_area.add(main_scrollable)  # noqa

        button_cancel.connect("clicked", delete_results)
        button_apply.connect("clicked", assign_results)
        button_ok.connect("clicked", assign_results)

        # Useless. The delays are BEFORE this dialog opens, and AFTER it closes.
        # progress_bar: GimpUi.ProgressBar = GimpUi.ProgressBar.new()
        # progress_bar.set_name("gimp_procedure_progressbar_00")
        # progress_bar.set_hexpand(True)
        # progress_bar.set_vexpand(True)
        # progress_bar.set_show_text(True)
        # progressbar_style_bytes: bytes = new_progressbar_css_bytes(widget=progress_bar)
        # install_css_styles(style_bytes=progressbar_style_bytes)
        # dialog_box.add(progress_bar)
        # progress_bar.show()

        # min_aspect and max_aspect must be the same on Mac
        # geometry = Gdk.Geometry()  # noqa
        # geometry.min_aspect = 1.0
        # geometry.max_aspect = 1.0
        # dialog.set_geometry_hints(None, geometry, Gdk.WindowHints.ASPECT)  # noqa
        fill_widget_values()
        dialog.show_all()
        return dialog
