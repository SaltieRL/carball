import unittest

from carball.analysis.analysis_manager import AnalysisManager

from carball.tests.utils import run_analysis_test_on_replay, get_raw_replays
from carball.generated.api.stats.dropshot_pb2 import DAMAGED, DESTROYED


class Test_Dropshot():

    def test_single_damage(self, replay_cache):
        def test(analysis: AnalysisManager):
            assertions = unittest.TestCase('__init__')
            proto_game = analysis.get_protobuf_data()

            assert proto_game.players[0].stats.dropshot_stats.total_damage == 1
            assert proto_game.players[0].stats.dropshot_stats.damage_efficiency == 1.0

            assert proto_game.teams[0].stats.dropshot_stats.total_damage == 1
            assert proto_game.teams[0].stats.dropshot_stats.damage_efficiency == 1.0

            dropshot_ball_proto = proto_game.game_stats.ball_stats.extra_mode

            assert dropshot_ball_proto.dropshot_phase_stats[0].phase == 0
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[0].average, 9.508282, 5)
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[0].max, 9.508282, 5)
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[0].total, 9.508282, 5)

            assert dropshot_ball_proto.dropshot_phase_stats[1].phase == 1
            assert dropshot_ball_proto.dropshot_phase_stats[1].average == 0
            assert dropshot_ball_proto.dropshot_phase_stats[1].max == 0
            assert dropshot_ball_proto.dropshot_phase_stats[1].total == 0

            assert dropshot_ball_proto.dropshot_phase_stats[2].phase == 2
            assert dropshot_ball_proto.dropshot_phase_stats[2].average == 0
            assert dropshot_ball_proto.dropshot_phase_stats[2].max == 0
            assert dropshot_ball_proto.dropshot_phase_stats[2].total == 0

            game_dropshot_stats = proto_game.game_stats.dropshot_stats

            assert len(game_dropshot_stats.damage_events) == 1
            assert len(game_dropshot_stats.damage_events[0].tiles) == 1
            assert game_dropshot_stats.damage_events[0].tiles[0].id == 101
            assert game_dropshot_stats.damage_events[0].tiles[0].state == DAMAGED

        run_analysis_test_on_replay(test, get_raw_replays()["DROPSHOT_SINGLE_DAMAGE"], cache=replay_cache)

    def test_double_damage(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            assertions = unittest.TestCase('__init__')

            assert proto_game.players[0].stats.dropshot_stats.total_damage == 3
            assert proto_game.players[0].stats.dropshot_stats.damage_efficiency == 1.0

            assert proto_game.teams[1].stats.dropshot_stats.total_damage == 3
            assert proto_game.teams[1].stats.dropshot_stats.damage_efficiency == 1.0

            dropshot_ball_proto = proto_game.game_stats.ball_stats.extra_mode

            assert dropshot_ball_proto.dropshot_phase_stats[0].phase == 0
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[0].average, 10.189136, 5)
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[0].max, 10.189136, 5)
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[0].total, 10.189136, 5)

            assert dropshot_ball_proto.dropshot_phase_stats[1].phase == 1
            assert dropshot_ball_proto.dropshot_phase_stats[1].average == 0
            assert dropshot_ball_proto.dropshot_phase_stats[1].max == 0
            assert dropshot_ball_proto.dropshot_phase_stats[1].total == 0

            assert dropshot_ball_proto.dropshot_phase_stats[2].phase == 2
            assert dropshot_ball_proto.dropshot_phase_stats[2].average == 0
            assert dropshot_ball_proto.dropshot_phase_stats[2].max == 0
            assert dropshot_ball_proto.dropshot_phase_stats[2].total == 0

            game_dropshot_stats = proto_game.game_stats.dropshot_stats

            assert len(game_dropshot_stats.damage_events) == 3
            assert game_dropshot_stats.damage_events[0].tiles[0].state == DAMAGED
            assert game_dropshot_stats.damage_events[1].tiles[0].state == DESTROYED
            assert len(game_dropshot_stats.tile_stats.damage_stats) == 2
            assert game_dropshot_stats.tile_stats.damage_stats[0].total_damage == 2

        run_analysis_test_on_replay(test, get_raw_replays()["DROPSHOT_DOUBLE_DAMAGE"], cache=replay_cache)

    def test_phase1_ball(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            assertions = unittest.TestCase('__init__')

            dropshot_ball_proto = proto_game.game_stats.ball_stats.extra_mode

            assert dropshot_ball_proto.dropshot_phase_stats[0].phase == 0
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[0].average, 3.72452275, 5)
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[0].max, 6.9999535, 5)
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[0].total, 7.4490455, 5)

            assert dropshot_ball_proto.dropshot_phase_stats[1].phase == 1
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[1].average, 0.1, 5)
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[1].max, 0.1, 5)
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[1].total, 0.1, 5)

            assert dropshot_ball_proto.dropshot_phase_stats[2].phase == 2
            assert dropshot_ball_proto.dropshot_phase_stats[2].average == 0
            assert dropshot_ball_proto.dropshot_phase_stats[2].max == 0
            assert dropshot_ball_proto.dropshot_phase_stats[2].total == 0

            game_dropshot_stats = proto_game.game_stats.dropshot_stats

            assert len(game_dropshot_stats.damage_events[0].tiles) == 7

        run_analysis_test_on_replay(test, get_raw_replays()["DROPSHOT_PHASE1_BALL"], cache=replay_cache)

    def test_phase2_ball(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            assertions = unittest.TestCase('__init__')

            dropshot_ball_proto = proto_game.game_stats.ball_stats.extra_mode

            assert dropshot_ball_proto.dropshot_phase_stats[0].phase == 0
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[0].average, 7.12466465, 5)
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[0].max, 12.1493613, 5)
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[0].total, 14.2493293, 5)

            assert dropshot_ball_proto.dropshot_phase_stats[1].phase == 1
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[1].average, 19.000713, 5)
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[1].max, 19.000713, 5)
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[1].total, 19.000713, 5)

            assert dropshot_ball_proto.dropshot_phase_stats[2].phase == 2
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[2].average, 4.901173, 5)
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[2].max, 4.901173, 5)
            assertions.assertAlmostEqual(dropshot_ball_proto.dropshot_phase_stats[2].total, 4.901173, 5)

            game_dropshot_stats = proto_game.game_stats.dropshot_stats

            assert len(game_dropshot_stats.damage_events[0].tiles) == 12

        run_analysis_test_on_replay(test, get_raw_replays()["DROPSHOT_PHASE2_BALL"], cache=replay_cache)

    def test_goal(self, replay_cache):
        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()

            assert proto_game.game_metadata.goals[0].extra_mode_info.dropshot_tile.id == 89
            assert proto_game.game_metadata.goals[0].extra_mode_info.phase_1_tiles == 0
            assert proto_game.game_metadata.goals[0].extra_mode_info.phase_2_tiles == 1

        run_analysis_test_on_replay(test, get_raw_replays()["DROPSHOT_GOAL"], cache=replay_cache)
