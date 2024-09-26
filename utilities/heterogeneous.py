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


import base64
import glob
import os.path
import pathlib
import platform
import utilities.png
# gi is the python module for PyGObject. It is a Python package which provides bindings for GObject based libraries such
# as GTK, GStreamer, WebKitGTK, GLib, GIO and many more. See https://gnome.pages.gitlab.gnome.org/pygobject/
import gi

gi.require_version('Gimp', '3.0')  # noqa: E402
gi.require_version('GimpUi', '3.0')  # noqa: E402
gi.require_version("Gtk", "3.0")  # noqa: E402
gi.require_version('Gdk', '3.0')  # noqa: E402
gi.require_version("Gegl", "0.4")  # noqa: E402
from gi.repository import Gdk, Gio, Gimp, GimpUi, Gtk, GLib, GObject, Gegl  # noqa
from pathlib import Path
from random import randrange
from utilities.babl_gegl_utils import *
from utilities.png import *
from utilities.sd_gui_utils import *
from utilities.type_utils import restack_image_array

LOGGER_HETERO_UTILS = logging.getLogger("heterogeneousutils")
LOGGER_FORMAT_GCUI_DEFAULT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"

HETERO_BRAND: str = "±htr0tmp±"  # Anything with this is the filename is subject to deletion. The unicode is deliberate.


def png_from_drawable(drawable: Gimp.Drawable) -> utilities.png.Image:
    """
     Creates a base64 encoded string, of a PNG, created from the specified drawable.
    :param drawable: The drawable to encode. Should be a Layer, other drawables are unsupported.
    :return: A base64 encoded string, of a PNG, created from the specified drawable.
    """
    d_id = drawable.get_id()
    d_name = drawable.get_name()
    height = drawable.get_height()
    width = drawable.get_width()
    change_message: str = f"Drawable {d_id} \"{d_name}\"changed."
    LOGGER_HETERO_UTILS.debug(change_message)
    channels_per_pixel: int = 3
    mode: str = "RGB"
    babl_format: BablFormat = BablFormat.RGB_SPACE_U16
    is_gray: bool = drawable.is_gray()
    if is_gray:
        channels_per_pixel = 1
        mode = "LA"
        babl_format = BablFormat.GRAYSCALE_SPACE_U16
    has_alpha: bool = drawable.has_alpha()
    if has_alpha:
        channels_per_pixel += 1
        mode = "RGBA"
        babl_format = BablFormat.RGBA_SPACE_U16

    info_dict = {
        "alpha": has_alpha,
        "bitdepth": 16,
        "gamma": 0.45455,
        "greyscale": is_gray,
        "height": height,
        "planes": channels_per_pixel,
        "size": [
            width,
            height
        ],
        "width": width
    }
    image_bytes_raw: bytes = drawable_bytes(drawable_in=drawable, babl_format=babl_format)
    if not isinstance(image_bytes_raw, bytes):
        ibt = type(image_bytes_raw)
        ibt_name = ibt.__name__
        err_msg = f"image_bytes_raw should be bytes, actual type is {ibt_name}"
        LOGGER_HETERO_UTILS.error(err_msg)
        raise TypeError(err_msg)
    if len(image_bytes_raw) == 0:
        raise ValueError("image_bytes_raw is empty")

    re_stacked = restack_image_array(image_bytes_raw,
                                     channels_per_pixel=channels_per_pixel,
                                     width=width,
                                     height=height)
    png_image: utilities.png.Image = from_matrix(re_stacked, mode=mode, info=info_dict)
    return png_image


def png_from_id(layer_id: int) -> utilities.png.Image:
    layer: Gimp.Layer = Gimp.Layer.get_by_id(layer_id)
    return png_from_drawable(drawable=layer)


def png_base64_str(subject: Gimp.Drawable | utilities.png.Image) -> str:
    drawable: Gimp.Drawable
    png_image: utilities.png.Image
    if isinstance(subject, Gimp.Drawable):
        drawable = subject
        png_image = png_from_drawable(drawable=drawable)
    else:
        if isinstance(subject, utilities.png.Image):
            png_image = subject
        else:
            raise TypeError(f"Cannot process {type(subject).__name__};"
                            f" Argument must be a Gimp.Drawable or utilities.png.Image")
    png_bytes: bytes = png_image.serialize()
    image_b64 = base64.b64encode(png_bytes)
    image_as_str = image_b64.decode('utf-8')
    return image_as_str


def png_base64_str_from_id(layer_id: int) -> str:
    layer: Gimp.Layer = Gimp.Layer.get_by_id(layer_id)
    return png_base64_str(subject=layer)


def png_temp_file(subject: Gimp.Drawable | utilities.png.Image) -> str:
    """
    IMPORTANT: Repeated calls to this method will return different results for the same state, because a new
    temp file name is generated from the current time in millis.
    :param: A Gimp Layer or png.Image to save in a temp file.
    :return: The path to a tempfile created for the currently selected layer, or None
    """
    drawable: Gimp.Drawable
    png_image: utilities.png.Image
    leaf_basename = "png_graphic"
    if isinstance(subject, Gimp.Drawable):
        drawable = subject
        png_image = png_from_drawable(drawable=drawable)
        leaf_basename = drawable.get_name()
    else:
        if isinstance(subject, utilities.png.Image):
            png_image = subject
        else:
            raise TypeError(f"Cannot process {type(subject).__name__};"
                            f" Argument must be a Gimp.Drawable or utilities.png.Image")
    filesystem_name = temp_filename(leaf_basename=leaf_basename, extension="png")
    save_png_to_file(png_image=png_image, file_path=filesystem_name, overwrite=False)
    return filesystem_name


def png_tmp_file_from_id(layer_id: int) -> str:
    layer: Gimp.Layer = Gimp.Layer.get_by_id(layer_id)
    return png_temp_file(subject=layer)


def remove_hetero_temp_files():
    doomed: list[str] = glob.glob(f"{tempfile.gettempdir()}/*{HETERO_BRAND}*")
    for f in doomed:
        LOGGER_HETERO_UTILS.debug(f"Attempting to delete old temp file \"{f}\"")
        os.remove(f)
    time.sleep(.5)
    failed = False
    for f in doomed:
        if os.path.exists(f):
            failed = True
            LOGGER_HETERO_UTILS.error(f"Failed to delete \"{f}\"")
    if failed:
        raise IOError(f"Failed to delete *{HETERO_BRAND}* temporary files.")


def save_png_to_file(png_image: utilities.png.Image, file_path: str, overwrite: bool = True):
    pre_exists = os.path.exists(file_path)
    if pre_exists and (not overwrite):
        raise IOError(f"{file_path} already exists")
    # LOGGER_HETERO_UTILS.debug(f"save_png_to_file():Saving temp png to \"{file_path}\"")
    png_image.save(file_path)


def strip_hetero_brand_from_root(leaf_string: str) -> str:
    """
    Removes the infix that makes every filename unique from the "root" of the filename. The extension is
    left unchanged.
    :param leaf_string: The file's name. It must NOT have any regex special characters, excepting the final dot that
    separates the extension. Using entire paths is unsupported, because they will likely contain regex characters.
    :return:
    """
    stem, dotted_ext = os.path.splitext(leaf_string)
    ext = dotted_ext.strip(".")
    pattern_str = f"_{HETERO_BRAND}.*\.{ext}$"
    stripped = re.sub(pattern=pattern_str, repl="", string=leaf_string)
    return f"{stripped}.{ext}"


def temp_filename(leaf_basename: str = "png_temp", extension: str = "png") -> str:
    rand_part: int = randrange(100, 1000)
    time_part = datetime.now().strftime("%Y_%m_%d-%I_%M_%f")
    filtered = leaf_basename.replace(f".{extension}", "")
    out_fyle_name = f"{filtered}_{HETERO_BRAND}_{rand_part:04}_{time_part}.{extension}"
    return os.path.join(tempfile.gettempdir(), out_fyle_name)


class ImageComboBox(Gtk.ComboBox):
    ID_INDEX: int = 0
    INDEX_INDEX: int = 1
    ITEM_ITEM_NAME_INDEX: int = 2

    def _selection_changed_handler(self, ignored):  # noqa
        treeiter = self.get_active_iter()
        if treeiter is not None:
            model: Gtk.TreeModel = self.get_model()
            # path: Gtk.TreePath = model.get_path(treeiter)
            self._row = list(model[treeiter])
            # LOGGER_HETERO_UTILS.debug(f"You selected {self._row}; path={path}")
        else:
            self._row = list()

    def __init__(self):
        super().__init__()
        self._row: list[int, int, str] = list()  # noqa
        self._image_store: Gtk.ListStore = Gtk.ListStore.new(types=[int, int, str])  # image_id, index, image_name
        self._image_store = new_list_store_images()
        # LOGGER_HETERO_UTILS.debug(f"image_store has {len(image_store)} images")
        self.set_model(self._image_store)
        self.set_name("image_combobox")
        self.set_active(0)
        self._cell_renderer_text = Gtk.CellRendererText()
        self.pack_start(self._cell_renderer_text, expand=True)
        self.add_attribute(self._cell_renderer_text, attribute="text", column=ImageComboBox.ITEM_ITEM_NAME_INDEX)
        self.connect("changed", self._selection_changed_handler)

    @property
    def selected_row(self) -> list[int, int, str]:
        treeiter = self.get_active_iter()
        if treeiter is not None:
            model: Gtk.TreeModel = self.get_model()
            self._row = list(model[treeiter])
        else:
            self._row = list()
        return self._row  # noqa

    def get_selected_image_id(self) -> int:
        if self.selected_row:
            return self._row[ImageComboBox.ID_INDEX]
        else:
            return -1

    @property
    def selected_image_id(self) -> int:
        return self.get_selected_image_id()

    def index_of_image(self, image_id: int) -> int:
        img_tpl: tuple[int, int, str]
        for img_tpl in self._image_store:  # noqa
            img_id = img_tpl[0]
            if img_id == image_id:
                return img_id
        raise ValueError(f"image_id not found.")

    def set_selected_image_id(self, image_id: int):
        all_image_ids = new_set_image_ids()
        if image_id not in all_image_ids:
            raise ValueError(f"Could not find image_id {image_id}")
        self._image_store = new_list_store_images()  # is this necessary?
        img_idx = self.index_of_image(image_id)
        self.set_active(img_idx)

    @selected_image_id.setter
    def selected_image_id(self, image_id: int):
        self.set_selected_image_id(image_id=image_id)

    def get_selected_gimp_image(self) -> Gimp.Image | None:
        s_r: list[int, int, str] = self.selected_row
        if s_r:
            return Gimp.Image.get_by_id(s_r[ImageComboBox.ID_INDEX])
        else:
            return None

    @property
    def selected_gimp_image(self) -> Gimp.Image | None:
        return self.get_selected_gimp_image()


class LayerTreeView(Gtk.TreeView):
    _TYPE_NAME_INDEX = 0
    _ID_INDEX: int = 1
    _INDEX_INDEX: int = 2
    _ITEM_NAME_INDEX: int = 3

    # noinspection PyMethodMayBeStatic
    def is_selectable(self, selection, model, path, path_currently_selected, *data) -> bool:  # noqa
        """
        A function used by Gtk.TreeSelection.set_select_function() to filter whether a row may be selected.
        :param selection: A Gtk.TreeSelection
        :param model: A Gtk.TreeModel being viewed
        :param path: The Gtk.TreePath of the row in question
        :param path_currently_selected: True, if the path is currently selected
        :param data: user data
        :return: true if the row is for a layer
        """
        is_layer: bool = False
        if model:
            if path:
                treeiter: Gtk.TreeIter = model.get_iter(path)
                if treeiter:
                    type_name = model[treeiter][LayerTreeView._TYPE_NAME_INDEX]
                    is_layer = type_name == "layer"
                    # LOGGER_HETERO_UTILS.debug(f"is_layer=\"{is_layer}\"")
                else:
                    LOGGER_HETERO_UTILS.warning(f"No iterator from path \"{path}\"")
            else:
                LOGGER_HETERO_UTILS.warning("No path passed to is_selectable()")
        else:
            LOGGER_HETERO_UTILS.warning("No model passed to is_selectable()")
        return is_layer

    def _selection_changed_handler(self, selection: Gtk.TreeSelection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            self._row = list(model[treeiter])
        else:
            self._row = list()

    def __init__(self):
        super().__init__()
        self._row: list[str, int, int, str] = list()  # noqa
        store: Gtk.TreeStore = new_list_store_all_layers()
        self.set_model(model=store)
        self.set_name("all_layers_treeview")
        text_renderer = Gtk.CellRendererText()
        column_type = Gtk.TreeViewColumn(title="Type", cell_renderer=text_renderer, text=LayerTreeView._TYPE_NAME_INDEX)  # noqa
        column_name = Gtk.TreeViewColumn(title="Name", cell_renderer=text_renderer, text=LayerTreeView._ITEM_NAME_INDEX)  # noqa
        self.append_column(column_type)
        self.append_column(column_name)
        self.expand_all()
        select: Gtk.TreeSelection = self.get_selection()
        select.select_path("0:0")  # Root node, 1st child.
        select.set_select_function(self.is_selectable)
        select.connect("changed", self._selection_changed_handler)

    @property
    def selected_row(self) -> list[str, int, int, str]:
        model, treeiter = self.get_selection().get_selected()
        if treeiter is not None:
            self._row = list(model[treeiter])
        else:
            self._row = list()
        return self._row  # noqa

    def get_selected_layer_id(self) -> int:
        if self.selected_row:
            return self._row[LayerTreeView._ID_INDEX]
        else:
            return -1

    @property
    def selected_layer_id(self):
        return self.get_selected_layer_id()

    @property
    def select_path(self) -> str | None:
        tree_selection: Gtk.TreeSelection = self.get_selection()
        model, treeiter = tree_selection.get_selected()
        if treeiter is not None:
            sel_path = model.get_path(treeiter)
            return sel_path.to_string()
        return None

    @select_path.setter
    def select_path(self, path_str: str | Gtk.TreePath):
        tree_selection: Gtk.TreeSelection = self.get_selection()
        tree_selection.select_path(path_str)

    def path_to_layer(self, layer_id: int) -> Gtk.TreePath | None:  # analogous to index_of in a combobox
        """
        Returns the path to a layer or None if the layer_id could not be found.
        :param layer_id:
        :return: the path to a layer, or None if the layer_id could not be found.
        """
        result: Gtk.TreePath = path_to_id(model=self.get_model(), item_id=layer_id, row_index=LayerTreeView._ID_INDEX)
        return result

    def set_selected_layer_id(self, layer_id: int):
        ptl: Gtk.TreePath = self.path_to_layer(layer_id)
        if ptl is None:
            raise ValueError(f"Could not determine path to layer \"{layer_id}\"")
        select: Gtk.TreeSelection = self.get_selection()
        select.select_path(ptl)

    @selected_layer_id.setter
    def selected_layer_id(self, layer_id: int):
        self.set_selected_layer_id(layer_id=layer_id)

    @property
    def selected_layer(self) -> Gimp.Layer | None:
        s_r: list[str, int, int, str] = self.selected_row
        if s_r:
            return Gimp.Layer.get_by_id(s_r[LayerTreeView._ID_INDEX])
        else:
            return None

    def get_selected_png_image(self) -> utilities.png.Image | None:
        sgl: Gimp.Layer = self.selected_layer
        if sgl is not None:
            return png_from_drawable(sgl)
        else:
            return None

    @property
    def selected_png_image(self) -> utilities.png.Image | None:
        return self.get_selected_png_image()

    def get_selected_png_str(self) -> str | None:
        png: utilities.png.Image = self.selected_png_image
        if png is not None:
            return png_base64_str(png)
        else:
            return None

    @property
    def selected_png_str(self) -> str | None:
        return self.get_selected_png_str()

    def get_selected_png_path(self) -> str | None:
        """
        IMPORTANT: Repeated calls to this method will return different results for the same state, because a new
        temp file name is generated from the current time in millis.
        :return: The path to a tempfile created for the currently selected layer, or None
        """
        layer: Gimp.Layer = self.selected_layer
        if layer is not None:
            return png_temp_file(layer)
        else:
            return None

    def get_selected_png_leaf(self) -> tuple[str, str] | None:
        """
        The leaf of the filepath is stripped of the HETERO_BRAND infix.
        IMPORTANT: Repeated calls to this method will return different path results, because a new temp file name is
        generated from the current time in millis.
        :return: a tuple of (path to a tempfile created for the currently selected layer, the leaf of that path) or None
        """
        leaf_name: str | None = None
        path_raw: str = self.get_selected_png_path()
        if path_raw is None or not Path:
            return leaf_name
        platform_name = platform.system().lower()
        path_pure: pathlib.PurePath
        match platform_name:
            case "windows":
                path_pure = pathlib.PureWindowsPath(path_raw)
            case _:
                path_pure = pathlib.PurePosixPath(path_raw)
        return path_raw, strip_hetero_brand_from_root(path_pure.name)


def treepath_to_ids(model: Gtk.TreeModel, layer_path: Gtk.TreePath) -> tuple[int, int]:
    """
    Gets the image_id and layer_id of items on the path
    :param model: TreeModel to access
    :param layer_path:
    :return:
    """
    parent_tp = layer_path.copy()
    parent_tp.up()
    parent_titer = model.get_iter(parent_tp)
    layer_titer = model.get_iter(layer_path)
    image_id = model.get_value(parent_titer, ImageComboBox.ID_INDEX + 1)
    layer_id = model.get_value(layer_titer, ImageComboBox.ID_INDEX + 1)
    return image_id, layer_id


def ids_to_treepath(model: Gtk.TreeModel, image_id: int, layer_id: int) -> Gtk.TreePath:
    """
    Takes a tuple of an image_id and a layer_id, and walks the model to build a path to those items.
    :param model: TreeModel to walk
    :param image_id Image to search for
    :param layer_id Layer to search for
    :return: A TreePath to the row of the layer
    """
    # It might be more robust to use foreach() and return the path when the layer_id matches.
    row: Gtk.TreeModelRow
    for row in model:  # noqa
        item = row[ImageComboBox.ID_INDEX + 1]
        if item == image_id:
            image_iter: Gtk.TreeIter = row.iter
            if image_iter is None:
                raise ValueError("ImageIter is None.")
            layer_iter = model.iter_children(image_iter)
            if layer_iter is None:
                raise ValueError("Could not get children layers of image.")
            while True:
                value = model.get_value(layer_iter, ImageComboBox.ID_INDEX + 1)
                if value == layer_id:
                    return model.get_path(layer_iter)
                layer_iter = model.iter_next(layer_iter)
                if layer_iter is None:
                    break
    raise KeyError(f"Could not find path to {image_id},{layer_id}")


def main() -> int:
    print(strip_hetero_brand_from_root("1962_TR3B_mask_scaled_±htr0tmp±_0177_2024_09_04-02_10_783976.png"))
    return 0


if __name__ == '__main__':
    sys.exit(main())
