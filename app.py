#!/usr/bin/env python3
import os

import aws_cdk as cdk
import os
from ipa_backup.ipa_backup_stack import IpaBackupStack
from ipa_backup.code_repository_stack import CodeRepoStack
from ipa_backup.pipeline_stack import Pipeline

app = cdk.App()

repository_name = "ipa-backup"

CodeRepoStack(
    scope=app,
    construct_id=f"{repository_name}-code-construct",
    env=cdk.Environment(account="832435373672", region="ap-southeast-2"),
    repository_name=repository_name,
)

Pipeline(
    scope=app,
    construct_id=f"{repository_name}-pipeline-construct",
    branch_name="master",
    repository_name=repository_name,
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.
    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.
    # env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */
    env=cdk.Environment(account="832435373672", region="ap-southeast-2"),
    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
)

app.synth()
