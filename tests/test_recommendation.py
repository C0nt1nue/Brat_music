

import unittest
from data_structures.song import Song, Genre
from data_structures.doubly_linked_list import Playlist
from data_structures.bst import SongCatalogue
from algorithms.recommendation import recommend, recommend_for_genre


def make_song(sid, title, artist, genre=Genre.ROCK, likes=0, plays=0):
    return Song(sid, title, artist, "Album", genre, 200, plays, likes)


class TestRecommendation(unittest.TestCase):
    def setUp(self):
        self.cat = SongCatalogue()
        for i in range(1, 11):
            genre = Genre.ROCK if i <= 5 else Genre.POP
            self.cat.insert(make_song(f"c{i}", f"Song{i:02d}", f"Artist{i}",
                                       genre, likes=i * 10, plays=i * 5))
        self.pl = Playlist()
        self.pl.add_song(make_song("c1", "Song01", "Artist1", Genre.ROCK, 10, 5))
        self.pl.add_song(make_song("c2", "Song02", "Artist2", Genre.ROCK, 20, 10))
        print(f"\n    播放列表: {[s.song_id for s in self.pl]} (ROCK 偏好)")
        print(f"    曲库: {len(self.cat)} 首 (c1-c5=ROCK, c6-c10=POP)")

    def test_recommend_returns_songs(self):
        print("\n>>> recommend: 基于播放列表推荐歌曲")
        recs = recommend(self.pl, self.cat, top_n=3)
        print(f"    推荐 {len(recs)} 首:")
        for r in recs:
            print(f"      {r.song_id} - {r.title} (genre={r.genre.name}, likes={r.like_count})")
        self.assertGreater(len(recs), 0)
        self.assertLessEqual(len(recs), 3)

    def test_recommend_excludes_playlist(self):
        print("\n>>> recommend: 推荐结果排除已在播放列表中的歌曲")
        recs = recommend(self.pl, self.cat, top_n=10)
        rec_ids = set(r.song_id for r in recs)
        print(f"    推荐ID: {sorted(rec_ids)}")
        print(f"    播放列表ID: c1, c2")
        print(f"    排除成功? {'c1' not in rec_ids and 'c2' not in rec_ids}")
        self.assertNotIn("c1", rec_ids)
        self.assertNotIn("c2", rec_ids)

    def test_recommend_empty_playlist(self):
        print("\n>>> recommend: 空播放列表 -> 推荐曲库中最受欢迎的歌曲")
        pl = Playlist()
        recs = recommend(pl, self.cat, top_n=3)
        print(f"    推荐 {len(recs)} 首:")
        for r in recs:
            print(f"      {r.song_id} - {r.title} (likes={r.like_count})")
        self.assertEqual(len(recs), 3)

    def test_recommend_empty_catalogue(self):
        print("\n>>> recommend: 空曲库 -> 返回空列表")
        cat = SongCatalogue()
        recs = recommend(self.pl, cat, top_n=3)
        print(f"    推荐结果: {recs}")
        self.assertEqual(recs, [])

    def test_recommend_top_n(self):
        print("\n>>> recommend: 限制推荐数量 top_n=2")
        recs = recommend(self.pl, self.cat, top_n=2)
        print(f"    返回 {len(recs)} 首 (期望 <= 2)")
        self.assertLessEqual(len(recs), 2)

    def test_recommend_for_genre(self):
        print("\n>>> recommend_for_genre: 按指定流派推荐 (POP)")
        recs = recommend_for_genre(self.pl, self.cat, Genre.POP, top_n=3)
        print(f"    推荐 {len(recs)} 首POP歌曲:")
        for r in recs:
            print(f"      {r.song_id} - {r.title} (genre={r.genre.name}, likes={r.like_count})")
        for r in recs:
            self.assertEqual(r.genre, Genre.POP)

    def test_recommend_sorted_by_score(self):
        print("\n>>> recommend: 推荐结果按分数降序排列")
        recs = recommend(self.pl, self.cat, top_n=5)
        print(f"    推荐顺序 (按 likes 降序):")
        for r in recs:
            print(f"      {r.song_id} - likes={r.like_count}")
        if len(recs) >= 2:
            print(f"    首位 likes={recs[0].like_count} >= 末位 likes={recs[-1].like_count}? "
                  f"{recs[0].like_count >= recs[-1].like_count}")
            self.assertGreaterEqual(recs[0].like_count, recs[-1].like_count)


if __name__ == "__main__":
    unittest.main()
