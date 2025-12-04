import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import numpy as np
import pandas as pd
import os
import argparse
from enum import Enum, auto


load_dotenv()
class term(Enum):
    SHORT = auto()
    MEDIUM = auto()
    LONG = auto()

    # Optional: add a __str__ method to make help messages cleaner (show names instead of the full <Enum> object)
    def __str__(self):
        return self.name.lower()

def main(output_folder, time_range):
    scope = "user-library-read user-top-read"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    os.makedirs(output_folder, exist_ok=True)

    got_all_artists = False
    offset = 0
    total_top_artists_in_frame = None
    artist_ids = []
    artist_genres = []
    while total_top_artists_in_frame is None or  len(artist_ids) < total_top_artists_in_frame:
        limit = 50
        if total_top_artists_in_frame is not None and total_top_artists_in_frame-len(artist_ids) < 50:
            limit = total_top_artists_in_frame-len(artist_ids)
        fetch = sp.current_user_top_artists(limit=limit, offset=offset, time_range=time_range)
        if total_top_artists_in_frame is None: 
            total_top_artists_in_frame = fetch["total"]
        for artist in fetch["items"]:
            artist_ids.append(artist["id"])
            artist_genres += artist["genres"]
        offset += len(fetch["items"])
    artist_genres = np.array(artist_genres)
    vals,counts = np.unique(artist_genres, return_counts=True)

    rows = zip(vals, counts)
    artist_genre_df = pd.DataFrame(rows,columns=["genre", "count"])

    artist_genre_df = artist_genre_df.sort_values(["count"], ascending=False)
    artist_genre_df.to_csv(os.path.join(output_folder,"artist_genre_info.csv"), index=False)

    artist_info = []
    for artist in artist_ids:
        info = sp.artist(artist)
        artist_info.append({"artist": info["name"], "popularity": info["popularity"], "genres": info["genres"]})
    artist_df = pd.DataFrame(artist_info)
    artist_df.to_csv(os.path.join(output_folder, "artist_info.csv"), index=False)

    got_all_songs = False
    offset = 0
    total_top_songs = None
    songs = []
    while total_top_songs is None or  len(songs) < total_top_songs:
        if total_top_songs is not None and total_top_songs-len(songs) < 50:
            limit = total_top_artists_in_frame-len(artist_ids)
        fetch = sp.current_user_top_tracks(limit=50, offset=offset, time_range=time_range)
        if total_top_songs is None:
            total_top_songs = fetch["total"]
        for item in fetch["items"]:
            song = {}
            song["song"] = item["name"]
            song["popularity"] = item["popularity"]
            song["artists"] = [a["name"] for a in item["artists"]]
            song["album"] = item["album"]["name"]
            songs.append(song)
        offset += len(fetch["items"])
    song_df = pd.DataFrame(songs)
    song_df.to_csv(os.path.join(output_folder, "song_info.csv"), index=False)

    album_counts = pd.read_csv(os.path.join(output_folder, "song_info.csv"), index_col=0)
    album_counts = album_counts.drop('popularity', axis=1).reset_index()
    counts = album_counts["album"].value_counts()
    album_counts = album_counts.groupby("album", sort=False).agg(lambda x: ', '.join(x.unique())).reset_index()
    album_counts = pd.merge(album_counts, counts, on='album')
    album_counts = album_counts.drop('song', axis=1)
    album_counts.to_csv(os.path.join(output_folder, "album_info.csv"), index=False)

if __name__ == "__main__":
     # 1. Create the ArgumentParser object
    parser = argparse.ArgumentParser(description="A simple spotify scraper.")

    # 2. Add arguments
    # Positional argument (required)
    parser.add_argument("output_folder", type=str, help="output folder for data")
    parser.add_argument("--term", 
                        type=term,                             # Converts input string to an Enum member
                        choices=list(term),                    # Restricts choices to valid Enum members
                        default=term.MEDIUM,
                        help="'short', 'medium', or 'long' term data scrape")

    # 3. Parse the arguments from the command line
    args = parser.parse_args()
    main(args.output_folder, time_range=f"{args.term}_term")
