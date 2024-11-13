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
import json
import os
import platform

gi.require_version('GimpUi', '3.0')  # noqa: E402
from abc import ABC, abstractmethod
from gi.repository import GimpUi  # noqa
from os.path import expanduser
from types import MappingProxyType
from typing import Dict, Any, Set, FrozenSet
from utilities.cui_net_utils import upload_images_to_inputs
from utilities.persister_petite import PersisterPetite, ReadOption, get_comfy_svr_origin
from utilities.sd_gui_utils import LOGGER_SDGUIU, index_and_input
from workflow.node_accessor import NodesAccessor


class WorkflowDialogFactory(ABC):
    WORKFLOW_TAG = "_workflow_api"
    ASSET_DIR_NAME = "../assets"
    GIMP_COMFYUI_CONFIG_FILENAME = "comfyui_config.json"

    DEBUG_ENV_KEY = "WORKFLOW_FACTORY_DEBUG"

    @staticmethod
    def get_metaconfig_defaults() -> MappingProxyType[str, str]:
        local_platform: str = platform.system().lower()
        # Update when GIMP 3.0 is released!
        if local_platform == "windows":
            defaults = {
                "gimp_plugins_dir": expanduser("~/AppData/Roaming/GIMP/3.0/plug-ins"),
                "gimp_plugin_data_dir": expanduser("~/AppData/Roaming/gimp_plugin_data"),
                "comfyui_custom_nodes_dir": expanduser("~/ComfyUI/custom_nodes"),
                "stable_diffusion_data_dir": expanduser("~/ComfyUI")
            }
        else:
            if local_platform == "darwin":
                defaults = {
                    "gimp_plugins_dir": expanduser("~/Library/Application Support/GIMP/3.0/plug-ins"),
                    "gimp_plugin_data_dir": expanduser("~/.config/gimp_plugin_data"),
                    # Assuming no local ComfyUI
                    "comfyui_custom_nodes_dir": os.environ.get('TMPDIR', expanduser("~/")),
                    # Assuming no local stable_diffusion
                    "stable_diffusion_data_dir": os.environ.get('TMPDIR', expanduser("~/"))
                }
            else:
                defaults = {
                    "gimp_plugins_dir": expanduser("~/.var/app/org.gimp.GIMP/config/GIMP/3.0/plug-ins"),
                    "gimp_plugin_data_dir": expanduser("~/.config/gimp_plugin_data"),
                    "comfyui_custom_nodes_dir": expanduser("~/ComfyUI/custom_nodes"),
                    "stable_diffusion_data_dir": expanduser("~/ComfyUI")
                }
        return MappingProxyType(defaults)

    @classmethod
    def get_script_data_dir(cls):
        return cls.get_metaconfig_defaults()["gimp_plugin_data_dir"]

    @classmethod
    def get_comfyui_config_path(cls):
        return os.path.join(cls.get_script_data_dir(), cls.GIMP_COMFYUI_CONFIG_FILENAME)

    @classmethod
    def is_config_found(cls) -> bool:
        return os.path.isfile(cls.get_comfyui_config_path())

    @classmethod
    def verify_config_found(cls):
        if not cls.is_config_found():
            raise IOError(f"Could not find file \"{cls.get_comfyui_config_path()}\"")

    @classmethod
    def get_comfyui_dirs_dict(cls) -> MappingProxyType[str, str]:
        """
        Will throw IOException if "comfyui_config.json" not found.
        :return:
        """
        cls.verify_config_found()
        with open(cls.get_comfyui_config_path(), 'r') as in_file:
            data = MappingProxyType(json.load(in_file))
            return data

    def __init__(self,
                 accessor: NodesAccessor,
                 api_workflow: str,
                 dialog_config_chassis_name: str,
                 wf_data_chassis_name: str,
                 ):
        script_filename = os.path.realpath(__file__)
        self.__script_dir_path = os.path.dirname(script_filename)
        self.__asset_dir_path = os.path.join(self.__script_dir_path, WorkflowDialogFactory.ASSET_DIR_NAME)
        self.__fallback_path_lr = os.path.join(self.__asset_dir_path, "stable_diffusion_metadata_last_resort.json")
        fallback_path: str = os.path.join(self.__asset_dir_path, "comfyui_fallback_config.json")
        self._installation_persister: PersisterPetite = PersisterPetite(chassis=self,
                                                                        chassis_name=dialog_config_chassis_name,
                                                                        fallback_path=fallback_path
                                                                        )
        # Fallback data is only used if Persisted data is missing.
        fallback_path = os.path.join(self.__asset_dir_path, api_workflow)
        # LOGGER_SDGUIU.debug(f"{self.__class__.__class__}: fallback_path=\"{fallback_path}\"")
        # LOGGER_SDGUIU.debug(f"{self.__class__.__class__}: chassis_name=\"{wf_data_chassis_name}\"")
        self._workflow_persister: PersisterPetite = PersisterPetite(chassis=self,
                                                                    chassis_name=wf_data_chassis_name,
                                                                    fallback_path=fallback_path
                                                                    )
        self._accessor: NodesAccessor = accessor
        # LOGGER_SDGUIU.debug(f"{self.__class__.__class__}:"
        #                       f" (self._accessor.__class__=\"{self._accessor.__class__.__name__}\"")
        # LOGGER_SDGUIU.debug(f"{self.__class__.__class__}:"
        #                       f" (self._accessor.asset_dir_path=\"{self._accessor.asset_dir_path}\"")
        self._workflow_persister.update_config(self._accessor.nodes_dict)  # First the data from the read-only asset
        # Then the data that was persisted locally,
        self._workflow_persister.load_config(read_option=ReadOption.MERGE_OVER)
        # self._workflow_persister.log_config()
        self._workflow_data: Dict = dict(self._workflow_persister.configuration)  # Now, a dynamic working copy.
        self._image_paths: Set[tuple[str, str]] = set()
        self._mask_paths: Set[tuple[str, str]] = set()

    @property
    def accessor(self):
        return self._accessor

    @property
    def asset_dir(self):
        return self.__asset_dir_path

    @property
    def fallback_path_last_resort(self):
        return self.__fallback_path_lr

    @property
    def comfy_svr_origin(self) -> str:
        return get_comfy_svr_origin()

    @property
    def image_path_tuples(self) -> FrozenSet[tuple[str, str]]:
        return frozenset(self._image_paths)

    @property
    def mask_path_tuples(self) -> FrozenSet[tuple[str, str]]:
        return frozenset(self._mask_paths)

    @property
    def workflow_data(self) -> Dict[str, Any]:
        return dict(self._workflow_data)

    @abstractmethod
    def new_workflow_dialog(self,
                            title_in: str,
                            role_in: str,
                            blurb_in: str,
                            gimp_icon_name: str = GimpUi.ICON_DIALOG_INFORMATION
                            ) -> GimpUi.Dialog:
        pass

    def add_image_tuple(self, image_tuple: tuple[str, str]):
        self._image_paths.add(image_tuple)

    def add_mask_tuple(self, mask_tuple: tuple[str, str]):
        self._mask_paths.add(mask_tuple)

    def put_inputs(self, dialog_data: Dict):
        self.upload_dialog_images()
        self.upload_dialog_masks()
        for items in dialog_data.items():
            widget_name: str = items[0]
            input_value: Any = items[1]
            if widget_name.startswith("zzz"):
                continue
            index_str, input_name = index_and_input(widget_name=widget_name)
            if index_str == '00':
                continue
            # LOGGER_SDGUIU.debug(f"widget_name=\"{widget_name}\"; input_value=\"{input_value}\"")
            try:
                # LOGGER_SDGUIU.warning(f"self._workflow_data[{index_str}][inputs][{input_name}]=\"{input_value}\"")
                self._workflow_data[index_str]["inputs"][input_name] = input_value
            except KeyError as ke:
                jt = json.dumps(self._workflow_data, indent=2, sort_keys=True)
                LOGGER_SDGUIU.error(jt)
                LOGGER_SDGUIU.exception(ke)
                raise ke
        self._workflow_persister.update_config(self._workflow_data)
        # self._workflow_persister.log_config()
        self._workflow_persister.store_config()

    def inputs_dict(self, index_str: str) -> Dict:
        return self.accessor.nodes_dict[index_str]["inputs"]

    def upload_dialog_images(self):
        self.upload_dialog_blobs(self.image_path_tuples)

    def upload_dialog_masks(self):
        self.upload_dialog_blobs(self.mask_path_tuples)

    def upload_dialog_blobs(self, tuple_source: FrozenSet[tuple[str, str]]):
        blob_file_tuple: tuple[str, str]
        for blob_file_tuple in tuple_source:
            blob_path: str = blob_file_tuple[0]
            try:
                upload_images_to_inputs(
                    cu_origin=self.comfy_svr_origin,
                    image_file_path=blob_path
                )
            except Exception as e_err:
                LOGGER_SDGUIU.exception(e_err)

    def val_str(self, index_str: str, key: str) -> str:
        result = self.inputs_dict(index_str=index_str)[key]
        if not isinstance(result, str):
            raise ValueError("%s is not a str, it is a %s" % (key, str(type(result))))
        return result

    def val_float(self, index_str: str, key: str) -> float:
        result = self.inputs_dict(index_str=index_str)[key]
        if not isinstance(result, float):
            raise ValueError("%s is not a float, it is a %s" % (key, str(type(result))))
        return result

    def val_int(self, index_str: str, key: str) -> int:
        try:
            result = self.inputs_dict(index_str=index_str)[key]
        except KeyError as key_error:
            for a_key in self.inputs_dict(index_str=index_str).keys():
                LOGGER_SDGUIU.error("existing key %s" % str(a_key))
            raise key_error
        if not isinstance(result, int):
            raise ValueError("%s is not a int, it is a %s" % (key, str(type(result))))
        return result
