import boto3
from datetime import datetime, timezone


def collect_iam_users(creds, state):
    """
    Collect IAM users and access key metadata.
    """

    iam = boto3.client(
        "iam",
        aws_access_key_id=creds["aws_access_key_id"],
        aws_secret_access_key=creds["aws_secret_access_key"],
        region_name=creds["region"]
    )

    users = iam.list_users()["Users"]

    for user in users:
        username = user["UserName"]

        access_keys = iam.list_access_keys(UserName=username)["AccessKeyMetadata"]

        user_data = {
            "access_keys": []
        }

        for key in access_keys:
            key_id = key["AccessKeyId"]

            last_used_info = iam.get_access_key_last_used(AccessKeyId=key_id)
            last_used_date = last_used_info.get("AccessKeyLastUsed", {}).get("LastUsedDate")

            user_data["access_keys"].append({
                "key_id": key_id,
                "status": key["Status"],
                "last_used": last_used_date
            })

        state.add_resource("iam_users", username, user_data)
