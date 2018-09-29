import os
import unittest
from unittest.mock import patch

from ..create_proto import get_proto


class GetProtoTests(unittest.TestCase):
    @patch.dict(os.environ, {'PROTOC_PATH': '/foo/bar/protoc'})
    def test_with_env_var(self):
        protoc_path = get_proto()
        self.assertEqual(protoc_path, '/foo/bar/protoc')

    @patch('utils.create_proto.is_windows', return_value=True)
    def test_windows(self, is_windows):
        self.assertIsNone(os.getenv('PROTOC_PATH'))
        self.assertTrue(is_windows())

        protoc_path = get_proto()
        self.assertTrue(protoc_path.endswith('protoc.exe'))

    @patch('utils.create_proto.is_windows', return_value=False)
    def test_is_not_windows(self, is_windows):
        self.assertIsNone(os.getenv('PROTOC_PATH'))
        self.assertFalse(is_windows())

        protoc_path = get_proto()
        self.assertTrue(protoc_path.endswith('protoc'))
