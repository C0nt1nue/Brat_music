# Algorithm Explanations and Complexity Analysis

## 1. Doubly Linked List Operations

| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| `add_song` | O(1) | Append to tail, update `_node_map` |
| `remove_song` | O(1) | Lookup via `_node_map`, relink neighbors |
| `play_next` | O(1) | Follow `current.next` |
| `play_previous` | O(1) | Follow `current.prev` (key advantage over singly linked list) |
| `move_to_position` | O(n) | Walk from head to index |
| `shuffle` | O(n) | Fisher-Yates on node list + relink |
| `current_index` | O(n) | Walk from head to find current |
| `get_song` | O(1) | Hash map lookup via `_node_map` |

### Fisher-Yates Shuffle

The shuffle collects all nodes into a list, applies Fisher-Yates (random swap from end backward), then relinks the nodes in the new order. The current pointer is preserved because it references a Node object, not an index.

```
nodes = collect_all_nodes()    # O(n)
for i from len-1 down to 1:    # O(n)
    j = random(0, i)
    swap nodes[i], nodes[j]
relink(nodes)                  # O(n)
```

## 2. Binary Search Tree Operations

| Operation | Average | Worst Case | Notes |
|-----------|---------|------------|-------|
| `insert` | O(log n) | O(n) | Degenerate if sorted input |
| `search` | O(log n) | O(n) | Exact title match |
| `find_by_artist` | O(n) | O(n) | Full traversal (no artist index) |
| `find_by_genre` | O(n) | O(n) | Full traversal |
| `range_search` | O(log n + k) | O(n) | k = number of results; prunes subtrees outside range |
| `in_order_traversal` | O(n) | O(n) | Iterative (stack-based) |
| `height` | O(n) | O(n) | DFS with explicit stack |
| `remove` | O(n) | O(n) | Must traverse to find by song_id, then standard BST deletion |

### Why Iterative Implementation

Python's default recursion limit is ~1000. At N=20000 with sorted insertion, the BST degenerates into a linked list with height 20000, causing `RecursionError` in any recursive traversal. All BST methods use explicit stacks:

```python
# Iterative in-order traversal
stack = []
node = self.root
while node is not None or stack:
    while node is not None:
        stack.append(node)
        node = node.left
    node = stack.pop()
    yield node.song
    node = node.right
```

### Range Search with Pruning

The range search skips subtrees that fall entirely outside [low, high]:
- If `current_key < low`, skip the left subtree.
- If `current_key > high`, skip the right subtree.

This gives O(log n + k) on a balanced tree, where k is the number of results.

## 3. Max-Heap Operations

| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| `add_to_autoplay` | O(log n) | `heapq.heappush` |
| `next_autoplay` | O(log n) amortized | `heappop` + lazy cleanup |
| `remove_from_autoplay` | O(1) | Lazy: add to `_removed` set |
| `update_score` | O(log n) | Mark old as removed + push new |
| `peek` | O(1) amortized | Read heap[0] after cleanup |

### Scoring Formula

```
score = 0.40 * like_norm     # user likes (highest weight)
      + 0.15 * play_norm      # play frequency
      + 0.30 * recency_norm   # how recently played
      + 0.15 * genre_bonus    # 1.0 if matches favorite genre, else 0
```

Normalization: `like_norm = min(like_count, max_likes) / max_likes`, where `max_likes` is the maximum across all loaded songs.

### Lazy Deletion

Physical deletion from a heap requires finding the element (O(n)) and then sifting (O(log n)). Instead, we mark the song_id in a `_removed` set. When `next_autoplay` is called, stale entries at the top of the heap are popped and discarded until a live entry is found. This makes removal O(1) at the cost of some wasted heap space.

## 4. Smart Shuffle (Constrained Permutation)

**Goal**: Rearrange the playlist so that consecutive songs differ in both artist and genre, when possible.

**Algorithm**: Greedy with progressive relaxation.
1. At each step, find a candidate that differs from the previous song in both artist and genre.
2. If none exists, relax to differ in artist only.
3. If still none, relax to differ in genre only.
4. If fully degenerate (all remaining songs share the same artist and genre), take any.

**Complexity**: O(n^2) worst case (for each of n positions, scan the remaining list). This is acceptable for playlist sizes (typically < 1000).

**Degeneration handling**: If a single artist occupies >50% of the playlist, back-to-back repeats are mathematically unavoidable. The algorithm detects this and returns a warning string.

## 5. Recommendation Engine

**Pipeline** (integrates all three data structures):

| Step | Structure | Operation | Complexity |
|------|-----------|-----------|------------|
| 1. Find related songs | BST | `find_by_genre` + `find_by_artist` | O(n) |
| 2. Filter playlist songs | DLL `_node_map` | Set lookup | O(1) per song |
| 3. Score candidates | Heap | `add_many` + `next_autoplay` | O(m log m) |
| 4. Exclude recent | DLL | `recent_songs(10)` | O(n log n) |
| 5. Return top 5 | Heap | 5x `next_autoplay` | O(5 log m) |

Where n = catalogue size, m = candidate count after filtering.

## 6. Taste Shift Detection

### EMA Distribution

The historical genre distribution is maintained as an EMA:

```
EMA[g] = (1 - alpha) * EMA[g] + alpha * new_action[g]
```

With alpha=0.1, the EMA has a "half-life" of approximately 7 actions. Each new action contributes a small amount, preventing single-action noise from dominating.

### Symmetric KL Divergence

The detector compares the recent window distribution (last N actions) with the EMA using symmetric KL divergence:

```
KL_sym(P, Q) = (KL(P||Q) + KL(Q||P)) / 2
```

Both distributions are Laplace-smoothed with eps=0.01 to handle zero-support genres (when the user only plays one genre, the window is a delta function). Without smoothing, KL(Q||P) would be infinite whenever P has a zero where Q is non-zero.

### Trigger Logic

1. **Minimum samples**: Detection is disabled until at least `min_samples` (default 20) actions have been recorded.
2. **Threshold**: KL > 0.3 triggers a potential shift.
3. **Confirmation**: The threshold must be exceeded for `confirm_streak` (default 3) consecutive actions before a shift is confirmed.
4. **Progressive adjustment**: On confirmation, `step_adjustment` (0.05) is returned for the autoplay heap to nudge scores toward the new taste.

### Complexity

| Operation | Complexity |
|-----------|------------|
| `record_action` | O(G) where G = number of genres (14) |
| `get_stats` | O(G) |
| `simulate_shift` | O(n * G) |

Since G is fixed at 14, all operations are effectively O(1) with respect to the number of actions.
