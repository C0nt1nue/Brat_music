"""Load a CSV dataset into the three core data structures."""

import csv
import os

from data_structures.song import Song, Genre
from data_structures.doubly_linked_list import Playlist
from data_structures.bst import SongCatalogue
from data_structures.heap import AutoplayQueue


def load_songs_from_csv(filepath):
    """Read a CSV file and return a list of Song objects."""
    songs = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["liked"] = row.get("liked", "False").strip().lower() in ("true", "1", "yes")
            songs.append(Song.from_dict(row))
    return songs


def load_into_all_structures(filepath):
    """Load a CSV into Playlist, SongCatalogue, and AutoplayQueue.

    Returns a tuple (playlist, catalogue, autoplay_queue, songs).
    """
    songs = load_songs_from_csv(filepath)
    playlist = Playlist()
    catalogue = SongCatalogue()
    max_likes = max((s.like_count for s in songs), default=1)
    max_plays = max((s.play_count for s in songs), default=1)
    now = max((s.last_played for s in songs), default=0.0)
    autoplay = AutoplayQueue(max_likes=max_likes, max_plays=max_plays, now=now)
    for song in songs:
        playlist.add_song(song)
        catalogue.insert(song)
        autoplay.add_to_autoplay(song)
    return playlist, catalogue, autoplay, songs


def load_catalogue_only(filepath):
    """Load a CSV into a SongCatalogue only."""
    songs = load_songs_from_csv(filepath)
    catalogue = SongCatalogue()
    for song in songs:
        catalogue.insert(song)
    return catalogue, songs


def load_playlist_only(filepath):
    """Load a CSV into a Playlist only."""
    songs = load_songs_from_csv(filepath)
    playlist = Playlist()
    for song in songs:
        playlist.add_song(song)
    return playlist, songs


def load_autoplay_only(filepath):
    """Load a CSV into an AutoplayQueue only."""
    songs = load_songs_from_csv(filepath)
    max_likes = max((s.like_count for s in songs), default=1)
    max_plays = max((s.play_count for s in songs), default=1)
    now = max((s.last_played for s in songs), default=0.0)
    autoplay = AutoplayQueue(max_likes=max_likes, max_plays=max_plays, now=now)
    for song in songs:
        autoplay.add_to_autoplay(song)
    return autoplay, songs


def ensure_dataset(filepath="songs_dataset.csv", count=25, seed=42):
    """Generate the CSV if it doesn't exist, then return the path."""
    if not os.path.exists(filepath):
        from data.csv_generator import generate_csv
        generate_csv(filepath, count=count, seed=seed)
    return filepath
