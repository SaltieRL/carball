from carball.tests.utils import get_replay_path
from carball.decompile_replays import analyze_replay_file

"""
This file is doing benchmarking for the main replay varieties. The tests are run via the benchmarking GitHub action.

kwargs is a dict of variable name to value for the benchmarked method.
rounds are collections of iterations, and the data is collected off of these.
iterations are single method runs.
"""


def test_short_sample(benchmark):
    replay_path = get_replay_path("SHORT_SAMPLE.replay")

    benchmark.pedantic(analyze_replay_file,
                       kwargs={"replay_path":replay_path}, rounds=10, iterations=3)


def test_short_dropshot(benchmark):
    replay_path = get_replay_path("DROPSHOT_PHASE2_BALL.replay")

    benchmark.pedantic(analyze_replay_file,
                       kwargs={"replay_path":replay_path}, rounds=10, iterations=3)


def test_full_rumble(benchmark):
    replay_path = get_replay_path("RUMBLE_FULL.replay")

    benchmark.pedantic(analyze_replay_file,
                       kwargs={"replay_path":replay_path}, rounds=10, iterations=3)


def test_oce_rlcs(benchmark):
    replay_path = get_replay_path("OCE_RLCS_7_CARS.replay")

    benchmark.pedantic(analyze_replay_file,
                       kwargs={"replay_path":replay_path}, rounds=10, iterations=3)


def test_intensive_oce_rlcs(benchmark):
    replay_path = get_replay_path("OCE_RLCS_7_CARS.replay")

    benchmark.pedantic(analyze_replay_file,
                       kwargs={"replay_path":replay_path, "calculate_intensive_events":True}, rounds=5, iterations=1)
