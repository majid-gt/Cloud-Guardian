import getpass
import boto3
from botocore.exceptions import ClientError

def prompt_for_credentials():
    print("\nEnter AWS Credentials")

    access_key = input("AWS Access Key ID: ").strip()
    secret_key = getpass.getpass("AWS Secret Access Key: ").strip()
    region = input("AWS Region (e.g. us-east-1): ").strip()

    return {
        "aws_access_key_id": access_key,
        "aws_secret_access_key": secret_key,
        "region": region
    }

def validate_credentials(creds):
    try:
        sts = boto3.client(
            "sts",
            aws_access_key_id=creds["aws_access_key_id"],
            aws_secret_access_key=creds["aws_secret_access_key"],
            region_name=creds["region"]
        )

        identity = sts.get_caller_identity()
        return True, identity

    except ClientError as e:
        return False, str(e)
