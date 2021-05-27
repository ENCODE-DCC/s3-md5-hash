# s3-md5-hash

This is a serverless AWS application for calculating md5 hashes of objects in S3. When new objects are added to the specified bucket a Step Functions State Machine will be triggered that will calculate the md5sum.

This repo was created using `sam init` from the [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-init.html) using the built-in Step Functions sample app (Stock Trader) template.

## Deployment

First install the [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html). Then run the following to build the Lambda functions:

```bash
sam build
```

> Note: You must run this even if you only change the template.yaml

To deploy, run the following:

```bash
sam deploy --guided
```

If you have a specific environment saved in `samconfig.toml`, e.g. `test`, you can use it for deployment like this:

```bash
sam deploy --guided --config-env test
```

This will package and deploy your application to AWS, with prompts. When prompted for `[Y/n]` enter `Y`. For an existing environment you should accept all the pre-supplied values. For a new environment you will need to type in the values for `Stack Name`, `AWS Region`, `Parameter eventSourceBucket`, and `SAM configuration environment`. These parameters are explained below:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to the account and region.
* **AWS Region**: The AWS region to deploy the app to.
* **Parameter eventSourceBucket**: The bucket for which to enable tagging objects with their md5sum. This should be in the region specified above.
* **SAM configuration environment**: The name of the configuration environment to save to.

After deployment, you should commit and PR the changes to `samconfig.toml`. It is meant to be maintained in version control.

### Deleting the deployment

First, delete all objects in the CloudTrail bucket. it should have a name of the form `${STACK_NAME}-cloudtrailbucket-XXXX`. Then, delete the CloudFormation stack, replacing `$STACK_NAME`, `$REGION`, and `$PROFILE` with the name of the CloudFormation stack, the region the stack is located in, and the name of the appropriate profile in your `~/.aws/credentials` file, respectively:

```bash
aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION --profile $PROFILE
```

## Development

Linting/formatting and tests are set up via tox. Install the dev dependencies then run tox with the appropriate arguments.

```bash
s3-md5-hash$ pip install -r requirements-dev.txt
# Run linting and formatting
s3-md5-hash$ tox -e lint
# Run unit tests
s3-md5-hash$ tox -e py38
```

To install all the Lambda dependencies install all three of the `requirements.txt` files in a `venv`, they are located in each function's respective directory.

If your editor/IDE is set up to check files with `mypy` then you should install the `aws-lambda-typing` and `boto3-stubs` plugin, see [pre-commit config](./.pre-commit-config.yaml) for exact versions.

For VS Code users, the `AWS Toolkit` and `CloudFormation Linter` extensions are recommended. The first will allow you to lint and interactively visualize the state machine definition.
