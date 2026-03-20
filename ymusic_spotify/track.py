import re
from typing import List, Optional, Callable

from ymusic_spotify import utils
from ymusic_spotify.config import (ARTIST_SEP, ENTITY_SEP, TRANSLATION,
                                   FORBIDDEN_WORDS, FORBIDDEN_TYPES_PATTERN, FORBIDDEN_WORDS_PATTERN)
from ymusic_spotify.exceptions import InvalidDataStructure


class Track:
    """Class for creating a track instance after validation"""
    def __new__(cls, artists: List[str], title: str, *args, **kwargs):
        __valid_artists = utils.validate_list_items(artists)
        __valid_title = utils.validate_str(title)
        if not __valid_artists or not __valid_title:
            return None

        instance = super().__new__(cls)
        instance.__valid_artists = __valid_artists
        instance.__valid_track_title = __valid_title
        return instance

    def __init__(self, artists: List[str], title: str, album: Optional[str] = None, _id: Optional[str] = None):
        self.artists = self.__valid_artists
        self.title = self.__valid_track_title
        self.album = utils.validate_str(album)
        self.id = utils.validate_str(_id)
        delattr(self, f'_{self.__class__.__name__}__valid_artists')
        delattr(self, f'_{self.__class__.__name__}__valid_track_title')

        self._matching_title = None
        self._matching_artists = None
        self._matching_album = None
        self._search_title = None
        self._search_artists = None
        self._search_album = None

    @staticmethod
    def factory(func: Callable):
        """Decorator for safe Track instance creation from JSON"""
        def wrapper(cls, item: Optional[dict]):
            if item is None:
                return None
            try:
                return func(cls, item)
            except Exception as e:
                raise InvalidDataStructure(f'JSON has an invalid format', e)
        return wrapper

    @classmethod
    @factory
    def from_ymusic(cls, item: Optional[dict]):
        """Creates Track instance from YMusic JSON item"""
        return cls(artists=[artist['name'] for artist in item['artists']],
                   title=item['title'],
                   album=next((album['title'] for album in item['albums'] if album.get('type') is None), None))

    @classmethod
    @factory
    def from_spotify(cls, item: Optional[dict]):
        """Creates Track instance from Spotify JSON item"""
        return cls(artists=[artist['name'] for artist in item['artists']],
                   title=item['name'],
                   album=item['album']['name'],
                   _id=item['id'])

    def is_studio_album(self, album_type: str) -> bool:
        if not re.fullmatch(pattern=FORBIDDEN_TYPES_PATTERN, string=album_type or ''):
            return False
        album_pattern = re.compile(pattern=FORBIDDEN_WORDS_PATTERN.format('|'.join(FORBIDDEN_WORDS)), flags=re.IGNORECASE)
        return bool(album_pattern.match(self.album or ''))

    def __getitem__(self, item: str):
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(f"Attribute '{item}' not found")

    def __bool__(self):
        return all([self.artists, self.title])

    def __repr__(self):
        line = [ARTIST_SEP.join(self.artists), self.title]
        if self.album:
            line.append(self.album)
        return ENTITY_SEP.join(line)

    def __iter__(self):
        return iter(self.__dict__.items())

    def _normalize_attr(self, attr: str, func: Callable):
        """Normalizes Track attribute using specified function (see below)"""
        value = getattr(self, attr)
        if value is None:
            value = func()
            setattr(self, attr, value)
        return value

    @property
    def matching_title(self) -> str:
        return self._normalize_attr('_matching_title',
                                    lambda: self.title.lower())

    @property
    def matching_artists(self) -> set:
        return self._normalize_attr('_matching_artists',
                                    lambda: {artist.lower() for artist in self.artists})

    @property
    def matching_album(self) -> str:
        return self._normalize_attr('_matching_album',
                                    lambda: self.album.lower())

    def _match_title(self, other: 'Track') -> int:
        return utils.match_str(self.matching_title, other.matching_title, a=8, b=2, c=0)

    def _match_artists(self, other: 'Track') -> int:
        return utils.match_set(self.matching_artists, other.matching_artists, a=4, b=1)

    def _match_album(self, other: 'Track') -> int:
        return utils.match_str(self.matching_album, other.matching_album, a=4, b=3, c=2)

    def rate_match(self, other: 'Track') -> int:
        """Return overall similarity score between two tracks"""
        if not isinstance(other, Track):
            return 0
        if not (title_score := self._match_title(other)):
            return 0
        if not (artists_score := self._match_artists(other)):
            return 0
        if album_score := self._match_album(other):
            return title_score + artists_score + album_score
        return (title_score + artists_score) // 3

    @property
    def search_title(self) -> str:
        return self._normalize_attr('_search_title',
                                    lambda: self.matching_title.partition('feat')[0].strip().translate(TRANSLATION))

    @property
    def search_artists(self) -> list:
        return self._normalize_attr('_search_artists',
                                    lambda: [artist.lower().translate(TRANSLATION) for artist in self.artists])

    @property
    def search_album(self) -> str:
        return self._normalize_attr('_search_album',
                                    lambda: self.matching_album.translate(TRANSLATION))

    def format_query(self, simplify: bool = False) -> str:
        """Formats search query string"""
        query = 'track:"%s" artist:"%s"'
        if simplify:
            return query % (self.search_title.split()[0], self.search_artists[0])
        query += ' album:"%s"' if self.search_album else '%s'
        return query % (self.search_title, ', '.join(self.search_artists), self.search_album or '')
