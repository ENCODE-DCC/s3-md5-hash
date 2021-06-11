import json
from typing import TYPE_CHECKING, Iterator, Optional

import boto3
from boto3.session import Session
import typer

if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client

app = typer.Typer()


@app.command()
def calculate_md5sums(
    bucket: str,
    state_machine_arn: str,
    prefix: Optional[str] = None,
    dry_run: bool = typer.Option(False, help="Only print the objects to update"),
    profile: str = "default",
) -> None:
    session = Session(profile_name=profile)
    s3_client = session.client("s3")
    for key in list_objects(s3_client, bucket, prefix):
        if object_should_be_updated(s3_client, bucket, key):
            if dry_run:
                print(key)
            else:
                trigger_state_machine(state_machine_arn, bucket, key)


def object_should_be_updated(client: "S3Client", bucket: str, key: str) -> bool:
    object_tagging = client.get_object_tagging(Bucket=bucket, Key=key)
    for tag in object_tagging["TagSet"]:
        if tag["Key"] == "md5sum":
            return False
    return True


def trigger_state_machine(state_machine_arn: str, bucket: str, key: str) -> None:
    client = boto3.client("stepfunctions")
    client.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps(
            {
                "detail": {
                    "resources": [{"type": "AWS::S3::Object", "ARN": f"{bucket}/{key}"}]
                }
            }
        ),
    )


def list_objects(
    client: "S3Client", bucket: str, prefix: Optional[str] = None
) -> Iterator[str]:
    if prefix is not None:
        response = client.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
        )
    else:
        response = client.list_objects_v2(
            Bucket=bucket,
        )
    while True:
        for obj in response["Contents"]:
            yield obj["Key"]
        if not response["IsTruncated"]:
            break
        last_key = response["Contents"][-1]["Key"]
        if prefix is not None:
            response = client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                StartAfter=last_key,
            )
        else:
            response = client.list_objects_v2(
                Bucket=bucket,
                StartAfter=last_key,
            )


if __name__ == "__main__":
    app()
