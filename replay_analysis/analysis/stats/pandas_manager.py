import logging

from replay_analysis.generated.api.stats import data_frames_pb2


logger = logging.getLogger(__name__)


class PandasManager:
    @staticmethod
    def add_pandas(proto_data_frame: data_frames_pb2.DataFrames, data_frames):
        hdf5_bytes = PandasManager.safe_write_pandas_to_memory(data_frames, field_name="game_frames")
        if hdf5_bytes is not None:
            proto_data_frame.game_frames = hdf5_bytes

    @staticmethod
    def get_pandas(proto_data_frame: data_frames_pb2.DataFrames):
        game_frames = None
        if proto_data_frame.HasField("game_frames"):
            game_frames = PandasManager.safe_read_pandas_to_memory(proto_data_frame.game_frames,
                                                                   field_name="game_frames")
        return game_frames

    @staticmethod
    def safe_write_pandas_to_memory(df, field_name=""):
        try:
            return PandasManager.write_hdf_to_buffer(df)
        except BaseException as e:
            logger.exception("Failure to write pandas [%s] to memory: %s", field_name, e)

    @staticmethod
    def safe_read_pandas_to_memory(buffer, field_name=""):
        try:
            return PandasManager.read_hdf_from_buffer(buffer)
        except BaseException as e:
            logger.exception("Failure to read pandas [%s] from memory: %s", field_name, e)

    @staticmethod
    def read_hdf_from_buffer(buffer, key="/data"):
        from pandas import get_store
        with get_store(
                "data.h5",
                mode="r",
                driver="H5FD_CORE",
                driver_core_backing_store=0,
                driver_core_image=buffer.read()
        ) as store:
            return store[key]

    @staticmethod
    def write_hdf_to_buffer(df):
        from pandas import get_store
        with get_store(
                "data.h5", mode="a", driver="H5FD_CORE",
                driver_core_backing_store=0
        ) as out:
            out["/data"] = df
            return out._handle.get_file_image()
