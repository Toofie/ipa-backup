from aws_cdk import (
    aws_iam,
    CfnOutput,
    aws_kms,
    aws_backup,
    Tags,
    RemovalPolicy,
)
from constructs import Construct
from typing import List


class SilverIpaVaultCustomConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        organization_id: str,
        vault_name: str = None,
        class_value: str = "silver",
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The role is assumed by the AWS Backup service principal, and has two managed policies for backup and restore.
        account_backup_role = aws_iam.Role(
            scope=self,
            id="backup-role",
            assumed_by=aws_iam.ServicePrincipal(service="backup.amazonaws.com"),
            description="Alows AWS backup to access AWS services",
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    managed_policy_name="service-role/AWSBackupServiceRolePolicyForBackup"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    managed_policy_name="service-role/AWSBackupServiceRolePolicyForRestores"
                ),
                # there are additional managed policies to provide access to s3 resources
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    managed_policy_name="AWSBackupServiceRolePolicyForS3Backup"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    managed_policy_name="AWSBackupServiceRolePolicyForS3Restore"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    managed_policy_name="AmazonSSMManagedInstanceCore"
                ),
            ],
        )

        existing_iam_role = aws_iam.Role.from_role_name(
            scope=self,
            id="ec2-role-for-ssm",
            role_name="AmazonEC2RoleForSSM",
        )
        # add more permissions to be able to pass a service role for ssm
        ssm_permissions_policy = aws_iam.Policy(
            scope=self,
            id="iam-pass-role",
            statements=[
                aws_iam.PolicyStatement(
                    actions=[
                        "iam:PassRole",
                    ],
                    resources=[existing_iam_role.role_arn],
                )
            ],
        )
        account_backup_role.attach_inline_policy(ssm_permissions_policy)

        # Creates a new CloudFormation output for the cross-account AWS Backup role ARN.
        # This output can be used to reference the role from other CloudFormation stacks.
        account_backup_role_output = CfnOutput(
            scope=self,
            id="backup-role-arn-output",
            value=account_backup_role.role_arn,
        )

        # Creates a new AWS KMS key that will be used for encrypting backups in a member account.
        # The key is created with key rotation enabled, and a description is provided for clarity.
        member_account_backup_key = aws_kms.Key(
            scope=self,
            id="MemberAccountBackupKey",
            description="Symmetric AWS CMK for Member account Backup Vault Encryption",
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Grants the specified IAM role permission to use the AWS KMS key for encryption and decryption.
        member_account_backup_key.grant_encrypt_decrypt(grantee=account_backup_role)
        self.account_role = account_backup_role

        # Creates an AWS KMS key alias for the member account backup key.
        # The alias name is generated dynamically based on the class value,
        # and the alias is associated with the member account backup key.
        # member_account_backup_key_alias = aws_kms.Alias(
        #     scope=self,
        #     id="MemberAccountBackupKeyAlias",
        #     alias_name=f"aws-backup-key-{class_value}",
        #     target_key=member_account_backup_key,
        # )

        # Creates a new AWS Backup vault for storing backups in the member account.
        # The vault is associated with the member account backup key for encryption,
        # and an access policy is specified to restrict access to the vault.
        self.member_account_backup_vault = aws_backup.BackupVault(
            scope=self,
            id="MemberAccountBackupVault",
            backup_vault_name=vault_name,
            encryption_key=member_account_backup_key,
            access_policy=aws_iam.PolicyDocument(
                minimize=True,
                statements=[
                    aws_iam.PolicyStatement(
                        actions=["backup:CopyIntoBackupVault"],
                        resources=["*"],
                        principals=[aws_iam.AnyPrincipal()],
                        conditions={
                            "StringEquals": {"aws:PrincipalOrgID": organization_id}
                        },
                    )
                ],
            ),
            removal_policy=RemovalPolicy.DESTROY,
            block_recovery_point_deletion=False,
        )
        # set the aws vault as the default for this construct
        self.node.default_child = self.member_account_backup_vault

        # Overrides the "Class" tag value for the member account backup vault.
        # This is done by accessing the default CloudFormation resource for the vault,
        # and adding an override for the "Class" tag to the specified class value.
        cfn_vault = self.member_account_backup_vault.node.default_child
        cfn_vault.add_override("Properties.BackupVaultTags.Class", class_value)

        # Then we add some backup plans
        self.weekly_plan = aws_backup.BackupPlan(
            scope=self,
            id="WeeklyIPABackupPlan",
        )
        self.monthly_plan = aws_backup.BackupPlan(
            scope=self,
            id="MonthlyIPABackupPlan",
        )
        self.daily_plan = aws_backup.BackupPlan(
            scope=self,
            id="DailyIPABackupPlan",
        )
        # Then we add each of the rules these generally follow the same configuration as the template
        self.weekly_plan.add_rule(
            aws_backup.BackupPlanRule.weekly(
                backup_vault=self.member_account_backup_vault
            )
        )
        self.monthly_plan.add_rule(
            aws_backup.BackupPlanRule.monthly1_year(
                backup_vault=self.member_account_backup_vault
            )
        )
        self.daily_plan.add_rule(
            aws_backup.BackupPlanRule.daily(
                backup_vault=self.member_account_backup_vault
            )
        )

        # Adds a "Class" tag to the AWS CDK construct with the specified class value.
        # This tag can be used to identify and group related constructs in the AWS console.
        Tags.of(self).add(key="Class", value=class_value)

        # Creates new CloudFormation outputs for the member account backup vault and key ARNs.
        # These outputs can be used to reference the resources from other CloudFormation stacks.
        member_account_backup_vault_output = CfnOutput(
            scope=self,
            id="MemberAccountBackupVaultOutput",
            value=self.member_account_backup_vault.backup_vault_arn,
        )
        member_account_backup_key_output = CfnOutput(
            scope=self,
            id="MemberAccountBackupKeyOutput",
            value=member_account_backup_key.key_arn,
        )

    def add_resource_to_daily_plan(self, resource_arns: List[str], selection_id: str):
        resources = [aws_backup.BackupResource.from_arn(arn) for arn in resource_arns]
        aws_backup.BackupSelection(
            scope=self,
            id=f"DailyBackupSelection-{selection_id}",
            backup_plan=self.daily_plan,
            resources=resources,
            role=self.account_role,
        )

    def add_resource_to_weekly_plan(self, resource_arns: List[str], selection_id: str):
        resources = [aws_backup.BackupResource.from_arn(arn) for arn in resource_arns]
        aws_backup.BackupSelection(
            scope=self,
            id=f"WeeklyBackupSelection-{selection_id}",
            backup_plan=self.weekly_plan,
            resources=resources,
            role=self.account_role,
        )

    def add_resource_to_monthly_plan(self, resource_arns: List[str], selection_id: str):
        resources = [aws_backup.BackupResource.from_arn(arn) for arn in resource_arns]
        aws_backup.BackupSelection(
            scope=self,
            id=f"MonthlyBackupSelection-{selection_id}",
            backup_plan=self.monthly_plan,
            resources=resources,
            role=self.account_role,
        )


class GoldIpaVaultCustomConstruct(SilverIpaVaultCustomConstruct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        organization_id: str,
        vault_name: str = None,
        class_value: str = "gold",
        **kwargs,
    ) -> None:
        super().__init__(
            scope,
            construct_id,
            organization_id,
            vault_name,
            class_value,
            **kwargs,
        )

        # Overrides the lock configuration values for the default backup vault in the current stack.
        # This is done by iterating over the children of the current stack,
        # identifying the default backup vault, and adding overrides for the desired lock configuration values.
        for child in self.node.children:
            if isinstance(child, aws_backup.BackupVault):
                vault = child
                break
        cfn_vault = vault.node.default_child
        cfn_vault.add_override("Properties.LockConfiguration.ChangeableForDays", 14)
        cfn_vault.add_override("Properties.LockConfiguration.MaxRetentionDays", 35)
        cfn_vault.add_override("Properties.LockConfiguration.MinRetentionDays", 1)

        # Display a warning message about the cooling off period in red color
        print(
            "\033[91m"
            + "WARNING: This AWS Backup Vault is set to compliance mode. Once created, it cannot be deleted or modified by the root or AWS after a period of 14 days."
            + "\033[0m"
        )


class PlatinumIpaVaultCustomConstruct(GoldIpaVaultCustomConstruct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        organization_id: str,
        vault_name: str = None,
        class_value: str = "platinum",
        **kwargs,
    ) -> None:
        super().__init__(
            scope,
            construct_id,
            organization_id,
            vault_name,
            class_value,
            **kwargs,
        )
