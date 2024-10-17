#  Copyright (c) 2023. Charles Hymes
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

import logging
import numbers
from typing import Any, List

ALL_NUMERIC_LIST_MSG = "List is all numeric."
CHANNEL_BYTE_DEPTH_GIMP: int = 2
CHANNEL_BYTE_DEPTH_PNG: int = 2
SIXTEEN_BYTES: int = (2**16)-1
SIXTEEN_BYTES_STR: str = SIXTEEN_BYTES.to_bytes(2, 'big').hex()
SEVENTEEN_BYTES: int = 2**16
SEVENTEEN_BYTES_STR: str = SEVENTEEN_BYTES.to_bytes(3, 'big').hex()
SIXTY_FOUR_BYTES: int = (2**64)-1
SIXTY_FOUR_BYTES_STR: str = SIXTY_FOUR_BYTES.to_bytes(8, 'big').hex()


def uint64_to_uint16_channel_value(orig_value: int):
    divided: float = orig_value / SIXTY_FOUR_BYTES
    # Here, floating point prevents difference between SEVENTEEN_BYTES vs SIXTEEN_BYTES
    condensed = int(SIXTEEN_BYTES * divided)
    return condensed


def as_strings_deeply(data: Any):
    """Recursively converts dictionary keys to strings."""
    if isinstance(data, str):
        return str(data)
    if not isinstance(data, dict):
        return data
    return dict((str(k), as_strings_deeply(v))
                for k, v in data.items())


def attempt_parse(datum) -> Any:
    # So far, all node JSON is dicts, lists, and strings. Numbers and bools are often, but not allways, wrapped as strs
    if isinstance(datum, dict):
        raise NotImplementedError("dict types are not currently supported.")
    if isinstance(datum, list):
        data: List = datum
        if len(data) < 2:
            raise ValueError("List is Empty or singleton.")
        if is_all_numeric_list(some_list=data):
            raise TypeError(ALL_NUMERIC_LIST_MSG)
        if is_all_nonnumerical_strings(some_list=data):
            return data
        if is_homogenous_list(some_list=data):
            return data
        else:
            raise TypeError("Heterogeneous List")

    if isinstance(datum, str):
        if is_numerical(datum):
            return float.__name__
        try:
            bool_of(datum)  # noqa
            return bool.__name__
        except:  # noqa
            pass
        return str.__name__
    if is_numerical(datum):
        return float.__name__
    datum_type = type(datum)
    datum_type_name = datum_type.__name__
    message = "Unsupported data type %s" % datum_type_name
    raise NotImplementedError(message)


def bool_of(string: str, include_digits=False) -> bool:
    """
    Strings consisting of or containing digits will raise type errors unless include_digits is true.
    Strings of floats will raise type errors. ints other than 1 ot 0 will raise type errors.
    :param string:
    :param include_digits: If true "0" and "1" will be parsed as booleans.
    :return:
    """
    if isinstance(string, bool):
        return string
    if string.lower() in ['true', 't', 'y', 'yes', 'enable', 'enabled', 'yeah', 'yup', 'certainly', 'uh-huh']:
        return True
    if string.lower() in ['false', 'f', 'n', 'no', 'disable', 'disabled', 'nope', 'nah', 'no-way', 'nuh-uh']:
        return False
    if include_digits:
        if string.lower() == '1':
            return True
        if string.lower() == '0':
            return False
    raise TypeError("Could not interpret \"%s\" as bool" % string)


def bool_safe_of(string: str) -> bool:
    if isinstance(string, bool):
        return string
    try:
        if string is not None and (string.strip() != ""):
            return bool_of(string)
        return False
    except (KeyError, ValueError):
        return False


def float_of(datum) -> float:
    """This function will be enhanced to be more robust than standard float()"""
    if not is_numerical(datum):
        raise TypeError("Cannot convert \"%s\" into number." % str(datum))
    return float(datum)


def float_or_str(datum: str) -> float | str:
    if isinstance(datum, float):
        return datum
    subject = datum.strip()
    if not is_numerical(subject):
        return datum
    try:
        return float(subject)
    except Exception as conversion_error:
        logging.exception(conversion_error)
        raise conversion_error


def int_or_str(datum: str) -> int | str:
    if isinstance(datum, int):
        return datum
    subject = datum.strip()
    if not is_numerical(subject):
        return datum
    try:
        return int(subject)
    except Exception as conversion_error:
        logging.exception(conversion_error)
        raise conversion_error


def is_all_nonnumerical_strings(some_list: List) -> bool:
    """
    Opens strs found as items of some_list, returns False if any of them can be parsed as numerical
    :param some_list: the list to evaluate.
    :return: True if all items are of type str, and none of the contents of each str are numerical.
    """
    for item in some_list:
        if not isinstance(item, str):
            return False
        if is_numerical(item):
            return False
    return True


def is_all_numeric_list(some_list: List) -> bool:
    for item in some_list:
        if not is_numerical(item):
            return False
    return True


def is_homogenous_list(some_list: List) -> bool:
    f_type: type = type(some_list[0])
    for item in some_list:
        if not isinstance(item, f_type):
            return False
    return True


def is_numerical(thing) -> bool:
    if isinstance(thing, numbers.Number):
        return True
    if isinstance(thing, str):
        if thing.isnumeric():
            return True
        try:
            as_float: float = float(thing)  # noqa
            return True
        except:  # noqa
            pass
    try:
        as_bool: bool = bool_of(thing)  # noqa
        return True
    except:  # noqa
        pass
    return False


def restack_image_array(image_array: bytes,
                        width: int,
                        height: int,
                        channels_per_pixel: int) -> list[list[int]]:
    """
    The image_array is 16 bits/2 bytes per channel. In other words, each channel is an
    unsigned int:
     [RR, GG, BB, AA].
     For %50 gray:
     CB32, CB32, CB32, 003C
    :param image_array: A 1D array of bytes, which is a flattened 2D array of width * height pixels. Each pixel has a
     count of channels_per_pixel values: If there's no alpha chanel, each pixel has 1 or 3 values. If there's an alpha
     chanel, each pixel has 2 OR 4 values.
     SURPRISE! Each value is a 64-bit unsigned long long. Accordingly, looking at
     the bytes, each colored pixel appears as [RRRRRRRR, GGGGGGGG, BBBBBBBB] for RGB, and
     [RRRRRRRR, GGGGGGGG, BBBBBBBB, AAAAAAAA] for RGBA.
    :param channels_per_pixel: 1 for grayscale, 2 for grayscale + alpha, 3 for RGB, 4 for RGB + alpha
    :param width: width of image in pixels. input_row length must be (CHANNEL_BYTE_DEPTH_PNG bytes *
     channels_per_pixel * width)
    :param height: height of image in pixels, will be the count of input_rows.
    :return: a new 2D array of ints, of height rows, and each output_row with a length of channels_per_pixel * width
    """
    # See https://docs.python.org/3/library/array.html
    value_count: int = channels_per_pixel * width * height
    total_len: int = CHANNEL_BYTE_DEPTH_GIMP * value_count
    len_actual = len(image_array)
    if total_len != len_actual:
        msg_err = f"Actual length of image_array={len_actual}, required length is {total_len}"
        raise ValueError(msg_err)
    # row_len_output_expected = channels_per_pixel * width
    pixel_index: int
    output_2d_array: list[list[int]] = list()
    i_channel: int
    i_column: int
    i_row: int
    for i_row in range(height):
        lossy_row: list[int] = list()
        for i_column in range(width):
            for i_channel in range(channels_per_pixel):
                pixel_index = i_channel + (i_column * channels_per_pixel) + (i_row * width * channels_per_pixel)
                # logging.warning(f"i={pixel_index}, i_channel={i_channel},i_column={i_column}, i_row={i_row}")
                abs_start: int = pixel_index * CHANNEL_BYTE_DEPTH_GIMP
                abs_end: int = abs_start + CHANNEL_BYTE_DEPTH_GIMP
                # logging.warning(f"absolute_range=[{abs_start}:{abs_end}]")
                in_bytes: bytes = image_array[abs_start:abs_end]
                value_uint16: int = int.from_bytes(bytes=in_bytes, byteorder="little", signed=False)
                lossy_row.append(value_uint16)
        # row_len_actual = len(lossy_row)
        # if row_len_actual != row_len_output_expected:
        #     raise ValueError(f"row_len should be {row_len_output_expected}, is actually {row_len_actual}")
        # else:
        #     validation_message: str = f"row_len={row_len_actual}"
        #     logging.warning(validation_message)
        output_2d_array.append(lossy_row)
    return output_2d_array


def round_to_multiple(value, multiple):
    return multiple * round(float(value) / multiple)


def type_in(item_type: type, some_list: List) -> bool:
    return item_type in some_list


def types_in(some_list: List) -> list[type]:
    return [type(item) for item in some_list]
