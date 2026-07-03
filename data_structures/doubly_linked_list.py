"""Doubly linked list implementation of a music playlist."""

import random


class Node:
    """A node in the doubly linked list."""

    __slots__ = ("song", "next", "prev")

    def __init__(self, song):
        self.song = song
        self.next = None
        self.prev = None


class Playlist:
    """A playlist backed by a doubly linked list.

    Maintains a ``_node_map`` (song_id -> Node) for O(1) lookups and
    removals.  Supports bidirectional navigation in O(1).
    """

    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None
        self._size = 0
        self._node_map = {}  # song_id -> Node

    # -- size / iteration ------------------------------------------------

    def __len__(self):
        return self._size

    def __iter__(self):
        node = self.head
        while node is not None:
            yield node.song
            node = node.next

    def __contains__(self, song_id):
        return song_id in self._node_map

    # -- mutation ---------------------------------------------------------

    def add_song(self, song):
        """Append *song* to the end of the playlist.

        Returns False (without adding) if a song with the same id already
        exists.
        """
        if song.song_id in self._node_map:
            return False
        node = Node(song)
        if self.tail is None:
            self.head = self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        if self.current is None:
            self.current = self.head
        self._node_map[song.song_id] = node
        self._size += 1
        return True

    def insert_at(self, song, index):
        """Insert *song* at zero-based *index*."""
        if song.song_id in self._node_map:
            return False
        if index <= 0:
            return self._insert_head(song)
        if index >= self._size:
            return self.add_song(song)
        # walk to the node currently at *index*
        target = self._node_at(index)
        node = Node(song)
        node.prev = target.prev
        node.next = target
        if target.prev:
            target.prev.next = node
        target.prev = node
        if target is self.head:
            self.head = node
        self._node_map[song.song_id] = node
        self._size += 1
        return True

    def _insert_head(self, song):
        node = Node(song)
        if self.head is None:
            self.head = self.tail = node
            self.current = self.head
        else:
            node.next = self.head
            self.head.prev = node
            self.head = node
            if self.current is None:
                self.current = self.head
        self._node_map[song.song_id] = node
        self._size += 1
        return True

    def remove_song(self, song_id):
        """Remove the song with *song_id* from the playlist."""
        node = self._node_map.get(song_id)
        if node is None:
            return False
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        if self.current is node:
            self.current = node.next or node.prev
        del self._node_map[song_id]
        self._size -= 1
        return True

    def move_song(self, song_id, to_index):
        """Relocate the song with *song_id* to zero-based *to_index*.

        Returns False if the song is missing or the index is out of range.
        The ``current`` pointer is preserved (it follows the Node object,
        not the position).  O(n) due to the index walk.
        """
        node = self._node_map.get(song_id)
        if node is None:
            return False
        if to_index < 0 or to_index >= self._size:
            return False
        cur_idx = 0
        walker = self.head
        while walker is not node:
            cur_idx += 1
            walker = walker.next
            if walker is None:
                return False
        if cur_idx == to_index:
            return True
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        node.prev = node.next = None
        remaining = self._size - 1
        if to_index == 0:
            node.next = self.head
            if self.head:
                self.head.prev = node
            self.head = node
            if self.tail is None:
                self.tail = node
        elif to_index >= remaining:
            node.prev = self.tail
            if self.tail:
                self.tail.next = node
            self.tail = node
            if self.head is None:
                self.head = node
        else:
            target = self.head
            for _ in range(to_index):
                target = target.next
            node.prev = target.prev
            node.next = target
            if target.prev:
                target.prev.next = node
            target.prev = node
            if target is self.head:
                self.head = node
        return True

    def clear(self):
        """Remove all songs."""
        self.head = self.tail = self.current = None
        self._node_map.clear()
        self._size = 0


   # -- navigation -------------------------------------------------------

    def play_next(self):
        """Advance current to the next song and return it (or None)."""
        if self.current and self.current.next:
            self.current = self.current.next
        return self.current.song if self.current else None

    def play_previous(self):
        """Move current to the previous song and return it (or None)."""
        if self.current and self.current.prev:
            self.current = self.current.prev
        return self.current.song if self.current else None

    def move_to_position(self, index):
        """Set current to the node at *index*. Returns the song or None."""
        node = self._node_at(index)
        if node is None:
            return None
        self.current = node
        return node.song

    def current_song(self):
        """Return the currently selected song (or None)."""
        return self.current.song if self.current else None

    def current_index(self):
        """Zero-based index of the current song, or -1."""
        if self.current is None:
            return -1
        idx = 0
        node = self.head
        while node is not None:
            if node is self.current:
                return idx
            idx += 1
            node = node.next
        return -1

    def get_song(self, song_id):
        """O(1) song lookup by id. Returns the Song or None."""
        node = self._node_map.get(song_id)
        return node.song if node else None

    # -- shuffle ----------------------------------------------------------

    def shuffle(self, rng=None):
        """Fisher-Yates shuffle of node order, then relink.

        Current pointer is preserved on whatever song it was pointing to.
        """
        if self._size <= 1:
            return
        rng = rng or random.Random()
        nodes = self._to_list()
        rng.shuffle(nodes)
        self._relink(nodes)

    # -- display / helpers ------------------------------------------------

    def display(self):
        """Return a list of dicts representing the playlist in order."""
        result = []
        for i, song in enumerate(self):
            d = song.to_dict()
            d["index"] = i
            d["is_current"] = (self.current is not None and
                               self.current.song.song_id == song.song_id)
            result.append(d)
        return result

    def to_list(self):
        """Return a list of Song objects in order."""
        return list(self)

    def _to_list(self):
        """Internal: collect all Node objects into a list."""
        nodes = []
        node = self.head
        while node is not None:
            nodes.append(node)
            node = node.next
        return nodes

    def _relink(self, nodes):
        """Relink a list of Node objects into the list."""
        if not nodes:
            self.head = self.tail = None
            return
        self.head = nodes[0]
        self.head.prev = None
        for i in range(1, len(nodes)):
            nodes[i - 1].next = nodes[i]
            nodes[i].prev = nodes[i - 1]
        nodes[-1].next = None
        self.tail = nodes[-1]

    def _node_at(self, index):
        """Return the Node at *index* or None. Negative indexes wrap."""
        if index < 0:
            return None
        if index >= self._size:
            return None
        node = self.head
        for _ in range(index):
            node = node.next
        return node

    def recent_songs(self, n):
        """Return the most recently *played* songs, newest first.

        Uses last_played timestamps; songs with timestamp 0 are excluded.
        """
        played = [s for s in self if s.last_played > 0]
        played.sort(key=lambda s: s.last_played, reverse=True)
        return played[:n]
