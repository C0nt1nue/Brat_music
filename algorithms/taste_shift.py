"""Taste shift detection using EMA-smoothed genre distributions and KL divergence.

Tracks the user's genre distribution over time with an exponential moving
average. When the symmetric KL divergence between the recent distribution and
the EMA exceeds a threshold, a taste shift is flagged.
"""

import math
from collections import deque, Counter

from data_structures.song import Genre

ALL_GENRES = [g for g in Genre]


class TasteShiftDetector:
    """Detects shifts in user taste (genre preferences) over time.

    Parameters:
        alpha: EMA smoothing factor (0 < alpha <= 1)
        threshold: KL divergence threshold for triggering a shift
        min_samples: minimum actions before detection is enabled
        confirm_streak: consecutive triggers needed to confirm a shift
        step_adjustment: per-step score adjustment on confirmed shift
    """

    def __init__(self, alpha=0.1, threshold=0.3, min_samples=20,
                 confirm_streak=3, step_adjustment=0.05):
        self.alpha = alpha
        self.threshold = threshold
        self.min_samples = min_samples
        self.confirm_streak = confirm_streak
        self.step_adjustment = step_adjustment
        self._ema = self._uniform_distribution()
        self._window = deque()
        self._window_size = min_samples
        self._total_actions = 0
        self._streak = 0
        self._shift_confirmed = False
        self._shift_count = 0
        self._last_kl = 0.0
        self._history = []

    def _uniform_distribution(self):
        n = len(ALL_GENRES)
        return {g: 1.0 / n for g in ALL_GENRES}

    def _genre_to_distribution(self, genres):
        """Convert a list of Genre objects to a normalized distribution."""
        counts = Counter(genres)
        total = sum(counts.values())
        if total == 0:
            return self._uniform_distribution()
        dist = {}
        for g in ALL_GENRES:
            dist[g] = counts.get(g, 0) / total
        return dist

    def _symmetric_kl(self, p, q):
        """Symmetric KL divergence: (KL(p||q) + KL(q||p)) / 2.

        Both distributions are Laplace-smoothed with a small epsilon
        to avoid infinite divergence when supports do not overlap.
        """
        total = 0.0
        eps = 0.01
        n = len(ALL_GENRES)
        for g in ALL_GENRES:
            pi = (p.get(g, 0.0) + eps) / (1.0 + n * eps)
            qi = (q.get(g, 0.0) + eps) / (1.0 + n * eps)
            total += pi * math.log(pi / qi)
            total += qi * math.log(qi / pi)
        return total / 2

    def _update_ema(self, new_dist):
        """Blend the EMA toward new_dist using alpha."""
        for g in ALL_GENRES:
            self._ema[g] = ((1 - self.alpha) * self._ema[g] + self.alpha * new_dist.get(g, 0.0))

    def record_action(self, genre):
        """Record a single play/like action. Returns detection status dict."""
        if isinstance(genre, str):
            genre = Genre.from_string(genre)
        self._total_actions += 1
        self._window.append(genre)
        if len(self._window) > self._window_size:
            self._window.popleft()

        result = {
            "total_actions": self._total_actions,
            "shift_detected": False,
            "shift_confirmed": False,
            "kl_divergence": 0.0,
            "threshold": self.threshold,
            "streak": 0,
            "enabled": False,
        }

        # Build a single-action distribution: concentrated on the genre
        # but with a small uniform floor so the EMA never fully collapses.
        floor = 0.01
        single_dist = {g: floor for g in ALL_GENRES}
        single_dist[genre] = 1.0
        total = sum(single_dist.values())
        single_dist = {g: v / total for g, v in single_dist.items()}
        self._update_ema(single_dist)

        if self._total_actions < self.min_samples:
            self._history.append(result)
            return result

        result["enabled"] = True
        recent_dist = self._genre_to_distribution(list(self._window))
        kl = self._symmetric_kl(recent_dist, self._ema)
        self._last_kl = kl
        result["kl_divergence"] = round(kl, 4)

        if kl > self.threshold:
            self._streak += 1
            result["shift_detected"] = True
            result["streak"] = self._streak
            if self._streak >= self.confirm_streak:
                self._shift_confirmed = True
                self._shift_count += 1
                result["shift_confirmed"] = True
                self._streak = 0
        else:
            self._streak = 0
            result["streak"] = 0

        self._history.append(result)
        return result

    def record_many(self, genres):
        """Record multiple actions. Returns list of per-action results."""
        return [self.record_action(g) for g in genres]

    def get_stats(self):
        """Return current detector statistics."""
        recent_dist = self._genre_to_distribution(list(self._window))
        return {
            "total_actions": self._total_actions,
            "ema_distribution": {g.name: round(v, 4) for g, v in self._ema.items()},
            "recent_distribution": {g.name: round(v, 4) for g, v in recent_dist.items()},
            "kl_divergence": round(self._last_kl, 4),
            "threshold": self.threshold,
            "streak": self._streak,
            "shift_confirmed": self._shift_confirmed,
            "shift_count": self._shift_count,
            "enabled": self._total_actions >= self.min_samples,
            "step_adjustment": self.step_adjustment,
        }

    def get_step_adjustment(self):
        """Return the current score adjustment for the autoplay heap."""
        if self._shift_confirmed:
            return self.step_adjustment
        return 0.0

    def reset_shift(self):
        """Acknowledge a shift and reset the confirmed flag."""
        self._shift_confirmed = False
        self._streak = 0

    @property
    def shift_count(self):
        return self._shift_count

    @property
    def last_kl(self):
        return self._last_kl


def simulate_shift(detector, from_genre, to_genre, n=30):
    """Simulate a taste shift by playing from_genre then switching to to_genre.

    Returns the index (1-based) at which the shift was confirmed, or 0.
    """
    warmup = min(detector.min_samples, n // 2)
    for _ in range(warmup):
        detector.record_action(from_genre)
    for i in range(n - warmup):
        result = detector.record_action(to_genre)
        if result.get("shift_confirmed"):
            return warmup + i + 1
    return 0
