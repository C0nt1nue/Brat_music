/* Playlist (doubly linked list) visualization. */

const PlaylistView = {
    render(playlist, currentIndex) {
        const el = document.getElementById("playlist-list");
       if (!playlist || playlist.length === 0) {
            el.innerHTML = '<p class="placeholder">播放列表为空 Playlist is empty</p>';
           return;
       }
        el.innerHTML = playlist.map((song, i) => {
            const isCurrent = i === currentIndex;
            const color = App.genreColor(song.genre);
            return `
                <div class="playlist-item ${isCurrent ? "current" : ""}" data-index="${i}" data-id="${song.song_id}">
                    <span class="idx">${i + 1}</span>
                    <div class="info">
                        <div class="title">${song.title} ${song.liked ? "&#9829;" : ""}</div>
                        <div class="artist">${song.artist}</div>
                    </div>
                    <span class="genre-tag" style="background:${color}33;color:${color}">${song.genre}</span>
                    <button class="remove-btn" data-id="${song.song_id}" title="移除 Remove">&times;</button>
                </div>`;
        }).join("");

        el.querySelectorAll(".playlist-item").forEach(item => {
            item.addEventListener("click", async (e) => {
                if (e.target.classList.contains("remove-btn")) return;
                const idx = parseInt(item.dataset.index);
                await App.api("/api/playlist/goto", "POST", { index: idx });
                await App.refreshPlaylist();
            });
        });
        el.querySelectorAll(".remove-btn").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                e.stopPropagation();
                const id = btn.dataset.id;
                await App.api("/api/playlist/remove", "POST", { song_id: id });
                await App.refreshPlaylist();
                await App.refreshAnalytics();
            });
        });

        // Scroll current into view
        const current = el.querySelector(".current");
        if (current) current.scrollIntoView({ block: "nearest", behavior: "smooth" });
    },
};
