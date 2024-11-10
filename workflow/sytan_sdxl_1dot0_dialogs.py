
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


class SytanSdxl1Dot0Dialogs(WorkflowDialogFactory):

    WORKFLOW_FILE = "sytan_sdxl_1.0_workflow_api.json"

    def __init__(self, accessor: NodesAccessor):
        super().__init__(
            accessor=accessor,
            api_workflow=SytanSdxl1Dot0Dialogs.WORKFLOW_FILE,
            dialog_config_chassis_name="SytanSdxl1Dot0Dialogs_dialog_config",
            wf_data_chassis_name="SytanSdxl1Dot0Dialogs_wf_data",
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
                                                     chassis_name="sytan_sdxl_1dot0_dialog",
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
        frame_checkpointloadersimple_004refiner_model: Gtk.Frame = Gtk.Frame.new(label="Refiner Model        #4")  # noqa
        frame_checkpointloadersimple_004refiner_model.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_4_ckpt_name: Gtk.Label = Gtk.Label.new("Ckpt_Name")
        comboboxtext_4_ckpt_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_4_ckpt_name: list[str] = get_models_filenames(
            model_type=ModelType.CHECKPOINTS,
            cu_origin=self.comfy_svr_origin)
        if combo_values_4_ckpt_name is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_4_ckpt_name:
            raise ValueError(fr"No models retrieved from ComfyUI")
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
        widget_getters[comboboxtext_4_ckpt_name.get_name()] = comboboxtext_4_ckpt_name.get_active_text  # noqa
        widget_setters[comboboxtext_4_ckpt_name.get_name()] = setter_4_ckpt_name  # noqa

        grid_4: Gtk.Grid = Gtk.Grid.new()
        grid_4.attach(label_4_ckpt_name,        left=0, top=0, width=1, height=1)  # noqa
        grid_4.attach(comboboxtext_4_ckpt_name, left=1, top=0, width=3, height=1)  # noqa
        grid_4.set_column_homogeneous(False)
        grid_4.set_row_homogeneous(False)
        frame_checkpointloadersimple_004refiner_model.add(widget=grid_4)  # noqa

        # New Frame
        frame_emptylatentimage_005image_resolution: Gtk.Frame = Gtk.Frame.new(label="Image Resolution        #5")  # noqa
        frame_emptylatentimage_005image_resolution.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_5_width: Gtk.Label = Gtk.Label.new("Width")
        label_5_width.set_margin_start(8)
        label_5_width.set_alignment(0.95, 0)
        entry_5_width: Gtk.Entry = Gtk.Entry.new()
        entry_5_width.set_text(str(1024))
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
        widget_getters[entry_5_width.get_name()] = getter_5_width  # noqa
        widget_setters[entry_5_width.get_name()] = setter_5_width  # noqa

        label_5_height: Gtk.Label = Gtk.Label.new("Height")
        label_5_height.set_margin_start(8)
        label_5_height.set_alignment(0.95, 0)
        entry_5_height: Gtk.Entry = Gtk.Entry.new()
        entry_5_height.set_text(str(1024))
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
        widget_getters[entry_5_height.get_name()] = getter_5_height  # noqa
        widget_setters[entry_5_height.get_name()] = setter_5_height  # noqa

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
        widget_getters[entry_5_batch_size.get_name()] = getter_5_batch_size  # noqa
        widget_setters[entry_5_batch_size.get_name()] = setter_5_batch_size  # noqa

        grid_5: Gtk.Grid = Gtk.Grid.new()
        grid_5.attach(label_5_width,      left=0, top=0, width=1, height=1)  # noqa
        grid_5.attach(entry_5_width,      left=1, top=0, width=3, height=1)  # noqa
        grid_5.attach(label_5_height,     left=4, top=0, width=1, height=1)  # noqa
        grid_5.attach(entry_5_height,     left=5, top=0, width=3, height=1)  # noqa
        grid_5.attach(label_5_batch_size, left=8, top=0, width=1, height=1)  # noqa
        grid_5.attach(entry_5_batch_size, left=9, top=0, width=3, height=1)  # noqa
        grid_5.set_column_homogeneous(False)
        grid_5.set_row_homogeneous(False)
        frame_emptylatentimage_005image_resolution.add(widget=grid_5)  # noqa

        # New Frame
        frame_checkpointloadersimple_010base_model: Gtk.Frame = Gtk.Frame.new(label="Base Model        #10")  # noqa
        frame_checkpointloadersimple_010base_model.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_10_ckpt_name: Gtk.Label = Gtk.Label.new("Ckpt_Name")
        comboboxtext_10_ckpt_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_10_ckpt_name: list[str] = get_models_filenames(
            model_type=ModelType.CHECKPOINTS,
            cu_origin=self.comfy_svr_origin)
        if combo_values_10_ckpt_name is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_10_ckpt_name:
            raise ValueError(fr"No models retrieved from ComfyUI")
        for combo_item_path in combo_values_10_ckpt_name:
            comboboxtext_10_ckpt_name.append_text(combo_item_path)
        comboboxtext_10_ckpt_name.set_name("comboboxtext_10_ckpt_name")
        comboboxtext_10_ckpt_name.set_hexpand(True)
        comboboxtext_10_ckpt_name.set_active(13)

        def change_handler_10_ckpt_name(source, **args):  # noqa
            pass
        comboboxtext_10_ckpt_name.connect(SIG_CHANGED, change_handler_10_ckpt_name)

        def setter_10_ckpt_name(a_val: str):
            nonlocal combo_values_10_ckpt_name
            selected_index = combo_values_10_ckpt_name.index(a_val)
            comboboxtext_10_ckpt_name.set_active(selected_index)
        widget_getters[comboboxtext_10_ckpt_name.get_name()] = comboboxtext_10_ckpt_name.get_active_text  # noqa
        widget_setters[comboboxtext_10_ckpt_name.get_name()] = setter_10_ckpt_name  # noqa

        grid_10: Gtk.Grid = Gtk.Grid.new()
        grid_10.attach(label_10_ckpt_name,        left=0, top=0, width=1, height=1)  # noqa
        grid_10.attach(comboboxtext_10_ckpt_name, left=1, top=0, width=3, height=1)  # noqa
        grid_10.set_column_homogeneous(False)
        grid_10.set_row_homogeneous(False)
        frame_checkpointloadersimple_010base_model.add(widget=grid_10)  # noqa

        # New Frame
        frame_ksampleradvanced_022base_pass: Gtk.Frame = Gtk.Frame.new(label="Base Pass        #22")  # noqa
        frame_ksampleradvanced_022base_pass.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        checkbutton_22_add_noise: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Add Noise")  # noqa
        checkbutton_22_add_noise.set_active(True)
        checkbutton_22_add_noise.set_name("checkbutton_22_add_noise")
        checkbutton_22_add_noise.set_hexpand(False)

        def toggled_handler_22_add_noise(source, **args):  # noqa
            pass
        checkbutton_22_add_noise.connect(SIG_TOGGLED, toggled_handler_22_add_noise)

        def getter_22_add_noise():
            return "enable" if checkbutton_22_add_noise.get_active() else "disable"
        widget_getters[checkbutton_22_add_noise.get_name()] = getter_22_add_noise  # noqa

        label_22_noise_seed: Gtk.Label = Gtk.Label.new("Noise_Seed")
        label_22_noise_seed.set_margin_start(8)
        label_22_noise_seed.set_alignment(0.95, 0)
        entry_22_noise_seed: Gtk.Entry = Gtk.Entry.new()
        entry_22_noise_seed.set_text(str(423))
        entry_22_noise_seed.set_name("entry_22_noise_seed")
        entry_22_noise_seed.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_22_noise_seed,
                           minimum=-1, maximum=18446744073709519872,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_22_noise_seed(source, **args):  # noqa
            pass
        entry_22_noise_seed.connect(SIG_CHANGED, change_handler_22_noise_seed)

        def getter_22_noise_seed() -> int:
            return int(entry_22_noise_seed.get_text())

        def setter_22_noise_seed(a_val: int):
            entry_22_noise_seed.set_text(str(a_val))
        widget_getters[entry_22_noise_seed.get_name()] = getter_22_noise_seed  # noqa
        widget_setters[entry_22_noise_seed.get_name()] = setter_22_noise_seed  # noqa

        label_22_steps: Gtk.Label = Gtk.Label.new("Steps")
        label_22_steps.set_margin_start(8)
        label_22_steps.set_alignment(0.95, 0)
        entry_22_steps: Gtk.Entry = Gtk.Entry.new()
        entry_22_steps.set_text(str(25))
        entry_22_steps.set_name("entry_22_steps")
        entry_22_steps.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_22_steps,
                           minimum=1, maximum=128,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_22_steps(source, **args):  # noqa
            pass
        entry_22_steps.connect(SIG_CHANGED, change_handler_22_steps)

        def getter_22_steps() -> int:
            return int(entry_22_steps.get_text())

        def setter_22_steps(a_val: int):
            entry_22_steps.set_text(str(a_val))
        widget_getters[entry_22_steps.get_name()] = getter_22_steps  # noqa
        widget_setters[entry_22_steps.get_name()] = setter_22_steps  # noqa

        label_22_cfg: Gtk.Label = Gtk.Label.new("Cfg")
        label_22_cfg.set_margin_start(8)
        adjustment_22_cfg: Gtk.Adjustment = Gtk.Adjustment(value=7.50000,
                                                           lower=1.00000,
                                                           upper=25.00000,
                                                           step_increment=0.100,
                                                           page_increment=2.000,
                                                           page_size=0)
        scale_22_cfg: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_22_cfg)  # noqa
        scale_22_cfg.set_name("scale_22_cfg")
        scale_22_cfg.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_22_cfg.set_hexpand(True)

        def change_handler_22_cfg(source, **args):  # noqa
            pass
        scale_22_cfg.connect(SIG_VALUE_CHANGED, change_handler_22_cfg)
        widget_getters[scale_22_cfg.get_name()] = scale_22_cfg.get_value
        widget_setters[scale_22_cfg.get_name()] = scale_22_cfg.set_value

        label_22_sampler_name: Gtk.Label = Gtk.Label.new("Sampler_Name")
        comboboxtext_22_sampler_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_22_sampler_name: list[str] = ["euler", "euler_ancestral", "heun", "heunpp2", "dpm_2", "dpm_2_ancestral", "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_sde", "dpmpp_sde_gpu", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu", "ddpm", "lcm", "ddim", "uni_pc", "uni_pc_bh2"]  # noqa
        for combo_item_path in combo_values_22_sampler_name:
            comboboxtext_22_sampler_name.append_text(combo_item_path)
        comboboxtext_22_sampler_name.set_name("comboboxtext_22_sampler_name")
        comboboxtext_22_sampler_name.set_hexpand(True)
        comboboxtext_22_sampler_name.set_active(19)

        def change_handler_22_sampler_name(source, **args):  # noqa
            pass
        comboboxtext_22_sampler_name.connect(SIG_CHANGED, change_handler_22_sampler_name)

        def setter_22_sampler_name(a_val: str):
            nonlocal combo_values_22_sampler_name
            selected_index = combo_values_22_sampler_name.index(a_val)
            comboboxtext_22_sampler_name.set_active(selected_index)
        widget_getters[comboboxtext_22_sampler_name.get_name()] = comboboxtext_22_sampler_name.get_active_text  # noqa
        widget_setters[comboboxtext_22_sampler_name.get_name()] = setter_22_sampler_name  # noqa

        label_22_scheduler: Gtk.Label = Gtk.Label.new("Scheduler")
        comboboxtext_22_scheduler: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_22_scheduler: list[str] = ["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"]  # noqa
        for combo_item_path in combo_values_22_scheduler:
            comboboxtext_22_scheduler.append_text(combo_item_path)
        comboboxtext_22_scheduler.set_name("comboboxtext_22_scheduler")
        comboboxtext_22_scheduler.set_hexpand(True)
        comboboxtext_22_scheduler.set_active(0)

        def change_handler_22_scheduler(source, **args):  # noqa
            pass
        comboboxtext_22_scheduler.connect(SIG_CHANGED, change_handler_22_scheduler)

        def setter_22_scheduler(a_val: str):
            nonlocal combo_values_22_scheduler
            selected_index = combo_values_22_scheduler.index(a_val)
            comboboxtext_22_scheduler.set_active(selected_index)
        widget_getters[comboboxtext_22_scheduler.get_name()] = comboboxtext_22_scheduler.get_active_text  # noqa
        widget_setters[comboboxtext_22_scheduler.get_name()] = setter_22_scheduler  # noqa

        label_22_start_at_step: Gtk.Label = Gtk.Label.new("Start_At_Step")
        label_22_start_at_step.set_margin_start(8)
        label_22_start_at_step.set_alignment(0.95, 0)
        entry_22_start_at_step: Gtk.Entry = Gtk.Entry.new()
        entry_22_start_at_step.set_text(str(0))
        entry_22_start_at_step.set_name("entry_22_start_at_step")
        entry_22_start_at_step.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_22_start_at_step,
                           minimum=0, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_22_start_at_step(source, **args):  # noqa
            pass
        entry_22_start_at_step.connect(SIG_CHANGED, change_handler_22_start_at_step)

        def getter_22_start_at_step() -> int:
            return int(entry_22_start_at_step.get_text())

        def setter_22_start_at_step(a_val: int):
            entry_22_start_at_step.set_text(str(a_val))
        widget_getters[entry_22_start_at_step.get_name()] = getter_22_start_at_step  # noqa
        widget_setters[entry_22_start_at_step.get_name()] = setter_22_start_at_step  # noqa

        label_22_end_at_step: Gtk.Label = Gtk.Label.new("End_At_Step")
        label_22_end_at_step.set_margin_start(8)
        label_22_end_at_step.set_alignment(0.95, 0)
        entry_22_end_at_step: Gtk.Entry = Gtk.Entry.new()
        entry_22_end_at_step.set_text(str(20))
        entry_22_end_at_step.set_name("entry_22_end_at_step")
        entry_22_end_at_step.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_22_end_at_step,
                           minimum=0, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_22_end_at_step(source, **args):  # noqa
            pass
        entry_22_end_at_step.connect(SIG_CHANGED, change_handler_22_end_at_step)

        def getter_22_end_at_step() -> int:
            return int(entry_22_end_at_step.get_text())

        def setter_22_end_at_step(a_val: int):
            entry_22_end_at_step.set_text(str(a_val))
        widget_getters[entry_22_end_at_step.get_name()] = getter_22_end_at_step  # noqa
        widget_setters[entry_22_end_at_step.get_name()] = setter_22_end_at_step  # noqa

        checkbutton_22_return_with_leftover_noise: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Return With Leftover Noise")  # noqa
        checkbutton_22_return_with_leftover_noise.set_active(True)
        checkbutton_22_return_with_leftover_noise.set_name("checkbutton_22_return_with_leftover_noise")
        checkbutton_22_return_with_leftover_noise.set_hexpand(False)

        def toggled_handler_22_return_with_leftover_noise(source, **args):  # noqa
            pass
        checkbutton_22_return_with_leftover_noise.connect(SIG_TOGGLED, toggled_handler_22_return_with_leftover_noise)

        def getter_22_return_with_leftover_noise():
            return "enable" if checkbutton_22_return_with_leftover_noise.get_active() else "disable"
        widget_getters[checkbutton_22_return_with_leftover_noise.get_name()] = getter_22_return_with_leftover_noise  # noqa

        grid_22: Gtk.Grid = Gtk.Grid.new()
        grid_22.attach(checkbutton_22_add_noise,                  left=0, top=0, width=8, height=1)  # noqa
        grid_22.attach(label_22_noise_seed,                       left=0, top=1, width=1, height=1)  # noqa
        grid_22.attach(entry_22_noise_seed,                       left=1, top=1, width=7, height=1)  # noqa
        grid_22.attach(label_22_steps,                            left=0, top=2, width=1, height=1)  # noqa
        grid_22.attach(entry_22_steps,                            left=1, top=2, width=7, height=1)  # noqa
        grid_22.attach(label_22_cfg,                              left=0, top=3, width=1, height=1)  # noqa
        grid_22.attach(scale_22_cfg,                              left=1, top=3, width=7, height=1)  # noqa
        grid_22.attach(label_22_sampler_name,                     left=0, top=4, width=1, height=1)  # noqa
        grid_22.attach(comboboxtext_22_sampler_name,              left=1, top=4, width=7, height=1)  # noqa
        grid_22.attach(label_22_scheduler,                        left=0, top=5, width=1, height=1)  # noqa
        grid_22.attach(comboboxtext_22_scheduler,                 left=1, top=5, width=7, height=1)  # noqa
        grid_22.attach(label_22_start_at_step,                    left=0, top=6, width=1, height=1)  # noqa
        grid_22.attach(entry_22_start_at_step,                    left=1, top=6, width=3, height=1)  # noqa
        grid_22.attach(label_22_end_at_step,                      left=4, top=6, width=1, height=1)  # noqa
        grid_22.attach(entry_22_end_at_step,                      left=5, top=6, width=3, height=1)  # noqa
        grid_22.attach(checkbutton_22_return_with_leftover_noise, left=0, top=7, width=8, height=1)  # noqa
        grid_22.set_column_homogeneous(False)
        grid_22.set_row_homogeneous(False)
        frame_ksampleradvanced_022base_pass.add(widget=grid_22)  # noqa

        # New Frame
        frame_ksampleradvanced_023refiner_pass: Gtk.Frame = Gtk.Frame.new(label="Refiner Pass        #23")  # noqa
        frame_ksampleradvanced_023refiner_pass.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        checkbutton_23_add_noise: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Add Noise")  # noqa
        checkbutton_23_add_noise.set_active(False)
        checkbutton_23_add_noise.set_name("checkbutton_23_add_noise")
        checkbutton_23_add_noise.set_hexpand(False)

        def toggled_handler_23_add_noise(source, **args):  # noqa
            pass
        checkbutton_23_add_noise.connect(SIG_TOGGLED, toggled_handler_23_add_noise)

        def getter_23_add_noise():
            return "enable" if checkbutton_23_add_noise.get_active() else "disable"
        widget_getters[checkbutton_23_add_noise.get_name()] = getter_23_add_noise  # noqa

        label_23_noise_seed: Gtk.Label = Gtk.Label.new("Noise_Seed")
        label_23_noise_seed.set_margin_start(8)
        label_23_noise_seed.set_alignment(0.95, 0)
        entry_23_noise_seed: Gtk.Entry = Gtk.Entry.new()
        entry_23_noise_seed.set_text(str(423))
        entry_23_noise_seed.set_name("entry_23_noise_seed")
        entry_23_noise_seed.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_23_noise_seed,
                           minimum=-1, maximum=18446744073709519872,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_23_noise_seed(source, **args):  # noqa
            pass
        entry_23_noise_seed.connect(SIG_CHANGED, change_handler_23_noise_seed)

        def getter_23_noise_seed() -> int:
            return int(entry_23_noise_seed.get_text())

        def setter_23_noise_seed(a_val: int):
            entry_23_noise_seed.set_text(str(a_val))
        widget_getters[entry_23_noise_seed.get_name()] = getter_23_noise_seed  # noqa
        widget_setters[entry_23_noise_seed.get_name()] = setter_23_noise_seed  # noqa

        label_23_steps: Gtk.Label = Gtk.Label.new("Steps")
        label_23_steps.set_margin_start(8)
        label_23_steps.set_alignment(0.95, 0)
        entry_23_steps: Gtk.Entry = Gtk.Entry.new()
        entry_23_steps.set_text(str(25))
        entry_23_steps.set_name("entry_23_steps")
        entry_23_steps.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_23_steps,
                           minimum=1, maximum=128,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_23_steps(source, **args):  # noqa
            pass
        entry_23_steps.connect(SIG_CHANGED, change_handler_23_steps)

        def getter_23_steps() -> int:
            return int(entry_23_steps.get_text())

        def setter_23_steps(a_val: int):
            entry_23_steps.set_text(str(a_val))
        widget_getters[entry_23_steps.get_name()] = getter_23_steps  # noqa
        widget_setters[entry_23_steps.get_name()] = setter_23_steps  # noqa

        label_23_cfg: Gtk.Label = Gtk.Label.new("Cfg")
        label_23_cfg.set_margin_start(8)
        adjustment_23_cfg: Gtk.Adjustment = Gtk.Adjustment(value=7.50000,
                                                           lower=1.00000,
                                                           upper=25.00000,
                                                           step_increment=0.100,
                                                           page_increment=2.000,
                                                           page_size=0)
        scale_23_cfg: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_23_cfg)  # noqa
        scale_23_cfg.set_name("scale_23_cfg")
        scale_23_cfg.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_23_cfg.set_hexpand(True)

        def change_handler_23_cfg(source, **args):  # noqa
            pass
        scale_23_cfg.connect(SIG_VALUE_CHANGED, change_handler_23_cfg)
        widget_getters[scale_23_cfg.get_name()] = scale_23_cfg.get_value
        widget_setters[scale_23_cfg.get_name()] = scale_23_cfg.set_value

        label_23_sampler_name: Gtk.Label = Gtk.Label.new("Sampler_Name")
        comboboxtext_23_sampler_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_23_sampler_name: list[str] = ["euler", "euler_ancestral", "heun", "heunpp2", "dpm_2", "dpm_2_ancestral", "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_sde", "dpmpp_sde_gpu", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu", "ddpm", "lcm", "ddim", "uni_pc", "uni_pc_bh2"]  # noqa
        for combo_item_path in combo_values_23_sampler_name:
            comboboxtext_23_sampler_name.append_text(combo_item_path)
        comboboxtext_23_sampler_name.set_name("comboboxtext_23_sampler_name")
        comboboxtext_23_sampler_name.set_hexpand(True)
        comboboxtext_23_sampler_name.set_active(19)

        def change_handler_23_sampler_name(source, **args):  # noqa
            pass
        comboboxtext_23_sampler_name.connect(SIG_CHANGED, change_handler_23_sampler_name)

        def setter_23_sampler_name(a_val: str):
            nonlocal combo_values_23_sampler_name
            selected_index = combo_values_23_sampler_name.index(a_val)
            comboboxtext_23_sampler_name.set_active(selected_index)
        widget_getters[comboboxtext_23_sampler_name.get_name()] = comboboxtext_23_sampler_name.get_active_text  # noqa
        widget_setters[comboboxtext_23_sampler_name.get_name()] = setter_23_sampler_name  # noqa

        label_23_scheduler: Gtk.Label = Gtk.Label.new("Scheduler")
        comboboxtext_23_scheduler: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_23_scheduler: list[str] = ["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"]  # noqa
        for combo_item_path in combo_values_23_scheduler:
            comboboxtext_23_scheduler.append_text(combo_item_path)
        comboboxtext_23_scheduler.set_name("comboboxtext_23_scheduler")
        comboboxtext_23_scheduler.set_hexpand(True)
        comboboxtext_23_scheduler.set_active(0)

        def change_handler_23_scheduler(source, **args):  # noqa
            pass
        comboboxtext_23_scheduler.connect(SIG_CHANGED, change_handler_23_scheduler)

        def setter_23_scheduler(a_val: str):
            nonlocal combo_values_23_scheduler
            selected_index = combo_values_23_scheduler.index(a_val)
            comboboxtext_23_scheduler.set_active(selected_index)
        widget_getters[comboboxtext_23_scheduler.get_name()] = comboboxtext_23_scheduler.get_active_text  # noqa
        widget_setters[comboboxtext_23_scheduler.get_name()] = setter_23_scheduler  # noqa

        label_23_start_at_step: Gtk.Label = Gtk.Label.new("Start_At_Step")
        label_23_start_at_step.set_margin_start(8)
        label_23_start_at_step.set_alignment(0.95, 0)
        entry_23_start_at_step: Gtk.Entry = Gtk.Entry.new()
        entry_23_start_at_step.set_text(str(20))
        entry_23_start_at_step.set_name("entry_23_start_at_step")
        entry_23_start_at_step.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_23_start_at_step,
                           minimum=0, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_23_start_at_step(source, **args):  # noqa
            pass
        entry_23_start_at_step.connect(SIG_CHANGED, change_handler_23_start_at_step)

        def getter_23_start_at_step() -> int:
            return int(entry_23_start_at_step.get_text())

        def setter_23_start_at_step(a_val: int):
            entry_23_start_at_step.set_text(str(a_val))
        widget_getters[entry_23_start_at_step.get_name()] = getter_23_start_at_step  # noqa
        widget_setters[entry_23_start_at_step.get_name()] = setter_23_start_at_step  # noqa

        label_23_end_at_step: Gtk.Label = Gtk.Label.new("End_At_Step")
        label_23_end_at_step.set_margin_start(8)
        label_23_end_at_step.set_alignment(0.95, 0)
        entry_23_end_at_step: Gtk.Entry = Gtk.Entry.new()
        entry_23_end_at_step.set_text(str(1000))
        entry_23_end_at_step.set_name("entry_23_end_at_step")
        entry_23_end_at_step.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_23_end_at_step,
                           minimum=0, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_23_end_at_step(source, **args):  # noqa
            pass
        entry_23_end_at_step.connect(SIG_CHANGED, change_handler_23_end_at_step)

        def getter_23_end_at_step() -> int:
            return int(entry_23_end_at_step.get_text())

        def setter_23_end_at_step(a_val: int):
            entry_23_end_at_step.set_text(str(a_val))
        widget_getters[entry_23_end_at_step.get_name()] = getter_23_end_at_step  # noqa
        widget_setters[entry_23_end_at_step.get_name()] = setter_23_end_at_step  # noqa

        checkbutton_23_return_with_leftover_noise: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Return With Leftover Noise")  # noqa
        checkbutton_23_return_with_leftover_noise.set_active(False)
        checkbutton_23_return_with_leftover_noise.set_name("checkbutton_23_return_with_leftover_noise")
        checkbutton_23_return_with_leftover_noise.set_hexpand(False)

        def toggled_handler_23_return_with_leftover_noise(source, **args):  # noqa
            pass
        checkbutton_23_return_with_leftover_noise.connect(SIG_TOGGLED, toggled_handler_23_return_with_leftover_noise)

        def getter_23_return_with_leftover_noise():
            return "enable" if checkbutton_23_return_with_leftover_noise.get_active() else "disable"
        widget_getters[checkbutton_23_return_with_leftover_noise.get_name()] = getter_23_return_with_leftover_noise  # noqa

        grid_23: Gtk.Grid = Gtk.Grid.new()
        grid_23.attach(checkbutton_23_add_noise,                  left=0, top=0, width=8, height=1)  # noqa
        grid_23.attach(label_23_noise_seed,                       left=0, top=1, width=1, height=1)  # noqa
        grid_23.attach(entry_23_noise_seed,                       left=1, top=1, width=7, height=1)  # noqa
        grid_23.attach(label_23_steps,                            left=0, top=2, width=1, height=1)  # noqa
        grid_23.attach(entry_23_steps,                            left=1, top=2, width=7, height=1)  # noqa
        grid_23.attach(label_23_cfg,                              left=0, top=3, width=1, height=1)  # noqa
        grid_23.attach(scale_23_cfg,                              left=1, top=3, width=7, height=1)  # noqa
        grid_23.attach(label_23_sampler_name,                     left=0, top=4, width=1, height=1)  # noqa
        grid_23.attach(comboboxtext_23_sampler_name,              left=1, top=4, width=7, height=1)  # noqa
        grid_23.attach(label_23_scheduler,                        left=0, top=5, width=1, height=1)  # noqa
        grid_23.attach(comboboxtext_23_scheduler,                 left=1, top=5, width=7, height=1)  # noqa
        grid_23.attach(label_23_start_at_step,                    left=0, top=6, width=1, height=1)  # noqa
        grid_23.attach(entry_23_start_at_step,                    left=1, top=6, width=3, height=1)  # noqa
        grid_23.attach(label_23_end_at_step,                      left=4, top=6, width=1, height=1)  # noqa
        grid_23.attach(entry_23_end_at_step,                      left=5, top=6, width=3, height=1)  # noqa
        grid_23.attach(checkbutton_23_return_with_leftover_noise, left=0, top=7, width=8, height=1)  # noqa
        grid_23.set_column_homogeneous(False)
        grid_23.set_row_homogeneous(False)
        frame_ksampleradvanced_023refiner_pass.add(widget=grid_23)  # noqa

        # New Frame
        frame_cliptextencodesdxl_075positive_base: Gtk.Frame = Gtk.Frame.new(label="Positive Base        #75")  # noqa
        frame_cliptextencodesdxl_075positive_base.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_75_width: Gtk.Label = Gtk.Label.new("Width")
        label_75_width.set_margin_start(8)
        label_75_width.set_alignment(0.95, 0)
        entry_75_width: Gtk.Entry = Gtk.Entry.new()
        entry_75_width.set_text(str(2048))
        entry_75_width.set_name("entry_75_width")
        entry_75_width.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_75_width,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_75_width(source, **args):  # noqa
            pass
        entry_75_width.connect(SIG_CHANGED, change_handler_75_width)

        def getter_75_width() -> int:
            return int(entry_75_width.get_text())

        def setter_75_width(a_val: int):
            entry_75_width.set_text(str(a_val))
        widget_getters[entry_75_width.get_name()] = getter_75_width  # noqa
        widget_setters[entry_75_width.get_name()] = setter_75_width  # noqa

        label_75_height: Gtk.Label = Gtk.Label.new("Height")
        label_75_height.set_margin_start(8)
        label_75_height.set_alignment(0.95, 0)
        entry_75_height: Gtk.Entry = Gtk.Entry.new()
        entry_75_height.set_text(str(2048))
        entry_75_height.set_name("entry_75_height")
        entry_75_height.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_75_height,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_75_height(source, **args):  # noqa
            pass
        entry_75_height.connect(SIG_CHANGED, change_handler_75_height)

        def getter_75_height() -> int:
            return int(entry_75_height.get_text())

        def setter_75_height(a_val: int):
            entry_75_height.set_text(str(a_val))
        widget_getters[entry_75_height.get_name()] = getter_75_height  # noqa
        widget_setters[entry_75_height.get_name()] = setter_75_height  # noqa

        label_75_crop_w: Gtk.Label = Gtk.Label.new("Crop_W")
        label_75_crop_w.set_margin_start(8)
        label_75_crop_w.set_alignment(0.95, 0)
        entry_75_crop_w: Gtk.Entry = Gtk.Entry.new()
        entry_75_crop_w.set_text(str(0))
        entry_75_crop_w.set_name("entry_75_crop_w")
        entry_75_crop_w.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_75_crop_w,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_75_crop_w(source, **args):  # noqa
            pass
        entry_75_crop_w.connect(SIG_CHANGED, change_handler_75_crop_w)

        def getter_75_crop_w() -> int:
            return int(entry_75_crop_w.get_text())

        def setter_75_crop_w(a_val: int):
            entry_75_crop_w.set_text(str(a_val))
        widget_getters[entry_75_crop_w.get_name()] = getter_75_crop_w  # noqa
        widget_setters[entry_75_crop_w.get_name()] = setter_75_crop_w  # noqa

        label_75_crop_h: Gtk.Label = Gtk.Label.new("Crop_H")
        label_75_crop_h.set_margin_start(8)
        label_75_crop_h.set_alignment(0.95, 0)
        entry_75_crop_h: Gtk.Entry = Gtk.Entry.new()
        entry_75_crop_h.set_text(str(0))
        entry_75_crop_h.set_name("entry_75_crop_h")
        entry_75_crop_h.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_75_crop_h,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_75_crop_h(source, **args):  # noqa
            pass
        entry_75_crop_h.connect(SIG_CHANGED, change_handler_75_crop_h)

        def getter_75_crop_h() -> int:
            return int(entry_75_crop_h.get_text())

        def setter_75_crop_h(a_val: int):
            entry_75_crop_h.set_text(str(a_val))
        widget_getters[entry_75_crop_h.get_name()] = getter_75_crop_h  # noqa
        widget_setters[entry_75_crop_h.get_name()] = setter_75_crop_h  # noqa

        label_75_target_width: Gtk.Label = Gtk.Label.new("Target_Width")
        label_75_target_width.set_margin_start(8)
        label_75_target_width.set_alignment(0.95, 0)
        entry_75_target_width: Gtk.Entry = Gtk.Entry.new()
        entry_75_target_width.set_text(str(2048))
        entry_75_target_width.set_name("entry_75_target_width")
        entry_75_target_width.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_75_target_width,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_75_target_width(source, **args):  # noqa
            pass
        entry_75_target_width.connect(SIG_CHANGED, change_handler_75_target_width)

        def getter_75_target_width() -> int:
            return int(entry_75_target_width.get_text())

        def setter_75_target_width(a_val: int):
            entry_75_target_width.set_text(str(a_val))
        widget_getters[entry_75_target_width.get_name()] = getter_75_target_width  # noqa
        widget_setters[entry_75_target_width.get_name()] = setter_75_target_width  # noqa

        label_75_target_height: Gtk.Label = Gtk.Label.new("Target_Height")
        label_75_target_height.set_margin_start(8)
        label_75_target_height.set_alignment(0.95, 0)
        entry_75_target_height: Gtk.Entry = Gtk.Entry.new()
        entry_75_target_height.set_text(str(2048))
        entry_75_target_height.set_name("entry_75_target_height")
        entry_75_target_height.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_75_target_height,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_75_target_height(source, **args):  # noqa
            pass
        entry_75_target_height.connect(SIG_CHANGED, change_handler_75_target_height)

        def getter_75_target_height() -> int:
            return int(entry_75_target_height.get_text())

        def setter_75_target_height(a_val: int):
            entry_75_target_height.set_text(str(a_val))
        widget_getters[entry_75_target_height.get_name()] = getter_75_target_height  # noqa
        widget_setters[entry_75_target_height.get_name()] = setter_75_target_height  # noqa

        label_75_text_g: Gtk.Label = Gtk.Label.new("Text_G")
        textview_75_text_g: Gtk.TextView = Gtk.TextView.new()
        textview_75_text_g.get_buffer().set_text("A head on portrait photograph of a majestic and elegant white tiger in an autumn forest full of foliage and trees at sunset")  # noqa
        textview_75_text_g.set_name("textview_75_text_g")
        textview_75_text_g.set_hexpand(True)
        textview_75_text_g.set_vexpand(True)
        textview_75_text_g.set_valign(Gtk.Align.FILL)
        # Create a ScrolledWindow to hold the TextView
        scrolled_window_75_text_g = Gtk.ScrolledWindow()
        scrolled_window_75_text_g.add(textview_75_text_g)  # noqa
        scrolled_window_75_text_g.set_size_request(864, 288)

        def preedit_handler_75_text_g(source, **args):  # noqa
            pass
        textview_75_text_g.connect(SIG_PREEDIT_CHANGED, preedit_handler_75_text_g)

        def getter_75_text_g():
            buffer: Gtk.TextBuffer = textview_75_text_g.get_buffer()
            start: Gtk.TextIter = buffer.get_start_iter()
            end: Gtk.TextIter = buffer.get_end_iter()
            return buffer.get_text(start, end, False)

        def setter_75_text_g(a_val: str):
            textview_75_text_g.get_buffer().set_text(str(a_val))

        widget_getters[textview_75_text_g.get_name()] = getter_75_text_g
        widget_setters[textview_75_text_g.get_name()] = setter_75_text_g

        label_75_text_l: Gtk.Label = Gtk.Label.new("Text_L")
        textview_75_text_l: Gtk.TextView = Gtk.TextView.new()
        textview_75_text_l.get_buffer().set_text("centered, white tiger, autumn, forest, foliage, head on, looking into the camera, fujifilm, close up, bokeh, f1.8")  # noqa
        textview_75_text_l.set_name("textview_75_text_l")
        textview_75_text_l.set_hexpand(True)
        textview_75_text_l.set_vexpand(True)
        textview_75_text_l.set_valign(Gtk.Align.FILL)
        # Create a ScrolledWindow to hold the TextView
        scrolled_window_75_text_l = Gtk.ScrolledWindow()
        scrolled_window_75_text_l.add(textview_75_text_l)  # noqa
        scrolled_window_75_text_l.set_size_request(864, 288)

        def preedit_handler_75_text_l(source, **args):  # noqa
            pass
        textview_75_text_l.connect(SIG_PREEDIT_CHANGED, preedit_handler_75_text_l)

        def getter_75_text_l():
            buffer: Gtk.TextBuffer = textview_75_text_l.get_buffer()
            start: Gtk.TextIter = buffer.get_start_iter()
            end: Gtk.TextIter = buffer.get_end_iter()
            return buffer.get_text(start, end, False)

        def setter_75_text_l(a_val: str):
            textview_75_text_l.get_buffer().set_text(str(a_val))

        widget_getters[textview_75_text_l.get_name()] = getter_75_text_l
        widget_setters[textview_75_text_l.get_name()] = setter_75_text_l

        grid_75: Gtk.Grid = Gtk.Grid.new()
        grid_75.attach(label_75_width,            left=0, top=0, width=1, height=1)  # noqa
        grid_75.attach(entry_75_width,            left=1, top=0, width=3, height=1)  # noqa
        grid_75.attach(label_75_height,           left=4, top=0, width=1, height=1)  # noqa
        grid_75.attach(entry_75_height,           left=5, top=0, width=3, height=1)  # noqa
        grid_75.attach(label_75_crop_w,           left=8, top=0, width=1, height=1)  # noqa
        grid_75.attach(entry_75_crop_w,           left=9, top=0, width=3, height=1)  # noqa
        grid_75.attach(label_75_crop_h,           left=12, top=0, width=1, height=1)  # noqa
        grid_75.attach(entry_75_crop_h,           left=13, top=0, width=3, height=1)  # noqa
        grid_75.attach(label_75_target_width,     left=16, top=0, width=1, height=1)  # noqa
        grid_75.attach(entry_75_target_width,     left=17, top=0, width=3, height=1)  # noqa
        grid_75.attach(label_75_target_height,    left=20, top=0, width=1, height=1)  # noqa
        grid_75.attach(entry_75_target_height,    left=21, top=0, width=3, height=1)  # noqa
        grid_75.attach(label_75_text_g,           left=0, top=1, width=1, height=1)  # noqa
        grid_75.attach(scrolled_window_75_text_g, left=1, top=1, width=23, height=1)  # noqa
        grid_75.attach(label_75_text_l,           left=0, top=2, width=1, height=1)  # noqa
        grid_75.attach(scrolled_window_75_text_l, left=1, top=2, width=23, height=1)  # noqa
        grid_75.set_column_homogeneous(False)
        grid_75.set_row_homogeneous(False)
        frame_cliptextencodesdxl_075positive_base.add(widget=grid_75)  # noqa

        # New Frame
        frame_cliptextencodesdxlrefiner_081negative_refiner: Gtk.Frame = Gtk.Frame.new(label="Negative Refiner        #81")  # noqa
        frame_cliptextencodesdxlrefiner_081negative_refiner.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_81_ascore: Gtk.Label = Gtk.Label.new("Ascore")
        label_81_ascore.set_margin_start(8)
        label_81_ascore.set_alignment(0.95, 0)
        entry_81_ascore: Gtk.Entry = Gtk.Entry.new()
        entry_81_ascore.set_text(str(2))
        entry_81_ascore.set_name("entry_81_ascore")
        entry_81_ascore.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_81_ascore,
                           minimum=1, maximum=10,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_81_ascore(source, **args):  # noqa
            pass
        entry_81_ascore.connect(SIG_CHANGED, change_handler_81_ascore)

        def getter_81_ascore() -> int:
            return int(entry_81_ascore.get_text())

        def setter_81_ascore(a_val: int):
            entry_81_ascore.set_text(str(a_val))
        widget_getters[entry_81_ascore.get_name()] = getter_81_ascore  # noqa
        widget_setters[entry_81_ascore.get_name()] = setter_81_ascore  # noqa

        label_81_width: Gtk.Label = Gtk.Label.new("Width")
        label_81_width.set_margin_start(8)
        label_81_width.set_alignment(0.95, 0)
        entry_81_width: Gtk.Entry = Gtk.Entry.new()
        entry_81_width.set_text(str(2048))
        entry_81_width.set_name("entry_81_width")
        entry_81_width.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_81_width,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_81_width(source, **args):  # noqa
            pass
        entry_81_width.connect(SIG_CHANGED, change_handler_81_width)

        def getter_81_width() -> int:
            return int(entry_81_width.get_text())

        def setter_81_width(a_val: int):
            entry_81_width.set_text(str(a_val))
        widget_getters[entry_81_width.get_name()] = getter_81_width  # noqa
        widget_setters[entry_81_width.get_name()] = setter_81_width  # noqa

        label_81_height: Gtk.Label = Gtk.Label.new("Height")
        label_81_height.set_margin_start(8)
        label_81_height.set_alignment(0.95, 0)
        entry_81_height: Gtk.Entry = Gtk.Entry.new()
        entry_81_height.set_text(str(2048))
        entry_81_height.set_name("entry_81_height")
        entry_81_height.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_81_height,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_81_height(source, **args):  # noqa
            pass
        entry_81_height.connect(SIG_CHANGED, change_handler_81_height)

        def getter_81_height() -> int:
            return int(entry_81_height.get_text())

        def setter_81_height(a_val: int):
            entry_81_height.set_text(str(a_val))
        widget_getters[entry_81_height.get_name()] = getter_81_height  # noqa
        widget_setters[entry_81_height.get_name()] = setter_81_height  # noqa

        label_81_text: Gtk.Label = Gtk.Label.new("Text")
        textview_81_text: Gtk.TextView = Gtk.TextView.new()
        textview_81_text.get_buffer().set_text("noise, grit, dull, washed out, low contrast, blurry, deep-fried, hazy, malformed, warped, deformed")  # noqa
        textview_81_text.set_name("textview_81_text")
        textview_81_text.set_hexpand(True)
        textview_81_text.set_vexpand(True)
        textview_81_text.set_valign(Gtk.Align.FILL)
        # Create a ScrolledWindow to hold the TextView
        scrolled_window_81_text = Gtk.ScrolledWindow()
        scrolled_window_81_text.add(textview_81_text)  # noqa
        scrolled_window_81_text.set_size_request(864, 288)

        def preedit_handler_81_text(source, **args):  # noqa
            pass
        textview_81_text.connect(SIG_PREEDIT_CHANGED, preedit_handler_81_text)

        def getter_81_text():
            buffer: Gtk.TextBuffer = textview_81_text.get_buffer()
            start: Gtk.TextIter = buffer.get_start_iter()
            end: Gtk.TextIter = buffer.get_end_iter()
            return buffer.get_text(start, end, False)

        def setter_81_text(a_val: str):
            textview_81_text.get_buffer().set_text(str(a_val))

        widget_getters[textview_81_text.get_name()] = getter_81_text
        widget_setters[textview_81_text.get_name()] = setter_81_text

        grid_81: Gtk.Grid = Gtk.Grid.new()
        grid_81.attach(label_81_ascore,         left=0, top=0, width=1, height=1)  # noqa
        grid_81.attach(entry_81_ascore,         left=1, top=0, width=3, height=1)  # noqa
        grid_81.attach(label_81_width,          left=4, top=0, width=1, height=1)  # noqa
        grid_81.attach(entry_81_width,          left=5, top=0, width=3, height=1)  # noqa
        grid_81.attach(label_81_height,         left=8, top=0, width=1, height=1)  # noqa
        grid_81.attach(entry_81_height,         left=9, top=0, width=3, height=1)  # noqa
        grid_81.attach(label_81_text,           left=0, top=1, width=1, height=1)  # noqa
        grid_81.attach(scrolled_window_81_text, left=1, top=1, width=11, height=1)  # noqa
        grid_81.set_column_homogeneous(False)
        grid_81.set_row_homogeneous(False)
        frame_cliptextencodesdxlrefiner_081negative_refiner.add(widget=grid_81)  # noqa

        # New Frame
        frame_cliptextencodesdxl_082negative_base: Gtk.Frame = Gtk.Frame.new(label="Negative Base        #82")  # noqa
        frame_cliptextencodesdxl_082negative_base.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_82_width: Gtk.Label = Gtk.Label.new("Width")
        label_82_width.set_margin_start(8)
        label_82_width.set_alignment(0.95, 0)
        entry_82_width: Gtk.Entry = Gtk.Entry.new()
        entry_82_width.set_text(str(2048))
        entry_82_width.set_name("entry_82_width")
        entry_82_width.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_82_width,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_82_width(source, **args):  # noqa
            pass
        entry_82_width.connect(SIG_CHANGED, change_handler_82_width)

        def getter_82_width() -> int:
            return int(entry_82_width.get_text())

        def setter_82_width(a_val: int):
            entry_82_width.set_text(str(a_val))
        widget_getters[entry_82_width.get_name()] = getter_82_width  # noqa
        widget_setters[entry_82_width.get_name()] = setter_82_width  # noqa

        label_82_height: Gtk.Label = Gtk.Label.new("Height")
        label_82_height.set_margin_start(8)
        label_82_height.set_alignment(0.95, 0)
        entry_82_height: Gtk.Entry = Gtk.Entry.new()
        entry_82_height.set_text(str(2048))
        entry_82_height.set_name("entry_82_height")
        entry_82_height.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_82_height,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_82_height(source, **args):  # noqa
            pass
        entry_82_height.connect(SIG_CHANGED, change_handler_82_height)

        def getter_82_height() -> int:
            return int(entry_82_height.get_text())

        def setter_82_height(a_val: int):
            entry_82_height.set_text(str(a_val))
        widget_getters[entry_82_height.get_name()] = getter_82_height  # noqa
        widget_setters[entry_82_height.get_name()] = setter_82_height  # noqa

        label_82_crop_w: Gtk.Label = Gtk.Label.new("Crop_W")
        label_82_crop_w.set_margin_start(8)
        label_82_crop_w.set_alignment(0.95, 0)
        entry_82_crop_w: Gtk.Entry = Gtk.Entry.new()
        entry_82_crop_w.set_text(str(0))
        entry_82_crop_w.set_name("entry_82_crop_w")
        entry_82_crop_w.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_82_crop_w,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_82_crop_w(source, **args):  # noqa
            pass
        entry_82_crop_w.connect(SIG_CHANGED, change_handler_82_crop_w)

        def getter_82_crop_w() -> int:
            return int(entry_82_crop_w.get_text())

        def setter_82_crop_w(a_val: int):
            entry_82_crop_w.set_text(str(a_val))
        widget_getters[entry_82_crop_w.get_name()] = getter_82_crop_w  # noqa
        widget_setters[entry_82_crop_w.get_name()] = setter_82_crop_w  # noqa

        label_82_crop_h: Gtk.Label = Gtk.Label.new("Crop_H")
        label_82_crop_h.set_margin_start(8)
        label_82_crop_h.set_alignment(0.95, 0)
        entry_82_crop_h: Gtk.Entry = Gtk.Entry.new()
        entry_82_crop_h.set_text(str(0))
        entry_82_crop_h.set_name("entry_82_crop_h")
        entry_82_crop_h.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_82_crop_h,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_82_crop_h(source, **args):  # noqa
            pass
        entry_82_crop_h.connect(SIG_CHANGED, change_handler_82_crop_h)

        def getter_82_crop_h() -> int:
            return int(entry_82_crop_h.get_text())

        def setter_82_crop_h(a_val: int):
            entry_82_crop_h.set_text(str(a_val))
        widget_getters[entry_82_crop_h.get_name()] = getter_82_crop_h  # noqa
        widget_setters[entry_82_crop_h.get_name()] = setter_82_crop_h  # noqa

        label_82_target_width: Gtk.Label = Gtk.Label.new("Target_Width")
        label_82_target_width.set_margin_start(8)
        label_82_target_width.set_alignment(0.95, 0)
        entry_82_target_width: Gtk.Entry = Gtk.Entry.new()
        entry_82_target_width.set_text(str(2048))
        entry_82_target_width.set_name("entry_82_target_width")
        entry_82_target_width.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_82_target_width,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_82_target_width(source, **args):  # noqa
            pass
        entry_82_target_width.connect(SIG_CHANGED, change_handler_82_target_width)

        def getter_82_target_width() -> int:
            return int(entry_82_target_width.get_text())

        def setter_82_target_width(a_val: int):
            entry_82_target_width.set_text(str(a_val))
        widget_getters[entry_82_target_width.get_name()] = getter_82_target_width  # noqa
        widget_setters[entry_82_target_width.get_name()] = setter_82_target_width  # noqa

        label_82_target_height: Gtk.Label = Gtk.Label.new("Target_Height")
        label_82_target_height.set_margin_start(8)
        label_82_target_height.set_alignment(0.95, 0)
        entry_82_target_height: Gtk.Entry = Gtk.Entry.new()
        entry_82_target_height.set_text(str(2048))
        entry_82_target_height.set_name("entry_82_target_height")
        entry_82_target_height.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_82_target_height,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_82_target_height(source, **args):  # noqa
            pass
        entry_82_target_height.connect(SIG_CHANGED, change_handler_82_target_height)

        def getter_82_target_height() -> int:
            return int(entry_82_target_height.get_text())

        def setter_82_target_height(a_val: int):
            entry_82_target_height.set_text(str(a_val))
        widget_getters[entry_82_target_height.get_name()] = getter_82_target_height  # noqa
        widget_setters[entry_82_target_height.get_name()] = setter_82_target_height  # noqa

        label_82_text_g: Gtk.Label = Gtk.Label.new("Text_G")
        textview_82_text_g: Gtk.TextView = Gtk.TextView.new()
        textview_82_text_g.get_buffer().set_text("noise, grit, dull, washed out, low contrast, blurry, deep-fried, hazy, malformed, warped, deformed")  # noqa
        textview_82_text_g.set_name("textview_82_text_g")
        textview_82_text_g.set_hexpand(True)
        textview_82_text_g.set_vexpand(True)
        textview_82_text_g.set_valign(Gtk.Align.FILL)
        # Create a ScrolledWindow to hold the TextView
        scrolled_window_82_text_g = Gtk.ScrolledWindow()
        scrolled_window_82_text_g.add(textview_82_text_g)  # noqa
        scrolled_window_82_text_g.set_size_request(864, 288)

        def preedit_handler_82_text_g(source, **args):  # noqa
            pass
        textview_82_text_g.connect(SIG_PREEDIT_CHANGED, preedit_handler_82_text_g)

        def getter_82_text_g():
            buffer: Gtk.TextBuffer = textview_82_text_g.get_buffer()
            start: Gtk.TextIter = buffer.get_start_iter()
            end: Gtk.TextIter = buffer.get_end_iter()
            return buffer.get_text(start, end, False)

        def setter_82_text_g(a_val: str):
            textview_82_text_g.get_buffer().set_text(str(a_val))

        widget_getters[textview_82_text_g.get_name()] = getter_82_text_g
        widget_setters[textview_82_text_g.get_name()] = setter_82_text_g

        label_82_text_l: Gtk.Label = Gtk.Label.new("Text_L")
        textview_82_text_l: Gtk.TextView = Gtk.TextView.new()
        textview_82_text_l.get_buffer().set_text("noise, grit, dull, washed out, low contrast, blurry, deep-fried, hazy, malformed, warped, deformed")  # noqa
        textview_82_text_l.set_name("textview_82_text_l")
        textview_82_text_l.set_hexpand(True)
        textview_82_text_l.set_vexpand(True)
        textview_82_text_l.set_valign(Gtk.Align.FILL)
        # Create a ScrolledWindow to hold the TextView
        scrolled_window_82_text_l = Gtk.ScrolledWindow()
        scrolled_window_82_text_l.add(textview_82_text_l)  # noqa
        scrolled_window_82_text_l.set_size_request(864, 288)

        def preedit_handler_82_text_l(source, **args):  # noqa
            pass
        textview_82_text_l.connect(SIG_PREEDIT_CHANGED, preedit_handler_82_text_l)

        def getter_82_text_l():
            buffer: Gtk.TextBuffer = textview_82_text_l.get_buffer()
            start: Gtk.TextIter = buffer.get_start_iter()
            end: Gtk.TextIter = buffer.get_end_iter()
            return buffer.get_text(start, end, False)

        def setter_82_text_l(a_val: str):
            textview_82_text_l.get_buffer().set_text(str(a_val))

        widget_getters[textview_82_text_l.get_name()] = getter_82_text_l
        widget_setters[textview_82_text_l.get_name()] = setter_82_text_l

        grid_82: Gtk.Grid = Gtk.Grid.new()
        grid_82.attach(label_82_width,            left=0, top=0, width=1, height=1)  # noqa
        grid_82.attach(entry_82_width,            left=1, top=0, width=3, height=1)  # noqa
        grid_82.attach(label_82_height,           left=4, top=0, width=1, height=1)  # noqa
        grid_82.attach(entry_82_height,           left=5, top=0, width=3, height=1)  # noqa
        grid_82.attach(label_82_crop_w,           left=8, top=0, width=1, height=1)  # noqa
        grid_82.attach(entry_82_crop_w,           left=9, top=0, width=3, height=1)  # noqa
        grid_82.attach(label_82_crop_h,           left=12, top=0, width=1, height=1)  # noqa
        grid_82.attach(entry_82_crop_h,           left=13, top=0, width=3, height=1)  # noqa
        grid_82.attach(label_82_target_width,     left=16, top=0, width=1, height=1)  # noqa
        grid_82.attach(entry_82_target_width,     left=17, top=0, width=3, height=1)  # noqa
        grid_82.attach(label_82_target_height,    left=20, top=0, width=1, height=1)  # noqa
        grid_82.attach(entry_82_target_height,    left=21, top=0, width=3, height=1)  # noqa
        grid_82.attach(label_82_text_g,           left=0, top=1, width=1, height=1)  # noqa
        grid_82.attach(scrolled_window_82_text_g, left=1, top=1, width=23, height=1)  # noqa
        grid_82.attach(label_82_text_l,           left=0, top=2, width=1, height=1)  # noqa
        grid_82.attach(scrolled_window_82_text_l, left=1, top=2, width=23, height=1)  # noqa
        grid_82.set_column_homogeneous(False)
        grid_82.set_row_homogeneous(False)
        frame_cliptextencodesdxl_082negative_base.add(widget=grid_82)  # noqa

        # New Frame
        frame_cliptextencodesdxlrefiner_120positive_refiner: Gtk.Frame = Gtk.Frame.new(label="Positive Refiner        #120")  # noqa
        frame_cliptextencodesdxlrefiner_120positive_refiner.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_120_ascore: Gtk.Label = Gtk.Label.new("Ascore")
        label_120_ascore.set_margin_start(8)
        label_120_ascore.set_alignment(0.95, 0)
        entry_120_ascore: Gtk.Entry = Gtk.Entry.new()
        entry_120_ascore.set_text(str(6))
        entry_120_ascore.set_name("entry_120_ascore")
        entry_120_ascore.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_120_ascore,
                           minimum=1, maximum=10,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_120_ascore(source, **args):  # noqa
            pass
        entry_120_ascore.connect(SIG_CHANGED, change_handler_120_ascore)

        def getter_120_ascore() -> int:
            return int(entry_120_ascore.get_text())

        def setter_120_ascore(a_val: int):
            entry_120_ascore.set_text(str(a_val))
        widget_getters[entry_120_ascore.get_name()] = getter_120_ascore  # noqa
        widget_setters[entry_120_ascore.get_name()] = setter_120_ascore  # noqa

        label_120_width: Gtk.Label = Gtk.Label.new("Width")
        label_120_width.set_margin_start(8)
        label_120_width.set_alignment(0.95, 0)
        entry_120_width: Gtk.Entry = Gtk.Entry.new()
        entry_120_width.set_text(str(2048))
        entry_120_width.set_name("entry_120_width")
        entry_120_width.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_120_width,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_120_width(source, **args):  # noqa
            pass
        entry_120_width.connect(SIG_CHANGED, change_handler_120_width)

        def getter_120_width() -> int:
            return int(entry_120_width.get_text())

        def setter_120_width(a_val: int):
            entry_120_width.set_text(str(a_val))
        widget_getters[entry_120_width.get_name()] = getter_120_width  # noqa
        widget_setters[entry_120_width.get_name()] = setter_120_width  # noqa

        label_120_height: Gtk.Label = Gtk.Label.new("Height")
        label_120_height.set_margin_start(8)
        label_120_height.set_alignment(0.95, 0)
        entry_120_height: Gtk.Entry = Gtk.Entry.new()
        entry_120_height.set_text(str(2048))
        entry_120_height.set_name("entry_120_height")
        entry_120_height.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_120_height,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_120_height(source, **args):  # noqa
            pass
        entry_120_height.connect(SIG_CHANGED, change_handler_120_height)

        def getter_120_height() -> int:
            return int(entry_120_height.get_text())

        def setter_120_height(a_val: int):
            entry_120_height.set_text(str(a_val))
        widget_getters[entry_120_height.get_name()] = getter_120_height  # noqa
        widget_setters[entry_120_height.get_name()] = setter_120_height  # noqa

        label_120_text: Gtk.Label = Gtk.Label.new("Text")
        textview_120_text: Gtk.TextView = Gtk.TextView.new()
        textview_120_text.get_buffer().set_text("centered, white tiger, autumn, forest, foliage, head on, looking into the camera, fujifilm, close up, bokeh, f1.8")  # noqa
        textview_120_text.set_name("textview_120_text")
        textview_120_text.set_hexpand(True)
        textview_120_text.set_vexpand(True)
        textview_120_text.set_valign(Gtk.Align.FILL)
        # Create a ScrolledWindow to hold the TextView
        scrolled_window_120_text = Gtk.ScrolledWindow()
        scrolled_window_120_text.add(textview_120_text)  # noqa
        scrolled_window_120_text.set_size_request(864, 288)

        def preedit_handler_120_text(source, **args):  # noqa
            pass
        textview_120_text.connect(SIG_PREEDIT_CHANGED, preedit_handler_120_text)

        def getter_120_text():
            buffer: Gtk.TextBuffer = textview_120_text.get_buffer()
            start: Gtk.TextIter = buffer.get_start_iter()
            end: Gtk.TextIter = buffer.get_end_iter()
            return buffer.get_text(start, end, False)

        def setter_120_text(a_val: str):
            textview_120_text.get_buffer().set_text(str(a_val))

        widget_getters[textview_120_text.get_name()] = getter_120_text
        widget_setters[textview_120_text.get_name()] = setter_120_text

        grid_120: Gtk.Grid = Gtk.Grid.new()
        grid_120.attach(label_120_ascore,         left=0, top=0, width=1, height=1)  # noqa
        grid_120.attach(entry_120_ascore,         left=1, top=0, width=3, height=1)  # noqa
        grid_120.attach(label_120_width,          left=4, top=0, width=1, height=1)  # noqa
        grid_120.attach(entry_120_width,          left=5, top=0, width=3, height=1)  # noqa
        grid_120.attach(label_120_height,         left=8, top=0, width=1, height=1)  # noqa
        grid_120.attach(entry_120_height,         left=9, top=0, width=3, height=1)  # noqa
        grid_120.attach(label_120_text,           left=0, top=1, width=1, height=1)  # noqa
        grid_120.attach(scrolled_window_120_text, left=1, top=1, width=11, height=1)  # noqa
        grid_120.set_column_homogeneous(False)
        grid_120.set_row_homogeneous(False)
        frame_cliptextencodesdxlrefiner_120positive_refiner.add(widget=grid_120)  # noqa

        # New Frame
        frame_saveimage_184sytan_workflow: Gtk.Frame = Gtk.Frame.new(label="Sytan Workflow        #184")  # noqa
        frame_saveimage_184sytan_workflow.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_184_filename_prefix: Gtk.Label = Gtk.Label.new("Filename_Prefix")
        entry_184_filename_prefix: Gtk.Entry = Gtk.Entry.new()
        entry_184_filename_prefix.set_text("gimp_generated")
        entry_184_filename_prefix.set_name("entry_184_filename_prefix")
        entry_184_filename_prefix.set_hexpand(True)
        widget_getters[entry_184_filename_prefix.get_name()] = entry_184_filename_prefix.get_text
        widget_setters[entry_184_filename_prefix.get_name()] = entry_184_filename_prefix.set_text

        grid_184: Gtk.Grid = Gtk.Grid.new()
        grid_184.attach(label_184_filename_prefix, left=0, top=0, width=1, height=1)  # noqa
        grid_184.attach(entry_184_filename_prefix, left=1, top=0, width=3, height=1)  # noqa
        grid_184.set_column_homogeneous(False)
        grid_184.set_row_homogeneous(False)
        frame_saveimage_184sytan_workflow.add(widget=grid_184)  # noqa

        # New Frame
        frame_upscalemodelloader_187upscale_model: Gtk.Frame = Gtk.Frame.new(label="Upscale Model        #187")  # noqa
        frame_upscalemodelloader_187upscale_model.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_187_model_name: Gtk.Label = Gtk.Label.new("Model_Name")
        comboboxtext_187_model_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_187_model_name: list[str] = get_models_filenames(
            model_type=ModelType.UPSCALE_MODELS,
            cu_origin=self.comfy_svr_origin)
        if combo_values_187_model_name is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_187_model_name:
            raise ValueError(fr"No models retrieved from ComfyUI")
        for combo_item_path in combo_values_187_model_name:
            comboboxtext_187_model_name.append_text(combo_item_path)
        comboboxtext_187_model_name.set_name("comboboxtext_187_model_name")
        comboboxtext_187_model_name.set_hexpand(True)
        comboboxtext_187_model_name.set_active(0)

        def change_handler_187_model_name(source, **args):  # noqa
            pass
        comboboxtext_187_model_name.connect(SIG_CHANGED, change_handler_187_model_name)

        def setter_187_model_name(a_val: str):
            nonlocal combo_values_187_model_name
            selected_index = combo_values_187_model_name.index(a_val)
            comboboxtext_187_model_name.set_active(selected_index)
        widget_getters[comboboxtext_187_model_name.get_name()] = comboboxtext_187_model_name.get_active_text  # noqa
        widget_setters[comboboxtext_187_model_name.get_name()] = setter_187_model_name  # noqa

        grid_187: Gtk.Grid = Gtk.Grid.new()
        grid_187.attach(label_187_model_name,        left=0, top=0, width=1, height=1)  # noqa
        grid_187.attach(comboboxtext_187_model_name, left=1, top=0, width=3, height=1)  # noqa
        grid_187.set_column_homogeneous(False)
        grid_187.set_row_homogeneous(False)
        frame_upscalemodelloader_187upscale_model.add(widget=grid_187)  # noqa

        # New Frame
        frame_saveimage_2012048x_upscale: Gtk.Frame = Gtk.Frame.new(label="2048x Upscale        #201")  # noqa
        frame_saveimage_2012048x_upscale.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_201_filename_prefix: Gtk.Label = Gtk.Label.new("Filename_Prefix")
        entry_201_filename_prefix: Gtk.Entry = Gtk.Entry.new()
        entry_201_filename_prefix.set_text("generated_upscaled")
        entry_201_filename_prefix.set_name("entry_201_filename_prefix")
        entry_201_filename_prefix.set_hexpand(True)
        widget_getters[entry_201_filename_prefix.get_name()] = entry_201_filename_prefix.get_text
        widget_setters[entry_201_filename_prefix.get_name()] = entry_201_filename_prefix.set_text

        grid_201: Gtk.Grid = Gtk.Grid.new()
        grid_201.attach(label_201_filename_prefix, left=0, top=0, width=1, height=1)  # noqa
        grid_201.attach(entry_201_filename_prefix, left=1, top=0, width=3, height=1)  # noqa
        grid_201.set_column_homogeneous(False)
        grid_201.set_row_homogeneous(False)
        frame_saveimage_2012048x_upscale.add(widget=grid_201)  # noqa

        # New Frame
        frame_imagescaleby_215downscale: Gtk.Frame = Gtk.Frame.new(label="Downscale        #215")  # noqa
        frame_imagescaleby_215downscale.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_215_upscale_method: Gtk.Label = Gtk.Label.new("Upscale_Method")
        comboboxtext_215_upscale_method: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_215_upscale_method: list[str] = ["nearest-exact", "bilinear", "area", "bicubic", "lanczos"]  # noqa
        for combo_item_path in combo_values_215_upscale_method:
            comboboxtext_215_upscale_method.append_text(combo_item_path)
        comboboxtext_215_upscale_method.set_name("comboboxtext_215_upscale_method")
        comboboxtext_215_upscale_method.set_hexpand(True)
        comboboxtext_215_upscale_method.set_active(2)

        def change_handler_215_upscale_method(source, **args):  # noqa
            pass
        comboboxtext_215_upscale_method.connect(SIG_CHANGED, change_handler_215_upscale_method)

        def setter_215_upscale_method(a_val: str):
            nonlocal combo_values_215_upscale_method
            selected_index = combo_values_215_upscale_method.index(a_val)
            comboboxtext_215_upscale_method.set_active(selected_index)
        widget_getters[comboboxtext_215_upscale_method.get_name()] = comboboxtext_215_upscale_method.get_active_text  # noqa
        widget_setters[comboboxtext_215_upscale_method.get_name()] = setter_215_upscale_method  # noqa

        label_215_scale_by: Gtk.Label = Gtk.Label.new("Scale_By")
        label_215_scale_by.set_margin_start(8)
        entry_215_scale_by: Gtk.Entry = Gtk.Entry.new()
        entry_215_scale_by.set_text(str(0.5))
        entry_215_scale_by.set_name("entry_215_scale_by")
        entry_215_scale_by.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_215_scale_by,
                           minimum=0, maximum=None,  # noqa
                           int_only=False,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_215_scale_by(source, **args):  # noqa
            pass
        entry_215_scale_by.connect(SIG_CHANGED, change_handler_215_scale_by)

        def getter_215_scale_by() -> float:
            return float(entry_215_scale_by.get_text())

        def setter_215_scale_by(a_val: float):
            entry_215_scale_by.set_text(str(a_val))
        widget_getters[entry_215_scale_by.get_name()] = getter_215_scale_by  # noqa
        widget_setters[entry_215_scale_by.get_name()] = setter_215_scale_by  # noqa

        grid_215: Gtk.Grid = Gtk.Grid.new()
        grid_215.attach(label_215_upscale_method,        left=0, top=0, width=1, height=1)  # noqa
        grid_215.attach(comboboxtext_215_upscale_method, left=1, top=0, width=3, height=1)  # noqa
        grid_215.attach(label_215_scale_by,              left=0, top=1, width=1, height=1)  # noqa
        grid_215.attach(entry_215_scale_by,              left=1, top=1, width=3, height=1)  # noqa
        grid_215.set_column_homogeneous(False)
        grid_215.set_row_homogeneous(False)
        frame_imagescaleby_215downscale.add(widget=grid_215)  # noqa

        # New Frame
        frame_ksampleradvanced_216upscale_mixed_diff: Gtk.Frame = Gtk.Frame.new(label="Upscale Mixed Diff        #216")  # noqa
        frame_ksampleradvanced_216upscale_mixed_diff.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        checkbutton_216_add_noise: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Add Noise")  # noqa
        checkbutton_216_add_noise.set_active(True)
        checkbutton_216_add_noise.set_name("checkbutton_216_add_noise")
        checkbutton_216_add_noise.set_hexpand(False)

        def toggled_handler_216_add_noise(source, **args):  # noqa
            pass
        checkbutton_216_add_noise.connect(SIG_TOGGLED, toggled_handler_216_add_noise)

        def getter_216_add_noise():
            return "enable" if checkbutton_216_add_noise.get_active() else "disable"
        widget_getters[checkbutton_216_add_noise.get_name()] = getter_216_add_noise  # noqa

        label_216_noise_seed: Gtk.Label = Gtk.Label.new("Noise_Seed")
        label_216_noise_seed.set_margin_start(8)
        label_216_noise_seed.set_alignment(0.95, 0)
        entry_216_noise_seed: Gtk.Entry = Gtk.Entry.new()
        entry_216_noise_seed.set_text(str(423))
        entry_216_noise_seed.set_name("entry_216_noise_seed")
        entry_216_noise_seed.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_216_noise_seed,
                           minimum=-1, maximum=18446744073709519872,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_216_noise_seed(source, **args):  # noqa
            pass
        entry_216_noise_seed.connect(SIG_CHANGED, change_handler_216_noise_seed)

        def getter_216_noise_seed() -> int:
            return int(entry_216_noise_seed.get_text())

        def setter_216_noise_seed(a_val: int):
            entry_216_noise_seed.set_text(str(a_val))
        widget_getters[entry_216_noise_seed.get_name()] = getter_216_noise_seed  # noqa
        widget_setters[entry_216_noise_seed.get_name()] = setter_216_noise_seed  # noqa

        label_216_steps: Gtk.Label = Gtk.Label.new("Steps")
        label_216_steps.set_margin_start(8)
        label_216_steps.set_alignment(0.95, 0)
        entry_216_steps: Gtk.Entry = Gtk.Entry.new()
        entry_216_steps.set_text(str(30))
        entry_216_steps.set_name("entry_216_steps")
        entry_216_steps.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_216_steps,
                           minimum=1, maximum=128,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_216_steps(source, **args):  # noqa
            pass
        entry_216_steps.connect(SIG_CHANGED, change_handler_216_steps)

        def getter_216_steps() -> int:
            return int(entry_216_steps.get_text())

        def setter_216_steps(a_val: int):
            entry_216_steps.set_text(str(a_val))
        widget_getters[entry_216_steps.get_name()] = getter_216_steps  # noqa
        widget_setters[entry_216_steps.get_name()] = setter_216_steps  # noqa

        label_216_cfg: Gtk.Label = Gtk.Label.new("Cfg")
        label_216_cfg.set_margin_start(8)
        adjustment_216_cfg: Gtk.Adjustment = Gtk.Adjustment(value=7.50000,
                                                            lower=1.00000,
                                                            upper=25.00000,
                                                            step_increment=0.100,
                                                            page_increment=2.000,
                                                            page_size=0)
        scale_216_cfg: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_216_cfg)  # noqa
        scale_216_cfg.set_name("scale_216_cfg")
        scale_216_cfg.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_216_cfg.set_hexpand(True)

        def change_handler_216_cfg(source, **args):  # noqa
            pass
        scale_216_cfg.connect(SIG_VALUE_CHANGED, change_handler_216_cfg)
        widget_getters[scale_216_cfg.get_name()] = scale_216_cfg.get_value
        widget_setters[scale_216_cfg.get_name()] = scale_216_cfg.set_value

        label_216_sampler_name: Gtk.Label = Gtk.Label.new("Sampler_Name")
        comboboxtext_216_sampler_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_216_sampler_name: list[str] = ["euler", "euler_ancestral", "heun", "heunpp2", "dpm_2", "dpm_2_ancestral", "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_sde", "dpmpp_sde_gpu", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu", "ddpm", "lcm", "ddim", "uni_pc", "uni_pc_bh2"]  # noqa
        for combo_item_path in combo_values_216_sampler_name:
            comboboxtext_216_sampler_name.append_text(combo_item_path)
        comboboxtext_216_sampler_name.set_name("comboboxtext_216_sampler_name")
        comboboxtext_216_sampler_name.set_hexpand(True)
        comboboxtext_216_sampler_name.set_active(19)

        def change_handler_216_sampler_name(source, **args):  # noqa
            pass
        comboboxtext_216_sampler_name.connect(SIG_CHANGED, change_handler_216_sampler_name)

        def setter_216_sampler_name(a_val: str):
            nonlocal combo_values_216_sampler_name
            selected_index = combo_values_216_sampler_name.index(a_val)
            comboboxtext_216_sampler_name.set_active(selected_index)
        widget_getters[comboboxtext_216_sampler_name.get_name()] = comboboxtext_216_sampler_name.get_active_text  # noqa
        widget_setters[comboboxtext_216_sampler_name.get_name()] = setter_216_sampler_name  # noqa

        label_216_scheduler: Gtk.Label = Gtk.Label.new("Scheduler")
        comboboxtext_216_scheduler: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_216_scheduler: list[str] = ["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"]  # noqa
        for combo_item_path in combo_values_216_scheduler:
            comboboxtext_216_scheduler.append_text(combo_item_path)
        comboboxtext_216_scheduler.set_name("comboboxtext_216_scheduler")
        comboboxtext_216_scheduler.set_hexpand(True)
        comboboxtext_216_scheduler.set_active(5)

        def change_handler_216_scheduler(source, **args):  # noqa
            pass
        comboboxtext_216_scheduler.connect(SIG_CHANGED, change_handler_216_scheduler)

        def setter_216_scheduler(a_val: str):
            nonlocal combo_values_216_scheduler
            selected_index = combo_values_216_scheduler.index(a_val)
            comboboxtext_216_scheduler.set_active(selected_index)
        widget_getters[comboboxtext_216_scheduler.get_name()] = comboboxtext_216_scheduler.get_active_text  # noqa
        widget_setters[comboboxtext_216_scheduler.get_name()] = setter_216_scheduler  # noqa

        label_216_start_at_step: Gtk.Label = Gtk.Label.new("Start_At_Step")
        label_216_start_at_step.set_margin_start(8)
        label_216_start_at_step.set_alignment(0.95, 0)
        entry_216_start_at_step: Gtk.Entry = Gtk.Entry.new()
        entry_216_start_at_step.set_text(str(20))
        entry_216_start_at_step.set_name("entry_216_start_at_step")
        entry_216_start_at_step.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_216_start_at_step,
                           minimum=0, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_216_start_at_step(source, **args):  # noqa
            pass
        entry_216_start_at_step.connect(SIG_CHANGED, change_handler_216_start_at_step)

        def getter_216_start_at_step() -> int:
            return int(entry_216_start_at_step.get_text())

        def setter_216_start_at_step(a_val: int):
            entry_216_start_at_step.set_text(str(a_val))
        widget_getters[entry_216_start_at_step.get_name()] = getter_216_start_at_step  # noqa
        widget_setters[entry_216_start_at_step.get_name()] = setter_216_start_at_step  # noqa

        label_216_end_at_step: Gtk.Label = Gtk.Label.new("End_At_Step")
        label_216_end_at_step.set_margin_start(8)
        label_216_end_at_step.set_alignment(0.95, 0)
        entry_216_end_at_step: Gtk.Entry = Gtk.Entry.new()
        entry_216_end_at_step.set_text(str(1000))
        entry_216_end_at_step.set_name("entry_216_end_at_step")
        entry_216_end_at_step.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_216_end_at_step,
                           minimum=0, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_216_end_at_step(source, **args):  # noqa
            pass
        entry_216_end_at_step.connect(SIG_CHANGED, change_handler_216_end_at_step)

        def getter_216_end_at_step() -> int:
            return int(entry_216_end_at_step.get_text())

        def setter_216_end_at_step(a_val: int):
            entry_216_end_at_step.set_text(str(a_val))
        widget_getters[entry_216_end_at_step.get_name()] = getter_216_end_at_step  # noqa
        widget_setters[entry_216_end_at_step.get_name()] = setter_216_end_at_step  # noqa

        checkbutton_216_return_with_leftover_noise: Gtk.CheckButton = Gtk.CheckButton.new_with_label("Return With Leftover Noise")  # noqa
        checkbutton_216_return_with_leftover_noise.set_active(False)
        checkbutton_216_return_with_leftover_noise.set_name("checkbutton_216_return_with_leftover_noise")
        checkbutton_216_return_with_leftover_noise.set_hexpand(False)

        def toggled_handler_216_return_with_leftover_noise(source, **args):  # noqa
            pass
        checkbutton_216_return_with_leftover_noise.connect(SIG_TOGGLED, toggled_handler_216_return_with_leftover_noise)

        def getter_216_return_with_leftover_noise():
            return "enable" if checkbutton_216_return_with_leftover_noise.get_active() else "disable"
        widget_getters[checkbutton_216_return_with_leftover_noise.get_name()] = getter_216_return_with_leftover_noise  # noqa

        grid_216: Gtk.Grid = Gtk.Grid.new()
        grid_216.attach(checkbutton_216_add_noise,                  left=0, top=0, width=8, height=1)  # noqa
        grid_216.attach(label_216_noise_seed,                       left=0, top=1, width=1, height=1)  # noqa
        grid_216.attach(entry_216_noise_seed,                       left=1, top=1, width=7, height=1)  # noqa
        grid_216.attach(label_216_steps,                            left=0, top=2, width=1, height=1)  # noqa
        grid_216.attach(entry_216_steps,                            left=1, top=2, width=7, height=1)  # noqa
        grid_216.attach(label_216_cfg,                              left=0, top=3, width=1, height=1)  # noqa
        grid_216.attach(scale_216_cfg,                              left=1, top=3, width=7, height=1)  # noqa
        grid_216.attach(label_216_sampler_name,                     left=0, top=4, width=1, height=1)  # noqa
        grid_216.attach(comboboxtext_216_sampler_name,              left=1, top=4, width=7, height=1)  # noqa
        grid_216.attach(label_216_scheduler,                        left=0, top=5, width=1, height=1)  # noqa
        grid_216.attach(comboboxtext_216_scheduler,                 left=1, top=5, width=7, height=1)  # noqa
        grid_216.attach(label_216_start_at_step,                    left=0, top=6, width=1, height=1)  # noqa
        grid_216.attach(entry_216_start_at_step,                    left=1, top=6, width=3, height=1)  # noqa
        grid_216.attach(label_216_end_at_step,                      left=4, top=6, width=1, height=1)  # noqa
        grid_216.attach(entry_216_end_at_step,                      left=5, top=6, width=3, height=1)  # noqa
        grid_216.attach(checkbutton_216_return_with_leftover_noise, left=0, top=7, width=8, height=1)  # noqa
        grid_216.set_column_homogeneous(False)
        grid_216.set_row_homogeneous(False)
        frame_ksampleradvanced_216upscale_mixed_diff.add(widget=grid_216)  # noqa

        # New Frame
        frame_imageblend_221contrast_fix: Gtk.Frame = Gtk.Frame.new(label="Contrast Fix        #221")  # noqa
        frame_imageblend_221contrast_fix.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_221_blend_factor: Gtk.Label = Gtk.Label.new("Blend_Factor")
        label_221_blend_factor.set_margin_start(8)
        entry_221_blend_factor: Gtk.Entry = Gtk.Entry.new()
        entry_221_blend_factor.set_text(str(0.225))
        entry_221_blend_factor.set_name("entry_221_blend_factor")
        entry_221_blend_factor.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_221_blend_factor,
                           minimum=0, maximum=None,  # noqa
                           int_only=False,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_221_blend_factor(source, **args):  # noqa
            pass
        entry_221_blend_factor.connect(SIG_CHANGED, change_handler_221_blend_factor)

        def getter_221_blend_factor() -> float:
            return float(entry_221_blend_factor.get_text())

        def setter_221_blend_factor(a_val: float):
            entry_221_blend_factor.set_text(str(a_val))
        widget_getters[entry_221_blend_factor.get_name()] = getter_221_blend_factor  # noqa
        widget_setters[entry_221_blend_factor.get_name()] = setter_221_blend_factor  # noqa

        label_221_blend_mode: Gtk.Label = Gtk.Label.new("Blend_Mode")
        comboboxtext_221_blend_mode: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_221_blend_mode: list[str] = ["normal", "multiply", "screen", "overlay", "soft_light", "difference"]  # noqa
        for combo_item_path in combo_values_221_blend_mode:
            comboboxtext_221_blend_mode.append_text(combo_item_path)
        comboboxtext_221_blend_mode.set_name("comboboxtext_221_blend_mode")
        comboboxtext_221_blend_mode.set_hexpand(True)
        comboboxtext_221_blend_mode.set_active(3)

        def change_handler_221_blend_mode(source, **args):  # noqa
            pass
        comboboxtext_221_blend_mode.connect(SIG_CHANGED, change_handler_221_blend_mode)

        def setter_221_blend_mode(a_val: str):
            nonlocal combo_values_221_blend_mode
            selected_index = combo_values_221_blend_mode.index(a_val)
            comboboxtext_221_blend_mode.set_active(selected_index)
        widget_getters[comboboxtext_221_blend_mode.get_name()] = comboboxtext_221_blend_mode.get_active_text  # noqa
        widget_setters[comboboxtext_221_blend_mode.get_name()] = setter_221_blend_mode  # noqa

        grid_221: Gtk.Grid = Gtk.Grid.new()
        grid_221.attach(label_221_blend_factor,      left=0, top=0, width=1, height=1)  # noqa
        grid_221.attach(entry_221_blend_factor,      left=1, top=0, width=3, height=1)  # noqa
        grid_221.attach(label_221_blend_mode,        left=0, top=1, width=1, height=1)  # noqa
        grid_221.attach(comboboxtext_221_blend_mode, left=1, top=1, width=3, height=1)  # noqa
        grid_221.set_column_homogeneous(False)
        grid_221.set_row_homogeneous(False)
        frame_imageblend_221contrast_fix.add(widget=grid_221)  # noqa

        content_area: Gtk.Box = dialog.get_content_area()
        main_scrollable: Gtk.ScrolledWindow = Gtk.ScrolledWindow()
        subject_box: Gtk.Box = Gtk.Box()
        subject_box.set_orientation(Gtk.Orientation.VERTICAL)

        subject_box.pack_start(child=frame_checkpointloadersimple_004refiner_model, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_emptylatentimage_005image_resolution, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_checkpointloadersimple_010base_model, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_ksampleradvanced_022base_pass, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_ksampleradvanced_023refiner_pass, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_cliptextencodesdxl_075positive_base, expand=True, fill=True, padding=0)  # noqa
        subject_box.pack_start(child=frame_cliptextencodesdxlrefiner_081negative_refiner, expand=True, fill=True, padding=0)  # noqa
        subject_box.pack_start(child=frame_cliptextencodesdxl_082negative_base, expand=True, fill=True, padding=0)  # noqa
        subject_box.pack_start(child=frame_cliptextencodesdxlrefiner_120positive_refiner, expand=True, fill=True, padding=0)  # noqa
        subject_box.pack_start(child=frame_saveimage_184sytan_workflow, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_upscalemodelloader_187upscale_model, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_saveimage_2012048x_upscale, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_imagescaleby_215downscale, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_ksampleradvanced_216upscale_mixed_diff, expand=False, fill=False, padding=0)  # noqa
        subject_box.pack_start(child=frame_imageblend_221contrast_fix, expand=False, fill=False, padding=0)  # noqa

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
