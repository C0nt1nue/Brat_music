

import unittest
from data_structures.song import Song, Genre


class TestGenre(unittest.TestCase):
    def test_from_string(self):
        print("\n>>> Genre.from_string: 字符串到枚举的解析")
        for raw in ["rock", "HIP_HOP", "  Jazz "]:
            g = Genre.from_string(raw)
            print(f"    from_string({raw!r}) = {g}")
        self.assertEqual(Genre.from_string("rock"), Genre.ROCK)
        self.assertEqual(Genre.from_string("HIP_HOP"), Genre.HIP_HOP)
        self.assertEqual(Genre.from_string("  Jazz "), Genre.JAZZ)

    def test_from_string_invalid(self):
        print("\n>>> Genre.from_string: 非法流派应抛出 ValueError")
        try:
            Genre.from_string("POLKA")
        except ValueError as e:
            print(f"    from_string('POLKA') -> ValueError: {e}")
        with self.assertRaises(ValueError):
            Genre.from_string("POLKA")

    def test_from_string_passthrough(self):
        print("\n>>> Genre.from_string: 传入 Genre 枚举应原样返回")
        result = Genre.from_string(Genre.POP)
        print(f"    from_string(Genre.POP) = {result}")
        self.assertEqual(result, Genre.POP)


class TestSong(unittest.TestCase):
    def setUp(self):
        self.s1 = Song("s1", "Hello", "Adele", "25", Genre.POP, 300, 5, 10)
        self.s2 = Song("s2", "World", "B", "Z", Genre.ROCK, 200, 3, 8)
        self.s3 = Song("s3", "hello", "C", "Y", Genre.JAZZ, 250, 1, 0)
        print(f"\n    s1 = {self.s1!r}")
        print(f"    s2 = {self.s2!r}")
        print(f"    s3 = {self.s3!r}")

    def test_eq_by_id(self):
        print("\n>>> Song.__eq__: 按 song_id 判等")
        clone = Song("s1", "Different", "X", "Y", Genre.ROCK)
        print(f"    s1 == Song('s1', 'Different', ...) -> {self.s1 == clone}")
        print(f"    s1 == s2 -> {self.s1 == self.s2}")
        self.assertEqual(self.s1, clone)
        self.assertNotEqual(self.s1, self.s2)

    def test_lt_by_title(self):
        print("\n>>> Song.__lt__: 按标题排序 (大小写不敏感)")
        print(f"    s1('Hello') < s2('World') -> {self.s1 < self.s2}")
        print(f"    s2('World') < s1('Hello') -> {self.s2 < self.s1}")
        self.assertTrue(self.s1 < self.s2)
        self.assertFalse(self.s2 < self.s1)

    def test_lt_case_insensitive(self):
        print("\n>>> Song.__lt__: 'Hello' 与 'hello' 应相等")
        print(f"    s1('Hello') < s3('hello') -> {self.s1 < self.s3}")
        print(f"    s1('Hello') <= s3('hello') -> {self.s1 <= self.s3}")
        self.assertFalse(self.s1 < self.s3)
        self.assertTrue(self.s1 <= self.s3)

    def test_hash(self):
        print("\n>>> Song.__hash__: 相同 id 的 Song 哈希值相同")
        clone = Song("s1", "x", "y", "z", Genre.ROCK)
        print(f"    hash(s1) = {hash(self.s1)}")
        print(f"    hash(clone) = {hash(clone)}")
        print(f"    相同? {hash(self.s1) == hash(clone)}")
        self.assertEqual(hash(self.s1), hash(clone))

    def test_to_dict(self):
        print("\n>>> Song.to_dict: 序列化为字典")
        d = self.s1.to_dict()
        for k, v in d.items():
            print(f"    {k}: {v}")
        self.assertEqual(d["song_id"], "s1")
        self.assertEqual(d["genre"], "POP")
        self.assertEqual(d["duration_seconds"], 300)

    def test_from_dict(self):
        print("\n>>> Song.from_dict: 从字典重建 Song")
        d = {"song_id": "x1", "title": "T", "artist": "A", "album": "Al",
             "genre": "ROCK", "duration_seconds": 100, "play_count": 2,
             "like_count": 3, "liked": True, "last_played": 5.0}
        song = Song.from_dict(d)
        print(f"    输入字典: {d}")
        print(f"    重建结果: {song!r}")
        print(f"    genre={song.genre}, liked={song.liked}, last_played={song.last_played}")
        self.assertEqual(song.song_id, "x1")
        self.assertEqual(song.genre, Genre.ROCK)
        self.assertTrue(song.liked)

    def test_genre_string_in_constructor(self):
        print("\n>>> Song 构造器: 传入字符串 'JAZZ' 自动转换为 Genre.JAZZ")
        song = Song("s", "T", "A", "Al", "JAZZ")
        print(f"    song.genre = {song.genre} (type={type(song.genre).__name__})")
        self.assertEqual(song.genre, Genre.JAZZ)


if __name__ == "__main__":
    unittest.main()
