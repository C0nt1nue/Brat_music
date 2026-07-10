"""
structures/C_xingneng_ceshi.py
===============================
Part 2 — Task 4: 性能基准测试（Empirical Benchmarking） 成员C 负责

╔══════════════════════════════════════════════════════════════╗
║  对三种结构进行跨规模的性能测量:                             ║
║                                                              ║
║  测试项:                                                     ║
║    1. BST 插入时间 — 最好情况(随机序) vs 最坏情况(有序)     ║
║    2. BST 搜索时间                                          ║
║    3. Heap 插入 + 提取 时间                                 ║
║    4. 链表 shuffle 时间                                     ║
║                                                              ║
║  测试规模: N = 50, 200, 1000, 5000, 20000                   ║
║                                                              ║
║  输出: 终端表格 + matplotlib 图表                           ║
╚══════════════════════════════════════════════════════════════╝

【调用链】
  benchmark_all()
    ├→ BST() / bst.insert() / bst.search()      【成员C: C_ercha_sousuo_shu】
    ├→ AutoplayHeap() / add_to_autoplay() / next_autoplay()【成员D: D_dui】
    ├→ Playlist() / add_song() / shuffle()      【成员B: B_bofang_liebiao】
    └→ matplotlib.pyplot                        【外部库】

负责人：成员 C
"""

import sys
import time
import random
import math
from pathlib import Path

# 确保项目路径
_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from models.A_gequ import Song
from models.liupai import Genre
from structures.C_ercha_sousuo_shu import BST
from structures.D_dui import AutoplayHeap
from structures.B_bofang_liebiao import Playlist

# matplotlib 可选
try:
    import matplotlib.pyplot as plt
    _HAS_PLT = True
except ImportError:
    _HAS_PLT = False
    plt = None


# ============================================================================
# 【辅助】生成测试歌曲
# ============================================================================

_GENRES = list(Genre)

def _make_song(idx: int) -> Song:
    """生成一首测试歌曲。"""
    g = _GENRES[idx % len(_GENRES)]
    return Song(
        song_id=f"B{idx:06d}",
        title=f"Benchmark Song {idx:06d}",
        artist=f"Artist {idx % 5000}",
        album=f"Album {idx % 2000}",
        genre=g,
        duration_seconds=random.randint(60, 600),
        play_count=random.randint(0, 100000),
        like_count=random.randint(0, 50000),
    )


# ============================================================================
# 【单项测试函数】
# ============================================================================

def benchmark_bst_insert_random(n: int) -> float:
    """BST 插入 N 首随机序歌曲的时间（最好情况）。"""
    songs = [_make_song(i) for i in range(n)]
    random.shuffle(songs)  # 随机顺序 → 接近平衡树
    bst = BST()
    t0 = time.perf_counter()
    for s in songs:
        bst.insert(s)  # ★ 调用成员C BST.insert
    return time.perf_counter() - t0


def benchmark_bst_insert_sorted(n: int) -> float:
    """BST 插入 N 首有序歌曲的时间（最坏情况 → 退化为链表）。"""
    songs = [_make_song(i) for i in range(n)]
    # 已按 title 字母序排列 → 退化为 O(n²)
    bst = BST()
    t0 = time.perf_counter()
    for s in songs:
        bst.insert(s)  # ★ 调用成员C BST.insert
    return time.perf_counter() - t0


def benchmark_bst_search(n: int) -> float:
    """BST 搜索一首歌的时间。"""
    songs = [_make_song(i) for i in range(n)]
    random.shuffle(songs)
    bst = BST()
    for s in songs:
        bst.insert(s)

    target = songs[n // 3].title  # 搜索中间位置的一首
    t0 = time.perf_counter()
    for _ in range(100):  # 重复100次取平均
        bst.search(target)  # ★ 调用成员C BST.search
    return (time.perf_counter() - t0) / 100


def benchmark_heap_ops(n: int) -> dict:
    """堆插入 + 提取时间。"""
    songs = [_make_song(i) for i in range(n)]
    heap = AutoplayHeap()  # ★ 调用成员D

    # 插入
    t0 = time.perf_counter()
    for s in songs:
        score = AutoplayHeap.compute_score(s)
        heap.add_to_autoplay(s, score)  # ★ 调用成员D
    insert_time = time.perf_counter() - t0

    # 提取全部
    t0 = time.perf_counter()
    while not heap.is_empty():
        heap.next_autoplay()  # ★ 调用成员D
    extract_time = time.perf_counter() - t0

    return {"insert": insert_time, "extract": extract_time}


def benchmark_shuffle(n: int) -> float:
    """链表 shuffle 时间。"""
    songs = [_make_song(i) for i in range(n)]
    pl = Playlist()
    for s in songs:
        pl.add_song(s)  # ★ 调用成员B

    t0 = time.perf_counter()
    pl.shuffle()  # ★ 调用成员B Playlist.shuffle
    return time.perf_counter() - t0


# ============================================================================
# 【主函数】benchmark_all — 全部规模全部测试
# ============================================================================

# 测试规模
SIZES = [50, 200, 1000, 5000, 20000]


def benchmark_all(plot: bool = True) -> dict:
    """
    运行全部基准测试，返回结果字典并可选绘图。

    返回格式:
        { N: {
            "bst_insert_random": float,
            "bst_insert_sorted": float,
            "bst_search": float,
            "heap_insert": float,
            "heap_extract": float,
            "shuffle": float,
        }, ... }
    """
    results: dict = {}

    print("=" * 80)
    print("  Part 2 — Task 4: 性能基准测试")
    print("  成员 C  |  BST / Heap / Shuffle 跨规模性能对比")
    print("=" * 80)

    for n in SIZES:
        print(f"\n── N = {n:,} ──────────────────────────────")

        # BST 插入 (随机序)
        t_random = benchmark_bst_insert_random(n)
        print(f"  BST 插入 (随机序)      {t_random:10.4f}s")

        # BST 插入 (有序 — 最坏情况)
        t_sorted = benchmark_bst_insert_sorted(n)
        print(f"  BST 插入 (有序-最坏)   {t_sorted:10.4f}s")

        # BST 搜索
        t_search = benchmark_bst_search(n)
        print(f"  BST 搜索 (100次平均)   {t_search:10.6f}s")

        # 堆操作
        heap_t = benchmark_heap_ops(n)
        print(f"  堆 插入 {n} 首          {heap_t['insert']:10.4f}s")
        print(f"  堆 提取 {n} 首          {heap_t['extract']:10.4f}s")

        # 链表 shuffle
        t_shuffle = benchmark_shuffle(n)
        print(f"  链表 shuffle            {t_shuffle:10.4f}s")

        results[n] = {
            "bst_insert_random": t_random,
            "bst_insert_sorted": t_sorted,
            "bst_search": t_search,
            "heap_insert": heap_t["insert"],
            "heap_extract": heap_t["extract"],
            "shuffle": t_shuffle,
        }

    # ── 汇总表 ──
    print("\n" + "=" * 80)
    print("  性能汇总表")
    print("=" * 80)
    header = f"  {'N':>6} | {'BST随机插入':>12} | {'BST有序插入':>12} | {'BST搜索':>10} | {'堆插入':>10} | {'堆提取':>10} | {'shuffle':>10}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for n in SIZES:
        r = results[n]
        print(f"  {n:>6} | {r['bst_insert_random']:>12.4f} | {r['bst_insert_sorted']:>12.4f} | "
              f"{r['bst_search']:>10.6f} | {r['heap_insert']:>10.4f} | "
              f"{r['heap_extract']:>10.4f} | {r['shuffle']:>10.4f}")

    # ── 分析与建议 ──
    print("\n" + "=" * 80)
    print("  分析与解读")
    print("=" * 80)
    _print_analysis(results)

    # ── 绘图 ──
    if plot and _HAS_PLT:
        _plot_results(results)
    elif plot and not _HAS_PLT:
        print("\n  ⚠️  matplotlib 未安装，跳过绘图。pip install matplotlib")

    return results


def _print_analysis(results: dict) -> None:
    """打印基准测试的文字分析。"""
    n_small = results[50]
    n_large = results[20000]

    print(f"""
  【BST 最好 vs 最坏】
    规模 50:    随机={n_small['bst_insert_random']:.4f}s  有序={n_small['bst_insert_sorted']:.4f}s
    规模 20000:  随机={n_large['bst_insert_random']:.4f}s  有序={n_large['bst_insert_sorted']:.4f}s

    分析: 有序插入导致BST退化为链表，时间复杂度从 O(n log n) 退化为 O(n²)。
          随机序能保持接近平衡，深度 ≈ log₂(n)。
          为了保证 O(log n) 在所有情况下，应使用 AVL 树或红黑树。

  【堆 vs BST】
    堆插入 20000 首:  {n_large['heap_insert']:.4f}s
    BST插入20000首:   {n_large['bst_insert_random']:.4f}s
    堆提取 20000 首:  {n_large['heap_extract']:.4f}s

    分析: 堆的插入和提取都是 O(log n)，且数组存储比 BST 的指针结构缓存更友好。
          对于只需"最大值"的场景（Autoplay），堆是比 BST 更优的选择。

  【shuffle 性能】
    规模 50:    {n_small['shuffle']:.4f}s
    规模 20000: {n_large['shuffle']:.4f}s

    分析: shuffle 需要收集所有节点到列表再重新链接，O(n)。
          大规模下主要开销在 Python list 操作和随机数生成。
""")


# ============================================================================
# 【绘图】matplotlib 双图对比
# ============================================================================

def _plot_results(results: dict) -> None:
    """绘制性能对比图。"""
    if not _HAS_PLT:
        return

    sizes = list(results.keys())
    random_times = [results[n]["bst_insert_random"] for n in sizes]
    sorted_times = [results[n]["bst_insert_sorted"] for n in sizes]
    heap_insert = [results[n]["heap_insert"] for n in sizes]
    heap_extract = [results[n]["heap_extract"] for n in sizes]
    shuffle_times = [results[n]["shuffle"] for n in sizes]
    search_times = [results[n]["bst_search"] for n in sizes]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Part 2 Task 4 — Empirical Benchmarking", fontsize=14)

    # ── 图1: BST 插入对比 + 堆 + shuffle ──
    ax1.plot(sizes, random_times, 'go-', label='BST insert (random)')
    ax1.plot(sizes, sorted_times, 'ro-', label='BST insert (sorted — worst)')
    ax1.plot(sizes, heap_insert, 'bs-', label='Heap insert')
    ax1.plot(sizes, shuffle_times, 'm^-', label='List shuffle')
    ax1.set_xlabel('N (number of songs)')
    ax1.set_ylabel('Time (seconds)')
    ax1.set_title('Insert / Shuffle Performance')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # ── 图2: BST 搜索 + 堆提取 ──
    ax2.plot(sizes, search_times, 'co-', label='BST search (avg)')
    ax2.plot(sizes, heap_extract, 'ys-', label='Heap extract all')
    ax2.set_xlabel('N (number of songs)')
    ax2.set_ylabel('Time (seconds)')
    ax2.set_title('Search / Extract Performance')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(str(_PROJECT_ROOT / "benchmark_results.png"), dpi=150)
    print(f"\n  📊 图表已保存至: benchmark_results.png")
    plt.show()
