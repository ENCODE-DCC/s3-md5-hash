from typing import TYPE_CHECKING, Any, Dict

import boto3

if TYPE_CHECKING:
    from aws_lambda_typing import Context
    from mypy_boto3_s3.type_defs import TaggingTypeDef


def lambda_handler(event: Dict[str, Any], context: "Context") -> None:
    bucket = event["bucket"]
    key = event["key"]
    client = boto3.client("s3")
    object_tagging = client.get_object_tagging(Bucket=bucket, Key=key)
    tagging: "TaggingTypeDef" = {"TagSet": object_tagging["TagSet"]}
    tagging["TagSet"].append({"Key": "md5sum", "Value": event["hash"]})
    client.put_object_tagging(Bucket=bucket, Key=key, Tagging=tagging)
