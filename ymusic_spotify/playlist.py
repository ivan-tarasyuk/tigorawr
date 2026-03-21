import time
from pathlib import Path
from typing import Union, List, Optional

from ymusic_spotify.config import ARTIST_SEP, JSON_FILE, JSON_URL, ENTITY_SEP, TXT_FILE, RESULTS
from ymusic_spotify.exceptions import IOException, InvalidDataStructure
from ymusic_spotify.io import load_json, fetch_json, load_txt, write_txt
from ymusic_spotify.track import Track
from ymusic_spotify.validation import validate_str, validate_list, validate_pattern


class YMPlaylistBase:
    def __init__(self, username: str, playlist_id: Union[str, int], playlist_title: str, tracks: List[Track]):
        self._username = validate_str(username)
        self._playlist_id = validate_str(playlist_id)
        self._playlist_title = validate_str(playlist_title)
        self._tracks = validate_list(tracks)

    def __bool__(self):
        return all([self._username, self._playlist_id, self._playlist_title, self._tracks])

    def __repr__(self):
        if not self._tracks:
            return '\nPlaylist is empty'
        return '\n'.join([str(track) for track in self._tracks])

    def __len__(self):
        return len(self._tracks)

    def __getitem__(self, item: str):
        if not hasattr(self, f'_{item}'):
            raise KeyError(f"\nAttribute '{item}' not found")
        return getattr(self, f'_{item}')

    def save_to_txt(self) -> None:
        if bool(self):
            base_name = f'{self._username}_{self._playlist_title}_{self._playlist_id}'
        else:
            base_name = 'tigorawr'
        file_path = RESULTS / f'{base_name}_{time.time_ns()}.txt'
        try:
            write_txt(file_path, str(self))
            print(f"\nPlaylist has been saved to '{file_path}'")
        except Exception as e:
            raise IOException(f"An error occurred while saving playlist to '{file_path}'", e) from e


class YMPlaylistDict(YMPlaylistBase):
    def __init__(self, playlist_dict: dict):
        try:
            raw_playlist = playlist_dict['playlist']
            tracks = [Track.from_ymusic(item) for item in raw_playlist['tracks']]
            super().__init__(raw_playlist['owner']['login'], raw_playlist['kind'], raw_playlist['title'], tracks)
        except KeyError as e:
            raise InvalidDataStructure(f'Invalid data structure {playlist_dict}. Key is missing', e)


class YMPlaylistJSON(YMPlaylistDict):
    def __init__(self, file_path: Union[Path, str] = JSON_FILE):
        playlist_dict = load_json(Path(file_path))
        super().__init__(playlist_dict)


class YMPlaylistCreds(YMPlaylistDict):
    def __init__(self, username: str, playlist_id: Union[str, int]):
        username = validate_pattern(username, datatype='username')
        playlist_id = validate_pattern(playlist_id, datatype='playlist_id')
        playlist_json = fetch_json(JSON_URL % (username, playlist_id))
        super().__init__(playlist_json)


class YMPlaylistURL(YMPlaylistCreds):
    def __init__(self, playlist_url: str):
        username, playlist_id = validate_pattern(playlist_url, datatype='playlist_url')
        super().__init__(username, playlist_id)


class YMPlaylistHTML(YMPlaylistCreds):
    def __init__(self, playlist_html: str):
        username, playlist_id = validate_pattern(playlist_html, datatype='playlist_html')
        super().__init__(username, playlist_id)


class YMPlaylistList(YMPlaylistBase):
    def __init__(self, track_list: List[str], username: Optional[str] = None, playlist_id: Optional[str] = None,
                 playlist_title: Optional[str] = None, artist_sep: str = ARTIST_SEP, entity_sep: str = ENTITY_SEP):
        tracks = self.__parse_track_list(track_list, artist_sep, entity_sep)
        super().__init__(username, playlist_id, playlist_title, tracks)

    @staticmethod
    def __parse_track_list(tracks_list: List[str], artist_sep: str, entity_sep: str) -> List[Track]:
        tracks = []
        for raw_track in tracks_list:
            if type(raw_track) is not str:
                continue
            track_entity = raw_track.strip().split(entity_sep)
            if len(track_entity) not in (2, 3):
                continue
            artists = [artist.strip() for artist in track_entity[0].split(artist_sep) if artist.strip()]
            track_title = track_entity[1].strip()
            album_title = track_entity[2].strip() if len(track_entity) == 3 else None
            if artists and track_title:
                tracks.append(Track(artists, track_title, album_title))
        return tracks


class YMPlaylistTXT(YMPlaylistList):
    def __init__(self, file_path: Union[Path, str] = TXT_FILE, username: Optional[str] = None,
                 playlist_id: Optional[str] = None, playlist_title: Optional[str] = None,
                 artist_sep: str = ARTIST_SEP, entity_sep: str = ENTITY_SEP):
        track_list = load_txt(Path(file_path))
        super().__init__(track_list, username, playlist_id, playlist_title, artist_sep, entity_sep)
