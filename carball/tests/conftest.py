import pytest


replay_cache_map = dict()

@pytest.fixture(scope="session")
def replay_cache():
    return replay_cache_map
