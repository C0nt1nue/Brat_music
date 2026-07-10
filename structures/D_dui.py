"""
structures/D_dui.py
===================
Task 4 — Autoplay 队列：自定义堆（Heap）全套实现

【成员 D 负责】

本文件包含三个堆结构:
  1. MaxHeap      — 最大堆（堆顶=最大评分）→ AutoplayHeap 的底层引擎
  2. MinHeap      — 最小堆（堆顶=最小评分）→ 被 MedianFinder/K路归并 调用
  3. AutoplayHeap — Autoplay 优先级队列（基于 MaxHeap）

设计思路：
  1. 堆是一种完全二叉树，使用数组（列表）存储。
  2. 最大堆性质：父节点的值 >= 子节点的值，因此堆顶永远是优先级最高的元素。
  3. Autoplay 场景下，我们总是希望下一次播放的是"评分最高"的歌，
     所以最大堆比最小堆更自然（堆顶就是下一首要播的歌）。
  4. 所有堆操作都基于数组索引的父子关系：
     - 父节点索引: parent(i) = (i-1) // 2
     - 左孩子索引: left(i) = 2*i + 1
     - 右孩子索引: right(i) = 2*i + 2

为什么 Autoplay 用堆而不用 BST？
  - 堆的插入和提取最大值都是 O(log n)，BST 退化为链表时是 O(n)
  - 堆在内存中连续存储（数组），缓存友好
  - 我们只需要"最高优先级"的元素，不需要范围查询或中序遍历

remove_from_autoplay 的改进：
  - 删除时将要删除的元素与末尾元素交换后再弹出，同时执行上浮+下沉
  - 相比旧版 O(n) 的 pop(0)，改为 O(1) 的 pop()，避免数组搬移

实现要求（对应 Task 4 的四个核心函数）：
  1. add_to_autoplay(song, score)   -> O(log n)
  2. next_autoplay()                -> O(log n)
  3. remove_from_autoplay(song_id)  -> O(n) 查找 + O(log n) 调整
  4. update_score(song_id, new_score) -> O(n) 查找 + O(log n) 调整
"""

from typing import Optional
from models.A_gequ import Song
import math


class HeapNode:
    """Heap node storing a song and its autoplay priority score."""

    def __init__(self, song: Song, score: float):
        self.song = song
        self.score = score

    def __repr__(self) -> str:
        return "HeapNode({}, score={:.1f})".format(self.song.song_id, self.score)


class MaxHeap:
    """Custom binary max heap backed by a list (0-indexed)."""

    def __init__(self):
        self._data: list[HeapNode] = []

    def _parent(self, i: int) -> int:
        return (i - 1) // 2

    def _left(self, i: int) -> int:
        return 2 * i + 1

    def _right(self, i: int) -> int:
        return 2 * i + 2

    def _swap(self, i: int, j: int) -> None:
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def _sift_up(self, i: int) -> None:
        """上浮：新插入元素向上调整到正确位置。O(log n)"""
        while i > 0:
            p = self._parent(i)
            if self._data[i].score > self._data[p].score:
                self._swap(i, p)
                i = p
            else:
                break

    def _sift_down(self, i: int) -> None:
        """下沉：堆顶元素向下调整到正确位置。O(log n)"""
        n = len(self._data)
        while True:
            largest = i
            l = self._left(i)
            r = self._right(i)
            if l < n and self._data[l].score > self._data[largest].score:
                largest = l
            if r < n and self._data[r].score > self._data[largest].score:
                largest = r
            if largest == i:
                break
            self._swap(i, largest)
            i = largest

    def push(self, node: HeapNode) -> None:
        """插入新节点。O(log n)"""
        self._data.append(node)
        self._sift_up(len(self._data) - 1)

    def pop(self) -> Optional[HeapNode]:
        """弹出堆顶（最大评分节点）。O(log n)"""
        if not self._data:
            return None
        self._swap(0, len(self._data) - 1)
        top = self._data.pop()
        if self._data:
            self._sift_down(0)
        return top

    def peek(self) -> Optional[HeapNode]:
        """查看堆顶但不弹出。O(1)"""
        return self._data[0] if self._data else None

    def size(self) -> int:
        return len(self._data)

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def get_all(self) -> list[HeapNode]:
        """返回堆中所有节点的快照列表。"""
        return list(self._data)

    # ── 树形可视化 ──────────────────────────────────────

    def print_tree(self) -> None:
        """以树形结构打印堆（UTF-8 画线字符）。"""
        if not self._data:
            print("(空堆)")
            return
        print(f"\n  MaxHeap (size={len(self._data)}):")
        self._print_node(0, "", True)

    def _print_node(self, i: int, prefix: str, is_last: bool) -> None:
        """递归打印节点及其子树。"""
        n = len(self._data)
        if i >= n:
            return

        node = self._data[i]
        connector = "+-- " if is_last else "|-- "
        print(f"  {prefix}{connector}{node.song.song_id} {node.song.title[:22]} (score: {node.score:.1f})")

        child_prefix = prefix + ("    " if is_last else "|   ")

        left = self._left(i)
        right = self._right(i)

        has_left = left < n
        has_right = right < n

        if has_left:
            self._print_node(left, child_prefix, not has_right)
        if has_right:
            self._print_node(right, child_prefix, True)

    def tree(self) -> str:
        """返回堆的树形字符串（UTF-8 画线）。适合保存或打印到支持 UTF-8 的终端。"""
        if not self._data:
            return "(空堆)"
        lines = [f"MaxHeap (size={len(self._data)}):"]
        self._tree_lines(0, "", True, lines)
        return "\n".join(lines)

    def _tree_lines(self, i: int, prefix: str, is_last: bool, lines: list) -> None:
        """递归构建树形字符串。"""
        n = len(self._data)
        if i >= n:
            return
        node = self._data[i]
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{node.song.song_id} {node.song.title[:22]} ({node.score:.1f})")
        child_prefix = prefix + ("    " if is_last else "│   ")
        left = self._left(i)
        right = self._right(i)
        has_left = left < n
        has_right = right < n
        if has_left:
            self._tree_lines(left, child_prefix, not has_right, lines)
        if has_right:
            self._tree_lines(right, child_prefix, True, lines)


# ============================================================================
# 【补充结构】MinHeap —— 最小堆（成员D）
# ============================================================================
# 与上面的 MaxHeap 对称，区别在于父节点 <= 子节点（堆顶是最小值）。
#
# 被哪些模块调用:
#   - D_zhongweishu.py (MedianFinder) → 双堆求中位数，左半用MinHeap存负数模拟最大堆
#   - D_guibing_hebing.py (MergeKSorted) → K路归并
#   - D_bofang_gongju.py (HotColdBalancer) → 冷门歌曲用最小堆管理

class MinHeap:
    """自定义最小堆（0-indexed 数组实现）。

    与 MaxHeap 对称。堆顶是评分最小的元素。
    """

    def __init__(self):
        self._data: list = []

    @staticmethod
    def _parent(i: int) -> int:
        return (i - 1) // 2

    @staticmethod
    def _left(i: int) -> int:
        return 2 * i + 1

    @staticmethod
    def _right(i: int) -> int:
        return 2 * i + 2

    def _swap(self, i: int, j: int) -> None:
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def _sift_up(self, i: int) -> None:
        """上浮：子节点小于父节点则交换。O(log n)"""
        while i > 0:
            p = self._parent(i)
            if self._data[i] < self._data[p]:
                self._swap(i, p)
                i = p
            else:
                break

    def _sift_down(self, i: int) -> None:
        """下沉：父节点大于最小的子节点则交换。O(log n)"""
        n = len(self._data)
        while True:
            smallest = i
            l = self._left(i)
            r = self._right(i)
            if l < n and self._data[l] < self._data[smallest]:
                smallest = l
            if r < n and self._data[r] < self._data[smallest]:
                smallest = r
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest

    def push(self, item) -> None:
        """插入元素。O(log n)"""
        self._data.append(item)
        self._sift_up(len(self._data) - 1)

    def pop(self):
        """弹出堆顶（最小值）。O(log n)"""
        if not self._data:
            return None
        self._swap(0, len(self._data) - 1)
        top = self._data.pop()
        if self._data:
            self._sift_down(0)
        return top

    def peek(self):
        """查看堆顶（不移除）。O(1)"""
        return self._data[0] if self._data else None

    def size(self) -> int:
        return len(self._data)

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def get_all(self) -> list:
        """返回堆中所有元素的快照列表。"""
        return list(self._data)

    def verify_heap_property(self) -> bool:
        """验证最小堆性质。O(n)"""
        n = len(self._data)
        for i in range(n):
            l, r = 2 * i + 1, 2 * i + 2
            if l < n and self._data[i] > self._data[l]:
                return False
            if r < n and self._data[i] > self._data[r]:
                return False
        return True


# ============================================================================
# 【Task 4 主结构】AutoplayHeap —— Autoplay 优先级队列（成员D）
# ============================================================================

class AutoplayHeap:
    """Autoplay priority queue built on MaxHeap."""

    def __init__(self):
        self._heap = MaxHeap()

    def add_to_autoplay(self, song: Song, score: float) -> None:
        """将一首歌加入 Autoplay 队列。O(log n)"""
        self._heap.push(HeapNode(song, score))

    def next_autoplay(self) -> Optional[Song]:
        """获取并移除优先级最高的歌曲。O(log n)"""
        node = self._heap.pop()
        return node.song if node else None

    def remove_from_autoplay(self, song_id: str) -> bool:
        """
        从队列中移除指定 song_id 的歌曲。O(n)

        改进算法：找到目标后与末尾元素交换再弹出，
        然后同时执行上浮+下沉，确保堆性质恢复。
        """
        data = self._heap._data
        for i, node in enumerate(data):
            if node.song.song_id == song_id:
                last_idx = len(data) - 1
                if i != last_idx:
                    self._heap._swap(i, last_idx)
                    data.pop()
                    if data:
                        self._heap._sift_up(i)
                        self._heap._sift_down(i)
                else:
                    data.pop()
                return True
        return False

    def update_score(self, song_id: str, new_score: float) -> bool:
        """更新指定歌曲的评分并调整堆。O(n)"""
        data = self._heap._data
        for i, node in enumerate(data):
            if node.song.song_id == song_id:
                old = node.score
                node.score = new_score
                if new_score > old:
                    self._heap._sift_up(i)
                elif new_score < old:
                    self._heap._sift_down(i)
                return True
        return False

    def peek_next(self) -> Optional[Song]:
        """查看下一首要播放的歌（不移除）。O(1)"""
        node = self._heap.peek()
        return node.song if node else None

    def size(self) -> int:
        return self._heap.size()

    def is_empty(self) -> bool:
        return self._heap.is_empty()

    def display_all(self) -> list[dict]:
        """以字典列表形式返回队列中所有歌曲及其评分。"""
        return [
            {
                "song_id": n.song.song_id,
                "title": n.song.title,
                "artist": n.song.artist,
                "score": round(n.score, 2),
            }
            for n in self._heap.get_all()
        ]

    def print_tree(self) -> None:
        """以树形结构打印 Autoplay 堆（ASCII 字符，兼容所有终端）。"""
        self._heap.print_tree()

    def tree(self) -> str:
        """返回 Autoplay 堆的树形字符串（UTF-8 画线）。"""
        return self._heap.tree()

    def verify_heap_property(self) -> bool:
        """验证最大堆性质是否成立（用于测试）。O(n)"""
        data = self._heap._data
        n = len(data)
        for i in range(n):
            l = 2*i + 1
            r = 2*i + 2
            if l < n and data[i].score < data[l].score:
                return False
            if r < n and data[i].score < data[r].score:
                return False
        return True

    @staticmethod
    def compute_score(song: Song) -> float:
        """
        根据歌曲的点赞数和播放量计算 Autoplay 评分。

        公式:
            like_ratio  = like_count / max(play_count, 1)
            play_volume = log2(play_count + 1)
            score       = (like_ratio * play_volume * 50) + (play_volume * 5)
        """
        like_ratio = song.like_count / max(song.play_count, 1)
        play_volume = math.log2(song.play_count + 1)
        return (like_ratio * play_volume * 50) + (play_volume * 5)
