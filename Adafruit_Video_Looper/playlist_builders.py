import os
import re
import urllib.parse

from .model import Playlist, Movie


def build_playlist_m3u(playlist_path: str):
    playlist_dirname = os.path.dirname(playlist_path)
    movies = []

    title = None

    with open(playlist_path) as f:
        for line in f:
            if line.startswith('#'):
                if line.startswith('#EXTINF'):
                    matches = re.match(r'^#\w+:\d+(?:\s*\w+\=\".*\")*,(.*)$', line)
                    if matches:
                        title = matches[1]
            else:
                path = urllib.parse.unquote(line.rstrip())
                if not os.path.isabs(path):
                    path = os.path.join(playlist_dirname, path)
                movies.append(Movie(path, title))
                title = None

    return Playlist(movies)
