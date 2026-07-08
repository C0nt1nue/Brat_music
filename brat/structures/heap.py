from typing import Optional
from models.song import Song
import math


class HeapNode:
    """Heap node storing a song and its autoplay priority score."""

    def __init__(self, song: Song, score: float):
        self.song = song
        self.score = score

    def __repr__(self) -> str:
        return "HeapNode({}, score={:.1f})".format(self.song.song_id, self.score)


class MaxHeap:
    """Custom binary max heap backed by a list (0-indexed)."""

    def __init__(self):
        self._data = []

    def _parent(self, i):
        return (i - 1) // 2

    def _left(self, i):
        return 2 * i + 1

    def _right(self, i):
        return 2 * i + 2

    def _swap(self, i, j):
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def _sift_up(self, i):
        while i > 0:
            p = self._parent(i)
            if self._data[i].score > self._data[p].score:
                self._swap(i, p)
                i = p
            else:
                break

    def _sift_down(self, i):
        n = len(self._data)
        while True:
            largest = i
            l = self._left(i)
            r = self._right(i)
            if l < n and self._data[l].score > self._data[largest].score:
                largest = l
            if r < n and self._data[r].score > self._data[largest].score:
                largest = r
            if largest == i:
                break
            self._swap(i, largest)
            i = largest

    def push(self, node):
        self._data.append(node)
        self._sift_up(len(self._data) - 1)

    def pop(self):
        if not self._data:
            return None
        self._swap(0, len(self._data) - 1)
        top = self._data.pop()
        if self._data:
            self._sift_down(0)
        return top

    def peek(self):
        return self._data[0] if self._data else None

    def size(self):
        return len(self._data)

    def is_empty(self):
        return len(self._data) == 0

    def get_all(self):
        return list(self._data)


class AutoplayHeap:
    """Autoplay priority queue built on MaxHeap."""

    def __init__(self):
        self._heap = MaxHeap()

    def add_to_autoplay(self, song, score):
        self._heap.push(HeapNode(song, score))

    def next_autoplay(self):
        node = self._heap.pop()
        return node.song if node else None

    def remove_from_autoplay(self, song_id):
        data = self._heap._data
        for i, node in enumerate(data):
            if node.song.song_id == song_id:
                last_idx = len(data) - 1
                if i != last_idx:
                    self._heap._swap(i, last_idx)
                    data.pop()
                    if data:
                        self._heap._sift_up(i)
                        self._heap._sift_down(i)
                else:
                    data.pop()
                return True
        return False

    def update_score(self, song_id, new_score):
        data = self._heap._data
        for i, node in enumerate(data):
            if node.song.song_id == song_id:
                old = node.score
                node.score = new_score
                if new_score > old:
                    self._heap._sift_up(i)
                elif new_score < old:
                    self._heap._sift_down(i)
                return True
        return False

    def peek_next(self):
        node = self._heap.peek()
        return node.song if node else None

    def size(self):
        return self._heap.size()

    def is_empty(self):
        return self._heap.is_empty()

    def display_all(self):
        return [
            {
                "song_id": n.song.song_id,
                "title": n.song.title,
                "artist": n.song.artist,
                "score": round(n.score, 2),
            }
            for n in self._heap.get_all()
        ]

    def verify_heap_property(self):
        data = self._heap._data
        n = len(data)
        for i in range(n):
            l = 2*i + 1
            r = 2*i + 2
            if l < n and data[i].score < data[l].score:
                return False
            if r < n and data[i].score < data[r].score:
                return False
        return True

    @staticmethod
    def compute_score(song):
        like_ratio = song.like_count / max(song.play_count, 1)
        play_volume = math.log2(song.play_count + 1)
        return (like_ratio * play_volume * 50) + (play_volume * 5)
