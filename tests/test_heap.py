

import unittest
from data_structures.song import Song, Genre
from data_structures.heap import AutoplayQueue


def make_song(sid, likes=0, plays=0, last_played=0.0, genre=Genre.ROCK, title=None):
    return Song(sid, title or f"Title{sid}", "Artist", "Album", genre,
                200, plays, likes, last_played=last_played)


class TestHeap(unittest.TestCase):
    def setUp(self):
        self.q = AutoplayQueue(max_likes=100, max_plays=100, now=1000.0)
        print(f"\n    AutoplayQueue(max_likes=100, max_plays=100, now=1000.0)")

    def test_add_and_len(self):
        print("\n>>> add_to_autoplay / __len__: 添加歌曲到自动播放队列")
        self.q.add_to_autoplay(make_song("1", likes=50))
        print(f"    添加 s1(likes=50) 后 len = {len(self.q)}")
        dup = self.q.add_to_autoplay(make_song("1"))
        print(f"    重复添加 s1 -> 返回 {dup} (应返回 False)")
        print(f"    重复后 len = {len(self.q)}")
        self.assertEqual(len(self.q), 1)
        self.assertFalse(dup)

    def test_next_returns_highest(self):
        print("\n>>> next_autoplay: 按分数从高到低弹出")
        s_low = make_song("1", likes=10, plays=10)
        s_high = make_song("2", likes=90, plays=90, last_played=900.0)
        self.q.add_to_autoplay(s_low)
        self.q.add_to_autoplay(s_high)
        print(f"    队列: s1(score={self.q.score(s_low):.3f}), s2(score={self.q.score(s_high):.3f})")
        top = self.q.next_autoplay()
        print(f"    第1次弹出 -> {top.song_id} (期望 s2, 分数最高)")
        second = self.q.next_autoplay()
        print(f"    第2次弹出 -> {second.song_id} (期望 s1)")
        self.assertEqual(top.song_id, "2")
        self.assertEqual(second.song_id, "1")

    def test_lazy_removal(self):
        print("\n>>> remove_from_autoplay: 惰性删除 (标记后跳过)")
        s1 = make_song("1", likes=50)
        s2 = make_song("2", likes=30)
        self.q.add_to_autoplay(s1)
        self.q.add_to_autoplay(s2)
        print(f"    添加 s1(likes=50), s2(likes=30), len = {len(self.q)}")
        self.q.remove_from_autoplay("1")
        print(f"    remove_from_autoplay('1') 后 len = {len(self.q)}")
        top = self.q.next_autoplay()
        print(f"    next_autoplay -> {top.song_id} (期望 s2, s1 已删除)")
        print(f"    再次 next_autoplay -> {self.q.next_autoplay()} (期望 None)")
        self.assertEqual(top.song_id, "2")
        self.assertIsNone(self.q.next_autoplay())

    def test_remove_not_present(self):
        print("\n>>> remove_from_autoplay: 删除不存在的歌曲")
        result = self.q.remove_from_autoplay("999")
        print(f"    remove_from_autoplay('999') -> {result} (期望 False)")
        self.assertFalse(result)

    def test_peek(self):
        print("\n>>> peek: 查看队首但不弹出")
        s1 = make_song("1", likes=50)
        s2 = make_song("2", likes=90)
        self.q.add_to_autoplay(s1)
        self.q.add_to_autoplay(s2)
        print(f"    peek -> {self.q.peek().song_id} (期望 s2)")
        print(f"    peek 后 len = {len(self.q)} (期望仍为 2)")
        self.assertEqual(self.q.peek().song_id, "2")
        self.assertEqual(len(self.q), 2)

    def test_update_score(self):
        print("\n>>> update_score: 更新歌曲分数")
        s = make_song("1", likes=10, plays=10)
        self.q.add_to_autoplay(s)
        print(f"    初始 score = {self.q.score(s):.3f} (likes=10, plays=10)")
        s.like_count = 95
        s.play_count = 95
        self.q.update_score(s)
        print(f"    更新后 score = {self.q.score(s):.3f} (likes=95, plays=95)")
        print(f"    peek -> {self.q.peek().song_id} (期望 s1)")
        self.assertEqual(self.q.peek().song_id, "1")

    def test_genre_bonus(self):
        print("\n>>> genre_bonus: 偏好流派加分")
        q = AutoplayQueue(max_likes=100, max_plays=100, now=1000.0, favourite_genre=Genre.JAZZ)
        s_rock = make_song("1", likes=50, plays=50, last_played=500.0, genre=Genre.ROCK)
        s_jazz = make_song("2", likes=50, plays=50, last_played=500.0, genre=Genre.JAZZ)
        q.add_to_autoplay(s_rock)
        q.add_to_autoplay(s_jazz)
        print(f"    ROCK score = {q.score(s_rock):.3f}")
        print(f"    JAZZ score = {q.score(s_jazz):.3f} (偏好流派 +0.15)")
        top = q.next_autoplay()
        print(f"    next_autoplay -> {top.song_id} (期望 s2/JAZZ)")
        self.assertEqual(top.song_id, "2")

    def test_score_formula(self):
        print("\n>>> score: 评分公式验证")
        s = make_song("1", likes=50, plays=50, last_played=500.0, genre=Genre.ROCK)
        score = self.q.score(s)
        like_part = 0.5 * 0.40
        play_part = 0.5 * 0.15
        recency_part = 0.5 * 0.30
        genre_part = 0.0
        print(f"    likes=50/100 -> {like_part:.3f}")
        print(f"    plays=50/100 -> {play_part:.3f}")
        print(f"    recency=500/1000 -> {recency_part:.3f}")
        print(f"    genre_bonus -> {genre_part:.3f}")
        print(f"    总分 = {score:.3f} (期望 0.425)")
        self.assertAlmostEqual(score, 0.425, places=3)

    def test_to_sorted_list(self):
        print("\n>>> to_sorted_list: 按分数降序排列")
        songs = [make_song(str(i), likes=i * 10) for i in range(1, 6)]
        for s in songs:
            self.q.add_to_autoplay(s)
        sorted_songs = self.q.to_sorted_list()
        print(f"    队列内容 (按分数降序):")
        for s in sorted_songs:
            print(f"      {s.song_id} (likes={s.like_count}, score={self.q.score(s):.3f})")
        self.assertEqual(sorted_songs[0].song_id, "5")

    def test_to_heap_array(self):
        print("\n>>> to_heap_array: 导出堆数组 (含分数)")
        self.q.add_to_autoplay(make_song("1", likes=50))
        arr = self.q.to_heap_array()
        print(f"    堆数组: {arr}")
        self.assertEqual(arr[0]["song_id"], "1")
        self.assertIn("score", arr[0])

    def test_clear(self):
        print("\n>>> clear: 清空队列")
        self.q.add_to_autoplay(make_song("1"))
        self.q.add_to_autoplay(make_song("2"))
        print(f"    清空前 len = {len(self.q)}")
        self.q.clear()
        print(f"    清空后 len = {len(self.q)}")
        print(f"    next_autoplay -> {self.q.next_autoplay()}")
        self.assertEqual(len(self.q), 0)

    def test_contains(self):
        print("\n>>> __contains__: 检查歌曲是否在队列中")
        self.q.add_to_autoplay(make_song("1"))
        print(f"    '1' in queue -> {'1' in self.q}")
        print(f"    '2' in queue -> {'2' in self.q}")
        self.assertIn("1", self.q)
        self.assertNotIn("2", self.q)

    def test_empty_queue(self):
        print("\n>>> 空队列行为")
        print(f"    next_autoplay -> {self.q.next_autoplay()}")
        print(f"    peek -> {self.q.peek()}")
        self.assertIsNone(self.q.next_autoplay())
        self.assertIsNone(self.q.peek())


if __name__ == "__main__":
    unittest.main()
