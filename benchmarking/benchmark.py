"""Performance benchmarking for BST, heap, and linked list operations.

Measures insertion, search, and extraction times at N = 50, 200, 1000,
5000, 20000 and generates comparison charts with matplotlib.
"""

import time
import os
import random
import json

from data_structures.song import Song, Genre
from data_structures.bst import SongCatalogue
from data_structures.heap import AutoplayQueue
from data_structures.doubly_linked_list import Playlist

SIZES = [50, 200, 1000, 5000, 20000]
GENRES = list(Genre)


def generate_test_songs(n, seed=42):
    rng = random.Random(seed)
    songs = []
    for i in range(n):
        songs.append(Song(
            song_id=f"s{i:06d}",
            title=f"Title{i:06d}",
            artist=f"Artist{rng.randint(1, max(n // 5, 10))}",
            album=f"Album{rng.randint(1, max(n // 10, 5))}",
            genre=rng.choice(GENRES),
            duration_seconds=rng.randint(120, 360),
            play_count=rng.randint(0, 500),
            like_count=rng.randint(0, 200),
            last_played=float(rng.randint(0, 1000)),
        ))
    return songs


def benchmark_bst_insert(songs):
    cat = SongCatalogue()
    start = time.perf_counter()
    for s in songs:
        cat.insert(s)
    elapsed = time.perf_counter() - start
    return elapsed, cat


def benchmark_bst_search(cat, songs):
    start = time.perf_counter()
    for s in songs:
        cat.search(s.title)
    return time.perf_counter() - start


def benchmark_bst_height(cat):
    return cat.height()


def benchmark_bst_in_order(cat):
    start = time.perf_counter()
    cat.in_order_traversal()
    return time.perf_counter() - start


def benchmark_heap_insert(songs):
    max_likes = max(s.like_count for s in songs)
    max_plays = max(s.play_count for s in songs)
    now = max(s.last_played for s in songs)
    q = AutoplayQueue(max_likes=max_likes, max_plays=max_plays, now=now)
    start = time.perf_counter()
    for s in songs:
        q.add_to_autoplay(s)
    elapsed = time.perf_counter() - start
    return elapsed, q


def benchmark_heap_extract(q, n):
    start = time.perf_counter()
    for _ in range(min(n, len(q))):
        q.next_autoplay()
    return time.perf_counter() - start


def benchmark_dll_insert(songs):
    pl = Playlist()
    start = time.perf_counter()
    for s in songs:
        pl.add_song(s)
    elapsed = time.perf_counter() - start
    return elapsed, pl


def benchmark_dll_traverse(pl):
    start = time.perf_counter()
    list(pl)
    return time.perf_counter() - start


def run_benchmarks():
    """Run all benchmarks and return results dict."""
    results = {
        "sizes": SIZES,
        "bst_insert": [],
        "bst_search": [],
        "bst_height": [],
        "bst_in_order": [],
        "heap_insert": [],
        "heap_extract": [],
        "dll_insert": [],
        "dll_traverse": [],
    }
    for n in SIZES:
        print(f"  Benchmarking N={n}...")
        songs = generate_test_songs(n)
        # BST
        t, cat = benchmark_bst_insert(songs)
        results["bst_insert"].append(round(t, 6))
        results["bst_search"].append(round(benchmark_bst_search(cat, songs), 6))
        results["bst_height"].append(benchmark_bst_height(cat))
        results["bst_in_order"].append(round(benchmark_bst_in_order(cat), 6))
        # Heap
        t, q = benchmark_heap_insert(songs)
        results["heap_insert"].append(round(t, 6))
        results["heap_extract"].append(round(benchmark_heap_extract(q, n), 6))
        # DLL
        t, pl = benchmark_dll_insert(songs)
        results["dll_insert"].append(round(t, 6))
        results["dll_traverse"].append(round(benchmark_dll_traverse(pl), 6))
    return results


def plot_results(results, output_dir="."):
    """Generate performance charts and save to output_dir."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sizes = results["sizes"]

    # Chart 1: Insertion times
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(sizes, results["bst_insert"], "o-", label="BST Insert", color="royalblue")
    ax.plot(sizes, results["heap_insert"], "s-", label="Heap Insert", color="coral")
    ax.plot(sizes, results["dll_insert"], "^-", label="DLL Insert", color="seagreen")
    ax.set_xlabel("N (number of songs)")
    ax.set_ylabel("Time (seconds)")
    ax.set_title("Insertion Performance Comparison")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale("log")
    ax.set_yscale("log")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "benchmark_insert.png"), dpi=150)
    plt.close(fig)

    # Chart 2: Search / Extract / Traverse
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(sizes, results["bst_search"], "o-", label="BST Search", color="royalblue")
    ax.plot(sizes, results["heap_extract"], "s-", label="Heap Extract-Max", color="coral")
    ax.plot(sizes, results["dll_traverse"], "^-", label="DLL Traverse", color="seagreen")
    ax.plot(sizes, results["bst_in_order"], "D-", label="BST In-Order", color="purple")
    ax.set_xlabel("N (number of songs)")
    ax.set_ylabel("Time (seconds)")
    ax.set_title("Search / Extract / Traverse Performance")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale("log")
    ax.set_yscale("log")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "benchmark_search.png"), dpi=150)
    plt.close(fig)

    # Chart 3: BST height vs ideal (log2 N)
    import math
    fig, ax = plt.subplots(figsize=(10, 6))
    ideal = [math.log2(n) if n > 0 else 0 for n in sizes]
    ax.plot(sizes, results["bst_height"], "o-", label="Actual BST Height", color="crimson")
    ax.plot(sizes, ideal, "--", label="Ideal (log2 N)", color="gray")
    ax.set_xlabel("N (number of songs)")
    ax.set_ylabel("Height")
    ax.set_title("BST Height: Actual vs Ideal (Degeneration Check)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale("log")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "benchmark_height.png"), dpi=150)
    plt.close(fig)

    print(f"  Charts saved to {output_dir}/benchmark_*.png")


def print_results(results):
    """Print a formatted table of results."""
    print("\n" + "=" * 80)
    print(f"{'N':>8} | {'BST Insert':>12} | {'BST Search':>12} | {'BST Height':>12} | {'Heap Insert':>12} | {'Heap Extract':>13} | {'DLL Insert':>12}")
    print("-" * 80)
    for i, n in enumerate(results["sizes"]):
        print(f"{n:>8} | {results['bst_insert'][i]:>12.6f} | {results['bst_search'][i]:>12.6f} | {results['bst_height'][i]:>12} | {results['heap_insert'][i]:>12.6f} | {results['heap_extract'][i]:>13.6f} | {results['dll_insert'][i]:>12.6f}")
    print("=" * 80)


if __name__ == "__main__":
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    print("Running performance benchmarks...")
    results = run_benchmarks()
    print_results(results)
    plot_results(results, output_dir)
    # Save raw results as JSON
    with open(os.path.join(output_dir, "benchmark_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nRaw results saved to {output_dir}/benchmark_results.json")
    print("Done!")
