"""Functions to encode and decode data into frames."""
import hashlib
import os
from binascii import hexlify
from binascii import unhexlify
from hashlib import sha256
from typing import List
from typing import Tuple

import click


def encode_frames(file_path: str, size: Tuple[int, int]) -> List[bytes]:
    """Encodes data from a given file into frames of given size.

    Args:
        file_path (str): A valid filepath
        size (Tuple[int, int]): Resolution of the frames

    Returns:
        List[bytes]: A list of frames
    """
    frame_data_length = size[0] * size[1] * 3 - 40
    frames = []
    file_size = os.path.getsize(file_path)
    with open(file_path, "rb") as source:
        with click.progressbar(length=file_size, label="Generating frames") as bar:
            while True:
                frame_data = source.read(frame_data_length)
                if not frame_data:
                    break
                metadata = unhexlify(
                    sha256(frame_data).hexdigest() + hex(len(frame_data))[2:].zfill(16)
                )
                frame_data = metadata + frame_data
                frames.append(pad_frame(frame_data, size))
                bar.update(frame_data_length)
    return frames


def decode_frames(frames: List[bytes], file_path: str) -> None:
    """Decodes frames into bytes and writes them to the file."""
    output = open(file_path, "wb")
    try:
        with click.progressbar(frames, label="Writing to video") as bar:
            for frame in bar:
                metadata = frame[:40]
                hash = hexlify(metadata[:32]).decode()
                length = int.from_bytes(metadata[32:], "big")
                frame_data = frame[40:][:length]
                if not hash == hashlib.sha256(frame_data).hexdigest():
                    raise Exception("ERROR")
                output.write(frame_data)
                output.flush()
            output.close()
    except Exception:
        output.close()
        os.remove(file_path)


def pad_frame(frame_data: bytes, size: Tuple[int, int]) -> bytes:
    """Pads frame data to fit the size.

    Args:
        frame_data (bytes): Any byte string
        size (Tuple[int, int]): Resolution of the image

    Returns:
        bytes: Padded frame data
    """
    return frame_data.ljust(size[0] * size[1] * 3, b"\x00")
