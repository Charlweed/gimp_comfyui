#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2024 Charles Hymes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import argparse
import importlib.util
import json
import logging
import os
import os.path
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from enum import Enum, auto
from os.path import expanduser
from pathlib import Path
from typing import Dict, List, Set


class Fault(Enum):
    CANCELLED = auto()
    IO_ERROR = auto()
    MISSING_MODULE = auto()
    MISSING_RESOURCE = auto()
    USER_ERROR = auto()
    FAULTLESS = auto()


class UserValueType(Enum):
    DIRECTORY_PATH = auto()
    FILE_PATH = auto()
    INSTANT = auto()
    INVALID = auto()
    NUMBER = auto()
    STRING = auto()


logging.basicConfig(level=logging.INFO)
LOGGER_INSTALLER = logging.getLogger(__name__)

DEFAULTS: Dict[str, str]
PLATFORM: str = platform.system().lower()
PLUGIN_DIR_NAME: str = "gimp_comfyui"
LOGGER_INSTALLER.info(f"Installing as PLATFORM={PLATFORM}")

if PLATFORM == "windows":
    DEFAULTS = {
        "gimp_plugins_dir": "~/AppData/Roaming/GIMP/3.0/plug-ins",
        "gimp_plugin_data_dir": "~/AppData/Roaming/gimp_plugin_data",
        "comfyui_custom_nodes_dir": "~/ComfyUI/custom_nodes",
        "stable_diffusion_data_dir": "~/ComfyUI"
    }
else:
    if PLATFORM == "darwin":
        DEFAULTS = {
            "gimp_plugins_dir": "~/Library/Application Support/GIMP/3.0/plug-ins",
            "gimp_plugin_data_dir": "~/.config/gimp_plugin_data",
            "comfyui_custom_nodes_dir": os.environ.get('TMPDIR', expanduser("~/")),
            # Assuming no local stable_diffusion
            "stable_diffusion_data_dir": os.environ.get('TMPDIR', expanduser("~/"))
        }
    else:
        DEFAULTS = {
            "gimp_plugins_dir": "~/.var/app/org.gimp.GIMP/config/GIMP/3.0/plug-ins",
            "gimp_plugin_data_dir": "~/.config/gimp_plugin_data",
            "comfyui_custom_nodes_dir": "~/ComfyUI/custom_nodes",
            "stable_diffusion_data_dir": "~/ComfyUI"
        }
gsdd = os.path.abspath(expanduser(DEFAULTS["gimp_plugin_data_dir"]))
CMFUI_CONFIG_JSON_PATH = os.path.join(gsdd, "comfyui_config.json")
CMFUI_CONFIG_TEMPLATE = {
    "sd_checkpoints_dir": "DIR_TOKEN_00/models/checkpoints",
    "sd_clip_dir": "DIR_TOKEN_00/models/clip",
    "sd_clip_vision_dir": "DIR_TOKEN_00/models/clip_vision",
    "sd_configs_dir": "DIR_TOKEN_00/models/configs",
    "sd_controlnet_dir": "DIR_TOKEN_00/models/controlnets",
    "sd_data_root": "DIR_TOKEN_00",
    "sd_diffusers_dir": "DIR_TOKEN_00/models/diffusers",
    "sd_embeddings_dir": "DIR_TOKEN_00/models/embeddings",
    "sd_gligen_dir": "DIR_TOKEN_00/models/gligen",
    "sd_hypernetworks_dir": "DIR_TOKEN_00/models/hypernetworks",
    "sd_loras_dir": "DIR_TOKEN_00/models/loras",
    "sd_models_dir": "DIR_TOKEN_00/models",
    "sd_prompts_dir": "DIR_TOKEN_00/prompts",
    "sd_style_models_dir": "DIR_TOKEN_00/models/style_models",
    "sd_unet_dir": "DIR_TOKEN_00/models/unet",
    "sd_upscale_models_dir": "DIR_TOKEN_00/models/upscale_models",
    "sd_vae_dir": "DIR_TOKEN_00/models/vae",
    "sd_workflows_dir": "DIR_TOKEN_00/workflows"
}

SUBJECT_MODULES: list = ["tk"]
TEMP_DEFAULT_DIR = tempfile.gettempdir()
TRANSCEIVER_NODE_NAME = "image_transceiver"
TRANSCEIVER_NODE_PROJ_NAME: str = "comfy_image_transceiver_controller"

SUB_PROJ: Dict[str, str] = {
    TRANSCEIVER_NODE_PROJ_NAME: "https://github.com/Charlweed/image_transceiver.git"
}


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.stderr.flush()
    sys.stdout.flush()


def on_rm_error(func, path, exc_info):  # noqa
    # path contains the path of the file that couldn't be removed
    # let's just assume that it's read-only and unlink it.
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)


def _remove_git_parts(subject_dir):
    subject_abs = os.path.abspath(subject_dir)
    git_parts: List[str] = [".git", ".gitignore", ".gitmodules"]
    for part in git_parts:
        doomed = f"{subject_abs}/{part}"
        _remove_drek(doomed=doomed)


def _remove_duh(doomed) -> bool:
    """
    This fails if there's a read-only file, and git repos always have read-only files. There is no fix on Windows.
    :param doomed: The file or directory to delete.
    :return: True if deletion was successful.
    """
    doomed_abs = os.path.abspath(doomed)
    if os.path.exists(doomed_abs):
        try:
            if os.path.isdir(doomed_abs):
                LOGGER_INSTALLER.debug(f"rm -force -recurse \"{doomed_abs}\"")
                # This fails if there's a read-only file, and git repos always have read-only files.
                # There is no fix on Windows
                shutil.rmtree(doomed_abs, ignore_errors=False, onerror=on_rm_error)
            else:
                LOGGER_INSTALLER.debug(f"rm -force \"{doomed_abs}\"")
                os.remove(doomed_abs)
        except IOError as io_err:
            eprint(io_err)
            return False
        time.sleep(1)  # There's sometimes a lag were deleted objects are still found, but there's also a bug
        # where the deletion failed, but exists returns false anyway.
        if os.path.exists(doomed_abs):
            eprint(f"Failed to delete {doomed_abs}")
            return False
    else:
        # LOGGER_INSTALLER.debug(f"\"{doomed_abs}\" not found.")
        return False
    return True


def _remove_drek(doomed):
    """
    There's a whole tree of reasons why deleting something can fail. Python on Windows cannot deal with several of
    these. For example, restrictive attributes, and insufficient privileges. Here, we only expect the known
    un-handleable of read-only files. This case can be dealt with by using the platform's "built-in" commands.
    :param doomed:
    :return:
    """
    doomed_abs = os.path.abspath(doomed)
    if os.path.exists(doomed_abs):
        is_dir: bool = os.path.isdir(doomed_abs)
        try:
            if platform.system().lower() == "windows":
                # LOGGER_INSTALLER.debug(f"del /s /q \"{doomed_abs}\"")
                subprocess.check_call(["del", "/s", "/q", doomed_abs],
                                      shell=True,
                                      stdout=subprocess.DEVNULL,
                                      stderr=None)
                if is_dir:
                    # LOGGER_INSTALLER.debug(f"rmdir /s /q \"{doomed_abs}\"")
                    subprocess.check_call(["rmdir", "/s", "/q", doomed_abs],
                                          shell=True,
                                          stdout=subprocess.DEVNULL,
                                          stderr=None)
            else:  # Not Windows...
                LOGGER_INSTALLER.debug(f"rm -f -r \"{doomed_abs}\"")
                subprocess.check_call(["/bin/rm", "-f", "-r", doomed_abs],
                                      shell=False,
                                      stdout=None,
                                      stderr=None)
        except IOError as io_err:
            eprint(io_err)
            return
        time.sleep(1)  # There's sometimes a lag were deleted objects are still found, but there's also a bug
        # where the deletion failed, but exists() returns false anyway.
        if os.path.exists(doomed_abs):
            raise IOError(f"Failed to delete {doomed_abs}")


def _download_partners():
    this_repo_dir = os.path.dirname(os.path.abspath(__file__))
    for proj_name, git_url in SUB_PROJ.items():
        subordinate_dir = f"{this_repo_dir}/{proj_name}"
        _remove_drek(subordinate_dir)
        if os.path.exists(subordinate_dir):
            raise IOError(f"Failed to delete {subordinate_dir}")
        LOGGER_INSTALLER.info(f"git clone {git_url} \"{subordinate_dir}\"")
        subprocess.check_call(["git", "clone", git_url, subordinate_dir])


def _dirs_from_user(parameters: Dict[str, UserValueType], use_cli: bool) -> Dict[str, str] | Fault:
    # NOTE: Some environments, for example GIMP plugins, crash when functions attempt imports.
    if not use_cli:
        from tkinter import Tk, filedialog
        root = Tk()
        root.withdraw()  # Hides root window.
    answers: Dict[str, str] = {}
    main_fault: Fault = Fault.FAULTLESS
    parameter: str
    unselected: bool
    found_dir: bool
    for parameter in parameters.keys():
        unselected = True
        answer = "//::INVALID::\\\\"
        while unselected:
            default = expanduser(DEFAULTS[parameter])
            if use_cli:
                answer = input(f"Please provide an existing directory path for {parameter}  >").strip()
            else:
                if not os.path.isdir(default):
                    eprint(f"Did not find DEFAULT directory for {parameter}: \"{default}\"")
                    default = Path.home()
                # I suspect root.directory is magic, and needs to be tickled. So keep assigning to it.
                root.directory = filedialog.askdirectory(initialdir=default, title=f"Please Select {parameter}")  # noqa
                answer = root.directory
            found_dir = os.path.isdir(answer)
            if found_dir or (not answer):
                unselected = False
        if not answer:
            main_fault: Fault = Fault.CANCELLED
            break
        answers[parameter] = answer.strip()
    if main_fault != Fault.FAULTLESS:
        return main_fault
    return answers


def _obtain_user_arguments(parameters: Dict[str, UserValueType]) -> Dict[str, str] | Fault:
    """
    If possible, open dialogs so the user can provide input. Otherwise, return a fault reason.
    :return: (Dict | List) a dict of values obtained from the user, or a Fault reason.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    missing_required_module = False

    for subject_module in SUBJECT_MODULES:
        spam_spec = importlib.util.find_spec(subject_module)
        found = spam_spec is not None
        if not found:
            missing_required_module = True
            eprint(f"Missing module \"{subject_module}\"")
    if missing_required_module:
        eprint(f"Some gui modules are not installed. You can try to install them and re-run this installer.")
        eprint("Otherwise, you will need to run this installer exclusively from the the cli and specify "
               f"{parameters}.\n")
        eprint(f"NOTE: Apparently, TK GUI modules cannot be installed in the python bundled with GIMP 3.0.")
        sys.stdout.flush()
        sys.stderr.flush()
        main_fault = Fault.MISSING_MODULE
        answer = input(f"Continue with CLI?  >")
        if answer.lower() in ["y", "yes", "continue", "ok"]:
            return _dirs_from_user(parameters=parameters, use_cli=True)
        else:
            return main_fault
    else:
        return _dirs_from_user(parameters=parameters, use_cli=False)


def remove_modules():
    for subject_module in SUBJECT_MODULES:
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", subject_module])


def _from_here_to_there(sources: Set[str], dest_dir: str, sub_dir: str | None = None) -> bool:
    all_good: bool = False
    src_path: str = ""
    if not __file__:
        raise IOError("Cannot determine path to \"this\" script.")
    this_repo_dir = os.path.dirname(os.path.abspath(__file__))
    if sub_dir:
        this_repo_dir = f"{this_repo_dir}/{sub_dir}"  # os.path.join scrambles the separators. Whatever.
        if not os.path.isdir(this_repo_dir):
            raise IOError(f"Could not find sub-directory \"{this_repo_dir}\"")
    for src_leaf in sources:
        try:
            src_path = os.path.abspath(os.path.join(this_repo_dir, src_leaf))
            if not os.path.exists(src_path):
                if src_path.endswith("locale"):  # locale is optional.
                    continue
                raise IOError(f"Could not find source \"{src_path}\"")
            leaf = os.path.basename(src_path)
            new_dest = os.path.abspath(f"{dest_dir}/{leaf}")
            if os.path.isdir(src_path):
                if os.path.exists(new_dest):
                    _remove_drek(new_dest)
                shutil.copytree(src_path, new_dest)
            else:
                if os.path.exists(new_dest):
                    _remove_drek(new_dest)
                if not os.path.exists(dest_dir):
                    os.mkdir(dest_dir)
                # print(f"shutil.copy({src_path}, {dest_dir})")
                shutil.copy(src_path, dest_dir)
            LOGGER_INSTALLER.debug(f"Copied \"{src_path}\" to \"{dest_dir}\"")
        except IOError as io_err:
            eprint(f"Error at src_leaf={src_leaf}; src_path={src_path}; dest_dir={dest_dir}")
            eprint(f"{io_err}")
            all_good = False
    return all_good


def copy_gimp_plugin_sources(gimp_plugin_dir: str) -> bool:
    LOGGER_INSTALLER.info(f"Installing GIMP plug-in {gimp_plugin_dir}")
    all_good: bool
    sources: Set[str] = {
        "LICENSE",
        "README.md",
        "assets",
        "gimp3_concurrency",
        "gimp_comfyui.py",
        "locale",
        "requests",
        "requests_toolbelt",
        "utilities",
        "websocket",
        "workflow"
    }
    all_good = _from_here_to_there(sources=sources, dest_dir=gimp_plugin_dir)
    return all_good


def copy_comfyui_node_sources(comfyui_custom_nodes_dir: str) -> bool:
    LOGGER_INSTALLER.info(f"Installing ComfyUI custom node {comfyui_custom_nodes_dir}")
    all_good: bool
    sources: Set[str] = {
        "js",
        "utilities",
        "__init__.py",
        "image_transceiver.py"
    }
    tn_dir: str = os.path.join(comfyui_custom_nodes_dir, TRANSCEIVER_NODE_NAME)
    all_good = _from_here_to_there(sources=sources, dest_dir=tn_dir, sub_dir=TRANSCEIVER_NODE_PROJ_NAME)
    return all_good


def start_install(gimp_plugins_dir: str, comfyui_custom_nodes_dir: str, stable_diffusion_data_dir: str):
    LOGGER_INSTALLER.info(f"Installing ... gimp_plugins_dir=\"{gimp_plugins_dir}\","
                          f" comfyui_custom_nodes_dir=\"{comfyui_custom_nodes_dir}\""
                          f" stable_diffusion_data_dir=\"{stable_diffusion_data_dir}\""
                          )
    if not __file__:
        raise IOError("Cannot determine path to \"this\" script.")
    write_json_files(stable_diffusion_data_dir=stable_diffusion_data_dir)
    gimp_plugin_dir = os.path.join(gimp_plugins_dir, PLUGIN_DIR_NAME)
    if not os.path.exists(gimp_plugin_dir):
        os.mkdir(gimp_plugin_dir)
    if not os.path.isdir(gimp_plugin_dir):
        raise IOError(f"Existing file \"{gimp_plugin_dir}\" is not a directory.")
    copy_gimp_plugin_sources(gimp_plugin_dir=gimp_plugin_dir)
    _download_partners()
    copy_comfyui_node_sources(comfyui_custom_nodes_dir=comfyui_custom_nodes_dir)


def write_json_files(stable_diffusion_data_dir: str):
    if not os.path.exists(stable_diffusion_data_dir):
        raise IOError(f"Could not find source \"{stable_diffusion_data_dir}\"")
    if not os.path.isdir(stable_diffusion_data_dir):
        raise IOError(f"\"{stable_diffusion_data_dir}\" is not a directory.")
    models_dir: str = os.path.join(stable_diffusion_data_dir, "models")
    if not os.path.exists(models_dir):
        raise IOError(f"Could not find models dir in \"{stable_diffusion_data_dir}\"")
    if not os.path.isdir(models_dir):
        raise IOError(f"item \"models\" in \"{stable_diffusion_data_dir}\" is not a directory.")
    if not __file__:
        raise IOError("Cannot determine path to \"this\" script.")
    this_repo_dir: str = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(this_repo_dir):
        raise IOError(f"Could not find this repository directory.")
    assets_dir: str = os.path.join(this_repo_dir, "assets")
    if not os.path.exists(assets_dir):
        raise IOError(f"Could not find assets directory in this repository.")
    out_dict: dict[str, str] = {}
    for key, value in CMFUI_CONFIG_TEMPLATE.items():
        out_dict[key] = os.path.abspath(value.replace("DIR_TOKEN_00", f"{stable_diffusion_data_dir}/"))
    try:
        LOGGER_INSTALLER.info(f"Writing ComfyUI config to {CMFUI_CONFIG_JSON_PATH}")
        if not os.path.exists(gsdd):
            os.mkdir(gsdd)
        if not os.path.exists(gsdd):
            raise IOError(f"Could not find or create {gsdd}")
        with open(CMFUI_CONFIG_JSON_PATH, "w") as comfyui_config_json_file:
            sorted_keys = sorted(out_dict.keys())
            json.dump({i: out_dict[i] for i in sorted_keys}, comfyui_config_json_file, indent=2)
    except IOError as thrown:
        LOGGER_INSTALLER.error(f"Problem writing {CMFUI_CONFIG_JSON_PATH}")
        raise thrown


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gimp_plugins_dir", nargs='?')
    parser.add_argument("--comfyui_custom_nodes_dir", nargs='?')
    parser.add_argument("--stable_diffusion_data_dir", nargs='?')
    args_p = parser.parse_args()
    if not args_p.gimp_plugins_dir:
        LOGGER_INSTALLER.debug("gimp_plugins_dir not specified.")
    if not args_p.comfyui_custom_nodes_dir:
        LOGGER_INSTALLER.debug("comfyui_custom_nodes_dir not specified.")
    if not args_p.stable_diffusion_data_dir:
        LOGGER_INSTALLER.debug("stable_diffusion_data_dir not specified.")
    sys.stdout.flush()
    sys.stderr.flush()
    if args_p.comfyui_custom_nodes_dir and args_p.gimp_plugins_dir and args_p.stable_diffusion_data_dir:
        start_install(gimp_plugins_dir=args_p.gimp_plugins_dir,
                      comfyui_custom_nodes_dir=args_p.comfyui_custom_nodes_dir,
                      stable_diffusion_data_dir=args_p.stable_diffusion_data_dir
                      )
    else:
        user_args: Dict[str: str] | Fault = _obtain_user_arguments({
            "gimp_plugins_dir": UserValueType.DIRECTORY_PATH,
            "comfyui_custom_nodes_dir": UserValueType.DIRECTORY_PATH,
            "stable_diffusion_data_dir": UserValueType.DIRECTORY_PATH
        })
        if isinstance(user_args, Fault):
            fault_name: str = user_args.name
            eprint(f"Stopping because {fault_name}")
            sys.exit(10)
        start_install(gimp_plugins_dir=user_args["gimp_plugins_dir"],
                      comfyui_custom_nodes_dir=user_args["comfyui_custom_nodes_dir"],
                      stable_diffusion_data_dir=user_args["stable_diffusion_data_dir"]
                      )


if __name__ == '__main__':
    main()

# This might save typing while developing. Try:
# Windows:
# mkdir $ENV:TMP\gimp_plugins
# mkdir $ENV:TMP\stable_diffusion\models
# mkdir $ENV:TMP\stable_diffusion\custom_nodes
# $ENV:GCUI_REPO=$(Get-Location)
# python $ENV:GCUI_REPO\installer.py --gimp_plugins_dir $ENV:TMP/gimp_plugins --stable_diffusion_data_dir $ENV:TMP/stable_diffusion --comfyui_custom_nodes_dir $ENV:TMP/stable_diffusion/custom_nodes
# and
# python $ENV:GCUI_REPO\installer.py --gimp_plugins_dir $ENV:TMP/gimp_plugins --stable_diffusion_data_dir L:/projects/3rd_party/ComfyUI --comfyui_custom_nodes_dir L:/projects/3rd_party/ComfyUI/custom_nodes
##
##
# MacOS:
# mkdir -p $TMPDIR/gimp_plugins
# mkdir -p $TMPDIR/stable_diffusion/models
# mkdir -p $TMPDIR/stable_diffusion/custom_nodes
# export GCUI_REPO=$(pwd)
# /Applications/GIMP.app/Contents/MacOS/python3.10 $GCUI_REPO/installer.py --gimp_plugins_dir $TMPDIR/gimp_plugins --stable_diffusion_data_dir $TMPDIR/stable_diffusion --comfyui_custom_nodes_dir $TMPDIR/stable_diffusion/custom_nodes
