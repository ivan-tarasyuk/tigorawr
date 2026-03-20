# T I G O R A W R

### YMusic to Spotify Playlist Transfer Tool

---

## Overview
This application extracts playlist from Yandex Music and creates it on Spotify. It supports multiple input formats, track matching with configurable parameters, and detailed statistics export.
**Note:** Requires Spotify Developer API credentials (see [Configuration](#configuration))

---

## Features
- Import playlists from Yandex Music (username + playlist ID, URL, HTML, JSON, TXT )
- Track matching with configurable scoring system
- Interactive handling of low-confidence matches
- Create Spotify playlists with matched tracks
- Export detailed matching statistics

---

## Prerequisites
- Python 3.7+
- Spotify account
- [Spotify Developer Application](https://developer.spotify.com/dashboard/) credentials

---

## Installation
```bash
git clone https://github.com/yourusername/tigorgorawr.git
cd tigorgorawr
pip install -r requirements.txt
```
**Required packages:** `spotipy>=2.23.0`, `requests>=2.31.0`, `python-dotenv>=1.2.2`

---

## Configuration
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Create a new app and get **Client ID**, **Client Secret** and **Redirect URI**
3. Create `.env` file in the project root and add your Spotify credentials:

```python
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
REDIRECT_URI = 'http://localhost:8888/callback'
```

---

## Input Methods
The application accepts one of five possible input formats when prompted:
- **Username and Playlist ID** - Format: `tigorawr 666`
- **Playlist URL** - Direct link: `https://music.yandex.ru/users/tigorawr/playlists/666`
- **Playlist HTML** - Iframe embed code from Yandex Music (the simplest way)
- **Path to TXT File** - TXT file with tracks in format: `Artist1; Artist2; ... --- Track` or `Artist1; Artist2; ... --- Track --- Album`
- **Path to JSON File** - JSON file format downloaded from: `https://music.yandex.ru/handlers/playlist.jsx?owner=tigorawr&kinds=666`

---

## Parameters
**`req_score`** (1-16, default: 5) - Minimum matching score for automatic track addition. Lower values (5-7) are faster but less strict, higher values (13-16) ensure exact matches. Recommended: 10-12 for balanced results.

**`limit`** (1-25, default: 20) - Number of Spotify search results to evaluate per track. Lower is faster, higher is more thorough.

**`attempts`** (default: 1) - Number of search retries per track.

**`default_action`** (default: 4) - What to do when match score is below threshold:
- `0` - Skip track
- `1` - Add best match
- `2` - Add first result  
- `4` - Ask user to confirm each track

---

## Output
Once all tracks have been processed, the user specifies the name of the target Spotify playlist, and the application creates it using the tracks that were found and accepted.
In addition, the application can export matching results into four separate TXT files:
- **`results/playlist.txt`** - Normalized Yandex Music playlist (can be used to create Spotify playlist later)
- **`stats/found_ids.txt`** - IDs of the tracks successfully found on Spotify.
- **`stats/processed.txt`** - Tracks that were handled in some way, including both skipped and added tracks.
- **`stats/not_added.txt`** - Tracks that were not included in the final Spotify playlist.

---

## Project Structure
```
tigorawr/
├── .env                      # Spotify credentials (configure this!)
├── app.py                    # Entry point
├── requirements.txt          # Dependencies
└── ymusic_spotify/
    ├── config.py             # Constants
    ├── processor.py          # Main logic
    ├── playlist.py           # Playlist parsers
    ├── search.py             # Matching engine
    ├── track.py              # Track model
    └── utils.py              # Helpers
```
---