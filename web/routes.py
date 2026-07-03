"""All API routes and page rendering for the music streaming engine."""

import time
import tempfile
import csv
import os

from flask import Flask, render_template, request, jsonify

from data_structures.song import Song, Genre
from data_structures.doubly_linked_list import Playlist
from data_structures.bst import SongCatalogue
from data_structures.heap import AutoplayQueue
from algorithms.analytics import playlist_stats
from algorithms.smart_shuffle import smart_shuffle
from algorithms.recommendation import recommend
from algorithms.taste_shift import TasteShiftDetector, simulate_shift
from data.data_loader import load_into_all_structures, ensure_dataset


class AppState:
    """Holds the running application state (singleton per process)."""

    def __init__(self):
        self.playlist = None
        self.catalogue = None
        self.autoplay = None
        self.all_songs = None
        self.taste = TasteShiftDetector(min_samples=10, confirm_streak=2)
        self.now = time.time()
        self._loaded = False

    def load(self):
        if self._loaded:
            return
        csv_path = ensure_dataset("songs_dataset.csv", count=25, seed=42)
        self.playlist, self.catalogue, self.autoplay, self.all_songs = load_into_all_structures(csv_path)
        self.autoplay.now = self.now
        self._loaded = True

    def reload(self):
        self._loaded = False
        self.load()

    def load_from(self, filepath):
        """Load songs from a specific CSV file (CLI import or web upload).

        Bypasses the default-dataset logic and marks the state as loaded
        so subsequent ``load()`` calls don't overwrite the imported data.
        """
        self.playlist, self.catalogue, self.autoplay, self.all_songs = load_into_all_structures(filepath)
        self.autoplay.now = self.now
        self._loaded = True

    def song_to_dict(self, song):
        if song is None:
            return None
        return song.to_dict()


_state = AppState()


def register_routes(app):
    @app.route("/")
    def index():
        _state.load()
        return render_template("index.html")

    @app.route("/api/playlist", methods=["GET"])
    def get_playlist():
        _state.load()
        return jsonify({
            "playlist": _state.playlist.display(),
            "current": _state.song_to_dict(_state.playlist.current_song()),
            "current_index": _state.playlist.current_index(),
            "size": len(_state.playlist),
        })

    @app.route("/api/playlist/add", methods=["POST"])
    def playlist_add():
        _state.load()
        data = request.get_json()
        song_id = data.get("song_id")
        song = _state.catalogue.find_by_id(song_id)
        if song is None:
            return jsonify({"error": "Song not found in catalogue"}), 404
        if not _state.playlist.add_song(song):
            return jsonify({"error": "Song already in playlist"}), 409
        return jsonify({"ok": True, "playlist": _state.playlist.display()})

    @app.route("/api/playlist/remove", methods=["POST"])
    def playlist_remove():
        _state.load()
        data = request.get_json()
        song_id = data.get("song_id")
        if not _state.playlist.remove_song(song_id):
            return jsonify({"error": "Song not in playlist"}), 404
        return jsonify({"ok": True, "playlist": _state.playlist.display()})

    @app.route("/api/playlist/next", methods=["POST"])
    def playlist_next():
        _state.load()
        song = _state.playlist.play_next()
        if song:
            song.play_count += 1
            song.last_played = time.time()
            _state.taste.record_action(song.genre)
        return jsonify({
            "current": _state.song_to_dict(song),
            "current_index": _state.playlist.current_index(),
        })

    @app.route("/api/playlist/previous", methods=["POST"])
    def playlist_previous():
        _state.load()
        song = _state.playlist.play_previous()
        if song:
            song.play_count += 1
            song.last_played = time.time()
            _state.taste.record_action(song.genre)
        return jsonify({
            "current": _state.song_to_dict(song),
            "current_index": _state.playlist.current_index(),
        })

    @app.route("/api/playlist/goto", methods=["POST"])
    def playlist_goto():
        _state.load()
        data = request.get_json()
        index = int(data.get("index", 0))
        song = _state.playlist.move_to_position(index)
        return jsonify({
            "current": _state.song_to_dict(song),
            "current_index": _state.playlist.current_index(),
        })

    @app.route("/api/playlist/shuffle", methods=["POST"])
    def playlist_shuffle():
        _state.load()
        import random
        _state.playlist.shuffle(random.Random())
        return jsonify({"ok": True, "playlist": _state.playlist.display()})

    @app.route("/api/playlist/smart-shuffle", methods=["POST"])
    def playlist_smart_shuffle():
       _state.load()
       result, warning = smart_shuffle(_state.playlist)
       return jsonify({
           "ok": True,
           "warning": warning,
           "playlist": _state.playlist.display(),
       })

    @app.route("/api/playlist/move", methods=["POST"])
    def playlist_move():
        _state.load()
        data = request.get_json()
        song_id = data.get("song_id")
        to_index = int(data.get("to_index", 0))
        if not _state.playlist.move_song(song_id, to_index):
            return jsonify({"error": "Move failed (song not found or index out of range)"}), 400
        return jsonify({"ok": True, "playlist": _state.playlist.display()})

    @app.route("/api/playlist/like", methods=["POST"])
    def playlist_like():
        _state.load()
        data = request.get_json()
        song_id = data.get("song_id")
        song = _state.playlist.get_song(song_id)
        if song is None:
            return jsonify({"error": "Not in playlist"}), 404
        song.liked = not song.liked
        if song.liked:
            song.like_count += 1
            _state.taste.record_action(song.genre)
        else:
            song.like_count = max(0, song.like_count - 1)
        if song.song_id in _state.autoplay:
            _state.autoplay.update_score(song, now=time.time())
        return jsonify({"ok": True, "song": _state.song_to_dict(song)})

    @app.route("/api/playlist/analytics", methods=["GET"])
    def playlist_analytics():
        _state.load()
        stats = playlist_stats(_state.playlist)
        return jsonify(stats)

    @app.route("/api/catalogue/search", methods=["GET"])
    def catalogue_search():
        _state.load()
        query = request.args.get("q", "")
        if not query:
            return jsonify({"results": [], "total": 0})
        exact = _state.catalogue.search(query)
        results = []
        if exact:
            results.append(exact.to_dict())
        low = query
        high = query + "\uffff"
        range_results = _state.catalogue.range_search(low, high)
        seen = set(r.song_id for r in results)
        for s in range_results:
            if s.song_id not in seen:
                results.append(s.to_dict())
                seen.add(s.song_id)
        return jsonify({"results": results, "total": len(results)})

    @app.route("/api/catalogue/by-artist", methods=["GET"])
    def catalogue_by_artist():
        _state.load()
        artist = request.args.get("artist", "")
        results = _state.catalogue.find_by_artist(artist)
        return jsonify({"results": [s.to_dict() for s in results]})

    @app.route("/api/catalogue/by-genre", methods=["GET"])
    def catalogue_by_genre():
        _state.load()
        genre = request.args.get("genre", "")
        results = _state.catalogue.find_by_genre(genre)
        return jsonify({"results": [s.to_dict() for s in results]})

    @app.route("/api/catalogue/all", methods=["GET"])
    def catalogue_all():
        _state.load()
        songs = _state.catalogue.in_order_traversal()
        return jsonify({"results": [s.to_dict() for s in songs], "total": len(songs)})

    @app.route("/api/catalogue/range", methods=["GET"])
    def catalogue_range():
        _state.load()
        low = request.args.get("low", "A")
        high = request.args.get("high", "Z")
        results = _state.catalogue.range_search(low, high)
        return jsonify({"results": [s.to_dict() for s in results], "total": len(results)})

    @app.route("/api/catalogue/genres", methods=["GET"])
    def catalogue_genres():
        return jsonify({"genres": [g.name for g in Genre]})

    @app.route("/api/autoplay", methods=["GET"])
    def get_autoplay():
        _state.load()
        return jsonify({
            "queue": _state.autoplay.to_heap_array(),
            "size": len(_state.autoplay),
            "peek": _state.song_to_dict(_state.autoplay.peek()),
        })

    @app.route("/api/autoplay/next", methods=["POST"])
    def autoplay_next():
        _state.load()
        song = _state.autoplay.next_autoplay()
        if song:
            _state.playlist.add_song(song)
            song.play_count += 1
            song.last_played = time.time()
            _state.taste.record_action(song.genre)
        return jsonify({
            "song": _state.song_to_dict(song),
            "queue": _state.autoplay.to_heap_array(),
            "size": len(_state.autoplay),
        })

    @app.route("/api/autoplay/add", methods=["POST"])
    def autoplay_add():
        _state.load()
        data = request.get_json()
        song_id = data.get("song_id")
        song = _state.catalogue.find_by_id(song_id)
        if song is None:
            return jsonify({"error": "Not found"}), 404
        _state.autoplay.add_to_autoplay(song)
        return jsonify({"ok": True, "queue": _state.autoplay.to_heap_array()})

    @app.route("/api/autoplay/remove", methods=["POST"])
    def autoplay_remove():
        _state.load()
        data = request.get_json()
        song_id = data.get("song_id")
        _state.autoplay.remove_from_autoplay(song_id)
        return jsonify({"ok": True, "queue": _state.autoplay.to_heap_array()})

    @app.route("/api/recommend", methods=["GET"])
    def get_recommendations():
        _state.load()
        top_n = int(request.args.get("n", 5))
        recs = recommend(_state.playlist, _state.catalogue, top_n=top_n, now=time.time())
        return jsonify({"recommendations": [s.to_dict() for s in recs]})

    @app.route("/api/taste/stats", methods=["GET"])
    def taste_stats():
        _state.load()
        return jsonify(_state.taste.get_stats())

    @app.route("/api/taste/action", methods=["POST"])
    def taste_action():
        _state.load()
        data = request.get_json()
        genre = data.get("genre", "ROCK")
        result = _state.taste.record_action(genre)
        return jsonify(result)

    @app.route("/api/taste/simulate", methods=["POST"])
    def taste_simulate():
        _state.load()
        data = request.get_json()
        from_genre = data.get("from_genre", "ROCK")
        to_genre = data.get("to_genre", "JAZZ")
        n = int(data.get("n", 30))
        det = TasteShiftDetector(min_samples=10, confirm_streak=2)
        idx = simulate_shift(det, Genre.from_string(from_genre), Genre.from_string(to_genre), n)
        return jsonify({
            "shift_at": idx,
            "shift_count": det.shift_count,
            "stats": det.get_stats(),
        })

    @app.route("/api/taste/reset", methods=["POST"])
    def taste_reset():
        _state.load()
        _state.taste = TasteShiftDetector(min_samples=10, confirm_streak=2)
        return jsonify({"ok": True})

    @app.route("/api/reload", methods=["POST"])
    def reload_data():
        _state.reload()
        return jsonify({"ok": True, "size": len(_state.playlist)})

    @app.route("/api/import-csv", methods=["POST"])
    def import_csv():
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400
        if not file.filename.lower().endswith(".csv"):
            return jsonify({"error": "Only .csv files are accepted"}), 400

        # Save uploaded file to a temp location, validate, then load
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        try:
            file.save(tmp.name)
            tmp.close()
            _state.load_from(tmp.name)
            return jsonify({"ok": True, "size": len(_state.playlist), "filename": file.filename})
        finally:
            os.unlink(tmp.name)
