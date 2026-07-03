

import unittest
from data_structures.song import Song, Genre
from data_structures.doubly_linked_list import Playlist
from algorithms.analytics import (playlist_stats, top_genres, top_artists,
                                   average_duration, dominant_genre,
                                   artist_diversity, genre_diversity)


def make_song(sid, genre=Genre.ROCK, artist="A", duration=200):
    return Song(sid, f"Title{sid}", artist, "Album", genre, duration, 0, 0)


class TestAnalytics(unittest.TestCase):
    def setUp(self):
        self.pl = Playlist()
        self.pl.add_song(make_song("1", Genre.ROCK, "Beatles", 300))
        self.pl.add_song(make_song("2", Genre.ROCK, "Beatles", 200))
        self.pl.add_song(make_song("3", Genre.POP, "Adele", 250))
        self.pl.add_song(make_song("4", Genre.JAZZ, "Miles", 180))
        print(f"\n    播放列表: {[(s.song_id, s.genre.name, s.artist, s.duration_seconds) for s in self.pl]}")

    def test_playlist_stats(self):
        print("\n>>> playlist_stats: 播放列表综合统计")
        stats = playlist_stats(self.pl)
        for k, v in stats.items():
            print(f"    {k}: {v}")
        self.assertEqual(stats["total_songs"], 4)
        self.assertEqual(stats["total_duration"], 930)
        self.assertAlmostEqual(stats["avg_duration"], 232.5)

    def test_empty_playlist_stats(self):
        print("\n>>> playlist_stats: 空播放列表统计")
        stats = playlist_stats(Playlist())
        print(f"    {stats}")
        self.assertEqual(stats["total_songs"], 0)

    def test_top_genres(self):
        print("\n>>> top_genres: 流派排行 Top-N")
        result = top_genres(self.pl, 2)
        print(f"    top_genres(2) = {result}")
        self.assertEqual(result[0][0], "ROCK")
        self.assertEqual(result[0][1], 2)

    def test_top_artists(self):
        print("\n>>> top_artists: 艺人排行 Top-N")
        result = top_artists(self.pl, 2)
        print(f"    top_artists(2) = {result}")
        self.assertEqual(result[0][0], "Beatles")
        self.assertEqual(result[0][1], 2)

    def test_average_duration(self):
        print("\n>>> average_duration: 平均时长")
        avg = average_duration(self.pl)
        print(f"    平均时长 = {avg:.1f}s (期望 232.5)")
        self.assertAlmostEqual(avg, 232.5)

    def test_average_duration_empty(self):
        print("\n>>> average_duration: 空列表平均时长")
        avg = average_duration(Playlist())
        print(f"    平均时长 = {avg} (期望 0)")
        self.assertEqual(avg, 0)

    def test_dominant_genre(self):
        print("\n>>> dominant_genre: 主导流派")
        g = dominant_genre(self.pl)
        print(f"    主导流派 = {g} (期望 ROCK)")
        self.assertEqual(g, "ROCK")

    def test_dominant_genre_empty(self):
        print("\n>>> dominant_genre: 空列表主导流派")
        g = dominant_genre(Playlist())
        print(f"    主导流派 = {g} (期望 None)")
        self.assertIsNone(g)

    def test_artist_diversity(self):
        print("\n>>> artist_diversity: 艺人多样性 (去重数量)")
        d = artist_diversity(self.pl)
        print(f"    艺人数 = {d} (期望 3: Beatles, Adele, Miles)")
        self.assertEqual(d, 3)

    def test_genre_diversity(self):
        print("\n>>> genre_diversity: 流派多样性 (去重数量)")
        d = genre_diversity(self.pl)
        print(f"    流派数 = {d} (期望 3: ROCK, POP, JAZZ)")
        self.assertEqual(d, 3)


if __name__ == "__main__":
    unittest.main()
