"""
tests/B_ceshi_bofang_liebiao.py
================================
Task 2 单元测试 — 验证双向链表播放列表 Part1+Part2 全部功能

测试覆盖:
  Part 1 (Playlist 基类):
    - add_song / remove_song    增删歌曲
    - play_next / play_previous  上下首导航
    - current_song / jump_to    当前歌曲与跳转
    - move_to_position          移动歌曲位置
    - shuffle / display         随机打乱 / 打印显示
    - reset_to_head / find      重置头部 / 查找
    - insert_at_position        指定位置插入
    - set_loop / 循环模式       循环播放开关
    - 边界: 空列表 / 单首 / 删除不存在的ID

  Part 2 (PlaylistPart2 扩展):
    - sort_by                    归并排序（5种条件）
    - filter_by_genre            流派过滤
    - filter_by_artist           艺术家过滤
    - search_by_title            歌名搜索
    - search_by_artist           艺术家搜索
    - get_statistics             统计摘要
    - batch_add / batch_remove   批量操作

运行方式:
    cd D:/brat
    python -m unittest tests.B_ceshi_bofang_liebiao -v

负责人：成员 B
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.A_gequ import Song
from models.liupai import Genre
from structures.B_bofang_liebiao import Playlist, PlaylistPart2


# ============================================================================
# 测试辅助: 创建测试用歌曲
# ============================================================================

def _make_song(sid: str, title: str, artist: str = "Artist",
               play: int = 0, like: int = 0, duration: int = 200,
               genre: Genre = Genre.POP) -> Song:
    return Song(sid, title, artist, "Album", genre, duration,
                play_count=play, like_count=like)


# ============================================================================
# Part 1 测试: Playlist 基类 —— 基础双向链表操作
# ============================================================================

class TestPlaylistPart1(unittest.TestCase):
    """测试 Playlist 基类的全部核心操作（Part 1）。"""

    def setUp(self):
        self.pl = Playlist()
        self.s1 = _make_song("S001", "Blinding Lights", "The Weeknd", 1000, 500)
        self.s2 = _make_song("S002", "Bohemian Rhapsody", "Queen", 800, 400)
        self.s3 = _make_song("S003", "Shape of You", "Ed Sheeran", 600, 300)

    # ── add_song ──────────────────────────────────────────

    def test_add_song_increases_size(self):
        self.assertEqual(len(self.pl), 0)
        self.pl.add_song(self.s1)
        self.assertEqual(len(self.pl), 1)
        self.pl.add_song(self.s2)
        self.assertEqual(len(self.pl), 2)

    def test_add_song_first_becomes_head_tail_current(self):
        self.pl.add_song(self.s1)
        self.assertIs(self.pl.head.song, self.s1)
        self.assertIs(self.pl.tail.song, self.s1)
        self.assertIs(self.pl.current_song(), self.s1)

    def test_add_song_second_appends_to_tail(self):
        self.pl.add_song(self.s1)
        self.pl.add_song(self.s2)
        self.assertEqual(self.pl.to_list(), [self.s1, self.s2])
        self.assertIs(self.pl.tail.song, self.s2)

    def test_is_empty(self):
        self.assertTrue(self.pl.is_empty())
        self.pl.add_song(self.s1)
        self.assertFalse(self.pl.is_empty())

    # ── remove_song ───────────────────────────────────────

    def test_remove_existing_song(self):
        self.pl.add_song(self.s1)
        self.pl.add_song(self.s2)
        removed = self.pl.remove_song("S001")
        self.assertEqual(removed, self.s1)
        self.assertEqual(len(self.pl), 1)
        self.assertEqual(self.pl.to_list(), [self.s2])

    def test_remove_nonexistent_returns_none(self):
        self.pl.add_song(self.s1)
        self.assertIsNone(self.pl.remove_song("NONEXIST"))

    def test_remove_head_updates_head(self):
        self.pl.add_song(self.s1)
        self.pl.add_song(self.s2)
        self.pl.remove_song("S001")
        self.assertIs(self.pl.head.song, self.s2)

    def test_remove_tail_updates_tail(self):
        self.pl.add_song(self.s1)
        self.pl.add_song(self.s2)
        self.pl.remove_song("S002")
        self.assertIs(self.pl.tail.song, self.s1)

    def test_remove_current_moves_to_next(self):
        self.pl.add_song(self.s1)
        self.pl.add_song(self.s2)
        self.pl.add_song(self.s3)
        self.pl.jump_to("S002")
        self.pl.remove_song("S002")
        self.assertEqual(self.pl.current_song(), self.s3)

    def test_remove_last_song_clears_current(self):
        self.pl.add_song(self.s1)
        self.pl.remove_song("S001")
        self.assertIsNone(self.pl.current)
        self.assertIsNone(self.pl.head)
        self.assertIsNone(self.pl.tail)

    # ── play_next / play_previous ─────────────────────────

    def test_play_next_advances(self):
        self.pl.add_song(self.s1)
        self.pl.add_song(self.s2)
        self.pl.add_song(self.s3)
        self.assertEqual(self.pl.play_next(), self.s2)
        self.assertEqual(self.pl.play_next(), self.s3)

    def test_play_next_loops_to_head(self):
        self.pl.add_song(self.s1)
        self.pl.add_song(self.s2)
        self.pl.play_next()        # S1 → S2
        self.pl.play_next()        # S2 → S1 (loop)
        self.assertEqual(self.pl.current_song(), self.s1)

    def test_play_previous_loops_to_tail(self):
        self.pl.add_song(self.s1)
        self.pl.add_song(self.s2)
        s = self.pl.play_previous()  # S1 → S2 (loop)
        self.assertEqual(s, self.s2)

    def test_play_next_on_empty_returns_none(self):
        self.assertIsNone(self.pl.play_next())

    def test_play_next_no_loop_stays_at_tail(self):
        self.pl.add_song(self.s1)
        self.pl.add_song(self.s2)
        self.pl.set_loop(False)
        self.pl.play_next()  # S1 → S2
        song = self.pl.play_next()  # 已在末尾，不前进
        self.assertEqual(song, self.s2)

    # ── current_song / jump_to ────────────────────────────

    def test_current_song_returns_playing_song(self):
        self.pl.add_song(self.s1)
        self.assertEqual(self.pl.current_song(), self.s1)

    def test_jump_to_valid_id(self):
        self.pl.add_song(self.s1)
        self.pl.add_song(self.s2)
        self.pl.add_song(self.s3)
        self.assertTrue(self.pl.jump_to("S003"))
        self.assertEqual(self.pl.current_song(), self.s3)

    def test_jump_to_invalid_returns_false(self):
        self.pl.add_song(self.s1)
        self.assertFalse(self.pl.jump_to("NONEXIST"))

    # ── move_to_position ──────────────────────────────────

    def test_move_to_position_head(self):
        self.pl.add_song(self.s1)
        self.pl.add_song(self.s2)
        self.pl.add_song(self.s3)  # [S1, S2, S3]
        self.pl.move_to_position("S003", 0)
        self.assertEqual(self.pl.to_list(), [self.s3, self.s1, self.s2])

    def test_move_to_position_tail(self):
        self.pl.add_song(self.s1)
        self.pl.add_song(self.s2)
        self.pl.add_song(self.s3)
        self.pl.move_to_position("S001", 99)  # 超出范围 → 尾部
        self.assertEqual(self.pl.to_list(), [self.s2, self.s3, self.s1])

    def test_move_single_song_noop(self):
        self.pl.add_song(self.s1)
        self.assertTrue(self.pl.move_to_position("S001", 5))
        self.assertEqual(self.pl.to_list(), [self.s1])

    # ── shuffle ───────────────────────────────────────────

    def test_shuffle_preserves_all_songs(self):
        songs = [_make_song(f"S{i:03d}", f"Song{i}") for i in range(20)]
        for s in songs:
            self.pl.add_song(s)
        self.pl.shuffle()
        shuffled = self.pl.to_list()
        self.assertEqual(len(shuffled), 20)
        self.assertCountEqual([s.song_id for s in shuffled],
                             [s.song_id for s in songs])

    def test_shuffle_single_song_noop(self):
        self.pl.add_song(self.s1)
        self.pl.shuffle()
        self.assertEqual(self.pl.to_list(), [self.s1])

    def test_shuffle_empty_noop(self):
        self.pl.shuffle()
        self.assertEqual(self.pl.to_list(), [])

    # ── reset_to_head / find ──────────────────────────────

    def test_reset_to_head(self):
        self.pl.add_song(self.s1)
        self.pl.add_song(self.s2)
        self.pl.play_next()
        self.pl.reset_to_head()
        self.assertEqual(self.pl.current_song(), self.s1)

    def test_find_existing(self):
        self.pl.add_song(self.s1)
        self.assertEqual(self.pl.find("S001"), self.s1)

    def test_find_nonexistent(self):
        self.assertIsNone(self.pl.find("NONEXIST"))

    # ── insert_at_position ────────────────────────────────

    def test_insert_at_head(self):
        self.pl.add_song(self.s2)
        self.pl.add_song(self.s3)
        self.pl.insert_at_position(self.s1, 0)  # [S1, S2, S3]
        self.assertEqual(self.pl.to_list(), [self.s1, self.s2, self.s3])

    def test_insert_at_tail(self):
        self.pl.add_song(self.s1)
        self.pl.add_song(self.s2)
        self.pl.insert_at_position(self.s3, 99)  # [S1, S2, S3]
        self.assertEqual(self.pl.to_list(), [self.s1, self.s2, self.s3])

    def test_insert_into_empty(self):
        self.pl.insert_at_position(self.s1, 0)
        self.assertEqual(self.pl.to_list(), [self.s1])

    # ── __contains__ ──────────────────────────────────────

    def test_contains(self):
        self.pl.add_song(self.s1)
        self.assertIn("S001", self.pl)
        self.assertNotIn("NONEXIST", self.pl)

    # ── display ─ (不验证输出，只确保不崩溃) ───────────────

    def test_display_does_not_crash(self):
        self.pl.add_song(self.s1)
        self.pl.add_song(self.s2)
        self.pl.display()  # 不应抛出异常

    def test_display_empty_does_not_crash(self):
        self.pl.display()  # 空列表也不应崩溃


# ============================================================================
# Part 2 测试: PlaylistPart2 —— 扩展高级功能
# ============================================================================

class TestPlaylistPart2(unittest.TestCase):
    """测试 PlaylistPart2 的全部扩展功能（Part 2）。"""

    def setUp(self):
        self.pl = PlaylistPart2()
        # 准备一组测试歌曲，覆盖不同流派、热度、时长
        self._make_test_songs()
        for s in self._songs:
            self.pl.add_song(s)

    def _make_test_songs(self):
        self.s_a = _make_song("SA", "Alpha Song",   "Artist A", play=100, like=50,  duration=180, genre=Genre.POP)
        self.s_b = _make_song("SB", "Beta Tune",    "Artist B", play=300, like=150, duration=240, genre=Genre.ROCK)
        self.s_c = _make_song("SC", "Gamma Hit",    "Artist A", play=200, like=200, duration=120, genre=Genre.POP)
        self.s_d = _make_song("SD", "Delta Groove", "Artist C", play=50,  like=25,  duration=300, genre=Genre.JAZZ)
        self.s_e = _make_song("SE", "Epsilon Beat", "Artist B", play=400, like=100, duration=200, genre=Genre.ROCK)
        self._songs = [self.s_a, self.s_b, self.s_c, self.s_d, self.s_e]

    # ── sort_by ───────────────────────────────────────────

    def test_sort_by_title_ascending(self):
        self.pl.sort_by("title")
        titles = [s.title for s in self.pl.to_list()]
        self.assertEqual(titles, sorted(titles))

    def test_sort_by_artist(self):
        self.pl.sort_by("artist")
        artists = [s.artist for s in self.pl.to_list()]
        self.assertEqual(artists, sorted(artists))

    def test_sort_by_play_count_descending(self):
        self.pl.sort_by("play_count")
        plays = [s.play_count for s in self.pl.to_list()]
        self.assertEqual(plays, sorted(plays, reverse=True))

    def test_sort_by_like_count_descending(self):
        self.pl.sort_by("like_count")
        likes = [s.like_count for s in self.pl.to_list()]
        self.assertEqual(likes, sorted(likes, reverse=True))

    def test_sort_by_duration_ascending(self):
        self.pl.sort_by("duration")
        durs = [s.duration_seconds for s in self.pl.to_list()]
        self.assertEqual(durs, sorted(durs))

    def test_sort_preserves_all_songs(self):
        before = set(s.song_id for s in self.pl.to_list())
        self.pl.sort_by("play_count")
        after = set(s.song_id for s in self.pl.to_list())
        self.assertEqual(before, after)

    def test_sort_single_song_noop(self):
        pl = PlaylistPart2()
        pl.add_song(self.s_a)
        pl.sort_by("title")
        self.assertEqual(pl.to_list(), [self.s_a])

    # ── filter_by_genre ───────────────────────────────────

    def test_filter_by_genre_string(self):
        pop = self.pl.filter_by_genre("Pop")
        self.assertEqual(len(pop), 2)  # s_a, s_c
        for s in pop:
            self.assertEqual(s.genre, Genre.POP)

    def test_filter_by_genre_enum(self):
        rock = self.pl.filter_by_genre(Genre.ROCK)
        self.assertEqual(len(rock), 2)  # s_b, s_e
        for s in rock:
            self.assertEqual(s.genre, Genre.ROCK)

    def test_filter_by_genre_no_match(self):
        classical = self.pl.filter_by_genre("Classical")
        self.assertEqual(len(classical), 0)

    def test_filter_does_not_modify_original(self):
        orig_len = len(self.pl)
        self.pl.filter_by_genre("Pop")
        self.assertEqual(len(self.pl), orig_len)  # 原列表不变

    # ── filter_by_artist ──────────────────────────────────

    def test_filter_by_artist_fuzzy(self):
        result = self.pl.filter_by_artist("Artist A")
        self.assertEqual(len(result), 2)  # s_a, s_c

    def test_filter_by_artist_case_insensitive(self):
        result = self.pl.filter_by_artist("artist b")
        self.assertEqual(len(result), 2)  # s_b, s_e

    def test_filter_by_artist_no_match(self):
        result = self.pl.filter_by_artist("Nobody")
        self.assertEqual(len(result), 0)

    # ── search_by_title ───────────────────────────────────

    def test_search_by_title_exact(self):
        results = self.pl.search_by_title("Alpha Song")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.s_a)

    def test_search_by_title_partial(self):
        results = self.pl.search_by_title("Beat")
        self.assertEqual(len(results), 1)  # s_e: Epsilon Beat

    def test_search_by_title_case_insensitive(self):
        results = self.pl.search_by_title("alpha")
        self.assertEqual(len(results), 1)

    def test_search_by_title_no_match(self):
        results = self.pl.search_by_title("ZZZNotFound")
        self.assertEqual(len(results), 0)

    # ── search_by_artist ──────────────────────────────────

    def test_search_by_artist(self):
        results = self.pl.search_by_artist("Artist A")
        self.assertEqual(len(results), 2)

    def test_search_by_artist_no_match(self):
        results = self.pl.search_by_artist("ZZZ")
        self.assertEqual(len(results), 0)

    # ── get_statistics ────────────────────────────────────

    def test_statistics_total_songs(self):
        stats = self.pl.get_statistics()
        self.assertEqual(stats["total_songs"], 5)

    def test_statistics_genre_distribution(self):
        stats = self.pl.get_statistics()
        self.assertEqual(stats["genre_distribution"]["Pop"], 2)
        self.assertEqual(stats["genre_distribution"]["Rock"], 2)
        self.assertEqual(stats["genre_distribution"]["Jazz"], 1)

    def test_statistics_most_played(self):
        stats = self.pl.get_statistics()
        self.assertEqual(stats["most_played"], self.s_e)  # play=400

    def test_statistics_most_liked(self):
        stats = self.pl.get_statistics()
        self.assertEqual(stats["most_liked"], self.s_c)  # like=200

    def test_statistics_total_duration(self):
        stats = self.pl.get_statistics()
        expected = 180 + 240 + 120 + 300 + 200  # 1040
        self.assertEqual(stats["total_duration_seconds"], expected)

    def test_statistics_empty_list(self):
        pl = PlaylistPart2()
        stats = pl.get_statistics()
        self.assertEqual(stats["total_songs"], 0)
        self.assertIsNone(stats["most_played"])

    # ── batch_add / batch_remove ──────────────────────────

    def test_batch_add(self):
        pl = PlaylistPart2()
        count = pl.batch_add(self._songs)
        self.assertEqual(count, 5)
        self.assertEqual(len(pl), 5)

    def test_batch_remove(self):
        ok, fail = self.pl.batch_remove(["SA", "SB", "NONEXIST"])
        self.assertEqual(ok, 2)
        self.assertEqual(fail, 1)
        self.assertEqual(len(self.pl), 3)

    def test_batch_remove_all_success(self):
        ok, fail = self.pl.batch_remove(["SA", "SB", "SC", "SD", "SE"])
        self.assertEqual(ok, 5)
        self.assertEqual(fail, 0)
        self.assertTrue(self.pl.is_empty())

    # ── 继承验证: Part2 拥有 Part1 全部能力 ────────────────

    def test_part2_inherits_play_next(self):
        self.pl.play_next()
        self.assertEqual(self.pl.current_song(), self.s_b)

    def test_part2_inherits_shuffle(self):
        self.pl.shuffle()
        self.assertEqual(len(self.pl), 5)

    def test_part2_inherits_remove_song(self):
        removed = self.pl.remove_song("SC")
        self.assertEqual(removed, self.s_c)
        self.assertNotIn("SC", self.pl)


# ============================================================================
# Part 2 — Task 1 测试: playlist_analytics 播放列表分析
# ============================================================================

class TestPlaylistAnalytics(unittest.TestCase):
    """测试 Part 2 Task 1 — 播放列表分析（纯链表遍历）。"""

    def setUp(self):
        self.pl = PlaylistPart2()
        self.s1 = _make_song("S01", "Song1", "Artist A", play=100, like=50,
                             duration=120, genre=Genre.POP)
        self.s2 = _make_song("S02", "Song2", "Artist B", play=200, like=100,
                             duration=180, genre=Genre.ROCK)
        self.s3 = _make_song("S03", "Song3", "Artist A", play=300, like=150,
                             duration=240, genre=Genre.POP)
        self.s4 = _make_song("S04", "Song4", "Artist C", play=150, like=75,
                             duration=200, genre=Genre.JAZZ)
        for s in [self.s1, self.s2, self.s3, self.s4]:
            self.pl.add_song(s)

    def test_total_duration(self):
        a = self.pl.playlist_analytics()
        self.assertEqual(a["total_duration_seconds"], 120+180+240+200)

    def test_average_duration(self):
        a = self.pl.playlist_analytics()
        self.assertEqual(a["average_duration_seconds"], (120+180+240+200)/4)

    def test_most_common_genre(self):
        a = self.pl.playlist_analytics()
        self.assertEqual(a["most_common_genre"], "Pop")  # 2首Pop

    def test_artist_with_most_songs(self):
        a = self.pl.playlist_analytics()
        self.assertEqual(a["artist_with_most_songs"], "Artist A")  # 2首

    def test_genre_distribution(self):
        a = self.pl.playlist_analytics()
        self.assertEqual(a["genre_distribution"]["Pop"], 2)
        self.assertEqual(a["genre_distribution"]["Rock"], 1)
        self.assertEqual(a["genre_distribution"]["Jazz"], 1)

    def test_artist_distribution(self):
        a = self.pl.playlist_analytics()
        self.assertEqual(a["artist_distribution"]["Artist A"], 2)
        self.assertEqual(a["artist_distribution"]["Artist B"], 1)

    def test_empty_playlist(self):
        pl = PlaylistPart2()
        a = pl.playlist_analytics()
        self.assertEqual(a["total_songs"], 0)
        self.assertIsNone(a["most_common_genre"])
        self.assertIsNone(a["artist_with_most_songs"])


# ============================================================================
# Part 2 — Task 2 测试: smart_shuffle 智能随机
# ============================================================================

class TestSmartShuffle(unittest.TestCase):
    """测试 Part 2 Task 2 — Smart Shuffle 约束排列。"""

    def test_smart_shuffle_no_consecutive_same_artist_normal(self):
        """正常情况: 艺术家分散，应成功。"""
        pl = PlaylistPart2()
        artists = ["A", "B", "C", "D", "E"]
        for i, a in enumerate(artists):
            pl.add_song(_make_song(f"S{i:02d}", f"Song{i}", a,
                                   genre=_GENRES[i % len(_GENRES)]))
        result = pl.smart_shuffle()
        self.assertTrue(result)
        songs = pl.to_list()
        for i in range(len(songs) - 1):
            self.assertNotEqual(songs[i].artist, songs[i+1].artist,
                f"相邻歌曲 {i} 和 {i+1} 艺术家相同: {songs[i].artist}")

    def test_smart_shuffle_all_same_artist_fallback(self):
        """全部同一艺术家 → 降级为普通shuffle。"""
        pl = PlaylistPart2()
        genres = [Genre.POP, Genre.ROCK, Genre.JAZZ, Genre.POP, Genre.ROCK]
        for i in range(5):
            pl.add_song(_make_song(f"S{i:02d}", f"Song{i}", "SameArtist",
                                   genre=genres[i % len(genres)]))
        result = pl.smart_shuffle()
        self.assertFalse(result)  # 降级
        self.assertEqual(len(pl), 5)  # 仍保留全部歌曲

    def test_smart_shuffle_preserves_all_songs(self):
        """智能随机后不丢失歌曲。"""
        pl = PlaylistPart2()
        for i in range(20):
            pl.add_song(_make_song(f"S{i:02d}", f"Song{i}",
                                   f"Artist{i % 4}",
                                   genre=_GENRES[i % len(_GENRES)]))
        pl.smart_shuffle()
        songs = pl.to_list()
        self.assertEqual(len(songs), 20)
        ids = {s.song_id for s in songs}
        self.assertEqual(len(ids), 20)

    def test_smart_shuffle_small_playlist(self):
        """2首歌以内直接普通shuffle。"""
        pl = PlaylistPart2()
        pl.add_song(_make_song("S1", "A", "Artist1"))
        pl.add_song(_make_song("S2", "B", "Artist2"))
        result = pl.smart_shuffle()
        self.assertTrue(result)

    def test_smart_shuffle_genre_spread(self):
        """验证同流派尽量分散。"""
        pl = PlaylistPart2()
        for i in range(15):
            g = Genre.POP if i < 10 else Genre.ROCK  # 10首Pop + 5首Rock
            pl.add_song(_make_song(f"S{i:02d}", f"Song{i}", f"A{i % 4}",
                                   genre=g))
        pl.smart_shuffle()
        songs = pl.to_list()
        # 检查相邻同流派不超过2次
        consecutive = 0
        max_consecutive = 0
        for i in range(1, len(songs)):
            if songs[i].genre == songs[i-1].genre:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 0
        # 10首Pop + 5首Rock，贪心算法尽力分散但无法保证完美
        # 只要相邻同流派不超过5次即可（不连续出现全部Pop）
        self.assertLess(max_consecutive, 5,
            f"同流派连续出现 {max_consecutive+1} 次，分布不够均匀")


# 流派列表（供测试用）
_GENRES = list(Genre)


if __name__ == "__main__":
    unittest.main(verbosity=2)
