/* Heap (binary tree) visualization using array-index properties. */

const HeapView = {
    render(queue) {
        const el = document.getElementById("heap-view");
       if (!queue || queue.length === 0) {
            el.innerHTML = '<p class="placeholder">队列为空 Queue is empty</p>';
           return;
       }
       // Only show active (non-removed) nodes, limited to first 31 (4 levels)
       const active = queue.filter(n => !n.is_removed).slice(0, 31);
       if (active.length === 0) {
            el.innerHTML = '<p class="placeholder">所有条目已移除(惰性删除) All entries removed (lazy deletion)</p>';
           return;
       }
        // Group by level: level k contains indices 2^k - 1 .. 2^(k+1) - 2
        const levels = [];
        let i = 0;
        while (i < active.length) {
            const levelSize = levels.length === 0 ? 1 : levels[levels.length - 1].length * 2;
            const level = active.slice(i, i + levelSize);
            levels.push(level);
            i += level.length;
            if (i >= 31) break;
        }
        el.innerHTML = levels.map((level, li) => {
            const nodes = level.map((node, ni) => {
                const isRoot = li === 0 && ni === 0;
                const color = node.score > 0.5 ? "#98c379" : node.score > 0.3 ? "#e5c07b" : "#e06c75";
                return `
                    <div class="heap-node ${isRoot ? "root" : ""}" data-id="${node.song_id}" title="${node.title}: ${node.score}">
                        <span class="hn-title">${node.title}</span>
                        <span class="hn-score" style="color:${color}">${node.score.toFixed(3)}</span>
                    </div>`;
            }).join("");
            return `<div class="heap-level">${nodes}</div>`;
        }).join("");

        el.querySelectorAll(".heap-node").forEach(node => {
            node.addEventListener("click", async () => {
                const id = node.dataset.id;
                await App.api("/api/autoplay/remove", "POST", { song_id: id });
                await App.refreshAutoplay();
            });
        });
    },
};
