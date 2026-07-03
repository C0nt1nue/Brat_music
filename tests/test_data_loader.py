

import unittest
import os
import tempfile
from data.csv_generator import generate_csv
from data.data_loader import (load_songs_from_csv, load_into_all_structures,
                               load_catalogue_only, load_playlist_only,
                               load_autoplay_only, ensure_dataset)
from data_structures.song import Song
from data_structures.doubly_linked_list import Playlist
from data_structures.bst import SongCatalogue
from data_structures.heap import AutoplayQueue


class TestDataLoader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp()
        cls.csv_path = os.path.join(cls.tmpdir, "test_songs.csv")
        generate_csv(cls.csv_path, count=20, seed=7)

    def test_load_songs_from_csv(self):
        print("\n>>> load_songs_from_csv: 从 CSV 加载 Song 列表")
        songs = load_songs_from_csv(self.csv_path)
        print(f"    加载 {len(songs)} 首 (期望 20)")
        print(f"    前3首:")
        for s in songs[:3]:
            print(f"      {s.song_id}: {s.title} / {s.artist} / {s.genre.name}")
        self.assertEqual(len(songs), 20)
        for s in songs:
            self.assertIsInstance(s, Song)

    def test_load_into_all_structures(self):
        print("\n>>> load_into_all_structures: 同时载入三种数据结构")
        pl, cat, ap, songs = load_into_all_structures(self.csv_path)
        print(f"    Playlist  len = {len(pl)}")
        print(f"    Catalogue len = {len(cat)}")
        print(f"    Autoplay  len = {len(ap)}")
        print(f"    Songs     len = {len(songs)}")
        self.assertEqual(len(pl), 20)
        self.assertEqual(len(cat), 20)
        self.assertEqual(len(ap), 20)

    def test_load_catalogue_only(self):
        print("\n>>> load_catalogue_only: 仅载入 BST 曲库")
        cat, songs = load_catalogue_only(self.csv_path)
        print(f"    类型: {type(cat).__name__}")
        print(f"    曲库大小: {len(cat)}")
        self.assertIsInstance(cat, SongCatalogue)
        self.assertEqual(len(cat), 20)

    def test_load_playlist_only(self):
        print("\n>>> load_playlist_only: 仅载入播放列表")
        pl, songs = load_playlist_only(self.csv_path)
        print(f"    类型: {type(pl).__name__}")
        print(f"    列表大小: {len(pl)}")
        self.assertIsInstance(pl, Playlist)
        self.assertEqual(len(pl), 20)

    def test_load_autoplay_only(self):
        print("\n>>> load_autoplay_only: 仅载入自动播放队列")
        ap, songs = load_autoplay_only(self.csv_path)
        print(f"    类型: {type(ap).__name__}")
        print(f"    队列大小: {len(ap)}")
        top = ap.peek()
        if top:
            print(f"    队首: {top.song_id} - {top.title}")
        self.assertIsInstance(ap, AutoplayQueue)
        self.assertEqual(len(ap), 20)

    def test_ensure_dataset_creates_file(self):
        print("\n>>> ensure_dataset: 文件不存在时自动生成")
        path = os.path.join(self.tmpdir, "auto_gen.csv")
        print(f"    生成前文件存在? {os.path.exists(path)}")
        result = ensure_dataset(path, count=5, seed=1)
        print(f"    生成后文件存在? {os.path.exists(path)}")
        print(f"    返回路径: {result}")
        self.assertEqual(result, path)
        self.assertTrue(os.path.exists(path))

    def test_ensure_dataset_skips_existing(self):
        print("\n>>> ensure_dataset: 文件已存在时跳过重新生成")
        path = os.path.join(self.tmpdir, "existing.csv")
        generate_csv(path, count=10, seed=5)
        print(f"    已有文件: 10 首")
        result = ensure_dataset(path, count=99, seed=99)
        songs = load_songs_from_csv(result)
        print(f"    ensure_dataset(count=99) 后实际歌曲数: {len(songs)} (期望仍为 10)")
        self.assertEqual(len(songs), 10)


if __name__ == "__main__":
    unittest.main()
