"""
structures/D_bofang_gongju.py
==============================
Task 4 扩展 — 音乐播放高级工具集  成员D 负责

╔══════════════════════════════════════════════════════════════╗
║  包含以下工具:                                               ║
║                                                              ║
║  1. HotColdBalancer      — 冷热均衡播放器                   ║
║     按 hot_ratio 概率从热门/冷门堆中选取歌曲，              ║
║     避免只播热门歌，增加播放多样性                           ║
║                                                              ║
║  2. ScoreMedianReporter  — 评分中位数报告器                  ║
║     统计歌曲评分的中位数，了解整体质量分布                   ║
║                                                              ║
║  3. merge_playlists()    — 合并多个播放列表                  ║
║     利用K路归并将多个列表按评分合并                          ║
║                                                              ║
║  4. find_median_score_songs() — 找中位数评分附近的歌曲       ║
║     返回评分在中位数上下最近的两首歌                         ║
╚══════════════════════════════════════════════════════════════╝

【调用链总览】
  HotColdBalancer
    ├→ MaxHeap.push/pop/peek/is_empty        【成员D: D_dui】
    ├→ MinHeap.push/pop/peek/is_empty        【成员D: D_dui】
    └→ HeapNode (song + score 节点)          【成员D: D_dui】

  ScoreMedianReporter
    └→ MedianFinder.add_num / find_median    【成员D: D_zhongweishu】

  merge_playlists()
    ├→ MergeKSorted.merge()                  【成员D: D_guibing_hebing】
    └→ AutoplayHeap.compute_score()          【成员D: D_dui】

  find_median_score_songs()
    ├→ MedianFinder()                        【成员D: D_zhongweishu】
    └→ AutoplayHeap.compute_score()          【成员D: D_dui】
"""

import random
from typing import Optional

from structures.D_dui import MinHeap, MaxHeap, HeapNode, AutoplayHeap
from structures.D_zhongweishu import MedianFinder
from structures.D_guibing_hebing import MergeKSorted


# ============================================================================
# 【工具1】HotColdBalancer — 冷热均衡播放器
# ============================================================================
# 问题: 纯按评分播放总是播热门歌，用户听不到冷门好歌
# 方案: 热门歌放 MaxHeap（评分高优先），冷门歌放 MinHeap（评分低也保留）
#       每次以一定概率(ratio)从热门或冷门堆中选取

class HotColdBalancer:
    """
    冷热均衡播放器。

    原理:
      - 热门堆（MaxHeap）: 高分歌曲，以 hot_ratio 概率从这里选
      - 冷门堆（MinHeap）: 低分歌曲，以 1-hot_ratio 概率从这里选
      - 两堆存相同的歌曲，各自按评分排序

    使用示例:
        >>> balancer = HotColdBalancer(hot_ratio=0.7)
        >>> balancer.add_song(song, score=95.5)
        >>> next_song = balancer.next()  # 70%概率热歌, 30%概率冷门
    """

    def __init__(self, hot_ratio: float = 0.7):
        """
        初始化冷热均衡器。

        参数:
            hot_ratio: 选热门歌的概率（0~1），默认 0.7
        """
        self.hot = MaxHeap()    # ★ 调用成员D: MaxHeap — 热门歌（评分从高到低）
        self.cold = MinHeap()   # ★ 调用成员D: MinHeap — 冷门歌（评分从低到高）
        self.ratio = hot_ratio

    # ── add_song ─ 添加歌曲 O(log n) ──────────────────────

    def add_song(self, song, score: float) -> None:
        """
        将歌曲同时加入热门堆和冷门堆。

        参数:
            song:  Song 对象
            score: 优先级评分
        """
        node = HeapNode(song, score)  # ★ 调用成员D: HeapNode
        self.hot.push(node)           # ★ 调用 MaxHeap.push
        self.cold.push(node)          # ★ 调用 MinHeap.push

    # ── next ─ 获取下一首 O(log n) ────────────────────────

    def next(self):
        """
        按冷热概率选取下一首歌曲。

        返回:
            Song 对象 或 None（队列为空时）
        """
        if self.hot.is_empty() and self.cold.is_empty():
            return None

        use_hot = random.random() < self.ratio

        if use_hot and not self.hot.is_empty():
            n = self.hot.pop()  # ★ 调用 MaxHeap.pop
            if n:
                return n.song
        if not self.cold.is_empty():
            n = self.cold.pop()  # ★ 调用 MinHeap.pop
            if n:
                return n.song

        # 兜底: 某个堆为空时从另一个取
        n = self.hot.pop() or self.cold.pop()
        return n.song if n else None

    # ── 辅助 ─────────────────────────────────────────────

    def peek_next(self):
        """查看下一首但不移除。"""
        n = self.hot.peek() or self.cold.peek()
        return n.song if n else None

    def size(self) -> int:
        """总歌曲数（两个堆各存一份，所以除以2）。"""
        return self.hot.size()  # hot 和 cold 大小相同

    def is_empty(self) -> bool:
        return self.hot.is_empty() and self.cold.is_empty()


# ============================================================================
# 【工具2】ScoreMedianReporter — 评分中位数报告器
# ============================================================================
# 场景: 想知道播放列表中歌曲评分的"中等水平"在哪里

class ScoreMedianReporter:
    """
    歌曲评分中位数统计器。

    使用 MedianFinder（双堆法）动态计算评分中位数。

    调用链:
      feed_song(song)
        └→ AutoplayHeap.compute_score(song)  【成员D: D_dui】
        └→ MedianFinder.add_num(score)       【成员D: D_zhongweishu】

      feed_autoplay_heap(heap)
        └→ AutoplayHeap.display_all()        【成员D: D_dui】
        └→ MedianFinder.add_num(score)       【成员D: D_zhongweishu】

      report()
        └→ MedianFinder.find_median()        【成员D: D_zhongweishu】
    """

    def __init__(self):
        self._finder = MedianFinder()  # ★ 调用成员D: D_zhongweishu

    def feed_song(self, song) -> None:
        """
        喂入一首歌曲，计算评分并更新中位数。

        参数:
            song: Song 对象
        """
        score = AutoplayHeap.compute_score(song)  # ★ 调用成员D: D_dui
        self._finder.add_num(score)               # ★ 调用 D_zhongweishu

    def feed_autoplay_heap(self, heap: AutoplayHeap) -> None:
        """
        从 AutoplayHeap 批量喂入所有歌曲的评分。

        参数:
            heap: AutoplayHeap 实例
        """
        for info in heap.display_all():  # ★ 调用 AutoplayHeap.display_all
            self._finder.add_num(info["score"])  # ★ 调用 MedianFinder.add_num

    def report(self) -> dict:
        """
        返回评分中位数统计报告。

        返回:
            {"median": 中位数值, "total": 歌曲总数}
        """
        med = self._finder.find_median()  # ★ 调用 MedianFinder.find_median
        if med is not None:
            return {"median": med, "total": self._finder.size()}
        return {"median": None, "total": 0}


# ============================================================================
# 【工具3】merge_playlists — 合并多个播放列表
# ============================================================================

def merge_playlists(playlists: list, by_score: bool = True) -> list:
    """
    将多个播放列表（list[Song]）合并为一个有序列表。

    参数:
        playlists: 歌曲列表的列表
        by_score:  True=按评分降序合并, False=按song_id合并

    返回:
        合并后的 Song 列表

    调用链:
      MergeKSorted.merge()              【成员D: D_guibing_hebing】
      AutoplayHeap.compute_score(song)  【成员D: D_dui】（当 by_score=True）

    示例:
        >>> merged = merge_playlists([pop_list, rock_list])
    """
    if by_score:
        return MergeKSorted.merge(
            playlists,
            key=lambda s: -AutoplayHeap.compute_score(s)  # ★ 调用 D_dui + D_guibing_hebing
        )
    return MergeKSorted.merge(playlists, key=lambda s: s.song_id)


# ============================================================================
# 【工具4】find_median_score_songs — 找中位数附近的歌曲
# ============================================================================

def find_median_score_songs(songs: list) -> tuple:
    """
    找出评分最接近中位数的两首歌曲（低于和高于中位数的各一首）。

    参数:
        songs: Song 对象列表

    返回:
        (below_median_song, above_median_song) — 两者都可能为 None

    调用链:
      AutoplayHeap.compute_score(song)  【成员D: D_dui】
      MedianFinder.add_num(score)       【成员D: D_zhongweishu】
      MedianFinder.find_median()        【成员D: D_zhongweishu】
    """
    if not songs:
        return (None, None)

    finder = MedianFinder()  # ★ 调用成员D: D_zhongweishu

    # 计算每首歌评分并喂入 MedianFinder
    scored = [(AutoplayHeap.compute_score(s), s) for s in songs]  # ★ 调用 D_dui
    for sc, _ in scored:
        finder.add_num(sc)  # ★ 调用 D_zhongweishu

    med = finder.find_median()  # ★ 调用 D_zhongweishu
    if med is None:
        return (None, None)

    # 找中位数附近的两首歌
    scored.sort(key=lambda x: x[0])
    below, above = None, None
    for sc, song in scored:
        if sc <= med:
            below = song
        if sc >= med and above is None:
            above = song

    return (below, above)
