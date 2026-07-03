

import unittest
from data_structures.song import Song, Genre
from data_structures.bst import SongCatalogue


def make_song(sid, title, artist="Artist", genre=Genre.ROCK):
    return Song(sid, title, artist, "Album", genre, 200, 0, 0)


class TestBST(unittest.TestCase):
    def setUp(self):
        self.cat = SongCatalogue()
        self.s1 = make_song("1", "Alpha", "Adele")
        self.s2 = make_song("2", "Bravo", "Beatles")
        self.s3 = make_song("3", "Charlie", "Adele")
        self.s4 = make_song("4", "Delta", "Drake")
        self.s5 = make_song("5", "Echo", "Adele", Genre.JAZZ)
        for s in [self.s1, self.s2, self.s3, self.s4, self.s5]:
            self.cat.insert(s)
        print(f"\n    曲库已插入: {[s.title for s in self.cat.in_order_traversal()]}")
        print(f"    树高 = {self.cat.height()}")

    def test_insert_and_len(self):
        print("\n>>> insert / __len__: 插入歌曲并检查数量")
        print(f"    当前歌曲数 = {len(self.cat)}")
        dup = self.cat.insert(self.s1)
        print(f"    重复插入 s1 -> 返回 {dup} (应返回 False)")
        print(f"    重复后歌曲数 = {len(self.cat)}")
        self.assertEqual(len(self.cat), 5)
        self.assertFalse(dup)

    def test_search_exact(self):
        print("\n>>> search: 精确搜索标题")
        result = self.cat.search("Bravo")
        print(f"    search('Bravo') -> {result!r}")
        self.assertIsNotNone(result)
        self.assertEqual(result.song_id, "2")

    def test_search_case_insensitive(self):
        print("\n>>> search: 大小写不敏感搜索")
        result = self.cat.search("bravo")
        print(f"    search('bravo') -> {result!r}")
        self.assertEqual(result.song_id, "2")

    def test_search_not_found(self):
        print("\n>>> search: 搜索不存在的标题")
        result = self.cat.search("Zulu")
        print(f"    search('Zulu') -> {result}")
        self.assertIsNone(result)

    def test_find_by_artist(self):
        print("\n>>> find_by_artist: 按艺人搜索")
        results = self.cat.find_by_artist("Adele")
        print(f"    find_by_artist('Adele') -> {len(results)} 首:")
        for s in results:
            print(f"      {s.title} (id={s.song_id})")
        self.assertEqual(len(results), 3)

    def test_find_by_artist_substring(self):
        print("\n>>> find_by_artist: 子串匹配")
        results = self.cat.find_by_artist("dra")
        print(f"    find_by_artist('dra') -> {len(results)} 首:")
        for s in results:
            print(f"      {s.title} (id={s.song_id})")
        self.assertEqual(len(results), 1)

    def test_find_by_genre(self):
        print("\n>>> find_by_genre: 按流派搜索")
        results = self.cat.find_by_genre(Genre.JAZZ)
        print(f"    find_by_genre(JAZZ) -> {len(results)} 首:")
        for s in results:
            print(f"      {s.title} (genre={s.genre})")
        results_str = self.cat.find_by_genre("rock")
        print(f"    find_by_genre('rock') -> {len(results_str)} 首")
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results_str), 4)

    def test_in_order_traversal_sorted(self):
        print("\n>>> in_order_traversal: 中序遍历 (应按标题排序)")
        songs = self.cat.in_order_traversal()
        titles = [s.title for s in songs]
        print(f"    遍历结果: {titles}")
        self.assertEqual(titles, sorted(titles, key=str.lower))

    def test_range_search(self):
        print("\n>>> range_search: 标题范围查询 [B, D]")
        results = self.cat.range_search("B", "D")
        titles = sorted(s.title for s in results)
        print(f"    range_search('B','D') -> {titles}")
        self.assertEqual(titles, ["Bravo", "Charlie"])

    def test_range_search_full(self):
        print("\n>>> range_search: 全范围查询 [A, Z]")
        results = self.cat.range_search("A", "Z")
        print(f"    结果数 = {len(results)} (期望 5)")
        self.assertEqual(len(results), 5)

    def test_range_search_empty(self):
        print("\n>>> range_search: 空范围查询 [X, Z]")
        results = self.cat.range_search("X", "Z")
        print(f"    结果数 = {len(results)} (期望 0)")
        self.assertEqual(len(results), 0)

    def test_height(self):
        print("\n>>> height: 计算树高")
        h = self.cat.height()
        print(f"    树高 = {h}")
        self.assertGreaterEqual(h, 1)

    def test_find_by_id(self):
        print("\n>>> find_by_id: 按 ID 查找")
        s = self.cat.find_by_id("3")
        print(f"    find_by_id('3') -> {s!r}")
        print(f"    find_by_id('999') -> {self.cat.find_by_id('999')}")
        self.assertIsNotNone(s)
        self.assertEqual(s.title, "Charlie")

    def test_remove(self):
        print("\n>>> remove: 删除歌曲")
        print(f"    删除前: {[s.title for s in self.cat.in_order_traversal()]}")
        ok = self.cat.remove("3")
        print(f"    remove('3') -> {ok}")
        print(f"    删除后: {[s.title for s in self.cat.in_order_traversal()]}")
        print(f"    search('Charlie') -> {self.cat.search('Charlie')}")
        self.assertTrue(ok)
        self.assertIsNone(self.cat.search("Charlie"))

    def test_remove_root(self):
        print("\n>>> remove: 删除根节点")
        cat = SongCatalogue()
        cat.insert(make_song("1", "Bravo"))
        cat.insert(make_song("2", "Alpha"))
        cat.insert(make_song("3", "Charlie"))
        print(f"    删除前中序: {[s.title for s in cat.in_order_traversal()]}")
        cat.remove("1")
        print(f"    删除根('Bravo')后中序: {[s.title for s in cat.in_order_traversal()]}")
        print(f"    search('Alpha') -> {cat.search('Alpha')!r}")
        print(f"    search('Charlie') -> {cat.search('Charlie')!r}")
        self.assertEqual(len(cat), 2)
        self.assertIsNotNone(cat.search("Alpha"))

    def test_empty_catalogue(self):
        print("\n>>> 空曲库行为")
        cat = SongCatalogue()
        print(f"    search('x') -> {cat.search('x')}")
        print(f"    in_order = {cat.in_order_traversal()}")
        print(f"    height = {cat.height()}")
        self.assertIsNone(cat.search("x"))
        self.assertEqual(cat.height(), 0)

    def test_large_iterative(self):
        print("\n>>> 大规模插入: 500 首歌曲 (验证迭代遍历不溢出)")
        cat = SongCatalogue()
        for i in range(500):
            cat.insert(make_song(f"s{i}", f"Title{i:04d}"))
        songs = cat.in_order_traversal()
        print(f"    插入 500 首, 树高 = {cat.height()}, 遍历结果数 = {len(songs)}")
        self.assertEqual(len(songs), 500)


if __name__ == "__main__":
    unittest.main()
