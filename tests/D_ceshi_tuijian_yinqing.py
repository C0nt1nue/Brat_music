"""
tests/D_ceshi_tuijian_yinqing.py
=================================
Part 2 — Task 3 测试: 推荐引擎 单元测试

测试覆盖:
  - recommend_songs 正常推荐流程
  - 流派优先 vs 艺术家优先
  - 空播放列表/空BST 边界
  - 推荐数量控制
  - 不推荐已在播放列表中的歌曲

运行方式:
    cd D:/brat
    python -m unittest tests.D_ceshi_tuijian_yinqing -v

负责人：成员 D
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.A_gequ import Song
from models.liupai import Genre
from structures.C_ercha_sousuo_shu import BST
from structures.B_bofang_liebiao import PlaylistPart2
from structures.D_tuijian_yinqing import recommend_songs, _recommend_global_top


class TestRecommendEngine(unittest.TestCase):
    """测试 Part 2 Task 3 — 推荐引擎。"""

    @classmethod
    def setUpClass(cls):
        """构建测试用的 BST + Playlist。"""
        cls.bst = BST()
        cls.all_songs = []
        genres = list(Genre)
        for i in range(30):
            g = genres[i % len(genres)]
            s = Song(f"S{i:03d}", f"RecSong{i:03d}", f"Artist{i % 6}",
                     f"Album{i % 5}", g, 180 + i * 5,
                     play_count=i * 1000, like_count=i * 500)
            cls.all_songs.append(s)
            cls.bst.insert(s)

        cls.playlist = PlaylistPart2()
        for s in cls.all_songs[:5]:
            cls.playlist.add_song(s)

    def test_recommend_returns_5_songs(self):
        recs = recommend_songs(self.playlist, self.bst, n=5)
        self.assertLessEqual(len(recs), 5)
        self.assertGreater(len(recs), 0)

    def test_no_duplicates_in_playlist(self):
        """推荐结果不应包含已在播放列表中的歌曲。"""
        recs = recommend_songs(self.playlist, self.bst, n=5)
        for s in recs:
            self.assertNotIn(s.song_id, self.playlist)

    def test_recommend_with_prefer_genre(self):
        """同流派优先模式。"""
        recs = recommend_songs(self.playlist, self.bst, n=5, prefer_genre=True)
        self.assertGreater(len(recs), 0)

    def test_recommend_with_prefer_artist(self):
        """同艺术家优先模式。"""
        recs = recommend_songs(self.playlist, self.bst, n=5, prefer_genre=False)
        self.assertGreater(len(recs), 0)

    def test_empty_playlist_current(self):
        """无当前播放歌曲时返回全局 top-N。"""
        pl = PlaylistPart2()
        recs = recommend_songs(pl, self.bst, n=5)
        self.assertEqual(len(recs), 5)
        for s in recs:
            self.assertIsInstance(s, Song)

    def test_none_inputs(self):
        recs = recommend_songs(None, None)
        self.assertEqual(recs, [])

    def test_global_top_excludes_ids(self):
        recs = _recommend_global_top(self.bst, self.playlist, n=3,
                                     exclude_ids={"S000", "S001"})
        self.assertLessEqual(len(recs), 3)
        for s in recs:
            self.assertNotIn(s.song_id, {"S000", "S001"})

    def test_n_larger_than_available(self):
        """请求数量超过可用候选时返回尽可能多的。"""
        pl_small = PlaylistPart2()
        pl_small.add_song(self.all_songs[0])
        recs = recommend_songs(pl_small, self.bst, n=50)
        self.assertLessEqual(len(recs), 50)


if __name__ == "__main__":
    unittest.main(verbosity=2)
