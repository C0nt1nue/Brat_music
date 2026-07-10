"""
structures/A_tuxing_jiemian.py
===============================
Part 2 — Task 5: 图形界面 (Graphical Interface)  成员A 负责

用 tkinter 搭建界面:
  - 播放列表视图 (当前歌曲高亮)
  - Autoplay 堆列表 + 树形图 (Notebook 切换)
  - BST 搜索框
  - 增删/导航/推荐按钮

调用链:
  ├→ Playlist (成员B) — 播放列表导航+增删+shuffle
  ├→ BST (成员C)      — 搜索+前缀匹配
  ├→ AutoplayHeap (成员D) — 自动播放队列 + 树形图
  └→ recommend_songs (成员D) — 推荐引擎

运行: python structures/A_tuxing_jiemian.py
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from models.A_gequ import Song
from data.A_shuju_jiazai import DataLoader, compute_autoplay_score
from structures.B_bofang_liebiao import PlaylistPart2
from structures.C_ercha_sousuo_shu import BST
from structures.D_dui import AutoplayHeap
from structures.D_tuijian_yinqing import recommend_songs


class SimpleUI:
    """tkinter 图形界面 — 含堆树形可视化。"""

    def __init__(self, csv_path: str = "songs_dataset_20000.csv"):
        # ── 加载数据 ──
        loader = DataLoader(csv_path)
        self.songs = loader.load_songs()
        self.bst = BST()
        for s in self.songs:
            self.bst.insert(s)
        self.playlist = PlaylistPart2()
        for s in self.songs:
            self.playlist.add_song(s)
        self.heap = AutoplayHeap()
        for s in self.songs:
            self.heap.add_to_autoplay(s, compute_autoplay_score(s))

        # ── 窗口 ──
        self.root = tk.Tk()
        self.root.title("Music Streaming Engine")
        self.root.geometry("950x700")

        style = ttk.Style()
        style.configure("TButton", borderwidth=0, relief="flat")

        # ── 主布局: 左(播放列表) | 右(堆+搜索+推荐) ──
        left = ttk.Frame(self.root, width=420)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        right = ttk.Frame(self.root, width=520)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ═══════════════════════════════════════════════════
        # 左半: 播放列表
        # ═══════════════════════════════════════════════════
        ttk.Label(left, text="播放列表 (链表视图)", font=("", 12, "bold")).pack()
        btn_row = ttk.Frame(left)
        btn_row.pack(fill=tk.X, pady=2)
        tk.Button(btn_row, text="< 上一首", command=self._prev, bd=0).pack(side=tk.LEFT, padx=1)
        tk.Button(btn_row, text="下一首 >", command=self._next, bd=0).pack(side=tk.LEFT, padx=1)
        tk.Button(btn_row, text="回到开头", command=self._reset, bd=0).pack(side=tk.LEFT, padx=1)
        tk.Button(btn_row, text="随机", command=self._shuffle, bd=0).pack(side=tk.LEFT, padx=1)

        self.pl_list = tk.Listbox(left, height=28, font=("Consolas", 10))
        self.pl_list.pack(fill=tk.BOTH, expand=True, pady=2)
        self._refresh_playlist()

        edit_row = ttk.Frame(left)
        edit_row.pack(fill=tk.X, pady=2)
        self.del_entry = ttk.Entry(edit_row, width=8)
        self.del_entry.pack(side=tk.LEFT, padx=2)
        ttk.Button(edit_row, text="删除ID", command=self._remove).pack(side=tk.LEFT, padx=2)
        self.add_entry = ttk.Entry(edit_row, width=8)
        self.add_entry.pack(side=tk.LEFT, padx=2)
        ttk.Button(edit_row, text="添加ID", command=self._add).pack(side=tk.LEFT, padx=2)

        # ═══════════════════════════════════════════════════
        # 右半上: 堆 (Notebook: 列表 / 树形图)
        # ═══════════════════════════════════════════════════
        ttk.Label(right, text="Autoplay 最大堆", font=("", 12, "bold")).pack()

        self.heap_notebook = ttk.Notebook(right)
        self.heap_notebook.pack(fill=tk.BOTH, expand=True, pady=2)

        # --- Tab 1: 堆列表 ---
        tab_list = ttk.Frame(self.heap_notebook)
        self.heap_notebook.add(tab_list, text="堆列表")
        self.heap_list = tk.Listbox(tab_list, font=("Consolas", 10))
        self.heap_list.pack(fill=tk.BOTH, expand=True)
        self._refresh_heap()

        # --- Tab 2: 树形图 ---
        tab_tree = ttk.Frame(self.heap_notebook)
        self.heap_notebook.add(tab_tree, text="树形图")
        tree_scroll = ttk.Scrollbar(tab_tree, orient=tk.VERTICAL)
        self.tree_text = tk.Text(tab_tree, font=("Consolas", 9),
                                  yscrollcommand=tree_scroll.set,
                                  wrap=tk.NONE)
        tree_scroll.config(command=self.tree_text.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_text.pack(fill=tk.BOTH, expand=True)
        self._refresh_tree()

        # ═══════════════════════════════════════════════════
        # 右半中: BST 搜索
        # ═══════════════════════════════════════════════════
        ttk.Label(right, text="BST 搜索", font=("", 12, "bold")).pack(pady=(10,0))
        search_row = ttk.Frame(right)
        search_row.pack(fill=tk.X, pady=2)
        self.search_entry = ttk.Entry(search_row)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.search_entry.bind("<KeyRelease>", self._search)
        ttk.Button(search_row, text="搜索", command=self._search).pack(side=tk.RIGHT, padx=2)

        self.search_list = tk.Listbox(right, height=5, font=("Consolas", 10))
        self.search_list.pack(fill=tk.BOTH, expand=True, pady=2)

        # ═══════════════════════════════════════════════════
        # 右半下: 推荐
        # ═══════════════════════════════════════════════════
        ttk.Button(right, text="推荐 5 首歌曲", command=self._recommend).pack(pady=5)
        self.rec_label = ttk.Label(right, text="", foreground="blue")
        self.rec_label.pack()

        # 底部状态栏
        self.status = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    # ── 播放列表操作 ──────────────────────────────────

    def _refresh_playlist(self):
        self.pl_list.delete(0, tk.END)
        current = self.playlist.current_song()
        for i, s in enumerate(self.playlist.to_list()):
            text = f"{'>' if s == current else ' '} {i+1:2d}. {s.song_id} {s.title[:25]:26s} {s.artist[:18]}"
            self.pl_list.insert(tk.END, text)
            if s == current:
                self.pl_list.selection_set(i)
                self.pl_list.see(i)

    def _prev(self):
        s = self.playlist.play_previous()
        if s:
            self.status.config(text=f"上一首: {s.title} — {s.artist}")
        self._refresh_playlist()

    def _next(self):
        s = self.playlist.play_next()
        if s:
            self.status.config(text=f"下一首: {s.title} — {s.artist}")
        self._refresh_playlist()

    def _reset(self):
        self.playlist.reset_to_head()
        self._refresh_playlist()

    def _shuffle(self):
        self.playlist.shuffle()
        self._refresh_playlist()

    def _remove(self):
        sid = self.del_entry.get().strip().upper()
        if sid and self.playlist.remove_song(sid):
            self.status.config(text=f"已删除: {sid}")
            self._refresh_playlist()
        else:
            self.status.config(text=f"删除失败: {sid}")

    def _add(self):
        sid = self.add_entry.get().strip().upper()
        for s in self.songs:
            if s.song_id == sid:
                self.playlist.add_song(s)
                self.status.config(text=f"已添加: {s.title}")
                self._refresh_playlist()
                return
        self.status.config(text=f"未找到: {sid}")

    # ── 堆列表 ────────────────────────────────────────

    def _refresh_heap(self):
        self.heap_list.delete(0, tk.END)
        data = self.heap.display_all()
        for i, item in enumerate(data):
            self.heap_list.insert(tk.END, f"  {i+1:2d}. {item['song_id']} {item['title'][:28]:29s} {item['score']:.1f}")

    # ── 堆树形图 ──────────────────────────────────────

    def _refresh_tree(self):
        self.tree_text.delete("1.0", tk.END)
        tree_str = self.heap.tree()
        self.tree_text.insert("1.0", tree_str)

    # ── 搜索 ──────────────────────────────────────────

    def _search(self, event=None):
        self.search_list.delete(0, tk.END)
        kw = self.search_entry.get().strip()
        if not kw:
            return
        results = self.bst.search_prefix(kw)
        if results:
            for s in results[:15]:
                self.search_list.insert(tk.END, f"  {s.song_id} {s.title[:30]} — {s.artist}")
        else:
            self.search_list.insert(tk.END, "  无匹配结果")

    # ── 推荐 ──────────────────────────────────────────

    def _recommend(self):
        recs = recommend_songs(self.playlist, self.bst, n=5)
        if recs:
            lines = [f"{i+1}. {s.title} — {s.artist}" for i, s in enumerate(recs)]
            self.rec_label.config(text="\n".join(lines))
            self.status.config(text="已生成 5 首推荐")
        else:
            self.rec_label.config(text="无推荐结果")

    def run(self):
        self.root.mainloop()


# ============================================================================
# 主函数
# ============================================================================

def launch_gui(csv_path: str = "songs_dataset_20000.csv"):
    """启动图形界面。"""
    app = SimpleUI(csv_path)
    app.run()


if __name__ == "__main__":
    launch_gui()
