/* Recommendation card display. */

const Recommendations = {
    render(recs) {
        const el = document.getElementById("recommendations-container");
       if (!recs || recs.length === 0) {
            el.innerHTML = '<p class="placeholder">暂无推荐。请先向播放列表添加歌曲，或目录中所有歌曲已在播放列表中。No recommendations available.</p>';
           return;
       }
       el.innerHTML = recs.map(s => {
           const color = App.genreColor(s.genre);
           const dur = s.duration_seconds;
           const mins = Math.floor(dur / 60);
           const secs = String(dur % 60).padStart(2, "0");
           return `
               <div class="rec-card" data-id="${s.song_id}">
                   <div class="rc-title">${s.title}</div>
                   <div class="rc-artist">${s.artist}</div>
                   <div class="rc-meta">
                       <span class="genre-tag" style="background:${color}33;color:${color};font-size:9px;padding:1px 5px;border-radius:3px">${s.genre}</span>
                        ${mins}:${secs} | 点赞 Likes: ${s.like_count}
                   </div>
                   <div class="rc-add">
                        <button class="btn btn-sm" onclick="Recommendations.add('${s.song_id}')">加入播放列表 Add</button>
                   </div>
                </div>`;
        }).join("");
    },

    async add(songId) {
        try {
            await App.api("/api/playlist/add", "POST", { song_id: songId });
            await App.refreshPlaylist();
            await App.refreshRecommendations();
            await App.refreshAnalytics();
        } catch (e) {
            alert(e.message);
        }
    },
};
