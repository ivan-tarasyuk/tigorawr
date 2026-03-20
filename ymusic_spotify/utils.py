import json as json_module
import re
from pathlib import Path
from typing import Any, Optional, List, Union, Tuple

import requests

from ymusic_spotify.config import PATTERNS
from ymusic_spotify.exceptions import IOException, InvalidDataStructure, YMException


def load_txt(file_path: Union[Path]) -> List[str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            list_from_txt = [line.strip() for line in file if line.strip()]
        return list_from_txt
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found at '{file_path}'") from e
    except Exception as e:
        raise IOException(f"An error occurred while opening '{file_path}'", e) from e


def load_json(file_path: Union[Path]) -> dict:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            dict_from_json = json_module.load(file)
        return dict_from_json
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found at '{file_path}'") from e
    except json_module.JSONDecodeError as e:
        raise InvalidDataStructure(f"Invalid JSON at '{file_path}'", e.msg) from e
    except Exception as e:
        raise IOException(f"An error occurred while opening '{file_path}'", e) from e


def fetch_json(url: str) -> dict:
    try:
        response = requests.get(url)
        response.raise_for_status()
        try:
            return response.json()
        except json_module.JSONDecodeError as e:
            raise InvalidDataStructure(f"Invalid JSON received from '{url}'") from e
    except requests.HTTPError as e:
        raise RuntimeError(f"Failed to export data from website. Status code: {response.status_code}") from e
    except requests.RequestException as e:
        raise ConnectionError(f"Network error occurred while reaching '{url}': {e}") from e
    except Exception as e:
        raise YMException(f"An error occurred while processing data from '{url}'", e) from e


def write_file(file_path: Union[Path], lines: str, regime: str = 'w') -> None:
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, regime, encoding='utf-8') as file:
            file.write(lines)
    except Exception as e:
        raise IOException(f'An error occurred while writing to file "{file_path}"', e)


def validate_str(data: Any) -> Optional[str]:
    if type(data) not in (str, int):
        return None
    return str(data).strip()


def validate_list(data: Any) -> list:
    if type(data) is not list:
        return []
    return data


def validate_list_items(data: Any) -> Optional[List[str]]:
    valid_list = validate_list(data)
    return [valid_str for element in valid_list if (valid_str := validate_str(element))]


def validate_dict(data: Any) -> dict:
    if type(data) is not dict:
        return {}
    return data


def validate_dict_item(data: Any, key: str) -> str:
    valid_dict = validate_dict(data)
    return validate_str(valid_dict.get(key))


def validate_pattern(data: str, datatype: str) -> Union[str, Tuple[str]]:
    data = validate_str(data)
    if data is None:
        raise InvalidDataStructure(f'Data for pattern validation must be a string')

    if datatype not in PATTERNS:
        raise InvalidDataStructure(f'Pattern validation is not implemented for {datatype}')

    if datatype == 'playlist_html':
        match = re.search(PATTERNS[datatype], data)
    else:
        match = re.match(PATTERNS[datatype], data)
    if match is None:
        raise InvalidDataStructure(f'Data does not match pattern for {datatype}')
    return match.groups() if match.lastindex > 1 else match.group(1)


def validate_actions_key(key: Optional[str], range_limit: int = 4) -> int:
    return int(key) if key.isdigit() and int(key) in range(min(range_limit, 4)) else 4


def match_str(str_1: str, str_2: str, *, a: int, b: int, c: int) -> int:
    """Compare two strings and return weighted score

    Scoring:
        a - exact match
        b - prefix match (one starts with another)
        c - one or both strings are empty
        0 - no match
    """
    if not str_1 or not str_2:
        return c
    if str_1 == str_2:
        return a
    if str_1.startswith(str_2) or str_2.startswith(str_1):
        return b
    return 0


def match_set(set_1: set, set_2: set, *, a: int, b: int) -> int:
    """Compare two sets and return weighted score

    Scoring:
        a - exact match
        b - subset/superset relationship
        0 - no meaningful overlap
    """
    if set_1 == set_2:
        return a
    if set_1 > set_2 or set_1 < set_2:
        return b
    return 0
