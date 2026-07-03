"""Smart shuffle: constrained permutation that avoids back-to-back repeats.

Uses a greedy approach: at each step, pick a random candidate that doesn't
match the previous artist/genre. Falls back to best-effort when degenerate.
"""

import random
from collections import Counter


def smart_shuffle(playlist, rng=None):
    """Reorder the playlist in-place to minimize consecutive duplicates.

    Constraints (best-effort):
    - No two consecutive songs share the same artist (when possible)
    - No two consecutive songs share the same genre (when possible)

    Detects degenerate cases (e.g. single artist > 50% of playlist) and
    issues a warning string instead of failing.

    Returns (shuffled_order, warning) where shuffled_order is a list of
    Song objects and warning is None or a string.
    """
    rng = rng or random.Random()
    songs = list(playlist)
    if len(songs) <= 1:
        return songs, None

    # Degeneration check: single artist exceeds 50%
    artist_counts = Counter(s.artist for s in songs)
    dominant_artist, dominant_count = artist_counts.most_common(1)[0]
    warning = None
    if dominant_count > len(songs) * 0.5:
        warning = (f"Degenerate case: artist '{dominant_artist}' appears "
                   f"{dominant_count}/{len(songs)} times (>50%). "
                   f"Back-to-back repeats unavoidable.")

    result = []
    remaining = list(songs)
    rng.shuffle(remaining)

    # Group by artist for efficient candidate selection
    prev_artist = None
    prev_genre = None

    while remaining:
        # Try to find a candidate that differs in both artist and genre
        best = None
        best_idx = -1
        for i, song in enumerate(remaining):
            if song.artist != prev_artist and song.genre != prev_genre:
                best = song
                best_idx = i
                break
        if best is None:
            # Relax: differ in artist only
            for i, song in enumerate(remaining):
                if song.artist != prev_artist:
                    best = song
                    best_idx = i
                    break
        if best is None:
            # Relax: differ in genre only
            for i, song in enumerate(remaining):
                if song.genre != prev_genre:
                    best = song
                    best_idx = i
                    break
        if best is None:
            # Fully degenerate: take the first
            best = remaining[0]
            best_idx = 0

        result.append(best)
        prev_artist = best.artist
        prev_genre = best.genre
        remaining.pop(best_idx)

    # Apply to playlist
    nodes = playlist._to_list()
    song_to_node = {}
    for node in nodes:
        song_to_node[node.song.song_id] = node
    ordered_nodes = [song_to_node[s.song_id] for s in result]
    playlist._relink(ordered_nodes)

    return result, warning


def has_consecutive_duplicates(song_list, attribute="artist"):
    """Check if a list of songs has consecutive same-attribute entries."""
    for i in range(1, len(song_list)):
        if getattr(song_list[i], attribute) == getattr(song_list[i - 1], attribute):
            return True
    return False


def consecutive_duplicate_count(song_list, attribute="artist"):
    """Count the number of consecutive same-attribute pairs."""
    count = 0
    for i in range(1, len(song_list)):
        if getattr(song_list[i], attribute) == getattr(song_list[i - 1], attribute):
            count += 1
    return count
