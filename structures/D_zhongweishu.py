"""
structures/D_zhongweishu.py
============================
Task 4 扩展 — 双堆求中位数  成员D 负责

╔══════════════════════════════════════════════════════════════╗
║  功能: 用一个最大堆(左半) + 一个最小堆(右半)                ║
║        动态维护数据流的中位数                                ║
║                                                              ║
║  原理:                                                       ║
║    - 左堆存较小的一半（用负数模拟最大堆）                    ║
║    - 右堆存较大的一半（最小堆）                              ║
║    - 两堆平衡后，中位数 = 左堆顶 或 (左堆顶+右堆顶)/2       ║
╚══════════════════════════════════════════════════════════════╝

【调用链】
  MedianFinder
    ├→ MinHeap.push() / MinHeap.pop() / MinHeap.peek()  【成员D: D_dui】
    └→ 被 D_bofang_gongju.py 的 ScoreMedianReporter / find_median_score_songs 调用
"""

from structures.D_dui import MinHeap
from typing import Optional


class MedianFinder:
    """
    双堆动态中位数查找器。

    使用两个堆维护数据流:
      _left  — 存较小一半元素（用负数存入 MinHeap 模拟最大堆效果）
      _right — 存较大一半元素（MinHeap）

    平衡条件: len(_left) == len(_right) 或 len(_left) == len(_right) + 1

    使用示例:
        >>> mf = MedianFinder()
        >>> mf.add_num(3.5)
        >>> mf.add_num(7.2)
        >>> mf.add_num(1.0)
        >>> print(mf.find_median())  # 3.5
    """

    def __init__(self):
        """初始化左右两个空堆。"""
        self._left = MinHeap()    # 存较小一半，用负数 = 最大堆效果
        self._right = MinHeap()   # 存较大一半，标准最小堆

    # ── 操作1: add_num ─ 添加数值 O(log n) ─────────────────

    def add_num(self, num: float) -> None:
        """
        向数据流中添加一个数值，自动维护两堆平衡。

        算法:
          1. 如果左堆为空 或 num <= 左堆最大值 → 放入左堆（取负）
          2. 否则 → 放入右堆
          3. 平衡: 左堆最多比右堆多1个元素
        """
        # ── 决定放入哪个堆 ──
        if self._left.is_empty() or num <= -self._left.peek():
            self._left.push(-num)          # ★ 调用 MinHeap.push()
        else:
            self._right.push(num)          # ★ 调用 MinHeap.push()

        # ── 平衡两个堆的大小 ──
        if self._left.size() > self._right.size() + 1:
            # 左堆太多 → 移动最大值到右堆
            self._right.push(-self._left.pop())   # ★ 调用 MinHeap.pop()
        elif self._right.size() > self._left.size():
            # 右堆太多 → 移动最小值到左堆
            self._left.push(-self._right.pop())   # ★ 调用 MinHeap.pop()

    # ── 操作2: find_median ─ 获取中位数 O(1) ──────────────

    def find_median(self) -> Optional[float]:
        """
        获取当前数据流的中位数。

        返回:
            - 总数为奇数 → 左堆顶（即较小一半的最大值）
            - 总数为偶数 → (左堆顶 + 右堆顶) / 2
            - 无数据   → None
        """
        if self._left.is_empty():
            return None
        if self._left.size() == self._right.size():
            return (-self._left.peek() + self._right.peek()) / 2.0
        return float(-self._left.peek())

    # ── 辅助属性 ──────────────────────────────────────────

    def size(self) -> int:
        """返回当前数据流中的元素总数。"""
        return self._left.size() + self._right.size()

    def is_empty(self) -> bool:
        """判断数据流是否为空。"""
        return self._left.is_empty() and self._right.is_empty()
