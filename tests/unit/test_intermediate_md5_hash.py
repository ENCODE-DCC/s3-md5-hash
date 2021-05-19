from typing import Dict, Any

import pytest
from pytest_mock import MockerFixture

from functions.intermediate_md5_hash import app


@pytest.fixture
def event() -> Dict[str, Any]:
    return {
        "detail": {
            "requestParameters": {
                "bucketName": "foo",
                "key": "bar.baz",
            }
        }
    }


def test_intermediate_md5_hash(
    mocker: MockerFixture, event: Dict[str, Any]
) -> None:
    mocker.patch(
        "functions.intermediate_md5_hash.app._get_object",
        return_value={"ETag": "d159b8e5651dd7ad24e9049d41cbbb8e"},
    )
    context = mocker.Mock()
    result = app.lambda_handler(event, context)
    assert result == {
        "md5_hash": "d159b8e5651dd7ad24e9049d41cbbb8e",
        "bucket": "foo",
        "key": "bar.baz",
    }
