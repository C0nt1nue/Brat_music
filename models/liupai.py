"""
models/genre.py
==============
Task 1 — 数据建模：Genre 枚举类

定义音乐流派的枚举类型，用于 Song 类中的 genre 字段。
使用 Python 内置的 Enum 确保流派值的类型安全和可读性。

负责人：成员 A
"""

from enum import Enum


class Genre(Enum):
    """
    音乐流派枚举

    所有流派使用大写命名，遵循 Python 枚举命名规范。
    枚举值使用可读的英文名称，便于 CSV 数据生成和界面展示。
    """
    POP = "Pop"                  # 流行
    ROCK = "Rock"                # 摇滚
    JAZZ = "Jazz"                # 爵士
    HIP_HOP = "Hip Hop"          # 嘻哈
    CLASSICAL = "Classical"      # 古典
    ELECTRONIC = "Electronic"    # 电子
    RNB = "R&B"                  # 节奏布鲁斯
    COUNTRY = "Country"          # 乡村
    LATIN = "Latin"              # 拉丁
    INDIE = "Indie"              # 独立音乐
    METAL = "Metal"              # 金属
    FOLK = "Folk"                # 民谣
    REGGAE = "Reggae"            # 雷鬼
    SOUL = "Soul"                # 灵魂乐
    BLUES = "Blues"              # 蓝调
    KPOP = "K-Pop"               # 韩国流行

    @classmethod
    def from_string(cls, value: str) -> "Genre":
        """
        从字符串（不区分大小写）转换为 Genre 枚举值。

        参数:
            value: 流派名称字符串，如 "pop", "Rock", "hip hop"

        返回:
            对应的 Genre 枚举值

        抛出:
            ValueError: 当字符串不匹配任何已知流派时
        """
        for genre in cls:
            if genre.value.lower() == value.lower():
                return genre
        raise ValueError(f"未知的音乐流派: '{value}'。可用流派: {[g.value for g in cls]}")

    @classmethod
    def all_genres(cls) -> list[str]:
        """
        返回所有可用流派的字符串列表。

        返回:
            流派名称列表，如 ["Pop", "Rock", "Jazz", ...]
        """
        return [g.value for g in cls]
