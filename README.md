# Music Streaming Playlist Engine

A music streaming backend and web visualization that demonstrates three core data structures -- a doubly linked list, a binary search tree, and a max-heap -- working together in a realistic domain. Includes algorithm analysis (playlist statistics, smart shuffle, recommendation engine), performance benchmarking, and taste shift detection.

## Tech Stack

- **Backend**: Python 3.10+, Flask
- **Frontend**: Vanilla HTML/CSS/JS (no build step)
- **Charts**: matplotlib
- **Tests**: unittest

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
python -m unittest discover tests/ -v

# Start the web app
python run.py
# Open http://127.0.0.1:5000

# Run performance benchmarks
python benchmarking/benchmark.py
```

## Project Structure

```
data_structures/     Core data structures (no internal dependencies)
  song.py            Song class + Genre enum
  doubly_linked_list.py  Playlist (DLL with O(1) lookup via _node_map)
  bst.py             Song catalogue (iterative BST, range search)
  heap.py            Autoplay queue (max-heap with lazy deletion)

algorithms/          Business logic (depends on data_structures)
  analytics.py       Playlist statistics (genre/artist distribution)
  smart_shuffle.py   Constrained shuffle (avoid back-to-back duplicates)
  recommendation.py  Cross-structure recommendation pipeline
  taste_shift.py     EMA + KL divergence taste shift detection

data/                Data layer
  csv_generator.py   Generates songs_dataset.csv (25+ songs)
  data_loader.py     Loads CSV into all three structures

benchmarking/        Performance measurement
  benchmark.py       N=50/200/1000/5000/20000, generates charts

web/                 Flask web application
  routes.py          All API routes + page rendering
  templates/         Single-page HTML template
  static/css/        Dark-theme stylesheet
  static/js/         5 JS modules (main, playlist-view, heap-view, search, recommendations)

tests/               109 unit tests
docs/                Design docs, algorithm analysis, challenges
```

## Key Features

- **Playlist (DLL)**: Add/remove songs, navigate next/previous, Fisher-Yates shuffle, smart shuffle with duplicate avoidance
- **Catalogue (BST)**: Search by title (exact + range), filter by artist/genre, in-order alphabetical traversal
- **Autoplay Queue (Heap)**: Priority-based queue with weighted scoring (likes, plays, recency, genre bonus), lazy deletion
- **Recommendations**: Pipeline integrating BST (find related) -> DLL (filter) -> Heap (score) -> DLL (exclude recent)
- **Taste Shift Detection**: EMA-smoothed genre distribution with symmetric KL divergence, confirmation streaks, progressive score adjustment
- **Performance Benchmarking**: Insertion/search/traversal timing at 5 scales, BST height vs ideal comparison, matplotlib charts

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Main page (SPA) |
| GET | `/api/playlist` | Get playlist with current position |
| POST | `/api/playlist/add` | Add song to playlist |
| POST | `/api/playlist/remove` | Remove song from playlist |
| POST | `/api/playlist/next` | Play next song |
| POST | `/api/playlist/previous` | Play previous song |
| POST | `/api/playlist/goto` | Jump to position |
| POST | `/api/playlist/shuffle` | Fisher-Yates shuffle |
| POST | `/api/playlist/smart-shuffle` | Constrained shuffle |
| POST | `/api/playlist/like` | Toggle like |
| GET | `/api/playlist/analytics` | Playlist statistics |
| GET | `/api/catalogue/search?q=` | Title search (exact + range) |
| GET | `/api/catalogue/by-artist?artist=` | Filter by artist |
| GET | `/api/catalogue/by-genre?genre=` | Filter by genre |
| GET | `/api/catalogue/all` | All songs (in-order) |
| GET | `/api/catalogue/range?low=&high=` | Range search |
| GET | `/api/catalogue/genres` | List all genres |
| GET | `/api/autoplay` | Get heap state |
| POST | `/api/autoplay/next` | Extract next from queue |
| POST | `/api/autoplay/add` | Add to autoplay |
| POST | `/api/autoplay/remove` | Remove from autoplay |
| GET | `/api/recommend?n=5` | Get recommendations |
| GET | `/api/taste/stats` | Taste detector stats |
| POST | `/api/taste/action` | Record a genre action |
| POST | `/api/taste/simulate` | Simulate a taste shift |
| POST | `/api/taste/reset` | Reset detector |
| POST | `/api/reload` | Reload dataset |

## Verification

1. `python -m unittest discover tests/ -v` -- 109 tests
2. `python run.py` -- web app at http://127.0.0.1:5000
3. `python benchmarking/benchmark.py` -- generates `benchmark_*.png` charts
