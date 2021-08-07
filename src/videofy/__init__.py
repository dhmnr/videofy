"""Videofy."""
from typing import Tuple

from imageio_ffmpeg import read_frames  # type: ignore
from imageio_ffmpeg import write_frames

from videofy.frames import decode_frames
from videofy.frames import encode_frames


def encode(input_file_path: str, size: Tuple[int, int], output_file_path: str) -> None:
    """Encodes a binary file into a video.

    Args:
        input_file_path (str): Input file path of the binary file
        size (Tuple[int, int]): Resolution of the output video
        output_file_path (str): Output file path where the video will be saved
    """
    writer = write_frames(
        output_file_path,
        size,
        quality=10,
        codec="ffvhuff",
        pix_fmt_out="rgb24",
        output_params=["-flags", "bitexact", "-fflags", "bitexact"],
    )
    writer.send(None)  # seed the generator
    frames = encode_frames(input_file_path, size)
    for frame in frames:
        writer.send(frame)
    writer.close()


def decode(input_file_path: str, output_file_path: str) -> None:
    """Decodes a video into a binary file.

    Args:
    input_file_path (str): Input file path of the video
    output_file_path (str): Output file path where the decoded file will be saved
    """
    reader = read_frames(input_file_path)
    _ = reader.__next__()
    decode_frames(reader, output_file_path)
