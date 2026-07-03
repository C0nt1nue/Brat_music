"""Entry point: load CSV data, demo playback & reordering, start the web app.

Running ``py run.py`` performs the full pipeline in the main function:
  1. Read songs from the CSV file into in-memory Song objects.
  2. Build the playlist (doubly linked list) and supporting structures.
  3. Iterate through the playlist, playing different songs.
  4. Change song order (move a song, then Fisher-Yates shuffle).
  5. Start the Flask web server so the result is visible in the UI.

The demo operates on the *same* AppState singleton the web app uses, so
every change made here is immediately reflected in the browser.
"""

import os
import sys
import time
import random
import argparse

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web import create_app
from web.routes import _state

app = create_app()


def run_demo():
    """Load CSV, iterate playback, reorder songs -- synced to the web UI."""
    print("=" * 64)
    print("  Music Streaming Playlist Engine")
    print("=" * 64)

    # 1. Read CSV -> create songs in memory
    print("\n[1] Reading songs from CSV into memory...")
    _state.load()
    playlist = _state.playlist
    songs = _state.all_songs
    csv_label = getattr(_state, "_csv_source", "songs_dataset.csv")
    print(f"    Loaded {len(songs)} songs from {csv_label}")
    print(f"    Playlist (DLL) size: {len(playlist)}")
    print(f"    Catalogue (BST) size: {len(_state.catalogue)}")
    print(f"    Autoplay heap size:  {len(_state.autoplay)}")

    # 2. Iterate through the playlist, playing different songs
    print("\n[2] Iterating through the playlist (playing different songs)...")
    steps = min(5, len(playlist))
    first = playlist.current_song()
    if first:
        first.play_count += 1
        first.last_played = time.time()
        _state.taste.record_action(first.genre)
        print(f"    Playing #{playlist.current_index() + 1}: "
              f"{first.title} - {first.artist} [{first.genre.name}]")
    for i in range(steps - 1):
        song = playlist.play_next()
        if song:
            song.play_count += 1
            song.last_played = time.time()
            _state.taste.record_action(song.genre)
            print(f"    Playing #{playlist.current_index() + 1}: "
                  f"{song.title} - {song.artist} [{song.genre.name}]")
        time.sleep(0.05)

    # 3. Change song order
    print("\n[3] Changing song order...")
    ordered = playlist.to_list()
    if ordered:
        first_song = ordered[0]
        mid = len(playlist) // 2
        if playlist.move_song(first_song.song_id, mid):
            print(f"    Moved '{first_song.title}' "
                  f"from position 1 to position {mid + 1}")
    playlist.shuffle(random.Random(123))
    print("    Applied Fisher-Yates shuffle")

    print("\n    Final playlist order:")
    for i, s in enumerate(playlist):
        marker = "  <-- current" if playlist.current_index() == i else ""
        print(f"    {i + 1:>3}. {s.title} - {s.artist} [{s.genre.name}]{marker}")

    # 3b. Demonstrate the MaxHeap (autoplay queue) on the imported data
    print("\n[3b] MaxHeap autoplay queue -- songs sorted by priority score...")
    heap_arr = _state.autoplay.to_heap_array()
    heap_arr.sort(key=lambda e: e["score"], reverse=True)
    for i, entry in enumerate(heap_arr[:10]):
        removed = " (removed)" if entry["is_removed"] else ""
        print(f"    {i + 1:>3}. {entry['title']:<24} score={entry['score']:.4f}{removed}")
    print(f"    Heap size: {len(heap_arr)} songs total")

    # 4. Start the web visualization
    print("\n[4] Starting web visualization...")
    print("    Open http://127.0.0.1:5000 in your browser")
    print("    The playlist above is live in the web UI.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Music Streaming Playlist Engine")
    parser.add_argument("--csv", metavar="FILE",
                        help="Path to your own CSV file (same columns as songs_dataset.csv)")
    args = parser.parse_args()

    if args.csv:
        if not os.path.exists(args.csv):
            print(f"Error: CSV file not found: {args.csv}")
            sys.exit(1)
        _state.load_from(args.csv)
        _state._csv_source = os.path.basename(args.csv)
        print(f"Using custom dataset: {args.csv}")
    else:
        _state._csv_source = "songs_dataset.csv"

    run_demo()
    app.run(debug=True, port=5000)
