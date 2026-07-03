

import unittest
import random
from data_structures.song import Song, Genre
from data_structures.doubly_linked_list import Playlist
from algorithms.smart_shuffle import (smart_shuffle, has_consecutive_duplicates,
                                       consecutive_duplicate_count)


def make_song(sid, artist="A", genre=Genre.ROCK):
    return Song(sid, f"Title{sid}", artist, "Album", genre, 200, 0, 0)


class TestSmartShuffle(unittest.TestCase):
    def test_shuffles_in_place(self):
        print("\n>>> smart_shuffle: 洗牌并保持歌曲集合不变")
        pl = Playlist()
        genres = [Genre.ROCK, Genre.POP, Genre.JAZZ, Genre.CLASSICAL, Genre.HIP_HOP]
        songs = [make_song(str(i), f"Artist{i}", genres[i % 5]) for i in range(1, 11)]
        for s in songs:
            pl.add_song(s)
        before = [s.song_id for s in pl]
        print(f"    洗牌前: {before}")
        rng = random.Random(42)
        result, warn = smart_shuffle(pl, rng)
        after = [s.song_id for s in result]
        print(f"    洗牌后: {after}")
        print(f"    集合不变? {set(after) == set(before)}")
        print(f"    警告: {warn}")
        self.assertEqual(len(result), 10)
        self.assertEqual(set(after), set(before))

    def test_reduces_consecutive_duplicates(self):
        print("\n>>> smart_shuffle: 减少相邻重复 (同艺人/同流派)")
        pl = Playlist()
        for i in range(1, 11):
            genre = Genre.ROCK if i <= 5 else Genre.JAZZ
            artist = "BandA" if i <= 5 else "BandB"
            pl.add_song(make_song(str(i), artist, genre))
        print(f"    洗牌前: {[(s.song_id, s.artist, s.genre.name) for s in pl]}")
        rng = random.Random(42)
        result, warn = smart_shuffle(pl, rng)
        print(f"    洗牌后: {[(s.song_id, s.artist, s.genre.name) for s in result]}")
        artist_dups = consecutive_duplicate_count(result, "artist")
        genre_dups = consecutive_duplicate_count(result, "genre")
        print(f"    相邻艺人重复数: {artist_dups} (期望 0)")
        print(f"    相邻流派重复数: {genre_dups}")
        self.assertEqual(artist_dups, 0)

    def test_degenerate_warning(self):
        print("\n>>> smart_shuffle: 退化场景警告 (>50% 同艺人)")
        pl = Playlist()
        for i in range(1, 11):
            pl.add_song(make_song(str(i), "SameArtist", Genre.ROCK))
        print(f"    10首歌全部来自 SameArtist")
        rng = random.Random(42)
        result, warn = smart_shuffle(pl, rng)
        print(f"    警告: {warn}")
        print(f"    结果: {[s.song_id for s in result]}")
        self.assertIsNotNone(warn)
        self.assertIn("Degenerate", warn)

    def test_single_song(self):
        print("\n>>> smart_shuffle: 单首歌曲")
        pl = Playlist()
        pl.add_song(make_song("1"))
        result, warn = smart_shuffle(pl)
        print(f"    结果: {[s.song_id for s in result]}, 警告: {warn}")
        self.assertEqual(len(result), 1)
        self.assertIsNone(warn)

    def test_empty_playlist(self):
        print("\n>>> smart_shuffle: 空播放列表")
        result, warn = smart_shuffle(Playlist())
        print(f"    结果: {result}, 警告: {warn}")
        self.assertEqual(result, [])
        self.assertIsNone(warn)

    def test_has_consecutive_duplicates(self):
        print("\n>>> has_consecutive_duplicates: 检测相邻重复")
        songs = [make_song("1", "A"), make_song("2", "A"), make_song("3", "B")]
        print(f"    [A, A, B] -> {has_consecutive_duplicates(songs, 'artist')}")
        songs2 = [make_song("1", "A"), make_song("2", "B"), make_song("3", "C")]
        print(f"    [A, B, C] -> {has_consecutive_duplicates(songs2, 'artist')}")
        self.assertTrue(has_consecutive_duplicates(songs, "artist"))
        self.assertFalse(has_consecutive_duplicates(songs2, "artist"))

    def test_consecutive_duplicate_count(self):
        print("\n>>> consecutive_duplicate_count: 统计相邻重复对数")
        songs = [make_song("1", "A"), make_song("2", "A"), make_song("3", "A")]
        count = consecutive_duplicate_count(songs, "artist")
        print(f"    [A, A, A] -> {count} 对相邻重复 (期望 2)")
        self.assertEqual(count, 2)


if __name__ == "__main__":
    unittest.main()
