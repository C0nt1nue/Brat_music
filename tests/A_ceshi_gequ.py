"""
tests/A_ceshi_gequ.py
==================
Task 5 — 单元测试：验证 Song 类和 Genre 枚举的正确性

测试覆盖:
  - Genre 枚举的创建和 from_string() 转换
  - Song 对象的创建和字段验证
  - __repr__ 输出格式
  - __eq__ 基于 song_id 的比较
  - __lt__ 基于热度 (play_count, like_count) 的比较
  - __hash__ 与 __eq__ 的一致性
  - to_dict() / from_dict() 往返转换
  - display_duration() 时长格式化
  - 边界情况（相同 play_count 但不同 like_count、类型错误等）

运行方式:
    cd D:/brat
    python -m pytest tests/A_ceshi_gequ.py -v
    或
    python -m unittest tests.test_song -v

负责人：成员 A
"""

import sys
import unittest
from pathlib import Path

# 将项目根目录加入 sys.path，确保模块可以被导入
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.liupai import Genre
from models.A_gequ import Song


class TestGenreEnum(unittest.TestCase):
    """
    测试 Genre 枚举类

    验证点:
      1. 枚举值正确
      2. from_string() 大小写不敏感转换
      3. 无效字符串抛出 ValueError
      4. all_genres() 返回完整列表
    """

    def test_genre_values(self):
        """验证每个枚举成员的值是否正确"""
        self.assertEqual(Genre.POP.value, "Pop")
        self.assertEqual(Genre.ROCK.value, "Rock")
        self.assertEqual(Genre.JAZZ.value, "Jazz")
        self.assertEqual(Genre.HIP_HOP.value, "Hip Hop")
        self.assertEqual(Genre.CLASSICAL.value, "Classical")

    def test_from_string_exact_match(self):
        """测试精确字符串匹配"""
        genre = Genre.from_string("Pop")
        self.assertEqual(genre, Genre.POP)

    def test_from_string_case_insensitive(self):
        """测试大小写不敏感匹配"""
        self.assertEqual(Genre.from_string("pop"), Genre.POP)
        self.assertEqual(Genre.from_string("ROCK"), Genre.ROCK)
        self.assertEqual(Genre.from_string("Jazz"), Genre.JAZZ)
        self.assertEqual(Genre.from_string("k-PoP"), Genre.KPOP)

    def test_from_string_with_spaces(self):
        """测试带空格的流派名称"""
        self.assertEqual(Genre.from_string("Hip Hop"), Genre.HIP_HOP)
        self.assertEqual(Genre.from_string("hip hop"), Genre.HIP_HOP)

    def test_from_string_invalid_raises_error(self):
        """测试无效流派名抛出 ValueError"""
        with self.assertRaises(ValueError) as ctx:
            Genre.from_string("InvalidGenre")
        self.assertIn("InvalidGenre", str(ctx.exception))

    def test_from_string_empty_raises_error(self):
        """测试空字符串抛出 ValueError"""
        with self.assertRaises(ValueError):
            Genre.from_string("")

    def test_all_genres_returns_all_values(self):
        """测试 all_genres() 返回所有流派"""
        all_genres = Genre.all_genres()
        self.assertIsInstance(all_genres, list)
        self.assertEqual(len(all_genres), len(Genre))
        # 验证包含已知流派
        self.assertIn("Pop", all_genres)
        self.assertIn("Rock", all_genres)
        self.assertIn("Jazz", all_genres)


class TestSongClass(unittest.TestCase):
    """
    测试 Song 数据类

    验证点:
      1. Song 对象创建和字段访问
      2. __repr__ 输出格式
      3. __eq__ 基于 song_id 比较
      4. __lt__ 热度比较（play_count → like_count → title）
      5. __hash__ 与 __eq__ 一致性
      6. to_dict() / from_dict() 往返转换
      7. display_duration() 时长格式化
      8. 边界和异常情况
    """

    @classmethod
    def setUpClass(cls):
        """创建测试用的 Song 实例，供所有测试方法共用"""
        cls.song_pop = Song(
            song_id="S001",
            title="Blinding Lights",
            artist="The Weeknd",
            album="After Hours",
            genre=Genre.POP,
            duration_seconds=200,
            play_count=100_000,
            like_count=50_000,
        )
        cls.song_rock = Song(
            song_id="S002",
            title="Bohemian Rhapsody",
            artist="Queen",
            album="A Night at the Opera",
            genre=Genre.ROCK,
            duration_seconds=355,
            play_count=200_000,
            like_count=80_000,
        )
        # 与 S001 相同 song_id，但其他字段不同
        cls.song_pop_duplicate = Song(
            song_id="S001",
            title="Different Title",
            artist="Different Artist",
            album="Different Album",
            genre=Genre.ELECTRONIC,
            duration_seconds=999,
            play_count=1,
            like_count=1,
        )

    # ── 创建与字段验证 ──

    def test_song_creation(self):
        """测试 Song 对象正常创建，所有字段正确赋值"""
        song = self.song_pop
        self.assertEqual(song.song_id, "S001")
        self.assertEqual(song.title, "Blinding Lights")
        self.assertEqual(song.artist, "The Weeknd")
        self.assertEqual(song.album, "After Hours")
        self.assertEqual(song.genre, Genre.POP)
        self.assertEqual(song.duration_seconds, 200)
        self.assertEqual(song.play_count, 100_000)
        self.assertEqual(song.like_count, 50_000)

    def test_song_default_counts(self):
        """测试 play_count 和 like_count 的默认值"""
        song = Song(
            song_id="S999",
            title="New Song",
            artist="New Artist",
            album="New Album",
            genre=Genre.INDIE,
            duration_seconds=180,
        )
        self.assertEqual(song.play_count, 0)
        self.assertEqual(song.like_count, 0)

    # ── __repr__ ──

    def test_repr_format(self):
        """测试 __repr__ 输出格式"""
        rep = repr(self.song_pop)
        self.assertIn("Song", rep)             # 包含类名前缀
        self.assertIn("S001", rep)             # 包含 song_id
        self.assertIn("Blinding Lights", rep)  # 包含 title
        self.assertIn("The Weeknd", rep)       # 包含 artist
        self.assertIn("Pop", rep)              # 包含 genre
        self.assertIn("200s", rep)             # 包含时长

    def test_repr_includes_quotes_around_title(self):
        """测试 __repr__ 中歌名用引号包裹"""
        rep = repr(self.song_pop)
        self.assertIn('"Blinding Lights"', rep)

    # ── __eq__ ──

    def test_eq_same_id_returns_true(self):
        """测试相同 song_id 的 Song 对象相等"""
        self.assertEqual(self.song_pop, self.song_pop_duplicate)
        # 尽管其他字段完全不同，__eq__ 只看 song_id

    def test_eq_different_id_returns_false(self):
        """测试不同 song_id 的 Song 对象不相等"""
        self.assertNotEqual(self.song_pop, self.song_rock)

    def test_eq_non_song_returns_not_implemented(self):
        """测试与非 Song 对象比较时返回 NotImplemented"""
        result = self.song_pop.__eq__("not a song")
        self.assertIs(result, NotImplemented)

    def test_eq_none_returns_not_implemented(self):
        """测试与 None 比较不应抛出异常"""
        # __eq__ 接收 None 时应返回 NotImplemented，而非崩溃
        self.assertFalse(self.song_pop == None)  # noqa: E711

    # ── __lt__ ──

    def test_lt_by_play_count(self):
        """测试按 play_count（第一关键字）比较"""
        # song_pop: play_count=100k, song_rock: play_count=200k
        # song_pop 播放更少 → 热度更低 → "小于" song_rock
        self.assertTrue(self.song_pop < self.song_rock)
        self.assertFalse(self.song_rock < self.song_pop)

    def test_lt_same_play_count_falls_back_to_like_count(self):
        """测试 play_count 相同时，按 like_count（第二关键字）比较"""
        a = Song("A", "A", "A", "A", Genre.POP, 100, play_count=1000, like_count=500)
        b = Song("B", "B", "B", "B", Genre.POP, 100, play_count=1000, like_count=800)
        # a 的 like_count 更少 → a < b
        self.assertTrue(a < b)
        self.assertFalse(b < a)

    def test_lt_same_play_and_like_falls_back_to_title(self):
        """测试 play_count 和 like_count 都相同时，按 title（第三关键字）比较"""
        a = Song("A", "Alpha", "X", "X", Genre.POP, 100, play_count=1000, like_count=500)
        b = Song("B", "Beta",  "X", "X", Genre.POP, 100, play_count=1000, like_count=500)
        # title 降序（注意 __lt__ 中 title 比较用的是 >）
        # "alpha" < "beta" → a > b（因为 __lt__ 中 title 用了反向比较作为稳定排序）
        # 实际上: self.title.lower() > other.title.lower()
        # "alpha" > "beta"? No. "alpha" < "beta" in lex order.
        # So for a.title="Alpha" vs b.title="Beta": "alpha" > "beta"? No → False
        # So a < b is False. b < a: "beta" > "alpha"? Yes → True, so b < a.
        # This means b (Beta) is "less than" a (Alpha), meaning Beta comes first in sorted order.
        # This acts as a tiebreaker — the direction doesn't matter much as long as it's deterministic.
        self.assertFalse(a < b)  # Alpha > Beta in this tiebreaker
        self.assertTrue(b < a)   # Beta < Alpha in this tiebreaker

    def test_lt_non_song_returns_not_implemented(self):
        """测试与非 Song 对象比较时返回 NotImplemented"""
        result = self.song_pop.__lt__("not a song")
        self.assertIs(result, NotImplemented)

    def test_lt_reflexive(self):
        """测试自反性：a < a 应为 False"""
        self.assertFalse(self.song_pop < self.song_pop)

    def test_lt_transitive(self):
        """测试传递性：若 a < b 且 b < c，则 a < c"""
        a = Song("A", "A", "A", "A", Genre.POP, 100, play_count=100, like_count=10)
        b = Song("B", "B", "B", "B", Genre.POP, 100, play_count=200, like_count=20)
        c = Song("C", "C", "C", "C", Genre.POP, 100, play_count=300, like_count=30)
        self.assertTrue(a < b)
        self.assertTrue(b < c)
        self.assertTrue(a < c)

    # ── __hash__ ──

    def test_hash_based_on_song_id(self):
        """测试哈希值基于 song_id"""
        self.assertEqual(hash(self.song_pop), hash("S001"))

    def test_equal_songs_have_equal_hash(self):
        """测试相等的 Song（相同 song_id）有相同哈希值"""
        self.assertEqual(hash(self.song_pop), hash(self.song_pop_duplicate))

    def test_songs_in_set_dedup_by_id(self):
        """测试放入 set 时按 song_id 去重"""
        song_set = {self.song_pop, self.song_pop_duplicate, self.song_rock}
        self.assertEqual(len(song_set), 2)  # S001 x2 + S002 = 去重后 2 个

    # ── to_dict / from_dict 往返转换 ──

    def test_to_dict_returns_correct_keys(self):
        """测试 to_dict() 返回包含所有字段的字典"""
        d = self.song_pop.to_dict()
        expected_keys = {
            "song_id", "title", "artist", "album",
            "genre", "duration_seconds", "play_count", "like_count",
        }
        self.assertEqual(set(d.keys()), expected_keys)

    def test_to_dict_genre_is_string(self):
        """测试 to_dict() 中 genre 字段为字符串"""
        d = self.song_pop.to_dict()
        self.assertIsInstance(d["genre"], str)
        self.assertEqual(d["genre"], "Pop")

    def test_from_dict_creates_equal_song(self):
        """测试 from_dict() 创建的 Song 与原始对象相等"""
        d = self.song_pop.to_dict()
        recreated = Song.from_dict(d)
        self.assertEqual(self.song_pop, recreated)
        self.assertEqual(self.song_pop.title, recreated.title)
        self.assertEqual(self.song_pop.genre, recreated.genre)

    def test_from_dict_with_string_genre(self):
        """测试 from_dict() 中 genre 为字符串时的自动转换"""
        d = {
            "song_id": "T001",
            "title": "Test",
            "artist": "Test",
            "album": "Test",
            "genre": "Rock",          # 字符串，非 Genre 枚举
            "duration_seconds": 200,
            "play_count": 0,
            "like_count": 0,
        }
        song = Song.from_dict(d)
        self.assertEqual(song.genre, Genre.ROCK)

    def test_from_dict_with_enum_genre(self):
        """测试 from_dict() 中 genre 已经是枚举时的处理"""
        d = {
            "song_id": "T002",
            "title": "Test",
            "artist": "Test",
            "album": "Test",
            "genre": Genre.JAZZ,      # 已经是枚举值
            "duration_seconds": 300,
            "play_count": 0,
            "like_count": 0,
        }
        song = Song.from_dict(d)
        self.assertEqual(song.genre, Genre.JAZZ)

    def test_roundtrip_to_from_dict(self):
        """测试 Song → dict → Song 往返转换的一致性"""
        original = self.song_rock
        restored = Song.from_dict(original.to_dict())
        # 验证关键字段
        self.assertEqual(original.song_id, restored.song_id)
        self.assertEqual(original.title, restored.title)
        self.assertEqual(original.artist, restored.artist)
        self.assertEqual(original.genre, restored.genre)
        self.assertEqual(original.duration_seconds, restored.duration_seconds)
        self.assertEqual(original.play_count, restored.play_count)
        self.assertEqual(original.like_count, restored.like_count)

    # ── display_duration ──

    def test_display_duration_exact_minute(self):
        """测试整分钟时长的格式化"""
        song = Song("X", "X", "X", "X", Genre.POP, 120)
        self.assertEqual(song.display_duration(), "2:00")

    def test_display_duration_with_seconds(self):
        """测试非整分钟时长的格式化（秒数补零）"""
        song = Song("X", "X", "X", "X", Genre.POP, 205)
        self.assertEqual(song.display_duration(), "3:25")

    def test_display_duration_under_one_minute(self):
        """测试不足一分钟的时长"""
        song = Song("X", "X", "X", "X", Genre.POP, 45)
        self.assertEqual(song.display_duration(), "0:45")

    def test_display_duration_zero(self):
        """测试零时长"""
        song = Song("X", "X", "X", "X", Genre.POP, 0)
        self.assertEqual(song.display_duration(), "0:00")

    def test_display_duration_large(self):
        """测试较长时长（如古典音乐）"""
        song = Song("X", "X", "X", "X", Genre.CLASSICAL, 3725)
        self.assertEqual(song.display_duration(), "62:05")


class TestSongSorting(unittest.TestCase):
    """
    测试 Song 排序行为（与 __lt__ 关联）

    验证 sort() 和 sorted() 在使用 Song.__lt__ 时的正确性。
    """

    def setUp(self):
        """创建一组热度各异的测试歌曲"""
        self.songs = [
            Song("S1", "Hot",       "A", "A", Genre.POP, 100, play_count=1000, like_count=500),
            Song("S2", "Medium",    "B", "B", Genre.POP, 100, play_count=500,  like_count=300),
            Song("S3", "Cold",      "C", "C", Genre.POP, 100, play_count=100,  like_count=50),
            Song("S4", "Same Hot",  "D", "D", Genre.POP, 100, play_count=1000, like_count=400),
            Song("S5", "Same Hot 2","E", "E", Genre.POP, 100, play_count=1000, like_count=400),
        ]

    def test_sort_ascending_by_popularity(self):
        """测试按热度升序排列（默认 __lt__）"""
        sorted_songs = sorted(self.songs)
        # 热度最低的（Cold）排在最前面
        self.assertEqual(sorted_songs[0].song_id, "S3")    # play=100,  like=50
        self.assertEqual(sorted_songs[1].song_id, "S2")    # play=500,  like=300
        # S4 和 S5: play=1000, like=400（title 决定顺序）
        self.assertEqual(sorted_songs[2].song_id, "S5")    # "Same Hot 2"  (lower title → 反向比较更大)
        self.assertEqual(sorted_songs[3].song_id, "S4")    # "Same Hot" (higher title → 反向比较更小)
        # 热度最高的（Hot）排在最后
        self.assertEqual(sorted_songs[4].song_id, "S1")    # play=1000, like=500

    def test_sort_reverse_by_popularity(self):
        """测试按热度降序排列"""
        sorted_songs = sorted(self.songs, reverse=True)
        # 热度最高的排在最前面
        self.assertEqual(sorted_songs[0].song_id, "S1")    # 最热


if __name__ == "__main__":
    unittest.main(verbosity=2)
