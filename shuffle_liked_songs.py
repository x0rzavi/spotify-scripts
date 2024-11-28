"""
Shuffle Spotify Liked Songs into a Playlist
"""

import os
import random

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

scope = "playlist-read-private playlist-modify-private user-library-read"
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
auth_manager = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    open_browser=False,
)
sp = spotipy.Spotify(auth_manager=auth_manager)


def new_playlist():
    playlists = sp.current_user_playlists()
    for playlist in playlists["items"]:
        if "Liked Songs Playlist" in playlist["name"]:
            sp.current_user_unfollow_playlist(playlist["id"])
            break
    playlist_name = "Liked Songs Playlist"
    playlist_description = "A playlist of liked songs"
    playlist = sp.user_playlist_create(
        user_id, playlist_name, public=False, description=playlist_description
    )
    return playlist["id"]


user_id = sp.me()["id"]
playlist_id = new_playlist()


def get_tracks_uri(songs_list):
    tracks_list = []
    while True:
        for item in songs_list["items"]:
            track = item["track"]
            track_uri = track["uri"]
            tracks_list.append(track_uri)
        if songs_list["next"]:
            songs_list = sp.next(songs_list)
        else:
            break
    return tracks_list


liked_songs_uris = get_tracks_uri(sp.current_user_saved_tracks())
print(f"Shuffling {len(liked_songs_uris)} songs into new playlist!")
random.shuffle(liked_songs_uris)
for i in range(0, len(liked_songs_uris), 100):
    sp.user_playlist_add_tracks(user_id, playlist_id, liked_songs_uris[i : i + 100])
