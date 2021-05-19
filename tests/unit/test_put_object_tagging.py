from typing import Any, Dict

import pytest
from pytest_mock import MockerFixture

from functions.put_object_tagging import app


@pytest.fixture
def event() -> Dict[str, Any]:
    return {
        "md5_hash": "myhash",
        "bucket": "foo",
        "key": "bar.baz",
    }


def test_put_object_tagging_existing_tags(
    mocker: MockerFixture, event: Dict[str, Any]
) -> None:
    stub_client = mocker.MagicMock()
    stub_client_instance = mocker.MagicMock()
    stub_client.return_value = stub_client_instance
    stub_client_instance.get_object_tagging.return_value = {
        "TagSet": [{"Key": "existingtag", "Value": "alreadythere"}]
    }
    mocker.patch("functions.put_object_tagging.app.TaggingClient", stub_client)
    context = mocker.Mock()
    app.lambda_handler(event, context)
    stub_client_instance.put_object_tagging.assert_called_once_with(
        bucket="foo",
        key="bar.baz",
        tagging={
            "TagSet": [
                {"Key": "existingtag", "Value": "alreadythere"},
                {"Key": "md5sum", "Value": "myhash"},
            ]
        },
    )


def test_put_object_tagging_no_existing_tags(
    mocker: MockerFixture, event: Dict[str, Any]
) -> None:
    stub_client = mocker.MagicMock()
    stub_client_instance = mocker.MagicMock()
    stub_client.return_value = stub_client_instance
    stub_client_instance.get_object_tagging.return_value = {"TagSet": []}
    mocker.patch("functions.put_object_tagging.app.TaggingClient", stub_client)
    context = mocker.Mock()
    app.lambda_handler(event, context)
    stub_client_instance.put_object_tagging.assert_called_once_with(
        bucket="foo",
        key="bar.baz",
        tagging={
            "TagSet": [
                {"Key": "md5sum", "Value": "myhash"},
            ]
        },
    )
