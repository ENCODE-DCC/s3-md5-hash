import pickle
from typing import TYPE_CHECKING, Any, Dict
from urllib.parse import unquote_plus

import boto3
import rehash

if TYPE_CHECKING:
    from aws_lambda_typing import Context

CHUNKSIZE = 8192
MILLISECONDS_REMAINING_THRESHOLD = 1000 * 10


def lambda_handler(event: Dict[str, Any], context: "Context") -> Dict[str, Any]:
    client = boto3.client("s3")
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = unquote_plus(event["Records"][0]["s3"]["object"]["key"], encoding="utf-8")
    object = client.get_object(Bucket=bucket, Key=key)
    etag = object["ETag"].strip('"')
    if len(etag) == 32 and "-" not in etag:
        return {"md5_done": True}
    md5_hash = rehash.md5()
    for i, chunk in enumerate(object["Body"].iter_chunks(CHUNKSIZE)):
        remaining = context.get_remaining_time_in_millis()
        if remaining < MILLISECONDS_REMAINING_THRESHOLD:
            return {
                "index": i,
                "hash": pickle.dumps(md5_hash),
                "bucket": bucket,
                "key": key,
            }
        md5_hash.update(chunk)
    return {"hash": pickle.dumps(md5_hash)}
