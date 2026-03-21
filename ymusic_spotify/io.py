import json as json_module
from pathlib import Path
from typing import List

import requests

from ymusic_spotify.exceptions import IOException, InvalidDataStructure, YMException


def load_txt(file_path: Path) -> List[str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            list_from_txt = [line.strip() for line in file if line.strip()]
        return list_from_txt
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found at '{file_path}'") from e
    except Exception as e:
        raise IOException(f"An error occurred while opening '{file_path}'", e) from e


def write_txt(file_path: Path, lines: str, regime: str = 'w') -> None:
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, regime, encoding='utf-8') as file:
            file.write(lines)
    except Exception as e:
        raise IOException(f'An error occurred while writing to file "{file_path}"', e)


def load_json(file_path: Path) -> dict:
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
