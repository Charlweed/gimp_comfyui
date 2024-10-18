
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


class FluxNeg1Dot1Dialogs(WorkflowDialogFactory):

    WORKFLOW_FILE = "flux_neg_1.1_workflow_api.json"

    def __init__(self, accessor: NodesAccessor):
        super().__init__(
            accessor=accessor,
            api_workflow=FluxNeg1Dot1Dialogs.WORKFLOW_FILE,
            dialog_config_chassis_name="FluxNeg1Dot1Dialogs_dialog_config",
            wf_data_chassis_name="FluxNeg1Dot1Dialogs_wf_data",
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
                                                     chassis_name="flux_neg_1dot1_dialog",
                                                     fallback_path=fallback_path)
        dialog_data: Dict = dict(persister.load_config())
        widget_getters: Dict[str, Callable[[], Any]] = {}
        widget_setters: Dict[str, Callable[[Any], None]] = {}

        def fill_widget_values():
            for consumers in widget_setters.items():
                key_name: str = consumers[0]
                setter = consumers[1]
                try:
                    setter(dialog_data[key_name])
                except KeyError as k_err:  # noqa
                    pass
        
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
        grid_6.attach(scrolled_window_6_text, left=1, top=0, width=2, height=1)  # noqa
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
        widget_getters[comboboxtext_10_vae_name.get_name()] = comboboxtext_10_vae_name.get_active_text
        widget_setters[comboboxtext_10_vae_name.get_name()] = setter_10_vae_name

        grid_10: Gtk.Grid = Gtk.Grid.new()
        grid_10.attach(label_10_vae_name,        left=0, top=0, width=1, height=1)  # noqa
        grid_10.attach(comboboxtext_10_vae_name, left=1, top=0, width=2, height=1)  # noqa
        grid_10.set_column_homogeneous(False)
        grid_10.set_row_homogeneous(False)
        frame_vaeloader_010load_vae.add(widget=grid_10)  # noqa

        # New Frame
        frame_dualcliploader_011dualcliploader: Gtk.Frame = Gtk.Frame.new(label="DualCLIPLoader")  # noqa
        frame_dualcliploader_011dualcliploader.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_11_clip_name1: Gtk.Label = Gtk.Label.new("Clip_Name1")
        entry_11_clip_name1: Gtk.Entry = Gtk.Entry.new()
        entry_11_clip_name1.set_hexpand(True)
        label_11_clip_name2: Gtk.Label = Gtk.Label.new("Clip_Name2")
        entry_11_clip_name2: Gtk.Entry = Gtk.Entry.new()
        entry_11_clip_name2.set_hexpand(True)
        label_11_type: Gtk.Label = Gtk.Label.new("Type")
        entry_11_type: Gtk.Entry = Gtk.Entry.new()
        entry_11_type.set_hexpand(True)
        grid_11: Gtk.Grid = Gtk.Grid.new()
        grid_11.attach(label_11_clip_name1, left=0, top=0, width=1, height=1)  # noqa
        grid_11.attach(entry_11_clip_name1, left=1, top=0, width=2, height=1)  # noqa
        grid_11.attach(label_11_clip_name2, left=0, top=1, width=1, height=1)  # noqa
        grid_11.attach(entry_11_clip_name2, left=1, top=1, width=2, height=1)  # noqa
        grid_11.attach(label_11_type,       left=0, top=2, width=1, height=1)  # noqa
        grid_11.attach(entry_11_type,       left=1, top=2, width=2, height=1)  # noqa
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
        widget_getters[comboboxtext_12_unet_name.get_name()] = comboboxtext_12_unet_name.get_active_text
        widget_setters[comboboxtext_12_unet_name.get_name()] = setter_12_unet_name

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
        widget_getters[comboboxtext_12_weight_dtype.get_name()] = comboboxtext_12_weight_dtype.get_active_text
        widget_setters[comboboxtext_12_weight_dtype.get_name()] = setter_12_weight_dtype

        grid_12: Gtk.Grid = Gtk.Grid.new()
        grid_12.attach(label_12_unet_name,           left=0, top=0, width=1, height=1)  # noqa
        grid_12.attach(comboboxtext_12_unet_name,    left=1, top=0, width=2, height=1)  # noqa
        grid_12.attach(label_12_weight_dtype,        left=0, top=1, width=1, height=1)  # noqa
        grid_12.attach(comboboxtext_12_weight_dtype, left=1, top=1, width=2, height=1)  # noqa
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
        widget_getters[entry_49_width.get_name()] = getter_49_width
        widget_setters[entry_49_width.get_name()] = setter_49_width

        label_49_height: Gtk.Label = Gtk.Label.new("Height")
        label_49_height.set_margin_start(8)
        label_49_height.set_alignment(0.95, 0)
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
        widget_getters[entry_49_height.get_name()] = getter_49_height
        widget_setters[entry_49_height.get_name()] = setter_49_height

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
        widget_getters[entry_49_batch_size.get_name()] = getter_49_batch_size
        widget_setters[entry_49_batch_size.get_name()] = setter_49_batch_size

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
        frame_impactksampleradvancedbasicpipe_097ksampler_advancedpipe: Gtk.Frame = Gtk.Frame.new(label="KSampler (Advanced/pipe)")  # noqa
        frame_impactksampleradvancedbasicpipe_097ksampler_advancedpipe.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        checkbutton_97_add_noise: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Add Noise")  # noqa
        checkbutton_97_add_noise.set_active(False)
        checkbutton_97_add_noise.set_name("checkbutton_97_add_noise")
        checkbutton_97_add_noise.set_hexpand(False)

        def toggled_handler_97_add_noise(source, **args):  # noqa
            pass
        checkbutton_97_add_noise.connect(SIG_TOGGLED, toggled_handler_97_add_noise)

        def getter_97_add_noise():
            return "enable" if checkbutton_97_add_noise.get_active() else "disable"
        widget_getters[checkbutton_97_add_noise.get_name()] = getter_97_add_noise

        label_97_noise_seed: Gtk.Label = Gtk.Label.new("Noise_Seed")
        label_97_noise_seed.set_margin_start(8)
        label_97_noise_seed.set_alignment(0.95, 0)
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
        widget_getters[entry_97_noise_seed.get_name()] = getter_97_noise_seed
        widget_setters[entry_97_noise_seed.get_name()] = setter_97_noise_seed

        label_97_steps: Gtk.Label = Gtk.Label.new("Steps")
        label_97_steps.set_margin_start(8)
        label_97_steps.set_alignment(0.95, 0)
        entry_97_steps: Gtk.Entry = Gtk.Entry.new()
        entry_97_steps.set_text(str(20))
        entry_97_steps.set_name("entry_97_steps")
        entry_97_steps.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_97_steps,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_97_steps(source, **args):  # noqa
            pass
        entry_97_steps.connect(SIG_CHANGED, change_handler_97_steps)

        def getter_97_steps() -> int:
            return int(entry_97_steps.get_text())

        def setter_97_steps(a_val: int):
            entry_97_steps.set_text(str(a_val))
        widget_getters[entry_97_steps.get_name()] = getter_97_steps
        widget_setters[entry_97_steps.get_name()] = setter_97_steps

        label_97_cfg: Gtk.Label = Gtk.Label.new("Cfg")
        label_97_cfg.set_margin_start(8)
        entry_97_cfg: Gtk.Entry = Gtk.Entry.new()
        entry_97_cfg.set_text(str(3.5))
        entry_97_cfg.set_name("entry_97_cfg")
        entry_97_cfg.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_97_cfg,
                           minimum=0, maximum=None,  # noqa
                           int_only=False,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_97_cfg(source, **args):  # noqa
            pass
        entry_97_cfg.connect(SIG_CHANGED, change_handler_97_cfg)

        def getter_97_cfg() -> float:
            return float(entry_97_cfg.get_text())

        def setter_97_cfg(a_val: float):
            entry_97_cfg.set_text(str(a_val))
        widget_getters[entry_97_cfg.get_name()] = getter_97_cfg
        widget_setters[entry_97_cfg.get_name()] = setter_97_cfg

        label_97_sampler_name: Gtk.Label = Gtk.Label.new("Sampler_Name")
        entry_97_sampler_name: Gtk.Entry = Gtk.Entry.new()
        entry_97_sampler_name.set_hexpand(True)
        label_97_scheduler: Gtk.Label = Gtk.Label.new("Scheduler")
        entry_97_scheduler: Gtk.Entry = Gtk.Entry.new()
        entry_97_scheduler.set_hexpand(True)
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
        widget_getters[entry_97_start_at_step.get_name()] = getter_97_start_at_step
        widget_setters[entry_97_start_at_step.get_name()] = setter_97_start_at_step

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
        widget_getters[entry_97_end_at_step.get_name()] = getter_97_end_at_step
        widget_setters[entry_97_end_at_step.get_name()] = setter_97_end_at_step

        checkbutton_97_return_with_leftover_noise: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Return_With_Leftover_Noise")  # noqa

        grid_97: Gtk.Grid = Gtk.Grid.new()
        grid_97.attach(checkbutton_97_add_noise,                  left=0, top=0, width=3, height=1)  # noqa
        grid_97.attach(label_97_noise_seed,                       left=3, top=0, width=1, height=1)  # noqa
        grid_97.attach(entry_97_noise_seed,                       left=4, top=0, width=3, height=1)  # noqa
        grid_97.attach(label_97_steps,                            left=7, top=0, width=1, height=1)  # noqa
        grid_97.attach(entry_97_steps,                            left=8, top=0, width=3, height=1)  # noqa
        grid_97.attach(label_97_cfg,                              left=0, top=1, width=1, height=1)  # noqa
        grid_97.attach(entry_97_cfg,                              left=1, top=1, width=10, height=1)  # noqa
        grid_97.attach(label_97_sampler_name,                     left=0, top=2, width=1, height=1)  # noqa
        grid_97.attach(entry_97_sampler_name,                     left=1, top=2, width=10, height=1)  # noqa
        grid_97.attach(label_97_scheduler,                        left=0, top=3, width=1, height=1)  # noqa
        grid_97.attach(entry_97_scheduler,                        left=1, top=3, width=10, height=1)  # noqa
        grid_97.attach(label_97_start_at_step,                    left=0, top=4, width=1, height=1)  # noqa
        grid_97.attach(entry_97_start_at_step,                    left=1, top=4, width=3, height=1)  # noqa
        grid_97.attach(label_97_end_at_step,                      left=4, top=4, width=1, height=1)  # noqa
        grid_97.attach(entry_97_end_at_step,                      left=5, top=4, width=6, height=1)  # noqa
        grid_97.attach(checkbutton_97_return_with_leftover_noise, left=0, top=5, width=11, height=1)  # noqa
        grid_97.set_column_homogeneous(False)
        grid_97.set_row_homogeneous(False)
        frame_impactksampleradvancedbasicpipe_097ksampler_advancedpipe.add(widget=grid_97)  # noqa

        # New Frame
        frame_impactksampleradvancedbasicpipe_098ksampler_advancedpipe: Gtk.Frame = Gtk.Frame.new(label="KSampler (Advanced/pipe)")  # noqa
        frame_impactksampleradvancedbasicpipe_098ksampler_advancedpipe.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        checkbutton_98_add_noise: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Add Noise")  # noqa
        checkbutton_98_add_noise.set_active(True)
        checkbutton_98_add_noise.set_name("checkbutton_98_add_noise")
        checkbutton_98_add_noise.set_hexpand(False)

        def toggled_handler_98_add_noise(source, **args):  # noqa
            pass
        checkbutton_98_add_noise.connect(SIG_TOGGLED, toggled_handler_98_add_noise)

        def getter_98_add_noise():
            return "enable" if checkbutton_98_add_noise.get_active() else "disable"
        widget_getters[checkbutton_98_add_noise.get_name()] = getter_98_add_noise

        label_98_noise_seed: Gtk.Label = Gtk.Label.new("Noise_Seed")
        label_98_noise_seed.set_margin_start(8)
        label_98_noise_seed.set_alignment(0.95, 0)
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
        widget_getters[entry_98_noise_seed.get_name()] = getter_98_noise_seed
        widget_setters[entry_98_noise_seed.get_name()] = setter_98_noise_seed

        label_98_steps: Gtk.Label = Gtk.Label.new("Steps")
        label_98_steps.set_margin_start(8)
        label_98_steps.set_alignment(0.95, 0)
        entry_98_steps: Gtk.Entry = Gtk.Entry.new()
        entry_98_steps.set_text(str(20))
        entry_98_steps.set_name("entry_98_steps")
        entry_98_steps.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_98_steps,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_98_steps(source, **args):  # noqa
            pass
        entry_98_steps.connect(SIG_CHANGED, change_handler_98_steps)

        def getter_98_steps() -> int:
            return int(entry_98_steps.get_text())

        def setter_98_steps(a_val: int):
            entry_98_steps.set_text(str(a_val))
        widget_getters[entry_98_steps.get_name()] = getter_98_steps
        widget_setters[entry_98_steps.get_name()] = setter_98_steps

        label_98_cfg: Gtk.Label = Gtk.Label.new("Cfg")
        label_98_cfg.set_margin_start(8)
        entry_98_cfg: Gtk.Entry = Gtk.Entry.new()
        entry_98_cfg.set_text(str(3.5))
        entry_98_cfg.set_name("entry_98_cfg")
        entry_98_cfg.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_98_cfg,
                           minimum=0, maximum=None,  # noqa
                           int_only=False,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_98_cfg(source, **args):  # noqa
            pass
        entry_98_cfg.connect(SIG_CHANGED, change_handler_98_cfg)

        def getter_98_cfg() -> float:
            return float(entry_98_cfg.get_text())

        def setter_98_cfg(a_val: float):
            entry_98_cfg.set_text(str(a_val))
        widget_getters[entry_98_cfg.get_name()] = getter_98_cfg
        widget_setters[entry_98_cfg.get_name()] = setter_98_cfg

        label_98_sampler_name: Gtk.Label = Gtk.Label.new("Sampler_Name")
        entry_98_sampler_name: Gtk.Entry = Gtk.Entry.new()
        entry_98_sampler_name.set_hexpand(True)
        label_98_scheduler: Gtk.Label = Gtk.Label.new("Scheduler")
        entry_98_scheduler: Gtk.Entry = Gtk.Entry.new()
        entry_98_scheduler.set_hexpand(True)
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
        widget_getters[entry_98_start_at_step.get_name()] = getter_98_start_at_step
        widget_setters[entry_98_start_at_step.get_name()] = setter_98_start_at_step

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
        widget_getters[entry_98_end_at_step.get_name()] = getter_98_end_at_step
        widget_setters[entry_98_end_at_step.get_name()] = setter_98_end_at_step

        checkbutton_98_return_with_leftover_noise: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Return_With_Leftover_Noise")  # noqa

        grid_98: Gtk.Grid = Gtk.Grid.new()
        grid_98.attach(checkbutton_98_add_noise,                  left=0, top=0, width=3, height=1)  # noqa
        grid_98.attach(label_98_noise_seed,                       left=3, top=0, width=1, height=1)  # noqa
        grid_98.attach(entry_98_noise_seed,                       left=4, top=0, width=3, height=1)  # noqa
        grid_98.attach(label_98_steps,                            left=7, top=0, width=1, height=1)  # noqa
        grid_98.attach(entry_98_steps,                            left=8, top=0, width=3, height=1)  # noqa
        grid_98.attach(label_98_cfg,                              left=0, top=1, width=1, height=1)  # noqa
        grid_98.attach(entry_98_cfg,                              left=1, top=1, width=10, height=1)  # noqa
        grid_98.attach(label_98_sampler_name,                     left=0, top=2, width=1, height=1)  # noqa
        grid_98.attach(entry_98_sampler_name,                     left=1, top=2, width=10, height=1)  # noqa
        grid_98.attach(label_98_scheduler,                        left=0, top=3, width=1, height=1)  # noqa
        grid_98.attach(entry_98_scheduler,                        left=1, top=3, width=10, height=1)  # noqa
        grid_98.attach(label_98_start_at_step,                    left=0, top=4, width=1, height=1)  # noqa
        grid_98.attach(entry_98_start_at_step,                    left=1, top=4, width=3, height=1)  # noqa
        grid_98.attach(label_98_end_at_step,                      left=4, top=4, width=1, height=1)  # noqa
        grid_98.attach(entry_98_end_at_step,                      left=5, top=4, width=6, height=1)  # noqa
        grid_98.attach(checkbutton_98_return_with_leftover_noise, left=0, top=5, width=11, height=1)  # noqa
        grid_98.set_column_homogeneous(False)
        grid_98.set_row_homogeneous(False)
        frame_impactksampleradvancedbasicpipe_098ksampler_advancedpipe.add(widget=grid_98)  # noqa

        # New Frame
        frame_dynamicthresholdingfull_100dynamicthresholdingfull: Gtk.Frame = Gtk.Frame.new(label="DynamicThresholdingFull")  # noqa
        frame_dynamicthresholdingfull_100dynamicthresholdingfull.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_100_mimic_scale: Gtk.Label = Gtk.Label.new("Mimic_Scale")
        label_100_mimic_scale.set_margin_start(8)
        label_100_mimic_scale.set_alignment(0.95, 0)
        entry_100_mimic_scale: Gtk.Entry = Gtk.Entry.new()
        label_100_threshold_percentile: Gtk.Label = Gtk.Label.new("Threshold_Percentile")
        label_100_threshold_percentile.set_margin_start(8)
        label_100_threshold_percentile.set_alignment(0.95, 0)
        entry_100_threshold_percentile: Gtk.Entry = Gtk.Entry.new()
        label_100_mimic_mode: Gtk.Label = Gtk.Label.new("Mimic_Mode")
        entry_100_mimic_mode: Gtk.Entry = Gtk.Entry.new()
        entry_100_mimic_mode.set_hexpand(True)
        label_100_mimic_scale_min: Gtk.Label = Gtk.Label.new("Mimic_Scale_Min")
        label_100_mimic_scale_min.set_margin_start(8)
        label_100_mimic_scale_min.set_alignment(0.95, 0)
        entry_100_mimic_scale_min: Gtk.Entry = Gtk.Entry.new()
        label_100_cfg_mode: Gtk.Label = Gtk.Label.new("Cfg_Mode")
        entry_100_cfg_mode: Gtk.Entry = Gtk.Entry.new()
        entry_100_cfg_mode.set_hexpand(True)
        label_100_cfg_scale_min: Gtk.Label = Gtk.Label.new("Cfg_Scale_Min")
        label_100_cfg_scale_min.set_margin_start(8)
        label_100_cfg_scale_min.set_alignment(0.95, 0)
        entry_100_cfg_scale_min: Gtk.Entry = Gtk.Entry.new()
        label_100_sched_val: Gtk.Label = Gtk.Label.new("Sched_Val")
        label_100_sched_val.set_margin_start(8)
        label_100_sched_val.set_alignment(0.95, 0)
        entry_100_sched_val: Gtk.Entry = Gtk.Entry.new()
        checkbutton_100_separate_feature_channels: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Separate_Feature_Channels")  # noqa

        label_100_scaling_startpoint: Gtk.Label = Gtk.Label.new("Scaling_Startpoint")
        entry_100_scaling_startpoint: Gtk.Entry = Gtk.Entry.new()
        entry_100_scaling_startpoint.set_hexpand(True)
        label_100_variability_measure: Gtk.Label = Gtk.Label.new("Variability_Measure")
        entry_100_variability_measure: Gtk.Entry = Gtk.Entry.new()
        entry_100_variability_measure.set_hexpand(True)
        label_100_interpolate_phi: Gtk.Label = Gtk.Label.new("Interpolate_Phi")
        label_100_interpolate_phi.set_margin_start(8)
        label_100_interpolate_phi.set_alignment(0.95, 0)
        entry_100_interpolate_phi: Gtk.Entry = Gtk.Entry.new()
        grid_100: Gtk.Grid = Gtk.Grid.new()
        grid_100.attach(label_100_mimic_scale,                     left=0, top=0, width=1, height=1)  # noqa
        grid_100.attach(entry_100_mimic_scale,                     left=1, top=0, width=2, height=1)  # noqa
        grid_100.attach(label_100_threshold_percentile,            left=0, top=1, width=1, height=1)  # noqa
        grid_100.attach(entry_100_threshold_percentile,            left=1, top=1, width=2, height=1)  # noqa
        grid_100.attach(label_100_mimic_mode,                      left=0, top=2, width=1, height=1)  # noqa
        grid_100.attach(entry_100_mimic_mode,                      left=1, top=2, width=2, height=1)  # noqa
        grid_100.attach(label_100_mimic_scale_min,                 left=0, top=3, width=1, height=1)  # noqa
        grid_100.attach(entry_100_mimic_scale_min,                 left=1, top=3, width=2, height=1)  # noqa
        grid_100.attach(label_100_cfg_mode,                        left=0, top=4, width=1, height=1)  # noqa
        grid_100.attach(entry_100_cfg_mode,                        left=1, top=4, width=2, height=1)  # noqa
        grid_100.attach(label_100_cfg_scale_min,                   left=0, top=5, width=1, height=1)  # noqa
        grid_100.attach(entry_100_cfg_scale_min,                   left=1, top=5, width=2, height=1)  # noqa
        grid_100.attach(label_100_sched_val,                       left=0, top=6, width=1, height=1)  # noqa
        grid_100.attach(entry_100_sched_val,                       left=1, top=6, width=2, height=1)  # noqa
        grid_100.attach(checkbutton_100_separate_feature_channels, left=0, top=7, width=3, height=1)  # noqa
        grid_100.attach(label_100_scaling_startpoint,              left=0, top=8, width=1, height=1)  # noqa
        grid_100.attach(entry_100_scaling_startpoint,              left=1, top=8, width=2, height=1)  # noqa
        grid_100.attach(label_100_variability_measure,             left=0, top=9, width=1, height=1)  # noqa
        grid_100.attach(entry_100_variability_measure,             left=1, top=9, width=2, height=1)  # noqa
        grid_100.attach(label_100_interpolate_phi,                 left=0, top=10, width=1, height=1)  # noqa
        grid_100.attach(entry_100_interpolate_phi,                 left=1, top=10, width=2, height=1)  # noqa
        grid_100.set_column_homogeneous(False)
        grid_100.set_row_homogeneous(False)
        frame_dynamicthresholdingfull_100dynamicthresholdingfull.add(widget=grid_100)  # noqa

        # New Frame
        frame_cliptextencode_101negative_prompt: Gtk.Frame = Gtk.Frame.new(label="Negative Prompt")  # noqa
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
        grid_101.attach(scrolled_window_101_text, left=1, top=0, width=2, height=1)  # noqa
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
        frame_vaedecode_110vae_decode: Gtk.Frame = Gtk.Frame.new(label="VAE Decode")  # noqa
        frame_vaedecode_110vae_decode.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        grid_110: Gtk.Grid = Gtk.Grid.new()
        grid_110.set_column_homogeneous(False)
        grid_110.set_row_homogeneous(False)
        frame_vaedecode_110vae_decode.add(widget=grid_110)  # noqa

        # New Frame
        frame_saveimage_111save_image: Gtk.Frame = Gtk.Frame.new(label="Save Image")  # noqa
        frame_saveimage_111save_image.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_111_filename_prefix: Gtk.Label = Gtk.Label.new("Filename_Prefix")
        entry_111_filename_prefix: Gtk.Entry = Gtk.Entry.new()
        entry_111_filename_prefix.set_text("generated")
        entry_111_filename_prefix.set_name("entry_111_filename_prefix")
        entry_111_filename_prefix.set_hexpand(True)
        widget_getters[entry_111_filename_prefix.get_name()] = entry_111_filename_prefix.get_text
        widget_setters[entry_111_filename_prefix.get_name()] = entry_111_filename_prefix.set_text

        grid_111: Gtk.Grid = Gtk.Grid.new()
        grid_111.attach(label_111_filename_prefix, left=0, top=0, width=1, height=1)  # noqa
        grid_111.attach(entry_111_filename_prefix, left=1, top=0, width=2, height=1)  # noqa
        grid_111.set_column_homogeneous(False)
        grid_111.set_row_homogeneous(False)
        frame_saveimage_111save_image.add(widget=grid_111)  # noqa
        content_area: Gtk.Box = dialog.get_content_area()
        content_area.pack_start(child=frame_cliptextencode_006positive_prompt, expand=True, fill=True, padding=0)  # noqa
        content_area.pack_start(child=frame_vaeloader_010load_vae, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_dualcliploader_011dualcliploader, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_unetloader_012load_diffusion_model, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_tobasicpipe_047tobasicpipe, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_emptylatentimage_049empty_latent_image, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_impactksampleradvancedbasicpipe_097ksampler_advancedpipe, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_impactksampleradvancedbasicpipe_098ksampler_advancedpipe, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_dynamicthresholdingfull_100dynamicthresholdingfull, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_cliptextencode_101negative_prompt, expand=True, fill=True, padding=0)  # noqa
        content_area.pack_start(child=frame_editbasicpipe_103edit_basicpipe, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_frombasicpipe_v2_104frombasicpipe_v2, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_vaedecode_110vae_decode, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_saveimage_111save_image, expand=False, fill=False, padding=0)  # noqa

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
