# Design Decisions and Architecture

## Overview

The Music Streaming Playlist Engine is a single-page web application that demonstrates three core data structures (doubly linked list, binary search tree, max-heap) working together in a realistic domain. The backend is Python 3 + Flask; the frontend is vanilla HTML/CSS/JS with no build step.

## Layered Architecture

```
web/          <- Flask routes, templates, static assets
algorithms/   <- Business logic (depends on data_structures)
data/         <- CSV generation and loading (depends on data_structures)
data_structures/ <- Core data structures (no internal dependencies)
tests/        <- Unit tests per module
benchmarking/ <- Performance measurement
```

Dependencies flow downward: `web` depends on `algorithms` and `data`; `algorithms` depends on `data_structures`; `data_structures` has zero internal dependencies. This makes each layer independently testable.

## Data Structure Choices

### Doubly Linked List (Playlist)

**Why DLL over array or singly linked list?**
- `play_previous()` is O(1) with a DLL; a singly linked list would require O(n) traversal from head.
- The `_node_map` (song_id -> Node) gives O(1) lookup and removal, matching array-with-hash-map performance while preserving pointer-based structure for educational visualization.
- Fisher-Yates shuffle operates on node references then relinks in O(n), avoiding data copying.

### Binary Search Tree (Song Catalogue)

**Why BST over hash table?**
- BST supports ordered traversal (in-order gives alphabetical song listing) and range queries (e.g., "all titles from A to D").
- Hash tables only support exact-match lookups, not prefix or range searches.
- BST also demonstrates worst-case vs best-case performance: sorted insertion creates a degenerate (linked-list-like) tree, which the benchmarking module measures explicitly.

**Why not self-balancing (AVL/Red-Black)?**
- The project's goal includes demonstrating the degeneration problem. A plain BST makes this visible. The benchmarking results and documentation explain that AVL/Red-Black trees are the production solution.

**Iterative implementation**: All traversals and searches use explicit stacks to avoid Python's recursion limit (~1000) at N=20000.

### Max-Heap (Autoplay Queue)

**Why heap over BST?**
- The autoplay queue needs "always extract the highest-priority item" -- this is exactly what a max-heap does. `extract-max` is O(log n).
- In a BST, finding the maximum is O(h) and deletion adds complexity; a heap is simpler and faster for this use case.

**Lazy deletion**: Instead of physically removing from the heap (which would require search + sift), we mark song_ids in a `_removed` set. `next_autoplay` skips stale entries. This makes removal O(1) at the cost of occasional stale entries in the heap array.

**Scoring formula**: `score = 0.4*like_norm + 0.15*play_norm + 0.30*recency_norm + 0.15*genre_bonus`. Weights prioritize user likes, then recency, then play frequency, with a bonus for the user's favorite genre.

## Algorithm Design

### Recommendation Pipeline

The recommendation engine integrates all three data structures:
1. **BST** finds songs matching the playlist's dominant genre or artist.
2. **Linked list** `_node_map` provides O(1) filtering of songs already in the playlist.
3. **Heap** scores and ranks the remaining candidates.
4. **Linked list** `recent_songs()` excludes the 10 most recently played tracks.
5. Returns the top 5.

### Taste Shift Detection

Uses an EMA (Exponential Moving Average) of the genre distribution, compared against a sliding window of recent actions via symmetric KL divergence.

- **EMA (alpha=0.1)**: smooths the historical distribution, preventing single-action noise from triggering false shifts.
- **Laplace smoothing (eps=0.01)**: applied to both distributions before KL computation to handle zero-support genres (when the user only plays one genre, the window distribution is a delta function).
- **Confirmation streak (3 consecutive triggers)**: requires the KL to exceed the threshold for 3 consecutive actions before confirming a shift, reducing false positives.
- **Progressive adjustment (0.05 per step)**: when a shift is confirmed, the autoplay heap scores are nudged to favor the new taste direction.

## Web Architecture

Single-page application with a 3-panel layout:
- **Left**: Playlist (DLL visualization with vertical node list, current highlight)
- **Center**: Now Playing (song detail, player controls, analytics)
- **Right**: Autoplay Queue (heap binary tree visualization by level)
- **Bottom**: Catalogue search, recommendation cards, taste shift panel

The backend holds all state in a singleton `AppState` object (playlist, catalogue, autoplay queue, taste detector). All mutations go through API endpoints, and the frontend re-fetches affected data after each action.

## Testing Strategy

- 109 unit tests covering every module.
- Each data structure and algorithm has its own test file.
- Tests use deterministic seeds for reproducibility.
- The benchmark serves as integration testing for large N (up to 20000).
