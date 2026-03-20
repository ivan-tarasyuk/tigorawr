import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    load_dotenv = None


CLIENT_ID = os.getenv('CLIENT_ID', '')
CLIENT_SECRET = os.getenv('CLIENT_SECRET', '')
REDIRECT_URI = os.getenv('REDIRECT_URI', '')
SCOPE = ['user-library-read', 'playlist-modify-public']

TRACK_ATTRS = ['artists', 'track_title', 'album_title', 'album_date', 'track_id']

ENTITY_SEP = ' --- '
ARTIST_SEP = '; '

JSON_URL = 'https://music.yandex.ru/handlers/playlist.jsx?owner=%s&kinds=%s'
BASE_DIR = Path(__file__).resolve().parent.parent
JSON_FILE = BASE_DIR / f'playlist.json'
TXT_FILE = BASE_DIR / f'playlist.txt'
RESULTS = BASE_DIR / 'results'
STATS_DIR = BASE_DIR / 'stats'
FOUND_IDS = STATS_DIR / 'found_ids.txt'
PROCESSED = STATS_DIR / 'processed.txt'
NOT_ADDED = STATS_DIR / 'not_added.txt'

USERNAME_PATTERN = r'([a-zA-Z][a-zA-Z0-9.-]{0,29}[a-zA-Z0-9])'
PLAYLIST_ID_PATTERN = r'(\d+)'
PLAYLIST_URL_PATTERN = rf'https://music\.yandex\.ru/users/{USERNAME_PATTERN}/playlists/{PLAYLIST_ID_PATTERN}'
PLAYLIST_HTML_PATTERN = rf'src="https://music\.yandex\.ru/iframe/playlist/{USERNAME_PATTERN}/{PLAYLIST_ID_PATTERN}"'


PATTERNS = {
    'username': USERNAME_PATTERN,
    'playlist_id': PLAYLIST_ID_PATTERN,
    'playlist_url': PLAYLIST_URL_PATTERN,
    'playlist_html': PLAYLIST_HTML_PATTERN,
}

FORBIDDEN_TYPES_PATTERN = r'(?!single|compilation).*'
FORBIDDEN_WORDS_PATTERN = r'^(?!.*(?:{})).*$'
FORBIDDEN_WORDS = [
    r'\d{1}0s', r"\d{1}0's", r'19\d{2}', r'20\d{2}', r'best of', r'the best', r'boxset',
    r'collection', r'greatest', r'hits of', r'live', r'remix', r'single', r'years'
    ]

CHARS_TO_REMOVE = r'/|&;:,.\'"()[]{}'
TRANSLATION = str.maketrans('', '', CHARS_TO_REMOVE)

ACTIONS = [
    'Skip the track',
    'Add best match',
    'Add top result',
    'Specify default action',
    'Specify required action',
    'Specify path to JSON file with YM playlist',
    'Specify '
]
BASE_ACTIONS = (0, 1, 2)

TIGORAWR = r'''
 888   d8b                                                 
 888   Y8P                                                 
 888                                                       
 888888888 .d88b.  .d88b. 888d888d88b. 888  888  888888d888
 888   888d88P"88bd8P Y88b888P"    Y88b888  888  888888P"  
 888   888888  888888  888888 .d888b888888  888  888888    
 Y88b. 888Y88b 888Y8b.d88Y888 Y88b. 888Y88b.888.d888888    
  "Y888888 "Y88888 "Y88Y" 888  "Y88Y888 "Y888YY888Y"888    
               888                                         
          Y8b d88P                                         
           "Y88P"                                          
App to extract Yandex Music playlist and create it on Spotify'''
