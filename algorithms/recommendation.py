"""Recommendation engine: integrates BST, heap, and linked list.

Pipeline:
1. BST: find songs related to the playlist's dominant genre/artist
2. Filter: exclude songs already in the playlist (O(1) via _node_map)
3. Heap: score remaining candidates
4. Linked list: exclude the 10 most recently played songs
5. Return top 5
"""

from collections import Counter
from data_structures.heap import AutoplayQueue


def recommend(playlist, catalogue, top_n=5, now=0.0,
              max_likes=None, max_plays=None):
    """Generate song recommendations.

    Args:
        playlist: Playlist instance (the user's current list)
        catalogue: SongCatalogue instance (all available songs)
        top_n: number of recommendations to return
        now: current timestamp for recency normalization
        max_likes: max like count for normalization (auto-detected if None)
        max_plays: max play count for normalization (auto-detected if None)

    Returns a list of Song objects (at most top_n).
    """
    playlist_songs = list(playlist)
    if not playlist_songs:
        # If playlist is empty, recommend the most-liked songs from catalogue
        all_songs = catalogue.in_order_traversal()
        if not all_songs:
            return []
        if max_likes is None:
            max_likes = max((s.like_count for s in all_songs), default=1)
        if max_plays is None:
            max_plays = max((s.play_count for s in all_songs), default=1)
        heap = AutoplayQueue(max_likes=max_likes, max_plays=max_plays, now=now)
        heap.add_many(all_songs)
        results = []
        for _ in range(min(top_n, len(heap))):
            s = heap.next_autoplay()
            if s:
                results.append(s)
        return results

    # Step 1: Find dominant genre and artist from playlist
    genre_counts = Counter(s.genre for s in playlist_songs)
    artist_counts = Counter(s.artist for s in playlist_songs)
    dominant_genre = genre_counts.most_common(1)[0][0]
    dominant_artist = artist_counts.most_common(1)[0][0]

    # BST: find songs matching dominant genre or artist
    genre_matches = catalogue.find_by_genre(dominant_genre)
    artist_matches = catalogue.find_by_artist(dominant_artist)
    candidates = {}
    for s in genre_matches + artist_matches:
        candidates[s.song_id] = s

    # Step 2: Filter out songs already in the playlist (O(1) via _node_map)
    playlist_ids = set(playlist._node_map.keys())
    candidates = {sid: s for sid, s in candidates.items()
                  if sid not in playlist_ids}

    if not candidates:
        # Fallback: use all catalogue songs not in playlist
        all_songs = catalogue.in_order_traversal()
        for s in all_songs:
            if s.song_id not in playlist_ids:
                candidates[s.song_id] = s

    if not candidates:
        return []

    # Step 3: Score candidates using the heap scoring formula
    candidate_list = list(candidates.values())
    if max_likes is None:
        max_likes = max((s.like_count for s in candidate_list), default=1)
    if max_plays is None:
        max_plays = max((s.play_count for s in candidate_list), default=1)
    heap = AutoplayQueue(max_likes=max_likes, max_plays=max_plays, now=now,
                         favourite_genre=dominant_genre)
    heap.add_many(candidate_list)

    # Step 4: Exclude the 10 most recently played songs from the playlist
    recent_ids = set(s.song_id for s in playlist.recent_songs(10))

    # Step 5: Extract top_n, skipping recently played
    results = []
    while heap and len(results) < top_n:
        s = heap.next_autoplay()
        if s is None:
            break
        if s.song_id in recent_ids:
            continue
        results.append(s)

    # If we filtered too many, fill from remaining heap
    while heap and len(results) < top_n:
        s = heap.next_autoplay()
        if s:
            results.append(s)

    return results


def recommend_for_genre(playlist, catalogue, genre, top_n=5, now=0.0):
    """Recommend songs of a specific genre not already in the playlist."""
    playlist_ids = set(playlist._node_map.keys())
    candidates = [s for s in catalogue.find_by_genre(genre)
                  if s.song_id not in playlist_ids]
    if not candidates:
        return []
    max_likes = max((s.like_count for s in candidates), default=1)
    max_plays = max((s.play_count for s in candidates), default=1)
    heap = AutoplayQueue(max_likes=max_likes, max_plays=max_plays, now=now)
    heap.add_many(candidates)
    results = []
    while heap and len(results) < top_n:
        s = heap.next_autoplay()
        if s:
            results.append(s)
    return results
