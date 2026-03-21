from typing import Optional, List, Tuple, Union
import spotipy as sp

from ymusic_spotify.config import (ACTIONS, CLIENT_ID, CLIENT_SECRET, FOUND_IDS, PROCESSED, NOT_ADDED,
                                   REDIRECT_URI, RESULTS, SCOPE, TIGORAWR, STATS_DIR)
from ymusic_spotify.exceptions import TrackNotFound, YMException
from ymusic_spotify.io import write_txt
from ymusic_spotify.playlist import (YMPlaylistURL, YMPlaylistCreds, YMPlaylistTXT,
                                     YMPlaylistJSON, YMPlaylistHTML, YMPlaylistBase)
from ymusic_spotify.search import SearchEngine
from ymusic_spotify.track import Track
from ymusic_spotify.validation import validate_actions_key


class PlaylistProcessor:
    def __init__(self, req_score: int = 5, default_action: int = 4, limit: int = 20, attempts: int = 1):
        self.spotify = None
        if all((CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)):
            try:
                auth_manager = sp.SpotifyOAuth(
                    client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI,
                    scope=SCOPE, cache_handler=sp.MemoryCacheHandler()
                )
                self.spotify = sp.Spotify(auth_manager=auth_manager)
                self.search_engine = SearchEngine(self.spotify, req_score, default_action, limit, attempts)
                self.user = None
            except:
                self.spotify = None

    def run(self) -> None:
        print(TIGORAWR)
        while True:
            ym_playlist = self._get_playlist_from_user()
            if ym_playlist is None:
                break
            if not isinstance(ym_playlist, YMPlaylistTXT):
                if input('\nDo you want to save playlist in TXT file? [Y/N] ').strip().upper() == 'Y':
                    ym_playlist.save_to_txt()
            if input('\nDo you want to create playlist on Spotify? [Y/N] ').strip().upper() != 'Y':
                break
            if self.spotify is None:
                print('\nSpecify valid Spotify Credentials in .env file and try again')
                break
            self._configure_search()
            while self.user is None:
                self.user = self.spotify.me()
            found_ids, processed, not_added = self._process_playlist(ym_playlist)
            self._save_stats(found_ids, processed, not_added)
            self._create_spotify_playlist(found_ids)
            if input('\nDo you want to repeat? [Y/N] ').strip().upper() != 'Y':
                break
        print('\nRRRAAAWWWRRR!')
        return None

    def _configure_search(self) -> None:
        if input('\nDo you what to specify parameters for track search? [Y/N] ').strip().upper() != 'Y':
            return None
        print('\nSpecify required matching score to automatically add track to playlist')
        print('\t[1-4]   Titles: same / similar, Artists: same / similar, Albums: different')
        print('\t[5-10]  Titles: similar, Artists: same / similar, Albums: similar / unknown / same')
        print('\t[11-16] Titles: same, Artists: same, Albums: similar / unknown / same')
        req_score = input('\nEnter choice: ').strip()
        if req_score.isdigit() and (req_score := int(req_score)) in range(1, 17):
            self.search_engine.req_score = req_score
        print('\nSpecify amount of tracks in search result [1-25]')
        limit = input(f'\nEnter choice: ').strip()
        if limit.isdigit() and (limit := int(limit)) in range(1, 26):
            self.search_engine.limit = limit
        print('\nSpecify action for tracks which matching score is lower than required:')
        print('\t[0] Skip the track (do not add to playlist)')
        print('\t[1] Add the track with the best matching score')
        print('\t[2] Add the first track in search results')
        print('\t[4] Ask action for each track')
        default_action = input(f'\nEnter choice: ').strip()
        if default_action.isdigit() and (default_action := int(default_action)) in range(3):
            self.search_engine.default_action = default_action
        return None

    @staticmethod
    def _format_actions_line(key: int, track: Optional[Track] = None, key_type: Optional[str] = None) -> str:
        key_type = key_type if key_type in ('ANSW', 'DONE') else str(key)
        prefix = f'[{key_type}] '.rjust(7)
        suffix = f': {track or ""}' if track or key_type == 'ANSW' else ''
        return prefix + ACTIONS[key] + suffix

    def _choose_action(self, key: Optional[int] = None, tracks: Tuple[Optional[Track], ...] = (None,) * 5) -> int:
        if key in range(3):
            return key
        for i in range(5):
            if i != key:
                print(self._format_actions_line(i, tracks[i] if key != 3 else None))
        new_key = validate_actions_key(input(self._format_actions_line(key, key_type='ANSW')), range_limit=key)
        if key == 3:
            self.search_engine.default_action = new_key
        return self._choose_action(new_key, tracks)

    def _process_track(self, track: Track) -> Tuple[int, Optional[Track]]:
        """Process a single track and find Spotify match"""
        action = -1
        best_match = None
        best_score = 0
        try:
            spotify_results = self.search_engine.search(track)
            best_score, best_match, first_result = self.search_engine.get_best_match(track, spotify_results)
            if best_score < self.search_engine.req_score:
                action = self._choose_action(self.search_engine.default_action,
                                             (track, best_match, first_result, None, None))
                if action == 2:
                    best_match = first_result
                elif action == 0:
                    best_match = None
        except TrackNotFound:
            pass
        except YMException:
            raise
        except Exception as e:
            raise YMException(f'An error occurred while processing track {track}', e)
        finally:
            if best_match:
                print(f'[DONE] {best_match} [Score: {best_score}]')
            else:
                print(f'[FAIL] {track}')
            return action, best_match

    def _process_playlist(self, ym_playlist: Union[YMPlaylistBase]) -> Tuple[list, ...]:
        found_ids, processed, not_added = [], [], []
        for track in ym_playlist['tracks']:
            try:
                action, best_match = self._process_track(track)
                if best_match:
                    found_ids.append(best_match.id)
                else:
                    not_added.append(track)
                if action > -1:
                    processed.append((track, action, best_match))
            except Exception as e:
                print(e)
        print(f'All tracks has been processed')
        return found_ids, processed, not_added

    @staticmethod
    def _get_playlist_from_user() -> Optional[Union[YMPlaylistBase]]:
        input_methods = ['username and playlist ID (sep. with space)',
                         'playlist URL', 'playlist HTML',
                         'path to TXT file', 'path to JSON file']
        playlist_collectors = [YMPlaylistCreds, YMPlaylistURL, YMPlaylistHTML, YMPlaylistTXT, YMPlaylistJSON]
        print('\nSelect input method for collecting YMusic playlist data:')
        for i, input_method in enumerate(input_methods):
            print(f'\t[{i}] {input_method[0].upper() + input_method[1:]}')
        choice = input('\nEnter choice: ').strip()
        if not choice.isdigit():
            return None
        choice = int(choice)
        if choice not in range(len(input_methods)):
            return None
        input_data = input(f'\nEnter {input_methods[choice]}: ').strip()
        if not input_data:
            return None
        if playlist_collectors[choice] is not YMPlaylistCreds:
            return playlist_collectors[choice](input_data)
        input_data = input_data.split()
        if len(input_data) == 2:
            return YMPlaylistCreds(*input_data)
        return None

    @staticmethod
    def _save_stats(found_ids: List[str], processed: List[Tuple[Track, int, Optional[Track]]], not_added: List[Track]) -> None:
        print(f'\nMatching tracks: {len(found_ids)}')
        print(f'Processed tracks: {len(processed)}')
        print(f'Tracks not added: {len(not_added)}')
        if not input('\nSave stats to TXT files? [Y/N] ').upper() == 'Y':
            return None
        try:
            write_txt(FOUND_IDS, '\n'.join(found_ids))
            write_txt(PROCESSED, '\n'.join([f'{ym_track}\n{ACTIONS[action]}\n{spotify_track or "N/A"}\n'
                                            for ym_track, action, spotify_track in processed]))
            write_txt(NOT_ADDED, '\n'.join([str(ym_track) for ym_track in not_added]))
            print(f"\nStats has been saved to directory '{STATS_DIR}'")
        except Exception as e:
            print(e)
        return None

    def _create_spotify_playlist(self, found_ids: List[str]) -> None:
        playlist_title = input('\nEnter title for playlist to create on Spotify: ').strip() or 'new playlist'
        playlist_id = self.spotify.user_playlist_create(self.user['id'], name=playlist_title)['id']
        for i in range(0, len(found_ids), 100):
            self.spotify.playlist_add_items(playlist_id, found_ids[i:i + 100])
        print(f"Playlist '{playlist_title}' has been created successfully")
        return None
