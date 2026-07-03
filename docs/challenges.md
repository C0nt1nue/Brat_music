# Challenges and Solutions

## Challenge 1: BST Degeneration with Sorted Input

**Problem**: When songs are inserted in alphabetical order (which is common when loading from a sorted CSV), the BST degenerates into a linked list. Search and insertion become O(n) instead of O(log n). At N=20000, this caused insertion to take 15+ seconds.

**Solution**: 
- Used iterative implementations for all BST methods to avoid recursion-depth overflow at height=20000.
- Documented that AVL trees or Red-Black trees are the production solution (self-balancing guarantees O(log n) height).
- The benchmarking module explicitly measures and visualizes this degeneration, comparing actual height against ideal log2(N).

**Benchmark Results**:
| N | BST Insert (s) | BST Height | Ideal Height (log2 N) |
|---|----------------|------------|----------------------|
| 50 | 0.0001 | 50 | 5.6 |
| 200 | 0.0017 | 200 | 7.6 |
| 1000 | 0.048 | 1000 | 10.0 |
| 5000 | 0.912 | 5000 | 12.3 |
| 20000 | 15.24 | 20000 | 14.3 |

The height equals N exactly, confirming full degeneration.

## Challenge 2: Heap Visualization

**Problem**: Visualizing a heap as a binary tree requires mapping the array representation to a tree layout. Unlike a BST with explicit left/right pointers, a heap uses array indices: children of index `i` are at `2i+1` and `2i+2`.

**Solution**: Grouped heap entries by level. Level 0 has 1 node (index 0), level 1 has 2 nodes (indices 1-2), level 2 has 4 nodes (indices 3-6), etc. Each level is rendered as a flexbox row, centered. This gives the characteristic tree shape without needing explicit edge rendering.

Only active (non-removed) entries are shown, up to 4 levels (31 nodes) for readability. Removed entries are shown with strikethrough when present.

## Challenge 3: Smart Shuffle Impossibility

**Problem**: When a single artist occupies more than 50% of the playlist, it is mathematically impossible to avoid consecutive same-artist songs. The pigeonhole principle guarantees at least one collision.

**Solution**: 
- Before shuffling, check if any artist exceeds 50% of the playlist.
- If so, return a warning string alongside the shuffled result.
- The algorithm still does its best (greedy with progressive relaxation) to minimize collisions, but acknowledges the limitation.
- The warning is surfaced to the user via an alert in the web interface.

## Challenge 4: Recursion Overflow at N=20000

**Problem**: Python's default recursion limit is ~1000. A degenerate BST (linked list) at N=20000 has depth 20000, causing `RecursionError` in any recursive traversal.

**Solution**: Replaced all recursive BST methods with iterative equivalents using explicit stacks:
- `in_order_traversal`: stack-based left-spine descent
- `find_by_artist` / `find_by_genre`: same pattern with filtering
- `range_search`: stack with pruning
- `height`: DFS with explicit stack
- `is_balanced`: post-order with stack and visited flag
- `remove`: iterative search + standard iterative node removal

## Challenge 5: Lazy Deletion Correctness

**Problem**: With lazy deletion, removed entries remain in the heap array. If `next_autoplay` simply pops the top, it might return a removed song.

**Solution**: 
- Before any `peek` or `next_autoplay` operation, call `_clean_top()` which pops stale entries from the top of the heap until a live entry is found.
- The `_removed` set is checked by song_id. Once a stale entry is popped, its id is discarded from `_removed` to prevent unbounded set growth.
- The `_active_ids` set tracks which songs are truly in the queue, used for `__len__` and `__contains__`.
- `update_score` works by marking the old entry as removed and pushing a new one, so the heap may contain multiple entries for the same song -- only the latest is active.

## Challenge 6: KL Divergence with Zero-Support Distributions

**Problem**: When a user only plays one genre, the sliding window distribution is a delta function (probability 1.0 for one genre, 0.0 for all others). The EMA, even after convergence, has small non-zero values for other genres. The raw KL divergence `KL(Q||P)` includes terms like `q * log(q/0)` which are infinite.

**Solution**: Applied Laplace smoothing to both distributions before computing KL:
```
p_smoothed[g] = (p[g] + eps) / (1 + n_genres * eps)
```
With eps=0.01 and 14 genres, a delta distribution becomes approximately {0.886 for the dominant genre, 0.0088 for others}. This keeps KL finite while preserving meaningful discrimination. The threshold (0.3) was calibrated so that a stable single-genre taste produces KL near 0, while a sudden genre switch produces KL > 4.

## Challenge 7: EMA Convergence During Warmup

**Problem**: The EMA starts from a uniform distribution. During the first ~20 actions, the EMA is still converging toward the user's actual taste, which can cause false-positive shift detections.

**Solution**: 
- Detection is disabled until `min_samples` (default 20) actions have been recorded.
- A confirmation streak of 3 consecutive threshold-exceeding actions is required before confirming a shift.
- The single-action distribution pushed into the EMA includes a small uniform floor (0.01 per genre) to prevent the EMA from collapsing to a pure delta, which would make it overly sensitive.
