from typing import List, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from carball.analysis.stats.possessions import PlayerPossession


class PerPossessionStats:
    def __init__(self, possessions: List['PlayerPossession']):
        self.count = len(possessions)
        hit_counts = np.array([len(possession.hits) for possession in possessions])
        self.average_hits = hit_counts.mean()
        durations = np.array([possession.duration for possession in possessions])
        self.average_duration = durations.mean()

        self.average_counts = {}
        fields = [
            'pass_', 'passed',
            'dribble', 'dribble_continuation',
            'shot', 'goal',
            'assist', 'assisted',
            'save',
            'aerial',
        ]

        for field in fields:
            sum_ = sum([possession.counts[field] for possession in possessions])
            self.average_counts[field] = sum_ / self.count
