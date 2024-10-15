
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


class ComfyuiDefaultDialogs(WorkflowDialogFactory):

    WORKFLOW_FILE = "comfyui_default_workflow_api.json"

    def __init__(self, accessor: NodesAccessor):
        super().__init__(
            accessor=accessor,
            api_workflow=ComfyuiDefaultDialogs.WORKFLOW_FILE,
            dialog_config_chassis_name="ComfyuiDefaultDialogs_dialog_config",
            wf_data_chassis_name="ComfyuiDefaultDialogs_wf_data",
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
                                                     chassis_name="comfyui_default_dialog",
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
        frame_ksampler_003ksampler: Gtk.Frame = Gtk.Frame.new(label="KSampler")  # noqa
        frame_ksampler_003ksampler.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_3_seed: Gtk.Label = Gtk.Label.new("Seed")
        label_3_seed.set_margin_start(8)
        label_3_seed.set_alignment(0.95, 0)
        entry_3_seed: Gtk.Entry = Gtk.Entry.new()
        entry_3_seed.set_text(str(156680208700286))
        entry_3_seed.set_name("entry_3_seed")
        entry_3_seed.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_3_seed,
                           minimum=-1, maximum=18446744073709519872,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_3_seed(source, **args):  # noqa
            pass
        entry_3_seed.connect(SIG_CHANGED, change_handler_3_seed)

        def getter_3_seed() -> int:
            return int(entry_3_seed.get_text())

        def setter_3_seed(a_val: int):
            entry_3_seed.set_text(str(a_val))
        widget_getters[entry_3_seed.get_name()] = getter_3_seed
        widget_setters[entry_3_seed.get_name()] = setter_3_seed

        label_3_steps: Gtk.Label = Gtk.Label.new("Steps")
        label_3_steps.set_margin_start(8)
        label_3_steps.set_alignment(0.95, 0)
        entry_3_steps: Gtk.Entry = Gtk.Entry.new()
        entry_3_steps.set_text(str(20))
        entry_3_steps.set_name("entry_3_steps")
        entry_3_steps.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_3_steps,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_3_steps(source, **args):  # noqa
            pass
        entry_3_steps.connect(SIG_CHANGED, change_handler_3_steps)

        def getter_3_steps() -> int:
            return int(entry_3_steps.get_text())

        def setter_3_steps(a_val: int):
            entry_3_steps.set_text(str(a_val))
        widget_getters[entry_3_steps.get_name()] = getter_3_steps
        widget_setters[entry_3_steps.get_name()] = setter_3_steps

        label_3_cfg: Gtk.Label = Gtk.Label.new("Cfg")
        label_3_cfg.set_margin_start(8)
        label_3_cfg.set_alignment(0.95, 0)
        adjustment_3_cfg: Gtk.Adjustment = Gtk.Adjustment(value=8.00000,
                                                          lower=1.00000,
                                                          upper=25.00000,
                                                          step_increment=0.100,
                                                          page_increment=2.000,
                                                          page_size=0)
        scale_3_cfg: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_3_cfg)  # noqa
        scale_3_cfg.set_name("scale_3_cfg")
        scale_3_cfg.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_3_cfg.set_hexpand(True)

        def change_handler_3_cfg(source, **args):  # noqa
            pass
        scale_3_cfg.connect(SIG_VALUE_CHANGED, change_handler_3_cfg)
        widget_getters[scale_3_cfg.get_name()] = scale_3_cfg.get_value
        widget_setters[scale_3_cfg.get_name()] = scale_3_cfg.set_value

        label_3_sampler_name: Gtk.Label = Gtk.Label.new("Sampler_Name")
        comboboxtext_3_sampler_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_3_sampler_name: list[str] = ["euler", "euler_ancestral", "heun", "heunpp2", "dpm_2", "dpm_2_ancestral", "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_sde", "dpmpp_sde_gpu", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu", "ddpm", "lcm", "ddim", "uni_pc", "uni_pc_bh2"]  # noqa
        for combo_item_path in combo_values_3_sampler_name:
            comboboxtext_3_sampler_name.append_text(combo_item_path)
        comboboxtext_3_sampler_name.set_name("comboboxtext_3_sampler_name")
        comboboxtext_3_sampler_name.set_hexpand(True)
        comboboxtext_3_sampler_name.set_active(0)

        def change_handler_3_sampler_name(source, **args):  # noqa
            pass
        comboboxtext_3_sampler_name.connect(SIG_CHANGED, change_handler_3_sampler_name)

        def setter_3_sampler_name(a_val: str):
            nonlocal combo_values_3_sampler_name
            selected_index = combo_values_3_sampler_name.index(a_val)
            comboboxtext_3_sampler_name.set_active(selected_index)
        widget_getters[comboboxtext_3_sampler_name.get_name()] = comboboxtext_3_sampler_name.get_active_text
        widget_setters[comboboxtext_3_sampler_name.get_name()] = setter_3_sampler_name

        label_3_scheduler: Gtk.Label = Gtk.Label.new("Scheduler")
        comboboxtext_3_scheduler: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_3_scheduler: list[str] = ["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"]  # noqa
        for combo_item_path in combo_values_3_scheduler:
            comboboxtext_3_scheduler.append_text(combo_item_path)
        comboboxtext_3_scheduler.set_name("comboboxtext_3_scheduler")
        comboboxtext_3_scheduler.set_hexpand(True)
        comboboxtext_3_scheduler.set_active(0)

        def change_handler_3_scheduler(source, **args):  # noqa
            pass
        comboboxtext_3_scheduler.connect(SIG_CHANGED, change_handler_3_scheduler)

        def setter_3_scheduler(a_val: str):
            nonlocal combo_values_3_scheduler
            selected_index = combo_values_3_scheduler.index(a_val)
            comboboxtext_3_scheduler.set_active(selected_index)
        widget_getters[comboboxtext_3_scheduler.get_name()] = comboboxtext_3_scheduler.get_active_text
        widget_setters[comboboxtext_3_scheduler.get_name()] = setter_3_scheduler

        label_3_denoise: Gtk.Label = Gtk.Label.new("Denoise")
        label_3_denoise.set_margin_start(8)
        label_3_denoise.set_alignment(0.95, 0)
        adjustment_3_denoise: Gtk.Adjustment = Gtk.Adjustment(value=1.00000,
                                                              lower=0.00000,
                                                              upper=1.00000,
                                                              step_increment=0.001,
                                                              page_increment=0.010,
                                                              page_size=0)
        scale_3_denoise: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_3_denoise)  # noqa
        scale_3_denoise.set_name("scale_3_denoise")
        scale_3_denoise.set_digits(3)
        scale_3_denoise.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_3_denoise.set_hexpand(True)

        def change_handler_3_denoise(source, **args):  # noqa
            pass
        scale_3_denoise.connect(SIG_VALUE_CHANGED, change_handler_3_denoise)
        widget_getters[scale_3_denoise.get_name()] = scale_3_denoise.get_value
        widget_setters[scale_3_denoise.get_name()] = scale_3_denoise.set_value

        grid_3: Gtk.Grid = Gtk.Grid.new()
        grid_3.attach(label_3_seed,                left=0, top=0, width=1, height=1)  # noqa
        grid_3.attach(entry_3_seed,                left=1, top=0, width=3, height=1)  # noqa
        grid_3.attach(label_3_steps,               left=4, top=0, width=1, height=1)  # noqa
        grid_3.attach(entry_3_steps,               left=5, top=0, width=3, height=1)  # noqa
        grid_3.attach(label_3_cfg,                 left=0, top=1, width=1, height=1)  # noqa
        grid_3.attach(scale_3_cfg,                 left=1, top=1, width=7, height=1)  # noqa
        grid_3.attach(label_3_sampler_name,        left=0, top=2, width=1, height=1)  # noqa
        grid_3.attach(comboboxtext_3_sampler_name, left=1, top=2, width=7, height=1)  # noqa
        grid_3.attach(label_3_scheduler,           left=0, top=3, width=1, height=1)  # noqa
        grid_3.attach(comboboxtext_3_scheduler,    left=1, top=3, width=7, height=1)  # noqa
        grid_3.attach(label_3_denoise,             left=0, top=4, width=1, height=1)  # noqa
        grid_3.attach(scale_3_denoise,             left=1, top=4, width=7, height=1)  # noqa
        grid_3.set_column_homogeneous(False)
        grid_3.set_row_homogeneous(False)
        frame_ksampler_003ksampler.add(widget=grid_3)  # noqa

        # New Frame
        frame_checkpointloadersimple_004load_checkpoint: Gtk.Frame = Gtk.Frame.new(label="Load Checkpoint")  # noqa
        frame_checkpointloadersimple_004load_checkpoint.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_4_ckpt_name: Gtk.Label = Gtk.Label.new("Ckpt_Name")
        comboboxtext_4_ckpt_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_4_ckpt_name: list[str] = get_models_filenames(
            model_type=ModelType.CHECKPOINTS,
            cu_origin=self.comfy_svr_origin)
        if combo_values_4_ckpt_name is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_4_ckpt_name:
            raise ValueError(fr"No models retrieved from ComfyUI")  # noqa
        for combo_item_path in combo_values_4_ckpt_name:
            comboboxtext_4_ckpt_name.append_text(combo_item_path)
        comboboxtext_4_ckpt_name.set_name("comboboxtext_4_ckpt_name")
        comboboxtext_4_ckpt_name.set_hexpand(True)
        comboboxtext_4_ckpt_name.set_active(14)

        def change_handler_4_ckpt_name(source, **args):  # noqa
            pass
        comboboxtext_4_ckpt_name.connect(SIG_CHANGED, change_handler_4_ckpt_name)

        def setter_4_ckpt_name(a_val: str):
            nonlocal combo_values_4_ckpt_name
            selected_index = combo_values_4_ckpt_name.index(a_val)
            comboboxtext_4_ckpt_name.set_active(selected_index)
        widget_getters[comboboxtext_4_ckpt_name.get_name()] = comboboxtext_4_ckpt_name.get_active_text
        widget_setters[comboboxtext_4_ckpt_name.get_name()] = setter_4_ckpt_name

        grid_4: Gtk.Grid = Gtk.Grid.new()
        grid_4.attach(label_4_ckpt_name,        left=0, top=0, width=1, height=1)  # noqa
        grid_4.attach(comboboxtext_4_ckpt_name, left=1, top=0, width=2, height=1)  # noqa
        grid_4.set_column_homogeneous(False)
        grid_4.set_row_homogeneous(False)
        frame_checkpointloadersimple_004load_checkpoint.add(widget=grid_4)  # noqa

        # New Frame
        frame_emptylatentimage_005empty_latent_image: Gtk.Frame = Gtk.Frame.new(label="Empty Latent Image")  # noqa
        frame_emptylatentimage_005empty_latent_image.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_5_width: Gtk.Label = Gtk.Label.new("Width")
        label_5_width.set_margin_start(8)
        label_5_width.set_alignment(0.95, 0)
        entry_5_width: Gtk.Entry = Gtk.Entry.new()
        entry_5_width.set_text(str(512))
        entry_5_width.set_name("entry_5_width")
        entry_5_width.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_5_width,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_5_width(source, **args):  # noqa
            pass
        entry_5_width.connect(SIG_CHANGED, change_handler_5_width)

        def getter_5_width() -> int:
            return int(entry_5_width.get_text())

        def setter_5_width(a_val: int):
            entry_5_width.set_text(str(a_val))
        widget_getters[entry_5_width.get_name()] = getter_5_width
        widget_setters[entry_5_width.get_name()] = setter_5_width

        label_5_height: Gtk.Label = Gtk.Label.new("Height")
        label_5_height.set_margin_start(8)
        label_5_height.set_alignment(0.95, 0)
        entry_5_height: Gtk.Entry = Gtk.Entry.new()
        entry_5_height.set_text(str(512))
        entry_5_height.set_name("entry_5_height")
        entry_5_height.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_5_height,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_5_height(source, **args):  # noqa
            pass
        entry_5_height.connect(SIG_CHANGED, change_handler_5_height)

        def getter_5_height() -> int:
            return int(entry_5_height.get_text())

        def setter_5_height(a_val: int):
            entry_5_height.set_text(str(a_val))
        widget_getters[entry_5_height.get_name()] = getter_5_height
        widget_setters[entry_5_height.get_name()] = setter_5_height

        label_5_batch_size: Gtk.Label = Gtk.Label.new("Batch_Size")
        label_5_batch_size.set_margin_start(8)
        label_5_batch_size.set_alignment(0.95, 0)
        entry_5_batch_size: Gtk.Entry = Gtk.Entry.new()
        entry_5_batch_size.set_text(str(1))
        entry_5_batch_size.set_name("entry_5_batch_size")
        entry_5_batch_size.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_5_batch_size,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_5_batch_size(source, **args):  # noqa
            pass
        entry_5_batch_size.connect(SIG_CHANGED, change_handler_5_batch_size)

        def getter_5_batch_size() -> int:
            return int(entry_5_batch_size.get_text())

        def setter_5_batch_size(a_val: int):
            entry_5_batch_size.set_text(str(a_val))
        widget_getters[entry_5_batch_size.get_name()] = getter_5_batch_size
        widget_setters[entry_5_batch_size.get_name()] = setter_5_batch_size

        grid_5: Gtk.Grid = Gtk.Grid.new()
        grid_5.attach(label_5_width,      left=0, top=0, width=1, height=1)  # noqa
        grid_5.attach(entry_5_width,      left=1, top=0, width=3, height=1)  # noqa
        grid_5.attach(label_5_height,     left=4, top=0, width=1, height=1)  # noqa
        grid_5.attach(entry_5_height,     left=5, top=0, width=3, height=1)  # noqa
        grid_5.attach(label_5_batch_size, left=8, top=0, width=1, height=1)  # noqa
        grid_5.attach(entry_5_batch_size, left=9, top=0, width=3, height=1)  # noqa
        grid_5.set_column_homogeneous(False)
        grid_5.set_row_homogeneous(False)
        frame_emptylatentimage_005empty_latent_image.add(widget=grid_5)  # noqa

        # New Frame
        frame_cliptextencode_006positive_prompt: Gtk.Frame = Gtk.Frame.new(label="Positive Prompt")  # noqa
        frame_cliptextencode_006positive_prompt.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_6_text: Gtk.Label = Gtk.Label.new("Text")
        textview_6_text: Gtk.TextView = Gtk.TextView.new()
        textview_6_text.get_buffer().set_text("beautiful scenery nature glass bottle landscape, , purple galaxy bottle,")  # noqa
        textview_6_text.set_name("textview_6_text")
        textview_6_text.set_hexpand(True)
        textview_6_text.set_vexpand(True)
        textview_6_text.set_valign(Gtk.Align.FILL)

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
        grid_6.attach(label_6_text,    left=0, top=0, width=1, height=1)  # noqa
        grid_6.attach(textview_6_text, left=1, top=0, width=2, height=1)  # noqa
        grid_6.set_column_homogeneous(False)
        grid_6.set_row_homogeneous(False)
        frame_cliptextencode_006positive_prompt.add(widget=grid_6)  # noqa

        # New Frame
        frame_cliptextencode_007negative_prompt: Gtk.Frame = Gtk.Frame.new(label="Negative Prompt")  # noqa
        frame_cliptextencode_007negative_prompt.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_7_text: Gtk.Label = Gtk.Label.new("Text")
        textview_7_text: Gtk.TextView = Gtk.TextView.new()
        textview_7_text.get_buffer().set_text("text, watermark")  # noqa
        textview_7_text.set_name("textview_7_text")
        textview_7_text.set_hexpand(True)
        textview_7_text.set_vexpand(True)
        textview_7_text.set_valign(Gtk.Align.FILL)

        def preedit_handler_7_text(source, **args):  # noqa
            pass
        textview_7_text.connect(SIG_PREEDIT_CHANGED, preedit_handler_7_text)

        def getter_7_text():
            buffer: Gtk.TextBuffer = textview_7_text.get_buffer()
            start: Gtk.TextIter = buffer.get_start_iter()
            end: Gtk.TextIter = buffer.get_end_iter()
            return buffer.get_text(start, end, False)

        def setter_7_text(a_val: str):
            textview_7_text.get_buffer().set_text(str(a_val))

        widget_getters[textview_7_text.get_name()] = getter_7_text
        widget_setters[textview_7_text.get_name()] = setter_7_text

        grid_7: Gtk.Grid = Gtk.Grid.new()
        grid_7.attach(label_7_text,    left=0, top=0, width=1, height=1)  # noqa
        grid_7.attach(textview_7_text, left=1, top=0, width=2, height=1)  # noqa
        grid_7.set_column_homogeneous(False)
        grid_7.set_row_homogeneous(False)
        frame_cliptextencode_007negative_prompt.add(widget=grid_7)  # noqa

        # New Frame
        frame_vaedecode_008vae_decode: Gtk.Frame = Gtk.Frame.new(label="VAE Decode")  # noqa
        frame_vaedecode_008vae_decode.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        grid_8: Gtk.Grid = Gtk.Grid.new()
        grid_8.set_column_homogeneous(False)
        grid_8.set_row_homogeneous(False)
        frame_vaedecode_008vae_decode.add(widget=grid_8)  # noqa

        # New Frame
        frame_saveimage_009save_image: Gtk.Frame = Gtk.Frame.new(label="Save Image")  # noqa
        frame_saveimage_009save_image.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_9_filename_prefix: Gtk.Label = Gtk.Label.new("Filename_Prefix")
        entry_9_filename_prefix: Gtk.Entry = Gtk.Entry.new()
        entry_9_filename_prefix.set_text("generated")
        entry_9_filename_prefix.set_name("entry_9_filename_prefix")
        entry_9_filename_prefix.set_hexpand(True)
        widget_getters[entry_9_filename_prefix.get_name()] = entry_9_filename_prefix.get_text
        widget_setters[entry_9_filename_prefix.get_name()] = entry_9_filename_prefix.set_text

        grid_9: Gtk.Grid = Gtk.Grid.new()
        grid_9.attach(label_9_filename_prefix, left=0, top=0, width=1, height=1)  # noqa
        grid_9.attach(entry_9_filename_prefix, left=1, top=0, width=2, height=1)  # noqa
        grid_9.set_column_homogeneous(False)
        grid_9.set_row_homogeneous(False)
        frame_saveimage_009save_image.add(widget=grid_9)  # noqa
        content_area: Gtk.Box = dialog.get_content_area()
        content_area.pack_start(child=frame_ksampler_003ksampler, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_checkpointloadersimple_004load_checkpoint, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_emptylatentimage_005empty_latent_image, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_cliptextencode_006positive_prompt, expand=True, fill=True, padding=0)  # noqa
        content_area.pack_start(child=frame_cliptextencode_007negative_prompt, expand=True, fill=True, padding=0)  # noqa
        content_area.pack_start(child=frame_vaedecode_008vae_decode, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_saveimage_009save_image, expand=False, fill=False, padding=0)  # noqa

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
