/* Main controller: API calls, state management, event wiring. */

const App = {
    state: {
        playlist: [],
        current: null,
        currentIndex: -1,
        autoplayQueue: [],
        genres: [],
        autoPlaying: false,
        autoPlayTimer: null,
    },

    async init() {
        await this.loadGenres();
        await this.refreshPlaylist();
        await this.refreshAutoplay();
        await this.refreshRecommendations();
        await this.refreshTaste();
        await this.refreshAnalytics();
        this.wireEvents();
    },

    async api(url, method = "GET", body = null) {
        const opts = { method, headers: {} };
        if (body) {
            opts.headers["Content-Type"] = "application/json";
            opts.body = JSON.stringify(body);
        }
        const res = await fetch(url, opts);
        if (!res.ok) {
            const err = await res.json().catch(() => ({ error: res.statusText }));
            throw new Error(err.error || "Request failed");
        }
        return res.json();
    },

    async loadGenres() {
        const data = await this.api("/api/catalogue/genres");
        this.state.genres = data.genres;
        const genreFilter = document.getElementById("genre-filter");
        const simFrom = document.getElementById("sim-from");
        const simTo = document.getElementById("sim-to");
        data.genres.forEach(g => {
            genreFilter.innerHTML += `<option value="${g}">${g}</option>`;
            simFrom.innerHTML += `<option value="${g}">${g}</option>`;
            simTo.innerHTML += `<option value="${g}">${g}</option>`;
        });
        simTo.value = "JAZZ";
    },

    async refreshPlaylist() {
        const data = await this.api("/api/playlist");
        this.state.playlist = data.playlist;
        this.state.current = data.current;
        this.state.currentIndex = data.current_index;
        document.getElementById("playlist-size").textContent = data.size;
        PlaylistView.render(data.playlist, data.current_index);
        this.renderNowPlaying(data.current);
    },

    async refreshAutoplay() {
        const data = await this.api("/api/autoplay");
        this.state.autoplayQueue = data.queue;
        document.getElementById("autoplay-size").textContent = data.size;
        HeapView.render(data.queue);
    },

    async refreshRecommendations() {
        const data = await this.api("/api/recommend?n=5");
        Recommendations.render(data.recommendations);
    },

    async refreshTaste() {
        const data = await this.api("/api/taste/stats");
        this.renderTaste(data);
    },

    async refreshAnalytics() {
        const data = await this.api("/api/playlist/analytics");
        this.renderAnalytics(data);
    },

    renderNowPlaying(song) {
       const el = document.getElementById("nowplaying-detail");
      if (!song) {
           el.innerHTML = '<p class="placeholder">未选择歌曲 No song selected</p>';
          document.getElementById("btn-like").classList.remove("liked");
          return;
      }
      const dur = song.duration_seconds;
      const mins = Math.floor(dur / 60);
      const secs = String(dur % 60).padStart(2, "0");
       el.innerHTML = `
           <span class="np-genre">${song.genre}</span>
           <span class="np-title">${song.title}</span>
           <span class="np-artist">${song.artist}</span>
           <span class="np-album">${song.album}</span>
           <span class="np-meta">
                <span class="np-meta-item"><span class="label">时长 Dur</span><span class="value">${mins}:${secs}</span></span>
                <span class="np-meta-item"><span class="label">播放 Plays</span><span class="value">${song.play_count}</span></span>
                <span class="np-meta-item"><span class="label">点赞 Likes</span><span class="value">${song.like_count}</span></span>
           </span>`;
       const likeBtn = document.getElementById("btn-like");
       if (song.liked) likeBtn.classList.add("liked");
       else likeBtn.classList.remove("liked");
   },

    genreColor(genre) {
        const colors = {
            ROCK: "#e06c75", POP: "#e5c07b", JAZZ: "#61afef", CLASSICAL: "#c678dd",
            HIP_HOP: "#98c379", ELECTRONIC: "#56b6c2", COUNTRY: "#d19a66",
            RNB: "#ff6b9d", METAL: "#7f7f7f", FOLK: "#d4a76a", LATIN: "#f4a261",
            REGGAE: "#2a9d8f", BLUES: "#6c8eef", INDIE: "#bd93f9",
        };
        return colors[genre] || "#6c8eef";
    },

    renderAnalytics(stats) {
        const el = document.getElementById("analytics-content");
       if (!stats || stats.total_songs === 0) {
            el.innerHTML = '<p class="placeholder">暂无数据 No data</p>';
           return;
       }
       let genreBar = '<div class="genre-bar">';
       const total = stats.total_songs;
       for (const [genre, count] of Object.entries(stats.genre_distribution)) {
           const pct = (count / total) * 100;
           genreBar += `<div style="width:${pct}%;background:${this.genreColor(genre)}" title="${genre}: ${count}"></div>`;
       }
       genreBar += "</div>";
       const topArtists = stats.top_artists.map(a => `${a[0]} (${a[1]})`).join(", ");
       el.innerHTML = `
            <div class="stat-row"><span class="label">总歌曲数 Total Songs</span><span class="value">${stats.total_songs}</span></div>
            <div class="stat-row"><span class="label">总时长 Total Duration</span><span class="value">${stats.total_duration}s</span></div>
            <div class="stat-row"><span class="label">平均时长 Avg Duration</span><span class="value">${stats.avg_duration}s</span></div>
            <div class="stat-row"><span class="label">总播放 Total Plays</span><span class="value">${stats.total_plays}</span></div>
            <div class="stat-row"><span class="label">总点赞 Total Likes</span><span class="value">${stats.total_likes}</span></div>
           ${genreBar}
            <div class="stat-row"><span class="label">热门艺术家 Top Artists</span><span class="value" style="font-size:11px">${topArtists}</span></div>`;
    },

    renderTaste(stats) {
        const el = document.getElementById("taste-content");
        let distBar = '<div class="dist-bar">';
        for (const [genre, val] of Object.entries(stats.ema_distribution)) {
            if (val > 0.01) {
                distBar += `<div style="width:${val * 100}%;background:${this.genreColor(genre)}" title="${genre}: ${(val*100).toFixed(1)}%"></div>`;
            }
        }
        distBar += "</div>";
        let alert = "";
       if (stats.shift_confirmed) {
            alert = `<div class="shift-alert">检测到品味转变! Taste Shift Detected! (次数 count: ${stats.shift_count})</div>`;
       }
       el.innerHTML = `
           ${alert}
            <div class="stat-row"><span class="label">总动作 Total Actions</span><span class="value">${stats.total_actions}</span></div>
            <div class="stat-row"><span class="label">KL散度 KL Divergence</span><span class="value">${stats.kl_divergence}</span></div>
            <div class="stat-row"><span class="label">阈值 Threshold</span><span class="value">${stats.threshold}</span></div>
            <div class="stat-row"><span class="label">检测 Detection</span><span class="value">${stats.enabled ? "激活 Active" : "预热中 Warming up"}</span></div>
            <div class="stat-row"><span class="label">连续 Streak</span><span class="value">${stats.streak}</span></div>
            <div class="stat-row"><span class="label">转变次数 Shifts</span><span class="value">${stats.shift_count}</span></div>
            <div style="margin-top:6px;font-size:11px;color:var(--text-dim)">EMA分布 Distribution:</div>
           ${distBar}`;
    },

    startAutoPlay() {
        if (this.state.autoPlaying) {
            this.stopAutoPlay();
            return;
        }
        this.state.autoPlaying = true;
       const btn = document.getElementById("btn-autoplay-seq");
        btn.textContent = "停止 Stop";
       btn.classList.add("active");
        const tick = async () => {
            if (!this.state.autoPlaying) return;
            const data = await this.api("/api/playlist/next", "POST");
            if (!data.current) {
                this.stopAutoPlay();
                await this.refreshPlaylist();
                return;
            }
            await this.refreshPlaylist();
            await this.refreshAnalytics();
            await this.refreshTaste();
            this.state.autoPlayTimer = setTimeout(tick, 1200);
        };
        tick();
    },

    stopAutoPlay() {
        this.state.autoPlaying = false;
        if (this.state.autoPlayTimer) {
            clearTimeout(this.state.autoPlayTimer);
            this.state.autoPlayTimer = null;
        }
        const btn = document.getElementById("btn-autoplay-seq");
       if (btn) {
            btn.textContent = "自动播放 Auto Play";
           btn.classList.remove("active");
       }
    },

    async moveSong(songId, toIndex) {
        await this.api("/api/playlist/move", "POST", { song_id: songId, to_index: toIndex });
        await this.refreshPlaylist();
        await this.refreshAnalytics();
    },

    wireEvents() {
        document.getElementById("btn-next").addEventListener("click", async () => {
            await this.api("/api/playlist/next", "POST");
            await this.refreshPlaylist();
            await this.refreshAnalytics();
            await this.refreshTaste();
        });
        document.getElementById("btn-prev").addEventListener("click", async () => {
            await this.api("/api/playlist/previous", "POST");
            await this.refreshPlaylist();
            await this.refreshAnalytics();
            await this.refreshTaste();
        });
        document.getElementById("btn-like").addEventListener("click", async () => {
            if (!this.state.current) return;
            await this.api("/api/playlist/like", "POST", { song_id: this.state.current.song_id });
            await this.refreshPlaylist();
            await this.refreshAutoplay();
            await this.refreshTaste();
        });
        document.getElementById("btn-shuffle").addEventListener("click", async () => {
            await this.api("/api/playlist/shuffle", "POST");
            await this.refreshPlaylist();
        });
        document.getElementById("btn-smart-shuffle").addEventListener("click", async () => {
            const data = await this.api("/api/playlist/smart-shuffle", "POST");
            if (data.warning) alert(data.warning);
            await this.refreshPlaylist();
        });
        document.getElementById("btn-autoplay-next").addEventListener("click", async () => {
            await this.api("/api/autoplay/next", "POST");
            await this.refreshAutoplay();
            await this.refreshPlaylist();
            await this.refreshTaste();
        });
        document.getElementById("btn-refresh-recs").addEventListener("click", () => this.refreshRecommendations());
        document.getElementById("btn-autoplay-seq").addEventListener("click", () => this.startAutoPlay());
       document.getElementById("btn-reload").addEventListener("click", async () => {
           await this.api("/api/reload", "POST");
           location.reload();
       });
       // CSV import button: trigger hidden file input
       const importBtn = document.getElementById("btn-import");
       const fileInput = document.getElementById("csv-file-input");
       importBtn.addEventListener("click", () => fileInput.click());
       fileInput.addEventListener("change", async () => {
           if (!fileInput.files.length) return;
           const formData = new FormData();
           formData.append("file", fileInput.files[0]);
           try {
               const res = await fetch("/api/import-csv", { method: "POST", body: formData });
               const data = await res.json();
               if (!res.ok) throw new Error(data.error || "Import failed");
               location.reload();
           } catch (err) {
               alert("导入失败: " + err.message);
               fileInput.value = "";
           }
       });
        document.getElementById("btn-simulate").addEventListener("click", async () => {
            const fromG = document.getElementById("sim-from").value;
            const toG = document.getElementById("sim-to").value;
           const data = await this.api("/api/taste/simulate", "POST", { from_genre: fromG, to_genre: toG, n: 40 });
            alert(`在第 #${data.shift_at || "从未 never"} 次动作检测到转变\nShift detected at action #${data.shift_at || "never"}\n总转变次数 Total shifts: ${data.shift_count}`);
        });
        document.getElementById("btn-search").addEventListener("click", () => Search.search());
        document.getElementById("search-input").addEventListener("keypress", (e) => {
            if (e.key === "Enter") Search.search();
        });
        document.getElementById("genre-filter").addEventListener("change", () => Search.search());
        document.getElementById("artist-filter").addEventListener("keypress", (e) => {
            if (e.key === "Enter") Search.search();
        });
        document.getElementById("btn-range-search").addEventListener("click", () => Search.rangeSearch());
        const addInput = document.getElementById("add-song-input");
        addInput.addEventListener("input", () => Search.quickSearch(addInput.value));
    },
};

document.addEventListener("DOMContentLoaded", () => App.init());
