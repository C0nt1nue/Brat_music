

import unittest
import random
from data_structures.song import Song, Genre
from data_structures.doubly_linked_list import Playlist


def make_song(sid, title=None):
    return Song(sid, title or f"Title{sid}", f"Artist{sid}", "Album", Genre.ROCK, 200, 0, 0)


class TestPlaylist(unittest.TestCase):
    def setUp(self):
        self.pl = Playlist()
        self.s1 = make_song("1", "Alpha")
        self.s2 = make_song("2", "Bravo")
        self.s3 = make_song("3", "Charlie")
        for s in [self.s1, self.s2, self.s3]:
            self.pl.add_song(s)
        print(f"\n    播放列表初始状态: {[s.title for s in self.pl]}")
        print(f"    当前歌曲: {self.pl.current_song().title}")

    def test_add_and_len(self):
        print("\n>>> add_song / __len__: 添加歌曲并检查长度")
        print(f"    当前长度 = {len(self.pl)}")
        dup = self.pl.add_song(self.s1)
        print(f"    重复添加 s1 -> 返回 {dup} (应返回 False)")
        print(f"    重复添加后长度 = {len(self.pl)} (应仍为 3)")
        self.assertEqual(len(self.pl), 3)
        self.assertFalse(dup)

    def test_iteration(self):
        print("\n>>> __iter__: 遍历播放列表")
        titles = [s.title for s in self.pl]
        print(f"    顺序遍历: {titles}")
        self.assertEqual(titles, ["Alpha", "Bravo", "Charlie"])

    def test_contains(self):
        print("\n>>> __contains__: 检查歌曲是否存在")
        print(f"    '1' in playlist -> {'1' in self.pl}")
        print(f"    '99' in playlist -> {'99' in self.pl}")
        self.assertIn("1", self.pl)
        self.assertNotIn("99", self.pl)

    def test_current_song(self):
        print("\n>>> current_song: 获取当前播放歌曲")
        cur = self.pl.current_song()
        print(f"    当前歌曲: id={cur.song_id}, title={cur.title}")
        self.assertEqual(cur.song_id, "1")

    def test_play_next(self):
        print("\n>>> play_next: 向后播放")
        s = self.pl.play_next()
        print(f"    第1次 next -> {s.title} (期望 Bravo)")
        s = self.pl.play_next()
        print(f"    第2次 next -> {s.title} (期望 Charlie)")
        s = self.pl.play_next()
        print(f"    第3次 next (已在尾部) -> {s.title} (期望仍为 Charlie)")
        self.assertEqual(self.pl.current_song().song_id, "3")

    def test_play_previous(self):
        print("\n>>> play_previous: 向前播放")
        self.pl.move_to_position(2)
        print(f"    先移动到位置 2: {self.pl.current_song().title}")
        s = self.pl.play_previous()
        print(f"    第1次 prev -> {s.title} (期望 Bravo)")
        s = self.pl.play_previous()
        print(f"    第2次 prev -> {s.title} (期望 Alpha)")
        s = self.pl.play_previous()
        print(f"    第3次 prev (已在头部) -> {s.title} (期望仍为 Alpha)")
        self.assertEqual(s.song_id, "1")

    def test_move_to_position(self):
        print("\n>>> move_to_position: 跳转到指定位置")
        s = self.pl.move_to_position(2)
        print(f"    move_to_position(2) -> {s.title} (期望 Charlie)")
        r1 = self.pl.move_to_position(99)
        print(f"    move_to_position(99) -> {r1} (期望 None, 越界)")
        r2 = self.pl.move_to_position(-1)
        print(f"    move_to_position(-1) -> {r2} (期望 None, 负数)")
        self.assertEqual(s.song_id, "3")
        self.assertIsNone(r1)
        self.assertIsNone(r2)

    def test_current_index(self):
        print("\n>>> current_index: 获取当前歌曲的索引")
        print(f"    初始 index = {self.pl.current_index()}")
        self.pl.play_next()
        print(f"    play_next 后 index = {self.pl.current_index()}")
        self.assertEqual(self.pl.current_index(), 1)

    def test_remove_song(self):
        print("\n>>> remove_song: 删除中间歌曲")
        print(f"    删除前: {[s.title for s in self.pl]}")
        ok = self.pl.remove_song("2")
        print(f"    remove_song('2') -> {ok}")
        print(f"    删除后: {[s.title for s in self.pl]}")
        print(f"    remove_song('99') -> {self.pl.remove_song('99')} (不存在)")
        self.assertTrue(ok)
        self.assertEqual(len(self.pl), 2)
        self.assertFalse(self.pl.remove_song("99"))

    def test_remove_head(self):
        print("\n>>> remove_song: 删除头部歌曲")
        print(f"    删除前 head = {self.pl.head.song.title}")
        self.pl.remove_song("1")
        print(f"    删除后 head = {self.pl.head.song.title} (期望 Bravo)")
        print(f"    当前歌曲 = {self.pl.current_song().title}")
        self.assertEqual(self.pl.head.song.song_id, "2")

    def test_remove_tail(self):
        print("\n>>> remove_song: 删除尾部歌曲")
        print(f"    删除前 tail = {self.pl.tail.song.title}")
        self.pl.remove_song("3")
        print(f"    删除后 tail = {self.pl.tail.song.title} (期望 Bravo)")
        self.assertEqual(self.pl.tail.song.song_id, "2")

    def test_remove_current_reassigns(self):
        print("\n>>> remove_song: 删除当前歌曲后自动重定位")
        self.pl.move_to_position(1)
        print(f"    当前歌曲: {self.pl.current_song().title}")
        self.pl.remove_song("2")
        print(f"    删除后当前歌曲: {self.pl.current_song().title} (期望 Charlie)")
        self.assertEqual(self.pl.current_song().song_id, "3")

    def test_get_song(self):
        print("\n>>> get_song: O(1) 查找歌曲")
        s = self.pl.get_song("2")
        print(f"    get_song('2') -> {s.title}")
        print(f"    get_song('99') -> {self.pl.get_song('99')}")
        self.assertEqual(s.song_id, "2")
        self.assertIsNone(self.pl.get_song("99"))

    def test_shuffle_preserves_songs(self):
        print("\n>>> shuffle: Fisher-Yates 洗牌 (保持歌曲集合不变)")
        print(f"    洗牌前: {[s.song_id for s in self.pl]}")
        rng = random.Random(42)
        self.pl.shuffle(rng)
        ids = [s.song_id for s in self.pl]
        print(f"    洗牌后: {ids}")
        print(f"    集合不变? {set(ids) == {'1', '2', '3'}}")
        self.assertEqual(set(ids), {"1", "2", "3"})

    def test_shuffle_current_preserved(self):
        print("\n>>> shuffle: 洗牌后 current 指针保持不变")
        self.pl.move_to_position(1)
        cur_id = self.pl.current_song().song_id
        print(f"    洗牌前 current = {cur_id}")
        rng = random.Random(42)
        self.pl.shuffle(rng)
        print(f"    洗牌后 current = {self.pl.current_song().song_id}")
        self.assertEqual(self.pl.current_song().song_id, cur_id)

    def test_display(self):
        print("\n>>> display: 获取播放列表的展示数据")
        d = self.pl.display()
        for item in d:
            tag = " <-- current" if item["is_current"] else ""
            print(f"    [{item['index']}] {item['title']}{tag}")
        self.assertTrue(d[0]["is_current"])
        self.assertFalse(d[1]["is_current"])

    def test_clear(self):
        print("\n>>> clear: 清空播放列表")
        print(f"    清空前 len = {len(self.pl)}, head = {self.pl.head.song.title}")
        self.pl.clear()
        print(f"    清空后 len = {len(self.pl)}, head = {self.pl.head}")
        self.assertEqual(len(self.pl), 0)
        self.assertIsNone(self.pl.head)

    def test_insert_at(self):
        print("\n>>> insert_at: 在指定位置插入歌曲")
        s = make_song("4", "Delta")
        print(f"    插入前: {[s.title for s in self.pl]}")
        self.pl.insert_at(s, 1)
        print(f"    insert_at(Delta, 1) 后: {[s.title for s in self.pl]}")
        self.assertEqual([s.title for s in self.pl], ["Alpha", "Delta", "Bravo", "Charlie"])

    def test_empty_playlist(self):
        print("\n>>> 空播放列表行为")
        pl = Playlist()
        print(f"    len = {len(pl)}, current = {pl.current_song()}, next = {pl.play_next()}")
        self.assertIsNone(pl.current_song())
        self.assertIsNone(pl.play_next())
        self.assertEqual(len(pl), 0)

    def test_single_song(self):
        print("\n>>> 单歌曲播放列表")
        pl = Playlist()
        s = make_song("x")
        pl.add_song(s)
        print(f"    play_next -> {pl.play_next().song_id}")
        print(f"    play_previous -> {pl.play_previous().song_id}")
        self.assertEqual(pl.play_next().song_id, "x")

    def test_recent_songs(self):
        print("\n>>> recent_songs: 按播放时间获取最近歌曲")
        pl = Playlist()
        s1 = make_song("1"); s1.last_played = 100
        s2 = make_song("2"); s2.last_played = 200
        s3 = make_song("3"); s3.last_played = 0
        pl.add_song(s1); pl.add_song(s2); pl.add_song(s3)
        recent = pl.recent_songs(2)
        print(f"    最近2首: {[(s.song_id, s.last_played) for s in recent]}")
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0].song_id, "2")


if __name__ == "__main__":
    unittest.main()
