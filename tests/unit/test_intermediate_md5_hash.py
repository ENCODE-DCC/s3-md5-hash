import pickle
from typing import Any, Dict

import pytest
import rehash
from pytest_mock import MockerFixture

from functions.intermediate_md5_hash import app


@pytest.fixture
def event() -> Dict[str, Any]:
    md5_hash = rehash.md5()
    md5_hash.update(b"foo")
    return {
        "start_byte": 100,
        "hash_object": pickle.dumps(md5_hash),
        "bucket": "foo",
        "key": "bar.baz",
    }


def test_intermediate_md5_hash_complete_hash(
    mocker: MockerFixture, event: Dict[str, Any]
) -> None:
    stub_body = mocker.Mock()
    stub_body.iter_chunks.return_value = [b"bar", b"baz"]
    mocker.patch(
        "functions.intermediate_md5_hash.app._get_object",
        return_value={"ETag": "not-md5sum", "Body": stub_body},
    )
    context = mocker.Mock()
    context.get_remaining_time_in_millis.return_value = 100000
    result = app.lambda_handler(event, context)
    assert result == {
        "md5_hash": "6df23dc03f9b54cc38a0fc1483df6e21",
        "bucket": "foo",
        "key": "bar.baz",
    }


def test_intermediate_md5_hash_incomplete_hash(
    mocker: MockerFixture, event: Dict[str, Any]
) -> None:
    """
    Should execute one call to the iterator.
    """
    stub_body = mocker.Mock()
    stub_body.iter_chunks.return_value = [b"bar", b"baz"]
    mocker.patch(
        "functions.intermediate_md5_hash.app._get_object",
        return_value={"ETag": "not-md5sum", "Body": stub_body},
    )
    context = mocker.Mock()
    context.get_remaining_time_in_millis.return_value = 1000
    result = app.lambda_handler(event, context)
    hash_object = pickle.loads(result["hash_object"])
    assert result["bucket"] == "foo"
    assert result["key"] == "bar.baz"
    assert result["start_byte"] == 100 + app.CHUNKSIZE
    assert hash_object.hexdigest() == "3858f62230ac3c915f300c664312c63f"
