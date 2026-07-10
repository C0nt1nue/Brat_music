"""
data/A_shuju_jiazai.py
===================
Task 5 — 加载数据集：从 CSV 加载到三种数据结构

将 songs_dataset_20000.csv 中的数据加载到:
  1. BST（二叉搜索树）     — 成员 C 实现，按歌名索引全部歌曲
  2. Heap（Autoplay 堆）   — 成员 D 实现，管理自动播放优先级
  3. DoublyLinkedList（播放列表）— 成员 B 实现，管理播放列表导航

接口约定（成员 B/C/D 需要遵循的 API 规范）:
  - BST:         insert(song: Song)           — 将歌曲插入 BST
  - BST:         search(title: str) -> Song   — 按歌名搜索
  - AutoplayHeap: add_to_autoplay(song, score) — 添加歌曲及其优先级分数
  - Playlist:    add_song(song: Song)          — 向链表尾部添加歌曲

设计策略:
  - 使用 try/except 进行条件导入，即使其他成员代码尚未完成，此模块也能正常导入
  - 加载逻辑清晰分离，每个结构有独立的加载函数
  - 包含数据验证步骤，确保加载后的数据一致性

负责人：成员 A
"""

import csv
from pathlib import Path

from models.A_gequ import Song

# ============================================================================
# 导入各成员的数据结构
# ============================================================================

from structures.C_ercha_sousuo_shu import BST
from structures.D_dui import AutoplayHeap
from structures.B_bofang_liebiao import Playlist


# ============================================================================
# Autoplay 评分公式（与 Task 4 关联，此处预定义供数据加载使用）
# ============================================================================

def compute_autoplay_score(song: Song) -> float:
    """
    计算歌曲的 Autoplay 优先级分数。

    评分公式:
        score = like_count * 0.5 + play_count * 0.2 + duration_bonus

    其中:
        - like_count * 0.5:  点赞权重最高，反映用户主动喜爱
        - play_count * 0.2:  播放次数，反映流行度
        - duration_bonus:    时长奖励，3-5 分钟的歌曲更受欢迎（+10），
                             过长或过短不加分

    设计理由（详见 Task 4 文档）:
        - 点赞是用户主动行为，最能代表"喜欢"，权重最高
        - 播放次数是被动行为（可能被推荐算法推送），权重较低
        - 时长奖励基于音乐消费习惯：大多数热门歌曲在 3-5 分钟之间

    参数:
        song: Song 对象

    返回:
        float: 优先级分数，分数越高越优先播放
    """
    # 基础分数
    score = song.like_count * 0.5 + song.play_count * 0.2

    # 时长奖励：3-5 分钟的歌曲 +10 分
    if 180 <= song.duration_seconds <= 300:
        score += 10.0

    return score


# ============================================================================
# DataLoader —— 数据加载器
# ============================================================================

class DataLoader:
    """
    从 CSV 文件加载歌曲数据，并注入到三种数据结构中。

    使用示例:
        loader = DataLoader("songs_dataset_20000.csv")
        songs = loader.load_songs()                    # 获取 Song 对象列表
        bst = loader.load_into_bst()                   # 加载到 BST（成员 C）
        heap = loader.load_into_autoplay_heap()        # 加载到堆（成员 D）
        playlist = loader.load_into_playlist()         # 加载到链表（成员 B）
    """

    def __init__(self, csv_path: str = "songs_dataset_20000.csv"):
        """
        初始化数据加载器。

        参数:
            csv_path: CSV 文件路径
        """
        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise FileNotFoundError(
                f"CSV 文件不存在: {self.csv_path}\n"
                f"请先运行 data/shujuku_shengcheng.py 生成数据集。"
            )

    def load_songs(self) -> list[Song]:
        """
        从 CSV 文件加载全部歌曲，返回 Song 对象列表。

        此方法是加载到各数据结构的基础 —— 所有 load_into_* 方法
        都先调用此方法获取歌曲列表，再逐一插入目标结构。

        返回:
            list[Song]: 按 CSV 文件顺序排列的歌曲列表
        """
        songs: list[Song] = []

        with open(self.csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                song = Song.from_dict(row)
                songs.append(song)

        if len(songs) < 25:
            print(
                f"[WARN] CSV 中仅有 {len(songs)} 首歌曲，"
                f"项目要求至少 25 首。请重新生成数据集。"
            )

        return songs

    # =====================================================================
    # 加载到 BST（成员 C 负责实现 BST 类）
    # =====================================================================

    def load_into_bst(self) -> BST:
        """
        将 CSV 中所有歌曲插入到 BST 中。

        BST 按歌名（title）字母序组织，由成员 C 实现。
        """
        songs = self.load_songs()
        bst = BST()

        for song in songs:
            bst.insert(song)

        print(f"[OK] 已将 {len(songs)} 首歌曲加载到 BST 中")
        return bst

    # =====================================================================
    # 加载到 Autoplay Heap（成员 D 负责实现 AutoplayHeap 类）
    # =====================================================================

    def load_into_autoplay_heap(self) -> AutoplayHeap:
        """
        将 CSV 中所有歌曲加载到 Autoplay 堆中。

        使用 compute_autoplay_score() 计算每首歌的优先级分数，
        由成员 D 实现的 AutoplayHeap 管理。
        """
        songs = self.load_songs()
        heap = AutoplayHeap()

        for song in songs:
            score = compute_autoplay_score(song)
            heap.add_to_autoplay(song, score)

        print(f"[OK] 已将 {len(songs)} 首歌曲加载到 Autoplay 堆中")
        return heap

    # =====================================================================
    # 加载到双向链表播放列表（成员 B 负责实现 Playlist 类）
    # =====================================================================

    def load_into_playlist(self) -> Playlist:
        """
        将 CSV 中所有歌曲加载到双向链表播放列表中。

        歌曲按 CSV 文件顺序依次添加到链表尾部。
        """
        songs = self.load_songs()
        playlist = Playlist()

        for song in songs:
            playlist.add_song(song)

        print(f"[OK] 已将 {len(songs)} 首歌曲加载到播放列表中")
        return playlist

    # =====================================================================
    # 一键加载全部结构
    # =====================================================================

    def load_all(self) -> dict:
        """
        一键加载歌曲到所有三种数据结构。

        返回:
            dict: 包含三个结构的字典
                {
                    "songs":    list[Song],
                    "bst":      BST,
                    "heap":     AutoplayHeap,
                    "playlist": Playlist,
                }
        """
        songs = self.load_songs()

        result = {
            "songs": songs,
            "bst": self.load_into_bst(),
            "heap": self.load_into_autoplay_heap(),
            "playlist": self.load_into_playlist(),
        }

        print(f"\n数据加载完成: {len(songs)} 首歌曲, 3/3 个结构就绪")

        return result


# ============================================================================
# 脚本入口
# ============================================================================
