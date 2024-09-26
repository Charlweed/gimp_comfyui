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
import sys
from enum import Enum, auto
from types import MappingProxyType
from typing import TextIO
from utilities.long_term_storage_utils import *
from utilities.type_utils import *


class ReadOption(Enum):
    REPLACE = auto()
    MERGE_OVER = auto()
    MERGE_UNDER = auto()


def read_fallback(fallback_json_path: str = None, fail_on_missing: bool = True) -> Dict:
    if fallback_json_path is None:
        if fail_on_missing:
            raise IOError(f"JSON path argument was None.")
        else:
            return {}
    if not fallback_json_path.strip():
        if fail_on_missing:
            raise IOError(f"JSON path argument was empty or whitespace.")
        else:
            return {}
    if not os.path.exists(fallback_json_path):
        if fail_on_missing:
            raise IOError(f"{fallback_json_path} does not exist.")
        else:
            return {}
    result: Dict
    LOGGER_PRSTU.debug(f"Reading fallback JSON {fallback_json_path}.")
    with open(fallback_json_path, 'r') as in_file:
        result = json.load(in_file)
        if result is None:
            raise IOError(f"Failed to read config from fallback path {fallback_json_path}")
        if not fallback_json_path:
            raise IOError(f"Config from fallback path {fallback_json_path} is empty.")
    return result


class PersisterPetite:
    UUID_STR: str = "ad6a2895-bfb2-41f5-a521-ae641ed6ae47"
    LOGGER_PP = logging.getLogger("PersisterPetite")
    LOGGER_FORMAT_PP = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    SD_DATA_ROOT: str = sd_root_dir(create=True)
    make_sd_data_tree(SD_DATA_ROOT)
    _DEFAULT_CONFIG = {}
    DEBUG_ENV_KEY = "PYTHON_PERSISTER_DEBUG"

    @classmethod
    def is_debug_mode(cls):
        flag: str | None = os.environ.get(cls.DEBUG_ENV_KEY)
        if not flag:
            return False
        return bool_of(flag)

    def __init__(self, chassis, chassis_name: str, fallback_path: str = None, skip_initial_load: bool = False):
        if PersisterPetite.is_debug_mode():
            logging.basicConfig(format=PersisterPetite.LOGGER_FORMAT_PP, level=logging.DEBUG)
            PersisterPetite.LOGGER_PP.setLevel(logging.DEBUG)
        else:
            logging.basicConfig(format=PersisterPetite.LOGGER_FORMAT_PP, level=logging.INFO)
            PersisterPetite.LOGGER_PP.setLevel(logging.INFO)
        self._chassis = chassis
        self._chassis_name = chassis_name
        self._config: Dict = dict(PersisterPetite._DEFAULT_CONFIG)
        if not skip_initial_load:
            try:
                if fallback_path:
                    self.load_config_with_fallback(fallback_path=fallback_path)
                else:
                    self.load_config()
            except IOError as ioe:
                PersisterPetite.LOGGER_PP.exception(ioe)
                self._config = dict(PersisterPetite._DEFAULT_CONFIG)

    @property
    def chassis(self) -> Any:
        return self._chassis

    @property
    def chassis_name(self) -> str:
        return self._chassis_name

    @property
    def chassis_id(self) -> str:
        return f"{self._chassis_name}_{PersisterPetite.UUID_STR}"

    @property
    def configuration(self) -> MappingProxyType:
        if not self._config:
            raise SystemError("self._config is empty.")
        return MappingProxyType(self._config)

    @property
    def storage_path(self) -> str:
        json_path: str = get_persistent_json_path(self.chassis_id)
        json_file_exists = os.path.exists(json_path)
        if not json_file_exists:
            LOGGER_PRSTU.debug(f"{json_path} does not exist.")
        return json_path

    def storage_file_exists(self) -> bool:
        """
        Returns True if the storage file exists.
        :return: True if the storage file exists.
        """
        return os.path.exists(self.storage_path)

    def verify_storage_file_exists(self):
        """
        Raises IOError is the storage file does not exist.
        :return:
        """
        if not self.storage_file_exists():
            raise IOError(f"Could not find storage path \"{self.storage_path}\"")

    def dumps(self):
        if not self._config:
            raise SystemError(" self._config is empty")
        return json.dumps(self._config, indent=2, sort_keys=True)

    def log_config(self, logger: logging.Logger = LOGGER_PP, log_level=logging.INFO):
        logger.log(log_level, self.dumps())

    def load_config(self, read_option: ReadOption = ReadOption.MERGE_OVER) -> MappingProxyType:
        match read_option:
            case ReadOption.REPLACE:
                self._config = self._read_config()
            case ReadOption.MERGE_OVER:
                self._config.update(self._read_config())
            case ReadOption.MERGE_UNDER:
                d = self._read_config()
                d.update(self._config)
                self._config = d
        if self._config is None:
            raise SystemError("_read_config() returned None")
        if not self._config:
            LOGGER_PRSTU.debug("_read_config() returned empty dict.")
        return self.configuration

    def load_config_with_fallback(self, fallback_path: str,
                                  read_option: ReadOption = ReadOption.MERGE_OVER
                                  ) -> MappingProxyType:
        match read_option:
            case ReadOption.REPLACE:
                self._config = self._read_config()
            case ReadOption.MERGE_OVER:
                self._config.update(self._read_config())
            case ReadOption.MERGE_UNDER:
                d = self._read_config()
                d.update(self._config)
                self._config = d
        if self._config is None:
            raise SystemError("_read_config() returned None")
        if not self._config:
            self._config = read_fallback(fallback_json_path=fallback_path, fail_on_missing=True)
            if self._config is None:
                raise IOError(f"Failed to assign config from fallback path {fallback_path}")
            if not self._config:
                raise IOError(f"Config from fallback path {fallback_path} is empty.")
        return self.configuration

    def _read_config(self) -> Dict:
        json_path: str = self.storage_path
        json_file_exists = os.path.exists(json_path)
        if not json_file_exists:
            LOGGER_PRSTU.debug(f"{json_path} does not exist.")
            if self._DEFAULT_CONFIG is None:
                raise SystemError("_DEFAULT_CONFIG is None")
            if not self._DEFAULT_CONFIG:
                LOGGER_PRSTU.warning("_DEFAULT_CONFIG is empty.")
            return self._DEFAULT_CONFIG
        result: Dict = read_persistent_dictionary(self.chassis_id)
        return result

    def store_config(self):
        self._write_config(self._config)

    def store_if_missing(self):
        if os.path.exists(self.storage_path):
            return
        self.store_config()

    def store_defaults_if_missing(self, defaults: dict[str, Any]):
        if os.path.exists(self.storage_path):
            return
        LOGGER_PRSTU.info(f"Creating new {self.storage_path} from defaults.")
        self.update_config(defaults)
        self.store_config()

    def update_config(self, data: Dict):
        self._config.update(data)

    def _write_config(self, config: Dict):
        store_persistent_dictionary(self.chassis_id, dictionary=config)


def get_global_config_filename() -> str:
    """
    Will need to be re-written when PersisterPetite class is used in other plugins.
    :return: The config file for GimpComfyUI.
    """
    return f"GimpComfyUI_{PersisterPetite.UUID_STR}.json"


def read_global_config() -> MappingProxyType[str, Any]:
    """
    This function raises IOErrors if it cannot read the plugin's main config file
    :return: A read-only copy of the plugin's main config.
    """
    global_json_path = os.path.join(get_persistent_dir_name(), get_global_config_filename())
    if not os.path.isfile(global_json_path):
        raise IOError(f"Could not find config file \"{global_json_path}\"")
    json_file: TextIO
    with open(global_json_path, "r") as json_file:
        return MappingProxyType(json.load(json_file))


def get_comfy_svr_hostname() -> str:
    """
    This function raises IOErrors if it cannot read the plugin's main config file. It also raises a KeyError if
    the global configuration does not have the key "COMFYUI_HOST"
    :return: The hostname for the ComfyUI service, as stored in the plugin's global config.
    """
    all_config: MappingProxyType = read_global_config()
    return all_config["COMFYUI_HOST"]


def get_comfy_svr_port() -> int:
    """
    This function raises IOErrors if it cannot read the plugin's main config file. It also raises a KeyError if
    the global configuration does not have the key "COMFYUI_PORT"
    :return: The port number for the ComfyUI service, as stored in the plugin's global config.
    """
    all_config: MappingProxyType = read_global_config()
    return all_config["COMFYUI_PORT"]


def get_comfy_svr_origin() -> str:
    """
    This function raises IOErrors if it cannot read the plugin's main config file. It also raises a KeyError if
    the global configuration does not have the keys "COMFYUI_HOST" and "COMFYUI_PORT"
    :return: The hostname and port number for the ComfyUI service, as stored in the plugin's global config.
    """
    all_config: MappingProxyType = read_global_config()
    comfy_svr_host: str = all_config["COMFYUI_HOST"]
    comfy_svr_port: int = all_config["COMFYUI_PORT"]
    return f"{comfy_svr_host}:{comfy_svr_port}"


def main() -> int:
    chassis_instance: str = "String!"
    persister: PersisterPetite = PersisterPetite(chassis=chassis_instance, chassis_name="persisterpetite_testing_name")
    persister.log_config()
    return 0


if __name__ == '__main__':
    sys.exit(main())
