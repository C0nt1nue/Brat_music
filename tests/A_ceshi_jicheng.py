"""
tests/A_ceshi_jicheng.py
=========================
Task 5 — 集成测试：验证数据加载器的正确性

测试覆盖:
  - DataLoader 从 CSV 加载 Song 对象
  - 数据加载量验证（≥25 首）
  - 加载的 Song 对象字段完整性
  - DataLoader 对缺失文件的错误处理
  - 条件导入：成员 B/C/D 代码未就绪时不崩溃
  - 成员 B/C/D 代码就绪时的结构加载验证

运行方式:
    cd D:/brat
    python -m unittest tests.test_integration -v

负责人：成员 A
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.A_shuju_jiazai import DataLoader, compute_autoplay_score
from models.A_gequ import Song
from models.liupai import Genre

# 项目根目录下的事先生成好的数据集文件
_DATASET_PATH = str(Path(__file__).parent.parent / "songs_dataset_20000.csv")


class TestDataLoader(unittest.TestCase):
    """
    测试 DataLoader 类的核心功能

    直接使用项目中的 songs_dataset_20000.csv 进行测试。
    """

    @classmethod
    def setUpClass(cls):
        """验证数据集文件存在"""
        if not os.path.exists(_DATASET_PATH):
            raise FileNotFoundError(
                f"数据集文件不存在: {_DATASET_PATH}\n"
                f"请确认 songs_dataset_20000.csv 已放置在项目根目录。"
            )

    def setUp(self):
        """每个测试方法前创建新的 DataLoader 实例"""
        self.loader = DataLoader(_DATASET_PATH)

    # ── load_songs() 测试 ──

    def test_load_songs_returns_list(self):
        """验证 load_songs() 返回 list 类型"""
        songs = self.loader.load_songs()
        self.assertIsInstance(songs, list)

    def test_load_songs_returns_song_objects(self):
        """验证 load_songs() 返回的元素都是 Song 对象"""
        songs = self.loader.load_songs()
        for song in songs:
            self.assertIsInstance(song, Song)

    def test_load_songs_minimum_count(self):
        """验证加载的歌曲数量 ≥ 25"""
        songs = self.loader.load_songs()
        self.assertGreaterEqual(len(songs), 25,
            f"加载了 {len(songs)} 首歌曲，需要至少 25 首")

    def test_load_songs_field_types(self):
        """验证加载的歌曲字段类型正确"""
        songs = self.loader.load_songs()
        song = songs[0]
        self.assertIsInstance(song.song_id, str)
        self.assertIsInstance(song.title, str)
        self.assertIsInstance(song.artist, str)
        self.assertIsInstance(song.album, str)
        self.assertIsInstance(song.genre, Genre)
        self.assertIsInstance(song.duration_seconds, int)
        self.assertIsInstance(song.play_count, int)
        self.assertIsInstance(song.like_count, int)

    def test_load_songs_all_have_positive_duration(self):
        """验证所有加载的歌曲时长 > 0"""
        songs = self.loader.load_songs()
        for song in songs:
            self.assertGreater(song.duration_seconds, 0)

    def test_load_songs_all_unique_ids(self):
        """验证所有加载的歌曲 ID 唯一"""
        songs = self.loader.load_songs()
        ids = [s.song_id for s in songs]
        self.assertEqual(len(ids), len(set(ids)))

    # ── 错误处理测试 ──

    def test_file_not_found_creates_clear_error(self):
        """验证文件不存在时抛出清晰的错误信息"""
        with self.assertRaises(FileNotFoundError) as ctx:
            DataLoader("nonexistent_file.csv")
        err_msg = str(ctx.exception)
        self.assertIn("nonexistent_file.csv", err_msg)
        self.assertIn("CSV 文件不存在", err_msg)

    # ── load_all() 测试 ──

    def test_load_all_returns_dict(self):
        """验证 load_all() 返回 dict"""
        data = self.loader.load_all()
        self.assertIsInstance(data, dict)

    def test_load_all_contains_expected_keys(self):
        """验证 load_all() 返回的字典包含所有预期 key"""
        data = self.loader.load_all()
        self.assertIn("songs", data)
        self.assertIn("bst", data)
        self.assertIn("heap", data)
        self.assertIn("playlist", data)

    def test_load_all_songs_not_empty(self):
        """验证 load_all() 中 songs 不为空"""
        data = self.loader.load_all()
        self.assertGreater(len(data["songs"]), 0)

    # ── 条件导入测试：结构未就绪时应优雅降级 ──

    def test_load_into_bst_handles_missing_module(self):
        """验证 BST 模块不存在时不崩溃，返回 None"""
        result = self.loader.load_into_bst()
        if result is None:
            self.skipTest("BST 模块尚未就绪（预期行为）")
        self.assertIsNotNone(result)

    def test_load_into_autoplay_heap_handles_missing_module(self):
        """验证 AutoplayHeap 模块不存在时不崩溃，返回 None"""
        result = self.loader.load_into_autoplay_heap()
        if result is None:
            self.skipTest("AutoplayHeap 模块尚未就绪（预期行为）")
        self.assertIsNotNone(result)

    def test_load_into_playlist_handles_missing_module(self):
        """验证 Playlist 模块不存在时不崩溃，返回 None"""
        result = self.loader.load_into_playlist()
        if result is None:
            self.skipTest("Playlist 模块尚未就绪（预期行为）")
        self.assertIsNotNone(result)


class TestAutoplayScore(unittest.TestCase):
    """
    测试 compute_autoplay_score() 评分函数
    """

    def setUp(self):
        """创建测试用 Song"""
        self.song_hot = Song(
            "S001", "Hot", "A", "A", Genre.POP, 240,
            play_count=1_000_000,
            like_count=500_000,
        )
        self.song_cold = Song(
            "S002", "Cold", "B", "B", Genre.POP, 60,
            play_count=100,
            like_count=10,
        )

    def test_score_is_positive(self):
        """验证评分分数为正数"""
        score = compute_autoplay_score(self.song_hot)
        self.assertGreater(score, 0)

    def test_hotter_song_gets_higher_score(self):
        """验证更热门的歌曲获得更高的评分"""
        score_hot = compute_autoplay_score(self.song_hot)
        score_cold = compute_autoplay_score(self.song_cold)
        self.assertGreater(score_hot, score_cold,
            f"热门歌曲分数({score_hot})应 > 冷门歌曲分数({score_cold})")

    def test_like_count_has_higher_weight(self):
        """验证 like_count 的权重 (0.5) 高于 play_count (0.2)"""
        a = Song("A", "A", "A", "A", Genre.POP, 200, play_count=1000, like_count=1000)
        b = Song("B", "B", "B", "B", Genre.POP, 200, play_count=1000, like_count=100)
        self.assertGreater(compute_autoplay_score(a), compute_autoplay_score(b))

    def test_duration_bonus_for_optimal_length(self):
        """验证 3-5 分钟时长的歌曲获得奖励分"""
        song_good_duration = Song(
            "G", "Good", "G", "G", Genre.POP, 240,    # 4 分钟
            play_count=1000, like_count=500,
        )
        song_too_short = Song(
            "S", "Short", "S", "S", Genre.POP, 30,    # 30 秒
            play_count=1000, like_count=500,
        )
        self.assertGreater(
            compute_autoplay_score(song_good_duration),
            compute_autoplay_score(song_too_short),
        )


class TestCSVToStructuresPipeline(unittest.TestCase):
    """
    测试完整的数据管道：CSV 文件 → 加载 → 注入结构

    这是 Task 5 的"端到端"验证 —— 确保整个数据流正确无误。
    """

    def test_pipeline_csv_to_songs(self):
        """端到端测试：CSV 文件 → Song 对象列表"""
        if not os.path.exists(_DATASET_PATH):
            self.skipTest("数据集文件不存在，跳过集成测试")
        loader = DataLoader(_DATASET_PATH)
        songs = loader.load_songs()

        self.assertGreaterEqual(len(songs), 25)

        for song in songs:
            self.assertIsInstance(song, Song)
            self.assertTrue(song.song_id)
            self.assertTrue(song.title)
            self.assertIsInstance(song.genre, Genre)
            self.assertGreater(song.duration_seconds, 0)

    def test_pipeline_load_all_no_crash(self):
        """验证 load_all() 无论如何都不会崩溃（结构就绪或未就绪）"""
        if not os.path.exists(_DATASET_PATH):
            self.skipTest("数据集文件不存在，跳过集成测试")
        loader = DataLoader(_DATASET_PATH)
        try:
            data = loader.load_all()
            self.assertIn("songs", data)
            self.assertGreater(len(data["songs"]), 0)
        except Exception as e:
            self.fail(f"load_all() 不应该抛出异常，但抛出了: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
