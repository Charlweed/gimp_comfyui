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
import logging
import os
import sys
import urllib


gi.require_version("Gtk", "3.0")  # noqa E402
gi.require_version('GdkPixbuf', '2.0')  # noqa E402
# It is unfortunate that the requests, requests_toolbelt, and websocket-client modules are omitted from
# Linux GIMP's python. The source of those modules are therefore included in this plugin.
import requests_toolbelt  # This refers to the local package in this plug-in's directory
from requests_toolbelt import MultipartEncoder  # This refers to the local package in this plug-in's directory
import websocket  # This refers to the local package in this plug-in's directory
from websocket import WebSocket   # This refers to the local package in this plug-in's directory
from gi.repository import GdkPixbuf
from http.client import HTTPResponse
from typing import Any, Dict, List, Callable
from urllib import error
from urllib import request
from urllib.parse import urlencode
from utilities.heterogeneous import strip_hetero_brand_from_root

LGR_CNU = logging.getLogger("cui_net_utils")
LGR_FMT_CNU = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=LGR_FMT_CNU, level=logging.INFO)
LGR_CNU.setLevel(logging.INFO)


def enqueue_prompt(cu_origin: str, client_id: str, workflow_data) -> Dict:
    prompt_dict: Dict = {"prompt": workflow_data, "client_id": client_id}
    data = json.dumps(prompt_dict, indent=2, sort_keys=True).encode('utf-8')
    server_url = f"http://{cu_origin}/prompt"
    log_message = f"enqueue_prompt() opening {server_url}"
    LGR_CNU.debug(log_message)
    req: urllib.request.Request = urllib.request.Request(server_url, data=data)
    try:
        response: HTTPResponse = urllib.request.urlopen(req)  # *modified* http.client.HTTPResponse
        response_json_byes: bytes = response.read()  # bytes
        response_obj: Dict = json.loads(response_json_byes)
        return response_obj
    except urllib.error.HTTPError as h_err:
        LGR_CNU.exception(h_err)
        message = f"url={h_err.url}, code={h_err.code}, reason={h_err.reason}"
        LGR_CNU.error(message)
        LGR_CNU.error(str(h_err.headers))
    except urllib.error.URLError as u_err:
        LGR_CNU.exception(u_err)
        message = f"url={u_err.filename}, code={u_err.errno}, reason={u_err.reason}"
        LGR_CNU.error(message)
    return {}


def get_history(cu_origin: str, prompt_id) -> Dict:
    server_url = f"http://{cu_origin}/history/{prompt_id}"
    # log_message = "get_history() opening %s" % server_url
    # LGR_CNU.debug(log_message)
    response: HTTPResponse  # See https://docs.python.org/3.11/library/http.client.html#httpresponse-objects
    with urllib.request.urlopen(server_url) as response:
        try:
            response_bytes: bytes = response.read()
            response_obj: Dict = json.loads(response_bytes)
            return response_obj
        except urllib.error.HTTPError as h_err:
            LGR_CNU.exception(h_err)
            message = f"url={h_err.url}, code={h_err.code}, reason={h_err.reason}"
            LGR_CNU.error(message)
            LGR_CNU.error(str(h_err.headers))
        except urllib.error.URLError as u_err:
            LGR_CNU.exception(u_err)
            message = f"url={u_err.filename}, code={u_err.errno}, reason={u_err.reason}"
            LGR_CNU.error(message)
        return {}


def get_image(cu_origin: str, filename: str, subfolder: str, folder_type=None) -> bytes:
    """
     Requests that ComfyUI read an image from where the server has stored it.
     By default, the output folder is "ComfyUI/output", where "ComfyUI" is the home directory of the server.
    :param cu_origin: The origin part of the final constructed URL
    :param filename: The filename. This was obtained from the previous response.
    :param subfolder: The subfolder. This was also obtained from the previous response.
    :param folder_type: Unknown.
    :return: the bytes of the image.
    """
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    server_url = f"http://{cu_origin}/view?{url_values}"
    # log_message = f"get_image() opening {server_url}"
    # LGR_CNU.debug(log_message)
    try:
        response: HTTPResponse  # See https://docs.python.org/3.11/library/http.client.html#httpresponse-objects
        with urllib.request.urlopen(server_url) as response:
            body: bytes = response.read()
            return body
    except urllib.error.HTTPError as h_err:
        LGR_CNU.exception(h_err)
        message = f"url={h_err.url}, code={h_err.code}, reason={h_err.reason}"
        LGR_CNU.error(message)
        LGR_CNU.error(str(h_err.headers))
    except urllib.error.URLError as u_err:
        LGR_CNU.exception(u_err)
        message = f"url={u_err.filename}, code={u_err.errno}, reason={u_err.reason}"
        LGR_CNU.error(message)
    return b''


def get_images(cu_origin: str,
               client_id: str,
               socket: WebSocket,
               workflow_data: Dict,
               node_progress: Callable[[int, int, str | None], None],
               step_progress: Callable[[int, int, str | None], None],
               ) -> Dict[Any, List]:
    raw_dict: Dict = enqueue_prompt(cu_origin=cu_origin, client_id=client_id, workflow_data=workflow_data)
    if raw_dict is None:
        raise IOError("enqueue_prompt returned null instead of dict")
    if not raw_dict:
        raise ValueError("enqueue_prompt returned empty dict")
    if 'prompt_id' not in raw_dict:
        unexpected = json.dumps(raw_dict, indent=2, sort_keys=True)
        LGR_CNU.error(unexpected)
        raise ValueError("key \'prompt_id\' missing from prompt response.")

    prompt_id = raw_dict['prompt_id']
    output_images: Dict = {}
    _track_progress(workflow_data=workflow_data,
                    ws=socket,
                    prompt_id=prompt_id,
                    step_progress=step_progress,
                    node_progress=node_progress
                    )

    history_dict: Dict = get_history(cu_origin=cu_origin, prompt_id=prompt_id)[prompt_id]
    if 'outputs' not in history_dict:
        unexpected = json.dumps(history_dict, indent=2, sort_keys=True)
        LGR_CNU.error(unexpected)
        raise ValueError("\'outputs\' not in history dict.")
    for unused in history_dict['outputs']:  # noqa
        for node_id in history_dict['outputs']:
            node_output = history_dict['outputs'][node_id]
            # Note: "bytes" is a class whose instances (aka objects) are a sequence of byte objects.
            #  images_output is a list of "bytes" instances
            images_output: List[bytes] = []
            if 'images' in node_output:
                for image in node_output['images']:
                    # ComfyUI has already stored the images to its filesystem. We are fetching them from there.
                    # When the server is localhost, we could load them directly.
                    file_name = image['filename']
                    if "temporary_trash" in file_name.lower() or "PBL-_temp_" in file_name.lower():
                        fetch_log_message = f"get_images() skipping \"{file_name}\""
                        LGR_CNU.warning(fetch_log_message)
                        continue
                    else:  # "continue" above should make this "else" unnecessary, but logic might change.
                        fetch_log_message = (f"get_images() cu_origin={cu_origin}"
                                             f"; filename={file_name}"
                                             f"; subfolder={image['subfolder']}"
                                             f"; folder_type={image['type']}")
                        LGR_CNU.info(fetch_log_message)
                        image_data: bytes = get_image(cu_origin=cu_origin,
                                                      filename=image['filename'],
                                                      subfolder=image['subfolder'],
                                                      folder_type=image['type']
                                                      )
                        if image_data:  # Don't append if result is nothing
                            images_output.append(image_data)
                        else:
                            LGR_CNU.error("No bytes obtained from get_image(%s)" % image['filename'])
            output_images[node_id] = images_output
    return output_images


def log_node_progress(finished: int, total: int, message: str = str | None):
    if message is None:
        LGR_CNU.info(f"Node {finished} of {total} ...")
    else:
        LGR_CNU.info(message)


def log_step_progress(finished: int, total: int, message: str = str | None):
    if message is None:
        LGR_CNU.info(f"... step {finished} of {total} completed.")
    else:
        LGR_CNU.info(message)


def make_pixbuf_png(p_bytes: bytes) -> GdkPixbuf.Pixbuf | None:
    """
    :param p_bytes: A python bytes object
    :return: a prepped GdkPixbuf.Pixbuf, or None if there was an error.
    """

    pixel_buffer: GdkPixbuf.Pixbuf | None = None
    try:
        pixbuf_loader: GdkPixbuf.PixbufLoader = GdkPixbuf.PixbufLoader.new_with_type("png")

        def prepped(*args):  # noqa
            """
            :param args: So far, this is always a single GdkPixbuf.PixbufLoader
            :return: None
            """
            # LGR_CNU.debug('prepped:')
            nonlocal pixel_buffer
            pixel_buffer = pixbuf_loader.get_pixbuf()
            # message = f"prepped... width={pixel_buffer.get_width()},height={pixel_buffer.get_height()}"
            # LGR_CNU.debug(message)
            # for an_arg in args:
            #     LGR_CNU.debug(f"prepped... {str(an_arg)}")

        def updated(*args):  # noqa
            """
            :param args: So far, this is always a single GdkPixbuf.PixbufLoader
            :return: None
            """
            # LGR_CNU.debug('updated:')
            # for an_arg in args:
            #     LGR_CNU.debug(f"updated... {str(an_arg)}")
            pass

        def loader_closed(*args):  # noqa
            """
            :param args: So far, this is always a single GdkPixbuf.PixbufLoader
            :return: None
            """
            # LGR_CNU.debug('closed:')
            # for an_arg in args:
            #     LGR_CNU.debug(f"closed... {str(an_arg)}")
            pass

        # Keep these as examples for later development.
        pixbuf_loader.connect('area-prepared', prepped)
        pixbuf_loader.connect('area-updated', updated)
        pixbuf_loader.connect("closed", loader_closed)
        # This is not crazy. Gtk complains if pixbuf_loader.close() is not called, regardless of the
        # validity of pixbuf_loader, but will also raise a second exception on pixbuf_loader.close() if
        # pixbuf_loader.write() failed. So both get try-catch blocks.
        try:
            write_bool = pixbuf_loader.write(p_bytes)
            if not write_bool:
                LGR_CNU.warning("Something not quite correct with GdkPixbuf.PixbufLoader.write()...")

        except Exception as ex:
            LGR_CNU.exception(ex)
        try:
            close_bool = pixbuf_loader.close()
            if not close_bool:
                LGR_CNU.warning("Something not quite correct with GdkPixbuf.PixbufLoader.close()...")
        except Exception as ex:  # noqa
            pass

    except Exception as ex:
        LGR_CNU.exception(ex)

    return pixel_buffer


def send_workflow_data(cu_origin: str,
                       client_id: str,
                       nodes_dict: Dict,
                       node_progress: Callable[[int, int, str | None], None],
                       step_progress: Callable[[int, int, str | None], None],
                       ) -> List[GdkPixbuf.Pixbuf]:
    """
    Uses Websocket module to send workflow data to ComfyUI server
    :param cu_origin: The origin part of the final constructed URL
    :param client_id: An identifier for this client, here a UUID for this comfyUI plugin.
    :param nodes_dict: The workflow data.
    :param step_progress: a Callable[[int, int, str | None], None] to track the progress of steps in the Sampler. You
    can pass log_step_progress as an argument.
    :param node_progress: a Callable[[int, int, str | None], None] to track the progress of nodes in the workflow. You
    can pass log_node_progress as an argument.
    :return: A (singular) list of GdkPixbuf.Pixbufs
    """
    results: List[GdkPixbuf.Pixbuf] = []
    socket: WebSocket = WebSocket()
    ws_url = f"ws://{cu_origin}/ws?clientId={client_id}"
    log_message = f"send_workflow_data() opening {ws_url}"
    LGR_CNU.debug(log_message)
    socket.connect(ws_url)
    image_dict_of_lists: Dict = get_images(cu_origin=cu_origin,
                                           client_id=client_id,
                                           socket=socket,
                                           workflow_data=nodes_dict,
                                           node_progress=node_progress,
                                           step_progress=step_progress
                                           )
    message = f"Received {len(image_dict_of_lists)} lists from \"{ws_url}\""
    LGR_CNU.debug(message)
    for some_list in image_dict_of_lists.values():
        for list_item in some_list:
            item_type = type(list_item)
            item_type_name = item_type.__name__
            # message = f"type of image_data is {item_type_name}"
            # LGR_CNU.debug(message)
            if isinstance(list_item, bytes):
                # LGR_CNU.debug("submitting bytes...")
                pixel_buffer: GdkPixbuf.Pixbuf = make_pixbuf_png(list_item)
                if pixel_buffer is not None:
                    results.append(pixel_buffer)
            else:
                message = f"skipping non-string {item_type_name}"
                LGR_CNU.warning(message)
    return results


def _track_progress(workflow_data: Dict[str, Any],
                    ws: WebSocket,
                    prompt_id: str,
                    node_progress: Callable[[int, int, str | None], None],
                    step_progress: Callable[[int, int, str | None], None],
                    ):
    node_ids: List[str] = list(workflow_data.keys())
    finished_nodes = []

    while True:
        # ConnectionClosed – When the connection is closed.
        # RuntimeError – If two threads call recv() or recv_streaming() concurrently.
        # TimeoutError - If timeout is set and no message is received within timeout seconds
        received: str | bytes = ws.recv()
        if isinstance(received, str):
            server_reply: Dict[str, Any] = json.loads(received)
            reply_type: str = server_reply['type']
            match reply_type:
                case 'progress':
                    data: Dict[str, Any] = server_reply['data']
                    current_step = data['value']
                    total = data['max']
                    # sampler_progress_msg = f"Step {current_step} of {total}"
                    step_progress(current_step, total, None)
                case 'execution_cached':
                    data: Dict[str, Any] = server_reply['data']
                    for itm in data['nodes']:
                        if itm not in finished_nodes:
                            finished_nodes.append(itm)
                            # node_ex_progress_msg: str = f"Progress: {len(finished_nodes)}/{len(node_ids)} tasks done"
                            node_progress(len(finished_nodes) - 1, len(node_ids), None)
                case 'executing':
                    data: Dict[str, Any] = server_reply['data']
                    if data['node'] not in finished_nodes:
                        finished_nodes.append(data['node'])
                        # node_progress_msg: str = f"Progress: {len(finished_nodes)}/{len(node_ids)} tasks done"
                        node_progress(len(finished_nodes) - 1, len(node_ids), None)

                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break  # Execution is done
                case _:
                    pass
        else:  # Not str, assume bytes
            continue  # previews are binary data
    return


def upload_images_to_inputs(cu_origin: str,
                            image_file_path: str,
                            name_alt: str = None,
                            image_type: str = "input",
                            overwrite: bool = True) -> bytes:
    """
    Uploads an image to the ComfyUI inputs folder. You must do this before images can be used within workflows.
    :param cu_origin: The origin part of the final constructed URL
    :param image_file_path: Local path to the image file
    :param name_alt: An alternate name to give the file on the server
    :param image_type: The image "type", but don't use it. I think it chooses an ComfyUI image subdirectory.
    :param overwrite: If True, an image file on the server with the same name will be replaced. If false, I don't know.
    :return:
    """
    if not os.path.isfile(image_file_path):
        raise IOError(f"Could not read image file \"{image_file_path}\"")
    if name_alt is not None:
        name: str = name_alt
    else:
        # strip_hetero_brand_from_root() removes the infix that makes every filename unique. Accordingly, files with the
        # same name will be overwritten, instead of filling up the input directory with identical files that have
        # different names.
        name: str = strip_hetero_brand_from_root(os.path.basename(image_file_path))
    with open(image_file_path, 'rb') as image_file_object:
        multipart_data = MultipartEncoder(
            fields={
                'image': (name, image_file_object, 'image/png'),
                'type': image_type,
                'overwrite': str(overwrite).lower()
            }
        )

        data = multipart_data
        headers = {'Content-Type': multipart_data.content_type}
        upload_request = urllib.request.Request(f"http://{cu_origin}/upload/image", data=data, headers=headers)
        response: HTTPResponse
        try:
            LGR_CNU.debug(f"Uploading \"{image_file_path}\" to {cu_origin}")
            with urllib.request.urlopen(upload_request) as response:
                return response.read()
        except urllib.error.HTTPError as h_err:
            LGR_CNU.exception(h_err)
            message = f"url={h_err.url}, code={h_err.code}, reason={h_err.reason}"
            LGR_CNU.error(message)
            LGR_CNU.error(str(h_err.headers))
        except urllib.error.URLError as u_err:
            LGR_CNU.exception(u_err)
            message = f"url={u_err.filename}, code={u_err.errno}, reason={u_err.reason}"
            LGR_CNU.error(message)
        return bytes()


def demonstrate_00() -> int:
    pixel_buffer_version = GdkPixbuf.PIXBUF_VERSION  # GdkPixbuf.PIXBUF_VERSION=2.42.10
    LGR_CNU.info(f"GdkPixbuf.PIXBUF_VERSION={pixel_buffer_version}")
    script_filename = os.path.realpath(__file__)
    script_dir_path = os.path.dirname(script_filename)
    asset_dir_path = os.path.join(script_dir_path, "../assets")
    comfyui_host = sys.argv[1]
    comfyui_port = 8188  # Port
    comfyui_origin: str = f"{comfyui_host}:{comfyui_port}"
    demo_uuid = "ff6dd801-3eb0-4817-a4f3-46698c672959"
    workflow_file_path: str = os.path.join(asset_dir_path, "sytan_sdxl_1.0_workflow_api.json")
    workflow_data: Dict[str, Any]
    try:
        with open(workflow_file_path, 'r') as in_file:
            workflow_data = json.load(in_file)
    except IOError as io_err:
        logging.exception(io_err)
        return 10
    try:
        send_workflow_data(cu_origin=comfyui_origin,
                           nodes_dict=workflow_data,
                           client_id=demo_uuid,
                           node_progress=log_node_progress,
                           step_progress=log_step_progress
                           )
    except urllib.error.HTTPError as ht_err:
        logging.exception(ht_err)
        return 10
    return 0


def demonstrate_upload() -> int:
    script_filename = os.path.realpath(__file__)
    script_dir_path = os.path.dirname(script_filename)
    asset_dir_path = os.path.join(script_dir_path, "../assets")
    comfyui_host = sys.argv[1]
    comfyui_port = 8188  # Port
    comfyui_origin: str = f"{comfyui_host}:{comfyui_port}"
    image_file_path: str = os.path.join(asset_dir_path, "green_diamond_00.png")
    try:
        upload_images_to_inputs(
            cu_origin=comfyui_origin,
            image_file_path=image_file_path
        )
    except urllib.error.HTTPError as ht_err:
        logging.exception(ht_err)
        return 10
    return 0


def main() -> int:
    ret_code: int = demonstrate_upload()
    return ret_code


if __name__ == '__main__':
    sys.exit(main())
