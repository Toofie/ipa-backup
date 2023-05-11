from aws_cdk import (
    Stack,
    aws_iam,
    CfnOutput,
    aws_s3,
    aws_dynamodb,
)
from constructs import Construct
from typing import List

from ipa_backup.constructs.vaults import (
    GoldIpaVaultCustomConstruct,
    PlatinumIpaVaultCustomConstruct,
    SilverIpaVaultCustomConstruct,
)

import json
import os


class IpaBackupStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        cross_account_backup_role_name: str = None,
        silver_vault_name: str = None,
        gold_vault_name: str = None,
        platinum_vault_name: str = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        organization_id = "o-ir30vuy3t4"

        """
        A class for managing AWS Backup resources.

        :type cross_account_backup_role_name: str
        :param silver_vault_name: The name of the AWS Backup silver vault.
            Defaults to "ipa-aws-backup-vault-silver".
        :type silver_vault_name: str
        :param gold_vault_name: The name of the AWS Backup gold vault.
            Defaults to "ipa-aws-backup-vault".
        :type gold_vault_name: str
        :param platinum_vault_name: The name of the AWS Backup platinum vault.
            Defaults to "ipa-aws-backup-vault-continuous".
        :type platinum_vault_name: str
        """

        # Creates a new Silver IPA backup vault for the member account.
        # This is done by instantiating a new SilverIpaVault construct with the specified parameters.
        account_vault = SilverIpaVaultCustomConstruct(
            scope=self,
            construct_id="silver",
            organization_id=organization_id,
            vault_name=silver_vault_name,
        )

        # Creates a new Gold IPA backup vault for the member account.
        # This is done by instantiating a new GoldIpaVault construct with the specified parameters.
        # gold_member_account_vault = GoldIpaVaultCustomConstruct(
        #     scope=self,
        #     construct_id="Gold",
        #     account_role=account_backup_role,
        #     organization_id=organization_id,
        #     vault_name=gold_vault_name,
        # )

        # Creates a new Platinum IPA backup vault for the member account.
        # This is done by instantiating a new PlatinumIpaVault construct with the specified parameters.
        # platinum_member_account_vault = PlatinumIpaVaultCustomConstruct(
        #     scope=self,
        #     construct_id="Platinum",
        #     account_role=account_backup_role,
        #     organization_id=organization_id,
        #     vault_name=platinum_vault_name,
        # )

        # Define the directory path to the external JSON file
        directory = "ipa_backup/ipa_backup_stack_resources.json"

        # Read the resource names from the external JSON file
        with open(os.path.join(directory), "r") as f:
            resources = json.load(f).get(f"{self.account}", {}).get("daily", {})

        # Add the resources to the silver vault's daily backup plan.
        if resources:
            try:
                account_vault.add_resource_to_daily_plan(
                    resource_arns=resources, selection_id="all"
                )
            except Exception as e:
                print(f"Failed to add resources to the daily plan: {e}")
                raise e

        # Read the resource names from the external JSON file
        with open(os.path.join(directory), "r") as f:
            resources = json.load(f).get(f"{self.account}", {}).get("weekly", {})

        if resources:
            try:
                account_vault.add_resource_to_weekly_plan(
                    resource_arns=resources, selection_id="all"
                )
            except Exception as e:
                print(f"Failed to add resources to the weekly plan: {e}")
                raise e

        # Read the resource names from the external JSON file
        with open(os.path.join(directory), "r") as f:
            resources = json.load(f).get(f"{self.account}", {}).get("monthly", {})

        if resources:
            try:
                account_vault.add_resource_to_monthly_plan(
                    resource_arns=resources, selection_id="all"
                )
            except Exception as e:
                print(f"Failed to add resources to the monthly plan: {e}")
                raise e
