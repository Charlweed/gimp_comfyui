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

import codecs
import json
import os.path
import re
import sys
from abc import ABC, abstractmethod
from typing import Dict
from utilities.type_utils import *


ASCII_PUNCTUATION = r'!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'
ASCII_PUNCTUATION_REGEX = "[%s]" % re.escape(ASCII_PUNCTUATION)
BASIC_PUNCTUATION_REGEX: str = r'[^\w\s_]'
CRUDE_VERSION_REGEX: str = r"(\d+)\.(\d+)"
# noinspection RegExpRedundantEscape
ESCAPE_SEQUENCE_RE = re.compile(r'''
    ( \\U........      # 8-digit hex escapes
    | \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )''', re.UNICODE | re.VERBOSE)
FILE_BREAKERS = r'"\'*/:;<>\`{}~'
FILE_BREAKERS_REGEX = "[%s]" % re.escape(FILE_BREAKERS)
ID_BREAKERS = r'!"#$%&\'()*+,-./:;<=>?@[\]^`{|}~'
ID_BREAKERS_REGEX = "[%s]" % re.escape(ID_BREAKERS)
INITIAL_DIGITS_PATTERN: re.Pattern = re.compile(r"^\d+")
LOGGER_WF2PY = logging.getLogger("Workflow2PythonGenerator")
LOGGER_FORMAT_WF2PY = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
INT_MIN = -2147483648  # Local minimum to prevent API, JSON, and other errors. Python has no limit
INT_MAX = 18446744073709519872  # Local minimum to prevent API, JSON, and other errors. Python has no limit
SP04 = " " * 4
SP08 = " " * 8
SP12 = " " * 12
SP16 = " " * 16
SP24 = " " * 24
SP26 = " " * 26
SP27 = " " * 27
SP28 = " " * 28
SP36 = " " * 36
SP38 = " " * 38
SP40 = " " * 40
SP54 = " " * 54
SP55 = " " * 55
SP56 = " " * 56
SP58 = " " * 58
SP59 = " " * 59
SP60 = " " * 60
SP67 = " " * 67
SP68 = " " * 68
SP69 = " " * 69
SP70 = " " * 70
SP72 = " " * 72
SP73 = " " * 73
SP74 = " " * 74


def class_name(in_str: str) -> str:
    plain = in_str.replace(".", "")
    spaceless = plain.replace(" ", "_")
    punctless = re.sub(ID_BREAKERS_REGEX, "", spaceless)
    l_cases: List[str] = punctless.split("_")
    title_cases: List[str] = [lc.title() for lc in l_cases]
    return "".join(title_cases)


def class_name_external(index_str: str, node_dict: Dict) -> str:
    return node_dict["class_type"] + class_name(ugly_suffix(index_str=index_str, node_dict=node_dict))


def decode_escapes(s):
    def decode_match(match):
        return codecs.decode(match.group(0), 'unicode-escape')
    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)


def identifier(in_str: str) -> str:
    plain = in_str.replace(".", "")
    spaceless = plain.replace(" ", "_")
    punctless = re.sub(ID_BREAKERS_REGEX, "", spaceless)
    return punctless.lower()


def identifier_external(index_str: str, node_dict: Dict) -> str:
    return (node_dict["class_type"].lower() + "_" +
            identifier(ugly_suffix(index_str=index_str, node_dict=node_dict)))


def input_names(node_dict: Dict[str, Any]) -> List[str]:
    return node_dict["inputs"].keys()


def input_types(node_dict: Dict[str, Any]) -> Dict[str, type]:
    str_type_dict: Dict[str, type] = {}
    for item in node_dict.items():  # We don't need no stinking comprehensions!
        key = item[0]
        value = item[1]
        value_type = type(value)
        str_type_dict[key] = value_type
    return str_type_dict


def starts_with_digits(some_string: str):
    return INITIAL_DIGITS_PATTERN.search(some_string)


def snake_to_title(in_str: str) -> str:
    return in_str.replace("_", " ").title()


def title(node_dict: Dict) -> str:
    return node_dict["_meta"]["title"]


def ugly_suffix(index_str: str, node_dict: Dict):
    return "%03d%s" % (int(index_str), title(node_dict=node_dict))


def unique_id(candidate_identifier, name_list: List[str]) -> str:
    id_out = candidate_identifier
    count: int = 0
    if id_out in name_list:
        while id_out in name_list:
            count += 1
            id_out = "%s_%02d" % (candidate_identifier, count)
    name_list.append(id_out)
    return id_out


class Workflow2PythonGenerator(ABC):
    WORKFLOW_TAG = "_workflow_api"
    ASSET_DIR_NAME = "../assets"
    DEBUG_ENV_KEY = "PYTHON_GENERATOR_DEBUG"

    @classmethod
    def is_debug_mode(cls):
        flag: str | None = os.environ.get(cls.DEBUG_ENV_KEY)
        if not flag:
            return False
        return bool_of(flag)

    def __init__(self):
        if Workflow2PythonGenerator.is_debug_mode():
            logging.basicConfig(format=LOGGER_FORMAT_WF2PY, level=logging.DEBUG)
        else:
            logging.basicConfig(format=LOGGER_FORMAT_WF2PY, level=logging.INFO)
        script_filename = os.path.realpath(__file__)
        self._script_dir_path = os.path.dirname(script_filename)
        self._workflow_file_path: str = sys.argv[1]
        if not self._workflow_file_path.endswith(".json"):
            raise IOError(f"Filename argument \"{self._workflow_file_path}\" must end with \".json\"")
        if Workflow2PythonGenerator.WORKFLOW_TAG not in self._workflow_file_path:
            raise IOError("Filename argument must contain substring \"%s\"" % Workflow2PythonGenerator.WORKFLOW_TAG)
        self._asset_dir_path = os.path.join(self._script_dir_path, Workflow2PythonGenerator.ASSET_DIR_NAME)
        self._json_path = os.path.join(self._asset_dir_path, self._workflow_file_path)
        self._json_dict: Dict = {}
        self._enum_indexes_dict: Dict[str, str] = {}
        self._node_class_names: List[str] = []
        self._node_enum_names: List[str] = []

    @property
    def enum_instances(self) -> Dict[str, str]:
        return self._enum_indexes_dict

    @property
    def json_path(self):
        _json_path_exists = os.path.isfile(self._json_path)
        if not _json_path_exists:
            raise IOError("Could not find workflow JSON file \"%s\"" % self._json_path)
        return self._json_path

    @property
    @abstractmethod
    def python_class_file_name(self) -> str:
        pass

    @property
    def python_class_name(self) -> str:
        plain = self.python_class_file_name.replace(".py", "")
        return class_name(plain)

    @property
    def python_class_file_path(self):
        return os.path.join(self.script_dir_path, self.python_class_file_name)

    @property
    def nodes_dictionary(self) -> Dict:
        if (self._json_dict is None) or (not self._json_dict) or (len(self._json_dict) == 0):
            with open(self._json_path, "r") as f:
                self._json_dict = json.load(f)
        return self._json_dict

    @property
    def script_dir_path(self):
        return self._script_dir_path

    @property
    def workflow_path(self):
        return self._workflow_file_path

    @property
    def workflow_filename(self):
        return os.path.basename(os.path.normpath(self.workflow_path))

    def enum_identifier(self, node_title: str):
        punctless = re.sub(ID_BREAKERS_REGEX, "", node_title)
        enum_id = "NODE_" + punctless.upper().replace(" ", "_")
        return unique_id(enum_id, self._node_class_names)

    def title_of(self, index_str: str) -> str:
        return title(node_dict=self.nodes_dictionary[index_str])

    @abstractmethod
    def write_source_file(self):
        pass
