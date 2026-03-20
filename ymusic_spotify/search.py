from typing import Iterator

import spotipy as sp

from ymusic_spotify.exceptions import TrackNotFound, NoResponse
from ymusic_spotify.track import Track


class SearchEngine:
    def __init__(self, spotify: sp.Spotify, req_score: int = 5, default_action: int = 4, limit: int = 20, attempts: int = 1):
        """Class for Spotify track search configuration.

        Attributes:
            req_score: Minimum matching score required to accept a track
            limit: Maximum number of results returned by Spotify search
            attempts: Number of retry attempts for Spotify API requests
            default_action: Default action index used when match score is below req_score
        """
        self.spotify = spotify
        self.req_score = req_score
        self.default_action = default_action
        self.limit = limit
        self.attempts = attempts

    def search(self, ym_track: Track, simplify: bool = False) -> Iterator:
        """Perform track search using Spotify API"""
        query = ym_track.format_query(simplify)
        for _ in range(self.attempts):
            response = self.spotify.search(q=query, type='track', limit=self.limit)
            if not response:
                continue
            spotify_results = response['tracks']['items']
            if spotify_results:
                return iter(spotify_results)
            if not simplify:
                return self.search(ym_track, simplify=True)
            raise TrackNotFound(track=ym_track)
        raise NoResponse(track=ym_track)

    def get_best_match(self, ym_track: Track, spotify_results: Iterator) -> tuple:
        """Select best matching track from Spotify search results

        Scoring:
            0 - different tracks
            1-4 - similar or same title and artists, but different albums
            5-10 - similar titles, similar or same artists, similar/unknown/same albums
            11-16 - same titles and artists, similar/unknown/same albums
        """
        item = next(spotify_results, None)
        if item is None:
            raise TrackNotFound(track=ym_track)
        first_result = best_match = Track.from_spotify(item)
        best_score = ym_track.rate_match(first_result)
        if best_score < self.req_score:
            for item in spotify_results:
                spotify_track = Track.from_spotify(item)
                score = ym_track.rate_match(spotify_track)
                if score > best_score:
                    best_score, best_match = score, spotify_track
                    if best_score >= self.req_score:
                        break
        return best_score, best_match, first_result
