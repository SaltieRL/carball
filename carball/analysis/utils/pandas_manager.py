import io
import logging

import pandas as pd

from carball.analysis.utils.numpy_manager import write_array_to_file, read_array_from_file


logger = logging.getLogger(__name__)


class PandasManager:

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
        dataframe = pd.DataFrame.from_records(array)
        dataframe.set_index('index', drop=True, inplace=True)
        columns = []
        for tuple_str in dataframe.columns.values:
            columns.append(eval(tuple_str))
        dataframe.columns = pd.MultiIndex.from_tuples(columns)
        return dataframe
