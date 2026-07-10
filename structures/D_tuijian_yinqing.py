"""
structures/D_tuijian_yinqing.py
================================
Part 2 — Task 3: 推荐引擎（Recommendation Engine） 成员D 负责

╔══════════════════════════════════════════════════════════════╗
║  当用户播放列表结束时，推荐 5 首歌曲。                       ║
║                                                              ║
║  推荐流水线（三步联动三种结构）:                              ║
║    1. BST  → 找到与当前歌曲相似流派/相同艺术家的候选歌曲     ║
║    2. Heap → 按 Autoplay 评分对候选排序                      ║
║    3. 链表 → 排除已在播放列表中的歌曲（O(1) 查找）           ║
║                                                              ║
║  最终返回 Top-5 推荐                                         ║
╚══════════════════════════════════════════════════════════════╝

【调用链总览】
  recommend_songs(playlist, bst, autoplay_heap, n=5)
    ├→ BST.inorder_traversal()              【成员C: C_ercha_sousuo_shu】
    │     └→ 遍历BST获取全部歌曲（可按流派/艺术家过滤）
    ├→ Playlist.__contains__()              【成员B: B_bofang_liebiao】
    │     └→ O(1) 查重：排除已在播放列表中的歌曲
    ├→ AutoplayHeap.compute_score(song)     【成员D: D_dui】
    │     └→ 计算候选歌曲的优先级评分
    └→ MaxHeap                              【成员D: D_dui】
          └→ 堆排序取 Top-N

负责人：成员 D
"""

from structures.D_dui import AutoplayHeap, MaxHeap, HeapNode
from typing import Optional


# ============================================================================
# 【推荐引擎核心】recommend_songs — 三步流水线推荐
# ============================================================================

def recommend_songs(playlist, bst, n: int = 5,
                    prefer_genre: bool = True) -> list:
    """
    Part 2 Task 3 — 基于当前播放列表推荐 N 首歌曲。

    推荐流水线:
      ┌─────────────────────────────────────────────────────┐
      │ Step 1: BST 发现候选                                │
      │   获取当前歌曲的 genre 和 artist                     │
      │   → BST 中序遍历全部歌曲                             │
      │   → 筛选: 同流派 或 同艺术家 的歌曲                  │
      │                                                      │
      │ Step 2: 链表排除                                     │
      │   → 用 playlist.__contains__() O(1) 排除已存在的     │
      │                                                      │
      │ Step 3: 堆排序                                       │
      │   → AutoplayHeap.compute_score() 计算每首候选的评分  │
      │   → MaxHeap 取 Top-N                                 │
      └─────────────────────────────────────────────────────┘

    参数:
        playlist:     Playlist 播放列表（成员B）
        bst:          BST 歌曲目录（成员C）
        n:            推荐数量，默认 5
        prefer_genre: True=优先同流派，False=优先同艺术家

    返回:
        list[Song]: Top-N 推荐歌曲列表

    使用示例:
        >>> recs = recommend_songs(playlist, bst, n=5)
        >>> for s in recs:
        ...     print(f"推荐: {s.title} — {s.artist} [{s.genre.value}]")
    """
    if playlist is None or bst is None:
        return []

    # ── Step 0: 获取当前播放歌曲的上下文 ──
    current_song = playlist.current_song()
    if current_song is None:
        # 没在播放 → 返回全局评分最高的 N 首
        return _recommend_global_top(bst, playlist, n)

    current_genre = current_song.genre
    current_artist = current_song.artist

    # ── Step 1: BST → 发现候选歌曲 ──
    # 调用: BST.inorder_traversal() 【成员C: C_ercha_sousuo_shu】
    # 遍历全部歌曲，筛选同流派 + 同艺术家的歌曲
    all_songs = bst.inorder_traversal()  # ★ 调用成员C

    candidates: list = []
    seen_ids: set[str] = set()

    # 第一轮: 同流派 + 同艺术家（最佳匹配）
    for song in all_songs:
        if song.song_id in seen_ids:
            continue
        if song == current_song:
            continue
        if song.genre == current_genre and song.artist == current_artist:
            candidates.append((song, 3))  # 优先级 3（最高）
            seen_ids.add(song.song_id)

    # 第二轮: 同流派（次优）
    if prefer_genre:
        for song in all_songs:
            if song.song_id in seen_ids:
                continue
            if song == current_song:
                continue
            if song.genre == current_genre:
                candidates.append((song, 2))
                seen_ids.add(song.song_id)

        # 第三轮: 同艺术家
        for song in all_songs:
            if song.song_id in seen_ids:
                continue
            if song == current_song:
                continue
            if song.artist == current_artist:
                candidates.append((song, 1))
                seen_ids.add(song.song_id)
    else:
        # 同艺术家优先
        for song in all_songs:
            if song.song_id in seen_ids:
                continue
            if song == current_song:
                continue
            if song.artist == current_artist:
                candidates.append((song, 2))
                seen_ids.add(song.song_id)
        for song in all_songs:
            if song.song_id in seen_ids:
                continue
            if song == current_song:
                continue
            if song.genre == current_genre:
                candidates.append((song, 1))
                seen_ids.add(song.song_id)

    # ── Step 2: 链表 → 排除已在播放列表中的歌曲 ──
    # 调用: playlist.__contains__() 【成员B: B_bofang_liebiao】O(1)
    filtered = []
    for song, priority in candidates:
        if song.song_id not in playlist:  # ★ 调用成员B: O(1) 查重
            filtered.append((song, priority))

    # ── Step 3: 堆 → 按评分排序取 Top-N ──
    # 调用: AutoplayHeap.compute_score() 【成员D: D_dui】
    # 调用: MaxHeap 【成员D: D_dui】
    if not filtered:
        # 候选都在播放列表中 → 取消去重，直接用候选
        filtered = candidates

    heap = MaxHeap()  # ★ 调用成员D: MaxHeap
    for song, priority in filtered:
        score = AutoplayHeap.compute_score(song)  # ★ 调用成员D: 评分公式
        # 综合评分 = 基础评分 + 优先级加权
        final_score = score + priority * (score * 0.3)
        heap.push(HeapNode(song, final_score))  # ★ 调用 MaxHeap.push

    # 弹出 Top-N
    result = []
    while not heap.is_empty() and len(result) < n:
        node = heap.pop()  # ★ 调用 MaxHeap.pop
        if node:
            result.append(node.song)

    # 不够 N 首 → 从全局补
    if len(result) < n:
        extra = _recommend_global_top(bst, playlist, n - len(result),
                                      exclude_ids={s.song_id for s in result})
        result.extend(extra)

    return result[:n]


# ============================================================================
# 辅助: _recommend_global_top — 全局 Top-N（当无上下文时）
# ============================================================================

def _recommend_global_top(bst, playlist, n: int = 5,
                          exclude_ids: set = None) -> list:
    """
    从全局取评分最高的 N 首歌曲（排除已在播放列表中的）。

    调用链:
      BST.inorder_traversal()   【成员C】
      playlist.__contains__()   【成员B】
      AutoplayHeap.compute_score() 【成员D】
      MaxHeap                   【成员D】
    """
    if exclude_ids is None:
        exclude_ids = set()

    all_songs = bst.inorder_traversal()  # ★ 调用成员C
    heap = MaxHeap()  # ★ 调用成员D

    for song in all_songs:
        if song.song_id in exclude_ids:
            continue
        score = AutoplayHeap.compute_score(song)  # ★ 调用成员D
        heap.push(HeapNode(song, score))

    result = []
    while not heap.is_empty() and len(result) < n:
        node = heap.pop()
        if node:
            result.append(node.song)

    return result
