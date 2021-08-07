"""Functions to encode and decode data into frames."""
import io
from binascii import unhexlify
from hashlib import sha256
from typing import Any
from typing import BinaryIO
from typing import List
from typing import Tuple

from PIL import Image  # type: ignore


def generate_frames(file_path: str, size: Tuple[int, int]) -> List[Any]:
    """Generates frames from a given file path.

    Args:
        file_path (str): A valid filepath
        size (Tuple[int, int]): Resolution of the frames

    Returns:
        List[Any]: A list of binary image file objects
    """
    frame_data_length = size[0] * size[1] * 3 - 40
    frames = []
    with open(file_path, "rb") as source:
        while True:
            frame_data = source.read(frame_data_length)
            if not frame_data:
                break
            metadata = unhexlify(
                sha256(frame_data).hexdigest() + hex(len(frame_data))[2:].zfill(16)
            )
            frame_data = metadata + frame_data
            frames.append(convert_to_frame(frame_data, size))
    return frames


def convert_to_frame(frame_data: bytes, size: Tuple[int, int]) -> BinaryIO:
    """Converts raw bytes into an image.

    Args:
        frame_data (bytes): Any byte string
        size (Tuple[int, int]): Resolution of the image

    Returns:
        BinaryIO: A file like object containing actual image bytes
    """
    frame_data = frame_data.ljust(size[0] * size[1] * 3, b"\x00")
    frame = Image.frombytes("RGB", size, frame_data)
    frame_file = io.BytesIO()
    frame.save(frame_file, format="PNG")
    frame_file.seek(0)
    return frame_file
