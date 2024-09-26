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

import json
import os
import pathlib
import sys
import urllib
from enum import Enum, auto
from http.client import HTTPResponse
from typing import Callable
from typing import Dict
from urllib import error
from urllib import request
from utilities.type_utils import *

LGR_CRU = logging.getLogger("cui_resources_utils")
LGR_FMT_CRU = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
LGR_CRU.setLevel(logging.INFO)


class ResourceDir(Enum):
    MODELS = auto()
    OUTPUT = auto()
    USER = auto()


class ModelType(Enum):
    CHECKPOINTS = auto(),
    CLIP = auto(),
    CLIP_VISION = auto(),
    CODEFORMER = auto(),
    CONFIGS = auto(),  # not served, apparently unsupported.
    CONTROLNET = auto(),
    CONTROLNETS = auto(),
    DEEPBOORU = auto(),
    DIFFUSERS = auto(),
    EMBEDDINGS = auto(),
    ESRGAN = auto(),
    GFPGAN = auto(),  # not served, apparently unsupported.
    GLIGEN = auto(),
    HYPERNETWORKS = auto(),
    KARLO = auto(),  # not served, apparently unsupported.
    LDSR = auto(),
    LORAS = auto(),
    PHOTOMAKER = auto()  # not present in default release.
    STABLE_DIFFUSION = auto(),
    STYLE_MODELS = auto(),
    SWINIR = auto(),
    UNET = auto(),
    UPSCALE_MODELS = auto(),
    VAE = auto(),
    VAE_APPROX = auto()

    def _predicate(self) -> Callable[[str], bool]:
        match self:
            case ModelType.CHECKPOINTS:
                return seems_checkpoint
            case ModelType.CLIP:
                return seems_clip
            case ModelType.CONFIGS:
                return seems_config
            case ModelType.CONTROLNET:
                return seems_controlnet
            case ModelType.CONTROLNETS:
                return seems_controlnet
            case ModelType.DIFFUSERS:
                return seems_diffuser
            case ModelType.EMBEDDINGS:
                return seems_embedding
            case ModelType.GFPGAN:
                return seems_pytorch
            case ModelType.GLIGEN:
                return seems_gligen
            case ModelType.HYPERNETWORKS:
                return seems_hypernetwork
            case ModelType.KARLO:
                return seems_karlo
            case ModelType.LORAS:
                return seems_lora
            case ModelType.STABLE_DIFFUSION:
                return seems_checkpoint
            case ModelType.STYLE_MODELS:
                return seems_style_model
            case ModelType.UNET:
                return seems_unet
            case ModelType.UPSCALE_MODELS:
                return seems_pytorch
            case ModelType.VAE:
                return seems_vae
            case ModelType.VAE_APPROX:
                return seems_vae_approx
            case _:
                raise NotImplementedError(f"No predicate for {self}")

    def accept(self, file_path: str) -> bool:
        return self._predicate()(file_path)


def _get_models_list_placeholder() -> List[Dict[str, str]]:
    """
    This is a dummy function to avoid the network call as described in
    https://github.com/comfyanonymous/ComfyUI/pull/4295
    , where we get this data from the ComfyUI server. comfyui_models_catalog.json is the same JSON
    structure as documented in the pull request.
    :return: A list of model records
    """
    # WARNING. This yields platform-specific results.
    script_filename = os.path.realpath(__file__)
    script_dir_path = os.path.dirname(script_filename)
    asset_dir_path = os.path.join(script_dir_path, "../assets")
    models_json_path = os.path.join(asset_dir_path, "comfyui_models_catalog.json")
    try:
        with open(models_json_path, 'r') as models_json_file:
            models_list: List[Dict[str, str]] = json.load(models_json_file)['files']
        return models_list
    except Exception as err:
        LGR_CRU.exception(err)
        raise err


def seems_legit_resource(file_path: str, extensions: List[str]) -> bool:
    # LGR_CRU.debug(f"Checking {file_path}")
    fpl = file_path.lower()
    found = False
    for ext in extensions:
        if fpl.endswith(ext.lower()):
            found = True
            break
    if not found:
        return False
    return True


# NOTE: Several of these predicates are untested, because I don't have example files to put in the directories.
def seems_checkpoint(file_path: str) -> bool:
    return seems_legit_resource(file_path=file_path, extensions=[".ckpt", ".safetensors"])


def seems_clip(file_path: str) -> bool:
    return seems_legit_resource(file_path=file_path, extensions=[".clip", ".clp"])


def seems_config(file_path: str) -> bool:
    return seems_legit_resource(file_path=file_path, extensions=[".config", ".cfg", ".yaml"])


def seems_controlnet(file_path: str) -> bool:
    return seems_legit_resource(file_path=file_path, extensions=[".crlnet", ".t2i"])


def seems_diffuser(file_path: str) -> bool:
    return seems_legit_resource(file_path=file_path, extensions=[".diff", ".diffuse"])


def seems_embedding(file_path: str) -> bool:
    return seems_legit_resource(file_path=file_path, extensions=[".embd", ])


def seems_gligen(file_path: str) -> bool:
    return seems_legit_resource(file_path=file_path, extensions=[".gligen", ])


def seems_hypernetwork(file_path: str) -> bool:
    return seems_legit_resource(file_path=file_path, extensions=[".hnet", ])


def seems_json(file_path: str) -> bool:
    return seems_legit_resource(file_path=file_path, extensions=[".json", ])


def seems_karlo(file_path: str) -> bool:
    return seems_legit_resource(file_path=file_path, extensions=[".th", ])


def seems_lora(file_path: str) -> bool:
    return seems_legit_resource(file_path=file_path, extensions=[".lora", ".safetensors"])


def seems_pytorch(file_path: str) -> bool:
    return seems_legit_resource(file_path=file_path, extensions=[".pth", ".pytorch"])


def seems_style_model(file_path: str) -> bool:
    return seems_legit_resource(file_path=file_path, extensions=[".style", ])


def seems_unet(file_path: str) -> bool:
    return seems_legit_resource(file_path=file_path, extensions=[".unet", ".safetensors"])


def seems_vae(file_path: str) -> bool:
    return seems_legit_resource(file_path=file_path, extensions=[".vae", "vae.safetensors"])


def seems_vae_approx(file_path: str) -> bool:
    return seems_legit_resource(file_path=file_path, extensions=[".pt", ])


def request_resource_catalog(cu_origin: str, resource_dir: ResourceDir, protocol: str = 'http',) -> Dict:
    server_url = f"{protocol}://{cu_origin}/internal/files?directory={resource_dir.name.lower()}"
    log_message = f"request_resource_catalog() opening {server_url}"
    LGR_CRU.debug(log_message)
    req: urllib.request.Request = urllib.request.Request(server_url)
    try:
        response: HTTPResponse
        with urllib.request.urlopen(req) as response:
            response_json_byes: bytes = response.read()
            response_obj: Dict = json.loads(response_json_byes)
            return response_obj
    except urllib.error.HTTPError as h_err:
        LGR_CRU.exception(h_err)
        message = f"url={h_err.url}, code={h_err.code}, reason={h_err.reason}"
        LGR_CRU.error(message)
        LGR_CRU.error(str(h_err.headers))
    except urllib.error.URLError as u_err:
        LGR_CRU.exception(u_err)
        message = f"url={u_err.filename}, code={u_err.errno}, reason={u_err.reason}"
        LGR_CRU.error(message)
    return {}


def get_models_map(cu_origin: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Returns a dict of the models available in the ComfyUI server. Use the key "files" to access the lists
     of model records.
    :param cu_origin: The hostname and port of the ComfyUI server. i.e. "localhost:8188"
    :return:  a dict of the models available in the ComfyUI server.
    """
    meta_models: Dict[str, List[Dict[str, str]]] = {}
    models_list: List[Dict[str, str]] = request_resource_catalog(
        cu_origin=cu_origin,
        resource_dir=ResourceDir.MODELS)['files']  # FIXME: Breaks on macOS, can't find 'files' key.
    if not models_list:
        raise SystemError("children_raw is empty")
    record: Dict[str, str]
    for record in models_list:
        if record['type'] == "directory":
            meta_models[record['name'].lower()] = list()
    for record in models_list:
        if record['type'] == "file":
            parent: str = parent_dir(record['path'])
            if parent is None:
                raise ValueError(f"Could not get parent for path \"{record['path']}\"")
            if parent:
                children: List[Dict[str, str]] = meta_models[parent.lower()]
                children.append(record)
            else:
                LGR_CRU.debug(f"No parent for path \"{record['path']}\"")
    return meta_models


def get_models_list(model_type: ModelType, cu_origin: str) -> List[Dict[str, str]]:
    """
    Retrieves the list of specified models from ComfyUI
    :param model_type: The type of model, i.e. ModelType.CHECKPOINTS
    :param cu_origin: The hostname and port of the ComfyUI server. i.e. "localhost:8188"
    :return: A list of specified models from ComfyUI
    """
    models_map: Dict[str, List[Dict[str, str]]] = get_models_map(cu_origin=cu_origin)
    key = model_type.name.lower()
    models_list: List[Dict[str, str]] = list()
    if key not in models_map:
        LGR_CRU.error(f"key \"{key}\" not found in models_map")
        LGR_CRU.error(f"{list(models_map.keys())}")
        return list({})
    m_list = models_map[key]
    if not m_list:
        LGR_CRU.error(json.dumps(models_map, indent=2, sort_keys=True))
        raise ValueError(f"no items for models map[{key}] ")
    for subject in m_list:
        name: str = subject['name']
        if not name:
            raise ValueError(f"Name missing from {json.dumps(subject, sort_keys=True, indent=2)}")
        if model_type.accept(name):
            models_list.append(subject)
        else:
            LGR_CRU.debug(f"Rejected {name}")
    return models_list


def get_models_filenames(model_type: ModelType, cu_origin: str) -> List[str]:
    """
    Retrieves the list of specified models from ComfyUI, strips the path part of each model's full path, and returns
    just the filename.
    Replaces list_from_fs(fs_path, predicate), where "fs_path" and predicate arguments are replaced with single
     model_type argument.
    :param model_type: The type of the model. i.e. ModelType.CHECKPOINTS
    :param cu_origin: The hostname and port of the ComfyUI server. i.e. "localhost:8188"
    :return: The filenames of the models of the specified type.
    """
    models_list: List[Dict[str, str]] = get_models_list(model_type=model_type, cu_origin=cu_origin)
    filenames_list: List[str]
    filenames_list = [basename(record['path']) for record in models_list]
    return filenames_list


def basename(path_on_server: str) -> str:
    """
    A crude, platform independent function to obtain the final path component, excluding the drive and root, if any,
     f a path.
    This function assumes that any argument that contains a backslash or a colon is a Windows path.
    :param path_on_server: A path to parse. For example "checkpoints\\locomotive_sdxl_01.ckpt"
    :return: The final path component for the given path.
    """
    is_windows = '\\' in path_on_server or ':' in path_on_server
    if is_windows:
        pure_path = pathlib.PureWindowsPath(path_on_server)
    else:
        pure_path = pathlib.PurePosixPath(path_on_server)
    return pure_path.name


def parent_dir(path_on_server: str) -> str:
    """
    A crude, platform independent function to obtain the parent directory of a path.
    This function assumes that any argument that contains a backslash or a colon is a Windows path.
    :param path_on_server: A path to parse. For example "checkpoints\\locomotive_sdxl_01.ckpt"
    :return: The parent directory, if any, for the given path.
    """
    is_windows = '\\' in path_on_server or ':' in path_on_server
    if is_windows:
        pure_path = pathlib.PureWindowsPath(path_on_server)
    else:
        pure_path = pathlib.PurePosixPath(path_on_server)
    return pure_path.parent.name


def main() -> int:
    models_map = get_models_map(cu_origin=sys.argv[1])
    if models_map is None:
        raise ValueError("get_models_map() returned None")
    if not models_map:
        raise ValueError(f"get_models_map() returned empty map.")
    # print(json.dumps(models_map, sort_keys=True, indent=2))
    type_list: List[ModelType] = [
        ModelType.CHECKPOINTS,
        ModelType.CONFIGS,
        # ModelType.GFPGAN,
        # ModelType.KARLO,
        ModelType.LORAS,
        ModelType.UNET,
        ModelType.UPSCALE_MODELS,
        ModelType.VAE,
        ModelType.VAE_APPROX
    ]
    for model_type in type_list:
        records = get_models_list(model_type, cu_origin=sys.argv[1])
        if records is None:
            raise ValueError(f"models for {model_type} is None")
        if not records:
            raise ValueError(f"models for {model_type} is empty, check the type's predicate"
                             f" (and predicate's extensions)")
        filenames = get_models_filenames(model_type, cu_origin=sys.argv[1])
        print(filenames)
    return 0


def main0() -> int:
    cu_origin: str = sys.argv[1]
    if not cu_origin:
        raise ValueError("Missing cu_origin argument")
    models_map = request_resource_catalog(cu_origin=cu_origin, resource_dir=ResourceDir.MODELS)
    print(json.dumps(models_map, sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
