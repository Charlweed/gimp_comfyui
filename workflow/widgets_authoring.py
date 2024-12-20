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

import os.path

from utilities.long_term_storage_utils import *
from utilities.cui_resources_utils import *
from workflow.workflow_2_py_generator import *

METAKEY_FLAG = "±"  # The unicode is deliberate.
KEY_SUFFIX_DEBUG_LAYOUT = f"{METAKEY_FLAG}debug_layout{METAKEY_FLAG}"  # w_text keys with this suffix are newline flags.
KEY_SUFFIX_NEWLINE: str = f"{METAKEY_FLAG}newline{METAKEY_FLAG}"  # w_text keys with this suffix are newline flags.
# w_text keys with this suffix are the count of horizontal cells in a layout grid.
KEY_SUFFIX_GRID_WIDTH: str = f"{METAKEY_FLAG}grid_width{METAKEY_FLAG}"
# w_text keys with this suffix are the count of vertical cells in a layout grid.
KEY_SUFFIX_GRID_HEIGHT: str = f"{METAKEY_FLAG}grid_width{METAKEY_FLAG}"
NEGATIVE_PROMPT_TITLE_REGEX_1_PATTERN = r".*negative.*prompt|text.*"
NEGATIVE_PROMPT_TITLE_REGEX_1 = re.compile(NEGATIVE_PROMPT_TITLE_REGEX_1_PATTERN)
NEGATIVE_PROMPT_INPUT_REGEX_1_PATTERN = r".*negative.*"
NEGATIVE_PROMPT_INPUT_REGEX_1 = re.compile(NEGATIVE_PROMPT_INPUT_REGEX_1_PATTERN)


def append_newline_suffix(original_key: str) -> str:
    """
    Appends the newline suffix to a string, so that key can be used to retrieve the value of the newline flag.
    :param original_key: The original_key
    :return: The original_key with KEY_SUFFIX_NEWLINE appended.
    """
    return f"{original_key}{KEY_SUFFIX_NEWLINE}"


def index_or_not(entries: List[str], selected_entry: str, unselectable_entry: str | None = None) -> int:
    if unselectable_entry is None or (not unselectable_entry):
        return entries.index(selected_entry)
    if selected_entry == unselectable_entry:
        LOGGER_WF2PY.warning(f"Nullifying {unselectable_entry}")
        sel_idx: int = -1
    else:
        sel_idx: int = entries.index(selected_entry)
    return sel_idx


def list_as_literals(values: List[str]) -> str:
    return ', '.join(f'"{w}"' for w in values)


def handler_header(handler_id: str) -> str:
    return "def %s(source, **args):  # noqa\n" % handler_id


def indent_a(start: int, source_identifier: str, infix: str) -> str:
    id_len: int = len(source_identifier)
    infix_len: int = len(infix)
    indent: int = start + id_len + infix_len
    return " " * indent


def probably_negative_prompt_title(some_string: str) -> bool:
    if not some_string:
        raise ValueError("some_string argument cannot be empty")
    return bool(NEGATIVE_PROMPT_TITLE_REGEX_1.search(some_string.lower()))


def probably_negative_prompt_input(some_string: str) -> bool:
    if not some_string:
        raise ValueError("some_string argument cannot be empty")
    return bool(NEGATIVE_PROMPT_INPUT_REGEX_1.search(some_string.lower()))


def new_checkbutton(node_index_str: str,
                    node_title: str,  # noqa. Reserved
                    input_name: str,
                    toggled_handler_body_txt: str,
                    current: bool,
                    label: str | None = None,
                    bool_style: BoolStyle = BoolStyle.FALSE_TRUE
                    ) -> Dict[str, str]:
    result: Dict[str, str] = {}
    widget_id: str = f"checkbutton_{node_index_str}_{input_name}"
    handler_id: str = f"toggled_handler_{node_index_str}_{input_name}"
    if label is not None and label.strip():
        label_out: str = label
    else:
        label_out: str = snake_to_title(in_str=input_name)

    # logging.info(f"Creating {widget_id} node_title=\"{node_title}\", identifier_base=\"input_name\"")
    widget_declaration: str = f"{SP08}{widget_id}: Gtk.CheckButton = Gtk.CheckButton.new_with_label(\"{label_out}\")  # noqa\n"  # noqa
    widget_config: str = (f"{SP08}{widget_id}.set_name(\"{widget_id}\")\n"
                          f"{SP08}{widget_id}.set_hexpand(False)\n")
    content_assignment = f"{SP08}{widget_id}.set_active({str(current)})\n"
    hh = handler_header(handler_id)
    handler_definition = f"\n{SP08}{hh}{SP12}{toggled_handler_body_txt}\n"
    handler_assignment = f"{SP08}{widget_id}.connect(SIG_TOGGLED, {handler_id})\n"
    getter_id: str = f"getter_{node_index_str}_{input_name}"
    if bool_style == BoolStyle.FALSE_TRUE:
        getter_code = (f"\n{SP08}def {getter_id}():\n"
                       f"{SP12}return {widget_id}.get_active()\n")  # noqa
    else:
        getter_code = (f"\n{SP08}def {getter_id}():\n"
                       f"{SP12}return \"{bool_style.true_string}\" if {widget_id}.get_active() "
                       f"else \"{bool_style.false_string}\"\n")  # noqa
    content_access = f"{SP08}widget_getters[{widget_id}.get_name()] = {getter_id}  # noqa\n"
    text: str = ""
    text += widget_declaration
    text += content_assignment
    text += widget_config  # Must be after content_assignment
    text += handler_definition
    text += handler_assignment
    text += getter_code
    text += content_access
    result[widget_id] = text
    return result


def new_treeview_layer(node_index_str,
                       node_title: str,  # noqa reserved
                       input_name: str,
                       ) -> Dict[str, str]:
    result: Dict[str, str] = {}
    widget_id: str = "treeview_%s_%s" % (node_index_str, input_name)
    widget_declaration: str = f"{SP08}{widget_id}: LayerTreeView = LayerTreeView()\n"
    infix_str = ".select_path = ids_to_treepath("
    indentation = indent_a(start=12, source_identifier=widget_id, infix=infix_str)
    widget_config: str = (f"{SP08}{widget_id}.set_name(\"{widget_id}\")\n"
                          f"{SP08}{widget_id}.set_hexpand(True)\n"
                          f"{SP08}prev_selected_route = self._installation_persister.configuration.get('{widget_id}_selection_route', None)\n"  # noqa
                          f"{SP08}if prev_selected_route is not None:\n"
                          f"{SP12}{widget_id}{infix_str}model={widget_id}.get_model(),\n"
                          f"{indentation}image_id=prev_selected_route[0],\n"
                          f"{indentation}layer_id=prev_selected_route[1])\n"
                          # f"{SP08}else:\n"
                          # f"{SP12}message = \"No prev_selected_route for {widget_id}\"\n"
                          # f"{SP12}LOGGER_SDGUIU.warning(message)\n"
                          # f"{SP12}Gimp.message(message)\n"
                          "\n"
                          )
    selection_handler: str = (
        f"{SP08}def selection_handler_{node_index_str}_{input_name}(selection: Gtk.TreeSelection):\n"  # noqa
        f"{SP12}model, treeiter = selection.get_selected()\n"
        f"{SP12}if treeiter is not None:\n"
        f"{SP16}sel_path: Gtk.TreePath = model.get_path(treeiter)\n"
        f"{SP16}sel_route: tuple[int, int] = treepath_to_ids(model=model, layer_path=sel_path)\n"
        f"{SP16}self._installation_persister.update_config({{'{widget_id}_selection_route': sel_route}})\n"  # noqa
        f"{SP16}self._installation_persister.store_config()\n"
        # f"{SP12}else:\n"
        # f"{SP16}message0 = \"No selected path for {widget_id}\"\n"
        # f"{SP16}LOGGER_SDGUIU.warning(message0)\n"
        # f"{SP16}Gimp.message(message0)\n"
        "\n"
        f"{SP08}{widget_id}.get_selection().connect(\"changed\", selection_handler_{node_index_str}_{input_name})\n"
    )
    content_access = f"{SP08}widget_getters[{widget_id}.get_name()] = {widget_id}.get_selected_png_leaf  # noqa\n"
    text: str = ""
    text += widget_declaration
    text += widget_config  # Must be after content_assignment
    text += selection_handler
    text += content_access
    result[widget_id] = text
    return result


def new_combo_fs(node_index_str: str,
                 node_title: str,  # noqa. Reserved
                 input_name: str,
                 change_handler_body_txt: str,
                 config_key: str,
                 selected_index: int = 0,
                 predicate_name: str = "seems_json"
                 ) -> Dict[str, str]:
    """
    This function is deprecated, because it depends on ComfyUI resources being installed on the local filesystem.
    It will probably be removed in a future release.
    The @deprecated decorator is provided by the deprecation module, but that module does not seem readily available in
     GIMP 3 python installations. Therefore, it is not used here.
    :param node_index_str:
    :param node_title:
    :param input_name:
    :param change_handler_body_txt:
    :param config_key:
    :param selected_index:
    :param predicate_name:
    :return:
    """
    result: Dict[str, str] = {}
    widget_id: str = "comboboxtext_%s_%s" % (node_index_str, input_name)
    handler_id: str = "change_handler_%s_%s" % (node_index_str, input_name)
    combo_values_id: str = "combo_values_%s_%s" % (node_index_str, input_name)
    fs_path_id: str = "fspath_%s_%s" % (node_index_str, input_name)
    config_referencer: str = f"self._installation_persister.configuration['{config_key}']"
    config_referencer_meta: str = "{"f"{config_referencer}""}"
    widget_declaration: str = f"{SP08}{widget_id}: Gtk.ComboBoxText = Gtk.ComboBoxText.new()\n"
    widget_config: str = (f"{SP08}{widget_id}.set_name(\"{widget_id}\")\n"
                          f"{SP08}{widget_id}.set_hexpand(True)\n"
                          f"{SP08}{widget_id}.set_active({selected_index})\n")
    content_list_declaration: str = (f"{SP08}{fs_path_id} = {config_referencer}\n"
                                     f"{SP08}{combo_values_id}: list[str]"
                                     f" = list_from_fs(fs_path={fs_path_id}, predicate={predicate_name})\n")
    fault_checking: str = (f"{SP08}if {combo_values_id} is None:\n"
                           f"{SP12}raise SystemError(f\"list_from_fs() returned None.\")\n"
                           f"{SP08}if not {combo_values_id}:\n"
                           f"{SP12}raise ValueError(fr\"No items retrieved from {config_referencer_meta}\")  # noqa\n")  # noqa
    content_assignment = (f"{SP08}for combo_item_path in {combo_values_id}:\n"
                          f"{SP12}{widget_id}.append_text(combo_item_path)\n")
    hh = handler_header(handler_id)
    handler_definition = f"\n{SP08}{hh}{SP12}{change_handler_body_txt}\n"
    handler_assignment = f"{SP08}{widget_id}.connect(SIG_CHANGED, {handler_id})\n"
    setter_id: str = f"setter_{node_index_str}_{input_name}"
    setter_code = f"""
    def {setter_id}(a_val: str):
        nonlocal {combo_values_id}
        selected_index = {combo_values_id}.index(a_val)
        {widget_id}.set_active(selected_index)\n"""
    content_access = f"{SP08}widget_getters[{widget_id}.get_name()] = {widget_id}.get_active_text  # noqa\n"
    widget_filling = f"{SP08}widget_setters[{widget_id}.get_name()] = {setter_id}  # noqa\n"
    text: str = ""
    text += widget_declaration
    text += content_list_declaration
    text += fault_checking
    text += content_assignment
    text += widget_config  # Must be after content_assignment
    text += handler_definition
    text += handler_assignment
    text += setter_code
    text += content_access
    text += widget_filling
    result[widget_id] = text
    return result


def new_combo_models(node_index_str: str,
                     node_title: str,  # noqa. Reserved
                     input_name: str,
                     change_handler_body_txt: str,
                     model_type: ModelType,
                     selected_index: int = 0,
                     special_entries: List[str] | None = None,
                     ) -> Dict[str, str]:
    result: Dict[str, str] = {}
    widget_id: str = "comboboxtext_%s_%s" % (node_index_str, input_name)
    handler_id: str = "change_handler_%s_%s" % (node_index_str, input_name)
    combo_values_id: str = "combo_values_%s_%s" % (node_index_str, input_name)
    widget_declaration: str = f"{SP08}{widget_id}: Gtk.ComboBoxText = Gtk.ComboBoxText.new()\n"
    widget_config: str = (f"{SP08}{widget_id}.set_name(\"{widget_id}\")\n"
                          f"{SP08}{widget_id}.set_hexpand(True)\n"
                          f"{SP08}{widget_id}.set_active({selected_index})\n")
    content_list_declaration: str = (f"{SP08}{combo_values_id}: list[str]"
                                     f" = get_models_filenames(\n"
                                     f"{SP12}model_type={model_type},\n"
                                     f"{SP12}cu_origin=self.comfy_svr_origin)\n")
    fault_checking: str = (f"{SP08}if {combo_values_id} is None:\n"
                           f"{SP12}raise SystemError(f\"get_models_filenames() returned None.\")\n"
                           f"{SP08}if not {combo_values_id}:\n"
                           f"{SP12}raise ValueError(fr\"No models retrieved from ComfyUI\")\n")
    if special_entries is not None and special_entries:
        content_assignment = (
            f"{SP08}{combo_values_id} = {special_entries} + {combo_values_id}\n"
            f"{SP08}for combo_item_path in {combo_values_id}:\n"
            f"{SP12}{widget_id}.append_text(combo_item_path)\n")
    else:
        content_assignment = (f"{SP08}for combo_item_path in {combo_values_id}:\n"
                              f"{SP12}{widget_id}.append_text(combo_item_path)\n")
    hh = handler_header(handler_id)
    handler_definition = f"\n{SP08}{hh}{SP12}{change_handler_body_txt}\n"
    handler_assignment = f"{SP08}{widget_id}.connect(SIG_CHANGED, {handler_id})\n"
    setter_id: str = f"setter_{node_index_str}_{input_name}"
    setter_code = f"""
        def {setter_id}(a_val: str):
            nonlocal {combo_values_id}
            selected_index = {combo_values_id}.index(a_val)
            {widget_id}.set_active(selected_index)\n"""
    content_access = f"{SP08}widget_getters[{widget_id}.get_name()] = {widget_id}.get_active_text  # noqa\n"
    widget_filling = f"{SP08}widget_setters[{widget_id}.get_name()] = {setter_id}  # noqa\n"
    text: str = ""
    text += widget_declaration
    text += content_list_declaration
    text += fault_checking
    text += content_assignment
    text += widget_config  # Must be after content_assignment
    text += handler_definition
    text += handler_assignment
    text += setter_code
    text += content_access
    text += widget_filling
    result[widget_id] = text
    return result


def new_combo_static(node_index_str: str,
                     node_title: str,  # noqa. Reserved
                     input_name: str,
                     items: List[str],
                     selected_index: int = 0,
                     change_handler_body_txt: str = "pass",
                     ) -> Dict[str, str]:
    result: Dict[str, str] = {}
    widget_id: str = "comboboxtext_%s_%s" % (node_index_str, input_name)
    handler_id: str = "change_handler_%s_%s" % (node_index_str, input_name)
    combo_values_id: str = "combo_values_%s_%s" % (node_index_str, input_name)
    combo_value_literals = list_as_literals(items)
    widget_declaration: str = f"{SP08}{widget_id}: Gtk.ComboBoxText = Gtk.ComboBoxText.new()\n"
    widget_config: str = (f"{SP08}{widget_id}.set_name(\"{widget_id}\")\n"
                          f"{SP08}{widget_id}.set_hexpand(True)\n"
                          f"{SP08}{widget_id}.set_active({selected_index})\n")
    content_list_declaration: str = f"{SP08}{combo_values_id}: list[str] = [{combo_value_literals}]  # noqa\n"
    content_assignment = (f"{SP08}for combo_item_path in {combo_values_id}:\n"
                          f"{SP12}{widget_id}.append_text(combo_item_path)\n")
    hh = handler_header(handler_id)
    handler_definition = f"\n{SP08}{hh}{SP12}{change_handler_body_txt}\n"
    handler_assignment = f"{SP08}{widget_id}.connect(SIG_CHANGED, {handler_id})\n"
    setter_id: str = f"setter_{node_index_str}_{input_name}"
    setter_code = f"""
        def {setter_id}(a_val: str):
            nonlocal {combo_values_id}
            selected_index = {combo_values_id}.index(a_val)
            {widget_id}.set_active(selected_index)
"""
    content_access = f"{SP08}widget_getters[{widget_id}.get_name()] = {widget_id}.get_active_text  # noqa\n"
    widget_filling = f"{SP08}widget_setters[{widget_id}.get_name()] = {setter_id}  # noqa\n"
    text: str = ""
    text += widget_declaration
    text += content_list_declaration
    text += content_assignment
    text += widget_config  # Must be after content_assignment
    text += handler_definition
    text += handler_assignment
    text += setter_code
    text += content_access
    text += widget_filling
    result[widget_id] = text
    return result


def new_entry_float(node_index_str: str,
                    node_title: str,  # noqa. Reserved
                    input_name: str,
                    change_handler_body_txt: str,
                    current: float,
                    bounds: tuple | None = None,
                    ) -> Dict[str, str]:
    result: Dict[str, str] = {}
    widget_id: str = "entry_%s_%s" % (node_index_str, input_name)
    handler_id: str = "change_handler_%s_%s" % (node_index_str, input_name)
    # logging.info("Creating %s node_title=\"%s\", identifier_base=\"%s\"" % (widget_id, node_title, input_name))
    widget_declaration: str = f"{SP08}{widget_id}: Gtk.Entry = Gtk.Entry.new()\n"
    content_assignment: str = f"{SP08}{widget_id}.set_text(str({current}))\n"
    widget_config: str = (f"{SP08}{widget_id}.set_name(\"{widget_id}\")\n"
                          f"{SP08}{widget_id}.set_hexpand(True)\n")
    widget_restrictions: str
    if bounds is None:
        widget_restrictions = f"{SP08}restrict_to_numbers(entry_widget={widget_id})\n"
    else:
        minimum = bounds[0]
        maximum = bounds[1]
        widget_restrictions = (f"{SP08}validate_in_bounds(entry_widget={widget_id},\n"
                               f"{SP27}minimum={minimum}, maximum={maximum},  # noqa\n"
                               f"{SP27}int_only=False,\n"
                               f"{SP27}track_invalid_widgets=track_invalid_widgets)\n")
    # LOGGER_WF2PY.info(widget_restrictions)
    hh = handler_header(handler_id)
    handler_definition = f"\n{SP08}{hh}{SP12}{change_handler_body_txt}\n"
    handler_assignment = f"{SP08}{widget_id}.connect(SIG_CHANGED, {handler_id})\n"
    getter_id: str = f"getter_{node_index_str}_{input_name}"
    setter_id: str = f"setter_{node_index_str}_{input_name}"
    getter_code = f"""
        def {getter_id}() -> float:
            return float({widget_id}.get_text())
"""
    setter_code = f"""
        def {setter_id}(a_val: float):
            {widget_id}.set_text(str(a_val))
"""
    content_access = f"{SP08}widget_getters[{widget_id}.get_name()] = {getter_id}  # noqa\n"
    widget_filling = f"{SP08}widget_setters[{widget_id}.get_name()] = {setter_id}  # noqa\n"
    text: str = ""
    text += widget_declaration
    text += content_assignment
    text += widget_config  # Must be after content_assignment
    text += widget_restrictions  # Must be after widget_config
    text += handler_definition
    text += handler_assignment
    text += getter_code
    text += setter_code
    text += content_access
    text += widget_filling
    result[widget_id] = text
    return result


def new_entry_int(node_index_str: str,
                  node_title: str,  # noqa. Reserved
                  input_name: str,
                  change_handler_body_txt: str,
                  current: int,
                  bounds: tuple | None = None,
                  ) -> Dict[str, str]:
    result: Dict[str, str] = {}
    widget_id: str = "entry_%s_%s" % (node_index_str, input_name)
    handler_id: str = "change_handler_%s_%s" % (node_index_str, input_name)
    # logging.info("Creating %s node_title=\"%s\", identifier_base=\"%s\"" % (widget_id, node_title, input_name))
    widget_declaration: str = f"{SP08}{widget_id}: Gtk.Entry = Gtk.Entry.new()\n"
    content_assignment: str = f"{SP08}{widget_id}.set_text(str({current}))\n"
    widget_config: str = (f"{SP08}{widget_id}.set_name(\"{widget_id}\")\n"
                          f"{SP08}{widget_id}.set_hexpand(True)\n")
    widget_restrictions: str
    if bounds is None:
        widget_restrictions = f"{SP08}restrict_to_ints(entry_widget={widget_id})\n"
    else:
        minimum = bounds[0]
        maximum = bounds[1]
        widget_restrictions = (f"{SP08}validate_in_bounds(entry_widget={widget_id},\n"
                               f"{SP27}minimum={minimum}, maximum={maximum},  # noqa\n"
                               f"{SP27}int_only=True,\n"
                               f"{SP27}track_invalid_widgets=track_invalid_widgets)\n")
    # LOGGER_WF2PY.info(widget_restrictions)
    hh = handler_header(handler_id)
    handler_definition = f"\n{SP08}{hh}{SP12}{change_handler_body_txt}\n"
    handler_assignment = f"{SP08}{widget_id}.connect(SIG_CHANGED, {handler_id})\n"
    getter_id: str = f"getter_{node_index_str}_{input_name}"
    setter_id: str = f"setter_{node_index_str}_{input_name}"
    getter_code = f"""
        def {getter_id}() -> int:
            return int({widget_id}.get_text())
"""
    setter_code = f"""
        def {setter_id}(a_val: int):
            {widget_id}.set_text(str(a_val))
"""
    content_access = f"{SP08}widget_getters[{widget_id}.get_name()] = {getter_id}  # noqa\n"
    widget_filling = f"{SP08}widget_setters[{widget_id}.get_name()] = {setter_id}  # noqa\n"
    text: str = ""
    text += widget_declaration
    text += content_assignment
    text += widget_config  # Must be after content_assignment
    text += widget_restrictions  # Must be after widget_config
    text += handler_definition
    text += handler_assignment
    text += getter_code
    text += setter_code
    text += content_access
    text += widget_filling
    result[widget_id] = text
    return result


def new_entry_str(node_index_str: str,
                  node_title: str,  # noqa. Reserved
                  input_name: str,
                  current: str,
                  change_handler_body_txt: str = "pass"  # noqa
                  ) -> Dict[str, str]:
    result: Dict[str, str] = {}
    widget_id: str = f"entry_{node_index_str}_{input_name}"
    # handler_id: str = "change_handler_%s_%s" % (node_index_str, input_name)
    # logging.info("Creating %s node_title=\"%s\", identifier_base=\"%s\"" % (widget_id, node_title, input_name))
    widget_declaration: str = f"{SP08}{widget_id}: Gtk.Entry = Gtk.Entry.new()\n"
    cleaned: str = ' '.join(current.splitlines())
    content_assignment: str = f"{SP08}{widget_id}.set_text(\"{cleaned}\")\n"
    widget_config: str = (f"{SP08}{widget_id}.set_name(\"{widget_id}\")\n"
                          f"{SP08}{widget_id}.set_hexpand(True)\n")
    widget_restrictions: str
    # hh = handler_header(handler_id)
    # handler_definition = f"\n{SP08}{hh}{SP12}{change_handler_body_txt}\n"
    # handler_assignment = f"{SP08}{widget_id}.connect(SIG_CHANGED, {handler_id})\n"
    content_access = f"{SP08}widget_getters[{widget_id}.get_name()] = {widget_id}.get_text\n"
    widget_filling = f"{SP08}widget_setters[{widget_id}.get_name()] = {widget_id}.set_text\n"
    text: str = ""
    text += widget_declaration
    text += content_assignment
    text += widget_config  # Must be after content_assignment
    # text += handler_definition
    # text += handler_assignment
    text += content_access
    text += widget_filling
    result[widget_id] = text
    return result


def new_label(node_index_str: str,
              node_title: str,  # noqa. Reserved
              input_name: str,
              ) -> Dict[str, str]:
    widgets_dict: Dict[str, str] = {}
    widget_id: str = "label_%s_%s" % (node_index_str, input_name)
    label_declaration = "%s%s: Gtk.Label = Gtk.Label.new(\"%s\")" % (SP08, widget_id, input_name.title())
    margin_start: int = 8  # Should this sometimes be 2?
    label_configuration = (f"{SP08}{widget_id}.set_margin_start({margin_start})\n"
                           f"{SP08}{widget_id}.set_alignment(0.95, 0)  # noqa"
                           )
    widgets_dict[widget_id] = f"{label_declaration}\n{label_configuration}"
    return widgets_dict


def prefix_label(node_index_str: str,
                 node_title: str,  # noqa. Reserved
                 input_name: str,
                 subject_widgets_dict: Dict[str, str]
                 ) -> Dict[str, str]:
    label_dict: Dict[str, str] = new_label(node_index_str=node_index_str,
                                           node_title=node_title,
                                           input_name=input_name)
    widgets_dict: Dict[str, str] = label_dict | subject_widgets_dict
    return widgets_dict


def new_null_widget(node_index_str: str,
                    input_name: str,
                    ) -> Dict[str, str]:
    """
    Creates a dict entry with a widget_id, but an empty value. This non-empty dict can stop further processing,
     without inserting widget text.
    :param node_index_str: The node id/index.
    :param input_name:  The name of the input.
    :return:
    """
    result: Dict[str, str] = {}
    widget_id: str = f"null_widget_{node_index_str}_{input_name}"
    result[widget_id] = ""
    return result


def new_scale(node_index_str: str,
              node_title: str,  # noqa. Reserved
              input_name: str,
              current: float,
              lower: float = 0,
              upper: float = 100,
              step_increment: float = 1,
              page_increment: float = 5,
              change_handler_body_txt: str = "pass",
              ) -> Dict[str, str]:
    result: Dict[str, str] = {}
    widget_id: str = "scale_%s_%s" % (node_index_str, input_name)
    handler_id: str = "change_handler_%s_%s" % (node_index_str, input_name)
    # logging.info("Creating %s node_title=\"%s\", identifier_base=\"%s\"" % (widget_id, node_title, input_name))
    adjustment_id: str = "adjustment_%s_%s" % (node_index_str, input_name)
    infix_str = ": Gtk.Adjustment = Gtk.Adjustment("
    arg_indent = indent_a(start=8, source_identifier=adjustment_id, infix=infix_str)

    adjustment_declaration: str = ("%s%s%svalue=%5.5f,\n"
                                   "%slower=%5.5f,\n"
                                   "%supper=%5.5f,\n"
                                   "%sstep_increment=%3.3f,\n"
                                   "%spage_increment=%3.3f,\n"
                                   "%spage_size=0)\n" % (
                                       SP08, adjustment_id, infix_str, current,
                                       arg_indent, lower,
                                       arg_indent, upper,
                                       arg_indent, step_increment,
                                       arg_indent, page_increment,
                                       arg_indent
                                   )
                                   )
    widget_declaration = (f"{SP08}{widget_id}: Gtk.Scale = "
                          f"Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment={adjustment_id})  # noqa\n")
    precision: str = ""
    if (upper - lower) < 10:
        precision = f"{SP08}{widget_id}.set_digits(3)\n"
    widget_config: str = (f"{SP08}{widget_id}.set_name(\"{widget_id}\")\n"
                          f"{precision}"
                          f"{SP08}{widget_id}.set_value_pos(Gtk.PositionType.BOTTOM)\n"
                          f"{SP08}{widget_id}.set_hexpand(True)\n")
    hh = handler_header(handler_id)
    handler_definition = f"\n{SP08}{hh}{SP12}{change_handler_body_txt}\n"
    handler_assignment = f"{SP08}{widget_id}.connect(SIG_VALUE_CHANGED, {handler_id})\n"
    content_access = f"{SP08}widget_getters[{widget_id}.get_name()] = {widget_id}.get_value\n"
    widget_filling = f"{SP08}widget_setters[{widget_id}.get_name()] = {widget_id}.set_value\n"
    text: str = ""
    text += adjustment_declaration
    text += widget_declaration
    text += widget_config  # Must be after content_assignment
    text += handler_definition
    text += handler_assignment
    text += content_access
    text += widget_filling
    result[widget_id] = text
    return result


def new_textview(node_index_str: str,
                 node_title: str,  # noqa. Reserved
                 input_name: str,
                 preedit_handler_body_txt: str,
                 current: str,
                 lengthy: bool = False
                 ) -> Dict[str, str]:
    result: Dict[str, str] = {}
    widget_id: str = f"textview_{node_index_str}_{input_name}"
    scrollview_id: str = f"scrolled_window_{node_index_str}_{input_name}"
    handler_id: str = f"preedit_handler_{node_index_str}_{input_name}"
    # logging.debug("Creating %s node_title=\"%s\", identifier_base=\"%s\"" % (widget_id, node_title, input_name))
    widget_declaration: str = f"{SP08}{widget_id}: Gtk.TextView = Gtk.TextView.new()\n"
    cleaned: str = ' '.join(current.splitlines())
    content_assignment: str = f"{SP08}{widget_id}.get_buffer().set_text(\"{cleaned}\")  # noqa\n"  # noqa
    # Gtk.TextView is for multi-line strings. To get any widget to vertically expand, set_vexpand(true)
    # And possibly set_valign(Gtk.Align.FILL) to fill the expandable area.
    #   See:
    # https://lazka.github.io/pgi-docs/Gtk-3.0/classes/Widget.html#Gtk.Widget.set_valign
    # https://docs.gtk.org/gtk3/enum.Align.html
    # https://stackoverflow.com/questions/29985323/make-gtk-widget-fill-parent-window
    # https://docs.gtk.org/gtk3/enum.Align.html
    # https://lazka.github.io/pgi-docs/Gtk-3.0/mapping.html
    scroll_window_width = 864
    scroll_window_height = 288
    if probably_negative_prompt_title(node_title) or probably_negative_prompt_input(input_name):
        scroll_window_width = 288
        scroll_window_height = 96
    widget_config: str = (f"{SP08}{widget_id}.set_name(\"{widget_id}\")\n"
                          f"{SP08}{widget_id}.set_hexpand(True)\n"
                          f"{SP08}{widget_id}.set_vexpand({lengthy})\n"
                          f"{SP08}{widget_id}.set_valign(Gtk.Align.FILL)\n"
                          f"{SP08}# Create a ScrolledWindow to hold the TextView\n"
                          f"{SP08}{scrollview_id} = Gtk.ScrolledWindow()\n"
                          f"{SP08}{scrollview_id}.add({widget_id})  # noqa\n"
                          f"{SP08}{scrollview_id}.set_size_request({scroll_window_width}, {scroll_window_height})\n"
                          )
    widget_restrictions: str
    # LOGGER_WF2PY.info(widget_restrictions)
    hh = handler_header(handler_id)
    handler_definition = f"\n{SP08}{hh}{SP12}{preedit_handler_body_txt}\n"
    handler_assignment = f"{SP08}{widget_id}.connect(SIG_PREEDIT_CHANGED, {handler_id})\n"
    getter_id: str = f"getter_{node_index_str}_{input_name}"
    setter_id: str = f"setter_{node_index_str}_{input_name}"
    getter_code = f"""
        def {getter_id}():
            buffer: Gtk.TextBuffer = {widget_id}.get_buffer()
            start: Gtk.TextIter = buffer.get_start_iter()
            end: Gtk.TextIter = buffer.get_end_iter()
            return buffer.get_text(start, end, False)
"""
    setter_code = f"""
        def {setter_id}(a_val: str):
            {widget_id}.get_buffer().set_text(str(a_val))

"""
    content_access = f"{SP08}widget_getters[{widget_id}.get_name()] = {getter_id}\n"
    widget_filling = f"{SP08}widget_setters[{widget_id}.get_name()] = {setter_id}\n"
    text: str = ""
    text += widget_declaration
    text += content_assignment
    text += widget_config  # Must be after content_assignment

    text += handler_definition
    text += handler_assignment
    text += getter_code
    text += setter_code
    text += content_access
    text += widget_filling
    result[scrollview_id] = text
    return result


def set_row_continuation(result: Dict[str, str], input_name: str, end_row: bool = True) -> Dict[str, str]:
    if not result:
        raise ValueError("results argument cannot be empty.")
    if input_name is None:
        raise ValueError("input_name argument cannot be None (null)")
    if not input_name:
        raise ValueError("input_name argument cannot be blank.")
    metakey = append_newline_suffix(input_name)
    nls = str(end_row)
    result[metakey] = nls
    return result


def ends_row(result: Dict[str, str], input_name: str) -> Dict[str, str]:
    return set_row_continuation(result=result, input_name=input_name, end_row=True)


def continues_row(result: Dict[str, str], input_name: str) -> Dict[str, str]:
    return set_row_continuation(result=result, input_name=input_name, end_row=False)


class WidgetAuthor:
    PYTHON_CLASS_NAME: str = "WidgetAuthor"
    PYTHON_CLASS_UUID_STRING: str = "f48a906f-a13d-42a9-b21a-b288d3851187"
    PYTHON_CLASS_NAME_LONG: str = PYTHON_CLASS_NAME + "_" + PYTHON_CLASS_UUID_STRING
    SD_DATA_ROOT: str = sd_root_dir(create=True)
    make_sd_data_tree(SD_DATA_ROOT)
    _ABLEMENT = ["enable", "disable"]
    _BLEND_MODES = ["normal", "multiply", "screen", "overlay", "soft_light", "difference"]
    _CLIP_TYPE_NAMES = ["sdxl", "sd3", "flux", "sd3.5"]
    _CROP_METHODS = ["disabled", "center"]
    _DISCRETE_SAMPLING_METHODS = ["eps", "lcm", "v_prediction", "x0"]
    _KSAMPLER_NAMES = ["euler", "euler_ancestral", "heun", "heunpp2", "dpm_2", "dpm_2_ancestral",
                       "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_sde", "dpmpp_sde_gpu",
                       "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu", "ddpm",
                       "lcm"]
    _MIMIC_MODES = ["Constant", "Linear Down", "Cosine Down", "Half Cosine Down", "Linear Up", "Cosine Up",
                    "Half Cosine Up", "Power Up", "Power Down", "Linear Repeating", "Cosine Repeating", "Sawtooth"]
    _MODE_TYPES = ["Linear", "Chess", "None"]
    _SAMPLER_NAMES = _KSAMPLER_NAMES + ["ddim", "uni_pc", "uni_pc_bh2"]
    _SCALING_STARTPOINT = ["MEAN", "ZERO"]
    _SCHEDULER_NAMES = ["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"]
    _SEAM_FIX_MODES = ["None", "Band Pass", "Half Tile", "Half Tile + Intersections"]
    _TOKEN_NORMALIZATION = ["none", "mean", "length", "length+mean"]
    _UPSCALE_METHODS = ["nearest-exact", "bilinear", "area", "bicubic", "lanczos"]
    _UPSCALE_MODELS = ["4x_NMKD-Siax_200k.pth", "4x_NMKD-Superscale-SP_178000_G.pth", "4x-UltraSharp.pth",
                       "4xLexicaHAT.pth", "4xNomos2_hq_dat2.pth", "4xNomos2_hq_mosr.pth",
                       "8x_NMKD-Superscale_150000_G.pth", "NMKD Superscale.zip"]
    _VARIABILITY_MEASURE = ["AD", "STD"]
    _WEIGHT_INTERPRETATION = ["comfy", "A1111", "compel", "comfy++", "down_weight"]

    _CFG_MODES_DTF = _MIMIC_MODES.copy()

    _SD_MODELS_DIR = os.path.join(SD_DATA_ROOT, "models")
    _SD_PROMPTS_DIR = os.path.join(SD_DATA_ROOT, "prompts")
    _SD_WORKFLOWS_DIR = os.path.join(SD_DATA_ROOT, "workflows")
    _SD_CHECKPOINTS_DIR = os.path.join(_SD_MODELS_DIR, "checkpoints")
    _SD_CLIP_DIR = os.path.join(_SD_MODELS_DIR, "clip")
    _SD_CLIP_VISION_DIR = os.path.join(_SD_MODELS_DIR, "clip_vision")
    _SD_CONFIGS_DIR = os.path.join(_SD_MODELS_DIR, "configs")
    _SD_CONTROLNET_DIR = os.path.join(_SD_MODELS_DIR, "controlnets")
    _SD_DIFFUSERS_DIR = os.path.join(_SD_MODELS_DIR, "diffusers")
    _SD_EMBEDDINGS_DIR = os.path.join(_SD_MODELS_DIR, "embeddings")
    _SD_GLIGEN_DIR = os.path.join(_SD_MODELS_DIR, "gligen")
    _SD_HYPERNETWORKS_DIR = os.path.join(_SD_MODELS_DIR, "hypernetworks")
    _SD_LORAS_DIR = os.path.join(_SD_MODELS_DIR, "loras")
    _SD_STYLE_MODELS_DIR = os.path.join(_SD_MODELS_DIR, "style_models")
    _SD_UNET_DIR = os.path.join(_SD_MODELS_DIR, "unet")
    _SD_UPSCALE_MODELS_DIR = os.path.join(_SD_MODELS_DIR, "upscale_models")
    _SD_VAE_DIR = os.path.join(_SD_MODELS_DIR, "vae")

    _DEFAULT_CONFIG = {
        'prompts_base_positive': "beautiful ridiculous silly spaceship from science fiction",
        'prompts_base_negative': "noise, grit, blurry, watermark, text, people, person, hazy, malformed, deformed",
        'prompts_supporting_positive': "space, stars, outer space, starship",
        'prompts_supporting_negative': "aliens, ground, dirt, trees, grass, animals, cows",
        'blend_modes': ["normal", "multiply", "screen", "overlay", "soft_light", "difference"],
        'clip_type_names': ["sdxl", "sd3", "flux", "sd3.5"],
        'crop_methods': ["disabled", "center"],
        'discrete_sampling_methods': ["eps", "lcm", "v_prediction", "x0"],
        'ksampler_names': ["euler", "euler_ancestral", "heun", "heunpp2", "dpm_2", "dpm_2_ancestral",
                           "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_sde", "dpmpp_sde_gpu",
                           "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu", "ddpm",
                           "lcm"],
        'mimic_modes': ["Constant", "Linear Down", "Cosine Down", "Half Cosine Down", "Linear Up", "Cosine Up",
                        "Half Cosine Up", "Power Up", "Power Down", "Linear Repeating", "Cosine Repeating", "Sawtooth"],
        'mode_types': ["Linear", "Chess", "None"],
        'cfg_modes_dtf': ["Constant", "Linear Down", "Cosine Down", "Half Cosine Down", "Linear Up", "Cosine Up",
                          "Half Cosine Up", "Power Up", "Power Down", "Linear Repeating", "Cosine Repeating",
                          "Sawtooth"],
        'refiner_names': [],
        'scheduler_names': ["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"],
        'sampler_names': ["euler", "euler_ancestral", "heun", "heunpp2", "dpm_2", "dpm_2_ancestral",
                          "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_sde", "dpmpp_sde_gpu",
                          "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu", "ddpm",
                          "lcm", "ddim", "uni_pc", "uni_pc_bh2"],
        'scaling_startpoint': ["MEAN", "ZERO"],
        'seam_fix_modes': ["None", "Band Pass", "Half Tile", "Half Tile + Intersections"],
        'token_normalization': ["none", "mean", "length", "length+mean"],
        'upscale_methods': ["nearest-exact", "bilinear", "area", "bicubic", "lanczos"],
        'upscale_models': ["4x_NMKD-Siax_200k.pth", "4x_NMKD-Superscale-SP_178000_G.pth", "4x-UltraSharp.pth",
                           "4xLexicaHAT.pth", "4xNomos2_hq_dat2.pth", "4xNomos2_hq_mosr.pth",
                           "8x_NMKD-Superscale_150000_G.pth", "NMKD Superscale.zip"],
        'variability_measure': ["AD", "STD"],
        'weight_interpretation': ["comfy", "A1111", "compel", "comfy++", "down_weight"],
        'sd_data_root': SD_DATA_ROOT,
        'sd_models_dir': os.path.join(SD_DATA_ROOT, "models"),
        'sd_prompts_dir': os.path.join(SD_DATA_ROOT, "prompts"),
        'sd_workflows_dir': os.path.join(SD_DATA_ROOT, "workflows"),
        'sd_checkpoints_dir': os.path.join(_SD_MODELS_DIR, "checkpoints"),
        'sd_clip_dir': os.path.join(_SD_MODELS_DIR, "clip"),
        'sd_clip_vision_dir': os.path.join(_SD_MODELS_DIR, "clip_vision"),
        'sd_configs_dir': os.path.join(_SD_MODELS_DIR, "configs"),
        'sd_controlnet_dir': os.path.join(_SD_MODELS_DIR, "controlnets"),
        'sd_diffusers_dir': os.path.join(_SD_MODELS_DIR, "diffusers"),
        'sd_embeddings_dir': os.path.join(_SD_MODELS_DIR, "embeddings"),
        'sd_gligen_dir': os.path.join(_SD_MODELS_DIR, "gligen"),
        'sd_hypernetworks_dir': os.path.join(_SD_MODELS_DIR, "hypernetworks"),
        'sd_loras_dir': os.path.join(_SD_MODELS_DIR, "loras"),
        'sd_style_models_dir': os.path.join(_SD_MODELS_DIR, "style_models"),
        'sd_unet_dir': os.path.join(_SD_MODELS_DIR, "unet"),
        'sd_upscale_models_dir': os.path.join(_SD_MODELS_DIR, "upscale_models"),
        'sd_vae_dir': os.path.join(_SD_MODELS_DIR, "vae"),
    }

    @classmethod
    def get_authoring_config_path(cls) -> str:
        json_path: str = get_persistent_json_path(cls.PYTHON_CLASS_NAME_LONG)
        json_file_exists = os.path.exists(json_path)
        if not json_file_exists:
            LOGGER_PRSTU.debug(f"{json_path} does not exist.")
        return json_path

    @classmethod
    def read_authoring_config(cls) -> Dict:
        json_path: str = cls.get_authoring_config_path()
        json_file_exists = os.path.exists(json_path)
        if not json_file_exists:
            LOGGER_PRSTU.debug(f"{json_path} does not exist.")
            return cls._DEFAULT_CONFIG
        result: Dict = read_persistent_dictionary(cls.PYTHON_CLASS_NAME_LONG)
        return result

    @classmethod
    def write_authoring_config(cls, config: Dict):
        store_persistent_dictionary(cls.PYTHON_CLASS_NAME_LONG, dictionary=config)

    def __init__(self):
        self._config: Dict = dict(WidgetAuthor._DEFAULT_CONFIG)
        try:
            self.load_config()
        except IOError as ioe:
            LOGGER_WF2PY.exception(ioe)
            self._config = dict(WidgetAuthor._DEFAULT_CONFIG)
        self._blend_modes: List[str] = self._config['blend_modes']
        self._crop_methods: List[str] = self._config['crop_methods']
        self._discrete_sampling_methods = self._config['discrete_sampling_methods']
        # These predicates are in cui_resources_utils.py NOT long_term_storage_utils.py!
        self._models_checkpoints: List[str] = list_from_fs(fs_path=self._config['sd_checkpoints_dir'],
                                                           predicate=seems_checkpoint)
        self._models_clip: List[str] = list_from_fs(fs_path=self._config['sd_clip_dir'], predicate=seems_clip)
        self._models_configs: List[str] = list_from_fs(fs_path=self._config['sd_configs_dir'], predicate=seems_config)
        self._models_controlnet: List[str] = list_from_fs(fs_path=self._config['sd_controlnet_dir'],
                                                          predicate=seems_controlnet,
                                                          permitted_empties=["controlnets"])
        self._models_diffusers: List[str] = list_from_fs(fs_path=self._config['sd_diffusers_dir'],
                                                         predicate=seems_diffuser)
        self._models_loras: List[str] = list_from_fs(fs_path=self._config['sd_loras_dir'],
                                                     predicate=seems_lora)
        self._models_unet: List[str] = list_from_fs(fs_path=self._config['sd_unet_dir'],
                                                    predicate=seems_lora)
        self._models_upscale_models: List[str] = list_from_fs(fs_path=self._config['sd_upscale_models_dir'],
                                                              predicate=seems_pytorch)
        self._models_vae: List[str] = list_from_fs(fs_path=self._config['sd_vae_dir'], predicate=seems_vae)
        self._prompts_base_positive: List[str] = [self._config['prompts_base_positive'], ]
        self._prompts_base_negative: List[str] = [self._config['prompts_base_negative'], ]
        self._prompts_supporting_positive: List[str] = [self._config['prompts_supporting_positive'], ]
        self._prompts_supporting_negative: List[str] = [self._config['prompts_supporting_negative'], ]
        self._refiners: List[str] = [self._config['refiner_names'], ]
        self._samplers: List[str] = [self._config['sampler_names'], ]
        self._upscale_methods: List[str] = self._config['upscale_methods']

    @property
    def config(self) -> MappingProxyType:
        return MappingProxyType(self._config)

    def load_config(self) -> MappingProxyType:
        self._config = WidgetAuthor.read_authoring_config()
        return self.config

    def store_config(self):
        WidgetAuthor.write_authoring_config(self._config)

    # Avoid depending on this method, because Input Names are not unique nor consistent over node classes.
    def text_from_input_name(
            self,
            node_class_name: str,  # noqa
            node_index_str: str,
            node_title: str,
            input_name: str,
            json_value: str,
            newline: bool = True,
    ) -> Dict[str, str]:
        result: Dict[str, str] | None = None
        # log_msg: str = f"Using input \"{input_name}\" in node class {node_class_name}, entitled \"{node_title}\""
        # LOGGER_WF2PY.warning(log_msg)
        match input_name:
            case "add_noise":
                result = new_checkbutton(
                    node_title=node_title,
                    node_index_str=node_index_str,
                    input_name=input_name,
                    toggled_handler_body_txt="pass",
                    current=bool_of(json_value),
                    bool_style=BoolStyle.DISABLE_ENABLE
                )
            case "return_with_leftover_noise":
                result = new_checkbutton(
                    node_title=node_title,
                    node_index_str=node_index_str,
                    input_name=input_name,
                    toggled_handler_body_txt="pass",
                    bool_style=BoolStyle.DISABLE_ENABLE,
                    current=bool_of(json_value)
                )
                # Disable newline.
                newline = False  # Re-using parameters is generally bad practice, but exceptions must be made.
            case "ascore":
                result = new_entry_int(
                    node_title=node_title,
                    node_index_str=node_index_str,
                    input_name=input_name,
                    change_handler_body_txt="pass",
                    current=int(json_value),
                    bounds=(1, 10)
                )
            case "batch_size" | "height" | "width" | "crop_h" | "crop_w" | "target_width":
                result = new_entry_int(
                    node_title=node_title,
                    node_index_str=node_index_str,
                    input_name=input_name,
                    change_handler_body_txt="pass",
                    current=int(json_value),
                    bounds=(1, None)
                )
            case "target_height":
                result = new_entry_int(
                    node_title=node_title,
                    node_index_str=node_index_str,
                    input_name=input_name,
                    change_handler_body_txt="pass",
                    current=int(json_value),
                    bounds=(1, None)
                )
                # Insert newline.
                newline = True
            case "noise_seed" | "seed":
                result = new_entry_int(
                    node_title=node_title,
                    node_index_str=node_index_str,
                    input_name=input_name,
                    change_handler_body_txt="pass",
                    current=int(json_value),
                    bounds=(-1, INT_MAX)
                )
            case "steps":
                result = new_entry_int(
                    node_title=node_title,
                    node_index_str=node_index_str,
                    input_name=input_name,
                    change_handler_body_txt="pass",
                    current=int(json_value),
                    bounds=(1, None)
                )
                # Specify newline, overriding argument.
                newline = True
            case "start_at_step":
                result = new_entry_int(
                    node_title=node_title,
                    node_index_str=node_index_str,
                    input_name=input_name,
                    change_handler_body_txt="pass",
                    current=int(json_value),
                    bounds=(0, None)
                )
                # Specify newline, overriding argument.
                newline = False
            case "end_at_step":
                result = new_entry_int(
                    node_title=node_title,
                    node_index_str=node_index_str,
                    input_name=input_name,
                    change_handler_body_txt="pass",
                    current=int(json_value),
                    bounds=(0, None)
                )
                # Specify newline, overriding argument.
                newline = True
            # TODO: These inputs might have different bounds
            case "blend_factor" | "cfg" | "scale_by":
                result = new_entry_float(
                    node_title=node_title,
                    node_index_str=node_index_str,
                    input_name=input_name,
                    change_handler_body_txt="pass",
                    current=float(json_value),
                    bounds=(0, None)
                )
                # Specify newline, overriding argument.
                newline = True
            case "text" | "text_g" | "text_l":
                result = new_textview(
                    node_title=node_title,
                    node_index_str=node_index_str,
                    input_name=input_name,
                    preedit_handler_body_txt="pass",
                    current=json_value,
                    lengthy=True
                )
            case "blend_mode":
                sel_idx: int = self._blend_modes.index(json_value)
                result = new_combo_static(node_title=node_title,
                                          node_index_str=node_index_str,
                                          input_name=input_name,
                                          change_handler_body_txt="pass",
                                          items=self._blend_modes,
                                          selected_index=sel_idx
                                          )
            case "upscale_method":
                sel_idx: int = self._upscale_methods.index(json_value)
                result = new_combo_static(node_title=node_title,
                                          node_index_str=node_index_str,
                                          input_name=input_name,
                                          items=self._upscale_methods,
                                          selected_index=sel_idx
                                          )
            case "vae_name":
                vaes_from_fs = list_from_fs(fs_path=self._config['sd_vae_dir'], predicate=seems_vae)
                vae_literals = list_as_literals(vaes_from_fs)
                combo_message = f"Looking for index of {json_value} in {vae_literals}"
                LOGGER_WF2PY.info(combo_message)
                sel_idx: int = vaes_from_fs.index(json_value)  # Should be 1
                result = new_combo_models(node_title=node_title,
                                          node_index_str=node_index_str,
                                          input_name=input_name,
                                          change_handler_body_txt="pass",
                                          selected_index=sel_idx,
                                          model_type=ModelType.VAE
                                          )
            case _:
                pass
        # If widget text was written for this input, insert a new entry storing the newline flag.
        if result:
            metakey = append_newline_suffix(input_name)
            nls = str(newline)
            # if not newline:
            #     log_msg: str = f"text_from_input_name(): Inserting result[{metakey}]={nls}"
            #     LOGGER_WF2PY.warning(log_msg)
            result[metakey] = nls
        return result

    # This is the preferred way to obtain widget text, as it combines the node class name and the input name. It's
    # still not unique.
    def text_from_node_class_name(
            self,
            node_class_name: str,
            node_index_str: str,
            node_title: str,
            input_name: str,
            json_value: str,
            newline: bool = True,  # noqa
    ) -> Dict[str, str]:
        result: Dict[str, str] | None = None
        match node_class_name:
            case  "BasicScheduler":
                match input_name:
                    case "denoise":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            current=float(json_value),
                            lower=0.00001,
                            upper=1.0,
                            step_increment=0.001,
                            page_increment=0.01
                        )
                    case "scheduler":
                        sel_idx: int = WidgetAuthor._SCHEDULER_NAMES.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=WidgetAuthor._SCHEDULER_NAMES,
                                                  selected_index=sel_idx
                                                  )
                    case "steps":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(1, 128)
                        )
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "CheckpointLoaderSimple":
                sel_idx: int = self._models_checkpoints.index(json_value)
                result = new_combo_models(node_title=node_title,
                                          node_index_str=node_index_str,
                                          input_name=input_name,
                                          change_handler_body_txt="pass",
                                          selected_index=sel_idx,
                                          model_type=ModelType.CHECKPOINTS
                                          )
                ends_row(result=result, input_name=input_name)
            case "CLIPTextEncode":
                match input_name:
                    case "text" | "text_g" | "text_l":
                        result = new_textview(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            preedit_handler_body_txt="pass",
                            current=json_value,
                            lengthy=True
                        )
                        ends_row(result=result, input_name=input_name)
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "CLIPTextEncodeSDXL":
                match input_name:
                    case "height" | "width" | "crop_h" | "crop_w" | "target_width":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(1, None)
                        )
                        continues_row(result=result, input_name=input_name)
                    case  "target_height":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(1, None)
                        )
                        ends_row(result=result, input_name=input_name)
                    case "text" | "text_g" | "text_l":
                        result = new_textview(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            preedit_handler_body_txt="pass",
                            current=json_value,
                            lengthy=True
                        )
                        ends_row(result=result, input_name=input_name)
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "CLIPTextEncodeSDXLRefiner":
                match input_name:
                    case "ascore":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(1, 10)
                        )
                        continues_row(result=result, input_name=input_name)
                    case "width":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(1, None)
                        )
                        continues_row(result=result, input_name=input_name)
                    case  "height":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(1, None)
                        )
                        ends_row(result=result, input_name=input_name)
                    case "text" | "text_g" | "text_l":
                        result = new_textview(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            preedit_handler_body_txt="pass",
                            current=json_value,
                            lengthy=True
                        )
                        ends_row(result=result, input_name=input_name)
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "DualCLIPLoader":
                match input_name:
                    case "clip_name1" | "clip_name2":
                        sel_idx: int = self._models_clip.index(json_value)
                        result = new_combo_models(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  selected_index=sel_idx,
                                                  model_type=ModelType.CLIP
                                                  )
                        set_row_continuation(result=result, input_name=input_name, end_row=(input_name == "clip_name2"))
                    case "type":
                        sel_idx: int = WidgetAuthor._CLIP_TYPE_NAMES.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=WidgetAuthor._CLIP_TYPE_NAMES,
                                                  selected_index=sel_idx
                                                  )
                        ends_row(result=result, input_name=input_name)
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "EmptyLatentImage" | "EmptySD3LatentImage":
                match input_name:
                    case "batch_size" | "height" | "width" | "crop_h" | "crop_w" | "target_width":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(1, None)
                        )
                        continues_row(result=result, input_name=input_name)
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "FluxGuidance":
                match input_name:
                    case "guidance":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=float(json_value),
                            lower=0,
                            upper=10,
                            step_increment=1,
                            page_increment=2
                        )
                        result[KEY_SUFFIX_DEBUG_LAYOUT] = "True"
                        ends_row(result=result, input_name=input_name)
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "DynamicThresholdingFull":
                match input_name:
                    case "mimic_scale":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=float(json_value),
                            lower=0,
                            upper=100,
                            step_increment=1.0,
                            page_increment=10.0
                        )
                        result[KEY_SUFFIX_DEBUG_LAYOUT] = "True"
                        ends_row(result=result, input_name=input_name)
                    case "threshold_percentile":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=float(json_value),
                            lower=0,
                            upper=1.0,
                            step_increment=0.01,
                            page_increment=0.1
                        )
                        result[KEY_SUFFIX_DEBUG_LAYOUT] = "True"
                        ends_row(result=result, input_name=input_name)
                    case "mimic_mode":
                        sel_idx: int = WidgetAuthor._MIMIC_MODES.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=WidgetAuthor._MIMIC_MODES,
                                                  selected_index=sel_idx
                                                  )
                        continues_row(result=result, input_name=input_name)
                    case "mimic_scale_min":  # Blind guess as to scale and bounds.
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=float(json_value),
                            lower=0,
                            upper=1.0,
                            step_increment=0.01,
                            page_increment=0.1
                        )
                        result[KEY_SUFFIX_DEBUG_LAYOUT] = "True"
                        ends_row(result=result, input_name=input_name)
                    case "cfg_mode":
                        sel_idx: int = WidgetAuthor._CFG_MODES_DTF.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=WidgetAuthor._CFG_MODES_DTF,
                                                  selected_index=sel_idx
                                                  )
                        continues_row(result=result, input_name=input_name)
                    case "cfg_scale_min":  # Blind guess as to scale and bounds.
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=float(json_value),
                            lower=0,
                            upper=1.0,
                            step_increment=0.01,
                            page_increment=0.1
                        )
                        result[KEY_SUFFIX_DEBUG_LAYOUT] = "True"
                        ends_row(result=result, input_name=input_name)
                    case "sched_val":  # Blind guess as to scale and bounds.
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=float(json_value),
                            lower=0,
                            upper=1.0,
                            step_increment=0.01,
                            page_increment=0.1
                        )
                        ends_row(result=result, input_name=input_name)

                    case "separate_feature_channels":
                        sel_idx: int = WidgetAuthor._ABLEMENT.index(json_value)
                        combo_dict = new_combo_static(node_title=node_title,
                                                      node_index_str=node_index_str,
                                                      input_name=input_name,
                                                      change_handler_body_txt="pass",
                                                      items=WidgetAuthor._ABLEMENT,
                                                      selected_index=sel_idx
                                                      )
                        result = prefix_label(node_title=node_title,
                                              node_index_str=node_index_str,
                                              input_name=input_name,
                                              subject_widgets_dict=combo_dict)
                        continues_row(result=result, input_name=input_name)
                    case "scaling_startpoint":
                        sel_idx: int = WidgetAuthor._SCALING_STARTPOINT.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=WidgetAuthor._SCALING_STARTPOINT,
                                                  selected_index=sel_idx
                                                  )
                        continues_row(result=result, input_name=input_name)
                    case "variability_measure":
                        sel_idx: int = WidgetAuthor._VARIABILITY_MEASURE.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=WidgetAuthor._VARIABILITY_MEASURE,
                                                  selected_index=sel_idx
                                                  )
                        ends_row(result=result, input_name=input_name)
                    case "interpolate_phi":  # Blind guess as to scale and bounds.
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=float(json_value),
                            lower=0,
                            upper=1.0,
                            step_increment=0.01,
                            page_increment=0.1
                        )
                        ends_row(result=result, input_name=input_name)
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "Efficient Loader":
                match input_name:
                    case "ckpt_name":
                        checkpoints_from_fs = list_from_fs(fs_path=self._config['sd_checkpoints_dir'],
                                                           predicate=seems_checkpoint)
                        sel_idx: int = checkpoints_from_fs.index(json_value)
                        result = new_combo_models(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  selected_index=sel_idx,
                                                  model_type=ModelType.CHECKPOINTS
                                                  )
                    case "vae_name":
                        # We are constructing the dialog offline now, and also telling it what to expect from the
                        # ComfyUI server later. So we add our special_entries as an argument to list_from_fs AND as the
                        # special_entries argument to new_combo_models
                        # Baked VAE is a vae that's already merged into the checkpoint model.
                        vaes_from_fs = list_from_fs(fs_path=self._config['sd_vae_dir'],
                                                    predicate=seems_vae,
                                                    special_entries=['Baked VAE']
                                                    )
                        sel_idx: int = index_or_not(entries=vaes_from_fs, selected_entry=json_value)
                        result = new_combo_models(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  selected_index=sel_idx,
                                                  special_entries=['Baked VAE'],
                                                  model_type=ModelType.VAE
                                                  )
                    case "clip_skip":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(-1, INT_MAX)
                        )
                    case "lora_name":
                        # We are constructing the dialog offline now, and also telling it what to expect from the
                        # ComfyUI server later. So we add our special_entries as an argument to list_from_fs AND as the
                        # special_entries argument to new_combo_models.
                        # Also Confusing. The literal 'None' is (sometimes) returned as an entry by teh server, so we
                        # include it here as an entry for offline construction of the dialog source.
                        loras_from_fs = list_from_fs(fs_path=self._config['sd_loras_dir'],
                                                     predicate=seems_lora,
                                                     special_entries=['None'])
                        sel_idx: int = index_or_not(entries=loras_from_fs, selected_entry=json_value)
                        result = new_combo_models(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  selected_index=sel_idx,
                                                  special_entries=['None'],
                                                  model_type=ModelType.LORAS
                                                  )
                    case "lora_model_strength":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=float(json_value),
                            lower=0,
                            upper=20,
                            step_increment=1.0,
                            page_increment=5.0
                        )
                    case "lora_clip_strength":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=float(json_value),
                            lower=0,
                            upper=20,
                            step_increment=1.0,
                            page_increment=5.0
                        )
                    case "positive" | "negative":
                        result = new_textview(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            preedit_handler_body_txt="pass",
                            current=json_value,
                            lengthy=True
                        )
                    case "token_normalization":
                        sel_idx: int = WidgetAuthor._TOKEN_NORMALIZATION.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=WidgetAuthor._TOKEN_NORMALIZATION,
                                                  selected_index=sel_idx
                                                  )
                    case "weight_interpretation":
                        sel_idx: int = WidgetAuthor._WEIGHT_INTERPRETATION.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=WidgetAuthor._WEIGHT_INTERPRETATION,
                                                  selected_index=sel_idx
                                                  )
                    case "empty_latent_width" | "empty_latent_height":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(1, None)
                        )
                    case "batch_size":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(1, 256)  # Completely arbitrary.
                        )
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "ImpactKSamplerAdvancedBasicPipe":
                match input_name:
                    case "add_noise" | "return_with_leftover_noise":
                        result = new_checkbutton(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            toggled_handler_body_txt="pass",
                            current=bool_of(json_value)
                        )
                    case "noise_seed" | "seed":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(-1, INT_MAX)
                        )
                    case "steps":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(1, 128)
                        )
                    case "cfg":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=float(json_value),
                            lower=1,
                            upper=25,
                            step_increment=0.1,
                            page_increment=2
                        )
                        ends_row(result=result, input_name=input_name)
                    case "sampler_name":
                        sel_idx: int = WidgetAuthor._SAMPLER_NAMES.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=WidgetAuthor._SAMPLER_NAMES,
                                                  selected_index=sel_idx
                                                  )
                    case "scheduler":
                        sel_idx: int = WidgetAuthor._SCHEDULER_NAMES.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=WidgetAuthor._SCHEDULER_NAMES,
                                                  selected_index=sel_idx
                                                  )
                        ends_row(result=result, input_name=input_name)
                    case "start_at_step" | "end_at_step":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(0, None)
                        )
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "ImageBlend":
                match input_name:
                    case "blend_factor":
                        result = new_entry_float(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=float(json_value),
                            bounds=(0, None)
                        )
                    case "blend_mode":
                        sel_idx: int = self._blend_modes.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  items=self._blend_modes,
                                                  selected_index=sel_idx
                                                  )
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "ImageScale" | "ImageScaleBy":
                match input_name:
                    case "crop":
                        sel_idx: int = self._crop_methods.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=self._crop_methods,
                                                  selected_index=sel_idx
                                                  )
                    case "height" | "width":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(1, None)
                        )
                        continues_row(result=result, input_name=input_name)
                    case "scale_by":
                        result = new_entry_float(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=float(json_value),
                            bounds=(0, None)
                        )
                    case "upscale_method":
                        sel_idx: int = self._upscale_methods.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  items=self._upscale_methods,
                                                  selected_index=sel_idx
                                                  )
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "KSampler" | "KSamplerAdvanced" | "KSamplerSelect":
                match input_name:
                    case "add_noise":
                        result = new_checkbutton(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            toggled_handler_body_txt="pass",
                            current=bool_of(json_value),
                            bool_style=BoolStyle.DISABLE_ENABLE
                        )
                    case "cfg":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=float(json_value),
                            lower=1,
                            upper=25,
                            step_increment=0.1,
                            page_increment=2
                        )
                    case "denoise":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            current=float(json_value),
                            lower=0.00001,
                            upper=1.0,
                            step_increment=0.001,
                            page_increment=0.01
                        )
                    case "return_with_leftover_noise":
                        result = new_checkbutton(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            toggled_handler_body_txt="pass",
                            bool_style=BoolStyle.DISABLE_ENABLE,
                            current=bool_of(json_value)
                        )
                    case "sampler_name":
                        sel_idx: int = WidgetAuthor._SAMPLER_NAMES.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=WidgetAuthor._SAMPLER_NAMES,
                                                  selected_index=sel_idx
                                                  )
                    case "scheduler":
                        sel_idx: int = WidgetAuthor._SCHEDULER_NAMES.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=WidgetAuthor._SCHEDULER_NAMES,
                                                  selected_index=sel_idx
                                                  )
                    case "noise_seed" | "seed":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(-1, INT_MAX)
                        )
                    case "start_at_step":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(0, None)
                        )
                        continues_row(input_name=input_name, result=result)
                    case "end_at_step":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(0, None)
                        )
                    case "steps":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(1, 128)
                        )
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "LoraLoader":
                match input_name:
                    case "lora_name":
                        # We are constructing the dialog offline now, and also telling it what to expect from the
                        # ComfyUI server later. So we add our special_entries as an argument to list_from_fs AND as the
                        # special_entries argument to new_combo_models.
                        # Also Confusing. The literal 'None' is (sometimes) returned as an entry by teh server, so we
                        # include it here as an entry for offline construction of the dialog source.
                        loras_from_fs = list_from_fs(fs_path=self._config['sd_loras_dir'],
                                                     predicate=seems_lora,
                                                     special_entries=['None'])
                        sel_idx: int = index_or_not(entries=loras_from_fs, selected_entry=json_value)
                        result = new_combo_models(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  selected_index=sel_idx,
                                                  special_entries=['None'],
                                                  model_type=ModelType.LORAS
                                                  )
                    case "strength_model":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=float(json_value),
                            lower=0,
                            upper=20,
                            step_increment=1.0,
                            page_increment=5.0
                        )
                    case "strength_clip":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=float(json_value),
                            lower=0,
                            upper=20,
                            step_increment=1.0,
                            page_increment=5.0
                        )
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "ModelSamplingDiscrete":  # https://www.runcomfy.com/comfyui-nodes/ComfyUI/ModelSamplingDiscrete
                match input_name:
                    case "sampling":
                        sel_idx: int = self._discrete_sampling_methods.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=self._discrete_sampling_methods,
                                                  selected_index=sel_idx
                                                  )
                    case "zsnr":  # Is this value being correctly persisted?
                        result = new_checkbutton(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            toggled_handler_body_txt="pass",
                            current=bool_of(json_value)
                        )
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "ModelSamplingFlux":
                match input_name:
                    case "height" | "width":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(1, None)
                        )
                        continues_row(result=result, input_name=input_name)
                    case "max_shift" | "base_shift":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            current=float(json_value),
                            lower=0.00001,
                            upper=3.0,
                            step_increment=0.001,
                            page_increment=0.01
                        )
                        ends_row(result=result, input_name=input_name)
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "RandomNoise":
                match input_name:
                    case "noise_seed" | "seed":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(-1, INT_MAX)
                        )
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "SaveImage":
                match input_name:
                    case "filename_prefix":
                        current_val: str = "gimp_generated"
                        if "upscale" in node_title.lower():
                            current_val = "upscaled/gimp_generated"
                        result = new_entry_str(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            current=current_val)
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "SD_4XUpscale_Conditioning":
                match input_name:
                    case "scale_ratio":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            current=float(json_value),
                            lower=0.00001,
                            upper=10.0,
                            step_increment=0.1,
                            page_increment=1
                        )
                    case "noise_augmentation":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            current=float(json_value),
                            lower=0.00001,
                            upper=1.0,
                            step_increment=0.001,
                            page_increment=0.01
                        )
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "UltimateSDUpscale":
                match input_name:
                    case "upscale_by":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            current=float(json_value),
                            lower=0.00001,
                            upper=10.0,
                            step_increment=0.1,
                            page_increment=1.0
                        )
                    case "seed":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(0, None)
                        )
                    case "steps":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(1, 128)
                        )
                    case "cfg":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=float(json_value),
                            lower=1,
                            upper=25,
                            step_increment=0.1,
                            page_increment=2
                        )
                    case "sampler_name":
                        sel_idx: int = WidgetAuthor._SAMPLER_NAMES.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=WidgetAuthor._SAMPLER_NAMES,
                                                  selected_index=sel_idx
                                                  )
                    case "scheduler":
                        sel_idx: int = WidgetAuthor._SCHEDULER_NAMES.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=WidgetAuthor._SCHEDULER_NAMES,
                                                  selected_index=sel_idx
                                                  )
                    case "denoise":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            current=float(json_value),
                            lower=0.00001,
                            upper=1.0,
                            step_increment=0.001,
                            page_increment=0.01
                        )
                    case "mode_type":
                        sel_idx: int = WidgetAuthor._MODE_TYPES.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=WidgetAuthor._MODE_TYPES,
                                                  selected_index=sel_idx
                                                  )
                    case "mask_blur" | "tile_padding":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(0, 128)
                        )
                    case "seam_fix_mode":
                        sel_idx: int = WidgetAuthor._SEAM_FIX_MODES.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=WidgetAuthor._SEAM_FIX_MODES,
                                                  selected_index=sel_idx
                                                  )
                    case "seam_fix_denoise":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            current=float(json_value),
                            lower=0.00001,
                            upper=1.0,
                            step_increment=0.001,
                            page_increment=0.01
                        )
                    case "seam_fix_width" | "seam_fix_mask_blur" | "seam_fix_padding":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(0, 128)
                        )
                    case "force_uniform_tiles":
                        result = new_checkbutton(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            toggled_handler_body_txt="pass",
                            current=bool_of(json_value)
                        )
                    case "tiled_decode":
                        result = new_checkbutton(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            toggled_handler_body_txt="pass",
                            current=bool_of(json_value)
                        )
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "UpscaleModelLoader":
                match input_name:
                    case "model_name":
                        sel_idx: int = self._models_upscale_models.index(json_value)
                        result = new_combo_models(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  selected_index=sel_idx,
                                                  model_type=ModelType.UPSCALE_MODELS
                                                  )
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "VAEEncodeForInpaint":
                match input_name:
                    case "grow_mask_by":
                        result = new_scale(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            current=int(json_value),
                            lower=1,
                            upper=16,
                            step_increment=1,
                            page_increment=4
                        )
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case "ZZZDummyClassDoesNotExist":
                match input_name:
                    case "zzz_dummy_fake_input":
                        pass
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node class {node_class_name}"
                        LOGGER_WF2PY.warning(log_msg)
            case _:
                log_msg: str = f"Deferring node class \"{node_class_name}\""
                LOGGER_WF2PY.warning(log_msg)
        if not result:
            message = ("No known widget class for node_class_name=\"%s\", node_title=\"%s\", input_name=\"%s\""
                       % (node_class_name, node_title, input_name))
            logging.warning(message)
        return result

    # Node Title might be most specific, if the workflow is designed carefully. Otherwise, Node Title is NOT UNIQUE, and
    # there can be confusion.
    def text_from_node_title(
            self,
            node_class_name: str,  # noqa
            node_index_str: str,
            node_title: str,
            input_name: str,
            json_value: str,
            change_handler_body_txt: str,  # noqa
            newline: bool = True,  # noqa
    ) -> Dict[str, str]:
        result: Dict[str, str] | None = None
        match node_title:
            case "Base Model" | "Refiner Model":
                match input_name:
                    case "ckpt_name":
                        checkpoints_from_fs = list_from_fs(fs_path=self._config['sd_checkpoints_dir'],
                                                           predicate=seems_checkpoint)
                        checkpoint_literals = list_as_literals(checkpoints_from_fs)
                        combo_message = f"Looking for index of {json_value} in {checkpoint_literals}"
                        LOGGER_WF2PY.debug(combo_message)
                        sel_idx: int = checkpoints_from_fs.index(json_value)
                        result = new_combo_models(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  selected_index=sel_idx,
                                                  model_type=ModelType.CHECKPOINTS
                                                  )
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node titled {node_title}"
                        LOGGER_WF2PY.warning(log_msg)
            case "2048x Upscale":
                match input_name:
                    case "filename_prefix":
                        result = new_entry_str(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            current="generated_upscaled")
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node titled {node_title}"
                        LOGGER_WF2PY.warning(log_msg)
            case "Load Image" | "Base Image" | "Mask Image":
                match input_name:
                    case "image":
                        result = new_treeview_layer(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                        )
                    case "upload" | "Upload":
                        result = new_null_widget(node_index_str=node_index_str, input_name=input_name)
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node titled {node_title}"
                        LOGGER_WF2PY.warning(log_msg)
            case "Load VAE":
                match input_name:
                    case "vae_name":
                        vaes_from_fs = list_from_fs(fs_path=self._config['sd_vae_dir'], predicate=seems_vae,
                                                    special_entries=['Baked VAE']
                                                    )
                        vae_literals = list_as_literals(vaes_from_fs)
                        combo_message = f"Looking for index of {json_value} in {vae_literals}"
                        LOGGER_WF2PY.debug(combo_message)
                        sel_idx: int = index_or_not(entries=vaes_from_fs, selected_entry=json_value)
                        result = new_combo_models(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  selected_index=sel_idx,
                                                  special_entries=['Baked VAE'],
                                                  model_type=ModelType.VAE
                                                  )
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node titled {node_title}"
                        LOGGER_WF2PY.warning(log_msg)
            case "Save Image":
                match input_name:
                    case "filename_prefix":
                        current_val: str = "gimp_generated"
                        if "upscale" in node_title.lower():
                            current_val = "upscaled/gimp_generated"
                        result = new_entry_str(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            current=current_val)
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node titled {node_title}"
                        LOGGER_WF2PY.warning(log_msg)
                pass
            case "Sytan Workflow":
                match input_name:
                    case "filename_prefix":
                        current_val: str = "gimp_generated"
                        if "upscale" in node_title.lower():
                            current_val = "upscaled/gimp_generated"
                        result = new_entry_str(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            current=current_val)
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node titled {node_title}"
                        LOGGER_WF2PY.warning(log_msg)
            case "UNETLoader" | "Load Diffusion Model":
                match input_name:
                    case "unet_name":
                        unets_from_fs = list_from_fs(fs_path=self._config['sd_unet_dir'], predicate=seems_unet)
                        unet_literals = list_as_literals(unets_from_fs)
                        combo_message = f"Looking for index of {json_value} in {unet_literals}"
                        LOGGER_WF2PY.debug(combo_message)
                        sel_idx: int = unets_from_fs.index(json_value)  # Should be 0
                        result = new_combo_models(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  selected_index=sel_idx,
                                                  model_type=ModelType.UNET
                                                  )
                        continues_row(result=result, input_name=input_name)
                    case "weight_dtype":
                        weight_dtype_literals = ["default", "fp8_e4m3fn", "fp8_e5m2"]
                        combo_message = f"Looking for index of {json_value} in {weight_dtype_literals}"
                        LOGGER_WF2PY.debug(combo_message)
                        sel_idx: int = weight_dtype_literals.index(json_value)  # Should be 0
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=weight_dtype_literals,
                                                  selected_index=sel_idx
                                                  )
                        ends_row(result=result, input_name=input_name)
            case "Upscale Image":
                match input_name:
                    case "crop":
                        sel_idx: int = self._crop_methods.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  items=self._crop_methods,
                                                  selected_index=sel_idx
                                                  )
                    case "height" | "width":
                        result = new_entry_int(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=int(json_value),
                            bounds=(1, None)
                        )
                        continues_row(result=result, input_name=input_name)
                    case "scale_by":
                        result = new_entry_float(
                            node_title=node_title,
                            node_index_str=node_index_str,
                            input_name=input_name,
                            change_handler_body_txt="pass",
                            current=float(json_value),
                            bounds=(0, None)
                        )
                    case "upscale_method":
                        sel_idx: int = self._upscale_methods.index(json_value)
                        result = new_combo_static(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  items=self._upscale_methods,
                                                  selected_index=sel_idx
                                                  )

                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node titled {node_title}"
                        LOGGER_WF2PY.warning(log_msg)
            case "Upscale Model":
                match input_name:
                    case "model_name":
                        sel_idx: int = self._models_upscale_models.index(json_value)
                        result = new_combo_models(node_title=node_title,
                                                  node_index_str=node_index_str,
                                                  input_name=input_name,
                                                  change_handler_body_txt="pass",
                                                  selected_index=sel_idx,
                                                  model_type=ModelType.UPSCALE_MODELS
                                                  )
                    case _:
                        log_msg: str = f"Deferring input \"{input_name}\" in node titled {node_title}"
                        LOGGER_WF2PY.warning(log_msg)
            case _:
                log_msg: str = f"Deferring node titled \"{node_title}\""
                LOGGER_WF2PY.debug(log_msg)
        if not result:
            message = f"No known widget class for node_class_name=\"{node_class_name}\", node_title=\"{node_title}\""
            logging.debug(message)
        return result

    def widget_text_for(self,
                        node_class_name: str,
                        node_index_str: str,
                        node_title: str,
                        input_name: str,
                        newline: bool = True,
                        **kwargs) -> Dict[str, str]:
        """
         The newline argument is sometimes ignored and overridden by specific cases.
        :param node_class_name:
        :param node_index_str:
        :param node_title:
        :param input_name:
        :param newline:  Sometimes ignored and overridden by specific cases.
        :param kwargs:
        :return:  A dict that contains the source code for the input's widget(s) and metadata about the widget code.
        """
        # logging.warning("index=%s, node_class_name=%s, title=%s" % (node_index_str, node_class_name, node_title))
        # result is a dict that contains the source code for the input's widget(s) and metadata about the widget code.
        # in particular, the metadata might specify layout constraints.
        result: Dict[str, str] = {}
        json_value: str = kwargs["json_value"]
        if not result:
            result = self.text_from_node_title(
                node_class_name=node_class_name,
                node_index_str=node_index_str,
                node_title=node_title,
                input_name=input_name,
                json_value=json_value,
                change_handler_body_txt="pass",
                newline=newline,
            )
        if not result:
            result = self.text_from_node_class_name(
                node_class_name=node_class_name,
                node_index_str=node_index_str,
                node_title=node_title,
                input_name=input_name,
                json_value=json_value,
                newline=newline,
            )
        if not result:
            result = self.text_from_input_name(
                node_class_name=node_class_name,
                node_index_str=node_index_str,
                node_title=node_title,
                input_name=input_name,
                json_value=json_value,
                newline=newline,
            )
        # If widget text was written for this input, insert a new entry storing the newline flag.
        # if result:
        #     metakey = append_newline_suffix(input_name)
        #     nls = str(newline)
        #     if not newline:
        #         log_msg: str = f"Inserting result[{metakey}]={nls}"
        #         LOGGER_WF2PY.warning(log_msg)
        #     result[metakey] = nls
        return result


def main() -> int:
    generated_code: Dict[str, str]
    generated_code = new_combo_models(node_title="Ckpt_Name",
                                      node_index_str="14",
                                      input_name="ckpt_name",
                                      change_handler_body_txt="pass",
                                      selected_index=12,
                                      model_type=ModelType.CHECKPOINTS
                                      )
    unescaped_text = decode_escapes(json.dumps(generated_code, indent=2, sort_keys=True))
    LOGGER_WF2PY.warning(unescaped_text)
    return 0


if __name__ == '__main__':
    sys.exit(main())
