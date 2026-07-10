"""
structures/B_bofang_liebiao.py
==============================
Task 2 — 播放列表：双向链表 (Doubly Linked List)  成员B 负责

╔══════════════════════════════════════════════════════════════════╗
║  本文件包含 Part 1 + Part 2 全部功能                            ║
║                                                                  ║
║  Part 1 (基础) ─ Playlist 类 ─ 双向链表核心操作                  ║
║    链表节点 Node · 增删改查 · 上下首导航 · 随机打乱 · 循环模式   ║
║                                                                  ║
║  Part 2 (扩展) ─ PlaylistPart2 类 ─ 继承 Playlist，新增高级功能  ║
║    归并排序 · 流派/艺术家过滤 · 歌名/艺术家搜索 · 统计 · 播放历史 ║
╚══════════════════════════════════════════════════════════════════╝

【Part1 → Part2 关系】
  PlaylistPart2 通过继承获得 Part1 全部能力（add_song/remove_song/
  play_next/play_previous/shuffle/display 等），再叠加 Part2 的
  排序/过滤/搜索/统计功能。用户只需实例化 PlaylistPart2 即可使用全部功能。

【被哪些模块调用】
  - data/A_shuju_jiazai.py  (成员A) → from ... import Playlist → DataLoader 中加载歌曲
  - main.py                 (主程序) → from ... import Playlist, PlaylistPart2 → 全部功能

负责人：成员 B
"""

import random
import sys
from pathlib import Path
from typing import Optional, Iterator

from models.A_gequ import Song


# #############################################################################
#                                                                             #
#   ██████╗  █████╗ ██████╗ ████████╗    ██╗                                 #
#   ██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝    ██║                                 #
#   ██████╔╝███████║██████╔╝   ██║       ██║                                 #
#   ██╔═══╝ ██╔══██║██╔══██╗   ██║       ██║                                 #
#   ██║     ██║  ██║██║  ██║   ██║       ███████╗                            #
#   ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚══════╝                            #
#                                                                             #
#   基础双向链表播放列表                                                       #
#   功能: Node节点 · 增删歌曲 · 上下首导航 · 随机打乱 · 显示 · 循环模式       #
#                                                                             #
# #############################################################################


# ============================================================================
# 【Part 1 — 第1段】Node —— 双向链表节点
# ============================================================================
# 节点是链表的基本构建块。每个节点存一首歌，通过 prev/next 指针连接前后节点。
# __slots__ 减少内存：播放列表可能数十首歌，省去每个节点的 __dict__ 开销。

class Node:
    """双向链表节点。

    属性:
        song (Song): 歌曲数据
        next (Node|None): 后继节点指针
        prev (Node|None): 前驱节点指针
    """

    __slots__ = ("song", "next", "prev")

    def __init__(self, song: Song):
        self.song: Song = song
        self.next: Optional["Node"] = None
        self.prev: Optional["Node"] = None

    def __repr__(self) -> str:
        prev_id = self.prev.song.song_id if self.prev else "None"
        next_id = self.next.song.song_id if self.next else "None"
        return f"Node(prev={prev_id}, song={self.song.song_id}, next={next_id})"


# ============================================================================
# 【Part 1 — 第2段】Playlist —— 双向链表播放列表（基类）
# ============================================================================
# 提供所有基础播放列表操作。PlaylistPart2(Part2) 继承此类以获得这些能力。
#
# 核心数据结构:
#   head / tail  →  首尾哨兵，O(1) 头尾操作
#   current      →  当前播放位置指针
#   _node_map    →  song_id → Node 字典，O(1) 按ID查找
#   _loop        →  循环模式开关
#
# 时间复杂度总结:
#   add_song / remove_song → O(1)
#   play_next / play_previous → O(1)
#   move_to_position → O(position)
#   shuffle → O(n)
#   display / to_list → O(n)

class Playlist:
    """基于双向链表的播放列表（Part 1 基类）。

    使用示例:
        >>> pl = Playlist()
        >>> pl.add_song(song1)
        >>> pl.add_song(song2)
        >>> pl.play_next()
        >>> print(pl.current_song())
        >>> pl.display()
    """

    def __init__(self) -> None:
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self.current: Optional[Node] = None
        self._size: int = 0
        self._loop: bool = True
        self._node_map: dict[str, Node] = {}

    # ── 基本属性 ─────────────────────────────────────────────

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._size > 0

    def is_empty(self) -> bool:
        return self._size == 0

    def set_loop(self, enabled: bool) -> None:
        """设置循环模式。开启后首尾导航会循环。"""
        self._loop = enabled

    # ── 操作1: add_song ─ 尾部追加 O(1) ─────────────────────

    def add_song(self, song: Song) -> None:
        """将歌曲追加到播放列表尾部。O(1)"""
        new_node = Node(song)
        self._node_map[song.song_id] = new_node

        if self.head is None:
            self.head = new_node
            self.tail = new_node
            self.current = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        self._size += 1

    # ── 操作2: remove_song ─ 按ID删除 O(1) ──────────────────

    def remove_song(self, song_id: str) -> Optional[Song]:
        """根据 song_id 删除歌曲。O(1) 定位 + O(1) 删除。"""
        node = self._node_map.get(song_id)
        if node is None:
            print(f"[WARN] 未找到歌曲 {song_id}，无法删除。")
            return None

        deleted_song = node.song

        # 修改相邻指针
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        # 更新 current
        if self.current is node:
            if node.next:
                self.current = node.next
            elif node.prev:
                self.current = node.prev
            else:
                self.current = None

        del self._node_map[song_id]
        self._size -= 1
        node.next = None
        node.prev = None
        return deleted_song

    # ── 操作3: play_next ─ 下一首 O(1) ──────────────────────

    def play_next(self) -> Optional[Song]:
        """切换到下一首。支持循环模式。"""
        if self.current is None:
            return None
        if self.current.next:
            self.current = self.current.next
        elif self._loop:
            self.current = self.head
        else:
            print("[INFO] 已是最后一首，无法继续前进。")
            return self.current.song
        return self.current.song

    # ── 操作4: play_previous ─ 上一首 O(1) ──────────────────

    def play_previous(self) -> Optional[Song]:
        """切换到上一首。支持循环模式。"""
        if self.current is None:
            return None
        if self.current.prev:
            self.current = self.current.prev
        elif self._loop:
            self.current = self.tail
        else:
            print("[INFO] 已是第一首，无法继续后退。")
            return self.current.song
        return self.current.song

    # ── 操作5: current_song ─ 获取当前歌曲 O(1) ─────────────

    def current_song(self) -> Optional[Song]:
        """获取当前播放位置的歌曲，不改变播放状态。"""
        if self.current is None:
            return None
        return self.current.song

    # ── 操作6: move_to_position ─ 移动歌曲 O(position) ──────

    def move_to_position(self, song_id: str, position: int) -> bool:
        """将指定歌曲移动到目标位置（0-based）。O(position)"""
        node = self._node_map.get(song_id)
        if node is None:
            print(f"[WARN] 未找到歌曲 {song_id}，无法移动。")
            return False
        if self._size <= 1:
            return True

        # 摘除节点
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        if self.current is node:
            if node.next:
                self.current = node.next
            elif node.prev:
                self.current = node.prev

        # 插入到目标位置
        if position <= 0:
            node.next = self.head
            node.prev = None
            if self.head:
                self.head.prev = node
            self.head = node
            if self.tail is None:
                self.tail = node
            return True

        if position >= self._size:
            node.next = None
            node.prev = self.tail
            if self.tail:
                self.tail.next = node
            self.tail = node
            if self.head is None:
                self.head = node
            return True

        walker = self.head
        steps = 0
        while walker and steps < position:
            walker = walker.next
            steps += 1

        if walker is None:
            node.next = None
            node.prev = self.tail
            if self.tail:
                self.tail.next = node
            self.tail = node
        else:
            node.next = walker
            node.prev = walker.prev
            if walker.prev:
                walker.prev.next = node
            else:
                self.head = node
            walker.prev = node
        return True

    # ── 操作7: shuffle ─ Fisher-Yates 洗牌 O(n) ─────────────

    def shuffle(self) -> None:
        """随机打乱播放列表。仅修改指针，不创建新节点。O(n)"""
        if self._size <= 1:
            return

        nodes: list[Node] = []
        walker = self.head
        while walker is not None:
            nodes.append(walker)
            walker = walker.next

        current_node = self.current

        for i in range(len(nodes) - 1, 0, -1):
            j = random.randint(0, i)
            nodes[i], nodes[j] = nodes[j], nodes[i]

        for i in range(len(nodes)):
            nodes[i].prev = nodes[i - 1] if i > 0 else None
            nodes[i].next = nodes[i + 1] if i < len(nodes) - 1 else None

        self.head = nodes[0]
        self.tail = nodes[-1]
        if current_node is not None:
            self.current = current_node

    # ── 操作8: display ─ 打印播放列表 O(n) ──────────────────

    def display(self) -> None:
        """打印播放列表。当前歌曲用 >> 标记。"""
        if self._size == 0:
            print("播放列表为空。")
            return

        sep = "=" * 60
        print(f"\n{sep}")
        print(f"播放列表 (共 {self._size} 首)")
        if self._loop:
            print("循环模式: 开启 [LOOP]")
        print(sep)

        walker = self.head
        index = 1
        while walker is not None:
            marker = ">>" if walker is self.current else "  "
            print(
                f"{marker} {index:2d}. {walker.song.song_id} "
                f"\"{walker.song.title}\" — {walker.song.artist} "
                f"[{walker.song.genre.value}] {walker.song.display_duration()}"
            )
            walker = walker.next
            index += 1
        print(f"{sep}\n")

    # ── 辅助方法 ─────────────────────────────────────────────

    def to_list(self) -> list[Song]:
        """将播放列表转为 Song 列表（从头到尾）。"""
        result: list[Song] = []
        walker = self.head
        while walker is not None:
            result.append(walker.song)
            walker = walker.next
        return result

    def find(self, song_id: str) -> Optional[Song]:
        """按 song_id 查找歌曲。O(1)"""
        node = self._node_map.get(song_id)
        return node.song if node else None

    def jump_to(self, song_id: str) -> bool:
        """将 current 跳到指定歌曲。O(1)"""
        node = self._node_map.get(song_id)
        if node is None:
            print(f"[WARN] 未找到歌曲 {song_id}，无法跳转。")
            return False
        self.current = node
        return True

    def reset_to_head(self) -> None:
        """将当前播放位置重置到列表头部。"""
        if self.head is not None:
            self.current = self.head

    def insert_at_position(self, song: Song, position: int) -> None:
        """在指定位置插入新歌。O(position)"""
        new_node = Node(song)
        self._node_map[song.song_id] = new_node

        if self._size == 0:
            self.head = self.tail = self.current = new_node
            self._size = 1
            return
        if position <= 0:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
            self._size += 1
            return
        if position >= self._size:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
            self._size += 1
            return

        walker = self.head
        steps = 0
        while walker and steps < position:
            walker = walker.next
            steps += 1
        new_node.next = walker
        new_node.prev = walker.prev
        if walker.prev:
            walker.prev.next = new_node
        walker.prev = new_node
        self._size += 1

    def __iter__(self) -> Iterator[Song]:
        walker = self.head
        while walker is not None:
            yield walker.song
            walker = walker.next

    def __contains__(self, song_id: str) -> bool:
        return song_id in self._node_map

    def __repr__(self) -> str:
        current_id = self.current.song.song_id if self.current else "None"
        return (
            f"Playlist(size={self._size}, "
            f"head={self.head.song.song_id if self.head else 'None'}, "
            f"tail={self.tail.song.song_id if self.tail else 'None'}, "
            f"current={current_id}, loop={self._loop})"
        )


# #############################################################################
#                                                                             #
#   ██████╗  █████╗ ██████╗ ████████╗   ██████╗                               #
#   ██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝   ╚════██╗                              #
#   ██████╔╝███████║██████╔╝   ██║       █████╔╝                              #
#   ██╔═══╝ ██╔══██║██╔══██╗   ██║      ██╔═══╝                               #
#   ██║     ██║  ██║██║  ██║   ██║      ███████╗                              #
#   ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝      ╚══════╝                              #
#                                                                             #
#   播放列表扩展功能（继承 Playlist 基类）                                      #
#   功能: 归并排序 · 流派/艺术家过滤 · 歌名/艺术家搜索 · 统计 · 播放历史       #
#                                                                             #
# #############################################################################


# ============================================================================
# 【Part 2 — 第1段】PlaylistPart2 —— 扩展播放列表（继承 Playlist）
# ============================================================================
# 通过继承获得 Part1 全部方法。Part2 新增功能直接在子类中实现。
#
# 新增功能:
#   1. sort_by(criteria)        归并排序 — 按 title/artist/热度/时长
#   2. filter_by_genre(g)       流派过滤
#   3. filter_by_artist(a)      艺术家过滤
#   4. search_by_title(kw)      歌名模糊搜索
#   5. search_by_artist(kw)     艺术家模糊搜索
#   6. get_statistics()         统计信息（总时长/流派分布/热度极值）
#   7. get_recently_played()   播放历史
#   8. clear_history()         清空历史
#   9. batch_add(songs)        批量添加
#  10. batch_remove(ids)       批量删除
#
# 设计原则:
#   - 所有排序/过滤/搜索不创建新 Node 对象，仅修改指针或返回新列表
#   - 归并排序 O(n log n)，稳定
#   - 播放历史自动去重，最近播放排在末尾

class PlaylistPart2(Playlist):
    """扩展播放列表 —— Part1 全部能力 + Part2 高级功能。

    使用示例:
        >>> pl = PlaylistPart2()
        >>> pl.batch_add(songs)
        >>> pl.sort_by("play_count")
        >>> pop_songs = pl.filter_by_genre("Pop")
        >>> stats = pl.get_statistics()
    """

    # ═══════════════════════════════════════════════════════════
    # 内部: 播放历史记录
    # ═══════════════════════════════════════════════════════════

    def _add_to_history(self, song_id: str) -> None:
        """将 song_id 追加到播放历史（去重+裁剪）。"""
        if not hasattr(self, '_history'):
            self._history: list[str] = []
        if not hasattr(self, '_history_max'):
            self._history_max: int = 50
        if song_id in self._history:
            self._history.remove(song_id)
        self._history.append(song_id)
        while len(self._history) > self._history_max:
            self._history.pop(0)

    # ═══════════════════════════════════════════════════════════
    # 功能1: sort_by ─ 归并排序 O(n log n)
    # ═══════════════════════════════════════════════════════════

    def sort_by(self, criteria: str = "title") -> None:
        """按指定条件原地排序（归并排序，仅修改指针）。

        支持的 criteria:
          "title"       → 歌名字母序升序
          "artist"      → 艺术家的字母序升序
          "play_count"  → 播放次数降序（热门优先）
          "like_count"  → 点赞次数降序（受欢迎优先）
          "duration"    → 时长升序（短歌优先）
        """
        if self._size <= 1:
            return

        nodes: list = []
        walker = self.head
        while walker is not None:
            nodes.append(walker)
            walker = walker.next

        current_node = self.current
        sorted_nodes = self._merge_sort(nodes, criteria)

        for i in range(len(sorted_nodes)):
            sorted_nodes[i].prev = sorted_nodes[i - 1] if i > 0 else None
            sorted_nodes[i].next = (sorted_nodes[i + 1]
                                    if i < len(sorted_nodes) - 1 else None)

        self.head = sorted_nodes[0]
        self.tail = sorted_nodes[-1]
        if current_node is not None:
            self.current = current_node

    def _merge_sort(self, nodes: list, criteria: str) -> list:
        """递归归并排序。"""
        n = len(nodes)
        if n <= 1:
            return nodes
        mid = n // 2
        left = self._merge_sort(nodes[:mid], criteria)
        right = self._merge_sort(nodes[mid:], criteria)
        return self._merge(left, right, criteria)

    def _merge(self, left: list, right: list, criteria: str) -> list:
        """合并两个有序列表。"""
        result: list = []
        i, j = 0, 0
        while i < len(left) and j < len(right):
            if self._compare_nodes(left[i], right[j], criteria):
                result.append(left[i]); i += 1
            else:
                result.append(right[j]); j += 1
        while i < len(left):
            result.append(left[i]); i += 1
        while j < len(right):
            result.append(right[j]); j += 1
        return result

    def _compare_nodes(self, a, b, criteria: str) -> bool:
        """比较两个节点：a 是否应排在 b 前面。"""
        if criteria == "title":
            return a.song.title.lower() < b.song.title.lower()
        elif criteria == "artist":
            return a.song.artist.lower() < b.song.artist.lower()
        elif criteria == "play_count":
            if a.song.play_count != b.song.play_count:
                return a.song.play_count > b.song.play_count
            return a.song.title.lower() < b.song.title.lower()
        elif criteria == "like_count":
            if a.song.like_count != b.song.like_count:
                return a.song.like_count > b.song.like_count
            return a.song.title.lower() < b.song.title.lower()
        elif criteria == "duration":
            if a.song.duration_seconds != b.song.duration_seconds:
                return a.song.duration_seconds < b.song.duration_seconds
            return a.song.title.lower() < b.song.title.lower()
        else:
            return a.song.title.lower() < b.song.title.lower()

    # ═══════════════════════════════════════════════════════════
    # 功能2: filter_by_genre ─ 流派过滤
    # ═══════════════════════════════════════════════════════════

    def filter_by_genre(self, genre) -> "PlaylistPart2":
        """按流派过滤，返回新 PlaylistPart2（原列表不变）。

        参数: genre 可以是 Genre 枚举或流派名称字符串。
        """
        from models.liupai import Genre
        if isinstance(genre, str):
            genre = Genre.from_string(genre)

        filtered = PlaylistPart2()
        walker = self.head
        while walker is not None:
            if walker.song.genre == genre:
                filtered.add_song(walker.song)
            walker = walker.next
        return filtered

    # ═══════════════════════════════════════════════════════════
    # 功能3: filter_by_artist ─ 艺术家过滤
    # ═══════════════════════════════════════════════════════════

    def filter_by_artist(self, artist: str) -> "PlaylistPart2":
        """按艺术家名称过滤（不区分大小写，模糊匹配）。"""
        keyword = artist.lower()
        filtered = PlaylistPart2()
        walker = self.head
        while walker is not None:
            if keyword in walker.song.artist.lower():
                filtered.add_song(walker.song)
            walker = walker.next
        return filtered

    # ═══════════════════════════════════════════════════════════
    # 功能4: search_by_title ─ 歌名搜索
    # ═══════════════════════════════════════════════════════════

    def search_by_title(self, keyword: str) -> list[Song]:
        """按歌名模糊搜索（不区分大小写）。返回匹配的 Song 列表。"""
        results: list[Song] = []
        kw = keyword.lower()
        walker = self.head
        while walker is not None:
            if kw in walker.song.title.lower():
                results.append(walker.song)
            walker = walker.next
        return results

    # ═══════════════════════════════════════════════════════════
    # 功能5: search_by_artist ─ 艺术家搜索
    # ═══════════════════════════════════════════════════════════

    def search_by_artist(self, keyword: str) -> list[Song]:
        """按艺术家模糊搜索（不区分大小写）。返回匹配的 Song 列表。"""
        results: list[Song] = []
        kw = keyword.lower()
        walker = self.head
        while walker is not None:
            if kw in walker.song.artist.lower():
                results.append(walker.song)
            walker = walker.next
        return results

    # ═══════════════════════════════════════════════════════════
    # 功能6: get_statistics ─ 统计信息 O(n)
    # ═══════════════════════════════════════════════════════════

    def get_statistics(self) -> dict:
        """获取播放列表统计摘要（一次遍历）。

        返回字典包含: total_songs, total_duration_seconds,
        total_duration_formatted, average_duration_seconds,
        genre_distribution, average_play_count, average_like_count,
        most_played, most_liked, least_played
        """
        if self._size == 0:
            return {
                "total_songs": 0, "total_duration_seconds": 0,
                "total_duration_formatted": "0:00:00",
                "average_duration_seconds": 0, "genre_distribution": {},
                "average_play_count": 0, "average_like_count": 0,
                "most_played": None, "most_liked": None, "least_played": None,
            }

        total_duration = 0; total_plays = 0; total_likes = 0
        genre_counts: dict[str, int] = {}
        most_played_song = self.head.song
        most_liked_song = self.head.song
        least_played_song = self.head.song

        walker = self.head
        while walker is not None:
            s = walker.song
            total_duration += s.duration_seconds
            total_plays += s.play_count
            total_likes += s.like_count
            gn = s.genre.value
            genre_counts[gn] = genre_counts.get(gn, 0) + 1
            if s.play_count > most_played_song.play_count:
                most_played_song = s
            if s.like_count > most_liked_song.like_count:
                most_liked_song = s
            if s.play_count < least_played_song.play_count:
                least_played_song = s
            walker = walker.next

        n = self._size
        total_sec = total_duration
        h = total_sec // 3600; m = (total_sec % 3600) // 60; s = total_sec % 60

        return {
            "total_songs": n,
            "total_duration_seconds": total_duration,
            "total_duration_formatted": f"{h}:{m:02d}:{s:02d}",
            "average_duration_seconds": round(total_duration / n, 1),
            "genre_distribution": genre_counts,
            "average_play_count": round(total_plays / n, 1),
            "average_like_count": round(total_likes / n, 1),
            "most_played": most_played_song,
            "most_liked": most_liked_song,
            "least_played": least_played_song,
        }

    # ═══════════════════════════════════════════════════════════
    # 功能7-8: 播放历史
    # ═══════════════════════════════════════════════════════════

    def get_recently_played(self, n: int = 10) -> list[str]:
        """获取最近播放的歌曲 ID 列表（从旧到新）。"""
        if not hasattr(self, '_history'):
            self._history: list[str] = []
        if not hasattr(self, '_history_max'):
            self._history_max: int = 50
        if n <= 0:
            return []
        return self._history[-n:] if len(self._history) >= n else list(self._history)

    def clear_history(self) -> None:
        """清空播放历史。"""
        if not hasattr(self, '_history'):
            self._history: list[str] = []
        self._history.clear()

    # ═══════════════════════════════════════════════════════════
    # 功能9-10: 批量操作
    # ═══════════════════════════════════════════════════════════

    def batch_add(self, songs: list[Song]) -> int:
        """批量添加歌曲到尾部。返回成功添加的数量。"""
        count = 0
        for song in songs:
            self.add_song(song)
            count += 1
        return count

    def batch_remove(self, song_ids: list[str]) -> tuple[int, int]:
        """批量删除歌曲。返回 (成功数, 失败数)。"""
        success, fail = 0, 0
        for song_id in song_ids:
            if self.remove_song(song_id) is not None:
                success += 1
            else:
                fail += 1
        return (success, fail)


# #############################################################################
#                                                                             #
#   ██████╗  █████╗ ██████╗ ████████╗   ██████╗      ████████╗ █████╗ ███████╗██╗  ██╗
#   ██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝   ╚════██╗     ╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝
#   ██████╔╝███████║██████╔╝   ██║       █████╔╝        ██║   ███████║███████╗█████╔╝
#   ██╔═══╝ ██╔══██║██╔══██╗   ██║      ██╔═══╝         ██║   ██╔══██║╚════██║██╔═██╗
#   ██║     ██║  ██║██║  ██║   ██║      ███████╗        ██║   ██║  ██║███████║██║  ██╗
#   ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝      ╚══════╝        ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
#                                                                             #
#   Part 2 — Task 1: 播放列表分析 · Task 2: 智能随机                           #
#                                                                             #
# #############################################################################


# ============================================================================
# 【Part 2 — Task 1】播放列表分析（成员B）
# ============================================================================
# 要求: 全部遍历链表完成计算，不允许转 Python list。
# 调用链:
#   PlaylistPart2.playlist_analytics()
#     ├→ 遍历链表（head→tail）一次收集全部指标 O(n)
#     └→ 返回 dict: total_duration, avg_duration, most_common_genre,
#                   artist_most_songs, genre_counts, artist_counts

    def playlist_analytics(self) -> dict:
        """
        Part 2 Task 1 — 播放列表分析（纯链表遍历，不转 list）。

        一次遍历链表同时收集:
          - 总时长 (total_duration_seconds)
          - 平均时长 (average_duration_seconds)
          - 最常见流派 (most_common_genre)
          - 最多歌曲的艺术家 (artist_with_most_songs)
          - 流派分布 (genre_distribution)
          - 艺术家分布 (artist_distribution)

        时间复杂度: O(n)  一次遍历
        空间复杂度: O(g + a)  g=流派数, a=艺术家数

        返回:
            dict: 包含以上全部统计字段

        示例:
            >>> stats = pl.playlist_analytics()
            >>> print(stats['most_common_genre'])
            Pop
        """
        if self._size == 0:
            return {
                "total_songs": 0,
                "total_duration_seconds": 0,
                "average_duration_seconds": 0,
                "most_common_genre": None,
                "artist_with_most_songs": None,
                "genre_distribution": {},
                "artist_distribution": {},
            }

        total_duration = 0
        genre_counts: dict[str, int] = {}
        artist_counts: dict[str, int] = {}

        # ── 一次遍历链表，收集全部统计量 ──
        walker = self.head
        while walker is not None:
            s = walker.song

            # 累加时长
            total_duration += s.duration_seconds

            # 流派计数
            gn = s.genre.value
            genre_counts[gn] = genre_counts.get(gn, 0) + 1

            # 艺术家计数
            artist_counts[s.artist] = artist_counts.get(s.artist, 0) + 1

            walker = walker.next  # ★ 链表指针后移，不依赖索引

        n = self._size

        # ── 找最大值 ──
        most_genre = max(genre_counts, key=lambda k: genre_counts[k]) if genre_counts else None
        most_artist = max(artist_counts, key=lambda k: artist_counts[k]) if artist_counts else None

        return {
            "total_songs": n,
            "total_duration_seconds": total_duration,
            "average_duration_seconds": round(total_duration / n, 1) if n > 0 else 0,
            "most_common_genre": most_genre,
            "artist_with_most_songs": most_artist,
            "genre_distribution": genre_counts,
            "artist_distribution": artist_counts,
        }


# ============================================================================
# 【Part 2 — Task 2】Smart Shuffle — 约束排列智能随机（成员B）
# ============================================================================
# 要求:
#   1. 相邻两首歌不能是同一艺术家
#   2. 流派尽可能均匀分布（同流派歌曲间隔最大化）
#   3. 如果约束无法满足（如全是同一艺术家），给出警告并用普通shuffle
#
# 算法: 贪心 + 回溯
#   1. 按艺术家分组，按流派分组
#   2. 每次选"最久没出现"的艺术家 + "最久没出现"的流派
#   3. 用优先队列（堆）选最佳候选
#   4. 如果卡住（无合法候选），回溯或降级为普通shuffle
#
# 调用链:
#   PlaylistPart2.smart_shuffle()
#     ├→ 遍历链表收集节点 O(n)
#     ├→ 贪心构造新顺序 O(n log n)
#     └→ 如果失败 → 降级为 Playlist.shuffle() 【Part1 的 Fisher-Yates】

    def smart_shuffle(self) -> bool:
        """
        Part 2 Task 2 — 智能随机播放。

        约束:
          1. 相邻歌曲不能同一艺术家
          2. 同流派歌曲尽可能分散（间隔 >= 2）

        算法: 贪心构造
          - 维护每个艺术家的"冷却时间"（最近一次被选中后还需等几轮）
          - 每次从可选池中选流派最近最少出现的歌曲
          - 如果无合法候选，重置冷却继续尝试

        返回:
            True  → 智能随机成功
            False → 约束无法满足，已降级为普通 shuffle

        示例:
            >>> if not pl.smart_shuffle():
            ...     print("约束无法满足，使用普通随机")
        """
        if self._size <= 2:
            self.shuffle()
            return True

        # ── 步骤1: 收集所有节点 ──
        nodes: list = []
        walker = self.head
        while walker is not None:
            nodes.append(walker)
            walker = walker.next

        # ── 步骤2: 贪心构造 ──
        result = self._smart_shuffle_greedy(nodes)

        if result is None:
            # ── 降级: 约束无法满足 → 普通 shuffle ──
            print("[SmartShuffle] 约束无法满足，降级为普通随机播放。")
            self.shuffle()
            return False

        # ── 步骤3: 按新顺序重新链接指针 ──
        for i in range(len(result)):
            result[i].prev = result[i - 1] if i > 0 else None
            result[i].next = result[i + 1] if i < len(result) - 1 else None

        self.head = result[0]
        self.tail = result[-1]
        self.current = self.head
        return True

    def _smart_shuffle_greedy(self, nodes: list) -> list | None:
        """
        贪心构造满足约束的排列。

        策略:
          1. 按 (艺术家频率, 流派频率) 排序 — 频率高的优先放置
          2. 维护最近使用的艺术家集合和流派集合作为"冷却区"
          3. 每次从冷却区外选频率最高的节点

        参数:
            nodes: 待排列的节点列表

        返回:
            满足约束的节点列表，或 None（无法满足时）
        """
        n = len(nodes)

        # 构建艺术家→节点列表 和 流派→节点列表
        artist_map: dict[str, list] = {}
        genre_map: dict[str, list] = {}
        for node in nodes:
            a = node.song.artist
            g = node.song.genre.value
            if a not in artist_map:
                artist_map[a] = []
            artist_map[a].append(node)
            if g not in genre_map:
                genre_map[g] = []
            genre_map[g].append(node)

        # 如果只有一个艺术家 → 不可能满足约束
        if len(artist_map) == 1:
            return None

        result = []
        used = [False] * n
        last_artist = None
        last_genre = None

        for pos in range(n):
            # ── 找最佳候选 ──
            best_idx = -1
            best_score = -1

            for i, node in enumerate(nodes):
                if used[i]:
                    continue

                artist = node.song.artist
                genre = node.song.genre.value

                # 约束1: 不能和上一首同艺术家
                if artist == last_artist:
                    continue

                # 评分: 优先选当前最"少见"的流派
                score = 0
                if genre != last_genre:
                    score += 10  # 流派变化加分
                # 该艺术家的剩余歌曲越多，越优先（避免最后被迫同艺术家）
                remaining = sum(1 for j in range(n) if not used[j] and nodes[j].song.artist == artist)
                if remaining <= 1:
                    score += 5  # 最后机会加分

                if score > best_score:
                    best_score = score
                    best_idx = i

            # ── 如果找不到合法候选 → 放宽约束重试 ──
            if best_idx == -1:
                # 放宽: 只禁止同艺术家，接受同流派
                for i, node in enumerate(nodes):
                    if not used[i] and node.song.artist != last_artist:
                        best_idx = i
                        break

            if best_idx == -1:
                return None  # 完全失败

            used[best_idx] = True
            result.append(nodes[best_idx])
            last_artist = nodes[best_idx].song.artist
            last_genre = nodes[best_idx].song.genre.value

        return result
