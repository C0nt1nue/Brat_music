"""Binary Search Tree indexed by song title (case-insensitive).

All traversals and searches use iterative implementations to avoid
recursion-depth limits when N is large (e.g. 20 000).
"""


class BSTNode:
    __slots__ = ("song", "left", "right")

    def __init__(self, song):
        self.song = song
        self.left = None
        self.right = None


class SongCatalogue:
    """A BST catalogue of songs keyed by title (case-insensitive)."""

    def __init__(self):
        self.root = None
        self._size = 0

    def __len__(self):
        return self._size

    # -- insertion --------------------------------------------------------

    def insert(self, song):
        """Insert *song* into the tree. Returns False on duplicate id."""
        if self.root is None:
            self.root = BSTNode(song)
            self._size += 1
            return True
        node = self.root
        key = song.title.lower()
        while True:
            cur_key = node.song.title.lower()
            if key < cur_key:
                if node.left is None:
                    node.left = BSTNode(song)
                    self._size += 1
                    return True
                node = node.left
            elif key > cur_key:
                if node.right is None:
                    node.right = BSTNode(song)
                    self._size += 1
                    return True
                node = node.right
            else:
                # Same title key: allow if different song_id
                if node.song.song_id == song.song_id:
                    return False
                # Tie-break: go right for same-title different-id songs
                if node.right is None:
                    node.right = BSTNode(song)
                    self._size += 1
                    return True
                node = node.right

    def insert_many(self, songs):
        for song in songs:
            self.insert(song)

    # -- exact search -----------------------------------------------------

    def search(self, title):
        """Exact, case-insensitive match on *title*. Returns Song or None."""
        key = title.lower()
        node = self.root
        while node is not None:
            cur_key = node.song.title.lower()
            if key < cur_key:
                node = node.left
            elif key > cur_key:
                node = node.right
            else:
                return node.song
        return None

    def find_by_id(self, song_id):
        """Find a song by its id via in-order scan."""
        for song in self.in_order_traversal():
            if song.song_id == song_id:
                return song
        return None

    # -- filtered traversals ----------------------------------------------

    def find_by_artist(self, artist):
        """All songs whose artist matches (case-insensitive, substring)."""
        needle = artist.lower()
        results = []
        stack = []
        node = self.root
        while node is not None or stack:
            while node is not None:
                stack.append(node)
                node = node.left
            node = stack.pop()
            if needle in node.song.artist.lower():
                results.append(node.song)
            node = node.right
        return results

    def find_by_genre(self, genre):
        """All songs matching *genre* (Genre enum or string)."""
        from data_structures.song import Genre
        if not isinstance(genre, Genre):
            genre = Genre.from_string(genre)
        results = []
        stack = []
        node = self.root
        while node is not None or stack:
            while node is not None:
                stack.append(node)
                node = node.left
            node = stack.pop()
            if node.song.genre == genre:
                results.append(node.song)
            node = node.right
        return results

    def find_all(self):
        """Return every song as a list (in-order)."""
        return self.in_order_traversal()

    # -- range search -----------------------------------------------------

    def range_search(self, low, high):
        """All songs with title in [low, high] (inclusive, case-insensitive).

        Prunes subtrees that fall entirely outside the range.
        """
        low_k = low.lower()
        high_k = high.lower()
        results = []
        stack = []
        node = self.root
        while node is not None or stack:
            while node is not None:
                stack.append(node)
                cur_key = node.song.title.lower()
                if cur_key < low_k:
                    # No need to go further left
                    break
                node = node.left
            if not stack:
                break
            node = stack.pop()
            cur_key = node.song.title.lower()
            if low_k <= cur_key <= high_k:
                results.append(node.song)
            if cur_key < high_k:
                node = node.right
            else:
                node = None
        return results

    # -- in-order traversal (iterative) -----------------------------------

    def in_order_traversal(self):
        """Iterative in-order traversal. Yields Song objects."""
        results = []
        stack = []
        node = self.root
        while node is not None or stack:
            while node is not None:
                stack.append(node)
                node = node.left
            node = stack.pop()
            results.append(node.song)
            node = node.right
        return results

    def to_list(self):
        return self.in_order_traversal()

    # -- height (for benchmarking / diagnostics) --------------------------

    def height(self):
        """Iterative height computation."""
        if self.root is None:
            return 0
        max_depth = 0
        stack = [(self.root, 1)]
        while stack:
            node, depth = stack.pop()
            if depth > max_depth:
                max_depth = depth
            if node.left:
                stack.append((node.left, depth + 1))
            if node.right:
                stack.append((node.right, depth + 1))
        return max_depth

    def is_balanced(self):
        """Check if the tree is height-balanced (iterative)."""
        if self.root is None:
            return True
        stack = [(self.root, False)]
        heights = {}
        while stack:
            node, visited = stack.pop()
            if visited:
                lh = heights.get(id(node.left), 0)
                rh = heights.get(id(node.right), 0)
                if abs(lh - rh) > 1:
                    return False
                heights[id(node)] = 1 + max(lh, rh)
            else:
                stack.append((node, True))
                if node.right:
                    stack.append((node.right, False))
                if node.left:
                    stack.append((node.left, False))
        return True

    # -- remove -----------------------------------------------------------

    def remove(self, song_id):
        """Remove a song by id. Returns True if removed."""
        parent = None
        node = self.root
        # First find by id (may need full traversal since key is title)
        # Walk in-order to find the node with matching song_id
        target_node = None
        target_parent = None
        stack = []
        cur = self.root
        while cur is not None or stack:
            while cur is not None:
                stack.append(cur)
                cur = cur.left
            cur = stack.pop()
            if cur.song.song_id == song_id:
                target_node = cur
                break
            cur = cur.right
        if target_node is None:
            return False
        # Find parent of target_node
        target_parent = self._find_parent(self.root, target_node)
        self._remove_node(target_node, target_parent)
        self._size -= 1
        return True

    def _find_parent(self, root, target):
        if root is target:
            return None
        stack = [root]
        while stack:
            node = stack.pop()
            if node.left is target or node.right is target:
                return node
            if node.left:
                stack.append(node.left)
            if node.right:
                stack.append(node.right)
        return None

    def _remove_node(self, node, parent):
        # Case 1: no children
        if node.left is None and node.right is None:
            if parent is None:
                self.root = None
            elif parent.left is node:
                parent.left = None
            else:
                parent.right = None
        # Case 2: one child
        elif node.left is None:
            if parent is None:
                self.root = node.right
            elif parent.left is node:
                parent.left = node.right
            else:
                parent.right = node.right
        elif node.right is None:
            if parent is None:
                self.root = node.left
            elif parent.left is node:
                parent.left = node.left
            else:
                parent.right = node.left
        # Case 3: two children - replace with in-order successor
        else:
            succ_parent = node
            succ = node.right
            while succ.left is not None:
                succ_parent = succ
                succ = succ.left
            node.song = succ.song
            self._remove_node(succ, succ_parent)
