from tempfile import NamedTemporaryFile
from carball.analysis.analysis_manager import AnalysisManager
from carball.tests.utils import run_analysis_test_on_replay, get_raw_replays


class Test_Export():

    def test_json_export(self, replay_cache):
        def test(analysis: AnalysisManager):
            with NamedTemporaryFile(mode='w') as f:
                analysis.write_json_out_to_file(f)

        run_analysis_test_on_replay(test, get_raw_replays()["DEFAULT_3_ON_3_AROUND_58_HITS"], cache=replay_cache)

    def test_unicode_names(self, replay_cache):
        def test(analysis: AnalysisManager):
            with NamedTemporaryFile(mode='wb') as f:
                analysis.write_pandas_out_to_file(f)

        run_analysis_test_on_replay(test, get_raw_replays()["UNICODE_ERROR"], cache=replay_cache)
