from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_specific_replays, get_specific_answers, get_raw_replays


class Test_Hits():

    def test_num_hits_detected(self, replay_cache):
        def test(analysis: AnalysisManager, answer):
            proto_game = analysis.get_protobuf_data()
            hits = proto_game.game_stats.hits
            assert(len(hits) == answer)
            print(analysis)

        run_analysis_test_on_replay(test, replay_list=get_specific_replays()["HITS"], answers=get_specific_answers()["HITS"],
                                    cache=replay_cache)

    def test_num_kickoff_hits_detected(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            hits = proto_game.game_stats.hits
            kickoff_counter = 0
            for hit in hits:
                if hit.is_kickoff:
                    kickoff_counter += 1
            print(analysis)

            assert(kickoff_counter == 3)

        run_analysis_test_on_replay(test, replay_list=get_raw_replays()["3_KICKOFFS"],
                                    cache=replay_cache)

    def test_num_shots_detected(self, replay_cache):
        def test(analysis: AnalysisManager, answer):
            proto_game = analysis.get_protobuf_data()
            hits = proto_game.game_stats.hits
            shot_counter = 0
            for hit in hits:
                if hit.shot:
                    shot_counter += 1

            assert(shot_counter == answer)

        run_analysis_test_on_replay(test, replay_list=get_specific_replays()["SHOTS"],
                                    answers=get_specific_answers()["SHOTS"],
                                    cache=replay_cache)

    def test_num_passes_detected(self, replay_cache):
        def test(analysis: AnalysisManager, answer):
            proto_game = analysis.get_protobuf_data()
            hits = proto_game.game_stats.hits
            pass_counter = 0
            for hit in hits:
                if hit.pass_:
                    pass_counter += 1

            assert(pass_counter == answer)

        run_analysis_test_on_replay(test, replay_list=get_specific_replays()["PASSES"],
                                    answers=get_specific_answers()["PASSES"],
                                    cache=replay_cache)

    def test_num_saves_detected(self, replay_cache):
        def test(analysis: AnalysisManager, answer):
            proto_game = analysis.get_protobuf_data()
            hits = proto_game.game_stats.hits
            counter = 0
            for hit in hits:
                if hit.save:
                    counter += 1

            assert(counter == answer)

        run_analysis_test_on_replay(test, replay_list=get_specific_replays()["SAVES"],
                                    answers=get_specific_answers()["SAVES"],
                                    cache=replay_cache)

    def test_num_aerials_detected(self, replay_cache):
        def test(analysis: AnalysisManager, answer):
            proto_game = analysis.get_protobuf_data()
            hits = proto_game.game_stats.hits
            aerial_counter = 0
            for hit in hits:
                if hit.aerial:
                    aerial_counter += 1

            assert(aerial_counter == answer)

        run_analysis_test_on_replay(test, replay_list=get_specific_replays()["AERIALS"],
                                    answers=get_specific_answers()["AERIALS"],
                                    cache=replay_cache)

    def test_num_clears_detected(self, replay_cache):
        def test(analysis: AnalysisManager, answer):
            proto_game = analysis.get_protobuf_data()
            hits = proto_game.game_stats.hits
            clear_counter = 0
            for hit in hits:
                if hit.clear:
                    clear_counter += 1

            assert(clear_counter == answer)

        run_analysis_test_on_replay(test, replay_list=get_specific_replays()["CLEARS"],
                                    answers=get_specific_answers()["CLEARS"],
                                    cache=replay_cache)
