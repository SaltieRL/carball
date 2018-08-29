import gzip
import io
import struct
import numpy as np


def write_array_to_gzip(file_path, array: np.ndarray):
    with gzip.open(file_path, 'wb') as f:
        write_array_to_file(f, array)


def write_array_to_file(game_file, array: np.ndarray):
    """
    :param game_file: This is the file that the array will be written to.
    :param array: A numpy array of any size.
    """
    bytes = convert_numpy_array(array)
    size_of_bytes = len(bytes.getvalue())
    game_file.write(struct.pack('i', size_of_bytes))
    game_file.write(bytes.getvalue())


def convert_numpy_array(numpy_array: np.ndarray):
    """
    Converts a numpy array into compressed bytes
    :param numpy_array: An array that is going to be converted into bytes
    :return: A BytesIO object that contains compressed bytes
    """
    compressed_array = io.BytesIO()  # np.savez_compressed() requires a file-like object to write to
    np.save(compressed_array, numpy_array, allow_pickle=True, fix_imports=False)
    return compressed_array


def read_array_from_file(file):
    chunk = file.read(4)
    numpy_array, num_bytes = get_array(file, chunk)
    return numpy_array


def get_array(file, chunk):
    """
    Gets a compressed numpy array from a file.
    Throws an EOFError if it has problems loading the data.
    :param file: The file that is being read
    :param chunk: A chunk representing a single number, this will be the number of bytes the array takes up.
    :return: A numpy array
    """
    try:
        starting_byte = struct.unpack('i', chunk)[0]
    except struct.error:
        raise EOFError('Struct error')
    numpy_bytes = file.read(starting_byte)
    fake_file = io.BytesIO(numpy_bytes)
    try:
        result = np.load(fake_file, fix_imports=False)
    except OSError:
        raise EOFError('NumPy parsing error')
    return result, starting_byte
