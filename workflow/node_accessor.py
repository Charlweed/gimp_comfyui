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

from typing import Dict, Any


class NodesAccessor:
    ASSET_DIR_NAME = "../assets"

    def __init__(self, api_workflow: str):
        self._json_dict: Dict = {}
        script_filename = os.path.realpath(__file__)
        script_dir_path = os.path.dirname(script_filename)
        self._asset_dir_path = os.path.join(script_dir_path, "../assets")
        self._this_json_path = os.path.join(self._asset_dir_path, api_workflow)
        self._json_dict: Dict = {}

    @property
    def prompt_bytes(self) -> bytes:
        prompt = {"prompt": self.nodes_dict}
        return json.dumps(prompt).encode('utf-8')

    def read_dict_from_file(self) -> Dict[str, Any]:
        loaded: Dict[str, Any]
        with open(self._this_json_path, "r") as f:
            loaded = json.load(f)
        return loaded

    @property
    def asset_dir_path(self):
        asset_path_exists = os.path.isdir(self._asset_dir_path)
        if not asset_path_exists:
            raise IOError("Could not find directory \"%s\"" % self._asset_dir_path)
        return self._asset_dir_path

    @property
    def nodes_dict(self) -> Dict[str, Any]:
        if (self._json_dict is None) or (not self._json_dict) or (len(self._json_dict) == 0):
            self._json_dict = dict(self.read_dict_from_file())
        return self._json_dict

    @property
    def workflow_api_json_path(self):
        json_path_exists = os.path.isfile(self._this_json_path)
        if not json_path_exists:
            raise IOError("Could not find workflow JSON file \"%s\"" % self._this_json_path)
        return self._this_json_path
