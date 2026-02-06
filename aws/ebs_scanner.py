from aws.aws_connector import get_ec2_client

def scan_ebs(creds):
    ec2 = get_ec2_client(creds)
    response = ec2.describe_volumes()

    volumes = []

    for volume in response["Volumes"]:
        volumes.append(volume)

    return volumes
