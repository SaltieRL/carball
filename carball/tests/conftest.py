import pytest


replay_cache = dict()

@pytest.fixture(scope="session")
def replay_cache():
    return replay_cache
