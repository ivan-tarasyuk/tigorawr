import re
from typing import Any, List, Optional, Tuple, Union

from ymusic_spotify.config import PATTERNS
from ymusic_spotify.exceptions import InvalidDataStructure


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
