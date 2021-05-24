import logging
import os
from time import sleep
from uuid import uuid4

import boto3
import pytest


@pytest.fixture
def stack_name() -> str:
    stack_name = os.environ.get("AWS_SAM_STACK_NAME")
    if not stack_name:
        raise Exception(
            "Cannot find env var AWS_SAM_STACK_NAME. Please setup this environment "
            "variable with the stack name where we are running integration tests."
        )

    # Verify stack exists
    client = boto3.client("cloudformation")
    try:
        client.describe_stacks(StackName=stack_name)
    except Exception as e:
        raise Exception(
            f"Cannot find stack {stack_name}. \n"
            f'Please make sure stack with the name "{stack_name}" exists.'
        ) from e

    return stack_name


@pytest.fixture
def state_machine_arn(stack_name: str) -> str:
    """
    Based on the provided env variable AWS_SAM_STACK_NAME use cloudformation API to find
    ARN for S3MD5HashStateMachine
    """
    client = boto3.client("cloudformation")
    response = client.list_stack_resources(StackName=stack_name)
    resources = response["StackResourceSummaries"]
    state_machine_resources = [
        resource
        for resource in resources
        if resource["LogicalResourceId"] == "S3MD5HashStateMachine"
    ]
    if not state_machine_resources:
        raise Exception("Cannot find S3MD5HashStateMachine")

    return state_machine_resources[0]["PhysicalResourceId"]


@pytest.fixture
def bucket() -> str:
    return "bucket"


@pytest.fixture
def key() -> str:
    return "key"


@pytest.mark.skip("Requires deploying stack first which is not trivial in CircleCI")
def test_state_machine(bucket: str, key: str, state_machine_arn: str) -> None:
    client = boto3.client("stepfunctions")
    response = client.start_execution(
        stateMachineArn=state_machine_arn,
        name=f"integ-test-{uuid4()}",
        input="{}",
    )
    execution_arn = response["executionArn"]

    while True:
        response = client.describe_execution(executionArn=execution_arn)
        status = response["status"]
        if status == "SUCCEEDED":
            logging.info(f"Execution {execution_arn} completely successfully.")
            break
        elif status == "RUNNING":
            logging.info(f"Execution {execution_arn} is still running, waiting")
            sleep(3)
        else:
            raise RuntimeError(f"Execution {execution_arn} failed with status {status}")

    s3_client = boto3.client("s3")
    tagging = s3_client.get_object_tagging(Bucket=bucket, Key=key)
    assert {"Key": "md5sum", "Value": "mymd5"} in tagging["TagSet"]
