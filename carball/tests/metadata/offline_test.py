
from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_specific_replays


class DBTest():
    def test_offline_replay(self, replay_cache):

        def test(analysis: AnalysisManager):
            assert analysis.get_protobuf_data() is not None
            assert not analysis.get_protobuf_data().game_metadata.is_invalid_analysis
            game = analysis.get_protobuf_data()
            assert game.game_metadata.match_guid, game.game_metadata.id

        run_analysis_test_on_replay(test, replay_list=get_specific_replays()["OFFLINE"], cache=replay_cache)
