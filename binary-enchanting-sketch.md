# Music Streaming Playlist Engine - 完整项目计划

## 项目概述
构建音乐流媒体播放列表引擎的后端 + Web可视化界面。包含三个核心数据结构（双向链表、BST、堆）、算法分析（播放列表统计、智能洗牌、推荐引擎）、性能基准测试、以及品味转变检测。

**技术栈**: Python 3 + Flask + 原生HTML/CSS/JS + matplotlib

---

## 一、项目目录结构

```
d:/music/
├── run.py                          # 入口：启动Flask应用
├── requirements.txt                # flask, matplotlib
├── songs_dataset.csv               # 自动生成的数据集(25+首歌)
├── README.md
│
├── data_structures/                # 核心数据结构层（无内部依赖）
│   ├── __init__.py
│   ├── song.py                     # Song类 + Genre枚举
│   ├── doubly_linked_list.py       # 播放列表：双向链表
│   ├── bst.py                      # 歌曲目录：二叉搜索树
│   └── heap.py                     # 自动播放队列：最大堆
│
├── algorithms/                     # 算法层（依赖data_structures）
│   ├── __init__.py
│   ├── analytics.py                # 播放列表分析（遍历链表）
│   ├── smart_shuffle.py            # 智能洗牌（约束排列）
│   ├── recommendation.py           # 推荐引擎（跨结构整合）
│   └── taste_shift.py              # 品味转变检测 + 堆分数更新
│
├── data/                           # 数据层
│   ├── __init__.py
│   ├── csv_generator.py            # CSV数据集生成器
│   └── data_loader.py              # CSV→三种结构的加载器
│
├── benchmarking/                   # 性能基准测试
│   ├── __init__.py
│   └── benchmark.py                # N=50/200/1000/5000/20000 计时+绘图
│
├── web/                            # Flask Web应用
│   ├── __init__.py                 # App工厂
│   ├── routes.py                   # 所有API路由 + 页面渲染
│   ├── templates/
│   │   └── index.html              # 单页应用模板
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           ├── main.js             # 主控制器、API调用、状态管理
│           ├── playlist-view.js    # 双向链表可视化（当前高亮）
│           ├── heap-view.js        # 堆二叉树可视化
│           ├── search.js           # BST搜索栏+结果面板
│           └── recommendations.js  # 推荐卡片展示
│
├── tests/                          # 单元测试（每个核心模块一个测试文件）
│   ├── __init__.py
│   ├── test_song.py
│   ├── test_doubly_linked_list.py
│   ├── test_bst.py
│   ├── test_heap.py
│   ├── test_csv_generator.py
│   ├── test_data_loader.py
│   ├── test_analytics.py
│   ├── test_smart_shuffle.py
│   ├── test_recommendation.py
│   └── test_taste_shift.py
│
└── docs/                           # 项目文档
    ├── design.md                   # 设计决策和架构
    ├── algorithms.md               # 算法解释和复杂度分析
    └── challenges.md               # 挑战和解决方案
```

---

## 二、模块核心设计

### 2.1 Song (`data_structures/song.py`)
- Genre枚举: ROCK, POP, JAZZ, CLASSICAL, HIP_HOP, ELECTRONIC, COUNTRY, RNB, METAL, FOLK, LATIN, REGGAE, BLUES, INDIE
- 字段: song_id, title, artist, album, genre, duration_seconds, play_count, like_count
- `__eq__`: 按song_id比较 | `__lt__`: 按title.lower()比较（BST排序键）
- `to_dict()`: 用于JSON序列化

### 2.2 播放列表 (`data_structures/doubly_linked_list.py`)
- Node: song, next, prev
- Playlist: head, tail, current, _node_map (song_id→Node, O(1)查找)
- 方法: add_song, remove_song, play_next, play_previous, move_to_position, shuffle (Fisher-Yates洗牌节点引用后重链), current_song, display
- **为什么用双向链表**: play_previous()只需O(1)；单向链表需要O(n)

### 2.3 歌曲目录 (`data_structures/bst.py`)
- 按title(字母序)索引，支持: insert, search(精确匹配), find_by_artist(全遍历), find_by_genre(全遍历), range_search(区间搜索带剪枝), in_order_traversal
- 使用迭代实现避免深层递归溢出
- **为什么用BST而非哈希表**: 支持有序遍历和字母范围查询；且能展示最坏/最优性能对比

### 2.4 自动播放队列 (`data_structures/heap.py`)
- 最大堆结构，使用惰性删除(_removed集合)
- 评分公式: `score = 0.4*like_norm + 0.15*play_norm + 0.30*recency_norm + 0.15*genre_bonus`
- 方法: add_to_autoplay, next_autoplay, remove_from_autoplay(O(1)惰性), update_score(标记旧+插入新)
- **为什么用堆而非BST**: 堆专为"总是取最高优先级"设计，extract-max为O(log n)；BST找到最大值再删除更复杂

### 2.5 推荐引擎 (`algorithms/recommendation.py`)
流水线:
1. BST: 找出当前播放列表中最常见风格/艺术家的相关歌曲
2. 过滤: 排除已在播放列表中的歌(用_node_map O(1)检查)
3. 堆: 用评分公式对候选歌曲打分排序
4. 链表: 排除最近播放的10首歌
5. 返回前5首

### 2.6 品味转变检测 (`algorithms/taste_shift.py`)
- TasteShiftDetector类: EMA平滑历史风格分布，滑动窗口记录最近N个动作
- 检测: 对称KL散度超过阈值(0.3)时触发
- 平滑策略: EMA(α=0.1) + 最小样本量(20) + 连续3次确认 + 渐进分数调整(每步0.05)

---

## 三、Web界面设计

单页应用，四面板布局:

| 左面板 | 中面板 | 右面板 |
|--------|--------|--------|
| 播放列表(DLL可视化) | 正在播放(歌曲详情) | 自动播放队列(堆树可视化) |
| 垂直节点列表 | 标题/艺术家/专辑/风格 | 二叉树结构 |
| 当前位置高亮 | 导航按钮(上/下一首) | 下一首按钮 |
| 添加/删除/洗牌按钮 | 点赞/跳过 | |

底部: 推荐面板(5首横向卡片) + 品味转变状态栏

### API路由:
- `GET /` → 主页面
- `/api/playlist/*` → 播放列表CRUD + 导航 + 分析
- `/api/catalogue/*` → 搜索、按艺术家/风格查询、范围搜索
- `/api/autoplay/*` → 自动播放队列操作
- `/api/recommend` → 获取推荐
- `/api/taste/*` → 记录动作、获取统计、模拟转变

---

## 四、实施步骤（共8个阶段，34步）

### 阶段1: 基础数据结构 (步骤1-4)
1. `data_structures/song.py` - Song类 + Genre枚举
2. `data_structures/doubly_linked_list.py` - 双向链表播放列表
3. `data_structures/bst.py` - BST歌曲目录
4. `data_structures/heap.py` - 堆自动播放队列

### 阶段2: 数据层 (步骤5-6)
5. `data/csv_generator.py` - CSV生成器
6. `data/data_loader.py` - 数据加载到三种结构

### 阶段3: 阶段1-2的单元测试 (步骤7-12)
7. `tests/test_song.py`
8. `tests/test_doubly_linked_list.py`
9. `tests/test_bst.py`
10. `tests/test_heap.py`
11. `tests/test_csv_generator.py`
12. `tests/test_data_loader.py`

### 阶段4: 算法实现 (步骤13-16)
13. `algorithms/analytics.py` - 播放列表分析
14. `algorithms/smart_shuffle.py` - 智能洗牌
15. `algorithms/recommendation.py` - 推荐引擎
16. `algorithms/taste_shift.py` - 品味转变检测

### 阶段5: 算法测试 (步骤17-20)
17. `tests/test_analytics.py`
18. `tests/test_smart_shuffle.py`
19. `tests/test_recommendation.py`
20. `tests/test_taste_shift.py`

### 阶段6: 性能基准测试 (步骤21)
21. `benchmarking/benchmark.py` - 计时+绘图

### 阶段7: Web应用 (步骤22-30)
22. `web/__init__.py` + `web/routes.py` - Flask API层
23. `web/templates/index.html` - 页面结构
24. `web/static/css/style.css` - 样式
25. `web/static/js/main.js` - 主控制器
26. `web/static/js/playlist-view.js` - 链表可视化
27. `web/static/js/heap-view.js` - 堆树可视化
28. `web/static/js/search.js` - 搜索功能
29. `web/static/js/recommendations.js` - 推荐展示
30. `run.py` - 入口文件

### 阶段8: 文档 (步骤31-34)
31. `docs/design.md`
32. `docs/algorithms.md`
33. `docs/challenges.md`
34. `README.md`

---

## 五、关键挑战和解决方案

| 挑战 | 解决方案 |
|------|----------|
| BST有序插入退化成链表 | 基准测试中对比测量，文档说明AVL/红黑树是解决方案 |
| 堆可视化 | 利用堆数组特性：索引i的子节点在2i+1和2i+2，按层flexbox渲染 |
| 智能洗牌不可能情况 | 检测单艺术家>50%的退化情况，回退到尽力而为，给出警告 |
| N=20000时BST递归溢出 | 使用迭代实现BST方法 |
| 惰性删除正确性 | next_autoplay中跳过_removed集合中的song_id |

---

## 六、验证方式
1. 运行 `python -m unittest discover tests/ -v` 确保所有测试通过
2. 运行 `python run.py` 启动Web应用，在浏览器中验证所有交互功能
3. 运行 `python benchmarking/benchmark.py` 生成性能图表
4. 手动测试: 添加/删除歌曲、导航播放列表、搜索、获取推荐、模拟品味转变
