"""
structures/D_guibing_hebing.py
===============================
Task 4 扩展 — K路归并合并  成员D 负责

╔══════════════════════════════════════════════════════════════╗
║  功能: 使用最小堆实现 K 个有序列表的高效合并                ║
║                                                              ║
║  原理:                                                       ║
║    1. 每个列表的第一个元素入堆（堆节点记录值+来源+位置）     ║
║    2. 弹出堆顶（当前最小）加入结果                          ║
║    3. 从弹出元素所属列表取下一个元素入堆                    ║
║    4. 重复直到堆空                                          ║
║                                                              ║
║  应用场景:                                                   ║
║    - 合并多个已排序的播放列表                                ║
║    - 按评分合并多个推荐队列                                  ║
╚══════════════════════════════════════════════════════════════╝

【调用链】
  MergeKSorted
    ├→ MinHeap.push() / MinHeap.pop() / MinHeap.is_empty()  【成员D: D_dui】
    └→ 被 D_bofang_gongju.py 的 merge_playlists() 调用
"""

from structures.D_dui import MinHeap
from typing import List, Any, Callable, Optional


# ============================================================================
# 内部辅助: _HeapItem — 堆节点（存储值+来源列表索引+元素位置）
# ============================================================================

class _HeapItem:
    """K路归并用的堆节点。记录元素值、来自哪个列表、在列表中的位置。"""

    def __init__(self, value, list_idx: int, element_idx: int):
        self.value = value
        self.list_idx = list_idx
        self.element_idx = element_idx

    def __lt__(self, other) -> bool:
        """比较两个堆节点（按值的大小）。用于 MinHeap 排序。"""
        return self.value < other.value


# ============================================================================
# MergeKSorted — K路归并器
# ============================================================================

class MergeKSorted:
    """
    K路归并排序器。

    使用场景:
      - merge(lists, key=None): 合并K个有序列表
      - merge_by_score(song_lists, score_fn): 按评分降序合并歌曲列表
    """

    @staticmethod
    def merge(lists: list, key: Optional[Callable] = None) -> list:
        """
        合并 K 个有序列表为一个有序列表。

        参数:
            lists: 有序列表的列表（如 [[1,3,5], [2,4,6]]）
            key:   可选，提取比较键的函数

        返回:
            合并后的有序列表

        调用链:
          1. MinHeap()                    【成员D: D_dui】
          2. heap.push(_HeapItem(...))    【成员D: MinHeap.push】
          3. heap.pop()                   【成员D: MinHeap.pop】
          4. heap.is_empty()              【成员D: MinHeap.is_empty】

        示例:
            >>> MergeKSorted.merge([[1,4],[2,5],[3,6]])
            [1, 2, 3, 4, 5, 6]
        """
        # ── 过滤空列表，记录有效列表索引 ──
        active = [(i, lst) for i, lst in enumerate(lists) if lst]
        if not active:
            return []

        heap = MinHeap()  # ★ 调用成员D: MinHeap
        result = []

        # ── 初始化: 每个列表的第一个元素入堆 ──
        for idx, lst in active:
            val = lst[0] if key is None else key(lst[0])
            heap.push(_HeapItem(val, idx, 0))  # ★ 调用 MinHeap.push

        # ── 反复弹出最小值，补充同列表的下一个 ──
        while not heap.is_empty():  # ★ 调用 MinHeap.is_empty
            item = heap.pop()  # ★ 调用 MinHeap.pop
            # 取原始值（如用了 key 则从原列表取）
            result.append(
                item.value if key is None
                else lists[item.list_idx][item.element_idx]
            )

            nxt = item.element_idx + 1
            if nxt < len(lists[item.list_idx]):
                lst = lists[item.list_idx]
                val = lst[nxt] if key is None else key(lst[nxt])
                heap.push(_HeapItem(val, item.list_idx, nxt))  # ★ 调用 MinHeap.push

        return result

    @staticmethod
    def merge_by_score(song_lists: list, score_fn: Callable) -> list:
        """
        按评分降序合并多个歌曲列表。

        原理: 评分越高越优先 → 用 -score 作为堆键（最小堆弹出的是-score最小的=评分最高的）

        参数:
            song_lists: 歌曲列表的列表（每个子列表已按评分排序）
            score_fn:   计算歌曲评分的函数

        返回:
            按评分降序排列的合并歌曲列表

        示例:
            >>> from data.A_shuju_jiazai import compute_autoplay_score
            >>> merged = MergeKSorted.merge_by_score(
            ...     [pop_songs, rock_songs], compute_autoplay_score)
        """
        return MergeKSorted.merge(song_lists, key=lambda item: -score_fn(item))
