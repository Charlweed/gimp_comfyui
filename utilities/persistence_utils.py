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

import gi
from enum import Enum, auto
gi.require_version('Gimp', '3.0')  # noqa: E402
gi.require_version('GimpUi', '3.0')  # noqa: E402
gi.require_version("Gtk", "3.0")  # noqa: E402
gi.require_version('Gdk', '3.0')  # noqa: E402
# noinspection PyUnresolvedReferences
from gi.repository import Gdk, Gio, Gimp, GimpUi, Gtk, GLib, GObject
from utilities.long_term_storage_utils import *

# "ephemeral" is for memory-only data. The data is not persisted in any form between GIMP sessions, and is lost
# when GIMP is exited. Global non-persistent parasites should work this way.
# "temporary" is for data that is saved to a temporary system storage, for example a temporary file on the filesystem.
# Any data from previous GIMP sessions is ignored or deleted.
# "volatile" reserved.
# "persistent" is for data that is saved to long-term system storage, for example a file in the users directory of a
# filesystem. Data is shared from one GIMP session to another.
# "permanent" reserved


class Longevity(Enum):
    EPHEMERAL = auto()
    TEMPORARY = auto()
    VOLATILE = auto()
    PERSISTENT = auto()


def _assert_parasite_found(parasite_name: str):
    all_paras = Gimp.get_parasite_list()
    if all_paras is None:
        raise ValueError("No global parasites, Gimp.get_parasite_list() returned None")
    if len(all_paras) == 0:
        raise ValueError("No global parasites, Gimp.get_parasite_list() returned []")
    global_para = Gimp.get_parasite(parasite_name)
    if global_para is None:
        message = "Gimp.get_parasite(\"%s\") returned %s" % (parasite_name, str(global_para))
        raise ValueError(message)


def _demo_parasite_issue():
    name = "DEMONSTRATION_GLOBAL_PARASITE"
    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et"  # noqa
    encoded_ut8 = text.encode('utf-8')
    data_bytes = bytes(encoded_ut8)
    fresh_parasite = Gimp.Parasite.new(name=name, flags=0, data=data_bytes)
    Gimp.attach_parasite(parasite=fresh_parasite)
    _assert_parasite_found(parasite_name=name)  # ValueError is raised by _assert_parasite_found


def _new_parasite(plugin_name_long: str, json_str: str) -> Gimp.Parasite:
    if plugin_name_long is None:
        raise ValueError("plugin_name_long cannot be None")
    if not plugin_name_long.strip():
        raise ValueError("plugin_name_long cannot be empty or whitespace")
    if json_str is None:
        raise ValueError("json_str cannot be None")
    if not json_str.strip():
        raise ValueError("json_str cannot be empty or whitespace")
    name = plugin_name_long + GLOBAL_PARASITE_SUFFIX
    encoded_ut8 = json_str.strip().encode('utf-8')
    bytes_list = list(encoded_ut8)

    parasite_out = Gimp.Parasite.new(name=name, flags=0, data=bytes_list)
    if parasite_out is None:
        raise SystemError("Failed to create parasite")
    name_out = parasite_out.get_name()
    if name_out != name:
        raise SystemError("fresh parasite name \"%s\" != original name \"%s\"" % (name_out, name))
    return parasite_out


def contains(plugin_name_long: str, key: str, longevity: Longevity) -> bool:
    if plugin_name_long is None:
        raise ValueError("plugin_name_long cannot be None")
    if not plugin_name_long.strip():
        raise ValueError("plugin_name_long cannot be empty or whitespace")
    if key is None:
        raise ValueError("key cannot be None")
    if not key.strip():
        raise ValueError("key cannot be empty or whitespace")
    match longevity:
        case Longevity.EPHEMERAL:
            global_dict = read_ephemeral_dictionary(plugin_name_long=plugin_name_long)
        case Longevity.TEMPORARY:
            global_dict = read_temporary_dictionary(plugin_name_long=plugin_name_long)
        case Longevity.PERSISTENT:
            global_dict = read_persistent_dictionary(plugin_name_long=plugin_name_long)
        case _:
            raise ValueError("Longevity case %s is not supported" % str(longevity))
    if global_dict is None:
        return False
    return key in global_dict


def get(plugin_name_long: str, key: str, default: str, longevity: Longevity) -> str:
    # LOGGER_PRSTU.debug("get:")
    if plugin_name_long is None:
        raise ValueError("plugin_name_long cannot be None")
    if not plugin_name_long.strip():
        raise ValueError("plugin_name_long cannot be empty or whitespace")
    if key is None:
        raise KeyError("key cannot be None")
    if not key.strip():
        raise KeyError("key cannot be empty or whitespace")
    match longevity:
        case Longevity.EPHEMERAL:
            global_dict = read_ephemeral_dictionary(plugin_name_long=plugin_name_long)
        case Longevity.TEMPORARY:
            global_dict = read_temporary_dictionary(plugin_name_long=plugin_name_long)
        case Longevity.PERSISTENT:
            global_dict = read_persistent_dictionary(plugin_name_long=plugin_name_long)
        case _:
            raise ValueError("Longevity case %s is not supported" % str(longevity))
    if global_dict is None:
        message = "No global dictionary for %s, therefore no key \'%s\'" % (plugin_name_long, key)
        # LOGGER_PRSTU.debug(message)
        if default is not None:
            return default
        else:
            raise KeyError(message)
    if key in global_dict:
        message = "found key \'%s\'" % key
        LOGGER_PRSTU.debug(message)
        return str(global_dict[key])
    if default is not None:
        return default
    raise KeyError("No key \'%s\' in global dict for %s" % (key, plugin_name_long))


def put(plugin_name_long: str, key: str, value: str, longevity: Longevity):
    if plugin_name_long is None:
        raise ValueError("plugin_name_long cannot be None")
    if not plugin_name_long.strip():
        raise ValueError("plugin_name_long cannot be empty or whitespace")
    if key is None:
        raise KeyError("key cannot be None")
    if not key.strip():
        raise KeyError("key cannot be empty or whitespace")
    if value is None or (not value):
        value_out = ""
    else:
        value_out = str(value)
    # LOGGER_PRSTU.debug("put(%s);%s" % (key, str(value_out)))
    minidict: Dict[str, str] = {key: value_out}
    merged_dict: Dict
    match longevity:
        case Longevity.EPHEMERAL:
            previous_dict = read_ephemeral_dictionary(plugin_name_long=plugin_name_long)
        case Longevity.TEMPORARY:
            previous_dict = read_temporary_dictionary(plugin_name_long=plugin_name_long)
        case Longevity.PERSISTENT:
            previous_dict = read_persistent_dictionary(plugin_name_long=plugin_name_long)
        case _:
            raise ValueError("Longevity case %s is not supported" % str(longevity))
    if previous_dict is None:
        merged_dict = minidict
    else:
        merged_dict = previous_dict | minidict

    match longevity:
        case Longevity.EPHEMERAL:
            store_ephemeral_dictionary(plugin_name_long=plugin_name_long, dictionary=merged_dict)
        case Longevity.TEMPORARY:
            store_temporary_dictionary(plugin_name_long=plugin_name_long, dictionary=merged_dict)
        case Longevity.PERSISTENT:
            store_persistent_dictionary(plugin_name_long=plugin_name_long, dictionary=merged_dict)
        case _:
            raise ValueError("Longevity case %s is not supported" % str(longevity))
    return


def read_ephemeral_dictionary(plugin_name_long: str) -> Dict:
    if plugin_name_long is None:
        raise ValueError("plugin_name_long cannot be None")
    if not plugin_name_long.strip():
        raise ValueError("plugin_name_long cannot be empty or whitespace")
    name = plugin_name_long + GLOBAL_PARASITE_SUFFIX
    established_para: Gimp.Parasite
    # noinspection PyBroadException
    try:
        LOGGER_PRSTU.debug("Looking for global parasite " + name)
        if name in Gimp.get_parasite_list():  # Unfortunately, this does not prevent warnings from LibGimp
            established_para = Gimp.get_parasite(name)
            LOGGER_PRSTU.debug("Gimp.get_parasite(\"%s\") returned %s" % (name, str(established_para)))
        else:
            established_para = None
    except Exception as thrown: # noqa
        LOGGER_PRSTU.error(str(thrown))
        LOGGER_PRSTU.exception("Exception searching for " + name)
        established_para = None
    if established_para is None:
        LOGGER_PRSTU.warning("No parasite for \"%s\", returning None" % name)
        # noinspection PyTypeChecker
        return None  # noqa

    byte_list = bytes(established_para.get_data())
    json_str = byte_list.decode('utf-8')
    LOGGER_PRSTU.debug("Extracted data from " + name + "\n" + json_str + "\n")
    global_dict: Dict = json.loads(json_str)
    return global_dict


def store_ephemeral_dictionary(plugin_name_long: str, dictionary: Dict):
    json_short_str: str = json.dumps(dictionary, sort_keys=True, indent=2)
    fresh_parasite = _new_parasite(plugin_name_long=plugin_name_long, json_str=json_short_str)
    if fresh_parasite is None:
        raise SystemError("Failed to create parasite for " + plugin_name_long)
    try:
        Gimp.attach_parasite(fresh_parasite)
        _assert_parasite_found(parasite_name=plugin_name_long + GLOBAL_PARASITE_SUFFIX)
    except Exception as thrown:
        LOGGER_PRSTU.error(str(thrown))
        LOGGER_PRSTU.exception("Problem attaching parasite for" + plugin_name_long)
        raise thrown
