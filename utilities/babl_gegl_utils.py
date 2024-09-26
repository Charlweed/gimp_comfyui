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
import logging
import os
import tempfile
from datetime import datetime
gi.require_version('Gimp', '3.0')  # noqa: E402
gi.require_version("Gegl", "0.4")  # noqa: E402
from enum import Enum
from gi.repository import Gegl, Gimp  # noqa

LOGGER_GEGL_UTILS = logging.getLogger("BablGeglUtils")
LOGGER_FORMAT_GCUI_DEFAULT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"


class BablFormat(Enum):
    """
    GRAY and GRAYSCALE are U.S. English. Other packages and libraries will use GREY and GREYSCALE. Beware.
    See https://gegl.org/babl/Reference.html#R_G_B_A_u16 etc. for the inadequate but exclusive documentation on these
    formats.
    """
    GRAYSCALE_U08 = "Y u8"
    GRAYSCALE_U16 = "Y u16"
    RGB_DOUBLE = "RGB double"
    RGBA_DOUBLE = "RGBA double"
    RGB_FLOAT = "RGB float"
    RGBA_FLOAT = "RGBA float"
    RGB_HALF = "RGB half"
    RGBA_HALF = "RGBA half"
    RGB_U08 = "RGB u8"
    RGBA_U08 = "RGBA u8"
    RGB_U16 = "RGB u16"
    RGBA_U16 = "RGBA u16"
    RGB_U15 = "RGB u15"
    RGBA_U15 = "RGBA u15"
    RGB_U32 = "RGB u32"
    RGBA_U32 = "RGBA u32"
    GRAYSCALE_SPACE_U08 = "Y' u8"
    GRAYSCALE_SPACE_U16 = "Y' u16"
    RGB_SPACE_DOUBLE = "R'G'B' double"
    RGBA_SPACE_DOUBLE = "R'G'B'A double"
    RGB_SPACE_FLOAT = "R'G'B' float"
    RGBA_SPACE_FLOAT = "R'G'B'A float"
    RGB_SPACE_HALF = "R'G'B' half"
    RGBA_SPACE_HALF = "R'G'B'A half"
    RGB_SPACE_U08 = "R'G'B' u8"
    RGBA_SPACE_U08 = "R'G'B'A u8"
    RGB_SPACE_U16 = "R'G'B' u16"
    RGBA_SPACE_U16 = "R'G'B'A u16"
    RGB_SPACE_U15 = "R'G'B' u15"
    RGBA_SPACE_U15 = "R'G'B'A u15"
    RGB_SPACE_U32 = "R'G'B' u32"
    RGBA_SPACE_U32 = "R'G'B'A u32"


def _fyle_path(out_fyle_name: str) -> str:
    return os.path.join(tempfile.gettempdir(), out_fyle_name)


def store_buffer_all_formats(drawable_in: Gimp.Drawable):
    """
    Wacky testing method that writes the Gegl buffer of a drawable, in all the supported RGB and RGBA formats.
    This allows the formats to be searched and compared.
    Writes the Gegl buffer of a drawable to a set of binary files. Files are written in the temporary directory, each
    with a filename prefix from the drawable's name, then the name of the Babl format, then a time-date stamp, and a
    \"raw\" extension.
    :param drawable_in: The drawable to write
    :return: None
    """
    for babl_format in BablFormat:
        store_buffer(drawable_in=drawable_in, babl_format=babl_format)


def store_buffer(drawable_in: Gimp.Drawable, babl_format: BablFormat = BablFormat.RGBA_SPACE_U16):
    """
    Writes the Gegl buffer of a drawable to a binary file. File is written in the temporary directory, with a filename
    prefix from the drawable's name then the name of the Babl format, then a time-date stamp, and a \"raw\" extension.
    :param drawable_in: The drawable to write
    :param babl_format: The Babl format.
    :return: None
    """
    layer_name = drawable_in.get_name()
    time_part = datetime.now().strftime("%Y_%m_%d-%I_%M_%f")
    raw_name = f"{layer_name}_{babl_format.name}_{time_part}.raw"
    file_path_raw = _fyle_path(raw_name)
    image_bytes_raw = drawable_bytes(drawable_in=drawable_in, babl_format=babl_format)
    LOGGER_GEGL_UTILS.info(f"Writing buffer data to \"{file_path_raw}\"")
    with open(file_path_raw, "wb") as binary_file:
        binary_file.write(image_bytes_raw)


def drawable_bytes(drawable_in: Gimp.Drawable, babl_format: BablFormat = BablFormat.RGBA_SPACE_U16) -> bytes:
    """
     Returns an array of 64-bit pixels.
     In detail, a 1D array of bytes, which is a flattened matrix (2D array) of width * height pixels. Each pixel has a
     count of channels_per_pixel values: If there's no alpha chanel, each pixel has 1 or 3 values. If there's an alpha
     chanel, each pixel has 2 OR 4 values.
     Each value is an 16-bit little byte-ordered, unsigned int. Accordingly, looking at the bytes, each colored pixel
     appears as [RR, GG, BB] for RGB, and [RR, GG, BB, AA] for RGBA.
    :param drawable_in: The drawable that's the source of the result.
    :param babl_format: For normal use, choose RGBA_SPACE_U16, which is the default. Other values at best, yield
    undocumented results. See # See https://gegl.org/babl/Reference.html#R_G_B_A_u16 , etc.
    :return: An array of 64-bit pixels.
    """
    width: int = drawable_in.get_width()
    height: int = drawable_in.get_height()
    buffer: Gegl.Buffer = drawable_in.get_buffer()
    rect: Gegl.Rectangle = Gegl.Rectangle.new(0, 0, width, height)
    # see https://developer.gimp.org/api/gegl/method.Buffer.get.html
    src_pixels: bytes = buffer.get(rect,  # GeglRectangle rect
                                   1.0,  # double scale
                                   babl_format.value,  # Babl RGBA format
                                   Gegl.AbyssPolicy.CLAMP  # GeglAbyssPolicy repeat_mode
                                   )
    return src_pixels
