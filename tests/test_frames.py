"""Unit tests for frames.py file."""
from unittest.mock import Mock
from unittest.mock import mock_open

from pytest_mock import MockerFixture

from videofy.frames import convert_to_frame
from videofy.frames import generate_frames


def test_generate_frames(mocker: MockerFixture) -> None:
    """Tests the generate frames function."""
    test_size = (3, 3)
    test_file = "test_path"

    mock_file = mock_open(read_data=b"test")
    mock_convert = Mock()
    mock_unhex = Mock()
    mock_unhex.return_value = b"test_metadata"

    mocker.patch("videofy.frames.open", mock_file)
    mocker.patch("videofy.frames.convert_to_frame", mock_convert)
    mocker.patch("videofy.frames.unhexlify", mock_unhex)

    result = generate_frames(test_file, test_size)

    mock_file.assert_called()
    mock_file().read.assert_called()
    mock_convert.assert_called_with(b"test_metadata" + b"test", test_size)
    assert [mock_convert()] == result


def test_convert_to_frame(mocker: MockerFixture) -> None:
    """Tests the convert_to_frames function."""
    test_size = (2, 2)
    test_frame_data = b"test_data"
    test_padded_data = test_frame_data + b"\x00\x00\x00"

    mock_frombytes = Mock()
    mock_frame = Mock()
    mock_bytesio = Mock()
    mock_frombytes.return_value = mock_frame

    mocker.patch("videofy.frames.Image.frombytes", mock_frombytes)
    mocker.patch("videofy.frames.io.BytesIO", mock_bytesio)

    result = convert_to_frame(test_frame_data, test_size)

    mock_frombytes.assert_called_with("RGB", test_size, test_padded_data)
    mock_frame.save.assert_called_with(mock_bytesio(), format="PNG")
    assert mock_bytesio() == result
