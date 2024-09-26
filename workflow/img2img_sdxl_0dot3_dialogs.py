
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


class Img2ImgSdxl0Dot3Dialogs(WorkflowDialogFactory):

    WORKFLOW_FILE = "img2img_sdxl_0.3_workflow_api.json"

    def __init__(self, accessor: NodesAccessor):
        super().__init__(
            accessor=accessor,
            api_workflow=Img2ImgSdxl0Dot3Dialogs.WORKFLOW_FILE,
            dialog_config_chassis_name="Img2ImgSdxl0Dot3Dialogs_dialog_config",
            wf_data_chassis_name="Img2ImgSdxl0Dot3Dialogs_wf_data",
        )

    # Gimp is preventing subclassing GimpUI.Dialog by preventing access to the constructors. This might be accidental.
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
                                                     chassis_name="img2img_sdxl_0dot3_dialog",
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

        # New Frame
        frame_checkpointloadersimple_014load_checkpoint_base: Gtk.Frame = Gtk.Frame.new(label="Load Checkpoint Base")  # noqa
        frame_checkpointloadersimple_014load_checkpoint_base.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_14_ckpt_name: Gtk.Label = Gtk.Label.new("Ckpt_Name")
        comboboxtext_14_ckpt_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_14_ckpt_name: list[str] = get_models_filenames(
            model_type=ModelType.CHECKPOINTS,
            cu_origin=self.comfy_svr_origin)
        if combo_values_14_ckpt_name is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_14_ckpt_name:
            raise ValueError(fr"No models retrieved from ComfyUI")  # noqa
        for combo_item_path in combo_values_14_ckpt_name:
            comboboxtext_14_ckpt_name.append_text(combo_item_path)
        comboboxtext_14_ckpt_name.set_name("comboboxtext_14_ckpt_name")
        comboboxtext_14_ckpt_name.set_hexpand(True)
        comboboxtext_14_ckpt_name.set_active(12)

        def change_handler_14_ckpt_name(source, **args):  # noqa
            pass
        comboboxtext_14_ckpt_name.connect(SIG_CHANGED, change_handler_14_ckpt_name)

        def setter_14_ckpt_name(a_val: str):
            nonlocal combo_values_14_ckpt_name
            selected_index = combo_values_14_ckpt_name.index(a_val)
            comboboxtext_14_ckpt_name.set_active(selected_index)
        widget_getters[comboboxtext_14_ckpt_name.get_name()] = comboboxtext_14_ckpt_name.get_active_text
        widget_setters[comboboxtext_14_ckpt_name.get_name()] = setter_14_ckpt_name

        grid_14: Gtk.Grid = Gtk.Grid.new()
        grid_14.attach(label_14_ckpt_name,        left=0, top=0, width=1, height=1)  # noqa
        grid_14.attach(comboboxtext_14_ckpt_name, left=1, top=0, width=2, height=1)  # noqa
        grid_14.set_column_homogeneous(False)
        grid_14.set_row_homogeneous(False)
        frame_checkpointloadersimple_014load_checkpoint_base.add(widget=grid_14)  # noqa

        # New Frame
        frame_cliptextencodesdxl_016positivetextencodesdxl: Gtk.Frame = Gtk.Frame.new(label="PositiveTextEncodeSDXL")  # noqa
        frame_cliptextencodesdxl_016positivetextencodesdxl.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_16_width: Gtk.Label = Gtk.Label.new("Width")
        label_16_width.set_margin_start(8)
        label_16_width.set_alignment(0.95, 0)
        entry_16_width: Gtk.Entry = Gtk.Entry.new()
        entry_16_width.set_text(str(4096))
        entry_16_width.set_name("entry_16_width")
        entry_16_width.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_16_width,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_16_width(source, **args):  # noqa
            pass
        entry_16_width.connect(SIG_CHANGED, change_handler_16_width)

        def getter_16_width() -> int:
            return int(entry_16_width.get_text())

        def setter_16_width(a_val: int):
            entry_16_width.set_text(str(a_val))
        widget_getters[entry_16_width.get_name()] = getter_16_width
        widget_setters[entry_16_width.get_name()] = setter_16_width

        label_16_height: Gtk.Label = Gtk.Label.new("Height")
        label_16_height.set_margin_start(8)
        label_16_height.set_alignment(0.95, 0)
        entry_16_height: Gtk.Entry = Gtk.Entry.new()
        entry_16_height.set_text(str(4096))
        entry_16_height.set_name("entry_16_height")
        entry_16_height.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_16_height,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_16_height(source, **args):  # noqa
            pass
        entry_16_height.connect(SIG_CHANGED, change_handler_16_height)

        def getter_16_height() -> int:
            return int(entry_16_height.get_text())

        def setter_16_height(a_val: int):
            entry_16_height.set_text(str(a_val))
        widget_getters[entry_16_height.get_name()] = getter_16_height
        widget_setters[entry_16_height.get_name()] = setter_16_height

        label_16_crop_w: Gtk.Label = Gtk.Label.new("Crop_W")
        label_16_crop_w.set_margin_start(8)
        label_16_crop_w.set_alignment(0.95, 0)
        entry_16_crop_w: Gtk.Entry = Gtk.Entry.new()
        entry_16_crop_w.set_text(str(0))
        entry_16_crop_w.set_name("entry_16_crop_w")
        entry_16_crop_w.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_16_crop_w,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_16_crop_w(source, **args):  # noqa
            pass
        entry_16_crop_w.connect(SIG_CHANGED, change_handler_16_crop_w)

        def getter_16_crop_w() -> int:
            return int(entry_16_crop_w.get_text())

        def setter_16_crop_w(a_val: int):
            entry_16_crop_w.set_text(str(a_val))
        widget_getters[entry_16_crop_w.get_name()] = getter_16_crop_w
        widget_setters[entry_16_crop_w.get_name()] = setter_16_crop_w

        label_16_crop_h: Gtk.Label = Gtk.Label.new("Crop_H")
        label_16_crop_h.set_margin_start(8)
        label_16_crop_h.set_alignment(0.95, 0)
        entry_16_crop_h: Gtk.Entry = Gtk.Entry.new()
        entry_16_crop_h.set_text(str(0))
        entry_16_crop_h.set_name("entry_16_crop_h")
        entry_16_crop_h.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_16_crop_h,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_16_crop_h(source, **args):  # noqa
            pass
        entry_16_crop_h.connect(SIG_CHANGED, change_handler_16_crop_h)

        def getter_16_crop_h() -> int:
            return int(entry_16_crop_h.get_text())

        def setter_16_crop_h(a_val: int):
            entry_16_crop_h.set_text(str(a_val))
        widget_getters[entry_16_crop_h.get_name()] = getter_16_crop_h
        widget_setters[entry_16_crop_h.get_name()] = setter_16_crop_h

        label_16_target_width: Gtk.Label = Gtk.Label.new("Target_Width")
        label_16_target_width.set_margin_start(8)
        label_16_target_width.set_alignment(0.95, 0)
        entry_16_target_width: Gtk.Entry = Gtk.Entry.new()
        entry_16_target_width.set_text(str(4096))
        entry_16_target_width.set_name("entry_16_target_width")
        entry_16_target_width.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_16_target_width,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_16_target_width(source, **args):  # noqa
            pass
        entry_16_target_width.connect(SIG_CHANGED, change_handler_16_target_width)

        def getter_16_target_width() -> int:
            return int(entry_16_target_width.get_text())

        def setter_16_target_width(a_val: int):
            entry_16_target_width.set_text(str(a_val))
        widget_getters[entry_16_target_width.get_name()] = getter_16_target_width
        widget_setters[entry_16_target_width.get_name()] = setter_16_target_width

        label_16_target_height: Gtk.Label = Gtk.Label.new("Target_Height")
        label_16_target_height.set_margin_start(8)
        label_16_target_height.set_alignment(0.95, 0)
        entry_16_target_height: Gtk.Entry = Gtk.Entry.new()
        entry_16_target_height.set_text(str(4096))
        entry_16_target_height.set_name("entry_16_target_height")
        entry_16_target_height.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_16_target_height,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_16_target_height(source, **args):  # noqa
            pass
        entry_16_target_height.connect(SIG_CHANGED, change_handler_16_target_height)

        def getter_16_target_height() -> int:
            return int(entry_16_target_height.get_text())

        def setter_16_target_height(a_val: int):
            entry_16_target_height.set_text(str(a_val))
        widget_getters[entry_16_target_height.get_name()] = getter_16_target_height
        widget_setters[entry_16_target_height.get_name()] = setter_16_target_height

        label_16_text_g: Gtk.Label = Gtk.Label.new("Text_G")
        textview_16_text_g: Gtk.TextView = Gtk.TextView.new()
        textview_16_text_g.get_buffer().set_text("a fish man with fists and  clawed feet, wearing a tunic teal background standing on a white patch.  high resolution, highly detailed, 4k")  # noqa
        textview_16_text_g.set_name("textview_16_text_g")
        textview_16_text_g.set_hexpand(True)
        textview_16_text_g.set_vexpand(True)
        textview_16_text_g.set_valign(Gtk.Align.FILL)

        def preedit_handler_16_text_g(source, **args):  # noqa
            pass
        textview_16_text_g.connect(SIG_PREEDIT_CHANGED, preedit_handler_16_text_g)

        def getter_16_text_g():
            buffer: Gtk.TextBuffer = textview_16_text_g.get_buffer()
            start: Gtk.TextIter = buffer.get_start_iter()
            end: Gtk.TextIter = buffer.get_end_iter()
            return buffer.get_text(start, end, False)

        def setter_16_text_g(a_val: str):
            textview_16_text_g.get_buffer().set_text(str(a_val))

        widget_getters[textview_16_text_g.get_name()] = getter_16_text_g
        widget_setters[textview_16_text_g.get_name()] = setter_16_text_g

        label_16_text_l: Gtk.Label = Gtk.Label.new("Text_L")
        textview_16_text_l: Gtk.TextView = Gtk.TextView.new()
        textview_16_text_l.get_buffer().set_text("a fish man with fists and  clawed feet, wearing a tunic teal background standing on a white patch.  high resolution, highly detailed, 4k")  # noqa
        textview_16_text_l.set_name("textview_16_text_l")
        textview_16_text_l.set_hexpand(True)
        textview_16_text_l.set_vexpand(True)
        textview_16_text_l.set_valign(Gtk.Align.FILL)

        def preedit_handler_16_text_l(source, **args):  # noqa
            pass
        textview_16_text_l.connect(SIG_PREEDIT_CHANGED, preedit_handler_16_text_l)

        def getter_16_text_l():
            buffer: Gtk.TextBuffer = textview_16_text_l.get_buffer()
            start: Gtk.TextIter = buffer.get_start_iter()
            end: Gtk.TextIter = buffer.get_end_iter()
            return buffer.get_text(start, end, False)

        def setter_16_text_l(a_val: str):
            textview_16_text_l.get_buffer().set_text(str(a_val))

        widget_getters[textview_16_text_l.get_name()] = getter_16_text_l
        widget_setters[textview_16_text_l.get_name()] = setter_16_text_l

        grid_16: Gtk.Grid = Gtk.Grid.new()
        grid_16.attach(label_16_width,         left=0, top=0, width=1, height=1)  # noqa
        grid_16.attach(entry_16_width,         left=1, top=0, width=3, height=1)  # noqa
        grid_16.attach(label_16_height,        left=4, top=0, width=1, height=1)  # noqa
        grid_16.attach(entry_16_height,        left=5, top=0, width=3, height=1)  # noqa
        grid_16.attach(label_16_crop_w,        left=8, top=0, width=1, height=1)  # noqa
        grid_16.attach(entry_16_crop_w,        left=9, top=0, width=3, height=1)  # noqa
        grid_16.attach(label_16_crop_h,        left=12, top=0, width=1, height=1)  # noqa
        grid_16.attach(entry_16_crop_h,        left=13, top=0, width=3, height=1)  # noqa
        grid_16.attach(label_16_target_width,  left=16, top=0, width=1, height=1)  # noqa
        grid_16.attach(entry_16_target_width,  left=17, top=0, width=3, height=1)  # noqa
        grid_16.attach(label_16_target_height, left=20, top=0, width=1, height=1)  # noqa
        grid_16.attach(entry_16_target_height, left=21, top=0, width=3, height=1)  # noqa
        grid_16.attach(label_16_text_g,        left=0, top=1, width=1, height=1)  # noqa
        grid_16.attach(textview_16_text_g,     left=1, top=1, width=23, height=1)  # noqa
        grid_16.attach(label_16_text_l,        left=0, top=2, width=1, height=1)  # noqa
        grid_16.attach(textview_16_text_l,     left=1, top=2, width=23, height=1)  # noqa
        grid_16.set_column_homogeneous(False)
        grid_16.set_row_homogeneous(False)
        frame_cliptextencodesdxl_016positivetextencodesdxl.add(widget=grid_16)  # noqa

        # New Frame
        frame_cliptextencodesdxl_019negativetextencodesdxl: Gtk.Frame = Gtk.Frame.new(label="NegativeTextEncodeSDXL")  # noqa
        frame_cliptextencodesdxl_019negativetextencodesdxl.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_19_width: Gtk.Label = Gtk.Label.new("Width")
        label_19_width.set_margin_start(8)
        label_19_width.set_alignment(0.95, 0)
        entry_19_width: Gtk.Entry = Gtk.Entry.new()
        entry_19_width.set_text(str(4096))
        entry_19_width.set_name("entry_19_width")
        entry_19_width.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_19_width,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_19_width(source, **args):  # noqa
            pass
        entry_19_width.connect(SIG_CHANGED, change_handler_19_width)

        def getter_19_width() -> int:
            return int(entry_19_width.get_text())

        def setter_19_width(a_val: int):
            entry_19_width.set_text(str(a_val))
        widget_getters[entry_19_width.get_name()] = getter_19_width
        widget_setters[entry_19_width.get_name()] = setter_19_width

        label_19_height: Gtk.Label = Gtk.Label.new("Height")
        label_19_height.set_margin_start(8)
        label_19_height.set_alignment(0.95, 0)
        entry_19_height: Gtk.Entry = Gtk.Entry.new()
        entry_19_height.set_text(str(4096))
        entry_19_height.set_name("entry_19_height")
        entry_19_height.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_19_height,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_19_height(source, **args):  # noqa
            pass
        entry_19_height.connect(SIG_CHANGED, change_handler_19_height)

        def getter_19_height() -> int:
            return int(entry_19_height.get_text())

        def setter_19_height(a_val: int):
            entry_19_height.set_text(str(a_val))
        widget_getters[entry_19_height.get_name()] = getter_19_height
        widget_setters[entry_19_height.get_name()] = setter_19_height

        label_19_crop_w: Gtk.Label = Gtk.Label.new("Crop_W")
        label_19_crop_w.set_margin_start(8)
        label_19_crop_w.set_alignment(0.95, 0)
        entry_19_crop_w: Gtk.Entry = Gtk.Entry.new()
        entry_19_crop_w.set_text(str(0))
        entry_19_crop_w.set_name("entry_19_crop_w")
        entry_19_crop_w.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_19_crop_w,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_19_crop_w(source, **args):  # noqa
            pass
        entry_19_crop_w.connect(SIG_CHANGED, change_handler_19_crop_w)

        def getter_19_crop_w() -> int:
            return int(entry_19_crop_w.get_text())

        def setter_19_crop_w(a_val: int):
            entry_19_crop_w.set_text(str(a_val))
        widget_getters[entry_19_crop_w.get_name()] = getter_19_crop_w
        widget_setters[entry_19_crop_w.get_name()] = setter_19_crop_w

        label_19_crop_h: Gtk.Label = Gtk.Label.new("Crop_H")
        label_19_crop_h.set_margin_start(8)
        label_19_crop_h.set_alignment(0.95, 0)
        entry_19_crop_h: Gtk.Entry = Gtk.Entry.new()
        entry_19_crop_h.set_text(str(0))
        entry_19_crop_h.set_name("entry_19_crop_h")
        entry_19_crop_h.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_19_crop_h,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_19_crop_h(source, **args):  # noqa
            pass
        entry_19_crop_h.connect(SIG_CHANGED, change_handler_19_crop_h)

        def getter_19_crop_h() -> int:
            return int(entry_19_crop_h.get_text())

        def setter_19_crop_h(a_val: int):
            entry_19_crop_h.set_text(str(a_val))
        widget_getters[entry_19_crop_h.get_name()] = getter_19_crop_h
        widget_setters[entry_19_crop_h.get_name()] = setter_19_crop_h

        label_19_target_width: Gtk.Label = Gtk.Label.new("Target_Width")
        label_19_target_width.set_margin_start(8)
        label_19_target_width.set_alignment(0.95, 0)
        entry_19_target_width: Gtk.Entry = Gtk.Entry.new()
        entry_19_target_width.set_text(str(4096))
        entry_19_target_width.set_name("entry_19_target_width")
        entry_19_target_width.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_19_target_width,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_19_target_width(source, **args):  # noqa
            pass
        entry_19_target_width.connect(SIG_CHANGED, change_handler_19_target_width)

        def getter_19_target_width() -> int:
            return int(entry_19_target_width.get_text())

        def setter_19_target_width(a_val: int):
            entry_19_target_width.set_text(str(a_val))
        widget_getters[entry_19_target_width.get_name()] = getter_19_target_width
        widget_setters[entry_19_target_width.get_name()] = setter_19_target_width

        label_19_target_height: Gtk.Label = Gtk.Label.new("Target_Height")
        label_19_target_height.set_margin_start(8)
        label_19_target_height.set_alignment(0.95, 0)
        entry_19_target_height: Gtk.Entry = Gtk.Entry.new()
        entry_19_target_height.set_text(str(4096))
        entry_19_target_height.set_name("entry_19_target_height")
        entry_19_target_height.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_19_target_height,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_19_target_height(source, **args):  # noqa
            pass
        entry_19_target_height.connect(SIG_CHANGED, change_handler_19_target_height)

        def getter_19_target_height() -> int:
            return int(entry_19_target_height.get_text())

        def setter_19_target_height(a_val: int):
            entry_19_target_height.set_text(str(a_val))
        widget_getters[entry_19_target_height.get_name()] = getter_19_target_height
        widget_setters[entry_19_target_height.get_name()] = setter_19_target_height

        label_19_text_g: Gtk.Label = Gtk.Label.new("Text_G")
        textview_19_text_g: Gtk.TextView = Gtk.TextView.new()
        textview_19_text_g.get_buffer().set_text("blurry, rendering, illustration, drawing, painting")  # noqa
        textview_19_text_g.set_name("textview_19_text_g")
        textview_19_text_g.set_hexpand(True)
        textview_19_text_g.set_vexpand(True)
        textview_19_text_g.set_valign(Gtk.Align.FILL)

        def preedit_handler_19_text_g(source, **args):  # noqa
            pass
        textview_19_text_g.connect(SIG_PREEDIT_CHANGED, preedit_handler_19_text_g)

        def getter_19_text_g():
            buffer: Gtk.TextBuffer = textview_19_text_g.get_buffer()
            start: Gtk.TextIter = buffer.get_start_iter()
            end: Gtk.TextIter = buffer.get_end_iter()
            return buffer.get_text(start, end, False)

        def setter_19_text_g(a_val: str):
            textview_19_text_g.get_buffer().set_text(str(a_val))

        widget_getters[textview_19_text_g.get_name()] = getter_19_text_g
        widget_setters[textview_19_text_g.get_name()] = setter_19_text_g

        label_19_text_l: Gtk.Label = Gtk.Label.new("Text_L")
        textview_19_text_l: Gtk.TextView = Gtk.TextView.new()
        textview_19_text_l.get_buffer().set_text("blurry, rendering, illustration, drawing, painting")  # noqa
        textview_19_text_l.set_name("textview_19_text_l")
        textview_19_text_l.set_hexpand(True)
        textview_19_text_l.set_vexpand(True)
        textview_19_text_l.set_valign(Gtk.Align.FILL)

        def preedit_handler_19_text_l(source, **args):  # noqa
            pass
        textview_19_text_l.connect(SIG_PREEDIT_CHANGED, preedit_handler_19_text_l)

        def getter_19_text_l():
            buffer: Gtk.TextBuffer = textview_19_text_l.get_buffer()
            start: Gtk.TextIter = buffer.get_start_iter()
            end: Gtk.TextIter = buffer.get_end_iter()
            return buffer.get_text(start, end, False)

        def setter_19_text_l(a_val: str):
            textview_19_text_l.get_buffer().set_text(str(a_val))

        widget_getters[textview_19_text_l.get_name()] = getter_19_text_l
        widget_setters[textview_19_text_l.get_name()] = setter_19_text_l

        grid_19: Gtk.Grid = Gtk.Grid.new()
        grid_19.attach(label_19_width,         left=0, top=0, width=1, height=1)  # noqa
        grid_19.attach(entry_19_width,         left=1, top=0, width=3, height=1)  # noqa
        grid_19.attach(label_19_height,        left=4, top=0, width=1, height=1)  # noqa
        grid_19.attach(entry_19_height,        left=5, top=0, width=3, height=1)  # noqa
        grid_19.attach(label_19_crop_w,        left=8, top=0, width=1, height=1)  # noqa
        grid_19.attach(entry_19_crop_w,        left=9, top=0, width=3, height=1)  # noqa
        grid_19.attach(label_19_crop_h,        left=12, top=0, width=1, height=1)  # noqa
        grid_19.attach(entry_19_crop_h,        left=13, top=0, width=3, height=1)  # noqa
        grid_19.attach(label_19_target_width,  left=16, top=0, width=1, height=1)  # noqa
        grid_19.attach(entry_19_target_width,  left=17, top=0, width=3, height=1)  # noqa
        grid_19.attach(label_19_target_height, left=20, top=0, width=1, height=1)  # noqa
        grid_19.attach(entry_19_target_height, left=21, top=0, width=3, height=1)  # noqa
        grid_19.attach(label_19_text_g,        left=0, top=1, width=1, height=1)  # noqa
        grid_19.attach(textview_19_text_g,     left=1, top=1, width=23, height=1)  # noqa
        grid_19.attach(label_19_text_l,        left=0, top=2, width=1, height=1)  # noqa
        grid_19.attach(textview_19_text_l,     left=1, top=2, width=23, height=1)  # noqa
        grid_19.set_column_homogeneous(False)
        grid_19.set_row_homogeneous(False)
        frame_cliptextencodesdxl_019negativetextencodesdxl.add(widget=grid_19)  # noqa

        # New Frame
        frame_ksampler_036ksampler: Gtk.Frame = Gtk.Frame.new(label="KSampler")  # noqa
        frame_ksampler_036ksampler.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_36_seed: Gtk.Label = Gtk.Label.new("Seed")
        label_36_seed.set_margin_start(8)
        label_36_seed.set_alignment(0.95, 0)
        entry_36_seed: Gtk.Entry = Gtk.Entry.new()
        entry_36_seed.set_text(str(906619873857830))
        entry_36_seed.set_name("entry_36_seed")
        entry_36_seed.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_36_seed,
                           minimum=-1, maximum=18446744073709519872,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_36_seed(source, **args):  # noqa
            pass
        entry_36_seed.connect(SIG_CHANGED, change_handler_36_seed)

        def getter_36_seed() -> int:
            return int(entry_36_seed.get_text())

        def setter_36_seed(a_val: int):
            entry_36_seed.set_text(str(a_val))
        widget_getters[entry_36_seed.get_name()] = getter_36_seed
        widget_setters[entry_36_seed.get_name()] = setter_36_seed

        label_36_steps: Gtk.Label = Gtk.Label.new("Steps")
        label_36_steps.set_margin_start(8)
        label_36_steps.set_alignment(0.95, 0)
        entry_36_steps: Gtk.Entry = Gtk.Entry.new()
        entry_36_steps.set_text(str(20))
        entry_36_steps.set_name("entry_36_steps")
        entry_36_steps.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_36_steps,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_36_steps(source, **args):  # noqa
            pass
        entry_36_steps.connect(SIG_CHANGED, change_handler_36_steps)

        def getter_36_steps() -> int:
            return int(entry_36_steps.get_text())

        def setter_36_steps(a_val: int):
            entry_36_steps.set_text(str(a_val))
        widget_getters[entry_36_steps.get_name()] = getter_36_steps
        widget_setters[entry_36_steps.get_name()] = setter_36_steps

        label_36_cfg: Gtk.Label = Gtk.Label.new("Cfg")
        label_36_cfg.set_margin_start(8)
        adjustment_36_cfg: Gtk.Adjustment = Gtk.Adjustment(value=5.50000,
                                                           lower=1.00000,
                                                           upper=25.00000,
                                                           step_increment=0.100,
                                                           page_increment=2.000,
                                                           page_size=0)
        scale_36_cfg: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_36_cfg)  # noqa
        scale_36_cfg.set_name("scale_36_cfg")
        scale_36_cfg.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_36_cfg.set_hexpand(True)

        def change_handler_36_cfg(source, **args):  # noqa
            pass
        scale_36_cfg.connect(SIG_VALUE_CHANGED, change_handler_36_cfg)
        widget_getters[scale_36_cfg.get_name()] = scale_36_cfg.get_value
        widget_setters[scale_36_cfg.get_name()] = scale_36_cfg.set_value

        label_36_sampler_name: Gtk.Label = Gtk.Label.new("Sampler_Name")
        comboboxtext_36_sampler_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_36_sampler_name: list[str] = ["euler", "euler_ancestral", "heun", "heunpp2", "dpm_2", "dpm_2_ancestral", "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_sde", "dpmpp_sde_gpu", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu", "ddpm", "lcm", "ddim", "uni_pc", "uni_pc_bh2"]  # noqa
        for combo_item_path in combo_values_36_sampler_name:
            comboboxtext_36_sampler_name.append_text(combo_item_path)
        comboboxtext_36_sampler_name.set_name("comboboxtext_36_sampler_name")
        comboboxtext_36_sampler_name.set_hexpand(True)
        comboboxtext_36_sampler_name.set_active(14)

        def change_handler_36_sampler_name(source, **args):  # noqa
            pass
        comboboxtext_36_sampler_name.connect(SIG_CHANGED, change_handler_36_sampler_name)

        def setter_36_sampler_name(a_val: str):
            nonlocal combo_values_36_sampler_name
            selected_index = combo_values_36_sampler_name.index(a_val)
            comboboxtext_36_sampler_name.set_active(selected_index)
        widget_getters[comboboxtext_36_sampler_name.get_name()] = comboboxtext_36_sampler_name.get_active_text
        widget_setters[comboboxtext_36_sampler_name.get_name()] = setter_36_sampler_name

        label_36_scheduler: Gtk.Label = Gtk.Label.new("Scheduler")
        comboboxtext_36_scheduler: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_36_scheduler: list[str] = ["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"]  # noqa
        for combo_item_path in combo_values_36_scheduler:
            comboboxtext_36_scheduler.append_text(combo_item_path)
        comboboxtext_36_scheduler.set_name("comboboxtext_36_scheduler")
        comboboxtext_36_scheduler.set_hexpand(True)
        comboboxtext_36_scheduler.set_active(2)

        def change_handler_36_scheduler(source, **args):  # noqa
            pass
        comboboxtext_36_scheduler.connect(SIG_CHANGED, change_handler_36_scheduler)

        def setter_36_scheduler(a_val: str):
            nonlocal combo_values_36_scheduler
            selected_index = combo_values_36_scheduler.index(a_val)
            comboboxtext_36_scheduler.set_active(selected_index)
        widget_getters[comboboxtext_36_scheduler.get_name()] = comboboxtext_36_scheduler.get_active_text
        widget_setters[comboboxtext_36_scheduler.get_name()] = setter_36_scheduler

        label_36_denoise: Gtk.Label = Gtk.Label.new("Denoise")
        label_36_denoise.set_margin_start(8)
        adjustment_36_denoise: Gtk.Adjustment = Gtk.Adjustment(value=0.75000,
                                                               lower=0.00000,
                                                               upper=1.00000,
                                                               step_increment=0.001,
                                                               page_increment=0.010,
                                                               page_size=0)
        scale_36_denoise: Gtk.Scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_36_denoise)  # noqa
        scale_36_denoise.set_name("scale_36_denoise")
        scale_36_denoise.set_digits(3)
        scale_36_denoise.set_value_pos(Gtk.PositionType.BOTTOM)
        scale_36_denoise.set_hexpand(True)

        def change_handler_36_denoise(source, **args):  # noqa
            pass
        scale_36_denoise.connect(SIG_VALUE_CHANGED, change_handler_36_denoise)
        widget_getters[scale_36_denoise.get_name()] = scale_36_denoise.get_value
        widget_setters[scale_36_denoise.get_name()] = scale_36_denoise.set_value

        grid_36: Gtk.Grid = Gtk.Grid.new()
        grid_36.attach(label_36_seed,                left=0, top=0, width=1, height=1)  # noqa
        grid_36.attach(entry_36_seed,                left=1, top=0, width=3, height=1)  # noqa
        grid_36.attach(label_36_steps,               left=4, top=0, width=1, height=1)  # noqa
        grid_36.attach(entry_36_steps,               left=5, top=0, width=3, height=1)  # noqa
        grid_36.attach(label_36_cfg,                 left=0, top=1, width=1, height=1)  # noqa
        grid_36.attach(scale_36_cfg,                 left=1, top=1, width=7, height=1)  # noqa
        grid_36.attach(label_36_sampler_name,        left=0, top=2, width=1, height=1)  # noqa
        grid_36.attach(comboboxtext_36_sampler_name, left=1, top=2, width=7, height=1)  # noqa
        grid_36.attach(label_36_scheduler,           left=0, top=3, width=1, height=1)  # noqa
        grid_36.attach(comboboxtext_36_scheduler,    left=1, top=3, width=7, height=1)  # noqa
        grid_36.attach(label_36_denoise,             left=0, top=4, width=1, height=1)  # noqa
        grid_36.attach(scale_36_denoise,             left=1, top=4, width=7, height=1)  # noqa
        grid_36.set_column_homogeneous(False)
        grid_36.set_row_homogeneous(False)
        frame_ksampler_036ksampler.add(widget=grid_36)  # noqa

        # New Frame
        frame_vaeloader_037load_vae: Gtk.Frame = Gtk.Frame.new(label="Load VAE")  # noqa
        frame_vaeloader_037load_vae.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_37_vae_name: Gtk.Label = Gtk.Label.new("Vae_Name")
        comboboxtext_37_vae_name: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_37_vae_name: list[str] = get_models_filenames(
            model_type=ModelType.VAE,
            cu_origin=self.comfy_svr_origin)
        if combo_values_37_vae_name is None:
            raise SystemError(f"get_models_filenames() returned None.")
        if not combo_values_37_vae_name:
            raise ValueError(fr"No models retrieved from ComfyUI")  # noqa
        for combo_item_path in combo_values_37_vae_name:
            comboboxtext_37_vae_name.append_text(combo_item_path)
        comboboxtext_37_vae_name.set_name("comboboxtext_37_vae_name")
        comboboxtext_37_vae_name.set_hexpand(True)
        comboboxtext_37_vae_name.set_active(0)

        def change_handler_37_vae_name(source, **args):  # noqa
            pass
        comboboxtext_37_vae_name.connect(SIG_CHANGED, change_handler_37_vae_name)

        def setter_37_vae_name(a_val: str):
            nonlocal combo_values_37_vae_name
            selected_index = combo_values_37_vae_name.index(a_val)
            comboboxtext_37_vae_name.set_active(selected_index)
        widget_getters[comboboxtext_37_vae_name.get_name()] = comboboxtext_37_vae_name.get_active_text
        widget_setters[comboboxtext_37_vae_name.get_name()] = setter_37_vae_name

        grid_37: Gtk.Grid = Gtk.Grid.new()
        grid_37.attach(label_37_vae_name,        left=0, top=0, width=1, height=1)  # noqa
        grid_37.attach(comboboxtext_37_vae_name, left=1, top=0, width=2, height=1)  # noqa
        grid_37.set_column_homogeneous(False)
        grid_37.set_row_homogeneous(False)
        frame_vaeloader_037load_vae.add(widget=grid_37)  # noqa

        # New Frame
        frame_loadimage_038load_image: Gtk.Frame = Gtk.Frame.new(label="Load Image: (select layer)")  # noqa
        frame_loadimage_038load_image.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_38_image: Gtk.Label = Gtk.Label.new("Layer")
        treeview_38_image: LayerTreeView = LayerTreeView()
        treeview_38_image.set_name("treeview_38_image")
        treeview_38_image.set_hexpand(True)
        prev_selected_route = self._installation_persister.configuration.get('treeview_38_image_selection_route', None)
        if prev_selected_route is not None:
            treeview_38_image.select_path = ids_to_treepath(model=treeview_38_image.get_model(),
                                                            image_id=prev_selected_route[0],
                                                            layer_id=prev_selected_route[1])

        def selection_handler_38_image(selection: Gtk.TreeSelection):
            model, treeiter = selection.get_selected()
            if treeiter is not None:
                sel_path: Gtk.TreePath = model.get_path(treeiter)
                sel_route: tuple[int, int] = treepath_to_ids(model=model, layer_path=sel_path)
                self._installation_persister.update_config({'treeview_38_image_selection_route': sel_route})
                self._installation_persister.store_config()

        treeview_38_image.get_selection().connect("changed", selection_handler_38_image)
        widget_getters[treeview_38_image.get_name()] = treeview_38_image.get_selected_png_leaf

        grid_38: Gtk.Grid = Gtk.Grid.new()
        grid_38.attach(label_38_image,    left=0, top=0, width=1, height=1)  # noqa
        grid_38.attach(treeview_38_image, left=1, top=0, width=2, height=1)  # noqa
        grid_38.set_column_homogeneous(False)
        grid_38.set_row_homogeneous(False)
        frame_loadimage_038load_image.add(widget=grid_38)  # noqa

        # New Frame
        frame_vaeencode_039vae_encode: Gtk.Frame = Gtk.Frame.new(label="VAE Encode")  # noqa
        frame_vaeencode_039vae_encode.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        grid_39: Gtk.Grid = Gtk.Grid.new()
        grid_39.set_column_homogeneous(False)
        grid_39.set_row_homogeneous(False)
        frame_vaeencode_039vae_encode.add(widget=grid_39)  # noqa

        # New Frame
        frame_imagescale_040upscale_image: Gtk.Frame = Gtk.Frame.new(label="Upscale Image")  # noqa
        frame_imagescale_040upscale_image.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)  # noqa
        label_40_upscale_method: Gtk.Label = Gtk.Label.new("Upscale_Method")
        comboboxtext_40_upscale_method: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_40_upscale_method: list[str] = ["nearest-exact", "bilinear", "area", "bicubic", "lanczos"]  # noqa
        for combo_item_path in combo_values_40_upscale_method:
            comboboxtext_40_upscale_method.append_text(combo_item_path)
        comboboxtext_40_upscale_method.set_name("comboboxtext_40_upscale_method")
        comboboxtext_40_upscale_method.set_hexpand(True)
        comboboxtext_40_upscale_method.set_active(0)

        def change_handler_40_upscale_method(source, **args):  # noqa
            pass
        comboboxtext_40_upscale_method.connect(SIG_CHANGED, change_handler_40_upscale_method)

        def setter_40_upscale_method(a_val: str):
            nonlocal combo_values_40_upscale_method
            selected_index = combo_values_40_upscale_method.index(a_val)
            comboboxtext_40_upscale_method.set_active(selected_index)
        widget_getters[comboboxtext_40_upscale_method.get_name()] = comboboxtext_40_upscale_method.get_active_text
        widget_setters[comboboxtext_40_upscale_method.get_name()] = setter_40_upscale_method

        label_40_width: Gtk.Label = Gtk.Label.new("Width")
        label_40_width.set_margin_start(8)
        label_40_width.set_alignment(0.95, 0)
        entry_40_width: Gtk.Entry = Gtk.Entry.new()
        entry_40_width.set_text(str(1024))
        entry_40_width.set_name("entry_40_width")
        entry_40_width.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_40_width,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_40_width(source, **args):  # noqa
            pass
        entry_40_width.connect(SIG_CHANGED, change_handler_40_width)

        def getter_40_width() -> int:
            return int(entry_40_width.get_text())

        def setter_40_width(a_val: int):
            entry_40_width.set_text(str(a_val))
        widget_getters[entry_40_width.get_name()] = getter_40_width
        widget_setters[entry_40_width.get_name()] = setter_40_width

        label_40_height: Gtk.Label = Gtk.Label.new("Height")
        label_40_height.set_margin_start(8)
        label_40_height.set_alignment(0.95, 0)
        entry_40_height: Gtk.Entry = Gtk.Entry.new()
        entry_40_height.set_text(str(1024))
        entry_40_height.set_name("entry_40_height")
        entry_40_height.set_hexpand(True)
        validate_in_bounds(entry_widget=entry_40_height,
                           minimum=1, maximum=None,  # noqa
                           int_only=True,
                           track_invalid_widgets=track_invalid_widgets)

        def change_handler_40_height(source, **args):  # noqa
            pass
        entry_40_height.connect(SIG_CHANGED, change_handler_40_height)

        def getter_40_height() -> int:
            return int(entry_40_height.get_text())

        def setter_40_height(a_val: int):
            entry_40_height.set_text(str(a_val))
        widget_getters[entry_40_height.get_name()] = getter_40_height
        widget_setters[entry_40_height.get_name()] = setter_40_height

        label_40_crop: Gtk.Label = Gtk.Label.new("Crop")
        comboboxtext_40_crop: Gtk.ComboBoxText = Gtk.ComboBoxText.new()
        combo_values_40_crop: list[str] = ["disabled", "center"]  # noqa
        for combo_item_path in combo_values_40_crop:
            comboboxtext_40_crop.append_text(combo_item_path)
        comboboxtext_40_crop.set_name("comboboxtext_40_crop")
        comboboxtext_40_crop.set_hexpand(True)
        comboboxtext_40_crop.set_active(1)

        def change_handler_40_crop(source, **args):  # noqa
            pass
        comboboxtext_40_crop.connect(SIG_CHANGED, change_handler_40_crop)

        def setter_40_crop(a_val: str):
            nonlocal combo_values_40_crop
            selected_index = combo_values_40_crop.index(a_val)
            comboboxtext_40_crop.set_active(selected_index)
        widget_getters[comboboxtext_40_crop.get_name()] = comboboxtext_40_crop.get_active_text
        widget_setters[comboboxtext_40_crop.get_name()] = setter_40_crop

        grid_40: Gtk.Grid = Gtk.Grid.new()
        grid_40.attach(label_40_upscale_method,        left=0, top=0, width=1, height=1)  # noqa
        grid_40.attach(comboboxtext_40_upscale_method, left=1, top=0, width=2, height=1)  # noqa
        grid_40.attach(label_40_width,                 left=0, top=1, width=1, height=1)  # noqa
        grid_40.attach(entry_40_width,                 left=1, top=1, width=3, height=1)  # noqa
        grid_40.attach(label_40_height,                left=4, top=1, width=1, height=1)  # noqa
        grid_40.attach(entry_40_height,                left=5, top=1, width=3, height=1)  # noqa
        grid_40.attach(label_40_crop,                  left=8, top=1, width=1, height=1)  # noqa
        grid_40.attach(comboboxtext_40_crop,           left=9, top=1, width=3, height=1)  # noqa
        grid_40.set_column_homogeneous(False)
        grid_40.set_row_homogeneous(False)
        frame_imagescale_040upscale_image.add(widget=grid_40)  # noqa
        content_area: Gtk.Box = dialog.get_content_area()
        content_area.pack_start(child=frame_vaedecode_008vae_decode, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_saveimage_009save_image, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_checkpointloadersimple_014load_checkpoint_base, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_cliptextencodesdxl_016positivetextencodesdxl, expand=True, fill=True, padding=0)  # noqa
        content_area.pack_start(child=frame_cliptextencodesdxl_019negativetextencodesdxl, expand=True, fill=True, padding=0)  # noqa
        content_area.pack_start(child=frame_ksampler_036ksampler, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_vaeloader_037load_vae, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_loadimage_038load_image, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_vaeencode_039vae_encode, expand=False, fill=False, padding=0)  # noqa
        content_area.pack_start(child=frame_imagescale_040upscale_image, expand=False, fill=False, padding=0)  # noqa

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
