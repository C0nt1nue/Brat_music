"""
main.py  —  音乐流媒体播放列表引擎 · 主程序入口
====================================================
Project 4: Music Streaming Playlist Engine

【程序整体说明】
  本程序整合了四位成员（A/B/C/D）各自实现的核心数据结构，
  构建一个完整的音乐流媒体播放列表引擎。

  架构概览:
    ┌─────────────────────────────────────────────────────┐
    │                    main.py (主程序)                  │
    │         交互菜单 · 功能调度 · 流程控制               │
    ├─────────────────────────────────────────────────────┤
    │  调用以下模块:                                       │
    │    ├── 成员A: 数据加载 + 歌曲模型                    │
    │    ├── 成员B: 双向链表播放列表                       │
    │    ├── 成员C: BST二叉搜索树歌曲目录                   │
    │    └── 成员D: Autoplay最大堆优先级队列                │
    └─────────────────────────────────────────────────────┘

【运行方式】
    cd D:/brat
    python main.py

【成员分工标注说明】
    文件名格式: {功能拼音}_{成员字母}.py
    例: A_shuju_jiazai.py → 成员A实现的数据加载功能
"""

import sys
import os
from pathlib import Path

# ============================================================================
# 【第0段】确保项目根目录在 Python 搜索路径中
# ============================================================================
# 作用: 无论从哪个目录运行 main.py，都能正确导入项目模块
# 调用: 无外部依赖，纯路径设置
_PROJECT_ROOT = Path(__file__).parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


# ============================================================================
# 【第1段】导入各成员模块 — 标明成员分工与调用关系
# ============================================================================
# 每个 import 标注: 成员谁写的 → 导入什么类/函数 → 在主程序中用来做什么

# ── 成员A 模块导入 ───────────────────────────────────────────
#   A_gequ.py        → Song 类         → 所有歌曲的数据载体
#   liupai.py        → Genre 枚举      → 流派类型定义
#   A_shuju_jiazai.py → DataLoader     → 从 CSV 加载歌曲到各数据结构
#                      compute_autoplay_score → 计算 Autoplay 优先级分数
from models.A_gequ import Song
from models.liupai import Genre
from data.A_shuju_jiazai import DataLoader, compute_autoplay_score

# ── 成员B 模块导入 ───────────────────────────────────────────
#   B_bofang_liebiao.py → Playlist 类 (Part1)      → 双向链表基础操作
#                          PlaylistPart2 类 (Part2) → 排序/过滤/搜索/统计
from structures.B_bofang_liebiao import Playlist, PlaylistPart2

# ── 成员C 模块导入 ───────────────────────────────────────────
#   C_ercha_sousuo_shu.py → BST 类  → 二叉搜索树: 按歌名搜索/前缀匹配/有序遍历
from structures.C_ercha_sousuo_shu import BST

# ── 成员D 模块导入 ───────────────────────────────────────────
#   D_dui.py → AutoplayHeap 类 → 最大堆: 自动播放优先级队列
#            → MaxHeap 类      → 底层堆实现(不直接调用)
#            → HeapNode 类     → 堆节点(不直接调用)
from structures.D_dui import AutoplayHeap



# ============================================================================
# 【第2段】全局状态 — 程序运行时持有的数据结构实例
# ============================================================================
# 这些变量在程序启动时初始化，各功能函数通过它们操作数据

_data_loader: DataLoader = None          # 数据加载器(成员A)
_all_songs: list[Song] = []              # 全部歌曲列表(成员A加载)
_playlist: PlaylistPart2 = None          # 播放列表(成员B)
_bst: BST = None                         # 歌曲目录BST(成员C)
_autoplay_heap: AutoplayHeap = None      # Autoplay堆(成员D)


# ============================================================================
# 【第3段】初始化函数 — 程序启动入口
# ============================================================================
# 作用: 加载CSV数据集，注入三种数据结构
# 调用链:
#   init_app()
#     └→ DataLoader(songs_dataset_20000.csv)     【成员A: A_shuju_jiazai】
#         ├→ loader.load_songs()           → 返回 list[Song]
#         ├→ loader.load_into_bst()        → 调用 BST.insert()         【成员C: C_ercha_sousuo_shu】
#         ├→ loader.load_into_autoplay_heap() → 调用 AutoplayHeap      【成员D: D_dui】
#         │     .add_to_autoplay(song, score)
#         │     其中 score = compute_autoplay_score(song)              【成员A: A_shuju_jiazai】
#         └→ loader.load_into_playlist()   → 调用 Playlist.add_song()  【成员B: B_bofang_liebiao】

def init_app(csv_path: str = "songs_dataset_20000.csv") -> bool:
    """
    初始化应用程序: 加载数据集并注入三种数据结构。

    参数:
        csv_path: CSV 数据文件路径

    返回:
        True 初始化成功，False 失败
    """
    global _data_loader, _all_songs, _playlist, _bst, _autoplay_heap

    print("\n" + "=" * 62)
    print("  🎵 音乐流媒体播放列表引擎 — 初始化中...")
    print("=" * 62)

    # ── 步骤1: 创建数据加载器 ──
    # 调用: DataLoader.__init__(csv_path)  【成员A】
    try:
        _data_loader = DataLoader(csv_path)
    except FileNotFoundError as e:
        print(f"\n  ❌ 初始化失败: {e}")
        return False

    # ── 步骤2: 加载全部歌曲到内存 ──
    # 调用: DataLoader.load_songs()  【成员A】
    #   → 内部调用 Song.from_dict() 逐行解析CSV
    _all_songs = _data_loader.load_songs()
    print(f"  ✅ 步骤1: 从 CSV 加载了 {len(_all_songs)} 首歌曲")

    # ── 步骤3: 注入 BST（二叉搜索树歌曲目录）──
    # 调用链:
    #   DataLoader.load_into_bst()  【成员A】
    #     └→ BST()                  【成员C: C_ercha_sousuo_shu】
    #     └→ bst.insert(song)       【成员C: 递归插入, O(log n)】
    #         内部调用 my_str_compare() 手写字符串比较
    _bst = _data_loader.load_into_bst()
    if _bst:
        print(f"  ✅ 步骤2: BST 歌曲目录就绪 ({len(_bst)} 首，按歌名索引)")
    else:
        print(f"  ⚠️  步骤2: BST 模块未就绪（成员C代码缺失）")

    # ── 步骤4: 注入 Autoplay 堆（自动播放优先级队列）──
    # 调用链:
    #   DataLoader.load_into_autoplay_heap()  【成员A】
    #     └→ AutoplayHeap()                   【成员D: D_dui】
    #     └→ compute_autoplay_score(song)     【成员A: 评分公式】
    #        公式: score = like*0.5 + play*0.2 + duration_bonus
    #     └→ heap.add_to_autoplay(song,score) 【成员D: 堆插入, O(log n)】
    _autoplay_heap = _data_loader.load_into_autoplay_heap()
    if _autoplay_heap:
        print(f"  ✅ 步骤3: Autoplay 堆就绪 ({_autoplay_heap.size()} 首，按评分排序)")
    else:
        print(f"  ⚠️  步骤3: Autoplay 堆模块未就绪（成员D代码缺失）")

    # ── 步骤5: 注入双向链表播放列表 ──
    # 调用链:
    #   DataLoader.load_into_playlist()  【成员A】
    #     └→ Playlist()                  【成员B: B_bofang_liebiao】
    #     └→ playlist.add_song(song)     【成员B: O(1) 尾部追加】
    _playlist = PlaylistPart2()  # 使用 Part2 以获得完整功能
    for song in _all_songs:
        _playlist.add_song(song)
    print(f"  ✅ 步骤4: 播放列表就绪 ({len(_playlist)} 首歌曲)")

    print("=" * 62)
    return True


# ============================================================================
# 【第4段】功能函数 — 每个函数对应一个菜单选项
# ============================================================================
# 每个函数标注:
#   - 调用了哪个成员的哪个函数
#   - 实现什么用户功能

# ═══════════════════════════════════════════════════════════════
# 功能1: 显示全部歌曲（按歌名排序）
# ═══════════════════════════════════════════════════════════════

def show_all_songs_sorted():
    """
    按歌名字母序显示全部歌曲。

    调用链:
      BST.inorder_traversal()  【成员C: C_ercha_sousuo_shu】
        └→ 内部递归: 左→根→右，天然有序输出
      Song.display_duration()  【成员A: A_gequ】
    """
    if _bst is None:
        print("⚠️  BST 模块未就绪，无法按歌名排序。")
        return

    songs = _bst.inorder_traversal()  # ★ 调用成员C的中序遍历
    print(f"\n{'='*70}")
    print(f"  📋 全部歌曲（按歌名字母序排列）— 共 {len(songs)} 首")
    print(f"  📞 调用: BST.inorder_traversal() → 成员C: C_ercha_sousuo_shu")
    print(f"{'='*70}")
    print(f"  {'ID':<6} {'歌名':<30} {'艺术家':<22} {'流派':<12} {'时长':>6}")
    print(f"  {'-'*70}")
    for s in songs:
        print(f"  {s.song_id:<6} {s.title[:29]:<30} {s.artist[:21]:<22} "
              f"{s.genre.value:<12} {s.display_duration():>6}")
    print(f"  {'='*70}")


# ═══════════════════════════════════════════════════════════════
# 功能2: 按歌名搜索（精确 + 前缀）
# ═══════════════════════════════════════════════════════════════

def search_by_title():
    """
    按歌名搜索歌曲：先精确匹配，再前缀模糊搜索。

    调用链:
      BST.search(title)         【成员C: C_ercha_sousuo_shu】
        └→ 递归二分查找，O(log n)
      BST.search_prefix(prefix) 【成员C: C_ercha_sousuo_shu】
        └→ 前缀模糊匹配，利用BST有序性剪枝
    """
    if _bst is None:
        print("⚠️  BST 模块未就绪，无法搜索。")
        return

    keyword = input("\n🔍 请输入歌名关键词: ").strip()
    if not keyword:
        print("  输入为空，取消搜索。")
        return

    # ── 精确搜索 ──
    # 调用: BST.search(title) 【成员C】
    result = _bst.search(keyword)
    if result:
        print(f"\n  ✅ 精确匹配:")
        print(f"     {result}")
        return

    # ── 前缀模糊搜索 ──
    # 调用: BST.search_prefix(prefix) 【成员C】
    matches = _bst.search_prefix(keyword)
    if matches:
        print(f"\n  🔍 前缀匹配到 {len(matches)} 首歌曲:")
        for s in matches:
            print(f"     {s}")
    else:
        print(f"  ❌ 未找到包含 '{keyword}' 的歌曲。")


# ═══════════════════════════════════════════════════════════════
# 功能3: 播放列表导航（上一首/下一首/跳转/显示）
# ═══════════════════════════════════════════════════════════════

def playlist_navigation():
    """
    播放列表导航子菜单。

    调用链:
      Playlist.current_song()   【成员B: B_bofang_liebiao】
      Playlist.play_next()      【成员B: O(1) 指针后移】
      Playlist.play_previous()  【成员B: O(1) 指针前移】
      Playlist.jump_to(id)      【成员B: O(1) 跳转】
      Playlist.display()        【成员B: 遍历链表打印】
    """
    if _playlist is None or len(_playlist) == 0:
        print("⚠️  播放列表为空。")
        return

    while True:
        current = _playlist.current_song()  # ★ 调用成员B
        print(f"\n  {'─'*50}")
        print(f"  🎧 播放列表导航")
        print(f"  📞 调用: Playlist (成员B: B_bofang_liebiao)")
        if current:
            print(f"  ▶  当前播放: {current.title} — {current.artist}")
        print(f"  {'─'*50}")
        print(f"  [N] 下一首    [P] 上一首    [J] 跳转到...")
        print(f"  [D] 显示全部  [S] 随机打乱   [R] 回到开头")
        print(f"  [Q] 返回主菜单")
        choice = input("  🎵 请选择: ").strip().lower()

        if choice == 'n':
            song = _playlist.play_next()  # ★ 调用成员B
            if song:
                print(f"  ▶  切换到: {song.title} — {song.artist}")
        elif choice == 'p':
            song = _playlist.play_previous()  # ★ 调用成员B
            if song:
                print(f"  ◀  切换到: {song.title} — {song.artist}")
        elif choice == 'j':
            sid = input("  输入歌曲ID (如 S005): ").strip().upper()
            if _playlist.jump_to(sid):  # ★ 调用成员B
                s = _playlist.current_song()
                print(f"  ⏭  跳转到: {s.title} — {s.artist}")
        elif choice == 'd':
            _playlist.display()  # ★ 调用成员B
        elif choice == 's':
            _playlist.shuffle()  # ★ 调用成员B: Fisher-Yates洗牌
            _playlist.reset_to_head()  # ★ 调用成员B: 重置到头部
            print("  🔀 播放列表已随机打乱！")
            _playlist.display()
        elif choice == 'r':
            _playlist.reset_to_head()  # ★ 调用成员B
            s = _playlist.current_song()
            print(f"  ⏮  已回到开头: {s.title}")
        elif choice == 'q':
            break
        else:
            print("  无效选择，请重试。")


# ═══════════════════════════════════════════════════════════════
# 功能4: 播放列表排序
# ═══════════════════════════════════════════════════════════════

def playlist_sort():
    """
    按指定条件排序播放列表。

    调用链:
      PlaylistPart2.sort_by(criteria)  【成员B: B_bofang_liebiao_part2】
        └→ _merge_sort()  手写归并排序，O(n log n)
        └→ _merge()       合并两个有序子列表
        └→ _compare_nodes()  按 criteria 比较两首歌

    排序条件说明 (成员B实现):
      "title"      → 歌名字母序升序
      "artist"     → 艺术家的字母序升序
      "play_count" → 播放次数降序（热门优先）
      "like_count" → 点赞次数降序（受欢迎优先）
      "duration"   → 时长升序（短歌优先）
    """
    if _playlist is None or len(_playlist) == 0:
        print("⚠️  播放列表为空。")
        return

    print(f"\n  📊 排序条件:")
    print(f"     1. 按歌名 (title)")
    print(f"     2. 按艺术家 (artist)")
    print(f"     3. 按播放次数 (play_count) — 热门优先")
    print(f"     4. 按点赞次数 (like_count) — 受欢迎优先")
    print(f"     5. 按时长 (duration) — 短歌优先")
    choice = input("  请选择 (1-5): ").strip()

    criteria_map = {"1": "title", "2": "artist", "3": "play_count",
                    "4": "like_count", "5": "duration"}
    criteria = criteria_map.get(choice, "title")

    # ★ 调用成员B Part2 的归并排序
    _playlist.sort_by(criteria)
    _playlist.reset_to_head()  # ★ 调用成员B
    print(f"  ✅ 已按 '{criteria}' 排序完成。")
    _playlist.display()


# ═══════════════════════════════════════════════════════════════
# 功能5: 流派过滤
# ═══════════════════════════════════════════════════════════════

def filter_by_genre():
    """
    按流派筛选歌曲并显示。

    调用链:
      PlaylistPart2.filter_by_genre(genre)  【成员B: B_bofang_liebiao_part2】
        └→ 遍历链表，匹配 genre == target_genre
        └→ 返回新的 PlaylistPart2（不影响原列表）
      Genre.all_genres()                    【成员A: liupai.py】
    """
    if _playlist is None:
        print("⚠️  播放列表为空。")
        return

    # 显示可用流派
    print(f"\n  🏷️  可用流派:")
    all_genres = Genre.all_genres()  # ★ 调用成员A的Genre枚举
    for i, g in enumerate(all_genres):
        print(f"     {i+1:2d}. {g}", end="")
        if (i + 1) % 4 == 0:
            print()
    print()

    choice = input("  请输入流派名称 (如 Pop, Rock): ").strip()
    if not choice:
        return

    try:
        # ★ 调用成员B Part2 的流派过滤
        filtered = _playlist.filter_by_genre(choice)
        if len(filtered) == 0:
            print(f"  ❌ 没有找到流派为 '{choice}' 的歌曲。")
        else:
            filtered.display()
    except ValueError as e:
        print(f"  ❌ {e}")


# ═══════════════════════════════════════════════════════════════
# 功能6: Autoplay — 自动播放（按优先级队列）
# ═══════════════════════════════════════════════════════════════

def autoplay_mode():
    """
    进入 Autoplay 模式: 按评分从高到低自动播放。

    调用链:
      AutoplayHeap.peek_next()     【成员D: D_dui】→ O(1) 查看堆顶
      AutoplayHeap.next_autoplay() 【成员D: D_dui】→ O(log n) 弹出堆顶
        └→ MaxHeap.pop()           【成员D: 底层堆弹出】
        └→ MaxHeap._sift_down()    【成员D: 下沉调整】
      AutoplayHeap.display_all()   【成员D: D_dui】→ 显示全部评分
      compute_autoplay_score()     【成员A: A_shuju_jiazai】

    Autoplay 评分公式 (成员A设计):
      score = like_count * 0.5 + play_count * 0.2 + duration_bonus
      其中 duration_bonus: 3-5分钟的歌曲额外+10分
    """
    if _autoplay_heap is None or _autoplay_heap.is_empty():
        print("⚠️  Autoplay 堆为空或未就绪。")
        return

    # 重建堆（使用成员A的评分公式 + 成员D的堆操作）
    # 调用:
    #   AutoplayHeap()                       【成员D】
    #   compute_autoplay_score(song)          【成员A】
    #   AutoplayHeap.add_to_autoplay(s,score)【成员D】
    global _autoplay_heap
    _autoplay_heap = AutoplayHeap()
    for song in _all_songs:
        score = compute_autoplay_score(song)  # ★ 调用成员A
        _autoplay_heap.add_to_autoplay(song, score)  # ★ 调用成员D

    print(f"\n  🎧 Autoplay 自动播放模式")
    print(f"  📞 调用: AutoplayHeap (成员D: D_dui)")
    print(f"  📞 评分:  compute_autoplay_score (成员A: A_shuju_jiazai)")
    print(f"  📊 队列中有 {_autoplay_heap.size()} 首歌曲\n")

    while not _autoplay_heap.is_empty():
        # ── 查看下一首（不移除）──
        next_song = _autoplay_heap.peek_next()  # ★ 调用成员D

        print(f"  ⏭  即将播放: {next_song.title:30s} — {next_song.artist}")
        print(f"     流派: {next_song.genre.value}  |  "
              f"播放: {next_song.play_count:,}  |  点赞: {next_song.like_count:,}")

        action = input("\n  [Enter] 播放下一首  [S] 跳过  [Q] 退出Autoplay: ").strip().lower()

        if action == 'q':
            print("  ⏹  退出 Autoplay 模式。")
            break

        # ── 弹出并"播放" ──
        played = _autoplay_heap.next_autoplay()  # ★ 调用成员D: O(log n)
        if action == 's':
            print(f"  ⏭  已跳过: {played.title}")
        else:
            print(f"  ▶  正在播放: {played.title} — {played.artist}")
            # 播放计数+1（模拟播放行为）
            played.play_count += 1

        if _autoplay_heap.is_empty():
            print("\n  🎉 队列已播放完毕！")


# ═══════════════════════════════════════════════════════════════
# 功能7: 播放列表统计信息
# ═══════════════════════════════════════════════════════════════

def show_statistics():
    """
    显示播放列表的统计摘要。

    调用链:
      PlaylistPart2.get_statistics()  【成员B: B_bofang_liebiao_part2】
        └→ 一次遍历链表 O(n) 收集:
           • 总时长/平均时长
           • 流派分布
           • 平均播放/点赞
           • 最热/最爱/最冷门歌曲
      Song.display_duration()        【成员A: A_gequ】
    """
    if _playlist is None or len(_playlist) == 0:
        print("⚠️  播放列表为空。")
        return

    stats = _playlist.get_statistics()  # ★ 调用成员B Part2

    print(f"\n  {'='*55}")
    print(f"  📊 播放列表统计")
    print(f"  📞 调用: PlaylistPart2.get_statistics() → 成员B: B_bofang_liebiao_part2")
    print(f"  {'='*55}")
    print(f"  总歌曲数:         {stats['total_songs']}")
    print(f"  总时长:           {stats['total_duration_formatted']}")
    print(f"  平均时长:         {stats['average_duration_seconds']} 秒")
    print(f"  平均播放次数:     {stats['average_play_count']:,.1f}")
    print(f"  平均点赞次数:     {stats['average_like_count']:,.1f}")
    print(f"  {'─'*55}")
    print(f"  流派分布:")
    for genre, count in sorted(stats['genre_distribution'].items()):
        bar = "█" * count
        print(f"    {genre:<14} {count:>2} 首  {bar}")
    print(f"  {'─'*55}")
    if stats['most_played']:
        mp = stats['most_played']
        print(f"  🔥 最热门:   {mp.title} — {mp.artist} "
              f"({mp.play_count:,} 次播放)")
    if stats['most_liked']:
        ml = stats['most_liked']
        print(f"  ❤️  最受喜爱: {ml.title} — {ml.artist} "
              f"({ml.like_count:,} 赞)")
    if stats['least_played']:
        lp = stats['least_played']
        print(f"  🥶 最冷门:   {lp.title} — {lp.artist} "
              f"({lp.play_count:,} 次播放)")
    print(f"  {'='*55}")


# ═══════════════════════════════════════════════════════════════
# 功能8: 按艺术家搜索
# ═══════════════════════════════════════════════════════════════

def search_by_artist():
    """
    按艺术家名称搜索（模糊匹配）。

    调用链:
      PlaylistPart2.search_by_artist(keyword)  【成员B: B_bofang_liebiao_part2】
        └→ 遍历链表，不区分大小写模糊匹配
    """
    if _playlist is None:
        print("⚠️  播放列表为空。")
        return

    keyword = input("\n🔍 请输入艺术家关键词: ").strip()
    if not keyword:
        return

    # ★ 调用成员B Part2
    results = _playlist.search_by_artist(keyword)
    if results:
        print(f"\n  🎤 找到 {len(results)} 首匹配歌曲:")
        for s in results:
            print(f"     {s.song_id}  {s.title:30s} — {s.artist}")
    else:
        print(f"  ❌ 未找到艺术家包含 '{keyword}' 的歌曲。")


# ═══════════════════════════════════════════════════════════════
# 功能9: BST 歌曲目录概览
# ═══════════════════════════════════════════════════════════════

def bst_overview():
    """
    显示 BST 歌曲目录的结构信息。

    调用链:
      BST.get_min()  【成员C: C_ercha_sousuo_shu】→ 最左下角
      BST.get_max()  【成员C: C_ercha_sousuo_shu】→ 最右下角
      BST.size       【成员C: 属性】
      BST.search_prefix(prefix) 【成员C: 前缀搜索】
    """
    if _bst is None:
        print("⚠️  BST 模块未就绪。")
        return

    print(f"\n  {'='*50}")
    print(f"  🌳 BST 歌曲目录 (二叉搜索树)")
    print(f"  📞 调用: BST → 成员C: C_ercha_sousuo_shu")
    print(f"  {'='*50}")
    print(f"  歌曲总数:   {_bst.size}")
    print(f"  歌名最小:   {_bst.get_min().title}")   # ★ 调用成员C
    print(f"  歌名最大:   {_bst.get_max().title}")   # ★ 调用成员C
    print(f"  {'─'*50}")

    # 按首字母分组显示
    prefix = input("  输入首字母查看该字母开头的歌曲 (直接回车跳过): ").strip()
    if prefix:
        matches = _bst.search_prefix(prefix)  # ★ 调用成员C: 前缀搜索
        if matches:
            print(f"\n  🔤 以 '{prefix}' 开头的歌曲 ({len(matches)} 首):")
            for s in matches:
                print(f"     {s.song_id}  {s.title} — {s.artist}")
        else:
            print(f"  ❌ 没有以 '{prefix}' 开头的歌曲。")


# ═══════════════════════════════════════════════════════════════
# 功能10: 添加/删除歌曲（播放列表管理）
# ═══════════════════════════════════════════════════════════════

def manage_playlist():
    """
    管理播放列表：添加/删除歌曲。

    调用链:
      Playlist.add_song(song)      【成员B: B_bofang_liebiao】→ O(1) 尾部追加
      Playlist.remove_song(id)     【成员B: B_bofang_liebiao】→ O(1) 定位+删除
      Playlist.find(id)            【成员B: O(1) 查找】
      BST.search(title)            【成员C: C_ercha_sousuo_shu】
    """
    if _playlist is None:
        print("⚠️  播放列表未初始化。")
        return

    while True:
        print(f"\n  {'─'*45}")
        print(f"  📝 播放列表管理 (当前 {len(_playlist)} 首)")
        print(f"  {'─'*45}")
        print(f"  [A] 添加歌曲到列表尾部")
        print(f"  [R] 按ID删除歌曲")
        print(f"  [F] 按ID查找歌曲")
        print(f"  [D] 显示当前播放列表")
        print(f"  [Q] 返回主菜单")
        choice = input("  🎵 请选择: ").strip().lower()

        if choice == 'a':
            sid = input("  输入要添加的歌曲ID (如 S005): ").strip().upper()
            # 先在所有歌曲中查找
            found = None
            for s in _all_songs:
                if s.song_id == sid:
                    found = s
                    break
            if found:
                _playlist.add_song(found)  # ★ 调用成员B
                print(f"  ✅ 已添加: {found.title}")
            else:
                print(f"  ❌ 未找到歌曲 {sid}")

        elif choice == 'r':
            sid = input("  输入要删除的歌曲ID: ").strip().upper()
            result = _playlist.remove_song(sid)  # ★ 调用成员B
            if result:
                print(f"  ✅ 已删除: {result.title}")
            else:
                print(f"  ❌ 未找到 {sid}")

        elif choice == 'f':
            sid = input("  输入歌曲ID: ").strip().upper()
            result = _playlist.find(sid)  # ★ 调用成员B: O(1)
            if result:
                print(f"  ✅ 找到: {result}")
            else:
                print(f"  ❌ 未找到 {sid}")

        elif choice == 'd':
            _playlist.display()  # ★ 调用成员B
        elif choice == 'q':
            break
        else:
            print("  无效选择。")


# ============================================================================
# 【第5段】主菜单 — 程序交互入口
# ============================================================================
# 作用: 显示功能菜单，根据用户选择调度对应的功能函数
# 调用: 上述所有功能函数

def show_menu():
    """显示主菜单"""
    print(f"""
  ╔══════════════════════════════════════════════════════════╗
  ║       🎵  音乐流媒体播放列表引擎  🎵                     ║
  ║       Music Streaming Playlist Engine                    ║
  ╠══════════════════════════════════════════════════════════╣
  ║  成员A: 数据模型 + 数据加载 + 评分公式                   ║
  ║  成员B: 双向链表播放列表 (Part1 + Part2)                 ║
  ║  成员C: BST 二叉搜索树歌曲目录                           ║
  ║  成员D: Autoplay 最大堆优先级队列                        ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  [1] 📋 显示全部歌曲 (BST中序)     — 成员C + 成员A       ║
  ║  [2] 🔍 按歌名搜索 (BST)           — 成员C               ║
  ║  [3] 🎧 播放列表导航               — 成员B (Part1)       ║
  ║  [4] 📊 播放列表排序               — 成员B (Part2)       ║
  ║  [5] 🏷️  流派过滤                   — 成员B (Part2)       ║
  ║  [6] 🎛️  Autoplay 自动播放          — 成员D + 成员A       ║
  ║  [7] 📈 播放列表统计               — 成员B (Part2)       ║
  ║  [8] 🎤 按艺术家搜索               — 成员B (Part2)       ║
  ║  [9] 🌳 BST 歌曲目录概览           — 成员C               ║
  ║  [10]📝 管理播放列表(增删查)       — 成员B               ║
  ║                                                          ║
  ║  [0] 🚪 退出程序                                         ║
  ║                                                          ║
  ╚══════════════════════════════════════════════════════════╝
""")


def main():
    """
    主函数 — 程序入口。

    执行流程:
      1. init_app()           → 加载数据，初始化三种数据结构
      2. show_menu()          → 显示交互菜单
      3. 用户选择功能          → 调用对应的功能函数
      4. 循环直到用户退出
    """
    # ── 初始化 ──
    if not init_app():
        print("\n程序初始化失败，请检查 songs_dataset_20000.csv 是否存在。")
        sys.exit(1)

    # ── 主循环 ──
    while True:
        show_menu()
        choice = input("  请输入选项 [0-10]: ").strip()

        if choice == '1':
            show_all_songs_sorted()       # 成员C BST中序遍历 + 成员A Song
        elif choice == '2':
            search_by_title()              # 成员C BST搜索
        elif choice == '3':
            playlist_navigation()          # 成员B 双向链表导航
        elif choice == '4':
            playlist_sort()                # 成员B Part2 归并排序
        elif choice == '5':
            filter_by_genre()              # 成员B Part2 流派过滤 + 成员A Genre
        elif choice == '6':
            autoplay_mode()                # 成员D 堆 + 成员A 评分
        elif choice == '7':
            show_statistics()              # 成员B Part2 统计
        elif choice == '8':
            search_by_artist()             # 成员B Part2 艺术家搜索
        elif choice == '9':
            bst_overview()                 # 成员C BST概览
        elif choice == '10':
            manage_playlist()              # 成员B 播放列表管理
        elif choice == '0':
            print("\n  👋 感谢使用！再见！\n")
            break
        else:
            print(f"\n  ❌ 无效选项 '{choice}'，请输入 0-10。")

        input("\n  按 Enter 继续...")


# ============================================================================
# 【第6段】程序入口
# ============================================================================
if __name__ == "__main__":
    main()
