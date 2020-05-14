from tempfile import NamedTemporaryFile

import gzip
import pytest

from carball.analysis.analysis_manager import AnalysisManager
from carball.tests.utils import run_analysis_test_on_replay, get_raw_replays


class TestExport:

    def test_json_export(self, replay_cache):
        def test(analysis: AnalysisManager):
            with NamedTemporaryFile(mode='w') as f:
                analysis.write_json_out_to_file(f)

        run_analysis_test_on_replay(test, get_raw_replays()["DEFAULT_3_ON_3_AROUND_58_HITS"], cache=replay_cache)

    def test_proto_export(self, replay_cache):
        def test(analysis: AnalysisManager):
            with NamedTemporaryFile(mode='wb') as f:
                analysis.write_proto_out_to_file(f)

        run_analysis_test_on_replay(test, get_raw_replays()["DEFAULT_3_ON_3_AROUND_58_HITS"], cache=replay_cache)

    def test_gzip_export(self, replay_cache):
        def test(analysis: AnalysisManager):
            with NamedTemporaryFile(mode='wb') as f:
                gzip_file = gzip.GzipFile(mode='wb', fileobj=f)
                analysis.write_pandas_out_to_file(gzip_file)

        run_analysis_test_on_replay(test, get_raw_replays()["DEFAULT_3_ON_3_AROUND_58_HITS"], cache=replay_cache)

    def test_unicode_names(self, replay_cache):
        def test(analysis: AnalysisManager):
            with NamedTemporaryFile(mode='wb') as f:
                analysis.write_pandas_out_to_file(f)

        run_analysis_test_on_replay(test, get_raw_replays()["UNICODE_ERROR"], cache=replay_cache)

    def test_json_export_invalid_type(self, replay_cache):
        def test(analysis: AnalysisManager):
            with NamedTemporaryFile(mode='wb') as f:
                with pytest.raises(IOError):
                    analysis.write_json_out_to_file(f)

        run_analysis_test_on_replay(test, get_raw_replays()["DEFAULT_3_ON_3_AROUND_58_HITS"], cache=replay_cache)

    def test_proto_export_invalid_type(self, replay_cache):
        def test(analysis: AnalysisManager):
            with NamedTemporaryFile(mode='w') as f:
                with pytest.raises(IOError):
                    analysis.write_proto_out_to_file(f)

        run_analysis_test_on_replay(test, get_raw_replays()["DEFAULT_3_ON_3_AROUND_58_HITS"], cache=replay_cache)

    def test_unicode_names_invalid_type(self, replay_cache):
        def test(analysis: AnalysisManager):
            with NamedTemporaryFile(mode='w') as f:
                with pytest.raises(IOError):
                    analysis.write_pandas_out_to_file(f)

        run_analysis_test_on_replay(test, get_raw_replays()["UNICODE_ERROR"], cache=replay_cache)
