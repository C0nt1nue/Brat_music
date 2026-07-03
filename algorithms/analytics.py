"""Playlist analytics: statistics computed by traversing the linked list."""

from collections import Counter


def playlist_stats(playlist):
    """Compute aggregate statistics for a Playlist.

    Traverses the linked list once (O(n)) and returns a dict with:
    total_songs, total_duration, avg_duration, genre_distribution,
    top_artists, total_plays, total_likes.
    """
    songs = list(playlist)
    if not songs:
        return {
            "total_songs": 0,
            "total_duration": 0,
            "avg_duration": 0,
            "genre_distribution": {},
            "top_artists": [],
            "total_plays": 0,
            "total_likes": 0,
        }
    total_duration = sum(s.duration_seconds for s in songs)
    genre_counts = Counter(s.genre.name for s in songs)
    artist_counts = Counter(s.artist for s in songs)
    total_plays = sum(s.play_count for s in songs)
    total_likes = sum(s.like_count for s in songs)
    return {
        "total_songs": len(songs),
        "total_duration": total_duration,
        "avg_duration": round(total_duration / len(songs), 1),
        "genre_distribution": dict(genre_counts),
        "top_artists": artist_counts.most_common(5),
        "total_plays": total_plays,
        "total_likes": total_likes,
    }


def top_genres(playlist, n=3):
    """Return the top *n* genres by count as (genre, count) pairs."""
    counter = Counter(s.genre.name for s in playlist)
    return counter.most_common(n)


def top_artists(playlist, n=3):
    """Return the top *n* artists by song count."""
    counter = Counter(s.artist for s in playlist)
    return counter.most_common(n)


def average_duration(playlist):
    """Return the average duration in seconds (0 if empty)."""
    songs = list(playlist)
    if not songs:
        return 0
    return sum(s.duration_seconds for s in songs) / len(songs)


def dominant_genre(playlist):
    """Return the most common genre name, or None if playlist is empty."""
    counter = Counter(s.genre.name for s in playlist)
    if not counter:
        return None
    return counter.most_common(1)[0][0]


def artist_diversity(playlist):
    """Return the number of distinct artists in the playlist."""
    return len(set(s.artist for s in playlist))


def genre_diversity(playlist):
    """Return the number of distinct genres in the playlist."""
    return len(set(s.genre.name for s in playlist))
