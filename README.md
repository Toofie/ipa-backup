# IPA Backup Vaults

This repository contains the source code for managing AWS Backup resources with different backup classes: Silver, Gold, and Platinum. The code is written using the AWS Cloud Development Kit (CDK) in Python.

## Table of Contents

- [IPA Backup Vaults](#ipa-backup-vaults)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
    - [AWS Backup Vault Service Levels: Silver, Gold, and Platinum](#aws-backup-vault-service-levels-silver-gold-and-platinum)
  - [Background](#background)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Updating](#updating)
  - [AWS Services Overview](#aws-services-overview)
    - [AWS Backup](#aws-backup)
    - [AWS Key Management Service (KMS)](#aws-key-management-service-kms)
    - [AWS Identity and Access Management (IAM)](#aws-identity-and-access-management-iam)
    - [AWS Cloud Development Kit (CDK)](#aws-cloud-development-kit-cdk)
  - [Support](#support)
  - [License](#license)

## Overview

The code in this repository creates AWS Backup vaults with different configurations, depending on the backup class (Silver, Gold, or Platinum). Each backup vault has an associated AWS Key Management Service (KMS) key for encryption and an access policy that restricts access to the vault.

The main classes included in the code are:

- `SilverIpaVault`: Creates a Silver backup vault.
- `GoldIpaVault`: Inherits from `SilverIpaVault` and creates a Gold backup vault with additional lock configurations.
- `PlatinumIpaVault`: Inherits from `GoldIpaVault` and creates a Platinum backup vault.
- `IpaBackupStack`: Creates a new IAM role for cross-account AWS Backup access and instantiates Silver, Gold, and Platinum backup vaults.

### AWS Backup Vault Service Levels: Silver, Gold, and Platinum

The provided code creates three different backup vaults using AWS Backup, each with a different service level: Silver, Gold, and Platinum. The main differences between these vaults are in their naming and, in the case of the Gold vault, additional lock configuration settings. 

1. **SilverIpaVault**: This class creates a Silver-level backup vault with the specified name (defaulting to "ipa-aws-backup-vault-silver"). It uses the provided account role and organization ID to create the vault and the associated AWS KMS key for encryption. The class value is set to "silver".

2. **GoldIpaVault**: This class inherits from SilverIpaVault and creates a Gold-level backup vault. It uses the same process as the SilverIpaVault but sets the default name to "ipa-aws-backup-vault" and the class value to "gold". Additionally, it includes lock configuration settings in the backup vault with the following values:
   - ChangeableForDays: 14
   - MaxRetentionDays: 35
   - MinRetentionDays: 1

3. **PlatinumIpaVault**: This class inherits from GoldIpaVault and creates a Platinum-level backup vault. It uses the same process as the GoldIpaVault but sets the default name to "ipa-aws-backup-vault-continuous" and the class value to "platinum". There are no additional changes compared to the GoldIpaVault.

The IpaBackupStack class then creates instances of these three vaults with the specified parameters. The main differences between the Silver, Gold, and Platinum vaults are in their naming and the lock configuration settings in the Gold vault.

## Background

The purpose of this repository is to capture the proposed infrastructure for the implementation of backup strategies for IP Australia's data assets stored on AWS storage and database services. While infrastructure as code provides a stateless approach, data maintains state, and assuming everything can be captured as infrastructure as code is flawed. Therefore, this repository supplements infrastructure as code by encapsulating the implementation of AWS Backup, the service used to capture data state of resources.

Please note that the initial iteration of this repository is based solely on CloudFormation templates and JSON documents that include all input parameters for the CloudFormation templates. The supporting documentation consists only of a collection of screenshots. With this repository, our aim is to improve and streamline the process by providing a complete and comprehensive solution implemented using AWS CDK. We hope that this will provide a more efficient and effective way to capture data state and ensure reliable backup strategies for IP Australia's data assets on AWS storage and database services.

## Requirements

- Python 3.7 or later
- AWS CDK v2.0 or later
- AWS CLI v2 or later
- An AWS account and the necessary permissions to create the required resources

## Installation

1. Clone the repository:

```
git clone https://github.com/your-repo/ipa-backup-vaults.git
cd ipa-backup-vaults
```

2. Create a virtual environment and activate it:

```
python3 -m venv .venv
source .venv/bin/activate
```

3. Install the required packages:

```
pip install -r requirements.txt
```

4. Configure the AWS CLI with your AWS account credentials:

```
aws configure
```

## Usage

1. Compile the AWS CDK app:

```
cdk synth
```

2. Deploy the AWS CDK app:

```
cdk deploy
```

3. To destroy the resources created by the CDK app:

```
cdk destroy
```

## Updating

To update or add more resources to be backed up, you will need to modify the `ipa_backup\ipa_backup_stack_resources.json` file. This file defines what needs to be backed up for each AWS account.

The format of the `ipa_backup_stack_resources.json` file is as follows:

```java
{
    "<AWS_ACCOUNT_ID>": {
        "daily": [
            "<RESOURCE_ARN_1>",
            "<RESOURCE_ARN_2>",
            ...
        ],
        "weekly": [
            "<RESOURCE_ARN_1>",
            "<RESOURCE_ARN_2>",
            ...
        ],
        "monthly": [
            "<RESOURCE_ARN_1>",
            "<RESOURCE_ARN_2>",
            ...
        ]
    },
    "<ANOTHER_AWS_ACCOUNT_ID>": {
        ...
    },
    ...
}
```

To update an existing resource, simply add or remove the resource ARN from the appropriate daily or weekly array.

To add a new resource, follow these steps:

1. Determine the AWS account ID for the account that the resource belongs to.
2. Add a new key-value pair to the `ipa_backup_stack_resources.json` file with the AWS account ID as the key and an empty dictionary as the value.
3. Add the new resource ARN to the appropriate daily or weekly array for the AWS account.

For example, suppose you want to add a new S3 bucket to be backed up for the AWS account with ID `123456789012`. You would modify the `ipa_backup_stack_resources.json` file as follows:

```java
{
    "123456789012": {
        "daily": [
            "arn:aws:s3:::existing-bucket",
            "arn:aws:s3:::new-bucket"
        ],
        "weekly": [
            "arn:aws:s3:::existing-bucket"
        ]
    },
    ...
}
```


After modifying the `ipa_backup_stack_resources.json` file, you will need to run the CDK commands `cdk synth` and `cdk deploy` to update the AWS Backup resources with the new or modified resources to be backed up.

## AWS Services Overview

This project uses several AWS services to manage and secure backup resources. Here is a brief overview of the AWS services involved:

### AWS Backup

AWS Backup is a fully managed backup service that makes it easy to centralize and automate the backup of data across AWS services. It provides a cost-effective, fully managed, policy-based service to simplify the backup and restore process.

AWS Backup can be used to protect a wide range of AWS services, such as Amazon EBS volumes, Amazon RDS databases, Amazon DynamoDB tables, Amazon EFS file systems, and AWS Storage Gateway volumes.

For more information, visit the [AWS Backup product page](https://aws.amazon.com/backup/).

### AWS Key Management Service (KMS)

AWS Key Management Service (KMS) is a managed service that makes it easy for you to create and control the cryptographic keys used to encrypt your data. AWS KMS is integrated with other AWS services to help you protect the data you store with these services and control access to the keys that decrypt it.

In this project, AWS KMS is used to create and manage keys used for encrypting backup data stored in the backup vaults.

For more information, visit the [AWS KMS product page](https://aws.amazon.com/kms/).

### AWS Identity and Access Management (IAM)

AWS Identity and Access Management (IAM) enables you to manage access to AWS services and resources securely. With IAM, you can create and manage AWS users and groups, and use permissions to allow and deny their access to AWS resources.

In this project, IAM is used to create a cross-account backup role that allows AWS Backup to access the required resources for backup and restore operations.

For more information, visit the [AWS IAM product page](https://aws.amazon.com/iam/).

### AWS Cloud Development Kit (CDK)

The AWS Cloud Development Kit (CDK) is an open-source software development framework for defining cloud infrastructure as code (IAC) and provisioning it through AWS CloudFormation. The AWS CDK provides high-level components called constructs that preconfigure cloud resources with proven defaults, reducing the amount of code you need to write.

This project uses the AWS CDK to define and deploy the necessary infrastructure components, such as the backup vaults, KMS keys, and IAM roles.

For more information, visit the [AWS CDK product page](https://aws.amazon.com/cdk/).

Add this section to your README.md document to provide more context about the AWS services used in the project.


## Support

For any questions or issues related to this code, please open an issue in the GitHub repository or contact the author.

## License

This code is released under the MIT License. See the [LICENSE](LICENSE) file for more information.