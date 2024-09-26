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

import base64
import logging
import os
import sys
import tempfile

__GREEN_DIAMOND_FILE_PATH     = r"green_diamond_00.png"   # noqa
__GREEN_PIXEL_FILE_PATH       = r"green_pixel_00.png"     # noqa
__GREEN_SQUARE_FILE_PATH      = r"green_square_8x8.png"   # noqa
__GRAY_SQUARE_FILE_PATH       = r"512x512_middle_gray_gimp.png"   # noqa
__GRAY_SMALL_SQUARE_FILE_PATH = r"008x008_middle_gray.png"   # noqa
__LAMP_FILE_PATH              = r"magic_lamp_160x86.png"  # noqa


def _assets_dir_path():
    script_filename = os.path.realpath(__file__)
    script_dir_path = os.path.dirname(script_filename)
    return os.path.join(script_dir_path, "../assets")


def _asset_path(asset_name: str):
    return os.path.join(_assets_dir_path(), asset_name)


def load_image_b64_bytes(png_file_path_str: str = __GREEN_SQUARE_FILE_PATH) -> bytes:
    logging.warning(f"Current Working Directory={os.getcwd()}")
    with open(png_file_path_str, "rb") as data:
        data_base64 = base64.b64encode(data.read())  # encode to base64 (bytes)
        return data_base64


def load_image_raw_bytes(png_file_path_str: str = __GREEN_SQUARE_FILE_PATH) -> bytes:
    logging.warning(f"Current Working Directory={os.getcwd()}")
    file_path: str = _asset_path(png_file_path_str)
    with open(file_path, "rb") as data:
        bytes_raw = data.read()
        return bytes_raw


def lamp_image_b64_bytes() -> bytes:
    return load_image_b64_bytes(png_file_path_str=__LAMP_FILE_PATH)


def green_square_raw_bytes() -> bytes:
    return load_image_raw_bytes(png_file_path_str=__GREEN_SQUARE_FILE_PATH)


def gray_square_raw_bytes() -> bytes:
    return load_image_raw_bytes(png_file_path_str=__GRAY_SQUARE_FILE_PATH)


def fyle_path(out_fyle_name: str) -> str:
    return os.path.join(tempfile.gettempdir(), out_fyle_name)


def store_img_bytes(subject_bytes: bytes, out_fyle_name: str):
    bytes_fyle_name = os.path.join(tempfile.gettempdir(), out_fyle_name)
    logging.warning(f"_store_img_bytes(): filename \"{bytes_fyle_name}\"")
    # Open the file for writing
    with open(bytes_fyle_name, 'wb') as fyle:
        fyle.write(subject_bytes)


def main() -> int:
    store_img_bytes(subject_bytes=green_square_raw_bytes(), out_fyle_name="green_square_8x8.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
