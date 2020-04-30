import os

from carball.decompile_replays import analyze_replay_file


def test_short_sample(benchmark):
    carball_dir = os.path.dirname(os.path.dirname(__file__))
    replay_path = os.path.join(carball_dir, "carball/tests/replays/SHORT_SAMPLE.replay")

    benchmark.pedantic(analyze_replay_file,
                       kwargs={"replay_path":replay_path}, rounds=50, iterations=3)


def test_full_rumble(benchmark):
    carball_dir = os.path.dirname(os.path.dirname(__file__))
    replay_path = os.path.join(carball_dir, "carball/tests/replays/RUMBLE_FULL.replay")

    benchmark.pedantic(analyze_replay_file,
                       kwargs={"replay_path":replay_path}, rounds=20, iterations=3)


def test_oce_rlcs(benchmark):
    carball_dir = os.path.dirname(os.path.dirname(__file__))
    replay_path = os.path.join(carball_dir, "carball/tests/replays/OCE_RLCS_7_CARS.replay")

    benchmark.pedantic(analyze_replay_file,
                       kwargs={"replay_path":replay_path}, rounds=20, iterations=3)


def test_oce_rlcs_intensive(benchmark):
    carball_dir = os.path.dirname(os.path.dirname(__file__))
    replay_path = os.path.join(carball_dir, "carball/tests/replays/OCE_RLCS_7_CARS.replay")

    benchmark.pedantic(analyze_replay_file,
                       kwargs={"replay_path":replay_path, "calculate_intensive_events":True}, rounds=5, iterations=3)

