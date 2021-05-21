import pickle
from typing import TYPE_CHECKING, Any, Dict

import boto3

if TYPE_CHECKING:
    from aws_lambda_typing import Context
    from mypy_boto3_s3.type_defs import GetObjectOutputTypeDef

CHUNKSIZE = 8192
MILLISECONDS_REMAINING_THRESHOLD = 1000 * 10


def _get_object(
    bucket: str, key: str, start_byte: int
) -> "GetObjectOutputTypeDef":  # pragma: no cover
    client = boto3.client("s3")
    return client.get_object(Bucket=bucket, Key=key, Range=f"{start_byte}-")


def lambda_handler(event: Dict[str, Any], context: "Context") -> Dict[str, Any]:
    bucket = event["bucket"]
    key = event["key"]
    start_byte = event["start_byte"]
    object = _get_object(bucket=bucket, key=key, start_byte=start_byte)
    md5_hash = pickle.loads(bytes.fromhex(event["hash_object"]))
    for i, chunk in enumerate(object["Body"].iter_chunks(CHUNKSIZE)):
        md5_hash.update(chunk)
        remaining = context.get_remaining_time_in_millis()
        if remaining < MILLISECONDS_REMAINING_THRESHOLD:
            return {
                "start_byte": (i + 1) * CHUNKSIZE + start_byte,
                "hash_object": pickle.dumps(md5_hash).hex(),
                "bucket": bucket,
                "key": key,
            }
    return {
        "md5_hash": md5_hash.hexdigest(),
        "bucket": bucket,
        "key": key,
    }
