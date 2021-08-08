"""Unit tests for frames.py file."""
from unittest.mock import Mock
from unittest.mock import mock_open

from pytest_mock import MockerFixture

from videofy.frames import decode_frames
from videofy.frames import encode_frames
from videofy.frames import pad_frame


def test_encode_frames(mocker: MockerFixture) -> None:
    """Tests the encode_frames function."""
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


def test_decode_frames_hash_success(mocker: MockerFixture) -> None:
    """Tests the decode_frames function."""
    test_hash = b"hash" * 8
    test_metadata = test_hash + b"\x00" * 7 + b"\x04"
    test_frame_data = b"test"
    test_frames = [test_metadata + test_frame_data]
    test_file = "test_path"

    mock_file = mock_open()
    mock_sha256 = Mock()
    mock_sha256().hexdigest.return_value = "test_hash"
    mock_hex = Mock()
    mock_hex.return_value = b"test_hash"

    mocker.patch("videofy.frames.open", mock_file)
    mocker.patch("videofy.frames.hashlib.sha256", mock_sha256)
    mocker.patch("videofy.frames.hexlify", mock_hex)

    decode_frames(test_frames, test_file)

    mock_file.assert_called_with(test_file, "wb")
    mock_hex.assert_called_with(test_hash)
    mock_sha256.assert_called_with(test_frame_data)
    mock_file().write.assert_called_with(test_frame_data)
    mock_file().flush.assert_called()
    mock_file().close.asset_called()


def test_decode_frames_hash_fails(mocker: MockerFixture) -> None:
    """Tests the decode_frames function."""
    test_hash = b"hash" * 8
    test_metadata = test_hash + b"\x00" * 7 + b"\x04"
    test_frame_data = b"test"
    test_frames = [test_metadata + test_frame_data]
    test_file = "test_path"

    mock_file = mock_open()
    mock_sha256 = Mock()
    mock_sha256().hexdigest.return_value = "test_not_hash"
    mock_hex = Mock()
    mock_hex.return_value = b"test_hash"
    mock_remove = Mock()

    mocker.patch("videofy.frames.open", mock_file)
    mocker.patch("videofy.frames.hashlib.sha256", mock_sha256)
    mocker.patch("videofy.frames.hexlify", mock_hex)
    mocker.patch("videofy.frames.os.remove", mock_remove)

    decode_frames(test_frames, test_file)

    mock_file.assert_called_with(test_file, "wb")
    mock_hex.assert_called_with(test_hash)
    mock_sha256.assert_called_with(test_frame_data)
    mock_file().write.assert_not_called()
    mock_file().flush.assert_not_called()
    mock_file().close.asset_called()
    mock_remove.assert_called_with(test_file)


def test_pad_frame() -> None:
    """Tests the pad_frame function."""
    assert b"test\x00\x00" == pad_frame(b"test", (2, 1))
    assert b"test" == pad_frame(b"test", (1, 1))
    assert b"test\x00\x00\x00\x00\x00\x00\x00\x00" == pad_frame(b"test", (2, 2))
