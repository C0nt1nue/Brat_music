<h1 align="center">Music Streaming Playlist Engine</h1>

<p align="center">
  A collaborative group project implementing a full-featured music streaming
  playlist engine using hand-crafted data structures in Python — doubly linked
  lists, binary search trees, and heap-based priority queues — backed by a
  20,000-song dataset.
</p>

---

## Overview

This project models the core backend of a music streaming service: a playlist
system that supports navigation, search, sorting, filtering, autoplay, and
recommendations. All core data structures are built from scratch without
relying on Python's built-in high-level collections (dict, list.sort,
heapq, etc.), demonstrating algorithmic fundamentals in a practical domain.

Team members: A, B, C, D — each responsible for distinct modules and data
structures, with clearly delineated APIs between them.

---

## Project Structure

```
brat_music/
├── main.py                          # Entry point — CLI menu & flow control
├── songs_dataset_20000.csv          # 20,000-song dataset (with play/like stats)
│
├── models/                          # Data modeling (Member A)
│   ├── A_gequ.py                    #   Song dataclass (id, title, artist, genre, ...)
│   └── liupai.py                    #   Genre enum (16 genres: Pop, Rock, Jazz, ...)
│
├── data/                            # Data loading (Member A)
│   └── A_shuju_jiazai.py            #   CSV loader -> BST, Heap, Playlist
│
├── structures/                      # Core data structures
│   ├── B_bofang_liebiao.py          #   Doubly linked list playlist (Member B)
│   ├── C_ercha_sousuo_shu.py        #   BST song catalog (Member C)
│   ├── D_dui.py                     #   MaxHeap / MinHeap / AutoplayHeap (Member D)
│   ├── D_zhongweishu.py            #   Two-heap median finder (Member D)
│   ├── D_guibing_hebing.py         #   K-way merge via min-heap (Member D)
│   ├── D_tuijian_yinqing.py        #   Recommendation engine (Member D)
│   ├── D_bofang_gongju.py          #   Hot/cold balancer & median tools (Member D)
│   ├── A_tuxing_jiemian.py          #   tkinter GUI (Member A)
│   └── C_xingneng_ceshi.py          #   Performance benchmarking (Member C)
│
└── tests/                           # Unit & integration tests
    ├── A_ceshi_gequ.py              #   Song model tests
    ├── A_ceshi_jicheng.py           #   Inheritance tests
    ├── B_ceshi_bofang_liebiao.py    #   Playlist tests
    ├── C_ceshi_ercha_sousuo_shu.py  #   BST tests
    ├── D_ceshi_dui.py               #   Heap tests
    └── D_ceshi_tuijian_yinqing.py   #   Recommendation engine tests
```

---

## Features

### 1. Playlist Management (Member B — Doubly Linked List)

- Add / remove / find songs by ID — O(1) lookups.
- Bidirectional navigation: play next / previous, with optional circular mode.
- Shuffle (Fisher-Yates) and display operations.
- Part 2 extensions: merge sort by title/artist/score, genre filtering,
  artist search, play-count statistics, and playback history.

### 2. Song Catalog (Member C — Binary Search Tree)

- Insert & search songs by title with O(log n) average complexity.
- Prefix search for autocomplete-like song queries.
- In-order traversal produces alphabetically sorted song listings.
- Hand-crafted comparison and traversal functions (no sorted() or dict).

### 3. Autoplay Priority Queue (Member D — Max Heap)

- add_to_autoplay inserts songs with a computed score — O(log n).
- next_autoplay extracts the highest-priority song — O(log n).
- remove_from_autoplay and update_score with O(n) lookup + O(log n) adjustment.
- Autoplay score formula: like_count * 0.5 + play_count * 0.2 + duration_bonus.

### 4. Recommendation Engine (Member D)

- Three-structure pipeline: BST -> Heap -> Linked List.
- Finds top-5 songs by genre/artist similarity, scores them via the autoplay
  heap, and excludes songs already in the playlist.

### 5. Advanced Playback Tools (Member D)

| Tool | Description |
|---|---|
| HotColdBalancer | Mixes popular and niche songs at a configurable ratio |
| ScoreMedianReporter | Tracks the median autoplay score via two-heap median finder |
| merge_playlists() | Merges multiple sorted playlists using K-way min-heap merge |
| find_median_score_songs() | Finds songs nearest to the median score |

### 6. Performance Benchmarking (Member C)

Measures insertion and search time across all three structures at scales of
50, 200, 1,000, 5,000, and 20,000 songs, with both best-case (random order)
and worst-case (sorted order) BST scenarios. Outputs terminal tables and
matplotlib charts.

### 7. GUI (Member A — tkinter)

A graphical interface with playlist view, autoplay heap visualization,
BST search box, and buttons for add/remove/navigate/recommend.

---

## Getting Started

### Prerequisites

- Python 3.10+
- (Optional) matplotlib — required only for the benchmarking charts

### Running the CLI

```bash
cd D:\brat_music
python main.py
```

The interactive menu provides access to all features:

```
[1]  Show all songs (BST in-order)
[2]  Search by title (BST)
[3]  Playlist navigation
[4]  Playlist sorting
[5]  Filter by genre
[6]  Autoplay mode
[7]  Playlist statistics
[8]  Search by artist
[9]  BST overview
[10] Manage playlist (add/remove/find)
```

### Running the GUI

```bash
python structures/A_tuxing_jiemian.py
```

### Running Tests

```bash
python -m pytest tests/ -v
```

or run individual test files directly:

```bash
python tests/A_ceshi_gequ.py
python tests/B_ceshi_bofang_liebiao.py
python tests/C_ceshi_ercha_sousuo_shu.py
python tests/D_ceshi_dui.py
python tests/D_ceshi_tuijian_yinqing.py
```

### Running Benchmarks

```bash
python structures/C_xingneng_ceshi.py
```

---

## Data Structures at a Glance

| Structure | Implementation | Key Operations | Complexity |
|---|---|---|---|
| Doubly Linked List | Custom Node + head/tail pointers | add, remove, find, shuffle | O(1) add/remove, O(n) shuffle |
| BST | Recursive tree with hand-written helpers | insert, search, prefix-search, inorder | O(log n) avg, O(n) worst |
| MaxHeap / MinHeap | Array-based complete binary tree | push, pop, peek, heapify | O(log n) |
| AutoplayHeap | Wraps MaxHeap with song ID to index map | add, next, remove, update | O(log n) core ops |
| MedianFinder | Two heaps (max + min) | add, find_median | O(log n) |
| MergeKSorted | Min-heap K-way merge | merge | O(N log K) |

---

## Module Interdependence

```
DataLoader (Member A)
  ├── loads Song objects from CSV
  ├── populates BST (Member C)
  ├── populates AutoplayHeap (Member D)
  └── populates Playlist (Member B)

main.py
  ├── Playlist / PlaylistPart2  (Member B)
  ├── BST                       (Member C)
  ├── AutoplayHeap              (Member D)
  └── DataLoader                (Member A)

Recommendation Engine (Member D)
  ├── BST.inorder_traversal()   (Member C)
  ├── Playlist membership check (Member B)
  └── MaxHeap scoring           (Member D)
```

---

## Genre Coverage

Pop, Rock, Jazz, Hip Hop, Classical, Electronic, R&B, Country, Latin, Indie,
Metal, Folk, Reggae, Soul, Blues, K-Pop — 16 genres represented across the
20,000-song dataset.

---

## License

This project is created for educational purposes as a group data-structures
assignment.
