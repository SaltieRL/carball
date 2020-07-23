import unittest
from carball.analysis.analysis_manager import AnalysisManager
from carball.tests.utils import run_analysis_test_on_replay, get_raw_replays


class Test_CameraSettings:

    def test_camera_settings(self, replay_cache):
        assertions = unittest.TestCase('__init__')

        def test(analysis: AnalysisManager):
            proto_game = analysis.get_protobuf_data()
            camera_settings = proto_game.players[0].camera_settings

            assertions.assertAlmostEqual(camera_settings.distance, 330.0, 5)
            assertions.assertAlmostEqual(camera_settings.field_of_view, 100.0, 5)
            assertions.assertAlmostEqual(camera_settings.height, 100.0, 5)
            assertions.assertAlmostEqual(camera_settings.pitch, -4.0, 5)
            assertions.assertAlmostEqual(camera_settings.stiffness, 0.45, 5)
            assertions.assertAlmostEqual(camera_settings.swivel_speed, 4.2, 5)
            assertions.assertAlmostEqual(camera_settings.transition_speed, 1.0, 5)

        run_analysis_test_on_replay(test, get_raw_replays()["DROPSHOT_GOAL"], cache=replay_cache)
