"""
tests/D_ceshi_dui.py
=================
Task 4 单元测试：验证 AutoplayHeap 和自定义堆的正确性

测试覆盖:
  - MaxHeap 的基本操作（push、pop、peek、size）
  - 最大堆性质的自动维护
  - AutoplayHeap 的四个核心接口
  - remove_from_autoplay 删除指定歌曲
  - update_score 更新评分并恢复堆性质
  - 空堆的边界情况
  - 与 data_loader 的集成（compute_autoplay_score）

运行方式:
    cd D:/brat
    python -m pytest tests/D_ceshi_dui.py -v
    或
    python -m unittest tests.test_heap -v

（作者：成员 D）
"""

import sys
import unittest
from pathlib import Path

# 将项目根目录加入 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.liupai import Genre
from models.A_gequ import Song
from structures.D_dui import HeapNode, MaxHeap, AutoplayHeap


class TestMaxHeap(unittest.TestCase):
    """
    测试自定义最大堆 MaxHeap 的基本操作
    """

    def setUp(self):
        """每个测试前创建一个新堆和几个测试节点"""
        self.heap = MaxHeap()
        self.s1 = Song("S1", "A", "A1", "A", Genre.POP, 100, 1000, 500)
        self.s2 = Song("S2", "B", "A2", "B", Genre.ROCK, 200, 2000, 800)
        self.s3 = Song("S3", "C", "A3", "C", Genre.JAZZ, 150, 500, 100)

    def test_push_and_size(self):
        """测试 push 后 size 正确"""
        self.assertEqual(self.heap.size(), 0)
        self.heap.push(HeapNode(self.s1, 100.0))
        self.assertEqual(self.heap.size(), 1)
        self.heap.push(HeapNode(self.s2, 200.0))
        self.assertEqual(self.heap.size(), 2)

    def test_is_empty(self):
        """测试空堆判断"""
        self.assertTrue(self.heap.is_empty())
        self.heap.push(HeapNode(self.s1, 100.0))
        self.assertFalse(self.heap.is_empty())

    def test_peek(self):
        """测试 peek 查看堆顶但不移除"""
        self.assertIsNone(self.heap.peek())  # 空堆 peek 返回 None
        self.heap.push(HeapNode(self.s1, 50.0))
        self.heap.push(HeapNode(self.s2, 200.0))
        top = self.heap.peek()
        self.assertEqual(top.song.song_id, "S2")  # score 200 > 50
        self.assertEqual(self.heap.size(), 2)     # peek 不移除

    def test_pop_returns_highest_score(self):
        """测试 pop 返回评分最高的节点，且顺序正确"""
        self.heap.push(HeapNode(self.s1, 100.0))
        self.heap.push(HeapNode(self.s2, 300.0))
        self.heap.push(HeapNode(self.s3, 200.0))

        # 第一次 pop：score=300 (S2)
        top1 = self.heap.pop()
        self.assertEqual(top1.song.song_id, "S2")
        self.assertEqual(top1.score, 300.0)

        # 第二次 pop：score=200 (S3)
        top2 = self.heap.pop()
        self.assertEqual(top2.song.song_id, "S3")

        # 第三次 pop：score=100 (S1)
        top3 = self.heap.pop()
        self.assertEqual(top3.song.song_id, "S1")

    def test_pop_empty_heap(self):
        """测试空堆 pop 返回 None"""
        self.assertIsNone(self.heap.pop())

    def test_max_heap_property_after_multiple_pushes(self):
        """测试多次 push 后堆性质仍然保持"""
        scores = [30, 50, 10, 70, 20, 60, 40]
        for i, score in enumerate(scores):
            s = Song(f"S{i}", "T", "A", "Al", Genre.POP, 100, 0, 0)
            self.heap.push(HeapNode(s, float(score)))

        # 验证堆性质：每个父节点 score >= 子节点 score
        data = self.heap._data
        n = len(data)
        for i in range(n):
            l = 2*i + 1
            r = 2*i + 2
            if l < n:
                self.assertGreaterEqual(data[i].score, data[l].score,
                    f"节点 {i} (score={data[i].score}) < 左孩子 {l} (score={data[l].score})")
            if r < n:
                self.assertGreaterEqual(data[i].score, data[r].score,
                    f"节点 {i} (score={data[i].score}) < 右孩子 {r} (score={data[r].score})")

    def test_get_all(self):
        """测试 get_all 返回所有节点的快照"""
        self.heap.push(HeapNode(self.s1, 100.0))
        self.heap.push(HeapNode(self.s2, 200.0))
        all_nodes = self.heap.get_all()
        self.assertEqual(len(all_nodes), 2)
        # 修改快照不影响原堆
        all_nodes.pop()
        self.assertEqual(self.heap.size(), 2)


class TestAutoplayHeap(unittest.TestCase):
    """
    测试 AutoplayHeap 的四个核心接口
    """

    def setUp(self):
        """每个测试前创建测试用的 AutoplayHeap 和歌曲"""
        self.aheap = AutoplayHeap()

        # 创建测试歌曲，play_count 和 like_count 各不相同
        self.song_hot = Song(
            "S001", "Blinding Lights", "The Weeknd", "After Hours",
            Genre.POP, 200, play_count=1000000, like_count=500000,
        )
        self.song_medium = Song(
            "S002", "Bohemian Rhapsody", "Queen", "A Night at the Opera",
            Genre.ROCK, 355, play_count=500000, like_count=200000,
        )
        self.song_cold = Song(
            "S003", "Take Five", "Dave Brubeck", "Time Out",
            Genre.JAZZ, 324, play_count=50000, like_count=10000,
        )

    def test_add_and_size(self):
        """测试 add_to_autoplay 后 size 正确"""
        self.assertEqual(self.aheap.size(), 0)
        self.aheap.add_to_autoplay(self.song_hot, 95.5)
        self.assertEqual(self.aheap.size(), 1)
        self.aheap.add_to_autoplay(self.song_medium, 80.0)
        self.assertEqual(self.aheap.size(), 2)

    def test_next_autoplay_returns_highest_score(self):
        """测试 next_autoplay 返回评分最高的歌曲"""
        self.aheap.add_to_autoplay(self.song_hot, 95.5)    # 评分最高
        self.aheap.add_to_autoplay(self.song_medium, 80.0)
        self.aheap.add_to_autoplay(self.song_cold, 60.0)

        first = self.aheap.next_autoplay()
        self.assertEqual(first.song_id, "S001")  # S001 评分最高
        self.assertEqual(self.aheap.size(), 2)

        second = self.aheap.next_autoplay()
        self.assertEqual(second.song_id, "S002")

        third = self.aheap.next_autoplay()
        self.assertEqual(third.song_id, "S003")

    def test_next_autoplay_empty(self):
        """测试空队 next_autoplay 返回 None"""
        self.assertIsNone(self.aheap.next_autoplay())

    def test_add_and_peek_next(self):
        """测试 peek_next 查看队首但不移除"""
        self.aheap.add_to_autoplay(self.song_medium, 80.0)
        self.aheap.add_to_autoplay(self.song_hot, 95.5)
        top = self.aheap.peek_next()
        self.assertEqual(top.song_id, "S001")  # S001 评分 95.5 > 80.0
        self.assertEqual(self.aheap.size(), 2)   # peek 不移除

    def test_remove_from_autoplay(self):
        """测试 remove_from_autoplay 删除指定歌曲"""
        self.aheap.add_to_autoplay(self.song_hot, 95.5)
        self.aheap.add_to_autoplay(self.song_medium, 80.0)
        self.aheap.add_to_autoplay(self.song_cold, 60.0)

        # 删除中间的歌曲
        result = self.aheap.remove_from_autoplay("S002")
        self.assertTrue(result)
        self.assertEqual(self.aheap.size(), 2)

        # 验证堆性质仍然保持
        self.assertTrue(self.aheap.verify_heap_property())

        # 尝试删除不存在的歌曲
        result = self.aheap.remove_from_autoplay("NONEXIST")
        self.assertFalse(result)
        self.assertEqual(self.aheap.size(), 2)

    def test_remove_root_song(self):
        """测试删除堆顶元素"""
        self.aheap.add_to_autoplay(self.song_hot, 95.5)
        self.aheap.add_to_autoplay(self.song_medium, 80.0)

        # 删除堆顶（S001）
        result = self.aheap.remove_from_autoplay("S001")
        self.assertTrue(result)
        self.assertTrue(self.aheap.verify_heap_property())

        # 剩下的应该是 S002
        remaining = self.aheap.next_autoplay()
        self.assertEqual(remaining.song_id, "S002")

    def test_update_score_increase(self):
        """测试 update_score 提高评分后重新上浮"""
        self.aheap.add_to_autoplay(self.song_hot, 50.0)   # S001 初始 50
        self.aheap.add_to_autoplay(self.song_medium, 80.0)  # S002 80

        # 将 S001 的评分提高到 90，应该变为堆顶
        result = self.aheap.update_score("S001", 90.0)
        self.assertTrue(result)
        self.assertTrue(self.aheap.verify_heap_property())

        top = self.aheap.next_autoplay()
        self.assertEqual(top.song_id, "S001")  # S001 现在 90 > 80

    def test_update_score_decrease(self):
        """测试 update_score 降低评分后重新下沉"""
        self.aheap.add_to_autoplay(self.song_hot, 90.0)   # S001 90
        self.aheap.add_to_autoplay(self.song_medium, 80.0)  # S002 80

        # 将 S001 的评分降到 30
        result = self.aheap.update_score("S001", 30.0)
        self.assertTrue(result)
        self.assertTrue(self.aheap.verify_heap_property())

        top = self.aheap.next_autoplay()
        self.assertEqual(top.song_id, "S002")  # S002 80 > 30, 所以 S002 先出

    def test_update_score_nonexistent(self):
        """测试更新不存在的歌曲返回 False"""
        result = self.aheap.update_score("NONEXIST", 99.0)
        self.assertFalse(result)

    def test_is_empty(self):
        """测试 is_empty 判断"""
        self.assertTrue(self.aheap.is_empty())
        self.aheap.add_to_autoplay(self.song_hot, 100.0)
        self.assertFalse(self.aheap.is_empty())

    def test_display_all(self):
        """测试 display_all 返回正确的字典列表"""
        self.aheap.add_to_autoplay(self.song_hot, 95.5)
        self.aheap.add_to_autoplay(self.song_medium, 80.0)
        result = self.aheap.display_all()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["song_id"], "S001")
        self.assertEqual(result[0]["title"], "Blinding Lights")
        self.assertEqual(result[1]["score"], 80.0)

    def test_verify_heap_property(self):
        """测试 verify_heap_property 正确检测堆性质"""
        self.assertTrue(self.aheap.verify_heap_property())  # 空堆
        self.aheap.add_to_autoplay(self.song_hot, 90.0)
        self.aheap.add_to_autoplay(self.song_medium, 70.0)
        self.aheap.add_to_autoplay(self.song_cold, 80.0)
        self.assertTrue(self.aheap.verify_heap_property())

    def test_autoplay_with_compute_score(self):
        """测试与 data_loader 的 compute_autoplay_score 集成"""
        from data.A_shuju_jiazai import compute_autoplay_score

        # 计算测试歌曲的分数
        score_hot = compute_autoplay_score(self.song_hot)
        score_cold = compute_autoplay_score(self.song_cold)

        # 热门歌曲分数应该远高于冷门歌曲
        self.assertGreater(score_hot, score_cold)

        # 将分数加入堆后验证正确性
        self.aheap.add_to_autoplay(self.song_cold, score_cold)
        self.aheap.add_to_autoplay(self.song_hot, score_hot)
        top = self.aheap.next_autoplay()
        self.assertEqual(top.song_id, "S001")  # S001 更热门

    def test_next_autoplay_all_songs(self):
        """测试多次调用 next_autoplay 直到清空，确保每个元素弹出一次"""
        songs = [
            (Song("T01", "X1", "A", "A", Genre.POP, 100, 0, 0), 30.0),
            (Song("T02", "X2", "A", "A", Genre.POP, 100, 0, 0), 10.0),
            (Song("T03", "X3", "A", "A", Genre.POP, 100, 0, 0), 50.0),
            (Song("T04", "X4", "A", "A", Genre.POP, 100, 0, 0), 20.0),
            (Song("T05", "X5", "A", "A", Genre.POP, 100, 0, 0), 40.0),
        ]
        for song, score in songs:
            self.aheap.add_to_autoplay(song, score)

        # 按评分从高到低依次弹出
        popped_ids = []
        while not self.aheap.is_empty():
            s = self.aheap.next_autoplay()
            popped_ids.append(s.song_id)

        # 验证弹出顺序是降序：50, 40, 30, 20, 10
        expected = ["T03", "T05", "T01", "T04", "T02"]
        self.assertEqual(popped_ids, expected,
            f"弹出顺序不对：期望 {expected}，实际 {popped_ids}")
        self.assertTrue(self.aheap.is_empty())


if __name__ == "__main__":
    unittest.main(verbosity=2)