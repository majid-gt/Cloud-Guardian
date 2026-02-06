from aws.aws_connector import get_ec2_client
from tabulate import tabulate

def scan_ec2(creds):
    ec2 = get_ec2_client(creds)
    response = ec2.describe_instances()

    instances = []

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instances.append(instance)

    return instances
