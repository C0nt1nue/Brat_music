/* BST search functionality and catalogue browsing. */

const Search = {
    async search() {
        const query = document.getElementById("search-input").value.trim();
        const genre = document.getElementById("genre-filter").value;
        const artist = document.getElementById("artist-filter").value.trim();
        const el = document.getElementById("search-results");
        el.innerHTML = '<p class="placeholder">搜索中 Searching...</p>';
       let results = [];
        if (query) {
            const data = await App.api(`/api/catalogue/search?q=${encodeURIComponent(query)}`);
            results = data.results;
        } else if (genre) {
            const data = await App.api(`/api/catalogue/by-genre?genre=${encodeURIComponent(genre)}`);
            results = data.results;
        } else if (artist) {
            const data = await App.api(`/api/catalogue/by-artist?artist=${encodeURIComponent(artist)}`);
            results = data.results;
        } else {
            const data = await App.api("/api/catalogue/all");
            results = data.results;
        }
        this.renderResults(results, el);
    },

    async rangeSearch() {
        const query = document.getElementById("search-input").value.trim();
        const el = document.getElementById("search-results");
       if (!query) {
            el.innerHTML = '<p class="placeholder">请输入标题作为范围起点 Enter a title for range start</p>';
           return;
       }
        const high = query.charAt(0).toUpperCase() + query.slice(1) + "\uffff";
        const data = await App.api(`/api/catalogue/range?low=${encodeURIComponent(query)}&high=${encodeURIComponent(high)}`);
        this.renderResults(data.results, el);
    },

    async quickSearch(query) {
        const resultsEl = document.getElementById("add-song-results");
        if (!query || query.length < 1) {
            resultsEl.classList.remove("visible");
            return;
        }
        const data = await App.api(`/api/catalogue/search?q=${encodeURIComponent(query)}`);
        if (data.results.length === 0) {
            resultsEl.classList.remove("visible");
            return;
        }
        resultsEl.innerHTML = data.results.slice(0, 8).map(s => `
            <div class="add-song-result" data-id="${s.song_id}">
                <strong>${s.title}</strong> - ${s.artist} (${s.genre})
            </div>`).join("");
        resultsEl.classList.add("visible");
        resultsEl.querySelectorAll(".add-song-result").forEach(item => {
            item.addEventListener("click", async () => {
                await App.api("/api/playlist/add", "POST", { song_id: item.dataset.id });
                document.getElementById("add-song-input").value = "";
                resultsEl.classList.remove("visible");
                await App.refreshPlaylist();
                await App.refreshAnalytics();
            });
        });
    },

    renderResults(results, el) {
       if (!results || results.length === 0) {
            el.innerHTML = '<p class="placeholder">无结果 No results</p>';
           return;
       }
       el.innerHTML = results.map(s => `
           <div class="search-result-item">
               <div class="sri-title">${s.title}</div>
                <div class="sri-meta">${s.artist} | ${s.album} | ${s.genre} | ${s.duration_seconds}s | 播放 Plays: ${s.play_count} | 点赞 Likes: ${s.like_count}</div>
               <div class="sri-actions">
                    <button class="btn btn-sm" onclick="Search.addToPlaylist('${s.song_id}')">加入播放列表 Add to Playlist</button>
                    <button class="btn btn-sm" onclick="Search.addToAutoplay('${s.song_id}')">加入自动播放 Add to Autoplay</button>
               </div>
            </div>`).join("");
    },

    async addToPlaylist(songId) {
        try {
            await App.api("/api/playlist/add", "POST", { song_id: songId });
            await App.refreshPlaylist();
            await App.refreshAnalytics();
        } catch (e) {
            alert(e.message);
        }
    },

    async addToAutoplay(songId) {
        await App.api("/api/autoplay/add", "POST", { song_id: songId });
        await App.refreshAutoplay();
    },
};
