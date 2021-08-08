"""Test cases for the __main__ module."""
from unittest.mock import call
from unittest.mock import Mock

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

from videofy import __main__


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_main_encode(runner: CliRunner, mocker: MockerFixture) -> None:
    """It exits with a status code of zero."""
    mock_encode_file = Mock()

    mocker.patch("videofy.__main__.encode_file", mock_encode_file)

    with runner.isolated_filesystem():
        with open("input_file", "wb") as f:
            f.write(b"TEST")
        result = runner.invoke(
            __main__.main,
            ["--encode", "--size", "1920", "1080", "input_file", "output_file"],
            catch_exceptions=False,
        )
        mock_encode_file.assert_called_with("input_file", (1920, 1080), "output_file")
        assert result.exit_code == 0


def test_main_decode(runner: CliRunner, mocker: MockerFixture) -> None:
    """It exits with a status code of zero."""
    mock_decode_video = Mock()

    mocker.patch("videofy.__main__.decode_video", mock_decode_video)

    with runner.isolated_filesystem():
        with open("input_file", "wb") as f:
            f.write(b"TEST")
        result = runner.invoke(
            __main__.main,
            ["--decode", "input_file", "output_file"],
            catch_exceptions=False,
        )
        mock_decode_video.assert_called_with("input_file", "output_file")
        assert result.exit_code == 0


def test_main_both_option(runner: CliRunner) -> None:
    """It exits with a status code of two."""
    with runner.isolated_filesystem():
        with open("input_file", "wb") as f:
            f.write(b"TEST")
        result = runner.invoke(
            __main__.main, ["--encode", "--decode", "input_file", "output_file"]
        )
        assert result.exception
        assert result.exit_code == 2


def test_main_no_option(runner: CliRunner) -> None:
    """It exits with a status code of two."""
    with runner.isolated_filesystem():
        with open("input_file", "wb") as f:
            f.write(b"TEST")
        result = runner.invoke(__main__.main, ["input_file", "output_file"])
        assert result.exception
        assert result.exit_code == 2


def test_encode_file(mocker: MockerFixture) -> None:
    """Tests the encode_file function."""
    test_input = "input_file"
    test_size = (100, 100)
    test_output = "output_file"

    mock_write_frames = Mock()
    mock_writer = Mock()
    mock_write_frames.return_value = mock_writer
    mock_encode_frames = Mock()

    mock_encode_frames.return_value = [b"test_frame"]

    mocker.patch("videofy.__main__.write_frames", mock_write_frames)
    mocker.patch("videofy.__main__.encode_frames", mock_encode_frames)

    __main__.encode_file(test_input, test_size, test_output)

    mock_write_frames.assert_called_with(
        test_output,
        test_size,
        quality=10,
        codec="ffvhuff",
        pix_fmt_out="rgb24",
        macro_block_size=1,
        output_params=["-flags", "bitexact", "-fflags", "bitexact"],
    )
    mock_writer.send.assert_has_calls([call(None)])
    mock_encode_frames.assert_called_with(test_input, test_size)
    mock_writer.send.assert_called_with(b"test_frame")
    mock_writer.close.assert_called()


def test_decode_video(mocker: MockerFixture) -> None:
    """Tests the decode_video function."""
    test_input = "input_file"
    test_output = "output_file"
    test_iter = iter([b"metadata", b"frame1"])

    mock_read_frames = Mock()
    mock_read_frames.return_value = test_iter
    mock_decode_frames = Mock()

    mocker.patch("videofy.__main__.read_frames", mock_read_frames)
    mocker.patch("videofy.__main__.decode_frames", mock_decode_frames)

    __main__.decode_video(test_input, test_output)

    mock_read_frames.assert_called_with(test_input)
    mock_decode_frames.assert_called_with(test_iter, test_output)
