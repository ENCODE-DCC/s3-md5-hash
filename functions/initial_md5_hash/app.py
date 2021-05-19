import pickle
from typing import TYPE_CHECKING, Any, Dict
from urllib.parse import unquote_plus

import boto3
import rehash

if TYPE_CHECKING:
    from aws_lambda_typing import Context
    from mypy_boto3_s3.type_defs import GetObjectOutputTypeDef

CHUNKSIZE = 8192
MILLISECONDS_REMAINING_THRESHOLD = 1000 * 10


def _get_object(bucket: str, key: str) -> "GetObjectOutputTypeDef":
    client = boto3.client("s3")
    return client.get_object(Bucket=bucket, Key=key)


def lambda_handler(event: Dict[str, Any], context: "Context") -> Dict[str, Any]:
    bucket = event["detail"]["requestParameters"]["bucketName"]
    key = unquote_plus(event["detail"]["requestParameters"]["key"], encoding="utf-8")
    object = _get_object(bucket=bucket, key=key)
    etag = object["ETag"].strip('"')
    # Fast path, ETag is the md5sum
    if len(etag) == 32 and "-" not in etag:
        return {
            "md5_hash": etag,
            "bucket": bucket,
            "key": key,
        }
    md5_hash = rehash.md5()
    for i, chunk in enumerate(object["Body"].iter_chunks(CHUNKSIZE)):
        md5_hash.update(chunk)
        remaining = context.get_remaining_time_in_millis()
        if remaining < MILLISECONDS_REMAINING_THRESHOLD:
            return {
                "start_byte": (i + 1) * CHUNKSIZE,
                "hash_object": pickle.dumps(md5_hash),
                "bucket": bucket,
                "key": key,
            }
    return {
        "md5_hash": md5_hash.hexdigest(),
        "bucket": bucket,
        "key": key,
    }
