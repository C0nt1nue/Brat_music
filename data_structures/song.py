"""Song entity and Genre enum for the music streaming engine."""

from enum import Enum, auto
from dataclasses import dataclass


class Genre(Enum):
    """Supported music genres."""
    ROCK = auto()
    POP = auto()
    JAZZ = auto()
    CLASSICAL = auto()
    HIP_HOP = auto()
    ELECTRONIC = auto()
    COUNTRY = auto()
    RNB = auto()
    METAL = auto()
    FOLK = auto()
    LATIN = auto()
    REGGAE = auto()
    BLUES = auto()
    INDIE = auto()

    @classmethod
    def from_string(cls, name):
        """Case-insensitive lookup; raises ValueError for unknown genres."""
        if isinstance(name, Genre):
            return name
        for member in cls:
            if member.name.lower() == name.strip().lower():
                return member
        raise ValueError(f"Unknown genre: {name}")

    def __str__(self):
        return self.name


@dataclass
class Song:
    """A single track in the catalogue.

    Comparison uses ``song_id`` for equality and ``title`` (case-insensitive)
    for ordering, which makes ``Song`` suitable as a BST key.
    """
    song_id: str
    title: str
    artist: str
    album: str
    genre: Genre
    duration_seconds: int = 0
    play_count: int = 0
    like_count: int = 0
    liked: bool = False
    last_played: float = 0.0  # epoch timestamp of last play; 0 = never

    def __post_init__(self):
        if not isinstance(self.genre, Genre):
            self.genre = Genre.from_string(self.genre)

    def __eq__(self, other):
        if not isinstance(other, Song):
            return NotImplemented
        return self.song_id == other.song_id

    def __lt__(self, other):
        if not isinstance(other, Song):
            return NotImplemented
        return self.title.lower() < other.title.lower()

    def __le__(self, other):
        if not isinstance(other, Song):
            return NotImplemented
        return self.title.lower() <= other.title.lower()

    def __gt__(self, other):
        if not isinstance(other, Song):
            return NotImplemented
        return self.title.lower() > other.title.lower()

    def __ge__(self, other):
        if not isinstance(other, Song):
            return NotImplemented
        return self.title.lower() >= other.title.lower()

    def __hash__(self):
        return hash(self.song_id)

    def __repr__(self):
        return f"Song({self.song_id!r}, {self.title!r}, {self.artist!r})"

    def to_dict(self):
        """Serialize to a plain dict for JSON responses."""
        return {
            "song_id": self.song_id,
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "genre": self.genre.name,
            "duration_seconds": self.duration_seconds,
            "play_count": self.play_count,
            "like_count": self.like_count,
            "liked": self.liked,
            "last_played": self.last_played,
        }

    @classmethod
    def from_dict(cls, d):
        """Build a Song from a plain dict (e.g. CSV row or JSON body)."""
        genre_val = d.get("genre")
        genre = Genre.from_string(genre_val) if genre_val is not None else Genre.ROCK
        return cls(
            song_id=d["song_id"],
            title=d["title"],
            artist=d.get("artist", "Unknown"),
            album=d.get("album", "Unknown"),
            genre=genre,
            duration_seconds=int(d.get("duration_seconds", 0)),
            play_count=int(d.get("play_count", 0)),
            like_count=int(d.get("like_count", 0)),
            liked=bool(d.get("liked", False)),
            last_played=float(d.get("last_played", 0.0)),
        )
