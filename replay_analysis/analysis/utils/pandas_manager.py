import io
import logging

import pandas

from replay_analysis.analysis.utils.numpy_manager import write_array_to_file, read_array_from_file
from ...generated.api import game_pb2
from ...generated.api.stats import data_frame_pb2


logger = logging.getLogger(__name__)


class PandasManager:
    @staticmethod
    def add_pandas(protobuf_game: game_pb2.Game, data_frame: pandas.DataFrame):
        hdf5_bytes = PandasManager.safe_write_pandas_to_memory(data_frame, field_name="game_frames")
        if hdf5_bytes is not None:
            protobuf_game.Extensions[data_frame_pb2.data_frame] = hdf5_bytes

    @staticmethod
    def get_pandas(protobuf_game: game_pb2.Game):
        game_frames = None
        if protobuf_game.HasExtension("data_frame"):
            game_frames = PandasManager.safe_read_pandas_to_memory(protobuf_game.Extensions[data_frame_pb2.data_frame],
                                                                   field_name="game_frames")
        return game_frames

    @staticmethod
    def safe_write_pandas_to_memory(df, field_name=""):
        try:
            # return PandasManager.write_hdf_to_buffer(df)
            return PandasManager.write_numpy_to_memory(df)
        except BaseException as e:
            logger.exception("Failure to write pandas [%s] to memory: %s", field_name, e)

    @staticmethod
    def safe_read_pandas_to_memory(buffer, field_name=""):
        try:
            return PandasManager.read_numpy_from_memory(buffer)
        except BaseException as e:
            logger.exception("Failure to read pandas [%s] from memory: %s", field_name, e)

    @staticmethod
    def write_numpy_to_memory(df):
        numpy_array = df.to_records(index=True)
        compressed_array = io.BytesIO()
        write_array_to_file(compressed_array, numpy_array)
        return compressed_array.getvalue()

    @staticmethod
    def read_numpy_from_memory(buffer):
        array = read_array_from_file(buffer)
        return pandas.DataFrame.from_records(array)
