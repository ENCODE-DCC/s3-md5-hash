from functools import cached_property
from typing import TYPE_CHECKING, Any, Dict

import boto3

if TYPE_CHECKING:
    from aws_lambda_typing import Context
    from mypy_boto3_s3.client import S3Client
    from mypy_boto3_s3.type_defs import GetObjectTaggingOutputTypeDef, TaggingTypeDef


class TaggingClient:
    @cached_property
    def client(self) -> "S3Client":  # pragma: no cover
        return boto3.client("s3")

    def get_object_tagging(
        self, bucket: str, key: str
    ) -> "GetObjectTaggingOutputTypeDef":  # pragma: no cover
        return self.client.get_object_tagging(Bucket=bucket, Key=key)

    def put_object_tagging(
        self, bucket: str, key: str, tagging: "TaggingTypeDef"
    ) -> None:  # pragma: no cover
        self.client.put_object_tagging(Bucket=bucket, Key=key, Tagging=tagging)


def lambda_handler(event: Dict[str, Any], context: "Context") -> None:
    client = TaggingClient()
    bucket = event["bucket"]
    key = event["key"]
    object_tagging = client.get_object_tagging(bucket=bucket, key=key)
    tagging: "TaggingTypeDef" = {"TagSet": object_tagging["TagSet"]}
    tagging["TagSet"].append({"Key": "md5sum", "Value": event["md5_hash"]})
    client.put_object_tagging(bucket=bucket, key=key, tagging=tagging)
