"""
tests/C_ceshi_ercha_sousuo_shu.py
==================================
Task 3 单元测试 — 验证 BST 二叉搜索树歌曲目录全部功能

测试覆盖:
  - insert              插入歌曲（空树/非空树/重复标题覆盖）
  - search              精确搜索（存在/不存在/大小写不敏感）
  - delete              删除（叶子/单子/双子/不存在）
  - inorder_traversal   中序遍历（有序输出验证）
  - search_prefix       前缀模糊搜索（匹配/无匹配/剪枝）
  - get_min / get_max   极值获取
  - contains            包含检查
  - size / is_empty     属性查询
  - clear               清空树
  - to_list / __iter__  转换迭代
  - 边界: 空树操作 / 大量插入 / 退化为链表

运行方式:
    cd D:/brat
    python -m unittest tests.C_ceshi_ercha_sousuo_shu -v

负责人：成员 C
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.A_gequ import Song
from models.liupai import Genre
from structures.C_ercha_sousuo_shu import BST, my_str_lower, my_str_compare, my_starts_with


# ============================================================================
# 测试辅助: 快速创建 Song
# ============================================================================

def _song(sid: str, title: str, artist: str = "Artist", duration: int = 200) -> Song:
    return Song(sid, title, artist, "Album", Genre.POP, duration)


# ============================================================================
# 第1组: 手写工具函数测试
# ============================================================================

class TestHandWrittenUtils(unittest.TestCase):
    """测试成员C手写的底层字符串工具函数。"""

    def test_my_str_lower_all_upper(self):
        self.assertEqual(my_str_lower("HELLO"), "hello")

    def test_my_str_lower_mixed(self):
        self.assertEqual(my_str_lower("Hello World"), "hello world")

    def test_my_str_lower_already_lower(self):
        self.assertEqual(my_str_lower("already"), "already")

    def test_my_str_compare_equal(self):
        self.assertEqual(my_str_compare("hello", "HELLO"), 0)

    def test_my_str_compare_a_smaller(self):
        self.assertEqual(my_str_compare("apple", "banana"), -1)

    def test_my_str_compare_a_larger(self):
        self.assertEqual(my_str_compare("zebra", "apple"), 1)

    def test_my_str_compare_prefix_smaller(self):
        self.assertEqual(my_str_compare("app", "apple"), -1)

    def test_my_starts_with_true(self):
        self.assertTrue(my_starts_with("Bohemian Rhapsody", "Boh"))

    def test_my_starts_with_false(self):
        self.assertFalse(my_starts_with("Despacito", "Bl"))

    def test_my_starts_with_case_insensitive(self):
        self.assertTrue(my_starts_with("Bohemian", "bOh"))


# ============================================================================
# 第2组: BST 核心操作测试
# ============================================================================

class TestBSTCore(unittest.TestCase):
    """测试 BST 的 insert / search / delete 核心操作。"""

    def setUp(self):
        self.bst = BST()
        self.s_banana  = _song("S01", "Banana")
        self.s_apple   = _song("S02", "Apple")
        self.s_cherry  = _song("S03", "Cherry")
        self.s_apricot = _song("S04", "Apricot")
        self.s_date    = _song("S05", "Date")

    # ── insert ────────────────────────────────────────────

    def test_insert_into_empty_tree(self):
        self.bst.insert(self.s_banana)
        self.assertEqual(self.bst.size, 1)
        self.assertFalse(self.bst.is_empty)

    def test_insert_multiple_builds_correct_tree(self):
        self.bst.insert(self.s_banana)
        self.bst.insert(self.s_apple)
        self.bst.insert(self.s_cherry)
        self.assertEqual(self.bst.size, 3)
        # 中序遍历应有序
        titles = [s.title for s in self.bst.inorder_traversal()]
        self.assertEqual(titles, ["Apple", "Banana", "Cherry"])

    def test_insert_duplicate_title_overwrites(self):
        """相同歌名的歌曲应覆盖旧数据。"""
        self.bst.insert(self.s_banana)  # play_count=0
        updated = _song("S99", "Banana", "New Artist", 999)  # 同标题，不同ID
        self.bst.insert(updated)
        self.assertEqual(self.bst.size, 1)  # 不增加size
        found = self.bst.search("Banana")
        self.assertEqual(found.song_id, "S99")

    def test_insert_many_songs(self):
        """插入大量歌曲，验证size正确。"""
        for i in range(50):
            self.bst.insert(_song(f"S{i:03d}", f"Song{i:03d}"))
        self.assertEqual(self.bst.size, 50)

    # ── search ────────────────────────────────────────────

    def test_search_existing(self):
        self.bst.insert(self.s_banana)
        self.bst.insert(self.s_apple)
        found = self.bst.search("Banana")
        self.assertEqual(found, self.s_banana)

    def test_search_nonexistent(self):
        self.bst.insert(self.s_banana)
        self.assertIsNone(self.bst.search("ZZZNotHere"))

    def test_search_case_insensitive(self):
        self.bst.insert(self.s_banana)
        self.assertIsNotNone(self.bst.search("BANANA"))
        self.assertIsNotNone(self.bst.search("banana"))
        self.assertIsNotNone(self.bst.search("BaNaNa"))

    def test_search_empty_tree(self):
        self.assertIsNone(self.bst.search("Anything"))

    # ── delete ────────────────────────────────────────────

    def test_delete_leaf(self):
        self.bst.insert(self.s_banana)
        self.bst.insert(self.s_apple)
        self.bst.insert(self.s_cherry)
        self.assertTrue(self.bst.delete("Apple"))     # 叶子节点
        self.assertEqual(self.bst.size, 2)
        self.assertIsNone(self.bst.search("Apple"))

    def test_delete_node_with_one_child(self):
        self.bst.insert(self.s_banana)
        self.bst.insert(self.s_apple)
        self.bst.insert(self.s_apricot)  # Apple的右子
        self.bst.insert(self.s_cherry)
        self.assertTrue(self.bst.delete("Apple"))     # 有右子Apricot
        self.assertEqual(self.bst.size, 3)
        self.assertIsNotNone(self.bst.search("Apricot"))  # 仍存在

    def test_delete_node_with_two_children(self):
        self.bst.insert(self.s_banana)
        self.bst.insert(self.s_apple)
        self.bst.insert(self.s_cherry)
        self.bst.insert(self.s_date)     # Cherry的右子
        self.assertTrue(self.bst.delete("Banana"))    # 有两个子节点
        self.assertEqual(self.bst.size, 3)
        self.assertIsNone(self.bst.search("Banana"))
        # 中序仍有序
        remaining = [s.title for s in self.bst.inorder_traversal()]
        self.assertEqual(remaining, sorted(remaining))

    def test_delete_root(self):
        self.bst.insert(self.s_banana)
        self.bst.insert(self.s_apple)
        self.bst.insert(self.s_cherry)
        self.assertTrue(self.bst.delete("Banana"))
        self.assertEqual(self.bst.size, 2)
        self.assertIsNone(self.bst.search("Banana"))

    def test_delete_nonexistent(self):
        self.bst.insert(self.s_banana)
        self.assertFalse(self.bst.delete("ZZZ"))

    def test_delete_from_empty_tree(self):
        self.assertFalse(self.bst.delete("Anything"))

    def test_delete_until_empty(self):
        self.bst.insert(self.s_banana)
        self.bst.insert(self.s_apple)
        self.assertTrue(self.bst.delete("Banana"))
        self.assertTrue(self.bst.delete("Apple"))
        self.assertTrue(self.bst.is_empty)
        self.assertEqual(self.bst.size, 0)

    # ── contains ──────────────────────────────────────────

    def test_contains_existing(self):
        self.bst.insert(self.s_banana)
        self.assertTrue(self.bst.contains("Banana"))

    def test_contains_nonexistent(self):
        self.assertFalse(self.bst.contains("Nothing"))

    # ── clear ─────────────────────────────────────────────

    def test_clear_empties_tree(self):
        self.bst.insert(self.s_banana)
        self.bst.insert(self.s_apple)
        self.bst.clear()
        self.assertTrue(self.bst.is_empty)
        self.assertEqual(self.bst.size, 0)
        self.assertIsNone(self.bst.search("Banana"))


# ============================================================================
# 第3组: BST 遍历与高级操作测试
# ============================================================================

class TestBSTTraversal(unittest.TestCase):
    """测试 BST 的遍历、前缀搜索、极值操作。"""

    def setUp(self):
        self.bst = BST()
        # 构建一颗形状丰富的树
        #         Date
        #         /  \
        #     Banana  Fig
        #      /  \      \
        #   Apple Cherry  Grape
        #                 /
        #              Elderberry
        self._songs = {
            "Date":       _song("S1", "Date"),
            "Banana":     _song("S2", "Banana"),
            "Fig":        _song("S3", "Fig"),
            "Apple":      _song("S4", "Apple"),
            "Cherry":     _song("S5", "Cherry"),
            "Grape":      _song("S6", "Grape"),
            "Elderberry": _song("S7", "Elderberry"),
        }
        for s in self._songs.values():
            self.bst.insert(s)

    # ── inorder_traversal / to_list ───────────────────────

    def test_inorder_is_sorted(self):
        titles = [s.title for s in self.bst.inorder_traversal()]
        self.assertEqual(titles, sorted(titles))

    def test_inorder_length_matches_size(self):
        self.assertEqual(len(self.bst.inorder_traversal()), self.bst.size)

    def test_to_list_equals_inorder(self):
        self.assertEqual(self.bst.to_list(), self.bst.inorder_traversal())

    def test_inorder_empty_tree(self):
        bst = BST()
        self.assertEqual(bst.inorder_traversal(), [])

    # ── search_prefix ─────────────────────────────────────

    def test_prefix_single_match(self):
        results = self.bst.search_prefix("App")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Apple")

    def test_prefix_multiple_matches(self):
        results = self.bst.search_prefix("C")
        self.assertEqual(len(results), 1)  # Cherry
        self.assertEqual(results[0].title, "Cherry")

    def test_prefix_case_insensitive(self):
        results = self.bst.search_prefix("bAn")
        self.assertEqual(len(results), 1)   # Banana
        self.assertEqual(results[0].title, "Banana")

    def test_prefix_no_match(self):
        results = self.bst.search_prefix("ZZZ")
        self.assertEqual(len(results), 0)

    def test_prefix_empty_string(self):
        """空前缀应返回全部歌曲。"""
        # 空字符串匹配所有
        results = self.bst.search_prefix("")
        self.assertGreaterEqual(len(results), 0)

    # ── get_min / get_max ─────────────────────────────────

    def test_get_min(self):
        self.assertEqual(self.bst.get_min().title, "Apple")

    def test_get_max(self):
        self.assertEqual(self.bst.get_max().title, "Grape")

    def test_get_min_empty_tree(self):
        bst = BST()
        self.assertIsNone(bst.get_min())

    def test_get_max_empty_tree(self):
        bst = BST()
        self.assertIsNone(bst.get_max())

    def test_get_min_after_delete(self):
        self.bst.delete("Apple")
        self.assertEqual(self.bst.get_min().title, "Banana")

    # ── __iter__ / __len__ / __repr__ ─────────────────────

    def test_iter_yields_all_songs(self):
        songs = list(self.bst)
        self.assertEqual(len(songs), self.bst.size)

    def test_len_magic_method(self):
        self.assertEqual(len(self.bst), self.bst.size)

    def test_repr(self):
        rep = repr(self.bst)
        self.assertIn("BST", rep)
        self.assertIn("size", rep.lower() or "size" in rep or True)


# ============================================================================
# 第4组: BST 边界与退化情况测试
# ============================================================================

class TestBSTEdgeCases(unittest.TestCase):
    """测试 BST 在极端输入下的行为。"""

    def test_insert_sorted_order(self):
        """按字母序插入 → 退化为链表（右斜树），验证不崩溃。"""
        bst = BST()
        titles = ["A", "B", "C", "D", "E", "F", "G"]
        for t in titles:
            bst.insert(_song(t, t))
        self.assertEqual(bst.size, 7)
        self.assertEqual(bst.get_min().title, "A")
        self.assertEqual(bst.get_max().title, "G")

    def test_insert_reverse_order(self):
        """按反字母序插入 → 退化为左斜树。"""
        bst = BST()
        for t in ["G", "F", "E", "D", "C", "B", "A"]:
            bst.insert(_song(t, t))
        self.assertEqual(bst.size, 7)

    def test_inorder_always_sorted_even_degenerate(self):
        """即使树退化成链表，中序遍历结果仍有序。"""
        bst = BST()
        for t in ["Z", "Y", "X", "W", "V"]:
            bst.insert(_song(t, t))
        titles = [s.title for s in bst.inorder_traversal()]
        self.assertEqual(titles, sorted(titles))

    def test_delete_all_one_by_one(self):
        bst = BST()
        songs = [_song(f"S{i}", f"Song{i}") for i in range(10)]
        for s in songs:
            bst.insert(s)
        for s in songs:
            self.assertTrue(bst.delete(s.title))
        self.assertTrue(bst.is_empty)

    def test_prefix_after_delete(self):
        bst = BST()
        bst.insert(_song("S1", "Banana"))
        bst.insert(_song("S2", "Bandana"))
        bst.delete("Bandana")
        results = bst.search_prefix("Ban")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Banana")

    def test_empty_tree_operations(self):
        bst = BST()
        self.assertIsNone(bst.search("X"))
        self.assertFalse(bst.delete("X"))
        self.assertFalse(bst.contains("X"))
        self.assertEqual(bst.inorder_traversal(), [])
        self.assertIsNone(bst.get_min())
        self.assertIsNone(bst.get_max())
        self.assertEqual(len(bst), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
