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


import json
import os
import platform
import tempfile
from os import path
from os.path import exists
from typing import Dict, Callable
from utilities.type_utils import *

GLOBAL_PARASITE_SUFFIX = "_GLOBAL_JSON_UTF8_DATA"
HOME = os.path.expanduser('~')
LOGGER_PRSTU = logging.getLogger(__name__)
LOGGER_PRSTU.setLevel(logging.INFO)
TEMP_DEFAULT_DIR = tempfile.gettempdir()
USER_HOME_DIR = os.path.expanduser('~')
PREFERRED_ENV_KEY = "STABLE_DIFF_PREF_ROOT"  # Preferred root, over the user's home dir "~/data/stable_diffusion"

SD_DATA_TREE: List[str] = [
    "models",
    "prompts",
    "workflows",
    "models/checkpoints",
    "models/clip",
    "models/clip_vision",
    "models/configs",
    "models/controlnets",
    "models/diffusers",
    "models/embeddings",
    "models/gligen",
    "models/hypernetworks",
    "models/loras",
    "models/style_models",
    "models/unet",
    "models/upscale_models",
    "models/vae",
    "models/vae_approx",
    "workflows/Sytan-SDXL-ComfyUI",
]


def get_persistent_dir() -> str:
    gsd = get_persistent_dir_name()
    new_persistent_dir()
    return gsd


def get_temporary_dir() -> str:
    gsd = get_temporary_dir_name()
    new_persistent_dir()
    return gsd


def get_persistent_dir_name() -> str:
    if platform.system().lower() == 'windows':
        return path.expandvars(r'%APPDATA%\gimp_plugin_data')
    if platform.system().lower() == 'linux':
        return path.expandvars(r'$HOME/.config/gimp_plugin_data')
    if platform.system().lower() == 'darwin':
        return path.expandvars(r'$HOME/.config/gimp_plugin_data')
    raise Exception("Unsupported platform")


def get_temporary_dir_name() -> str:
    return tempfile.gettempdir()


def get_persistent_json_path(plugin_name_long: str) -> str:
    return join_persistent(plugin_name_long + ".json")


def get_temporary_json_path(plugin_name_long: str) -> str:
    return join_temporary(plugin_name_long + ".json")


def join_persistent(item_name: str) -> str:
    return os.path.join(get_persistent_dir(), item_name)


def join_temporary(item_name: str) -> str:
    return os.path.join(get_temporary_dir(), item_name)


def make_sd_data_tree(root_dir: str) -> bool:
    created: bool = False
    if not os.path.isdir(root_dir):
        os.makedirs(root_dir)
        created = True
    if not os.path.isdir(root_dir):
        raise IOError(f"Failed to create directory \"{root_dir}\"")
    for sub_dir in SD_DATA_TREE:
        try:
            location = os.path.join(root_dir, sub_dir)
            if not os.path.isdir(location):
                LOGGER_PRSTU.info(f"Creating \"{location}\"")
                os.makedirs(location)
        except IOError as ioe:
            LOGGER_PRSTU.exception(ioe)
    return created


def new_persistent_dir() -> bool:
    gsd = get_persistent_dir_name()
    # There is a bug in Microsoft Python, don't use it! exists falsely returns true!
    if os.path.exists(gsd):
        return False
    os.makedirs(gsd)
    if os.path.isdir(gsd):
        return True
    fail_message = "Failed to create directory " + gsd
    LOGGER_PRSTU.error(fail_message)
    raise IOError(fail_message)


def new_temporary_dir() -> bool:
    gsd = get_temporary_dir_name()
    # There is a bug in Microsoft Python, don't use it! exists falsely returns true!
    if os.path.exists(gsd):
        return False
    os.mkdir(gsd)
    if os.path.isdir(gsd):
        return True
    fail_message = "Failed to create directory " + gsd
    LOGGER_PRSTU.error(fail_message)
    raise IOError(fail_message)


def read_persistent_dictionary(plugin_name_long: str) -> Dict:
    return _read_dict_from_fs(get_persistent_json_path(plugin_name_long))


def read_temporary_dictionary(plugin_name_long: str) -> Dict:
    return _read_dict_from_fs(get_temporary_json_path(plugin_name_long))


def _read_dict_from_fs(storage_path: str) -> Dict:
    data: Dict = None  # noqa
    try:
        if os.path.exists(storage_path):
            # LOGGER_PRSTU.debug("_read_dict_from_fs() loading from " + storage_path)
            with open(storage_path, 'r') as in_file:
                # Parse JSON into an object with attributes corresponding to dict keys.
                data = json.load(in_file)
                return data
        else:
            return data
    except Exception as an_exception:
        LOGGER_PRSTU.error("Problem reading " + storage_path)
        LOGGER_PRSTU.exception(an_exception)


def remove_persistent_dictionary(plugin_name_long: str):
    storage_path = get_persistent_json_path(plugin_name_long)
    if exists(storage_path):
        LOGGER_PRSTU.info("Deleting persistent dictionary storage " + plugin_name_long)
        os.remove(storage_path)
    else:
        LOGGER_PRSTU.debug("Dictionary persistent storage " + plugin_name_long + " already deleted.")


def remove_temporary_dictionary(plugin_name_long: str):
    storage_path = get_temporary_json_path(plugin_name_long)
    if exists(storage_path):
        LOGGER_PRSTU.info("Deleting temporary dictionary storage " + plugin_name_long)
        os.remove(storage_path)
    else:
        # LOGGER_PRSTU.debug("Dictionary temporary storage " + plugin_name_long + " already deleted.")
        pass


def sd_root_dir(create: bool = False) -> str:
    sd_data_root: str | None = None
    if platform.system().lower() == 'windows':
        # Users can set STABLE_DIFF_PREF_ROOT to where-ever, but beware platform issues.
        preferred = os.environ.get('STABLE_DIFF_PREF_ROOT', "🤓🤓NOT_A_DIR🤓🤓")
        fallback = path.expanduser("~/data/stable_diffusion")
        preferred_exists = os.path.isdir(preferred)
        if preferred_exists:
            sd_data_root = preferred
        else:
            sd_data_root = fallback
    if platform.system().lower() == 'linux':
        sd_data_root = path.expanduser("~/data/stable_diffusion")
    if platform.system().lower() == 'darwin':
        sd_data_root = path.expanduser("~/data/stable_diffusion")
    if sd_data_root is None:
        raise NotImplementedError(f"Unsupported platform{platform.system()}")

    if os.path.isdir(sd_data_root):
        return sd_data_root
    if create:
        os.makedirs(sd_data_root)
    if not os.path.isdir(sd_data_root):
        raise IOError(f"SD data root dir \"{sd_data_root}\" not a directory and failed to create.")
    return sd_data_root


def seems_legit_file(file_path: str, extensions: List[str] | None = None) -> bool:
    if extensions:
        fpl = file_path.lower()
        found = False
        for ext in extensions:
            if fpl.endswith(ext.lower()):
                found = True
                break
        if not found:
            return False
    if not os.path.exists(file_path):
        raise IOError(f"Could not find \"{file_path}\"")
    if not os.path.isfile(file_path):
        return False
    file_stats = os.stat(file_path)
    sz = file_stats.st_size
    if not sz > 0:
        LOGGER_PRSTU.error(f"File \"{file_path}\" is zero-size.")
        return False
    return True


# NOTE: Several of these predicates are untested, because I don't have example files to put in the directories.
def seems_checkpoint(file_path: str) -> bool:
    return seems_legit_file(file_path=file_path, extensions=[".ckpt", ".safetensors", ".sft"])


def seems_clip(file_path: str) -> bool:
    return seems_legit_file(file_path=file_path, extensions=[".clip", ".clp", ".safetensors", ".sft"])


def seems_config(file_path: str) -> bool:
    return seems_legit_file(file_path=file_path, extensions=[".config", ".cfg"])


def seems_controlnet(file_path: str) -> bool:
    return seems_legit_file(file_path=file_path, extensions=[".crlnet", ".t2i"])


def seems_diffuser(file_path: str) -> bool:
    return seems_legit_file(file_path=file_path, extensions=[".diff", ".diffuse", ".safetensors", ".sft"])


def seems_embedding(file_path: str) -> bool:
    return seems_legit_file(file_path=file_path, extensions=[".embd", ])


def seems_gligen(file_path: str) -> bool:
    return seems_legit_file(file_path=file_path, extensions=[".gligen", ])


def seems_hypernetwork(file_path: str) -> bool:
    return seems_legit_file(file_path=file_path, extensions=[".hnet", ])


def seems_json(file_path: str) -> bool:
    return seems_legit_file(file_path=file_path, extensions=[".json", ])


def seems_lora(file_path: str) -> bool:
    return seems_legit_file(file_path=file_path, extensions=[".lora", ".safetensors", ".sft"])


def seems_pytorch(file_path: str) -> bool:
    return seems_legit_file(file_path=file_path, extensions=[".pth", ".pytorch"])


def seems_style_model(file_path: str) -> bool:
    return seems_legit_file(file_path=file_path, extensions=[".style", ])


def seems_unet(file_path: str) -> bool:
    return seems_legit_file(file_path=file_path, extensions=[".unet", ".safetensors", ".sft"])


def seems_vae(file_path: str) -> bool:
    return seems_legit_file(file_path=file_path, extensions=[".vae", "vae.safetensors", "vae.sft"])


def store_persistent_dictionary(plugin_name_long: str, dictionary: Dict):
    storage_path = get_persistent_json_path(plugin_name_long)
    try:
        LOGGER_PRSTU.info("Writing to " + storage_path)
        with open(storage_path, 'w') as outfile:
            sorted_keys = sorted(dictionary.keys(), key=int_or_str)
            json.dump({i: dictionary[i] for i in sorted_keys}, outfile, indent=2)
    except IOError as thrown:
        LOGGER_PRSTU.error("Problem writing " + storage_path)
        raise thrown


def store_temporary_dictionary(plugin_name_long: str, dictionary: Dict):
    storage_path = get_temporary_json_path(plugin_name_long)
    try:
        # LOGGER_PRSTU.debug("writing to " + storage_path)
        with open(storage_path, 'w') as outfile:
            sorted_keys = sorted(dictionary.keys(), key=int_or_str)
            json.dump({i: dictionary[i] for i in sorted_keys}, outfile, indent=2)
    except IOError as thrown:
        LOGGER_PRSTU.error("Problem writing " + storage_path)
        raise thrown


def list_from_fs(fs_path: str,
                 predicate: Callable[[str], bool] = seems_json,
                 permitted_empties: List[str] | None = None,
                 special_entries: List[str] | None = None) -> List[str]:
    if not os.path.exists(fs_path):
        raise IOError(f"Could not find \"{fs_path}\"")
    if not os.path.isdir(fs_path):
        raise IOError(f"\"{fs_path}\" is not a directory")
    raw_listing: List[str] = os.listdir(fs_path)
    len_raw: int = len(raw_listing)
    # LOGGER_PRSTU.debug(f"Found {len_raw} total items in {fs_path}")
    if len_raw == 0:
        fail_msg: str = f"{fs_path} is an empty directory."
        if permitted_empties is not None and permitted_empties:
            for suffix in permitted_empties:
                if fs_path.endswith(suffix):
                    return []
        raise IOError(fail_msg)
    filtered_listing: List[str] = list(thing for thing in raw_listing if predicate(os.path.join(fs_path, thing)))
    len_filtered: int = len(filtered_listing)
    # LOGGER_PRSTU.debug(f"Found {len_filtered} matched items in {fs_path}")
    if len_filtered == 0:
        complaint: str = f"Predicate \"{predicate.__name__}\" filtered out all items from listing of {fs_path}!"
        LOGGER_PRSTU.debug(complaint)
        # Disable and enable the following exception as the situation demands.
        if len_raw >= 2:  # USUALLY Not a problem if dir is practically empty.
            raise IOError(complaint)
    if special_entries is not None and special_entries:
        LOGGER_PRSTU.debug(f"prefixing {special_entries} to {filtered_listing}")
        return special_entries + filtered_listing
    return filtered_listing
