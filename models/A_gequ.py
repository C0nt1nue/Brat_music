"""
models/song.py
=============
Task 1 — 数据建模：Song 类

Song 类是音乐流媒体引擎的核心数据单元。
包含歌曲的基本元数据以及用户交互统计（播放次数、点赞数）。

实现要求:
  - __repr__: 返回 Song 对象的可读字符串表示
  - __eq__:   基于 song_id 判断两首歌是否相同
  - __lt__:   基于自定义标准比较两首歌的大小

负责人：成员 A
"""

from dataclasses import dataclass
from models.liupai import Genre


@dataclass
class Song:
    """
    歌曲数据类

    属性:
        song_id (str):           歌曲唯一标识符，格式如 "S001"
        title (str):             歌曲标题
        artist (str):            艺术家/乐队名称
        album (str):             所属专辑名称
        genre (Genre):           音乐流派（Genre 枚举类型）
        duration_seconds (int):  歌曲时长，单位：秒
        play_count (int):        累计播放次数（用于热度计算和 autoplay 优先级）
        like_count (int):        累计点赞次数（用于热度计算和推荐）
    """

    # ======================== 基础字段 ========================
    song_id: str
    title: str
    artist: str
    album: str
    genre: Genre
    duration_seconds: int
    play_count: int = 0          # 默认 0，从数据集加载或播放模拟中累加
    like_count: int = 0          # 默认 0，从数据集加载或用户交互中累加

    # ======================== 特殊方法 ========================

    def __repr__(self) -> str:
        """
        返回 Song 对象的可读字符串表示。

        格式:
            Song(S001, "Bohemian Rhapsody" by Queen, Pop, 355s)

        设计理由:
            - 包含 song_id 便于调试和日志追踪
            - 显示 title 和 artist 是最直观的识别信息
            - 显示 genre 和 duration 有助于快速了解歌曲属性
        """
        return (
            f'Song({self.song_id}, "{self.title}" by {self.artist}, '
            f"{self.genre.value}, {self.duration_seconds}s)"
        )

    def __eq__(self, other: object) -> bool:
        """
        判断两首歌曲是否相等。

        比较标准: song_id（歌曲唯一标识符）

        设计理由:
            - song_id 是歌曲的唯一标识，符合数据库主键的设计思想
            - 即使两首歌的标题、艺术家等元数据完全相同，
              只要 song_id 不同，就是不同的歌曲（例如：同一首歌的现场版 vs 录音室版）
            - 这确保了在 BST、堆、链表等数据结构中能精确定位歌曲

        参数:
            other: 要比较的另一个对象

        返回:
            True 当且仅当 other 是 Song 且 song_id 相同
        """
        if not isinstance(other, Song):
            return NotImplemented
        return self.song_id == other.song_id

    def __lt__(self, other: object) -> bool:
        """
        比较两首歌的"大小"，用于排序。

        比较标准: (play_count, like_count) 元组降序比较

        排序逻辑:
            第一关键字: play_count（播放次数） — 反映歌曲的流行度和传播广度
            第二关键字: like_count（点赞次数） — 在播放次数相同时，反映歌曲的用户喜爱度

        设计理由:
            - 音乐流媒体场景下，播放量和点赞数是衡量歌曲"热度"最直接的指标
            - 将 play_count 作为第一关键字，因为它更客观地反映听歌频率
            - 将 like_count 作为第二关键字，在播放次数相同时区分质量和用户偏好
            - 此排序标准与 Task 4（Autoplay 堆）的评分公式保持一致，
              便于在多种结构中统一使用热度排序

        注意:
            这是"小于"运算符，但实际语义是"热度更低"。
            因此 play_count 越小、like_count 越少的歌曲被视为"更小"。
            如果需要热度从高到低排序，使用 reverse=True 或调用 sorted() 后反转。

        参数:
            other: 要比较的另一个 Song 对象

        返回:
            True 当 self 的热度（play_count, like_count）低于 other 时
        """
        if not isinstance(other, Song):
            return NotImplemented

        # 第一关键字: play_count（播放次数越多 → 热度越高 → 在排序中"更大"）
        if self.play_count != other.play_count:
            return self.play_count < other.play_count

        # 第二关键字: like_count（点赞越多 → 热度越高 → 在排序中"更大"）
        if self.like_count != other.like_count:
            return self.like_count < other.like_count

        # 如果播放和点赞都相同，按歌名字母序作为稳定的第三关键字
        return self.title.lower() > other.title.lower()

    def __hash__(self) -> int:
        """
        返回 Song 对象的哈希值。

        基于 song_id 计算哈希，与 __eq__ 保持一致。
        这使得 Song 对象可以作为 dict 的 key 或放入 set 中。

        返回:
            song_id 的哈希值
        """
        return hash(self.song_id)

    # ======================== 辅助方法 ========================

    def to_dict(self) -> dict:
        """
        将 Song 对象转换为字典，便于写入 CSV 或 JSON。

        返回:
            包含所有字段的字典，genre 转换为字符串形式
        """
        return {
            "song_id": self.song_id,
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "genre": self.genre.value,       # 存储流派名称字符串
            "duration_seconds": self.duration_seconds,
            "play_count": self.play_count,
            "like_count": self.like_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Song":
        """
        从字典创建 Song 对象，用于从 CSV 加载数据。

        参数:
            data: 包含歌曲字段的字典，genre 字段可以是字符串或 Genre 枚举

        返回:
            新创建的 Song 对象
        """
        # 如果 genre 是字符串，先转换为 Genre 枚举
        genre = data["genre"]
        if isinstance(genre, str):
            genre = Genre.from_string(genre)

        return cls(
            song_id=str(data["song_id"]),
            title=str(data["title"]),
            artist=str(data["artist"]),
            album=str(data["album"]),
            genre=genre,
            duration_seconds=int(data["duration_seconds"]),
            play_count=int(data.get("play_count", 0)),
            like_count=int(data.get("like_count", 0)),
        )

    def display_duration(self) -> str:
        """
        以「分:秒」格式返回歌曲时长，便于界面展示。

        返回:
            格式化后的时长字符串，如 "5:55"
        """
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"
