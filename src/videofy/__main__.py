"""Command-line interface."""
from typing import Tuple

import click
from imageio_ffmpeg import read_frames  # type: ignore
from imageio_ffmpeg import write_frames

from videofy.frames import decode_frames
from videofy.frames import encode_frames


@click.command()
@click.version_option()
@click.option(
    "--encode", "-e", default=False, is_flag=True, help="Encode a file into a video"
)
@click.option(
    "--decode", "-d", default=False, is_flag=True, help="Decode a video into a file"
)
@click.option(
    "--size",
    "-s",
    nargs=2,
    type=click.Tuple([int, int]),
    default=(1920, 1080),
    help="Resolution of the video in case of encode. Default is 1920x1080",
)
@click.argument("INPUT", nargs=1, type=click.Path(exists=True, dir_okay=False))
@click.argument("OUTPUT", nargs=1, type=click.Path(dir_okay=False))
def main(
    encode: bool, decode: bool, size: Tuple[int, int], input: str, output: str
) -> None:
    """A tool to convert any file into a video and convert it back."""
    if encode and decode:
        raise click.UsageError(
            "Operation must be either --encode or --decode, cannot be both"
        )

    elif (not encode) and (not decode):
        raise click.UsageError(
            "Operation must be specified. either --encode or --decode"
        )
    elif (encode) and (not decode):
        encode_file(input, size, output)

    else:
        decode_video(input, output)


def encode_file(
    input_file_path: str, size: Tuple[int, int], output_file_path: str
) -> None:
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
        macro_block_size=1,
        output_params=["-flags", "bitexact", "-fflags", "bitexact"],
    )
    writer.send(None)  # seed the generator
    frames = encode_frames(input_file_path, size)
    for frame in frames:
        writer.send(frame)
    writer.close()


def decode_video(input_file_path: str, output_file_path: str) -> None:
    """Decodes a video into a binary file.

    Args:
    input_file_path (str): Input file path of the video
    output_file_path (str): Output file path where the decoded file will be saved
    """
    reader = read_frames(input_file_path)
    _ = reader.__next__()
    decode_frames(reader, output_file_path)


if __name__ == "__main__":
    main(prog_name="videofy")  # pragma: no cover
