import pickle
from typing import Any, Dict

import pytest
from pytest_mock import MockerFixture

from functions.initial_md5_hash import app


@pytest.fixture
def event() -> Dict[str, Any]:
    return {
        "detail": {
            "resources": [
                {"type": "AWS::S3::Object", "ARN": "arn:aws:s3:::foo/bar.baz"},
                {
                    "accountId": "123",
                    "type": "AWS::S3::Bucket",
                    "ARN": "arn:aws:s3:::foo",
                },
            ],
        }
    }


def test_initial_md5_hash_etag_is_md5sum(
    mocker: MockerFixture, event: Dict[str, Any]
) -> None:
    mocker.patch(
        "functions.initial_md5_hash.app._get_object",
        return_value={"ETag": "d159b8e5651dd7ad24e9049d41cbbb8e"},
    )
    context = mocker.Mock()
    result = app.lambda_handler(event, context)
    assert result == {
        "md5_hash": "d159b8e5651dd7ad24e9049d41cbbb8e",
        "bucket": "foo",
        "key": "bar.baz",
    }


def test_initial_md5_hash_complete_hash(
    mocker: MockerFixture, event: Dict[str, Any]
) -> None:
    stub_body = mocker.Mock()
    stub_body.iter_chunks.return_value = [b"foo", b"bar"]
    mocker.patch(
        "functions.initial_md5_hash.app._get_object",
        return_value={"ETag": "not-md5sum", "Body": stub_body},
    )
    context = mocker.Mock()
    context.get_remaining_time_in_millis.return_value = 100000
    result = app.lambda_handler(event, context)
    assert result == {
        "md5_hash": "3858f62230ac3c915f300c664312c63f",
        "bucket": "foo",
        "key": "bar.baz",
    }


def test_initial_md5_hash_incomplete_hash(
    mocker: MockerFixture, event: Dict[str, Any]
) -> None:
    """
    Should execute one call to the iterator.
    """
    stub_body = mocker.Mock()
    stub_body.iter_chunks.return_value = [b"foo", b"bar"]
    mocker.patch(
        "functions.initial_md5_hash.app._get_object",
        return_value={"ETag": "not-md5sum", "Body": stub_body},
    )
    context = mocker.Mock()
    context.get_remaining_time_in_millis.return_value = 1000
    result = app.lambda_handler(event, context)
    hash_object = pickle.loads(bytes.fromhex(result["hash_object"]))
    assert result["bucket"] == "foo"
    assert result["key"] == "bar.baz"
    assert result["start_byte"] == app.CHUNKSIZE
    assert hash_object.hexdigest() == "acbd18db4cc2f85cedef654fccc4a4d8"
