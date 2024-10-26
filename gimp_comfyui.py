#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# The two lines above, the shebang and the encoding hint, are required!
# Otherwise, GIMP for MacOS will fail to load this plugin. Inexplicable, hard to believe, but issue verified
# on GIMP 2.99.18 for MacOS, Python 3.10.13 for MacOS, MacOS Monterey 12.7.6
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

"""
Registers the plug-in "GimpComfyUI" as a thin API client for ComfyUI API.

GIMP plug-ins must have a python file with the exact same name as their parent directory. That is the "main" file of
the plug-in.

 See ... gimp/devel-docs/GIMP3-plug-in-porting-guide/removed_functions.md etcetera.

 REMEMBER: This entire script is run each time the menu option is selected. That's why we don't need to restart
 GIMP when you change the contents of the plug-in file. It also means we cannot store state in any class, instance,
 or global.
"""

# gi is the python module for PyGObject. It is a Python package which provides bindings for GObject based libraries such
# as GTK, GStreamer, WebKitGTK, GLib, GIO and many more. See https://gnome.pages.gitlab.gnome.org/pygobject/
import gi
import gettext
import logging.config
import os.path
import site

gi.require_version('Gimp', '3.0')  # noqa: E402
gi.require_version('GimpUi', '3.0')  # noqa: E402
gi.require_version("Gtk", "3.0")  # noqa: E402
gi.require_version('Gdk', '3.0')  # noqa: E402
gi.require_version("GObject", "2.0")  # noqa: E402
gi.require_version("Gegl", "0.4")  # noqa: E402
from gi.repository import GLib, GObject, Gdk, GdkPixbuf, Gegl, Gimp, GimpUi, Gio, Gtk  # noqa
from gimp3_concurrency.drawable_change_notifier import *
from utilities.babl_gegl_utils import *
from utilities.cui_net_utils import *
from utilities.demos_and_tests import display_images_n_layers_dialog
from utilities.heterogeneous import png_base64_str, remove_hetero_temp_files
from utilities.persistence_utils import *
from utilities.persister_petite import *
from utilities.samples import *
from utilities.sd_gui_utils import *
from workflow.comfyui_default_accessor import ComfyuiDefaultAccessor
from workflow.comfyui_default_dialogs import ComfyuiDefaultDialogs
from workflow.flux_1dot0_accessor import Flux1Dot0Accessor
from workflow.flux_1dot0_dialogs import Flux1Dot0Dialogs
from workflow.flux_neg_1dot1_accessor import FluxNeg1Dot1Accessor
from workflow.flux_neg_1dot1_dialogs import FluxNeg1Dot1Dialogs
from workflow.img2img_sdxl_0dot3_accessor import Img2ImgSdxl0Dot3Accessor
from workflow.img2img_sdxl_0dot3_dialogs import Img2ImgSdxl0Dot3Dialogs
from workflow.inpainting_sdxl_0dot4_accessor import InpaintingSdxl0Dot4Accessor
from workflow.inpainting_sdxl_0dot4_dialogs import InpaintingSdxl0Dot4Dialogs
from workflow.sytan_sdxl_1dot0_accessor import SytanSdxl1Dot0Accessor
from workflow.sytan_sdxl_1dot0_dialogs import SytanSdxl1Dot0Dialogs
from workflow.workflow_dialog_factory import WorkflowDialogFactory
from workflow.flux_neg_upscale_sdxl_0dot4_accessor import FluxNegUpscaleSdxl0Dot4Accessor
from workflow.flux_neg_upscale_sdxl_0dot4_dialogs import FluxNegUpscaleSdxl0Dot4Dialogs
# Insert WORKFLOW_IMPORTS→


# Set-up localization for your plug-in with your own text domain.
# This is complementary to the gimp_plug_in_set_translation_domain()
# which is only useful for the menu entries inside GIMP interface,
# whereas the below calls are used for localization within the plug-in.
textdomain = 'gimp30-std-plug-ins'
gettext.bindtextdomain(textdomain, Gimp.locale_directory())
LOGGER_GCUI = logging.getLogger("GimpComfyUI")
LOGGER_FORMAT_GCUI_DEFAULT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"

PLUGIN_NAME_COMFYUI: str = "GimpComfyUI"  # "Global" scope, so insure identifier is unique.
PLUGIN_UUID_COMFYUI_STR: str = "018e86cc-4d3e-70fd-84b1-63f990e90dae"  # "Global", so insure identifier is unique.
ASSET_DIR_NAME = "assets"

MAX_MEMORY_USAGE = 1_073_741_824  # bytes. 1gb


def images_from_pixbufs(pixbufs: List[GdkPixbuf.Pixbuf]) -> List[Gimp.Image]:
    """
    Creates a new untitled image from layers created with the pixbufs. Image size is set from each pixbuf.
    Remember to show a new display and invoke Gimp.displays_flush()
    :param pixbufs: A List[GdkPixbuf.Pixbuf]
    :return: A List[Gimp.Image]
    """
    fresh_images: List[Gimp.Image] = []
    fresh_image: Gimp.Image
    fresh_layer: Gimp.Layer
    fresh_layers: List[Gimp.Layer]
    layer_index: int = 0
    image_type: Gimp.ImageBaseType = Gimp.ImageBaseType.RGB
    for pixbuf in pixbufs:
        width = pixbuf.get_width()
        height = pixbuf.get_height()
        fresh_image = Gimp.Image.new(width=width, height=height, type=image_type)
        layer_name = "layer_%000d" % layer_index
        # parameter names are refused at invocation
        fresh_layer = Gimp.Layer.new_from_pixbuf(
            fresh_image,  # image: Gimp.Image
            layer_name,  # name: str
            pixbuf,  # pixbuf: GdkPixbuf.Pixbuf
            100,  # opacity: double
            Gimp.LayerMode.NORMAL,  # mode Gimp.LayerMode
            0,  # progress_start: double
            100  # progress_end: double
        )
        insertion_success = fresh_image.insert_layer(layer=fresh_layer, parent=None, position=layer_index)
        if not insertion_success:
            LOGGER_GCUI.error("Failure inserting %s into new image." % layer_name)
        fresh_images.append(fresh_image)
    return fresh_images


class ProcedureCategory(Enum):
    CONFIG = auto()
    LIVE_CONNECTION = auto()
    TEST_ANY = auto()
    TEST_IMAGE = auto()
    TEST_LAYER = auto()
    WORKFLOW = auto()


class ControllerCommand(Enum):
    """
    Commands for the Transceiver_Controller. Often, will be forwarded to ComfyUI.
    Ideally, this would be in a single module used by both GIMP and ComfyUI.
    """
    # Usage: Brackets for name, parentheses for value
    ATTENTION = "command"
    CONFIG = "config"
    ENQUEUE_PROMPT = "enqueue_prompt"
    ABORT_WORKFLOW = "abort_workflow"


class PayloadType(Enum):
    PICT_CHA = "pict_cha"
    COMFYUI_CMD = "comfyui_command"


class GimpComfyUI(Gimp.PlugIn):
    # With GIMP 2.99, site-packages is <GIMP_INSTALL_DIR>/lib/python<PYTHON_VERSION>/site-packages
    # For example, L:/bin/GIMP 2.99/lib/python3.11/site-packages

    # Wannabe Constants
    PYTHON_PLUGIN_NAME: str = "GimpComfyUI"
    PYTHON_PLUGIN_UUID_STRING: str = "018e86cc-4d3e-70fd-84b1-63f990e90dae"
    PYTHON_PLUGIN_NAME_LONG: str = PYTHON_PLUGIN_NAME + "_" + PYTHON_PLUGIN_UUID_STRING
    PLUGIN_MENU_LABEL: str = "_GimpComfyUI"  # Mnemonics work here.
    CONFIG_FALLBACK_NAME = f"{PYTHON_PLUGIN_NAME.lower()}_plugin_defaults.json"
    HOME: str = os.path.expanduser('~')
    MESSAGE_REGISTRATION = "Registering " + __file__ + ":" + PYTHON_PLUGIN_NAME
    MESSAGE_REGISTRATION_COMPLETED = __file__ + ":" + PYTHON_PLUGIN_NAME + " returned."
    VERSION: str = "0.7.8.1"

    # Procedure names.
    PROCEDURE_CONFIG_COMFY_SVR_CONNECTION = PYTHON_PLUGIN_NAME + "-comfyUi-Server-URL"
    PROCEDURE_CONFIG_TRANSCEIVER_CONNECTION = PYTHON_PLUGIN_NAME + "-transceiver-URL"
    PROCEDURE_DEMO_CUI_NET = "demo-cui-net"
    PROCEDURE_DEMO_IMG_N_LAYERS_TREEVIEWS = "demo-img-n-layers-treeview"
    PROCEDURE_INSTALL_COMFYUI = PYTHON_PLUGIN_NAME + "-install-comfyUI"
    PROCEDURE_INVOKE_DEFAULT_WF = "default"
    PROCEDURE_INVOKE_FLUX_NEG_WF = "flux-dev-neg"
    PROCEDURE_INVOKE_FLUX_WF = "flux-dev"
    PROCEDURE_INVOKE_IMG2IMG_WF = "img2img-sdxl"
    PROCEDURE_INVOKE_INPAINTING_WF = "inpainting-sdxl"
    PROCEDURE_INVOKE_SYTAN_WF = "sytan"
    PROCEDURE_WATCH_LAYER = "Follow-in-ComfyUI"
    PROCEDURE_INVOKE_FLUX_NEG_UPSCALE_SDXL_0DOT4_WF = "flux_neg_upscale_sdxl_0dot4"
    # Insert PROCEDURE_NAME_VARS→
    PROCEDURE_NAMES = [
        PROCEDURE_CONFIG_COMFY_SVR_CONNECTION,
        PROCEDURE_CONFIG_TRANSCEIVER_CONNECTION,
        PROCEDURE_WATCH_LAYER,
        PROCEDURE_INVOKE_DEFAULT_WF,
        PROCEDURE_INVOKE_FLUX_NEG_WF,
        PROCEDURE_INVOKE_FLUX_WF,
        PROCEDURE_INVOKE_IMG2IMG_WF,
        PROCEDURE_INVOKE_INPAINTING_WF,
        PROCEDURE_INVOKE_SYTAN_WF,
        PROCEDURE_INVOKE_FLUX_NEG_UPSCALE_SDXL_0DOT4_WF,
        # Insert PROCEDURE_NAME_ITEMS→
    ]

    # Configurable
    COMFYUI_HOST: str = "UNINITIALIZED"
    COMFYUI_PATH: str = ""
    COMFYUI_PORT: int = 8188
    COMFYUI_PROTOCOL: str = "http"
    COMFYUI_ORIGIN: str = f"{COMFYUI_HOST}:{COMFYUI_PORT}"
    COMFYUI_URL: str = f"http://{COMFYUI_ORIGIN}"  # Aka server address, server URL etc.
    TRANSCEIVER_HOST: str = "UNINITIALIZED"
    TRANSCEIVER_PATH: str = ""
    TRANSCEIVER_PORT: int = 8765
    TRANSCEIVER_PROTOCOL: str = "ws"
    LIMB_IMAGE_MENU_NAME: str = "<Image>/GimpComfyUI"
    LIMB_LAYERS_MENU_NAME: str = "<Layers>/GimpComfyUI"
    LOGGER_FORMAT_GCUI = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"

    # Class variables
    _script_filename = os.path.realpath(__file__)
    _script_dir_path = os.path.dirname(_script_filename)
    _asset_dir_path = os.path.join(_script_dir_path, ASSET_DIR_NAME)
    # Fallback data is only used if Persisted data is missing.
    _fallback_path = os.path.join(_asset_dir_path, CONFIG_FALLBACK_NAME)
    GCUI_PERSISTER: PersisterPetite = PersisterPetite(chassis="SABOT",  # No real chassis, we use a dummy plug.
                                                      chassis_name=PYTHON_PLUGIN_NAME,
                                                      fallback_path=_fallback_path)
    GCUI_PERSISTER.store_defaults_if_missing(defaults={
        "COMFYUI_HOST": COMFYUI_HOST,
        "COMFYUI_PATH": COMFYUI_PATH,
        "COMFYUI_PORT": COMFYUI_PORT,
        "COMFYUI_PROTOCOL": COMFYUI_PROTOCOL,
        "DEBUG": False,
        "LIMB_IMAGE_MENU_NAME": LIMB_IMAGE_MENU_NAME,
        "LIMB_LAYERS_MENU_NAME": LIMB_LAYERS_MENU_NAME,
        "LOGGER_FORMAT_GCUI": LOGGER_FORMAT_GCUI,
        "TRANSCEIVER_HOST": TRANSCEIVER_HOST,
        "TRANSCEIVER_PATH": TRANSCEIVER_PATH,
        "TRANSCEIVER_PORT": TRANSCEIVER_PORT,
        "TRANSCEIVER_PROTOCOL": TRANSCEIVER_PROTOCOL
    }
    )

    @classmethod
    def configure_loggers(cls):
        log_file_path: str = os.path.join(tempfile.gettempdir(), f"GimpComfyUI_logfile.txt")
        if LOGGER_GCUI.hasHandlers():
            LOGGER_GCUI.handlers.clear()
        logging.config.dictConfig({
            'version': 1,
            'formatters': {
                'default': {
                    'format': LOGGER_FORMAT_GCUI_DEFAULT,
                },
            },
            'handlers': {
                'debug': {
                    'level': logging.DEBUG,
                    'class': 'logging.FileHandler',
                    'filename': log_file_path,
                    'formatter': 'default',
                },
            },
            "loggers": {
                    "GimpComfyUI": {
                        "level": logging.DEBUG,
                        "handlers": ["debug"],
                        "propagate": False
                    },
                    "PersisterPetite": {
                        "level": logging.INFO,
                        "handlers": ["debug"],
                        "propagate": False
                    },
                    "heterogeneousutils": {
                        "level": logging.INFO,
                        "handlers": ["debug"],
                        "propagate": False
                    },
                    "cui_net_utils": {
                        "level": logging.INFO,
                        "handlers": ["debug"],
                        "propagate": False
                    },
                    "sd_gui_utils": {
                        "level": logging.INFO,
                        "handlers": ["debug"],
                        "propagate": False
                    },
                    "URLError": {
                        "level": logging.DEBUG,
                        "handlers": ["debug"],
                        "propagate": False
                    },
            },
            "root": {
                "level": logging.INFO
            }
        })

    @classmethod
    def get_str(cls, key: str) -> str:
        result: str = get(plugin_name_long=cls.PYTHON_PLUGIN_NAME_LONG,
                          key=key,
                          default="",
                          longevity=Longevity.TEMPORARY,
                          )
        return result

    @classmethod
    def put_str(cls, key: str, value):
        # LOGGER_GCUI.debug("put_str(%s);%s" % (key, str(value)))
        put(plugin_name_long=cls.PYTHON_PLUGIN_NAME_LONG, key=key, value=value, longevity=Longevity.TEMPORARY)

    @classmethod
    def set_initialized(cls):
        cls.put_str(key="INITIALIZED", value=str(True))

    @classmethod
    def is_initialized(cls):
        return bool_safe_of(cls.get_str(key="INITIALIZED"))

    @classmethod
    def is_debugging(cls):  # Same as property, but class properties are not supported
        return bool_safe_of(GimpComfyUI.get_str(key="DEBUGGING"))

    @classmethod
    def update_config(cls, data: dict[str, str | int]):
        cls.GCUI_PERSISTER.update_config(data=data)
        cls.GCUI_PERSISTER.store_config()

    @classmethod
    def _set_debugging(cls, do_debugging: bool):  # Same as property, but different scope
        # LOGGER_GCUI.debug("_set_debugging(%s)" % str(do_debugging))
        GimpComfyUI.put_str(key="DEBUGGING", value=str(do_debugging))

    @classmethod
    def __init_plugin(cls):
        """
        A GIMP plugin is NOT AN APPLICATION.
        This class method is called by do_query_procedures(), and then all state is lost.
        To use the persisted state, it needs to be called whenever a procedure's function is invoked.
        :return:
        """
        LOGGER_GCUI.debug(f"__init_plugin")
        if cls.is_initialized():
            raise SystemError("Class has already been initialized.")
        cls.set_initialized()
        cls.__init_debugging(debug=True)
        LOGGER_GCUI.info(sys.version)
        LOGGER_GCUI.info("GimpComfyUI version %s" % GimpComfyUI.VERSION)
        LOGGER_GCUI.info("GIMP Python3 site-packages paths are:")
        LOGGER_GCUI.info("\n".join(site.getsitepackages()))
        LOGGER_GCUI.info("GIMP Python3 sys.path is:")
        LOGGER_GCUI.info("\n".join(sys.path))

        config: Dict[str, bool | int | str] = dict(cls.GCUI_PERSISTER.configuration)
        try:
            cls.COMFYUI_HOST = config["COMFYUI_HOST"]
            cls.COMFYUI_PATH = config["COMFYUI_PATH"]
            cls.COMFYUI_PORT = int(config["COMFYUI_PORT"])
            cls.COMFYUI_PROTOCOL = config["COMFYUI_PROTOCOL"]
            cls._set_debugging(config["DEBUG"] == "True")
            cls.COMFYUI_ORIGIN = f"{cls.COMFYUI_HOST}:{cls.COMFYUI_PORT}"
            cls.COMFYUI_URL = url_string(
                host=cls.COMFYUI_HOST,
                path=cls.COMFYUI_PATH,
                port=cls.COMFYUI_PORT,
                protocol=cls.COMFYUI_PROTOCOL
            )
            g_msg = f"cls.COMFYUI_URL={cls.COMFYUI_URL}"
            LOGGER_GCUI.debug(g_msg)
            cls.TRANSCEIVER_HOST = config["TRANSCEIVER_HOST"]
            cls.TRANSCEIVER_PATH = config["TRANSCEIVER_PATH"]
            cls.TRANSCEIVER_PORT = int(config["TRANSCEIVER_PORT"])
            cls.TRANSCEIVER_PROTOCOL = config["TRANSCEIVER_PROTOCOL"]
            cls.TRANSCEIVER_ORIGIN = f"{cls.TRANSCEIVER_HOST}:{cls.TRANSCEIVER_PORT}"
            cls.TRANSCEIVER_URL = url_string(
                host=cls.TRANSCEIVER_HOST,
                path=cls.TRANSCEIVER_PATH,
                port=cls.TRANSCEIVER_PORT,
                protocol=cls.TRANSCEIVER_PROTOCOL
            )
            cls.LIMB_IMAGE_MENU_NAME = config["LIMB_IMAGE_MENU_NAME"]
            cls.LIMB_LAYERS_MENU_NAME = config["LIMB_LAYERS_MENU_NAME"]
            cls.LOGGER_FORMAT_GCUI = config["LOGGER_FORMAT_GCUI"]
        except KeyError as k_err:
            p = cls.GCUI_PERSISTER.storage_path
            LOGGER_GCUI.error(f"Corrupt config file {p}")
            LOGGER_GCUI.exception(k_err)

    @classmethod
    def __init_debugging(cls, debug: bool):
        # LOGGER_GCUI.debug("__init_debugging(%s)" % str(debug))
        cls._set_debugging(debug)

    @property
    def debugging(self) -> bool:
        try:
            return bool_of(GimpComfyUI.get_str(key="DEBUGGING"))
        except KeyError:
            return False

    @debugging.setter
    def debugging(self, do_debugging: bool):
        GimpComfyUI.put_str(key="DEBUGGING", value=str(do_debugging))

    @property
    def skip_comfyui(self):
        try:
            return bool_of(GimpComfyUI.get_str(key="SKIP_COMFYUI"))
        except KeyError:
            return False

    # GIMP says that defining the set_i18n() method disables internationalization, but I have not figured that out.
    # def set_i18n(self):
    #     pass

    @skip_comfyui.setter
    def skip_comfyui(self, ignore_api: bool):
        GimpComfyUI.put_str(key="SKIP_COMFYUI", value=str(ignore_api))

    @property
    def name(self) -> str:
        return self._name

    @property
    def default_acc(self) -> ComfyuiDefaultAccessor:
        return self._default_accessor

    @property
    def flux_acc(self) -> Flux1Dot0Accessor:
        return self._flux_accessor

    @property
    def flux_neg_acc(self) -> FluxNeg1Dot1Accessor:
        return self._flux_neg_accessor

    @property
    def sdxl_acc(self) -> SytanSdxl1Dot0Accessor:
        return self._sytan_sdxl_accessor

    @property
    def inpaint_accessor(self) -> InpaintingSdxl0Dot4Accessor:
        return self._inpainting_sdxl_accessor

    @property
    def img2img_accessor(self) -> Img2ImgSdxl0Dot3Accessor:
        return self._img2img_sdxl_accessor

    @property
    def flux_neg_upscale_sdxl_0dot4_accessor(self) -> FluxNegUpscaleSdxl0Dot4Accessor:
        return self._flux_neg_upscale_sdxl_0dot4_accessor
    # Insert WORKFLOW_ACCESSOR_PROPERTY→

    @property
    def is_server_running(self) -> bool:
        return self._is_server_running

    @is_server_running.setter
    def is_server_running(self, connectable: bool):
        self._is_server_running = connectable

    # noinspection PyMethodMayBeStatic
    def __new__(cls, *args, **kwargs):  # It seems like this is never invoked in GIMP ...
        # We will use 1st call to instance constructor to initialize class members
        instance_fresh = super(GimpComfyUI, cls).__new__(cls)
        return instance_fresh

    def __init__(self):  # Invoked at every use of a menu.
        # New instance is created every time an operation is selected ...
        # LOGGER_GCUI.debug("__init__()")
        self._name = GimpComfyUI.PYTHON_PLUGIN_NAME_LONG
        self._default_accessor: ComfyuiDefaultAccessor = ComfyuiDefaultAccessor()
        self._flux_accessor: Flux1Dot0Accessor = Flux1Dot0Accessor()
        self._flux_neg_accessor: FluxNeg1Dot1Accessor = FluxNeg1Dot1Accessor()
        self._img2img_sdxl_accessor: Img2ImgSdxl0Dot3Accessor = Img2ImgSdxl0Dot3Accessor()
        self._inpainting_sdxl_accessor: InpaintingSdxl0Dot4Accessor = InpaintingSdxl0Dot4Accessor()
        self._sytan_sdxl_accessor: SytanSdxl1Dot0Accessor = SytanSdxl1Dot0Accessor()
        self._flux_neg_upscale_sdxl_0dot4_accessor: FluxNegUpscaleSdxl0Dot4Accessor = FluxNegUpscaleSdxl0Dot4Accessor()
        # Insert WORKFLOW_ACCESSOR_DECLARATION→
        if os.environ.get('skip_comfyui'):
            self.skip_comfyui = True
            LOGGER_GCUI.warning("Disabling connection attempts to ComfyUI")
        self._is_server_running: bool = False
        self.auto_queue_prompt: bool = False


    def configure_comfy_connection(self, procedure, run_mode, image, n_drawables, drawables, config, run_data):  # noqa
        LOGGER_GCUI.debug(f"Configuring ComfyUI Connection")
        ret_values: Gimp.ValueArray = procedure.new_return_values(Gimp.PDBStatusType.CANCEL)
        all_config: MappingProxyType = GimpComfyUI.GCUI_PERSISTER.configuration
        comfy_svr_host: str = all_config.get("COMFYUI_HOST", "localhost")
        comfy_svr_path: str = all_config.get("COMFYUI_PATH", "")  # empty string, not "/"
        comfy_svr_port: int = all_config.get("COMFYUI_PORT", 8188)
        comfy_svr_protocol: str = all_config.get("COMFYUI_PROTOCOL", "http")
        comfy_svr_url: str = "UNSET"  # noqa

        def dict_consumer(dialog_data: dict[str, str | int]):
            nonlocal comfy_svr_host
            nonlocal comfy_svr_path
            nonlocal comfy_svr_port
            nonlocal comfy_svr_protocol
            nonlocal comfy_svr_url
            if dialog_data:
                comfy_svr_host = dialog_data.get('svr_host', 'MISSING')
                comfy_svr_path = dialog_data.get('svr_path', '')  # empty string, not "/"
                comfy_svr_port = dialog_data.get('svr_port', 'MISSING')
                comfy_svr_protocol = dialog_data.get('svr_protocol', 'MISSING')
                comfy_svr_url = dialog_data.get('svr_url', 'MISSING')
            else:
                # Should not happen?
                LOGGER_GCUI.warning("dict_consumer passed empty dict")

        dialog: GimpUi.Dialog = new_dialog_url(
            title_in="Configure ComfyUI Connection",
            blurb_in="Defaults are best most of the time...",
            dict_consumer=dict_consumer,
            defaults={
                'svr_protocol': comfy_svr_protocol,
                'svr_host': comfy_svr_host,
                'svr_path': comfy_svr_path,  # empty string, not "/"
                'svr_port': comfy_svr_port,
                'svr_url': "INVALID"
            }
        )
        response_code = dialog.run()  # Blocks until dialog is closed...
        if response_code != Gtk.ResponseType.OK:
            # Canceled
            dialog.destroy()
            return ret_values
        else:
            dialog.destroy()
        LOGGER_GCUI.debug(f"Configuring ComfyUI server hostname to {comfy_svr_host}")
        LOGGER_GCUI.debug(f"Configuring port number to {comfy_svr_port}")
        LOGGER_GCUI.debug(f"Configuring ComfyUI URL path to {comfy_svr_path}")
        GimpComfyUI.COMFYUI_PROTOCOL = comfy_svr_protocol
        GimpComfyUI.COMFYUI_HOST = comfy_svr_host
        GimpComfyUI.COMFYUI_PORT = comfy_svr_port
        GimpComfyUI.COMFYUI_PATH = comfy_svr_path
        GimpComfyUI.update_config({"COMFYUI_HOST": comfy_svr_host,
                                   "COMFYUI_PORT": comfy_svr_port,
                                   "COMFYUI_PATH": comfy_svr_path
                                   })

        ret_values = procedure.new_return_values(Gimp.PDBStatusType.SUCCESS)
        return ret_values

    def configure_transceiver_connection(self, procedure, run_mode, image, n_drawables, drawables, config, run_data):  # noqa
        LOGGER_GCUI.debug(f"Configuring Transceiver Connection")
        ret_values: Gimp.ValueArray = procedure.new_return_values(Gimp.PDBStatusType.CANCEL)
        all_config: MappingProxyType = GimpComfyUI.GCUI_PERSISTER.configuration
        transceiver_host: str = all_config.get("TRANSCEIVER_HOST", "localhost")
        transceiver_path: str = all_config.get("TRANSCEIVER_PATH", "")  # empty string, not "/"
        transceiver_port: int = all_config.get("TRANSCEIVER_PORT", "8765")
        transceiver_protocol: str = all_config.get("TRANSCEIVER_PROTOCOL", "ws")
        transceiver_url: str = "UNSET"  # noqa

        def dict_consumer(dialog_data: dict[str, str | int]):
            nonlocal transceiver_host
            nonlocal transceiver_path
            nonlocal transceiver_port
            nonlocal transceiver_protocol
            nonlocal transceiver_url
            if dialog_data:
                transceiver_host = dialog_data.get('svr_host', 'MISSING')
                transceiver_path = dialog_data.get('svr_path', '')  # empty string, not "/"
                transceiver_port = dialog_data.get('svr_port', 'MISSING')
                transceiver_protocol = dialog_data.get('svr_protocol', 'ws')
                transceiver_url = dialog_data.get('svr_url', 'MISSING')
            else:
                # Should not happen?
                LOGGER_GCUI.warning("dict_consumer passed empty dict")

        dialog: GimpUi.Dialog = new_dialog_url(
            title_in="Configure Transceiver Connection",
            blurb_in="Defaults are best most of the time...",
            dict_consumer=dict_consumer,
            defaults={
                'svr_protocol': transceiver_protocol,
                'svr_host': transceiver_host,
                'svr_path': transceiver_path,  # empty string, not "/"
                'svr_port': transceiver_port,
                'svr_url': transceiver_url
            }
        )
        response_code = dialog.run()  # Blocks until dialog is closed...
        if response_code != Gtk.ResponseType.OK:
            # Canceled
            dialog.destroy()
            return ret_values
        else:
            dialog.destroy()
        LOGGER_GCUI.debug(f"Configuring Transceiver hostname to {transceiver_host}")
        LOGGER_GCUI.debug(f"Configuring Transceiver port number to {transceiver_port}")
        LOGGER_GCUI.debug(f"Configuring Transceiver URL path to {transceiver_path}")
        GimpComfyUI.TRANSCEIVER_HOST = transceiver_host
        GimpComfyUI.TRANSCEIVER_PORT = transceiver_port
        GimpComfyUI.TRANSCEIVER_PATH = transceiver_path
        GimpComfyUI.update_config({"TRANSCEIVER_HOST": transceiver_host,
                                   "TRANSCEIVER_PORT": transceiver_port,
                                   "TRANSCEIVER_PATH": transceiver_path
                                   })
        ret_values = procedure.new_return_values(Gimp.PDBStatusType.SUCCESS)
        return ret_values

    # noinspection PyMethodMayBeStatic
    def do_query_procedures(self) -> List[str]:
        # Documentation states "query happens only once in the life of a plug-in (right after installation or update)."
        # First action is to remove temporary data from previous sessions.
        remove_temporary_dictionary(plugin_name_long=GimpComfyUI.PYTHON_PLUGIN_NAME_LONG)
        GimpComfyUI.__init_plugin()  # This invocation will NOT provide state
        # This is the list of procedure names.
        return GimpComfyUI.PROCEDURE_NAMES

    def do_create_procedure(self, name) -> Gimp.ImageProcedure:
        """
        This method must be overridden by all plug-ins and return a newly allocated GimpProcedure with the identifier
         specified by the parameter "name". Generally, procedures are the behaviour invoked by menu selections.
        NOTE: No plugin state is preserved between invocations of the function specified by the parameter "run_func_in".
        do_create_procedure() is the last action of one control-flow, and the invocation of the procedure's
        function is the start of a completely new control flow, with a freshly loaded plugin class, and a completely new
        instance of the plugin class.
        If the procedure-spawned instance needs to retrieve state, it will need to explicitly do so from within the
        function specified by the parameter "run_func_in".
        Parameters
        ----------
        :param name:
            The name of the procedure.
        :return:
            A Gimp.ImageProcedure.
        """
        procedure: Gimp.ImageProcedure = None  # noqa
        match name:
            case GimpComfyUI.PROCEDURE_INSTALL_COMFYUI:
                procedure = self.create_procedure(name_raw=name,
                                                  docs="Install GIMP-local ComfyUI",
                                                  usage_hint="Install ComfyUI into GIMP. This takes a while!",
                                                  run_func_in=self.run,
                                                  is_image_optional=True,  # Redundant with SubjectType.ANYTHING
                                                  proc_category=ProcedureCategory.CONFIG,
                                                  subject_type=SubjectType.ANYTHING)
            case GimpComfyUI.PROCEDURE_CONFIG_COMFY_SVR_CONNECTION:
                procedure = self.create_procedure(name_raw=name,
                                                  docs="ComfyUI server Connection",
                                                  usage_hint=f"Edit ComfyUI connection URL.",
                                                  run_func_in=self.configure_comfy_connection,
                                                  is_image_optional=True,  # Redundant with SubjectType.ANYTHING
                                                  proc_category=ProcedureCategory.CONFIG,
                                                  subject_type=SubjectType.ANYTHING)
            case GimpComfyUI.PROCEDURE_CONFIG_TRANSCEIVER_CONNECTION:
                procedure = self.create_procedure(name_raw=name,
                                                  docs="Transceiver Connection",
                                                  usage_hint=f"Edit Transceiver connection URL.",
                                                  run_func_in=self.configure_transceiver_connection,
                                                  is_image_optional=True,  # Redundant with SubjectType.ANYTHING
                                                  proc_category=ProcedureCategory.CONFIG,
                                                  subject_type=SubjectType.ANYTHING)
            case GimpComfyUI.PROCEDURE_WATCH_LAYER:
                procedure = self.create_procedure(name_raw=name,
                                                  docs="Send changes in layer to ComfyUI",
                                                  usage_hint="Any changes are sent every few seconds....",
                                                  run_func_in=self.publish_layer,
                                                  is_image_optional=False,  # Redundant with SubjectType.ANYTHING
                                                  proc_category=ProcedureCategory.LIVE_CONNECTION,
                                                  subject_type=SubjectType.LAYER)
            case GimpComfyUI.PROCEDURE_INVOKE_DEFAULT_WF:
                procedure = self.create_procedure(name_raw=name,
                                                  docs="ComfyUI default Workflow",
                                                  usage_hint="Keep duplicate fields synchronized.",
                                                  run_func_in=self.default_workflow,
                                                  is_image_optional=True,  # Redundant with SubjectType.ANYTHING
                                                  proc_category=ProcedureCategory.WORKFLOW,
                                                  subject_type=SubjectType.ANYTHING)
            case GimpComfyUI.PROCEDURE_INVOKE_SYTAN_WF:
                procedure = self.create_procedure(name_raw=name,
                                                  docs="Sytan 1.0 Workflow",
                                                  usage_hint="Keep duplicate fields synchronized.",
                                                  run_func_in=self.sytan_workflow,
                                                  is_image_optional=True,  # Redundant with SubjectType.ANYTHING
                                                  proc_category=ProcedureCategory.WORKFLOW,
                                                  subject_type=SubjectType.ANYTHING)
            case GimpComfyUI.PROCEDURE_DEMO_CUI_NET:
                procedure = self.create_procedure(name_raw=name,
                                                  docs="Demonstrate CUI_NET",
                                                  usage_hint="Sends unprocessed api workflow to server",
                                                  run_func_in=self.demo_cui_net,
                                                  is_image_optional=True,  # Redundant with SubjectType.ANYTHING
                                                  proc_category=ProcedureCategory.WORKFLOW,
                                                  subject_type=SubjectType.ANYTHING
                                                  )
            case GimpComfyUI.PROCEDURE_INVOKE_INPAINTING_WF:
                procedure = self.create_procedure(name_raw=name,
                                                  docs="Inpainting SDXL Workflow",
                                                  usage_hint="Keep duplicate fields synchronized. Sorry",
                                                  run_func_in=self.inpaint_workflow,
                                                  is_image_optional=True,  # Redundant with SubjectType.ANYTHING
                                                  proc_category=ProcedureCategory.WORKFLOW,
                                                  subject_type=SubjectType.ANYTHING)
            case GimpComfyUI.PROCEDURE_INVOKE_IMG2IMG_WF:
                procedure = self.create_procedure(name_raw=name,
                                                  docs="Img2Img SDXL Workflow",
                                                  usage_hint="Keep duplicate fields synchronized. Sorry!",
                                                  run_func_in=self.img2img_workflow,
                                                  is_image_optional=True,  # Redundant with SubjectType.ANYTHING
                                                  proc_category=ProcedureCategory.WORKFLOW,
                                                  subject_type=SubjectType.ANYTHING)
            case GimpComfyUI.PROCEDURE_INVOKE_FLUX_WF:
                procedure = self.create_procedure(name_raw=name,
                                                  docs="Flux1 Dev 16 Workflow",
                                                  usage_hint="Keep duplicate fields synchronized. Sorry!",
                                                  run_func_in=self.flux_workflow,
                                                  is_image_optional=True,  # Redundant with SubjectType.ANYTHING
                                                  proc_category=ProcedureCategory.WORKFLOW,
                                                  subject_type=SubjectType.ANYTHING)
            case GimpComfyUI.PROCEDURE_INVOKE_FLUX_NEG_WF:
                procedure = self.create_procedure(name_raw=name,
                                                  docs="Flux1 Dev 16 with negative prompt Workflow",
                                                  usage_hint="Keep duplicate fields synchronized. Sorry!",
                                                  run_func_in=self.flux_neg_workflow,
                                                  is_image_optional=True,  # Redundant with SubjectType.ANYTHING
                                                  proc_category=ProcedureCategory.WORKFLOW,
                                                  subject_type=SubjectType.ANYTHING)
            case GimpComfyUI.PROCEDURE_DEMO_IMG_N_LAYERS_TREEVIEWS:
                procedure = self.create_procedure(name_raw=name,
                                                  docs="Demonstrate Image and Layers GTK TreeViews",
                                                  usage_hint="Watch for errors in console.",
                                                  run_func_in=self.demo_images_n_layers,
                                                  is_image_optional=True,  # Redundant with SubjectType.ANYTHING
                                                  proc_category=ProcedureCategory.TEST_ANY,
                                                  subject_type=SubjectType.ANYTHING)
            
            case GimpComfyUI.PROCEDURE_INVOKE_FLUX_NEG_UPSCALE_SDXL_0DOT4_WF:
                procedure = self.create_procedure(name_raw=name,
                                                  docs="IFluxNegUpscaleSdxl04Json",
                                                  usage_hint="This dialog was machine-written.",
                                                  run_func_in=self.flux_neg_upscale_sdxl_0dot4_workflow,
                                                  is_image_optional=True,  # Redundant with SubjectType.ANYTHING
                                                  proc_category=ProcedureCategory.WORKFLOW,
                                                  subject_type=SubjectType.ANYTHING)
            # Insert WORKFLOW_PROCEDURE_CASE→
            case _:
                raise NotImplementedError("Unsupported procedure name " + name)
        if GimpComfyUI.is_debugging():
            if procedure is not None:
                message = "Added procedure %s to menu path %s" % (
                    procedure.get_name(), ", ".join(procedure.get_menu_paths()))
                LOGGER_GCUI.info(message)
        return procedure

    def create_procedure(self, name_raw: str,
                         docs: str,
                         usage_hint: str,
                         run_func_in: Callable,
                         subject_type: SubjectType,
                         proc_category: ProcedureCategory = ProcedureCategory.WORKFLOW,
                         is_image_optional: bool = False
                         ) -> Gimp.ImageProcedure:
        run_func: Callable
        match subject_type:
            case SubjectType.ANYTHING:
                run_func = self.run if run_func_in is None else run_func_in
                menu_path = GimpComfyUI.LIMB_IMAGE_MENU_NAME
            case SubjectType.IMAGE:
                run_func = self.run if run_func_in is None else run_func_in
                menu_path = GimpComfyUI.LIMB_IMAGE_MENU_NAME
            case SubjectType.LAYER:
                run_func = self.run_with_layer if run_func_in is None else run_func_in
                menu_path = GimpComfyUI.LIMB_LAYERS_MENU_NAME
            case _:
                raise TypeError("Unsupported SubjectType %s" % str(subject_type))

        name = re.sub(GimpComfyUI.PYTHON_PLUGIN_NAME + "-", "", name_raw)
        procedure = Gimp.ImageProcedure.new(self,
                                            name_raw,
                                            Gimp.PDBProcType.PLUGIN,
                                            run_func,
                                            None)
        procedure.set_menu_label(GLib.dgettext(None,
                                               pretty_name(name).replace("Comfyui", "ComfyUI")))
        procedure.set_documentation(docs, usage_hint, name)
        if is_image_optional or (subject_type == SubjectType.ANYTHING):
            procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.ALWAYS)  # "ALWAYS" required if image optional
            procedure.set_image_types("")  # NOTE: Isn't "*"
        else:
            procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.DRAWABLE)
            procedure.set_image_types("*")  # NOTE: Isn't ""
        procedure.set_icon_name(GimpUi.ICON_GEGL)
        procedure.set_attribution("Hymerfania", "Hymerfania", "2024")

        LOGGER_GCUI.debug(f"proc_category={proc_category}")
        match proc_category:
            case ProcedureCategory.CONFIG:
                menu_path = GimpComfyUI.LIMB_IMAGE_MENU_NAME + "/Config"
            case ProcedureCategory.LIVE_CONNECTION:
                menu_path = GimpComfyUI.LIMB_IMAGE_MENU_NAME + "/Live Connections"
            case ProcedureCategory.WORKFLOW:
                menu_path = GimpComfyUI.LIMB_IMAGE_MENU_NAME + "/Workflow"
            case _:
                pass
        procedure.add_menu_path(menu_path)
        return procedure

    def poll_server(self):
        url_in: str = GimpComfyUI.COMFYUI_URL
        message = f"Value of GimpComfyUI.COMFYUI_URL={GimpComfyUI.COMFYUI_URL}"
        LOGGER_GCUI.debug(message)
        # Gimp.message(message)
        if url_in is None:
            raise ValueError("COMFYUI_URL setting is missing.")
        if not url_in.strip():
            raise ValueError("COMFYUI_URL setting is blank or whitespace.")
        if not url_in.lower().startswith("http://"):
            raise ValueError(f"COMFYUI_URL setting \"{url_in}\" is not a valid http URL.")
        self.is_server_running = server_online(url_in)
        return self.is_server_running


    def run(self, procedure, run_mode, image, n_drawables, drawables, args, run_data):  # noqa
        LOGGER_GCUI.warning(f"Unimplemented procedure {procedure.get_name()}")
        return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, GLib.Error())

    # noinspection PyUnusedLocal
    def invoke_workflow(self,
                        procedure: Gimp.ImageProcedure,
                        factory: WorkflowDialogFactory,
                        title_in: str,
                        role_in: str,
                        blurb_in: str
                        ) -> Gimp.ValueArray:
        ret_values: Gimp.ValueArray = procedure.new_return_values(Gimp.PDBStatusType.CANCEL)
        try:
            if self.poll_server():
                GimpUi.init(GimpComfyUI.PYTHON_PLUGIN_NAME)
                procedure_name_short = re.sub(GimpComfyUI.PYTHON_PLUGIN_NAME + "-", "", procedure.get_name())
                if GimpComfyUI.is_debugging():
                    LOGGER_GCUI.debug("Building dialog for procedure %s" % procedure_name_short)
                dialog: GimpUi.Dialog = factory.new_workflow_dialog(title_in=title_in,
                                                                    role_in=role_in,
                                                                    blurb_in=blurb_in)
                while True:
                    response = dialog.run()
                    if response == Gtk.ResponseType.OK:
                        dialog.destroy()
                        Gimp.displays_flush()
                        pix_buffers: List[GdkPixbuf.Pixbuf] = send_workflow_data(cu_origin=GimpComfyUI.COMFYUI_ORIGIN,
                                                                                 client_id=PLUGIN_UUID_COMFYUI_STR,
                                                                                 nodes_dict=factory.workflow_data,
                                                                                 node_progress=log_node_progress,
                                                                                 step_progress=log_step_progress
                                                                                 )
                        if pix_buffers is None:
                            raise ValueError("None value instead of List[GdkPixbuf.Pixbuf]")
                        if not pix_buffers:
                            LOGGER_GCUI.error("Empty pix_buffers list.")
                        fresh_images: List[Gimp.Image] = images_from_pixbufs(pixbufs=pix_buffers)
                        if fresh_images is None:
                            raise ValueError("Failed to create images")
                        if not fresh_images:
                            raise ValueError("Failed to create images")
                        fresh_image: Gimp.Image
                        for fresh_image in fresh_images:
                            view: Gimp.Display = Gimp.Display.new(fresh_image)
                            if view is None:
                                LOGGER_GCUI.error("View not created for fresh Image")
                        Gimp.displays_flush()
                        ret_values = procedure.new_return_values(Gimp.PDBStatusType.SUCCESS)
                        break
                    elif response == Gtk.ResponseType.APPLY:
                        # This case continues looping within the while loop ...
                        pass
                    else:
                        dialog.destroy()
                        ret_values = procedure.new_return_values(Gimp.PDBStatusType.CANCEL)
                        break

        except Exception as thrown:
            LOGGER_GCUI.exception(thrown)
            ret_values = procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())
        return ret_values

    def default_workflow(self, procedure: Gimp.ImageProcedure,
                       run_mode,  # noqa
                       image,  # noqa
                       n_drawables,  # noqa
                       drawables,  # noqa
                       args,  # noqa
                       run_data  # noqa
                       ) -> Gimp.ValueArray:
        GimpComfyUI.__init_plugin()  # This invocation will provide class-scoped state
        factory: ComfyuiDefaultDialogs = ComfyuiDefaultDialogs(accessor=self._default_accessor)
        ret_values = self.invoke_workflow(procedure=procedure,
                                          factory=factory,
                                          title_in="Default Workflow",
                                          role_in="workflow",
                                          blurb_in="Some dialog values need to be duplicated."
                                          )
        return ret_values

    def sytan_workflow(self, procedure: Gimp.ImageProcedure,
                       run_mode,  # noqa
                       image,  # noqa
                       n_drawables,  # noqa
                       drawables,  # noqa
                       args,  # noqa
                       run_data  # noqa
                       ) -> Gimp.ValueArray:
        GimpComfyUI.__init_plugin()  # This invocation will provide class-scoped state
        factory: SytanSdxl1Dot0Dialogs = SytanSdxl1Dot0Dialogs(accessor=self._sytan_sdxl_accessor)
        ret_values = self.invoke_workflow(procedure=procedure,
                                          factory=factory,
                                          title_in="Sytan 1.0 workflow",
                                          role_in="workflow",
                                          blurb_in="Some dialog values need to be duplicated."
                                          )
        return ret_values

    def inpaint_workflow(self, procedure: Gimp.ImageProcedure,
                         run_mode,  # noqa
                         image,  # noqa
                         n_drawables,  # noqa
                         drawables,  # noqa
                         args,  # noqa
                         run_data  # noqa
                         ) -> Gimp.ValueArray:
        GimpComfyUI.__init_plugin()  # This invocation will provide class-scoped state
        factory: InpaintingSdxl0Dot4Dialogs = InpaintingSdxl0Dot4Dialogs(accessor=self.inpaint_accessor)
        ret_values = self.invoke_workflow(procedure=procedure,
                                          factory=factory,
                                          title_in="Inpainting SDXL",
                                          role_in="workflow",
                                          blurb_in="Some dialog values need to be duplicated."
                                          )
        return ret_values

    def img2img_workflow(self, procedure: Gimp.ImageProcedure,
                         run_mode,  # noqa
                         image,  # noqa
                         n_drawables,  # noqa
                         drawables,  # noqa
                         args,  # noqa
                         run_data  # noqa
                         ) -> Gimp.ValueArray:
        GimpComfyUI.__init_plugin()  # This invocation will provide class-scoped state
        factory: Img2ImgSdxl0Dot3Dialogs = Img2ImgSdxl0Dot3Dialogs(accessor=self.img2img_accessor)
        ret_values = self.invoke_workflow(procedure=procedure,
                                          factory=factory,
                                          title_in="Img2Img SDXL",
                                          role_in="workflow",
                                          blurb_in="Some dialog values need to be duplicated."
                                          )
        return ret_values

    def flux_workflow(self, procedure: Gimp.ImageProcedure,
                         run_mode,  # noqa
                         image,  # noqa
                         n_drawables,  # noqa
                         drawables,  # noqa
                         args,  # noqa
                         run_data  # noqa
                         ) -> Gimp.ValueArray:
        GimpComfyUI.__init_plugin()
        factory: Flux1Dot0Dialogs = Flux1Dot0Dialogs(accessor=self.flux_acc)
        ret_values = self.invoke_workflow(procedure=procedure,
                                          factory=factory,
                                          title_in="Flux dev 16",
                                          role_in="workflow",
                                          blurb_in="Careful with that axe, Eugene!"
                                          )
        return ret_values

    def flux_neg_workflow(self, procedure: Gimp.ImageProcedure,
                      run_mode,  # noqa
                      image,  # noqa
                      n_drawables,  # noqa
                      drawables,  # noqa
                      args,  # noqa
                      run_data  # noqa
                      ) -> Gimp.ValueArray:
        GimpComfyUI.__init_plugin()
        factory: FluxNeg1Dot1Dialogs = FluxNeg1Dot1Dialogs(accessor=self.flux_acc)
        ret_values = self.invoke_workflow(procedure=procedure,
                                          factory=factory,
                                          title_in="Flux dev 16",
                                          role_in="workflow",
                                          blurb_in="Careful with that axe, Eugene!"
                                          )
        return ret_values

    def flux_neg_upscale_sdxl_0dot4_workflow(self, procedure: Gimp.ImageProcedure,
                       run_mode,  # noqa
                       image,  # noqa
                       n_drawables,  # noqa
                       drawables,  # noqa
                       args,  # noqa
                       run_data  # noqa
                       ) -> Gimp.ValueArray:
        factory: FluxNegUpscaleSdxl0Dot4Dialogs = FluxNegUpscaleSdxl0Dot4Dialogs(accessor=self._flux_neg_upscale_sdxl_0dot4_accessor)  # noqa
        ret_values = self.invoke_workflow(procedure=procedure,
                                          factory=factory,
                                          title_in="FluxNegUpscaleSdxl04Json",
                                          role_in="workflow",
                                          blurb_in="This dialog was machine-written."
                                          )
        return ret_values

    # Insert WORKFLOW_INVOCATION_FUNCTION→

    # noinspection PyMethodMayBeStatic
    def demo_cui_net(self, procedure: Gimp.ImageProcedure,
                     run_mode,  # noqa
                     image,  # noqa
                     n_drawables,  # noqa
                     drawables,  # noqa
                     args,  # noqa
                     run_data  # noqa
                     ) -> Gimp.ValueArray:
        GimpComfyUI.__init_plugin()  # This invocation will provide class-scoped state
        ret_code = demonstrate_00()
        if ret_code == 0:
            return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS)
        else:
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())
    # noinspection PyMethodMayBeStatic

    # noinspection PyMethodMayBeStatic
    def demo_images_n_layers(self, procedure: Gimp.ImageProcedure,
                     run_mode,  # noqa
                     image,  # noqa
                     n_drawables,  # noqa
                     drawables,  # noqa
                     args,  # noqa
                     run_data  # noqa
                     ) -> Gimp.ValueArray:
        GimpComfyUI.__init_plugin()  # This invocation will provide class-scoped state
        # LOGGER_GCUI.debug(f"demo_images_n_layers(): ")

        def access_image(image_id):
            if image_id is not None:
                subject_image: Gimp.Image = Gimp.Image.get_by_id(image_id)
                if subject_image is not None:
                    LOGGER_GCUI.debug(f"Found image {image_id}")
                else:
                    LOGGER_GCUI.error(f"Could not find image {image_id}")
            else:
                LOGGER_GCUI.error("image_id is None")

        def access_layer(layer_id):
            if layer_id is not None:
                layer: Gimp.Layer = Gimp.Layer.get_by_id(layer_id)
                if layer is not None:
                    LOGGER_GCUI.debug(f"Found layer {layer_id}")
                else:
                    LOGGER_GCUI.error(f"Could not find layer {layer_id}")
            else:
                LOGGER_GCUI.error("layer_id is None")

        ret_code = display_images_n_layers_dialog(access_image, access_layer)
        if ret_code == 0:
            return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS)
        else:
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())
    # noinspection PyMethodMayBeStatic

    def transceiver_queue_handler(self, source, data=None):
        source_type: type = type(source)
        source_type_name: str = source_type.__name__
        if data is not None and data:
            data_type: type = type(data)
            data_type_name: str = data_type.__name__
            data_msg = f", data is a {data_type_name}, value=\"{data}\""
        else:
            data_msg = ""
        # NOTE: We can be (and are) spammed with duplicate events. We should ignore duplicates.
        # we should ignore the event.
        if source.get_active():
            LOGGER_SDGUIU.debug(f"source is a {source_type_name}{data_msg}")
            self.auto_queue_prompt = ("2" == data)

    def publish_layer(self,
                         procedure: Gimp.ImageProcedure,
                         run_mode,  # noqa
                         image,  # noqa
                         n_drawables,  # noqa
                         drawables,  # noqa
                         args,  # noqa
                         run_data  # noqa
                         ) -> Gimp.ValueArray:

        drawables_names_joined: str = "𝑢𝑛𝑘𝑛𝑜𝑤𝑛🤷"  # noqa This assigned value should never be used.

        def populate_transceiver_dialog(dialog: Gtk.Dialog):
            nonlocal drawables_names_joined
            drawable_name_frame: Gtk.Frame = Gtk.Frame.new(label=f"Layer: {drawables_names_joined}")
            radio_box: Gtk.Box = new_box_of_radios(
                options=["Queue prompt Manually", "Queue prompt Automatically"],
                handler=self.transceiver_queue_handler)
            empty_box: Gtk.Box = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            drawable_name_frame.add(widget=radio_box)  # noqa
            dialog_box: Gtk.Box = dialog.get_content_area()
            dialog_box.pack_start(child=drawable_name_frame, expand=True, fill=False, padding=0)  # noqa
            dialog_box.pack_start(child=empty_box, expand=True, fill=True, padding=4)  # noqa

        drawable_change_listener: DrawableChangeListener = HandleLayerChange(self)
        try:
            image_notifier: DrawableChangeNotifier = DrawableChangeNotifier(
                dialog_customizer=populate_transceiver_dialog)
            run_mode_str = str(run_mode)
            image_present = f"Image present" if image is not None else f"Image is None"
            drawables_cnt_str = f"n_drawables={n_drawables}"
            log_message = f"run_mode_str={run_mode_str}\n{image_present}\n{drawables_cnt_str}\n"
            if drawables is not None and drawables:
                drawables_type = type(drawables)
                drawables_type_name = drawables_type.__name__
                log_message += f"drawables is a {drawables_type_name}; {n_drawables}\n"
                drawables_names = [d.get_name() for d in drawables]
                # This is executed before populate_transceiver_dialog() is called, so the label is set correctly.
                drawables_names_joined = ", ".join(drawables_names)  # noqa
            if args is not None and args:
                args_type = type(args)
                args_type_name = args_type.__name__
                a_len = -1
                try:
                    a_len = len(args)
                except Exception:  # noqa
                    pass
                if a_len >= 0:
                    args_cnt_str = f"args count={a_len}"
                    args_literals = ', '.join(f'"{w}"' for w in args)
                else:
                    args_cnt_str = " singleton"
                    args_literals = ""
                log_message += f"args is a {args_type_name}; {args_cnt_str}\n{args_literals}\n"
            if run_data is not None and run_data:
                rd_type = type(run_data)
                rd_type_name = rd_type.__name__
                log_message += f"run_data type={rd_type_name}"
            # LOGGER_GCUI.debug(log_message)
            for drawable in drawables:
                image_notifier.track_drawables(drawables={drawable}, listener=drawable_change_listener)

            ret_values = procedure.new_return_values(Gimp.PDBStatusType.SUCCESS)
        except Exception as e_err:
            LOGGER_GCUI.exception(e_err)
            ret_values = procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())
        return ret_values

    # noinspection PyMethodMayBeStatic
    def do_quit(self):
        # https://developer.gimp.org/api/3.0/libgimp/vfunc.PlugIn.quit.html
        # This is run at every invocation of this plug-in's procedures, not at shutdown of GIMP.
        try:
            remove_hetero_temp_files()
        except Exception as e_err:
            LOGGER_GCUI.exception(e_err)
        LOGGER_GCUI.info("Plugin %s done." % GimpComfyUI.PYTHON_PLUGIN_NAME_LONG)
        remove_temporary_dictionary(plugin_name_long=GimpComfyUI.PYTHON_PLUGIN_NAME_LONG)


class HandleLayerChange(DrawableChangeListener):
    """
    This will be the GIMP transmitting side of a GIMP <-> ComfyUI-CustomNode connection for images to
    use as latents etc.
    """
    def __init__(self, chassis: GimpComfyUI):
        self._chassis = chassis

    def drawable_changed(self, drawable: Gimp.Drawable):
        """
        :param drawable: The drawable to send
        :return: None
        """
        d_id = drawable.get_id()
        d_name = drawable.get_name()
        change_message: str = f"Drawable {d_id} \"{d_name}\"changed."
        LOGGER_GCUI.debug(change_message)
        try:
            image_as_str = png_base64_str(subject=drawable)
            memory_usage = sys.getsizeof(image_as_str)
            # This cannot exceed the max_size value in the miniserver. Try to verify the argument in the
            # call to "async with serve". Currently, in function _run_server, line 197.
            if memory_usage > MAX_MEMORY_USAGE:
                raise MemoryError(f"Image requires too much memory: Used={memory_usage}, MAX={MAX_MEMORY_USAGE}."
                                  f" Try scaling image down.")
            gimp_websocket: WebSocket = WebSocket()
            transceiver_host: str = GimpComfyUI.TRANSCEIVER_HOST
            transceiver_port: int = GimpComfyUI.TRANSCEIVER_PORT
            transceiver_url: str = url_string(protocol="ws",
                                              host=transceiver_host,
                                              port=transceiver_port)
            try:
                # https://websocket-client.readthedocs.io/en/latest/core.html
                connect_result = gimp_websocket.connect(transceiver_url, max_size=MAX_MEMORY_USAGE)
                if connect_result:
                    LOGGER_GCUI.debug(f"connect_result={connect_result}")
                return_code_0: int = gimp_websocket.send(payload=image_as_str)
                LOGGER_GCUI.debug(f"return_code_0={return_code_0}")
                response_0 = gimp_websocket.recv()
                LOGGER_GCUI.debug(f"response_0={response_0}")
                gimp_websocket.close()
            except Exception as ws_err:
                LOGGER_GCUI.exception(ws_err)
            if self._chassis.auto_queue_prompt:
                gimp_websocket = WebSocket()
                try:
                    connect_result = gimp_websocket.connect(transceiver_url, max_size=MAX_MEMORY_USAGE)
                    if connect_result:
                        LOGGER_GCUI.debug(f"connect_result={connect_result}")
                    payload: str = json.dumps({
                        ControllerCommand.ATTENTION.value: ControllerCommand.ENQUEUE_PROMPT.value
                    })
                    return_code_0: int = gimp_websocket.send(payload=payload)
                    LOGGER_GCUI.debug(f"return_code_0={return_code_0}")
                    response_0 = gimp_websocket.recv()
                    LOGGER_GCUI.debug(f"response_0={response_0}")
                    gimp_websocket.close()
                except Exception as ws_err:
                    LOGGER_GCUI.exception(ws_err)

        except Exception as png_err:
            LOGGER_GCUI.exception(png_err)


# GIMP 2.99.18 is using Python 3.11.8 (main, Feb 13 2024, 07:18:52)  [GCC 13.2.0 64 bit (AMD64)]
GimpComfyUI.configure_loggers()
# For Gimp.main invocation see source gimp_world\gimp\libgimp\gimp.c and
# https://developer.gimp.org/api/3.0/libgimp/func.main.html
Gimp.main(GimpComfyUI.__gtype__, sys.argv)
