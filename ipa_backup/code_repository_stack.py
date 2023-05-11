from aws_cdk import (
    Stack,
    aws_codecommit,
    aws_s3_assets,
)
from constructs import Construct
from shutil import copytree, ignore_patterns, rmtree, make_archive
from os import path, remove


dirname = path.dirname(__file__)


class CodeRepoStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, repository_name: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # directory where all the code is stored
        parent = path.join(dirname, "../")
        # staging location for files to be compressed
        build = path.join(dirname, "../build/")
        # copy the whole file tree over except some of the following
        copytree(
            parent,
            build,
            ignore=ignore_patterns(
                ".venv", "cdk.out", "*.zip", ".git", "*__python__", "*,pyc"
            ),
        )
        # make a zip file with all the staged files
        seed_file_path = make_archive("code-commit-repo-seed", "zip", build)
        # then delete the staged files
        rmtree(build)
        # use the zip as a artefact
        seed_artifact = aws_s3_assets.Asset(
            scope=self, id="seed-artefact", path=seed_file_path
        )
        # then just delete the built file at the end
        remove(seed_file_path)
        # create a new repository
        code_repo = aws_codecommit.CfnRepository(
            scope=self,  # the scope of this object
            id="code-repository",  # the logical id for this resource
            repository_name=repository_name,  # the name of the repository
            code=aws_codecommit.CfnRepository.CodeProperty(  # we're going to seed the current working directory into the repo
                s3=aws_codecommit.CfnRepository.S3Property(
                    bucket=seed_artifact.s3_bucket_name, key=seed_artifact.s3_object_key
                ),
                branch_name="master",  # the branch that will used for the seed
            ),
            repository_description="This is an implementation of AWS Backup",
        )
