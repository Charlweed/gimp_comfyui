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

import utilities.png
from datetime import datetime
from utilities.heterogeneous import LayerTreeView, ImageComboBox
from utilities.png import *
from utilities.samples import *
from utilities.sd_gui_utils import *
from utilities.type_utils import *


def print_i(width: int,
            height: int,
            channels_per_pixel: int = 8):
    i_channel: int
    i_column: int
    i_row: int
    for i_row in range(height):
        for i_column in range(width):
            for i_channel in range(channels_per_pixel):
                pixel_index = i_channel + (i_column * channels_per_pixel) + (i_row * width * channels_per_pixel)
                # logging.warning(f"i={pixel_index}, i_channel={i_channel},i_column={i_column}, i_row={i_row}")
                abs_start: int = pixel_index * CHANNEL_BYTE_DEPTH_GIMP
                abs_end: int = abs_start + 8
                logging.warning(f"absolute_range=[{abs_start}:{abs_end}]")


def via_manual_array() -> int:
    channels_per_pixel: int = 4
    width: int = 8
    height: int = 8
    source_byte_count_expected = CHANNEL_BYTE_DEPTH_GIMP * channels_per_pixel * width * height
    not_an_image: bytearray = bytearray()  # All zeros
    info_dict = {
        "alpha": True,
        "bitdepth": 16,
        "gamma": 0.45455,
        "greyscale": False,
        "height": height,
        "planes": channels_per_pixel,
        "size": [
            width,
            height
        ],
        "width": width
    }
    gray_value: int = SIXTY_FOUR_BYTES // 2
    gray_value_8_bytes: bytes = gray_value.to_bytes(length=8, byteorder="little")
    # 64 bit ffffffffffffffff black
    #        7fffffffffffffff 50% gray
    #        3fffffffffffffff 25% gray
    #        0000000000000000 white
    i_channel: int
    i_column: int
    i_row: int
    for i_row in range(height):
        for i_column in range(width):
            for i_channel in range(channels_per_pixel):
                not_an_image.extend(gray_value_8_bytes)
    source_byte_count_actual = len(not_an_image)
    if source_byte_count_expected != source_byte_count_actual:
        source_err_msg = (f"source_byte_count_expected {source_byte_count_expected} != "
                          f"source_byte_count_actual {source_byte_count_actual}")
        raise ValueError(source_err_msg)

    re_stacked: list[list[int]] = restack_image_array(image_array=not_an_image,
                                                      channels_per_pixel=channels_per_pixel,
                                                      width=width, height=height)
    if re_stacked is None:
        raise ValueError("Result is none")
    if not re_stacked:
        raise ValueError("Result is empty")
    row_count: int = len(re_stacked)
    if row_count != height:
        raise ValueError(f"result_len should be {height}, is actually {row_count}")
    width_16: int = channels_per_pixel * width
    row: list[int]
    for row in re_stacked:
        if row is None:
            raise ValueError("row is none")
        if not row:
            raise ValueError("row is empty")
        # res = [hex(x) for x in row]
        # logging.warning(f"Retrieved row as string={res}")
        row_len: int = len(row)
        if row_len != width_16:
            width_err_msg = f"row_len should be {width_16}, is actually {row_len}"
            raise ValueError(width_err_msg)
    png_image: utilities.png.Image = from_matrix(re_stacked, mode='RGBA;16', info=info_dict)
    # png_image.save(fyle_path("example_png_00.png"))  # docs say Image is spent after calling save.
    png_bytes: bytes = png_image.serialize()
    with open(fyle_path("example_png_01.png"), "wb") as binary_file:
        binary_file.write(png_bytes)
    return 0


# L:\projects\hymerfania\gimp_scripts\two_nintynine\plug-ins_available\gimp_comfyui\assets\gray_RGB_SPACE_U16_2024_06_28-03_26_769190.raw
# L:\projects\hymerfania\gimp_scripts\two_nintynine\plug-ins_available\gimp_comfyui\assets\gray_RGBA_SPACE_U16_2024_06_28-03_39_253524.raw
def via_binary_file(in_file_name: str) -> int:
    channels_per_pixel: int = 4
    width: int = 512
    height: int = 512
    source_byte_count_expected = CHANNEL_BYTE_DEPTH_GIMP * channels_per_pixel * width * height
    gimp_layer_data: bytes
    with open(in_file_name, mode="rb") as gimp_layer_file:
        gimp_layer_data = gimp_layer_file.read()
    info_dict = {
        "alpha": True,
        "bitdepth": 16,
        "gamma": 0.45455,
        "greyscale": False,
        "height": height,
        "planes": channels_per_pixel,
        "size": [
            width,
            height
        ],
        "width": width
    }
    source_byte_count_actual = len(gimp_layer_data)
    if source_byte_count_expected != source_byte_count_actual:
        source_err_msg = (f"source_byte_count_expected {source_byte_count_expected} != "
                          f"source_byte_count_actual {source_byte_count_actual}")
        raise ValueError(source_err_msg)

    re_stacked: list[list[int]] = restack_image_array(image_array=gimp_layer_data,
                                                      channels_per_pixel=channels_per_pixel,
                                                      width=width, height=height)
    if re_stacked is None:
        raise ValueError("Result is none")
    if not re_stacked:
        raise ValueError("Result is empty")
    row_count: int = len(re_stacked)
    if row_count != height:
        raise ValueError(f"result_len should be {height}, is actually {row_count}")
    width_16: int = channels_per_pixel * width
    row: list[int]
    for row in re_stacked:
        if row is None:
            raise ValueError("row is none")
        if not row:
            raise ValueError("row is empty")
        # res = [hex(x) for x in row]
        # logging.warning(f"Retrieved row as string={res}")
        row_len: int = len(row)
        if row_len != width_16:
            width_err_msg = f"row_len should be {width_16}, is actually {row_len}"
            raise ValueError(width_err_msg)
    png_image: utilities.png.Image = from_matrix(re_stacked, mode='RGBA;16', info=info_dict)
    # png_image.save(fyle_path("example_png_00.png"))  # Note: Image is spent after calling save.
    png_bytes: bytes = png_image.serialize()
    time_part = datetime.now().strftime("%Y_%m_%d-%I_%M_%f")
    png_name = f"example_png_{time_part}.png"
    file_path_png = fyle_path(png_name)
    with open(file_path_png, "wb") as binary_file:
        binary_file.write(png_bytes)
    return 0


def display_tree_n_list_tutorial():
    # list of tuples for each software, containing the software name, initial release,
    # and main programming languages used
    software_list = [
        ("Firefox", 2002, "C++"),
        ("Eclipse", 2004, "Java"),
        ("Pitivi", 2004, "Python"),
        ("Netbeans", 1996, "Java"),
        ("Chrome", 2008, "C++"),
        ("Filezilla", 2001, "C++"),
        ("Bazaar", 2005, "Python"),
        ("Git", 2005, "C"),
        ("Linux Kernel", 1991, "C"),
        ("GCC", 1987, "C"),
        ("Frostwire", 2004, "Java"),
    ]

    class TreeViewFilterWindow(Gtk.Window):
        def __init__(self):
            super().__init__(title="Treeview Filter Demo")
            self.set_border_width(10)  # noqa
            # Setting up the self.grid in which the elements are to be positioned
            self.grid = Gtk.Grid()
            self.grid.set_column_homogeneous(True)
            self.grid.set_row_homogeneous(True)
            self.add(self.grid)  # noqa
            # Creating the ListStore model
            self.software_liststore = Gtk.ListStore(str, int, str)  # noqa
            for software_ref in software_list:
                self.software_liststore.append(list(software_ref))
            self.current_filter_language = None
            # Creating the filter, feeding it with the liststore model
            self.language_filter = self.software_liststore.filter_new()
            # setting the filter function, note that we're not using the
            self.language_filter.set_visible_func(self.language_filter_func)
            # creating the treeview, making it use the filter as a model, and adding the columns
            self.treeview = Gtk.TreeView(model=self.language_filter)
            for i, column_title in enumerate(["Software", "Release Year", "Programming Language"]):
                renderer = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(column_title, renderer, text=i)  # noqa
                self.treeview.append_column(column)

            # creating buttons to filter by programming language, and setting up their events
            self.buttons = list()
            for prog_language in ["Java", "C", "C++", "Python", "None"]:
                button = Gtk.Button(label=prog_language)
                self.buttons.append(button)
                button.connect("clicked", self.on_selection_button_clicked)

            # setting up the layout, putting the treeview in a scrollwindow, and the buttons in a row
            self.scrollable_treelist = Gtk.ScrolledWindow()
            self.scrollable_treelist.set_vexpand(True)
            self.grid.attach(self.scrollable_treelist, 0, 0, 8, 10)
            self.grid.attach_next_to(self.buttons[0], self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1)
            for i, button in enumerate(self.buttons[1:]):
                self.grid.attach_next_to(button, self.buttons[i], Gtk.PositionType.RIGHT, 1, 1)
            self.scrollable_treelist.add(self.treeview)
            self.show_all()  # noqa

        def language_filter_func(self, model, model_iter, data):  # noqa
            """Tests if the language in the row is the one in the filter"""
            if self.current_filter_language is None or self.current_filter_language == "None":
                return True
            else:
                return model[model_iter][2] == self.current_filter_language

        def on_selection_button_clicked(self, widget):
            """Called on any of the button clicks"""
            # we set the current language filter to the button's label
            self.current_filter_language = widget.get_label()
            LOGGER_SDGUIU.info("%s language selected!" % self.current_filter_language)
            # we update the filter, which updates in turn the view
            self.language_filter.refilter()

    win = TreeViewFilterWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()  # noqa
    Gtk.main()


def display_images_n_layers_dialog(
        image_id_consumer: Callable[[Any], None] | None = None,
        layer_id_consumer: Callable[[Any], None] | None = None
) -> int:
    blurb: str = "Play with the widgets, and check the \"GimpComfyUI_logfile.txt\" log."
    images_combo: ImageComboBox | None = None
    layers_treeview: LayerTreeView | None = None
    carry_on: bool = True
    return_code: int = -1

    def halt(source: Gtk.Widget, data=None):  # noqa
        nonlocal images_combo
        nonlocal layers_treeview
        nonlocal carry_on
        nonlocal return_code
        if layers_treeview is not None:
            long_row = get_selected_row(layers_treeview)
            if long_row is not None:
                layer_id = long_row[1]  # layer_id index
                if layer_id_consumer is not None:
                    layer_id_consumer(layer_id)
            else:
                LOGGER_SDGUIU.warning("long_row is None")
            # image_str: str = layers_treeview.selected_png_str
        else:
            LOGGER_SDGUIU.error("No images_treeview!")
        if images_combo is not None:
            # LOGGER_SDGUIU.debug(f"Calling get_selected_row() on {images_combo.get_name()}")
            short_row = get_selected_row(images_combo)
            if short_row is not None:
                image_id = short_row[0]  # image_id index
                if image_id_consumer is not None:
                    image_id_consumer(image_id)
                else:
                    LOGGER_SDGUIU.warning("image_id_consumer is None")
            else:
                LOGGER_SDGUIU.warning("short_row is None")
        else:
            LOGGER_SDGUIU.error("No images_combo!")

        close_window_of_widget(source)
        carry_on = False
        return_code = 0

    def insert_widgets(dialog: Gtk.Dialog):
        empty_box: Gtk.Box = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        dialog_box: Gtk.Box = dialog.get_content_area()
        nonlocal images_combo
        nonlocal layers_treeview
        try:
            images_combo = ImageComboBox()
            dialog_box.pack_start(child=images_combo, expand=False, fill=True, padding=1)
        except Exception as e_err:
            LOGGER_SDGUIU.exception(e_err)
        try:
            layers_treeview = LayerTreeView()
            dialog_box.pack_start(child=layers_treeview, expand=False, fill=True, padding=1)
        except Exception as e_err:
            LOGGER_SDGUIU.exception(e_err)
        dialog_box.pack_start(child=empty_box, expand=True, fill=True, padding=4)

    try:
        open_dialog_daemon(title_in="Images and Layers",
                           blurb_in=blurb,
                           main_button_label="Finished",
                           dialog_populator=insert_widgets,
                           ok_handler=halt)
        while carry_on:
            time.sleep(1)

    except Exception as e_exception:
        LOGGER_SDGUIU.exception(e_exception)
        return_code = 255
    return return_code


def main(argv) -> int:  # noqa
    ret_val: int
    ret_val = display_images_n_layers_dialog()
    # display_tree_n_list_tutorial()
    return ret_val


if __name__ == '__main__':
    sys.exit(main(sys.argv))
