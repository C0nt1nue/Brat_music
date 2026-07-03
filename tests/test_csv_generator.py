

import unittest
import os
import csv
import tempfile
from data.csv_generator import generate_csv, generate_songs
from data_structures.song import Genre


class TestCSVGenerator(unittest.TestCase):
    def test_generate_songs_count(self):
        print("\n>>> generate_songs: 生成指定数量的 Song 对象")
        songs = generate_songs(count=10, seed=1)
        print(f"    生成 {len(songs)} 首 (期望 10)")
        self.assertEqual(len(songs), 10)

    def test_generate_songs_unique_ids(self):
        print("\n>>> generate_songs: song_id 唯一性")
        songs = generate_songs(count=20, seed=1)
        ids = [s.song_id for s in songs]
        unique = len(set(ids))
        print(f"    总数={len(ids)}, 去重后={unique}")
        print(f"    前5个ID: {ids[:5]}")
        self.assertEqual(len(ids), unique)

    def test_generate_songs_valid_genre(self):
        print("\n>>> generate_songs: 流派字段有效性")
        songs = generate_songs(count=5, seed=1)
        for s in songs:
            print(f"    {s.song_id}: genre={s.genre.name} (is Genre? {isinstance(s.genre, Genre)})")
            self.assertIsInstance(s.genre, Genre)

    def test_generate_csv_file(self):
        print("\n>>> generate_csv: 生成 CSV 文件并验证内容")
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as tmp:
            path = tmp.name
        try:
            result = generate_csv(path, count=15, seed=42)
            print(f"    返回路径: {result}")
            print(f"    文件存在? {os.path.exists(path)}")
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            print(f"    数据行数: {len(rows)} (期望 15)")
            print(f"    列名: {list(rows[0].keys())}")
            print(f"    前3行:")
            for row in rows[:3]:
                print(f"      {row['song_id']}: {row['title']} / {row['artist']} / {row['genre']}")
            self.assertEqual(len(rows), 15)
            self.assertIn("song_id", rows[0])
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_generate_csv_reproducible(self):
        print("\n>>> generate_csv: 相同 seed 生成相同文件 (可复现性)")
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as tmp:
            path1 = tmp.name
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as tmp:
            path2 = tmp.name
        try:
            generate_csv(path1, count=10, seed=99)
            generate_csv(path2, count=10, seed=99)
            with open(path1, encoding="utf-8") as f1, open(path2, encoding="utf-8") as f2:
                c1 = f1.read()
                c2 = f2.read()
            same = c1 == c2
            print(f"    两个文件内容相同? {same}")
            print(f"    文件大小: {len(c1)} vs {len(c2)} 字符")
            self.assertEqual(c1, c2)
        finally:
            for p in [path1, path2]:
                if os.path.exists(p):
                    os.unlink(p)


if __name__ == "__main__":
    unittest.main()
