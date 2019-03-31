from typing import List, TYPE_CHECKING, Dict

import numpy as np

from carball.generated.api.stats.per_possession_stats_pb2 import PerPossessionStats, AverageCounts

if TYPE_CHECKING:
    from carball.analysis.stats.possessions import BasePossession


def get_per_possession_stats(possessions: List['BasePossession']) -> PerPossessionStats:
    count = len(possessions)
    hit_counts = np.array([len(possession.hits) for possession in possessions])
    average_hits = hit_counts.mean()
    durations = np.array([possession.duration for possession in possessions])
    average_duration = durations.mean()

    average_counts = {}
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
        average_counts[field] = sum_ / count

    per_possession_stats = PerPossessionStats()
    add_average_counts(per_possession_stats, average_counts)

    per_possession_stats.average_hits = average_hits
    per_possession_stats.average_duration = average_duration
    per_possession_stats.count = count

    return per_possession_stats


def add_average_counts(per_possession_stats: PerPossessionStats, average_counts: Dict[str, float]):
    for field, value in average_counts.items():
        setattr(per_possession_stats.average_counts, field, value)
