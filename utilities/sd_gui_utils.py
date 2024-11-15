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

import gi
import pprint
import random
import re
import site
import sys
import threading
import time

gi.require_version('Gimp', '3.0')  # noqa: E402
gi.require_version('GimpUi', '3.0')  # noqa: E402
gi.require_version("Gtk", "3.0")  # noqa: E402
gi.require_version('Gdk', '3.0')  # noqa: E402
# noinspection PyUnresolvedReferences
from gi.repository import Gdk, Gio, Gimp, GimpUi, Gtk, GLib, GObject
from urllib import request
from utilities.cui_resources_utils import ModelType, get_models_list
from utilities.long_term_storage_utils import *
from utilities.type_utils import *

# Constants
LOGGER_FORMAT_SDGUIU = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
LOGGER_SDGUIU = logging.getLogger("sd_gui_utils")
REGEX_IDX_N_INPUT = r"([a-zA-z]+)_([0-9]+)_(.+)"
REGEX_STR_INT = r"^[-+]?[0-9]+$"
SIG_CHANGED = 'changed'
SIG_PREEDIT_CHANGED = "preedit-changed"
SIG_TOGGLED = 'toggled'
SIG_TXT_INSERT = 'insert-text'
SIG_VALUE_CHANGED = 'value-changed'
WIDGET_ENTRY_DEFAULT_NAME = 'GtkEntry'
WIDGET_NAME_DEFAULTS: List[str] = [WIDGET_ENTRY_DEFAULT_NAME]


class SubjectType(Enum):
    ANYTHING = auto()
    CHANNEL = auto()
    DRAWABLE = auto()
    IMAGE = auto()
    LAYER = auto()
    LAYER_MASK = auto()
    SELECTION = auto()
    TEXT_LAYER = auto()


# Global functions

def append_all_texts(combo_box: Gtk.ComboBoxText, items: List[str]) -> Gtk.ComboBoxText:
    for item in items:
        combo_box.append_text(item)
    return combo_box


def assets_dir_path():
    script_filename = os.path.realpath(__file__)
    script_dir_path = os.path.dirname(script_filename)
    return os.path.join(script_dir_path, "../assets")


def asset_path(asset_name: str):
    return os.path.join(assets_dir_path(), asset_name)


def close_window_of_widget(source: Gtk.Widget):
    da_top = Gtk.Widget.get_toplevel(source)  # noqa
    Gtk.Window.close(da_top)
    da_top.destroy()


def config_combobox_dict_int_str(combo_box: Gtk.ComboBox, dictionary: Dict[str, int], default_value: str):
    config_combobox_dict_str_int(combo_box, reciprocal_dict(dictionary), default_value)


def config_combobox_dict_str_int(combo_box: Gtk.ComboBox, dictionary: Dict[str, int], default_value: str):
    list_store: Gtk.ListStore = Gtk.ListStore.new(types=[int, str])  # noqa n_columns unfilled
    for key, value in dictionary.items():
        row = [value, key]  # Deliberately inverted
        if key:
            if value is not None:
                list_store.append(row)
            else:
                raise ValueError("Missing value in dictionary for " + key)
        else:
            raise ValueError("Missing key in dictionary")
    index: int = dictionary[default_value]
    if index < 0:
        raise ValueError("Could not find \"%s\" in dictionary" % default_value)
    config_combobox_liststore(combo_box, list_store, index)


def config_combobox_liststore(combo_box: Gtk.ComboBox, list_store: Gtk.ListStore, index: int):
    combo_box.set_model(list_store)
    combo_box.set_active(index)
    cell_renderer_text = Gtk.CellRendererText()
    combo_box.pack_start(cell_renderer_text, True)
    combo_box.add_attribute(cell_renderer_text, "text", 1)


def filt_check_buttons(widgets: List[Gtk.Widget]) -> List[Gtk.ComboBox]:
    return filt_widg(Gtk.CheckButton, widgets)  # noqa


def filt_combo_box_texts(widgets: List[Gtk.Widget]) -> List[Gtk.ComboBoxText]:
    return filt_widg(Gtk.ComboBoxText, widgets)  # noqa


def filt_combo_boxes(widgets: List[Gtk.Widget]) -> List[Gtk.ComboBox]:
    return filt_widg(Gtk.ComboBox, widgets)  # noqa


def filt_entries(widgets: List[Gtk.Widget]) -> List[Gtk.Entry]:
    return filt_widg(Gtk.Entry, widgets)  # noqa


def filt_radio_buttons(widgets: List[Gtk.Widget]) -> List[Gtk.ComboBox]:
    return filt_widg(Gtk.RadioButton, widgets)  # noqa


def filt_scales(widgets: List[Gtk.Widget]) -> List[Gtk.Scale]:
    return filt_widg(Gtk.Scale, widgets)  # noqa


def filt_text_views(widgets: List[Gtk.Widget]) -> List[Gtk.TextView]:
    return filt_widg(Gtk.TextView, widgets)  # noqa


def filt_toggle_buttons(widgets: List[Gtk.Widget]) -> List[Gtk.ComboBox]:
    return filt_widg(Gtk.ToggleButton, widgets)  # noqa


def filt_widg(widget_type: type, widgets: List[Gtk.Widget]) -> List[Gtk.Widget]:
    if widget_type is None:
        raise ValueError("widget_type cannot be None")

    if widgets is None:
        raise ValueError("widgets list cannot be None")

    if not widgets:
        return []

    def widg_pred(subject) -> bool:
        # type_actual = type(subject)
        it_is = isinstance(subject, widget_type)
        # message = "%s is a %s %s" % (type_actual.__name__, widget_type.__name__, str(it_is))
        # print(message)
        return it_is

    return list(filter(widg_pred, widgets))


def find_all_widgets(widget: Gtk.Widget) -> List[Gtk.Widget]:
    contained: List[Gtk.Widget] = []
    if hasattr(widget, 'get_child') and callable(getattr(widget, 'get_child')):  # rare, but happens
        child: Gtk.Widget = widget.get_child()
        contained.append(child)  # append one singleton item
        contained += find_all_widgets(child)  # append all of new list
    if hasattr(widget, 'get_children') and callable(getattr(widget, 'get_children')):  # true for all containers
        children: List[Gtk.Widget] = widget.get_children()
        for child_widget in children:
            contained.append(child_widget)  # append one singleton item
            contained += find_all_widgets(child_widget)  # append all of new list
    return contained


def get_gtk_versions():
    # As of 2024, 05 , 05, The Gtk version used in GIMP was 3.24.41
    major: str = str(Gtk.get_major_version())
    minor: str = str(Gtk.get_minor_version())
    micro: str = str(Gtk.get_micro_version())
    return "Gtk used in GIMP is %s.%s.%s" % (major, minor, micro)


def get_selected_row(widget: Gtk.Widget) -> List[Any]:
    """
    Returns the selected row as a list. The list will be empty if there is no selection, but never None
    :param widget: a ComboBox or TreeView that might have a row selected.
    :return: The selected row as a list. Never None
    """
    row: List[Any] = list()
    if isinstance(widget, Gtk.TreeView):
        treeview: Gtk.TreeView = widget
        selection: Gtk.TreeSelection = treeview.get_selection()
        if selection is not None:
            model, treeiter = selection.get_selected()
            if treeiter is not None:
                row = list(model[treeiter])  # noqa
                if len(row) <= 0:
                    raise ValueError("row in TreeView is empty.")
            else:
                LOGGER_SDGUIU.warning("TreeView treeiter is None")
    else:
        if isinstance(widget, Gtk.ComboBox):
            combo: Gtk.ComboBox = widget
            treeiter = combo.get_active_iter()
            if treeiter is not None:
                model: Gtk.TreeModel = combo.get_model()
                if model is None:
                    LOGGER_SDGUIU.warning("model in ComboBox is None")
                else:
                    row = list(model[treeiter])  # noqa
                    if len(row) <= 0:
                        raise ValueError("row in combobox is empty.")
            else:
                LOGGER_SDGUIU.warning("ComboBox treeiter is None")
        else:
            raise TypeError(f"Cannot get row from object type {type(widget).__name__}")
    return row


def i8_text(message_text):
    return GLib.dgettext(None, message_text)


def index_and_input(widget_name: str) -> tuple[str, str]:
    parts = re.search(REGEX_IDX_N_INPUT, widget_name)
    # widget_class = parts.group(1)
    try:
        index_str = parts.group(2)
        input_name = parts.group(3)
        return index_str, input_name
    except AttributeError as ae:
        LOGGER_SDGUIU.error(f"Pattern {REGEX_IDX_N_INPUT} did not match \"{widget_name}\"")
        LOGGER_SDGUIU.exception(ae)
        raise ae


def install_css_styles(style_bytes: bytes):
    if style_bytes is None:
        raise ValueError("style_bytes cannot be None.")
    # decoded: str = style_bytes.decode('utf-8')
    # LOGGER_SDGUIU.debug("Installing CSS:\n%s" % decoded)
    try:
        style_provider = Gtk.CssProvider().new()
        # Verified in
        # https://lazka.github.io/pgi-docs/Gtk-3.0/classes/StyleContext.html#Gtk.StyleContext.add_provider_for_screen
        # and
        # https://lazka.github.io/pgi-docs/Gdk-3.0/classes/Screen.html#Gdk.Screen
        Gtk.StyleContext.add_provider_for_screen( # noqa
            Gdk.Screen.get_default(),  # noqa
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        style_provider.load_from_data(style_bytes)  # noqa
    except Exception as problem:
        logging.exception(problem)


# noinspection PyUnresolvedReferences
def new_box_of_radios(options: List[str], handler: Callable[[Any], None]) -> Gtk.Box:
    box_0: Gtk.Box = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    i: int = 1
    group: Gtk.RadioButton | None = None
    for label in options:
        check_button: Gtk.RadioButton = Gtk.RadioButton.new_with_label_from_widget(group, label)
        check_button.connect("toggled", handler, str(i))
        dig_str: str = str(random.randrange(111111, 999999, 6))  # not unique, so possibility of collision
        check_button.set_name(f"radio_button_{dig_str}")
        box_0.pack_start(child=check_button, expand=False, fill=False, padding=0)
        group = check_button
        i += 1
    return box_0


# noinspection PyUnresolvedReferences,PyArgumentList
def new_dialog_about(title_in: str,
                     plugin_short_name: str,
                     version_str: str,
                     comfy_srv_origin: str,
                     transceiver_url: str,
                     plugin_uuid: str,
                     plugin_log_file: str,
                     workflow_names: List[str],
                     procedure_names: List[str],
                     ) -> GimpUi.Dialog:
    gimp_icon_name: str = GimpUi.ICON_DIALOG_INFORMATION
    platform_friendly_name: str = get_platform_friendly_name()
    python_version: str = sys.version
    site_packages: str = "\n   ".join(site.getsitepackages())
    python_sys_path: str = "\n   ".join(sys.path)
    workflow_scroll: str = pprint.pformat(workflow_names, indent=4)
    procedure_names_text: str = pprint.pformat(procedure_names, indent=4)
    body_text: str = (
        f"{plugin_short_name}\n"
        f"Plugin Version: {version_str}\n"
        f"Plugin UUID: {plugin_uuid}\n"
        f"ComfyUI server origin: {comfy_srv_origin}\n"
        f"ComfyUI transceiver url: {transceiver_url}\n"
        f"Plugin UUID: {plugin_uuid}\n"
        f"Plugin data folder: \"{get_persistent_dir()}\"\n"
        f"Plugin log file: \"{plugin_log_file}\"\n"
        f"temporary folder: \"{get_temporary_dir_name()}\"\n"
        f"ComfyUI Workflows:\n{workflow_scroll}\n"
        f"Procedures: \n{procedure_names_text}\n"
        f"Platform: {platform_friendly_name}\n"
        f"Python Version: {python_version}\n"
        f"Python site-packages:\n    {site_packages}\n"
        f"Python python_sys_paths:\n    {python_sys_path}\n"
    )
    dialog = GimpUi.Dialog(use_header_bar=True, title=title_in, role="Information")
    textview_0_about: Gtk.TextView = Gtk.TextView.new()
    textview_0_about.get_buffer().set_text(body_text)
    textview_0_about.set_name("textview_0_about")
    textview_0_about.set_editable(False)
    textview_0_about.set_hexpand(True)
    textview_0_about.set_vexpand(True)
    textview_0_about.set_valign(Gtk.Align.FILL)
    # Create a ScrolledWindow to hold the TextView
    scrolled_window_0_about = Gtk.ScrolledWindow()
    scrolled_window_0_about.add(textview_0_about)  # noqa
    scrolled_window_0_about.set_size_request(864, 612)
    scrolled_window_0_about.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
    content_area: Gtk.Box = dialog.get_content_area()
    label_and_icon_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    icon_image = Gtk.Image.new_from_icon_name(gimp_icon_name, Gtk.IconSize.DIALOG)
    label_and_icon_box.pack_start(child=icon_image, expand=False, fill=False, padding=0)
    label_and_icon_box.pack_start(child=scrolled_window_0_about, expand=True, fill=True, padding=0)
    label_and_icon_box.set_margin_start(40)
    label_and_icon_box.set_margin_end(40)
    label_and_icon_box.show_all()
    content_area.add(label_and_icon_box)

    # GIMP does something to the layout in dialogs. I'm not sure if I should force it to look more conventional.
    dialog.add_button(GLib.dgettext(None, "OK"), Gtk.ResponseType.OK)
    geometry = Gdk.Geometry()  # noqa
    geometry.min_aspect = 1.0
    geometry.max_aspect = 1.0
    dialog.set_geometry_hints(None, geometry, Gdk.WindowHints.ASPECT)  # noqa
    dialog.show_all()
    return dialog


# noinspection PyUnresolvedReferences
def new_dialog_error_user(title_in: str,
                          blurb_in: str,
                          gimp_icon_name: str = GimpUi.ICON_DIALOG_ERROR
                          ) -> GimpUi.Dialog:
    dialog = GimpUi.Dialog(use_header_bar=True, title=title_in, role="User_Error")
    dialog_box: Gtk.Box = dialog.get_content_area()
    if blurb_in:
        label_and_icon_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        icon_image = Gtk.Image.new_from_icon_name(gimp_icon_name, Gtk.IconSize.DIALOG)  # noqa
        blurb_label: Gtk.Label = Gtk.Label(label=blurb_in)
        label_and_icon_box.pack_start(child=icon_image, expand=False, fill=False, padding=0)  # noqa
        label_and_icon_box.pack_start(child=blurb_label, expand=True, fill=True, padding=0)  # noqa
        label_and_icon_box.show_all()  # noqa
        dialog_box.add(label_and_icon_box)

    # GIMP does something to the layout in dialogs. I'm not sure if I should force it to look more conventional.
    dialog.add_button(GLib.dgettext(None, "_OK"), Gtk.ResponseType.OK)
    geometry = Gdk.Geometry()  # noqa
    geometry.min_aspect = 0.5
    geometry.max_aspect = 1.0
    dialog.set_geometry_hints(None, geometry, Gdk.WindowHints.ASPECT)  # noqa
    dialog.show_all()
    return dialog


# noinspection PyUnresolvedReferences
def new_dialog_info(title_in: str, blurb_in: str) -> GimpUi.Dialog:
    gimp_icon_name: str = GimpUi.ICON_DIALOG_INFORMATION
    dialog = GimpUi.Dialog(use_header_bar=True, title=title_in, role="Information")
    dialog_box: Gtk.Box = dialog.get_content_area()
    if blurb_in:
        label_and_icon_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        icon_image = Gtk.Image.new_from_icon_name(gimp_icon_name, Gtk.IconSize.DIALOG)  # noqa
        blurb_label: Gtk.Label = Gtk.Label(label=blurb_in)
        label_and_icon_box.pack_start(child=icon_image, expand=False, fill=False, padding=0)  # noqa
        label_and_icon_box.pack_start(child=blurb_label, expand=False, fill=False, padding=0)  # noqa
        label_and_icon_box.set_margin_start(40)
        label_and_icon_box.set_margin_end(40)
        label_and_icon_box.show_all()  # noqa
        dialog_box.add(label_and_icon_box)
    else:
        raise ValueError("new_dialog_info is missing blurb text.")

    # GIMP does something to the layout in dialogs. I'm not sure if I should force it to look more conventional.
    dialog.add_button(GLib.dgettext(None, "OK"), Gtk.ResponseType.OK)
    geometry = Gdk.Geometry()  # noqa
    # TODO: Far too much empty whitespace, but resizing toes not seem to work.
    geometry.min_aspect = 1.0
    geometry.max_aspect = 1.0
    dialog.set_geometry_hints(None, geometry, Gdk.WindowHints.ASPECT)  # noqa
    dialog.show_all()
    return dialog


def url_string(protocol: str = "http",
               host: str = "localhost",
               port: int = 80,
               path_part: str = "/") -> str:
    """
    Minimal URL builder. Concatenates arguments with {protocol}://{host}:{port}{path} unless port is 80, in which case
     it is omitted. "empty" path should be "/", not ""
    :param protocol: default http
    :param host:  default localhost
    :param port:  default 80
    :param path_part: default, /
    :return: {protocol}://{host}:{port}{path}
    """
    if port == 80:
        result = f"{protocol}://{host}{path_part}"
    else:
        result = f"{protocol}://{host}:{port}{path_part}"
    return result


# noinspection PyUnresolvedReferences
def new_dialog_url(title_in: str,
                   blurb_in: str,
                   dict_consumer: Callable[[dict[str, str | int]], None],
                   gimp_icon_name: str = GimpUi.ICON_DIALOG_INFORMATION,
                   defaults: dict[str, str | int] | None = None,
                   ) -> GimpUi.Dialog:
    """
    If default dict is provided, dict must contain key-values for protocol, host, port and path. Note that an "empty"
    path should be "/", not ""
    :param title_in:
    :param blurb_in:
    :param dict_consumer:
    :param gimp_icon_name:
    :param defaults:
    :return:
    """
    dialog_data: dict[str, Any]
    defaults0: dict[str, Any]
    if defaults is None:
        defaults0 = {
            'svr_protocol': "http",
            'svr_host': "localhost",
            'svr_path': "/",
            'svr_port': 80
        }
    else:
        defaults0 = defaults

    dialog = GimpUi.Dialog(use_header_bar=True, title=title_in, role="Questions")
    dialog_box: Gtk.Box = dialog.get_content_area()
    if blurb_in:
        label_and_icon_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        icon_image = Gtk.Image.new_from_icon_name(gimp_icon_name, Gtk.IconSize.DIALOG)  # noqa
        blurb_label: Gtk.Label = Gtk.Label(label=blurb_in)
        label_and_icon_box.pack_start(child=icon_image, expand=False, fill=False, padding=0)  # noqa
        label_and_icon_box.pack_start(child=blurb_label, expand=False, fill=False, padding=0)  # noqa
        label_and_icon_box.show_all()  # noqa
        dialog_box.add(label_and_icon_box)

    label_svr_host: Gtk.Label = Gtk.Label.new("Host Name")
    label_svr_path: Gtk.Label = Gtk.Label.new("Path")
    label_svr_protocol: Gtk.Label = Gtk.Label.new("Protocol")
    label_svr_port: Gtk.Label = Gtk.Label.new("Port")
    label_svr_url: Gtk.Label = Gtk.Label.new("URL")
    label_svr_url_val: Gtk.Label = Gtk.Label.new("UNSET")
    entry_svr_host: Gtk.Entry = Gtk.Entry.new()
    entry_svr_path: Gtk.Entry = Gtk.Entry.new()
    entry_svr_port: Gtk.Entry = Gtk.Entry.new()
    entry_svr_protocol: Gtk.Entry = Gtk.Entry.new()

    entry_svr_host.set_name('entry_svr_host')
    entry_svr_path.set_name('entry_svr_path')
    entry_svr_port.set_name('entry_svr_port')
    entry_svr_protocol.set_name('entry_svr_protocol')

    restrict_to_ints(entry_widget=entry_svr_port)

    entry_svr_host.set_text(defaults0['svr_host'])
    entry_svr_path.set_text(defaults0['svr_path'])
    entry_svr_port.set_text(str(defaults0['svr_port']))
    entry_svr_protocol.set_text(defaults0['svr_protocol'])
    label_svr_url_val.set_text(url_string(
        protocol=defaults0['svr_protocol'],
        host=defaults0['svr_host'],
        port=defaults0['svr_port'],
        path_part=defaults0['svr_path']
    ))

    entry_svr_host.set_hexpand(True)
    entry_svr_path.set_hexpand(True)
    entry_svr_port.set_hexpand(True)
    entry_svr_protocol.set_hexpand(True)
    label_svr_url_val.set_hexpand(True)

    def build_url(ignored: Any):  # noqa
        nonlocal entry_svr_protocol
        nonlocal entry_svr_port
        nonlocal entry_svr_host
        nonlocal entry_svr_path
        nonlocal label_svr_url_val
        protocol: str = entry_svr_protocol.get_text()
        hst: str = entry_svr_host.get_text()
        prt: int = int(entry_svr_port.get_text())
        pth: str = entry_svr_path.get_text()
        url: str = url_string(protocol=protocol, host=hst, port=prt, path_part=pth)
        label_svr_url_val.set_text(url)
    entry_svr_protocol.connect(SIG_CHANGED, build_url)
    entry_svr_host.connect(SIG_CHANGED, build_url)
    entry_svr_port.connect(SIG_CHANGED, build_url)
    entry_svr_path.connect(SIG_CHANGED, build_url)

    grid: Gtk.Grid = Gtk.Grid.new()
    grid.attach(child=label_svr_protocol, left=0, top=0, width=1, height=1)  # noqa
    grid.attach(child=entry_svr_protocol, left=1, top=0, width=3, height=1)  # noqa
    grid.attach(child=label_svr_host,     left=0, top=1, width=1, height=1)  # noqa
    grid.attach(child=entry_svr_host,     left=1, top=1, width=3, height=1)  # noqa
    grid.attach(child=label_svr_port,     left=0, top=2, width=1, height=1)  # noqa
    grid.attach(child=entry_svr_port,     left=1, top=2, width=3, height=1)  # noqa
    grid.attach(child=label_svr_path,     left=0, top=3, width=1, height=1)  # noqa
    grid.attach(child=entry_svr_path,     left=1, top=3, width=3, height=1)  # noqa
    grid.attach(child=label_svr_url,      left=0, top=5, width=1, height=1)  # noqa
    grid.attach(child=label_svr_url_val,  left=1, top=5, width=3, height=1)  # noqa

    dialog_box.pack_start(child=grid,expand=True, fill=True, padding=0)  # noqa

    dialog.add_button(GLib.dgettext(None, "_Cancel"), Gtk.ResponseType.CANCEL)
    dialog.add_button(GLib.dgettext(None, "_OK"), Gtk.ResponseType.OK)
    button_cancel: Gtk.Button = dialog.get_widget_for_response(Gtk.ResponseType.CANCEL)

    def cancelled(subject: Any):  # noqa
        nonlocal dialog_data
        dialog_data = {}

    button_cancel.connect("clicked", cancelled)
    button_ok: Gtk.Button = dialog.get_widget_for_response(Gtk.ResponseType.OK)

    def assign_results(subject: Any):  # noqa
        nonlocal dict_consumer
        nonlocal dialog_data
        nonlocal entry_svr_protocol
        nonlocal entry_svr_port
        nonlocal entry_svr_host
        nonlocal entry_svr_path
        protocol: str = entry_svr_protocol.get_text()
        hst: str = entry_svr_host.get_text()
        prt: int = int(entry_svr_port.get_text())
        pth: str = entry_svr_path.get_text()
        dialog_data = {
            'svt_protocol': protocol,
            'svr_host': hst,
            'svr_path': "",
            'svr_port': prt,
            'svr_url': url_string(protocol=protocol, host=hst, port=prt, path_part=pth)
        }
        dict_consumer(dialog_data)

    button_ok.connect("clicked", assign_results)
    geometry = Gdk.Geometry()  # noqa
    geometry.min_aspect = 0.5
    geometry.max_aspect = 1.0
    dialog.set_geometry_hints(None, geometry, Gdk.WindowHints.ASPECT)  # noqa
    dialog.show_all()
    return dialog


def open_dialog_daemon(title_in: str,
                       blurb_in: str,
                       ok_handler: Callable[[Gtk.Widget, ], None],
                       main_button_label: str = "Ok",
                       dialog_populator: Callable[[Gtk.Dialog, ], None] | None = None
                       ):
    """
    Opens a Gtk.Dialog in a thread separate from the GIMP application thread and the plugin thread. This allows
    interaction with the dialog without blocking GIMP or plug-in behavior, but creates risks of deadlocks and races.
    This dialog should be closed by the user, or programmatically, with a function like close_window_of_widget().
    If construction throws an exception, there might be a zombie thread running indefinitely.
    :param title_in: The Title for the dialog.
    :param blurb_in: A usage tip for the user.
    :param ok_handler: A function that does some final work stopping the daemon, THEN CALLS close_window_of_widget().
     This function is called from the Gtk event thread, so use great caution when accessing other objects!
    :param dialog_populator: A function to customise the dialog. dialog_populator is invoked after the primary buttons
    are added, abd before the Geometry is calculated. This may be None. This function is called from the Gtk event
     thread, so use great caution when accessing other objects!
    :param main_button_label: String to display in the "Ok" button that closes the dialog. Defaults to "Ok"
    """

    def run_on_idle():
        nonlocal title_in
        nonlocal blurb_in
        nonlocal ok_handler
        try:
            image_file_path: str = asset_path("magic_lamp_160x86.png")
            dialog: Gtk.Dialog = Gtk.Dialog(use_header_bar=True, title=title_in)
            dialog_box: Gtk.Box = dialog.get_content_area()
            if blurb_in:
                label_and_icon_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                icon_image = Gtk.Image.new_from_file(image_file_path)
                blurb_label: Gtk.Label = Gtk.Label(label=blurb_in)
                label_and_icon_box.pack_start(child=icon_image, expand=False, fill=False, padding=0)  # noqa
                label_and_icon_box.pack_start(child=blurb_label, expand=False, fill=False, padding=0)  # noqa
                label_and_icon_box.set_margin_start(40)
                label_and_icon_box.set_margin_end(40)
                label_and_icon_box.show_all()  # noqa
                dialog_box.add(label_and_icon_box)  # noqa
            else:
                raise ValueError("open_dialog_daemon is missing blurb text.")
            dialog.add_button(GLib.dgettext(None, main_button_label), Gtk.ResponseType.OK)
            button_ok: Gtk.Widget = dialog.get_widget_for_response(Gtk.ResponseType.OK)
            button_ok.connect("clicked", ok_handler)
            if dialog_populator is not None:
                try:
                    dialog_populator(dialog)
                except Exception as e_error_0:
                    LOGGER_SDGUIU.exception(e_error_0)
            geometry = Gdk.Geometry()  # noqa
            geometry.min_aspect = 1.0
            geometry.max_aspect = 1.0
            dialog.set_geometry_hints(None, geometry, Gdk.WindowHints.ASPECT)  # noqa
            dialog.show_all()  # noqa
        except Exception as e_error_1:
            LOGGER_SDGUIU.exception(e_error_1)

    def meta_fork():
        GLib.idle_add(run_on_idle)
        # Invoking GLib.MainLoop().run() is ... unconventional. Beware locks and races, even in stuff like logging.
        # The window created here should be closed by the user, or programmatically, with a function like
        # close_window_of_widget()
        GLib.MainLoop().run()  # Does not return, so needs new thread.

    my_thread: threading.Thread = threading.Thread(target=meta_fork)
    my_thread.daemon = True  # Required so thread stops with GIMP
    my_thread.start()


def new_list_store_images() -> Gtk.ListStore:
    """
    Returns a Gtk.ListStore of tuples image_id, index, image_name for the images open in GIMP
    :return: a Gtk.ListStore of tuples image_id, index, image_name for the images open in GIMP
    """
    images_list_store: Gtk.ListStore = Gtk.ListStore.new(types=[int, int, str])  # image_id, index, image_name
    image: Gimp.Image
    i: int = 0
    image_list = Gimp.get_images()
    if not image_list:
        LOGGER_SDGUIU.warning("Could not find any images.")
        return images_list_store
    # else:
    #     LOGGER_SDGUIU.debug(f"referencing {len(image_list)} images")
    for image in image_list:
        row = [image.get_id(), i, image.get_name()]
        # message = "image_id=%d, index=%d, image_name=%s" % (row[0], row[1], row[2])
        # StabDiffAuto1111.LOGGER.debug(message)
        images_list_store.append(row)
        i += 1
    return images_list_store


def new_list_store_models(model_type: ModelType, cu_origin: str) -> Gtk.ListStore:
    """
    Returns a Gtk.ListStore of tuples model_basename, index, model_path for models of the specified type currently
    available in ComfyUI
    :param model_type: The type of model, i.e. ModelType.CHECKPOINTS
    :param cu_origin: The hostname and port of the ComfyUI server. i.e. "localhost:8188"
    :return: a Gtk.ListStore of tuples  model_basename, index, model_path for models of the specified type
    """
    models_list_store: Gtk.ListStore = Gtk.ListStore.new(types=[str, int, str])  # model_basename, index, model_path

    i: int = 0
    models_list: List[Dict[str, str]]
    models_list = get_models_list(model_type=model_type, cu_origin=cu_origin)
    if not models_list:
        LOGGER_SDGUIU.warning(f"Could not find any models of type {model_type.name}.")
        return models_list_store
    # else:
    #     LOGGER_SDGUIU.debug(f"referencing {len(image_list)} images")
    for record in models_list:
        row = [record['name'], i, record['path']]
        # message = "image_id=%d, index=%d, image_name=%s" % (row[0], row[1], row[2])
        # LOGGER_SDGUIU.LOGGER.debug(message)
        models_list_store.append(row)
        i += 1
    return models_list_store


def new_set_images() -> set[tuple[int, int, str]]:
    """
    Returns a set of tuples image_id, index, image_name for the images open in GIMP
    :return: a set of tuples image_id, index, image_name for the images open in GIMP
    """
    images_set: set[tuple[int, int, str]] = set()  # image_id, index, image_name
    image: Gimp.Image
    i: int = 0
    image_list = Gimp.get_images()
    if not image_list:
        LOGGER_SDGUIU.warning("Could not find any images.")
        return images_set
    for image in image_list:
        row: tuple[int, int, str] = image.get_id(), i, image.get_name()
        message = "image_id=%d, index=%d, image_name=%s" % (row[0], row[1], row[2])
        LOGGER_SDGUIU.debug(message)
        images_set.add(row)
        i += 1
    return images_set


def new_set_image_ids() -> set[int]:
    """
    Returns a set of image_id ints for the images open in GIMP
    :return: a set of image_id ints for the images open in GIMP
    """
    images_set: set[tuple[int, int, str]] = new_set_images()
    image_ids: set[int] = set()
    if not images_set:
        LOGGER_SDGUIU.warning("Could not find any images.")
        return image_ids
    for image_id, index, image_name in images_set:
        image_ids.add(image_id)
    return image_ids


def new_tree_store_images() -> Gtk.TreeStore:
    images_tree_store: Gtk.TreeStore = Gtk.TreeStore.new(types=[int, int, str])  # image_id, index, image_name
    image: Gimp.Image
    i: int = 0
    image_list = Gimp.get_images()
    if not image_list:
        LOGGER_SDGUIU.warning("Could not find any images.")
        return images_tree_store
    # else:
    #     LOGGER_SDGUIU.debug(f"referencing {len(image_list)} images")
    for image in image_list:
        row = [image.get_id(), i, image.get_name()]
        # message = "image_id=%d, index=%d, image_name=%s" % (row[0], row[1], row[2])
        # LOGGER_SDGUIU.warning(message)
        images_tree_store.append(None, row)
        i += 1
    return images_tree_store


def new_list_store_layers(image_in: Gimp.Image) -> Gtk.ListStore:
    if not image_in:
        raise ValueError("image_in argument cannot be None.")
    # Model row will be layer_id, index, name
    layers_list_store: Gtk.ListStore = Gtk.ListStore.new(types=[int, int, str])  # image_id, index, image_name
    layer: Gimp.Layer
    i: int = 0
    for layer in image_in.get_layers():
        row = [layer.get_id(), i, layer.get_name()]
        # message = "layer_id=%d, index=%d, layer_name=%s" % (row[0], row[1], row[2])
        layers_list_store.append(row)
        i += 1
    return layers_list_store


def new_list_store_all_layers() -> Gtk.TreeStore:
    all_layers_tree_store: Gtk.TreeStore = (
        Gtk.TreeStore.new(types=[str, int, int, str]))  # type_name, image_id, index, image_name
    images: Gtk.TreeStore = new_tree_store_images()
    image_values: tuple[int, int, str]
    for image_values in images:  # noqa
        image_row: List = list(["image", *image_values])
        tree_iter = all_layers_tree_store.append(None, image_row)
        subject_image: Gimp.Image = Gimp.Image.get_by_id(image_values[0])
        layers: Gtk.ListStore = new_list_store_layers(subject_image)
        layer_values: tuple[int, int, str]
        for layer_values in layers:  # noqa
            layer_row: List = list(["layer", *layer_values])
            all_layers_tree_store.append(tree_iter, layer_row)
    return all_layers_tree_store


def new_set_all_layers() -> set[tuple[int, int, str]]:  # layer_id, index, layer_name
    """
    Returns a set of tuples tuple[int, int, str]  # layer_id, index, layer_name for all root layers in all open images.
    :return: a set of tuples tuple[int, int, str]  # layer_id, index, layer_name for all root layers in all open images
    """
    all_layers_set: set[tuple[int, int, str]] = set()
    image_list = Gimp.get_images()
    if not image_list:
        LOGGER_SDGUIU.warning("Could not find any images.")
        return all_layers_set
    image: Gimp.Image
    i: int = 0
    for image in image_list:
        layer: Gimp.Layer
        for layer in image.get_layers():
            row: tuple[int, int, str] = layer.get_id(), i, layer.get_name()
            all_layers_set.add(row)
            i += 1
    return all_layers_set


def new_set_all_layer_ids() -> set[int]:
    all_layer_id_set: set[int] = set()
    all_layers: set[tuple[int, int, str]] = new_set_all_layers()
    if not all_layers:
        LOGGER_SDGUIU.warning("Could not find any images.")
        return all_layer_id_set
    for layer_id, index, layer_name in all_layers:
        all_layer_id_set.add(layer_id)
    return all_layer_id_set


def path_to_id(model: Gtk.TreeModel, item_id: int, row_index: int = 1) -> Gtk.TreePath:
    """
    Returns the path to a layer or None if the layer_id could not be found.
    :param model: The TreeModel to search.
    :param item_id:
    :param row_index: this index of the item_in in a row: 0 for image rows, 1 for layer rows
    :return: the path to an item, or None if the layer_id could not be found.
    """
    result: Gtk.TreePath | None = None
    if model is None:
        raise ValueError("No model")
    if not model:
        raise ValueError("No values in model")

    # noinspection PyUnusedLocal
    def row_consumer(w_model: Gtk.TreeModel,
                     tree_path: Gtk.TreePath,
                     w_iter: Gtk.TreeIter,
                     *data: object | None) -> bool:
        nonlocal result
        found = w_model[w_iter][row_index] == item_id  # noqa
        if found:
            result = tree_path
            return True
        else:
            return False

    model.foreach(row_consumer)
    if result is None:
        LOGGER_SDGUIU.warning(f"Path to layer  {item_id} not found.")
    return result


def print_row(store: Gtk.TreeStore, treepath: Gtk.TreePath, treeiter: Gtk.TreeIter):
    print("\t" * (treepath.get_depth() - 1), store[treeiter][:], sep="")  # noqa


def new_images_combobox(selection_changed_handler: Callable[[Any], None]) -> Gtk.ComboBox:
    image_store: Gtk.ListStore = Gtk.ListStore.new(types=[int, int, str])  # image_id, index, image_name
    try:
        image_store = new_list_store_images()
    except Exception as e_err:
        LOGGER_SDGUIU.exception(e_err)
    # LOGGER_SDGUIU.debug(f"image_store has {len(image_store)} images")
    image_combo = Gtk.ComboBox.new_with_model(model=image_store)
    image_combo.set_name("image_combobox")
    image_combo.set_active(0)
    cell_renderer_text = Gtk.CellRendererText()
    image_combo.pack_start(cell_renderer_text, expand=True)
    image_combo.add_attribute(cell_renderer_text, attribute="text", column=2)  # column 2 has image_name
    image_combo.connect("changed", selection_changed_handler)
    return image_combo


def new_all_layers_treeview(selection_changed_handler: Callable[[Any], None]) -> Gtk.TreeView:
    index_type_name = 0
    index_item_name = 3

    def is_selectable(selection, model, path, path_currently_selected, *data) -> bool:  # noqa
        """
        A function used by Gtk.TreeSelection.set_select_function() to filter whether a row may be selected.
        :param selection: A Gtk.TreeSelection
        :param model: A Gtk.TreeModel being viewed
        :param path: The Gtk.TreePath of the row in question
        :param path_currently_selected: True, if the path is currently selected
        :param data: user data
        :return: true if the row is for a layer
        """
        nonlocal index_type_name
        is_layer: bool = False
        if model:
            if path:
                treeiter: Gtk.TreeIter = model.get_iter(path)
                if treeiter:
                    type_name = model[treeiter][index_type_name]
                    is_layer = type_name == "layer"
                    # LOGGER_SDGUIU.debug(f"is_layer=\"{is_layer}\"")
                else:
                    LOGGER_SDGUIU.warning(f"No iterator from path \"{path}\"")
            else:
                LOGGER_SDGUIU.warning("No path passed to is_selectable()")
        else:
            LOGGER_SDGUIU.warning("No model passed to is_selectable()")
        return is_layer

    store: Gtk.TreeStore = new_list_store_all_layers()
    fresh_treeview: Gtk.TreeView = Gtk.TreeView(model=store)
    fresh_treeview.set_name("all_layers_treeview")
    text_renderer = Gtk.CellRendererText()
    column_type = Gtk.TreeViewColumn(title="Type", cell_renderer=text_renderer, text=index_type_name)  # noqa
    column_name = Gtk.TreeViewColumn(title="Name", cell_renderer=text_renderer, text=index_item_name)  # noqa
    fresh_treeview.append_column(column_type)
    fresh_treeview.append_column(column_name)
    fresh_treeview.expand_all()
    select: Gtk.TreeSelection = fresh_treeview.get_selection()
    select.select_path("0:0")  # Root node, 1st child.
    select.set_select_function(is_selectable)
    select.connect("changed", selection_changed_handler)
    return fresh_treeview


def new_list_store_selected_drawables(image_in: Gimp.Image) -> Gtk.ListStore:
    if not image_in:
        raise ValueError("image_in argument cannot be None.")
    # Model row will be layer_id, index, name
    selected_drawables_list_store: Gtk.ListStore = Gtk.ListStore.new(types=[int, int, str])  # noqa
    drawable: Gimp.Item
    i: int = 0
    for drawable in image_in.get_selected_drawables():
        row = [drawable.get_id(), i, drawable.get_name()]
        # message = "drawable_id=%d, index=%d, drawable_name=%s" % (row[0], row[1], row[2])
        selected_drawables_list_store.append(row)
        i += 1
    return selected_drawables_list_store


def new_validation_css_bytes(widget: Gtk.Widget) -> bytes:
    widget_name: str = widget.get_name()
    if widget_name is None:
        raise ValueError("Widget does not have a name")
    if not widget_name.strip():
        raise ValueError("Widget name cannot be empty nor whitespace.")
    if re.search(r"\s", widget_name):
        raise ValueError("Widget name cannot contain whitespace")
    if widget_name in WIDGET_NAME_DEFAULTS:
        raise ValueError("Widget name cannot be default name \"%s\"" % widget_name)
    css_string = ("""
    #%s.INVALID { border-color: Red; }
    #%s.VALID { border-color: Green; }
    #%s.OK { border-color: Blue; }
    """ % (widget_name, widget_name, widget_name))
    # LOGGER_SDGUIU.debug("Generated CSS:\n%s" % css_string)
    return css_string.encode('utf-8')


def pretty_name(ugly_name: str) -> str:
    fresh_name = ugly_name.replace("StabDiffAuto1111-", "")
    fresh_name = fresh_name.replace("-image-context", "")
    fresh_name = fresh_name.replace("-layer", "")
    fresh_name = fresh_name.replace("-layers-context", "")
    fresh_name = fresh_name.replace("-info", " info")
    fresh_name = fresh_name.replace("-model", " model")
    fresh_name = fresh_name.replace("2", " to ")
    fresh_name = fresh_name.replace("img", "image")
    fresh_name = fresh_name.replace("txt", "text")
    fresh_name = fresh_name.replace("-context", "")  # Keep as penultimate
    fresh_name = fresh_name.title()
    return fresh_name


def reciprocal_dict(dictionary: Dict[Any, Any]) -> Dict[Any, Any]:
    reciprocal: Dict[Any, Any] = {}
    for key, value in dictionary.items():
        reciprocal[value] = key  # Deliberately inverted
    return reciprocal


def restrict_to_ints(entry_widget: Gtk.Entry):
    """
    Don't try and use this with other restrict*() functions. The internal validators will race for which gets invoked
    first, leading to unpredictable behavior.
    :param entry_widget:
    :return:
    """
    if not isinstance(entry_widget, Gtk.Entry):
        raise TypeError("Widget argument must be a Gtk.Entry")

    # noinspection PyUnusedLocal
    def filter_numbers(entry_0: Gtk.Entry, *args):
        text = entry_0.get_text().strip()
        # This is bad code. It's recursing through the signal system. The bug is invisible because it only recurses
        # once, but still ...
        entry_0.set_text(''.join([i for i in text if i in '0123456789-']))

    entry_widget.connect(SIG_CHANGED, filter_numbers)


def restrict_to_numbers(entry_widget: Gtk.Entry):
    """
    Don't try and use this with other restrict*() functions. The internal validators will race for which gets invoked
    first, leading to unpredictable behavior.
    :param entry_widget:
    :return:
    """
    if not isinstance(entry_widget, Gtk.Entry):
        raise TypeError("Widget argument must be a Gtk.Entry")

    # noinspection PyUnusedLocal
    def filter_numbers(entry_0: Gtk.Entry, *args):
        text = entry_0.get_text().strip()
        # This is bad code. It's recursing through the signal system. The bug is invisible because it only recurses
        # Once, but still ...
        entry_0.set_text(''.join([i for i in text if i in '0123456789.-']))

        entry_widget.connect(SIG_CHANGED, filter_numbers)


def validate_in_bounds(entry_widget: Gtk.Entry,
                       minimum: float = float('-inf'),
                       maximum: float = float('inf'),
                       int_only: bool = False,
                       track_invalid_widgets: Callable[[Gtk.Widget, bool], None] = None):
    """
    Don't try and combine this with other validate() functions. Trying to use other validator() methods are a problem
    because a single value can be valid to some, and invalid to others.
    :param entry_widget:
    :param minimum:
    :param maximum:
    :param int_only: text must parse to an int, floats are not adequate.
    :param track_invalid_widgets: The function track_invalid_widgets(self, my_widget: Gtk.Widget, is_invalid: bool):
    :return:
    """
    if not isinstance(entry_widget, Gtk.Entry):
        raise TypeError("Widget argument must be a Gtk.Entry")
    # There is ambiguity about the case where minimum or maximum are explicitly passed "None" as an argument value.
    # This code should resolve that ambiguity.
    if minimum is None:
        minimum = float('-inf')
    if maximum is None:
        maximum = float('inf')
    widget_name: str = entry_widget.get_name()
    if widget_name is None:
        raise ValueError("Widget does not have a name")
    if not widget_name.strip():
        raise ValueError("Widget name cannot be empty nor whitespace.")
    if re.search(r"\s", widget_name):
        raise ValueError("Widget name cannot contain whitespace")
    # This is an unpleasant surprise. The default widget names are ignored by the CSS classes.
    # Widgets must be explicitly named for CSS to work as expected.
    if widget_name in WIDGET_NAME_DEFAULTS:
        raise ValueError("Widget name cannot be default name \"%s\"" % widget_name)
    install_css_styles(new_validation_css_bytes(entry_widget))

    def handle_bounds_check(entry_0: Gtk.Entry, *args):  # noqa
        # This function is forbidden from changing the text in the widget, else infinite recursion.
        nonlocal minimum
        nonlocal maximum
        nonlocal widget_name
        nonlocal int_only
        nonlocal track_invalid_widgets
        entry_style_context = entry_0.get_style_context()
        css_class_list = entry_style_context.list_classes()  # noqa
        for class_name in css_class_list:
            if class_name in ["INVALID", "VALID", "OK"]:
                entry_style_context.remove_class(class_name=class_name)
        text = entry_0.get_text().strip()
        if text and ((text != "-") or (text != "+") or (text != "0.")):
            # v_message: str = f"Validating widget {widget_name} value \"{text}\""
            # LOGGER_SDGUIU.debug(v_message)
            try:
                value = float(text)
                if int_only:
                    is_int = re.match(REGEX_STR_INT, text)
                    if not is_int:
                        raise ValueError(f"{text} is not an int")
                valid = (value >= minimum) and (value <= maximum)
                if valid:
                    # LOGGER_SDGUIU.debug("in-bounds")
                    entry_style_context.add_class("VALID")
                    if track_invalid_widgets is not None:
                        track_invalid_widgets(entry_0, False)  # valid
                else:
                    # LOGGER_SDGUIU.debug("out-of-bounds")
                    entry_style_context.add_class("INVALID")
                    if track_invalid_widgets is not None:
                        track_invalid_widgets(entry_0, True)  # invalid
            except ValueError as ve:  # noqa
                entry_style_context.add_class("INVALID")
                # logging.exception(ve)
                if track_invalid_widgets is not None:
                    track_invalid_widgets(entry_0, True)  # invalid
        else:
            # v_message: str = "Skipping validation of widget %s value \"%s\"" % (widget_name, text)
            # LOGGER_SDGUIU.debug(v_message)
            pass

    # message: str = "Connecting validator to widget %s signal \"%s\"" % (widget_name, SIG_CHANGED)
    # LOGGER_SDGUIU.debug(message)
    entry_widget.connect(SIG_CHANGED, handle_bounds_check)


def validate_int(entry_widget: Gtk.Entry,
                 track_invalid_widgets: Callable[[Gtk.Widget, bool], None] = None):
    if not isinstance(entry_widget, Gtk.Entry):
        raise TypeError("Widget argument must be a Gtk.Entry")
    widget_name: str = entry_widget.get_name()
    if widget_name is None:
        raise ValueError("Widget does not have a name")
    if not widget_name.strip():
        raise ValueError("Widget name cannot be empty nor whitespace.")
    if re.search(r"\s", widget_name):
        raise ValueError("Widget name cannot contain whitespace")
    # This is an unpleasant surprise. The default widget names are ignored by the CSS classes.
    # Widgets must be explicitly named for CSS to work as expected.
    if widget_name in WIDGET_NAME_DEFAULTS:
        raise ValueError("Widget name cannot be default name \"%s\"" % widget_name)
    install_css_styles(new_validation_css_bytes(entry_widget))

    def handle_is_int(entry_0: Gtk.Entry, *args):  # noqa
        # This function is forbidden from changing the text in the widget, else infinite recursion.
        nonlocal widget_name
        nonlocal track_invalid_widgets
        entry_style_context = entry_0.get_style_context()
        css_class_list = entry_style_context.list_classes()  # noqa
        for class_name in css_class_list:
            if class_name in ["INVALID", "VALID", "OK"]:
                entry_style_context.remove_class(class_name=class_name)
        text = entry_0.get_text().strip()
        if text and ((text != "-") or (text != "+")):
            v_message: str = "Validating widget %s value \"%s\"" % (widget_name, text)
            LOGGER_SDGUIU.debug(v_message)
            try:
                valid = re.match(REGEX_STR_INT, text)
                if valid:
                    LOGGER_SDGUIU.debug("integer")
                    entry_style_context.add_class("VALID")
                    if track_invalid_widgets is not None:
                        track_invalid_widgets(entry_0, False)  # valid
                else:
                    LOGGER_SDGUIU.debug("not integer")
                    entry_style_context.add_class("INVALID")
                    if track_invalid_widgets is not None:
                        track_invalid_widgets(entry_0, True)  # invalid
            except ValueError as ve:
                entry_style_context.add_class("INVALID")
                logging.exception(ve)
                if track_invalid_widgets is not None:
                    track_invalid_widgets(entry_0, True)  # invalid
        else:
            # v_message: str = "Skipping validation of widget %s value \"%s\"" % (widget_name, text)
            # LOGGER_SDGUIU.debug(v_message)
            pass

    # message: str = "Connecting validator to widget %s signal \"%s\"" % (widget_name, SIG_CHANGED)
    # LOGGER_SDGUIU.debug(message)
    entry_widget.connect(SIG_CHANGED, handle_is_int)


def validate_float(entry_widget: Gtk.Entry,
                   track_invalid_widgets: Callable[[Gtk.Widget, bool], None] = None):
    if not isinstance(entry_widget, Gtk.Entry):
        raise TypeError("Widget argument must be a Gtk.Entry")
    widget_name: str = entry_widget.get_name()
    if widget_name is None:
        raise ValueError("Widget does not have a name")
    if not widget_name.strip():
        raise ValueError("Widget name cannot be empty nor whitespace.")
    if re.search(r"\s", widget_name):
        raise ValueError("Widget name cannot contain whitespace")
    # This is an unpleasant surprise. The default widget names are ignored by the CSS classes.
    # Widgets must be explicitly named for CSS to work as expected.
    if widget_name in WIDGET_NAME_DEFAULTS:
        raise ValueError("Widget name cannot be default name \"%s\"" % widget_name)
    install_css_styles(new_validation_css_bytes(entry_widget))

    def handle_is_float(entry_0: Gtk.Entry, *args):  # noqa
        # This function is forbidden from changing the text in the widget, else infinite recursion.
        nonlocal widget_name
        nonlocal track_invalid_widgets
        entry_style_context = entry_0.get_style_context()
        css_class_list = entry_style_context.list_classes()  # noqa
        for class_name in css_class_list:
            if class_name in ["INVALID", "VALID", "OK"]:
                entry_style_context.remove_class(class_name=class_name)
        text = entry_0.get_text().strip()
        if text and ((text != "-") or (text != "+")):
            v_message: str = "Validating widget %s value \"%s\"" % (widget_name, text)
            LOGGER_SDGUIU.debug(v_message)
            try:
                valid = float(text)
                if valid:
                    LOGGER_SDGUIU.debug("floating point")
                    entry_style_context.add_class("VALID")
                    if track_invalid_widgets is not None:
                        track_invalid_widgets(entry_0, False)  # valid
                else:
                    LOGGER_SDGUIU.debug("not floating point")
                    entry_style_context.add_class("INVALID")
                    if track_invalid_widgets is not None:
                        track_invalid_widgets(entry_0, True)  # invalid
            except ValueError as ve:
                entry_style_context.add_class("INVALID")
                logging.exception(ve)
                if track_invalid_widgets is not None:
                    track_invalid_widgets(entry_0, True)  # invalid
        else:
            # v_message: str = "Skipping validation of widget %s value \"%s\"" % (widget_name, text)
            # LOGGER_SDGUIU.debug(v_message)
            pass

    # message: str = "Connecting validator to widget %s signal \"%s\"" % (widget_name, SIG_CHANGED)
    # LOGGER_SDGUIU.debug(message)
    entry_widget.connect(SIG_CHANGED, handle_is_float)


def show_dialog_user_error(message: str):
    LOGGER_SDGUIU.error(f"{message}")
    dialog: GimpUi.Dialog = new_dialog_error_user(
        title_in=f"Error",
        blurb_in=message
    )
    response_code = dialog.run()  # Blocks until dialog is closed...
    LOGGER_SDGUIU.debug(f"Dialog response code={response_code}")
    dialog.destroy()


def server_online(url_in: str, show_dialog: bool = True):
    if url_in is None:
        raise ValueError("url_in argument is missing.")
    if url_in.strip() == "":
        raise ValueError("url_in argument is blank.")
    if not url_in.lower().startswith("http://"):
        raise ValueError(f"server_url argument \"{url_in}\" is not a valid http URL.")
    try:
        # There does not seem to be a way to make this fail quietly. Also, the printed error
        # "During handling of the above exception, another exception occurred" that references this is bogus.
        request.urlopen(url=url_in, timeout=3)
        return True
    except Exception as con_err:  # noqa
        logging.getLogger("URLError").error(f"Could not connect to {url_in}")
        logging.getLogger("URLError").exception(con_err)
        Gimp.message(str(con_err))
        if show_dialog:
            try:
                show_dialog_user_error(f"Could not connect to {url_in}\n{str(con_err)}")
            except Exception as problem:
                LOGGER_SDGUIU.error(problem)
        return False


def val_combo_index(cbox: Gtk.ComboBox) -> int:
    return cbox.get_active()


def val_combo(cbox: Gtk.ComboBox):
    return cbox.get_model()[cbox.get_active_iter()][0]  # noqa


def val_entry(an_entry: Gtk.Entry):
    return an_entry.get_text()


def val_scale(a_scale: Gtk.Scale):
    return a_scale.get_value()


def val_text_view(a_text_view: Gtk.TextView):
    buffer: Gtk.TextBuffer = a_text_view.get_buffer()
    start: Gtk.TextIter = buffer.get_start_iter()
    end: Gtk.TextIter = buffer.get_end_iter()
    return buffer.get_text(start, end, False)


def val_widget(a_widget: Gtk.Widget):
    if isinstance(a_widget, GimpUi.LayerComboBox):
        result = val_combo(a_widget)  # noqa
        if type(result) is tuple:
            return result[1]  # First or second value of this weird tuple?
        else:
            return result
    if isinstance(a_widget, Gtk.ComboBox): return val_combo(a_widget)  # noqa
    if isinstance(a_widget, Gtk.Entry): return a_widget.get_text()  # noqa
    if isinstance(a_widget, Gtk.Scale): return a_widget.get_value()  # noqa
    if isinstance(a_widget, Gtk.TextView): return val_text_view(a_widget)  # noqa
    if isinstance(a_widget, Gtk.ToggleButton): return a_widget.get_active()  # noqa


def example_dialog_0() -> int:
    blurb: str = "Test run from main()"
    carry_on: bool = True

    # noinspection PyUnusedLocal
    def halt(source: Gtk.Widget, data=None):
        nonlocal carry_on
        close_window_of_widget(source)
        carry_on = False

    def transceiver_queue_handler(source, data=None):
        source_type: type = type(source)
        source_type_name: str = source_type.__name__
        if data is not None and data:
            data_type: type = type(data)
            data_type_name: str = data_type.__name__
            data_msg = f", data is a {data_type_name}"
        else:
            data_msg = ""
        LOGGER_SDGUIU.debug(f"source is a {source_type_name}{data_msg}")

    def populate_transceiver_dialog(dialog: Gtk.Dialog):
        drawable_name_frame: Gtk.Frame = Gtk.Frame.new(label="Layer: generated_00")
        radio_box: Gtk.Box = new_box_of_radios(
            options=["Standby with changes", "Queue changes"],
            handler=transceiver_queue_handler)
        empty_box: Gtk.Box = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        drawable_name_frame.add(widget=radio_box)  # noqa
        dialog_box: Gtk.Box = dialog.get_content_area()
        dialog_box.pack_start(child=drawable_name_frame, expand=True, fill=False, padding=0)  # noqa
        dialog_box.pack_start(child=empty_box, expand=True, fill=True, padding=4)  # noqa

    open_dialog_daemon(title_in="Example Dialog",
                       blurb_in=blurb,
                       ok_handler=halt,
                       dialog_populator=populate_transceiver_dialog)

    while carry_on:
        time.sleep(1)

    return 0


# noinspection PyUnresolvedReferences
class ProgressBarWindow(Gtk.Window):
    def __init__(self,
                 title_in: str,
                 blurb_in: str,
                 total: float | None,
                 activity_mode: bool = False
                 ):
        super().__init__(title=title_in)
        self._activity_mode = activity_mode
        self._total: float | None = total
        self._current: float = 0.0
        self._progressbar = Gtk.ProgressBar()
        self.set_border_width(10)
        vbox_0: Gtk.Box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        if blurb_in:
            label_and_icon_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            blurb_label: Gtk.Label = Gtk.Label(label=blurb_in)
            label_and_icon_box.pack_start(child=blurb_label, expand=False, fill=False, padding=0)  # noqa
            label_and_icon_box.set_margin_start(40)
            label_and_icon_box.set_margin_end(40)
            label_and_icon_box.show_all()  # noqa
            vbox_0.add(label_and_icon_box)  # noqa
        self.add(vbox_0)
        # show_text_button: Gtk.CheckButton = Gtk.CheckButton(label="Show text")
        activity_button: Gtk.CheckButton = Gtk.CheckButton(label="Activity mode")
        r2l_button: Gtk.CheckButton = Gtk.CheckButton(label="Right to Left")

        # show_text_button.connect("toggled", self.on_show_text_toggled)
        activity_button.connect("toggled", self.on_activity_mode_toggled)
        r2l_button.connect("toggled", self.on_right_to_left_toggled)

        vbox_0.pack_start(self._progressbar, True, True, 0)
        # vbox_0.pack_start(show_text_button, True, True, 0)
        vbox_0.pack_start(activity_button, True, True, 0)
        vbox_0.pack_start(r2l_button, True, True, 0)

        self._progressbar.set_fraction(fraction=0)

    @property
    def activity_mode(self) -> bool:
        return self._activity_mode

    @activity_mode.setter
    def activity_mode(self, activity: bool):
        self._activity_mode = activity

    @property
    def total(self) -> float:
        return self._total

    @property
    def fraction(self) -> float:
        return self._progressbar.get_fraction()

    @property
    def progress_value(self) -> float:
        return self.fraction * self.total

    @progress_value.setter
    def progress_value(self, value: float):
        fraction: float = 0.0
        if value > 0.0:
            fraction = value/self.total
        LOGGER_PRSTU.debug(f"argument value={value}; setting fraction={fraction}")
        self._progressbar.set_fraction(fraction=fraction)

    # def on_show_text_toggled(self, button):
    #     show_text = button.get_active()
    #     if show_text:
    #         text = "some text"
    #     else:
    #         text = None
    #     self._progressbar.set_text(text)
    #     self._progressbar.set_show_text(show_text)

    def on_activity_mode_toggled(self, button):
        self._activity_mode = button.get_active()
        if self._activity_mode:
            self._progressbar.pulse()
        else:
            self.progress_value = 0.0

    def on_right_to_left_toggled(self, button):
        value = button.get_active()
        self._progressbar.set_inverted(value)

    def pulse_progress(self):
        self._progressbar.pulse()


# noinspection PyUnresolvedReferences
def example_progress_0():
    win: ProgressBarWindow = ProgressBarWindow(title_in="Progress Demo", blurb_in="Look at it go!", total=10.0)

    def on_timeout(self, user_data=None):
        nonlocal win
        """
        Update value on the progress bar
        """
        if win.activity_mode:
            win.pulse_progress()
        else:
            new_value = win.progress_value + .1
            if new_value > win.total:
                new_value = 0
            win.progress_value = new_value
        # As this is a timeout function, return True so that it
        # continues to get called
        return True

    timeout_id = GLib.timeout_add(50, on_timeout, None)

    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


def main() -> int:
    example_progress_0()
    return 0


if __name__ == '__main__':
    sys.exit(main())
