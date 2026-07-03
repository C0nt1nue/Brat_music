"""Generate a CSV dataset of songs for the music streaming engine."""

import csv
import random
import os

from data_structures.song import Genre

GENRES = [g.name for g in Genre]

TITLE_POOL = [
    "Midnight Echo", "Velvet Storm", "Crimson Dawn", "Neon Pulse", "Golden Hour",
    "Electric Soul", "Whispering Wind", "Ocean Drive", "Starlight", "Broken Glass",
    "Summer Rain", "Lost Horizon", "Diamond Eyes", "Fading Light", "Wildfire",
    "Crystal Dreams", "Shadow Dance", "Electric Pulse", "Silent Thunder", "Paper Planes",
    "Gravity", "Ocean Eyes", "Neon Lights", "Crim Sky", "Dust to Gold",
    "Afterglow", "Moonlit Road", "Static Heart", "Burning Bridges", "Hollow Crown",
    "Solar Flare", "Midnight Run", "Paper Hearts", "Electric Sky", "Golden Age",
    "Lost Stars", "Gravity Falls", "Northern Lights", "Echoes", "Time Machine",
    "Riverside", "Blue Horizon", "Gravity Waves", "Honey", "Tidal Wave",
    "After the Rain", "Chasing Cars", "Sunrise Boulevard", "Paper Moon", "Electric Avenue",
]

ARTIST_POOL = [
    "The Wanderers", "Luna Park", "Echo Valley", "Midnight Syndicate", "Solar Flux",
    "Neon Tigers", "Crystal Method", "The Astronauts", "Velvet Crow", "Blue Horizon",
    "Storm Chasers", "Electric Sheep", "Paper Tigers", "Golden State", "Lost Boys",
    "Crimson Tide", "Shadow Company", "Diamond Dogs", "Wildfire Co", "Static Bloom",
    "The Nightwatch", "River Stones", "Mountain Sound", "Ocean Gate", "Northern Call",
    "Skyline Drive", "Moon River", "Star Catchers", "Dawn Patrol", "Echo Chamber",
]

ALBUM_POOL = [
    "Origins", "Horizons", "Echoes in Time", "Midnight Sessions", "Golden Era",
    "Lost and Found", "Breaking Dawn", "Static", "Aftermath", "Reverie",
    "Parallels", "Open Roads", "Wandering Souls", "The Collection", "Uncharted",
]


def generate_songs(count=25, seed=42):
    """Return a list of Song objects for the dataset."""
    from data_structures.song import Song
    rng = random.Random(seed)
    songs = []
    used_titles = set()
    for i in range(count):
        # Ensure unique-ish titles
        title = rng.choice(TITLE_POOL)
        while title in used_titles and len(used_titles) < len(TITLE_POOL):
            title = rng.choice(TITLE_POOL)
        used_titles.add(title)
        artist = rng.choice(ARTIST_POOL)
        album = rng.choice(ALBUM_POOL)
        genre = rng.choice(GENRES)
        duration = rng.randint(120, 360)
        play_count = rng.randint(0, 500)
        like_count = rng.randint(0, 200)
        last_played = rng.choice([0.0, 0.0, 0.0, float(rng.randint(1, 1000))])
        song = Song(
            song_id=f"song_{i+1:03d}",
            title=title,
            artist=artist,
            album=album,
            genre=genre,
            duration_seconds=duration,
            play_count=play_count,
            like_count=like_count,
            last_played=last_played,
        )
        songs.append(song)
    return songs


def generate_csv(filepath="songs_dataset.csv", count=25, seed=42):
    """Write a CSV file with *count* songs. Returns the filepath."""
    songs = generate_songs(count=count, seed=seed)
    fieldnames = [
        "song_id", "title", "artist", "album", "genre",
        "duration_seconds", "play_count", "like_count", "liked", "last_played",
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for song in songs:
            row = song.to_dict()
            row["genre"] = song.genre.name
            row["liked"] = str(song.liked)
            writer.writerow(row)
    return filepath


def generate_csv_to_dir(directory, filename="songs_dataset.csv", count=25, seed=42):
    """Generate CSV in a specific directory."""
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    return generate_csv(filepath, count=count, seed=seed)


if __name__ == "__main__":
    path = generate_csv("songs_dataset.csv", count=25)
    print(f"Generated {path}")
