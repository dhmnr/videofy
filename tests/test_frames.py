"""Unit tests for frames.py file."""
from unittest.mock import Mock
from unittest.mock import mock_open

from pytest_mock import MockerFixture

from videofy.frames import encode_frames


def test_generate_frames(mocker: MockerFixture) -> None:
    """Tests the generate frames function."""
    test_size = (3, 3)
    test_file = "test_path"

    mock_file = mock_open(read_data=b"test")
    mock_pad = Mock()
    mock_unhex = Mock()
    mock_unhex.return_value = b"test_metadata"

    mocker.patch("videofy.frames.open", mock_file)
    mocker.patch("videofy.frames.pad_frame", mock_pad)
    mocker.patch("videofy.frames.unhexlify", mock_unhex)

    result = encode_frames(test_file, test_size)

    mock_file.assert_called()
    mock_file().read.assert_called()
    mock_pad.assert_called_with(b"test_metadata" + b"test", test_size)
    assert [mock_pad()] == result
