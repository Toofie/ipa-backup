# import the classes from the cdk library
from aws_cdk import (
    Stack,
    Stage,
    pipelines,
    aws_codecommit,
    Stage,
    Environment,
)
from constructs import Construct

from ipa_backup.ipa_backup_stack import IpaBackupStack


# create a stage for deployment of the solution into the target account and region
class DeploymentStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # create a instance of the intended class, i.e. the cloudformation stack
        stack = IpaBackupStack(
            scope=self,
            construct_id="stage",
            env=Environment(account="832435373672", region="ap-southeast-2"),
            silver_vault_name="ipa-backup-vault-silver",
        )


class Pipeline(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        repository_name: str,
        branch_name: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # create a reference to the existing repository
        existing_repository = aws_codecommit.Repository.from_repository_name(
            scope=self, id="existing-repository", repository_name=repository_name
        )
        # so we want to create a new pipeline for the code to be deployed
        pipeline = pipelines.CodePipeline(
            scope=self,
            id="pipeline",
            synth=pipelines.ShellStep(  # the commands required to complete the synthesis
                id="synth",
                input=pipelines.CodePipelineSource.code_commit(  # pull the code from code commit
                    repository=existing_repository,
                    branch=branch_name,  # refer to the master branch
                ),
                commands=[
                    # "python -m pytest tests/unit -v",
                    "cdk synth",
                ],  # the actual synthesis command
                install_commands=[
                    "npm install -g aws-cdk",  # install the cdk sdk
                    "python -m pip install -r requirements.txt",  # install the python libraries to support the cdk application
                    "python -m pip install -r requirements-dev.txt",  # install the python libraries that are used for testing only
                ],
            ),
        )
        # add a stage to the pipeline to deploy the solution into the development environment - local account for now.
        deployment_stage = DeploymentStage(
            scope=self,
            construct_id=self.stack_name + "-" + branch_name,
        )
        stage = pipeline.add_stage(stage=deployment_stage)
