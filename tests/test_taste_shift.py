

import unittest
from data_structures.song import Genre
from algorithms.taste_shift import TasteShiftDetector, simulate_shift


class TestTasteShift(unittest.TestCase):
    def test_initial_state(self):
        print("\n>>> TasteShiftDetector: 初始状态")
        det = TasteShiftDetector()
        stats = det.get_stats()
        print(f"    total_actions: {stats['total_actions']}")
        print(f"    shift_confirmed: {stats['shift_confirmed']}")
        print(f"    enabled: {stats['enabled']}")
        self.assertEqual(stats["total_actions"], 0)
        self.assertFalse(stats["shift_confirmed"])

    def test_record_action(self):
        print("\n>>> record_action: 记录单次播放行为")
        det = TasteShiftDetector(min_samples=5)
        result = det.record_action(Genre.ROCK)
        print(f"    记录 ROCK 后:")
        print(f"      total_actions = {result['total_actions']}")
        print(f"      enabled = {result['enabled']}")
        self.assertEqual(result["total_actions"], 1)
        self.assertFalse(result["enabled"])

    def test_enables_after_min_samples(self):
        print("\n>>> record_action: 达到 min_samples 后启用检测")
        det = TasteShiftDetector(min_samples=5)
        for i in range(4):
            det.record_action(Genre.ROCK)
        print(f"    记录4次后 enabled = {det.get_stats()['enabled']} (期望 False)")
        result = det.record_action(Genre.ROCK)
        print(f"    记录5次后 enabled = {result['enabled']} (期望 True)")
        self.assertTrue(result["enabled"])

    def test_no_shift_stable_taste(self):
        print("\n>>> 稳定口味: 持续播放同一流派不应检测到偏移")
        det = TasteShiftDetector(min_samples=20, confirm_streak=5)
        for i in range(80):
            result = det.record_action(Genre.ROCK)
        print(f"    80次ROCK后:")
        print(f"      kl_divergence = {result['kl_divergence']}")
        print(f"      shift_confirmed = {result['shift_confirmed']}")
        self.assertLess(result["kl_divergence"], 0.3)
        self.assertFalse(result["shift_confirmed"])

    def test_detects_shift(self):
        print("\n>>> detect_shift: 从 ROCK 切换到 JAZZ 应检测到偏移")
        det = TasteShiftDetector(min_samples=10, threshold=0.1, confirm_streak=2)
        idx = simulate_shift(det, Genre.ROCK, Genre.JAZZ, 40)
        stats = det.get_stats()
        print(f"    偏移在第 {idx} 次操作时被确认")
        print(f"    shift_count = {det.shift_count}")
        print(f"    kl_divergence = {stats['kl_divergence']}")
        self.assertGreater(idx, 0)
        self.assertGreater(det.shift_count, 0)

    def test_kl_divergence_zero_identical(self):
        print("\n>>> _symmetric_kl: 相同分布的 KL 散度应为 0")
        det = TasteShiftDetector()
        dist = det._uniform_distribution()
        kl = det._symmetric_kl(dist, dist)
        print(f"    KL(uniform, uniform) = {kl}")
        self.assertAlmostEqual(kl, 0.0, places=5)

    def test_kl_divergence_positive_different(self):
        print("\n>>> _symmetric_kl: 不同分布的 KL 散度应 > 0")
        det = TasteShiftDetector()
        d1 = det._uniform_distribution()
        d2 = det._uniform_distribution()
        d2[Genre.ROCK] = 0.9
        d2[Genre.POP] = 0.1 / (len(Genre) - 1)
        kl = det._symmetric_kl(d1, d2)
        print(f"    KL(uniform, rock-heavy) = {kl:.4f}")
        self.assertGreater(kl, 0)

    def test_get_stats(self):
        print("\n>>> get_stats: 获取检测器完整统计信息")
        det = TasteShiftDetector(min_samples=5)
        det.record_action(Genre.POP)
        det.record_action(Genre.JAZZ)
        stats = det.get_stats()
        print(f"    total_actions: {stats['total_actions']}")
        print(f"    threshold: {stats['threshold']}")
        print(f"    ema_distribution (前3): {dict(list(stats['ema_distribution'].items())[:3])}")
        print(f"    recent_distribution (前3): {dict(list(stats['recent_distribution'].items())[:3])}")
        self.assertEqual(stats["total_actions"], 2)
        self.assertEqual(stats["threshold"], 0.3)

    def test_step_adjustment(self):
        print("\n>>> get_step_adjustment: 偏移确认后的分数调整值")
        det = TasteShiftDetector(min_samples=5, confirm_streak=1, threshold=0.01)
        print(f"    初始 adjustment = {det.get_step_adjustment()} (期望 0.0)")
        simulate_shift(det, Genre.ROCK, Genre.JAZZ, 20)
        stats = det.get_stats()
        print(f"    shift_confirmed = {stats['shift_confirmed']}")
        if stats["shift_confirmed"]:
            print(f"    adjustment = {det.get_step_adjustment()} (>0)")
            self.assertGreater(det.get_step_adjustment(), 0)

    def test_reset_shift(self):
        print("\n>>> reset_shift: 重置偏移确认状态")
        det = TasteShiftDetector()
        det._shift_confirmed = True
        print(f"    重置前 shift_confirmed = {det.get_stats()['shift_confirmed']}")
        det.reset_shift()
        print(f"    重置后 shift_confirmed = {det.get_stats()['shift_confirmed']}")
        self.assertFalse(det.get_stats()["shift_confirmed"])

    def test_record_many(self):
        print("\n>>> record_many: 批量记录行为")
        det = TasteShiftDetector(min_samples=3)
        results = det.record_many([Genre.ROCK, Genre.POP, Genre.JAZZ])
        for i, r in enumerate(results):
            print(f"    第{i+1}次: enabled={r['enabled']}")
        self.assertEqual(len(results), 3)
        self.assertTrue(results[-1]["enabled"])

    def test_string_genre(self):
        print("\n>>> record_action: 传入字符串流派")
        det = TasteShiftDetector(min_samples=3)
        det.record_action("ROCK")
        det.record_action("POP")
        det.record_action("JAZZ")
        stats = det.get_stats()
        print(f"    记录 'ROCK','POP','JAZZ' 后 total_actions = {stats['total_actions']}")
        self.assertEqual(stats["total_actions"], 3)


if __name__ == "__main__":
    unittest.main()
