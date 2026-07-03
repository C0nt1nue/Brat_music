"""Max-heap for the autoplay queue, with lazy deletion.

Songs are scored by a weighted formula combining likes, play count,
recency, and a genre bonus. Removals are lazy (marked in a set) so
they stay O(1); stale entries are skipped during ``next_autoplay``.

The heap is implemented **from scratch** (no ``heapq``) as an
array-based binary max-heap with manual ``_sift_up`` / ``_sift_down``.
"""

import itertools


class MaxHeap:
    """A binary max-heap built from scratch.

    Stores entries as ``(score, counter, song_id, song)`` tuples in a
    flat list.  The children of index *i* live at ``2*i+1`` and
    ``2*i+2``; the parent of *i* is at ``(i-1)//2``.

    Ordering: **higher** score has higher priority (root = best).
    Ties are broken by lower counter (FIFO among equal scores).
    """

    def __init__(self):
        self._data = []

    def __len__(self):
        return len(self._data)

    def __bool__(self):
        return len(self._data) > 0

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, index):
        return self._data[index]

    # -- index helpers ----------------------------------------------------

    @staticmethod
    def _parent(i):
        return (i - 1) // 2

    @staticmethod
    def _left(i):
        return 2 * i + 1

    @staticmethod
    def _right(i):
        return 2 * i + 2

    # -- comparison -------------------------------------------------------

    def _better(self, i, j):
        """True if element at *i* outranks element at *j*.

        Max-heap: higher score wins; on a tie, lower counter wins.
        """
        a, b = self._data[i], self._data[j]
        if a[0] != b[0]:
            return a[0] > b[0]
        return a[1] < b[1]

    # -- core operations --------------------------------------------------

    def _sift_up(self, i):
        """Bubble the element at *i* upward toward the root."""
        while i > 0:
            parent = self._parent(i)
            if self._better(i, parent):
                self._data[i], self._data[parent] = self._data[parent], self._data[i]
                i = parent
            else:
                break

    def _sift_down(self, i):
        """Bubble the element at *i* downward toward the leaves."""
        n = len(self._data)
        while True:
            left = self._left(i)
            right = self._right(i)
            best = i
            if left < n and self._better(left, best):
                best = left
            if right < n and self._better(right, best):
                best = right
            if best == i:
                break
            self._data[i], self._data[best] = self._data[best], self._data[i]
            i = best

    def push(self, entry):
        """Insert *entry* into the heap.  O(log n)."""
        self._data.append(entry)
        self._sift_up(len(self._data) - 1)

    def pop(self):
        """Remove and return the top (highest-priority) entry.  O(log n)."""
        if not self._data:
            raise IndexError("pop from empty heap")
        top = self._data[0]
        last = self._data.pop()
        if self._data:
            self._data[0] = last
            self._sift_down(0)
        return top

    def peek(self):
        """Return the top entry without removing it."""
        if not self._data:
            raise IndexError("peek from empty heap")
        return self._data[0]

    def clear(self):
        self._data.clear()


class AutoplayQueue:
    """A max-heap of songs prioritised by an autoplay score.

    Uses the hand-written :class:`MaxHeap` instead of ``heapq``.
    Lazy deletion: removed song_ids are tracked in ``_removed`` and
    skipped during ``next_autoplay``.
    """

    def __init__(self, max_likes=1, max_plays=1, now=0.0, favourite_genre=None):
        self._heap = MaxHeap()  # entries: (score, counter, song_id, song)
        self._counter = itertools.count()
        self._removed = set()
        self._active_ids = set()
        self._scores = {}
        self.max_likes = max(max_likes, 1)
        self.max_plays = max(max_plays, 1)
        self.now = now
        self.favourite_genre = favourite_genre

    def __len__(self):
        return len(self._active_ids)

    def __contains__(self, song_id):
        return song_id in self._active_ids

    # -- scoring ----------------------------------------------------------

    def score(self, song):
        """Compute the autoplay priority score for *song*.

        Formula:
            0.40 * like_norm + 0.15 * play_norm
          + 0.30 * recency_norm + 0.15 * genre_bonus
        """
        like_norm = min(song.like_count, self.max_likes) / self.max_likes
        play_norm = min(song.play_count, self.max_plays) / self.max_plays
        recency = song.last_played
        recency_norm = 0.0
        if self.now > 0 and recency > 0:
            recency_norm = max(0.0, min(1.0, recency / self.now))
        genre_bonus = 0.0
        if self.favourite_genre is not None and song.genre == self.favourite_genre:
            genre_bonus = 1.0
        return (0.40 * like_norm + 0.15 * play_norm + 0.30 * recency_norm + 0.15 * genre_bonus)

    # -- mutation ---------------------------------------------------------

    def add_to_autoplay(self, song):
        if song.song_id in self._active_ids:
            return False
        self._removed.discard(song.song_id)
        s = self.score(song)
        self._scores[song.song_id] = s
        entry = (s, next(self._counter), song.song_id, song)
        self._heap.push(entry)
        self._active_ids.add(song.song_id)
        return True

    def add_many(self, songs):
        for song in songs:
            self.add_to_autoplay(song)

    def remove_from_autoplay(self, song_id):
        if song_id not in self._active_ids:
            return False
        self._removed.add(song_id)
        self._active_ids.discard(song_id)
        return True

    def update_score(self, song, now=None):
        if now is not None:
            self.now = now
        if song.song_id in self._active_ids:
            self._removed.add(song.song_id)
            self._active_ids.discard(song.song_id)
        self.add_to_autoplay(song)

    # -- extraction -------------------------------------------------------

    def peek(self):
        self._clean_top()
        if self._heap:
            return self._heap.peek()[3]
        return None

    def peek_score(self):
        self._clean_top()
        if self._heap:
            return self._scores.get(self._heap.peek()[2], 0.0)
        return None

    def next_autoplay(self):
        self._clean_top()
        if not self._heap:
            return None
        entry = self._heap.pop()
        song_id = entry[2]
        song = entry[3]
        self._active_ids.discard(song_id)
        self._scores.pop(song_id, None)
        return song

    def _clean_top(self):
        while self._heap and self._heap.peek()[2] in self._removed:
            entry = self._heap.pop()
            sid = entry[2]
            self._removed.discard(sid)

    # -- inspection -------------------------------------------------------

    def to_list(self):
        return [entry[3] for entry in self._heap if entry[2] not in self._removed]

    def to_sorted_list(self):
        active = [entry for entry in self._heap if entry[2] not in self._removed]
        # Sort by score descending (max-heap: root has highest score)
        active.sort(key=lambda e: e[0], reverse=True)
        return [entry[3] for entry in active]

    def to_heap_array(self):
        result = []
        for entry in self._heap:
            song = entry[3]
            score = self._scores.get(song.song_id, 0.0)
            result.append({
                "song_id": song.song_id,
                "title": song.title,
                "score": round(score, 4),
                "is_removed": song.song_id in self._removed,
            })
        return result

    def clear(self):
        self._heap.clear()
        self._removed.clear()
        self._active_ids.clear()
        self._scores.clear()

    def set_favourite_genre(self, genre):
        self.favourite_genre = genre

    def set_max_likes(self, max_likes):
        self.max_likes = max(max_likes, 1)

    def set_max_plays(self, max_plays):
        self.max_plays = max(max_plays, 1)
