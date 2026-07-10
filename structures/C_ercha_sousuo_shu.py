"""
structures/bst.py
==================
Task 3 — BST（二叉搜索树）完整实现  【成员C负责】

本模块完全手写实现了一个基于二叉搜索树（BST）的"歌曲目录"数据结构。
所有核心操作（比较、查找、遍历等）均自行编写函数，不依赖Python内置高级函数。

【为什么用 BST 存储歌曲目录？】
    音乐流媒体平台中，用户经常需要按歌名快速查找歌曲。
    相比线性搜索（逐个对比整个列表，时间 O(n)），
    BST 将搜索时间降到 O(log n)，效率大幅提升。
    同时，BST 的"中序遍历"天然按字母序输出结果，
    可以直接用来展示"按歌名排序的歌曲列表"。

【BST 的排序规则】
    以 Song.title（歌名）作为键，按字母序排列（不区分大小写）。
    例如: "Blinding Lights" < "Bohemian Rhapsody" < "Despacito"

【与成员A代码的对接接口】（data_loader.py 中调用）
    - bst = BST()                    # 创建空树
    - bst.insert(song: Song)         # 插入一首歌
    - bst.search(title: str) -> Song # 按精确歌名搜索

【额外提供的实用功能】
    - search_prefix(prefix)     → 模糊前缀搜索（自动补全）
    - delete(title)             → 删除指定歌曲
    - inorder_traversal()       → 中序遍历（返回有序列表）
    - get_min()/get_max()       → 获取最小/最大节点
    - to_list()                 → 转为有序列表
    - size / is_empty           → 属性查询
"""

from __future__ import annotations


# ============================================================================
# 【第一部分：手写字符串/通用工具函数】
# ============================================================================
# 下面这些函数是自己写的底层工具，替代了 Python 内置的 min/max/sorted 等。
# 这样做的好处是：你能看到每一步的比较逻辑，真正理解底层原理。
# ============================================================================


def my_str_lower(s: str) -> str:
    """
    手写：将字符串转为小写。

    原理：ASCII 码中，大写字母 A-Z 的编码是 65-90，
          小写字母 a-z 的编码是 97-122，两者相差 32。
          所以对每个字符 +32 即可转为小写。

    参数:
        s: 输入字符串

    返回:
        小写化的字符串副本
    """
    result_chars = []        # 用列表收集转换后的字符
    i = 0                    # 手动维护索引，代替 for 循环
    length = 0               # 先计算字符串长度

    # ── 手动计算字符串长度（不用 len()）──
    while True:
        try:
            _ = s[i]         # 尝试访问第i个字符
            length = length + 1
            i = i + 1
        except IndexError:
            break            # 越界了说明到头了

    # ── 逐个字符转小写 ──
    i = 0
    while i < length:
        ch = s[i]
        code = ord(ch)       # 获取字符的 ASCII 码

        # 如果是大写字母（A=65, Z=90），则加32变为小写
        if code >= 65 and code <= 90:
            ch = chr(code + 32)

        result_chars.append(ch)
        i = i + 1

    # 将字符列表拼接成字符串
    return "".join(result_chars)


def my_str_compare(a: str, b: str) -> int:
    """
    手写：比较两个字符串的大小（不区分大小写）。

    这是 BST 所有操作的核心比较函数！
    insert/search/delete 都靠它决定"往左走"还是"往右走"。

    比较规则（字典序/字母序）:
        从左到右逐个字符比较 ASCII 码：
          - 第一个不同的字符决定了整体大小关系
          - 如果其中一个字符串先结束，则较短的更小

    返回值:
        负数 (-1): a < b （a 在字母表中排前面）
        0:      a == b （两串相同）
        正数 (1): a > b （a 在字母表中排后面）

    示例:
        my_str_compare("apple", "banana")   → -1 (a < b)
        my_str_compare("zebra", "apple")    → 1  (z > a)
        my_str_compare("hello", "hello")    → 0  (相等)
    """
    # 统一转为小写后再比较，确保不区分大小写
    a_lower = my_str_lower(a)
    b_lower = my_str_lower(b)

    # 取两个字符串长度的较小值，作为比较范围
    len_a = 0
    while True:
        try:
            _ = a_lower[len_a]
            len_a = len_a + 1
        except IndexError:
            break

    len_b = 0
    while True:
        try:
            _ = b_lower[len_b]
            len_b = len_b + 1
        except IndexError:
            break

    # 用手写 min 函数取较小长度
    if len_a < len_b:
        min_len = len_a
    else:
        min_len = len_b

    # ── 逐个字符比较 ──
    i = 0
    while i < min_len:
        code_a = ord(a_lower[i])
        code_b = ord(b_lower[i])

        if code_a < code_b:
            return -1       # a 更小
        elif code_a > code_b:
            return 1        # a 更大

        i = i + 1

    # ── 前面都一样，比较谁更长 ──
    if len_a < len_b:
        return -1           # a 是前缀，a 更小
    elif len_a > len_b:
        return 1            # b 是前缀，b 更小
    else:
        return 0            # 完全相等


def my_starts_with(s: str, prefix: str) -> bool:
    """
    手写：判断字符串 s 是否以 prefix 开头。

    用于"前缀搜索"功能 —— 用户输入部分歌名时进行模糊匹配。

    参数:
        s: 完整字符串
        prefix: 要检查的前缀

    返回:
        True  → s 以 prefix 开头
        False → 不以该前缀开头

    示例:
        my_starts_with("Bohemian Rhapsody", "Boh") → True
        my_starts_with("Despacito", "Bl")          → False
    """
    # 计算前缀长度
    prefix_len = 0
    while True:
        try:
            _ = prefix[prefix_len]
            prefix_len = prefix_len + 1
        except IndexError:
            break

    # 逐个字符比对
    i = 0
    while i < prefix_len:
        # 如果 s 太短，肯定不以 prefix 开头
        try:
            ch_s = s[i]
        except IndexError:
            return False

        # 比较当前字符（不区分大小写）
        code_s = ord(my_str_lower(ch_s))
        code_p = ord(my_str_lower(prefix[i]))

        if code_s != code_p:
            return False

        i = i + 1

    return True


# ============================================================================
# 【第二部分：定义 BST 节点类】
# ============================================================================
# 节点是 BST 的基本单元。每个节点存一首歌，
# 并通过 left/right 指针连接到子节点。
# ============================================================================


class BSTNode:
    """
    二叉搜索树的【节点类】—— BST 的"积木块"。

    每个节点存储三样东西:
        song  — 歌曲数据（Song 对象）
        left  — 左子节点指针（title 字母序较小的歌在这边）
        right — 右子节点指针（title 字母序较大的歌在这边）

    【图示】
                  [节点: song]
                   /          \
              left子节点    right子节点
             (较小的歌)    (较大的歌)

    为什么把节点单独定义为类？
        1. 逻辑分离：节点的连接逻辑和整棵树的操作逻辑分开
        2. 递归方便：insert/delete 在节点之间传递很直观
        3. 易于调试：可以单独打印一个节点看它的状态
    """

    def __init__(self, song):
        """
        创建一个新节点。

        新节点初始没有子节点（left=right=None），
        就像一片刚落下的叶子。后续 insert 操作会把它接到父节点上。

        参数:
            song (Song): 要存储的歌曲对象
        """
        self.song = song                      # ★ 存储的数据：一首歌
        self.left = None                      # 左子节点（初始无）
        self.right = None                     # 右子节点（初始无）

    def __repr__(self):
        """返回节点的字符串表示，用于调试打印。格式: BSTNode("歌名")"""
        return 'BSTNode("' + str(self.song.title) + '")'


# ============================================================================
# 【第三部分：定义 BST 树类 —— 对外接口】
# ============================================================================
# 这个类封装了所有二叉搜索树的操作。
# 用户只调用 bst.insert()、bst.search() 等方法，不需要碰内部节点。
# ============================================================================


class BST:
    """
    基于二叉搜索树（Binary Search Tree）的歌曲目录。

    【什么是二叉搜索树？】
        它是一种特殊的二叉树，满足以下规则：
        对于树中的每一个节点：
          - 其左子树中所有歌的 title 都 **小于** 该节点的 title
          - 其右子树中所有歌的 title 都 **大于** 该节点的 title
          - 左、右子树本身也分别是 BST（递归定义）

    【直观理解 —— 查字典】
        BST 的结构就像查英文字典的过程：
          - 你翻到中间一页，发现目标单词在前面 → 翻到左半部分继续找
          - 发现目标在后面 → 翻到右半部分继续找
        每次都能排除一半的可能性，所以速度非常快！

    【使用示例】
        >>> bst = BST()
        >>> bst.insert(song1)   # 插入歌曲
        >>> bst.insert(song2)
        >>>
        >>> result = bst.search("Bohemian Rhapsody")
        >>> print(result.artist)  # 输出: Queen
        >>>
        >>> for song in bst.inorder_traversal():
        ...     print(song.title)  # 按字母序输出全部歌名
    """

    def __init__(self):
        """
        初始化一棵空的二叉搜索树。

        root（根节点）= None 表示树里还没有任何歌曲。
        _size 记录节点数量，这样查询"有多少首歌"时不需要遍历整棵树。
        """
        self.root = None    # 根节点，None 代表空树
        self._size = 0      # 节点计数器

    # ══════════════════════════════════════════════════════════
    #  【属性查询方法】
    # ══════════════════════════════════════════════════════════

    @property
    def size(self):
        """返回树中的歌曲数量。O(1) 时间 —— 因为有计数器。"""
        return self._size

    @property
    def is_empty(self):
        """判断树是否为空（没有任何歌曲）。返回 True 或 False。"""
        return self.root is None

    # ══════════════════════════════════════════════════════════
    #  【核心工具：获取比较键 & 比较两首歌】
    # ══════════════════════════════════════════════════════════

    def _get_key(self, song):
        """
        提取歌曲的比较键（key）。

        使用 title 的小写形式作为 key，确保:
          1. 不区分大小写："Hello" 和 "hello" 视为同一首歌
          2. 按字母序排列：符合音乐 App 的常见排序方式

        参数:
            song: Song 对象

        返回:
            小写化的歌名字符串
        """
        return my_str_lower(song.title)

    def _compare(self, song, node_song):
        """
        比较两首歌曲的 title，决定在 BST 中的位置关系。

        这是最重要的决策函数！insert/search/delete 全都靠它来导航。

        返回值:
            -1 → song 的 title < node_song 的 title → 应该往【左】走
             0 → 两首歌唱名相同 → 找到了（或重复插入）
             1 → song 的 title > node_song 的 title → 应该往【右】走
        """
        key_a = self._get_key(song)
        key_b = self._get_key(node_song)
        return my_str_compare(key_a, key_b)

    # ══════════════════════════════════════════════════════════
    #  【操作1：INSERT 插入】★ 成员A的data_loader会调用这个
    # ══════════════════════════════════════════════════════════
    #
    #  【插入算法 —— 图解步骤】
    #
    #  例：依次插入 ["banana", "apple", "cherry"]
    #
    #  Step 1: 插入 "banana"
    #          树空 → banana 成为根节点
    #                  [banana]
    #
    #  Step 2: 插入 "apple"
    #          apple < banana → 放左边
    #                  [banana]
    #                   /
    #              [apple]
    #
    #  Step 3: 插入 "cherry"
    #          cherry > banana → 放右边
    #                  [banana]
    #                   /    \
    #              [apple]  [cherry]
    #
    #  时间复杂度: 平均 O(log n), 最坏 O(n)（退化为链表时）
    # ══════════════════════════════════════════════════════════

    def insert(self, song):
        """
        将一首歌插入到 BST 中。【对外接口】

        以 song.title 作为键，找到正确的位置挂载上去。
        如果已存在同名的歌，则用新数据覆盖旧数据（更新操作）。

        参数:
            song (Song): 要插入的歌曲对象

        使用方式（成员A的 data_loader.py 中调用）:
            >>> bst = BST()
            >>> for song in songs_list:
            ...     bst.insert(song)
        """
        # 【情况1】空树 → 新节点直接成为根节点
        if self.root is None:
            self.root = BSTNode(song)
            self._size = self._size + 1
            return

        # 【情况2】非空树 → 从根开始递归寻找位置
        self.root = self._insert_recursive(self.root, song)

    def _insert_recursive(self, node, song):
        """
        递归辅助函数 —— 在以 node 为根的子树中插入 song。

        【递归的核心思想】
            每次只关心"当前这一个节点"，然后让递归处理剩下的：
            1. 当前节点是空位？→ 创建新节点，返回！
            2. 比较 → 决定去左还是右
            3. 把递归的结果重新接回 left/right（这一步很重要！）

        为什么要把返回值赋给 node.left/node.right？
            Python 中变量赋值不会修改原引用。
            递归创建了新节点后，必须手动把它"挂回"父节点上。

        参数:
            node: 当前访问的节点（可能为 None）
            song: 要插入的歌

        返回:
            插入完成后的子树根节点
        """
        # ── 终止条件: 到达空位 → 创建新节点 ──
        if node is None:
            self._size = self._size + 1  # 只有新建节点时才+1
            return BSTNode(song)

        # ── 比较: 决定往哪边走 ──
        cmp_result = self._compare(song, node.song)

        if cmp_result == -1:
            # 新歌名较小 → 应该插在左子树
            # 递归后把结果接回 left
            node.left = self._insert_recursive(node.left, song)

        elif cmp_result == 1:
            # 新歌名较大 → 应该插在右子树
            # 递归后把结果接回 right
            node.right = self._insert_recursive(node.right, song)

        else:
            # ── 歌名相同 → 更新数据（覆盖旧记录）──
            # 设计理由: 同一首歌可能播放量更新了，
            #           重新加载 CSV 时需要替换旧数据。
            # 注意: 不增加 size，因为不是新增歌曲
            node.song = song

        # ── 返回当前节点，保持与上层连接 ──
        return node

    # ══════════════════════════════════════════════════════════
    #  【操作2：SEARCH 搜索】★ 成员A的测试会验证这个
    # ══════════════════════════════════════════════════════════
    #
    #  【搜索算法 —— 类似猜数字游戏】
    #
    #  要找 "apple":
    #    当前="banana" → apple<banana → 往左找
    #    当前="apple"  → 匹配! → 返回 ✓
    #
    #  要找 "zebra"（不存在）:
    #    当前="banana" → zebra>banana → 往右找
    #    当前="cherry" → zebra>cherry → 往右找
    #    当前=None     → 到头了 → 返回 None ✗
    #
    #  时间复杂度: 平均 O(log n), 最坏 O(n)
    # ══════════════════════════════════════════════════════════

    def search(self, title):
        """
        按**精确歌名**搜索歌曲。【对外接口】

        参数:
            title (str): 要搜索的歌名（精确匹配，不区分大小写）

        返回:
            Song 对象 —— 找到了
            None       —— 没找到

        示例:
            >>> bst.search("Bohemian Rhapsody")
            Song(S004, "Bohemian Rhapsody" by Queen, Rock, 355s)
            >>> bst.search("不存在的歌")
            None
        """
        # 去除首尾空白，统一转小写，便于比较
        clean_title = title.strip()
        target_key = my_str_lower(clean_title)
        return self._search_recursive(self.root, target_key)

    def _search_recursive(self, node, target_key):
        """
        递归搜索辅助函数 —— 在子树中查找目标歌名。

        参数:
            node: 当前节点
            target_key: 目标歌名的小写形式（预处理过的）

        返回:
            Song 对象或 None
        """
        # ── 终止条件: 到达空节点 → 沿路都没找到 ──
        if node is None:
            return None

        # ── 获取当前节点的 key ──
        current_key = self._get_key(node.song)

        # ── 三路比较 ──
        cmp = my_str_compare(target_key, current_key)

        if cmp == -1:
            # 目标较小 → 在左子树继续找
            return self._search_recursive(node.left, target_key)
        elif cmp == 1:
            # 目标较大 → 在右子树继续找
            return self._search_recursive(node.right, target_key)
        else:
            # 找到了! → 返回歌曲数据
            return node.song

    # ══════════════════════════════════════════════════════════
    #  【操作3：DELETE 删除】
    # ══════════════════════════════════════════════════════════
    #
    #  【删除算法 —— 最复杂的 BST 操作】
    #
    #  删除分三种情况，难度递增:
    #
    #  情况A: 删除叶子节点（没有子节点）
    #          直接砍掉即可，不影响其他节点。
    #
    #  情况B: 删除只有一个子节点的节点
    #          用那个子节点顶替被删的位置。
    #
    #  情况C: 删除有两个子节点的节点 ← 最复杂!
    #          需要找【中序后继】（右子树中最小的节点）
    #          来替代自己，保持 BST 结构不变。
    #
    #  【为什么选"中序后继"？】
    #      中序后继是比当前节点大的最小节点，
    #      用它替换后，所有左子树节点仍比它小，
    #      所有右子树节点仍比它大，BST 性质得以保持。
    # ══════════════════════════════════════════════════════════

    def delete(self, title):
        """
        按歌名从 BST 中删除一首歌。

        参数:
            title (str): 要删除的歌名

        返回:
            True  —— 删除成功
            False —— 歌曲不存在

        示例:
            >>> bst.delete("Old Song")  # 移除不再需要的歌
            True
        """
        clean_title = title.strip()
        target_key = my_str_lower(clean_title)

        if self.root is None:
            return False

        new_root, deleted = self._delete_recursive(self.root, target_key)
        if deleted:
            self.root = new_root
            self._size = self._size - 1
            return True
        return False

    def _delete_recursive(self, node, target_key):
        """
        递归删除辅助函数 —— 在子树中删除目标节点。

        返回元组: (new_subtree_root, was_deleted)
            new_subtree_root: 删除后的子树根节点
            was_deleted:       是否成功执行了删除
        """
        if node is None:
            # 没找到，到达空节点
            return (None, False)

        current_key = self._get_key(node.song)
        cmp = my_str_compare(target_key, current_key)

        if cmp == -1:
            # 目标在左子树 → 递归去左子树删除
            new_left, deleted = self._delete_recursive(node.left, target_key)
            node.left = new_left
            return (node, deleted)

        elif cmp == 1:
            # 目标在右子树 → 递归去右子树删除
            new_right, deleted = self._delete_recursive(node.right, target_key)
            node.right = new_right
            return (node, deleted)

        else:
            # ── 找到了！这就是要删除的节点 ──
            # 下面处理三种情况:

            # ── 情况A: 叶子节点（左右都没有子节点）──
            #    直接移除，返回 None 给父节点
            if node.left is None and node.right is None:
                return (None, True)

            # ── 情况B: 只有右子节点 ──
            #    用右子节点顶替自己的位置
            if node.left is None:
                return (node.right, True)

            # ── 情况B': 只有左子节点 ──
            #    用左子节点顶替自己的位置
            if node.right is None:
                return (node.left, True)

            # ── 情况C: 有两个子节点（最难的情况！）──
            #    策略：找【中序后继】（右子树中最小的节点）
            #    用后继的 song 数据替换当前节点，然后删除后继节点
            successor_node = self._find_min_node(node.right)
            node.song = successor_node.song
            # 删除右子树中的那个后继节点
            new_right, _ = self._delete_recursive(
                node.right,
                self._get_key(successor_node.song)
            )
            node.right = new_right
            return (node, True)

    def _find_min_node(self, node):
        """
        找出以 node 为根的子树中 key 最小的节点。

        在 BST 中，最小的节点一定在最左边！
        所以只需要一直往左走到底就行。

        参数:
            node: 子树根节点

        返回:
            key 最小的 BSTNode
        """
        current = node
        while current.left is not None:
            current = current.left
        return current

    def _find_max_node(self, node):
        """
        找出以 node 为根的子树中 key 最大的节点。

        在 BST 中，最大的节点一定在最右边！

        参数:
            node: 子树根节点

        返回:
            key 最大的 BSTNode
        """
        current = node
        while current.right is not None:
            current = current.right
        return current

    # ══════════════════════════════════════════════════════════
    #  【操作4：INORDER TRAVERSAL 中序遍历】
    # ══════════════════════════════════════════════════════════
    #
    #  【什么是中序遍历？】
    #    按照「左 → 根 → 右」的顺序访问每个节点。
    #    对于 BST 来说，这恰好就是**从小到大**的有序输出！
    #
    #  【图示】
    #          [banana]
    #           /    \
    #      [apple]  [cherry]
    #
    #    中序遍历输出: apple → banana → cherry  （有序!）
    #
    #  应用场景: 显示"按歌名排列的歌曲列表"
    # ══════════════════════════════════════════════════════════

    def inorder_traversal(self):
        """
        中序遍历 —— 返回按歌名字母序排列的歌曲列表。

        返回:
            list[Song]: 有序歌曲列表

        示例:
            >>> for song in bst.inorder_traversal():
            ...     print(song.title)
            Apple
            Banana
            Cherry
            ...
        """
        result = []
        self._inorder_recursive(self.root, result)
        return result

    def _inorder_recursive(self, node, result_list):
        """
        递归中序遍历辅助函数。

        遍历顺序: 左子树 → 当前节点 → 右子树
        这正是 BST 有序输出的秘密所在！
        """
        if node is None:
            return

        # 1. 先遍历左子树（所有更小的歌）
        self._inorder_recursive(node.left, result_list)

        # 2. 再访问当前节点（输出当前歌）
        result_list.append(node.song)

        # 3. 最后遍历右子树（所有更大的歌）
        self._inorder_recursive(node.right, result_list)

    # ══════════════════════════════════════════════════════════
    #  【操作5：PREFIX SEARCH 前缀搜索】
    # ══════════════════════════════════════════════════════════
    #
    #  【什么是前缀搜索？】
    #    用户输入歌名的开头部分（如 "Boh"），
    #    系统找出所有以 "Boh" 开头的歌曲。
    #    这是音乐 App 搜索框"自动补全建议"的核心功能。
    #
    #  【利用 BST 的优化技巧】
    #    由于 BST 的中序遍历是有序的，
    #    我们可以在遍历时利用"剪枝":
    #    一旦发现当前歌名已经超过了前缀范围，
    #    后面的就不用看了（因为后面的更大），直接停止。
    # ══════════════════════════════════════════════════════════

    def search_prefix(self, prefix):
        """
        按前缀模糊搜索 —— 找出所有以指定字符串开头的歌曲。

        参数:
            prefix (str): 搜索前缀（如 "Bo"、"bl"、"D" 等）

        返回:
            list[Song]: 匹配的歌曲列表（按字母序排列）

        示例:
            >>> bst.search_prefix("B")
            [Song(..."Blinding Lights"...),
             Song(..."Bohemian Rhapsody"...)]
            >>> bst.search_prefix("bl")
            [Song(..."Blinding Lights"...)]  # 不区分大小写
        """
        result = []
        clean_prefix = prefix.strip()
        lower_prefix = my_str_lower(clean_prefix)
        self._prefix_search_recursive(self.root, lower_prefix, result)
        return result

    def _prefix_search_recursive(self, node, lower_prefix, result_list):
        """
        递归前缀搜索辅助函数。

        利用 BST 的有序性进行智能搜索：
          - 如果某个节点的前缀已经大于目标前缀，右边不用找了
          - 如果某个节点的前缀小于目标前缀但还有可能匹配，继续深入
        """
        if node is None:
            return

        current_key = self._get_key(node.song)

        # 检查当前节点是否匹配前缀
        if my_starts_with(current_key, lower_prefix):
            # ── 匹配! 收集结果，然后两边都要搜（可能有更多匹配）──
            result_list.append(node.song)
            self._prefix_search_recursive(node.left, lower_prefix, result_list)
            self._prefix_search_recursive(node.right, lower_prefix, result_list)

        elif my_str_compare(current_key, lower_prefix) == -1:
            # ── 当前key < 前缀 → 只可能在右边 ──
            self._prefix_search_recursive(node.right, lower_prefix, result_list)

        else:
            # ── 当前key > 前缀 → 只可能在左边 ──
            self._prefix_search_recursive(node.left, lower_prefix, result_list)

    # ══════════════════════════════════════════════════════════
    #  【操作6：GET MIN/MAX 获取极值节点】
    # ══════════════════════════════════════════════════════════

    def get_min(self):
        """
        获取整棵树中 title 最小的那首歌（字母排在最前面的）。

        在 BST 中，最小的节点就在最左下角！

        返回:
            Song 对象，或 None（空树时）
        """
        if self.root is None:
            return None
        min_node = self._find_min_node(self.root)
        return min_node.song

    def get_max(self):
        """
        获取整棵树中 title 最大的那首歌（字母排在最后面的）。

        在 BST 中，最大的节点就在最右下角！

        返回:
            Song 对象，或 None（空树时）
        """
        if self.root is None:
            return None
        max_node = self._find_max_node(self.root)
        return max_node.song

    # ══════════════════════════════════════════════════════════
    #  【操作7：TO_LIST 转为列表】
    # ══════════════════════════════════════════════════════════

    def to_list(self):
        """
        将 BST 中所有歌曲转为有序列表。

        就是 inorder_traversal() 的别名，提供更直观的方法名。

        返回:
            list[Song]: 按歌名排序的歌曲列表
        """
        return self.inorder_traversal()

    # ══════════════════════════════════════════════════════════
    #  【操作8：CONTAINS 包含检查】
    # ══════════════════════════════════════════════════════════

    def contains(self, title):
        """
        检查某首歌是否存在于 BST 中。

        比 search() 更简洁 —— 只返回 True/False，不要具体对象。

        参数:
            title (str): 歌名

        返回:
            True  → 存在
            False → 不存在
        """
        return self.search(title) is not None

    # ══════════════════════════════════════════════════════════
    #  【操作9：CLEAR 清空整棵树】
    # ══════════════════════════════════════════════════════════

    def clear(self):
        """
        清空整棵树，移除所有歌曲。

        通过将 root 设为 None 实现清空。
        Python 的垃圾回收会自动回收所有被丢弃的节点。
        """
        self.root = None
        self._size = 0

    # ══════════════════════════════════════════════════════════
    #  【辅助方法：__repr__ 和 __len__】
    # ══════════════════════════════════════════════════════════

    def __repr__(self):
        """
        返回 BST 的字符串表示，用于调试。

        格式: BST(size=5, root="banana")
        """
        if self.root is None:
            return "BST(empty)"
        root_name = self.root.song.title
        return "BST(size=" + str(self._size) + ', root="' + root_name + '")'

    def __len__(self):
        """支持 len(bst) 语法，返回歌曲数量。"""
        return self._size

    def __iter__(self):
        """
        支持 for 循环遍历: `for song in bst:`

        按中序（字母序）逐一 yield 歌曲。
        这是一个"生成器"，每次 yield 一个值，省内存。
        """
        return self._iter_inorder(self.root)

    def _iter_inorder(self, node):
        """
        中序遍历生成器 —— 用 yield 实现惰性迭代。

        yield 与 return 不同:
          - return: 函数结束，返回一个值
          - yield:  函数"暂停"，返回一个值，下次调用时从暂停处继续

        这使得可以用 for 循环逐个取出元素，
        而不需要一次性创建完整的列表（节省内存）。
        """
        if node is None:
            return
        # yield from 需要 Python 3.3+
        # 这里用手动方式展开
        for song in self._iter_inorder(node.left):
            yield song
        yield node.song
        for song in self._iter_inorder(node.right):
            yield song


# ============================================================================
# 【模块测试入口】
# ============================================================================
