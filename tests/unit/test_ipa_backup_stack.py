import aws_cdk as core
import aws_cdk.assertions as assertions

from ipa_backup.ipa_backup_stack import IpaBackupStack


# example tests. To run these tests, uncomment this file along with the example
# resource in ipa_backup/ipa_backup_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = IpaBackupStack(app, "ipa-backup")
    template = assertions.Template.from_stack(stack)


#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
