import boto3


def collect_security_groups(creds, state):
    """
    Collect Security Group rules and store in CloudState.
    """

    ec2 = boto3.client(
        "ec2",
        aws_access_key_id=creds["aws_access_key_id"],
        aws_secret_access_key=creds["aws_secret_access_key"],
        region_name=creds["region"]
    )

    response = ec2.describe_security_groups()

    for sg in response["SecurityGroups"]:
        sg_id = sg["GroupId"]

        inbound_rules = sg.get("IpPermissions", [])

        state.add_resource(
            "security_groups",
            sg_id,
            {
                "inbound_rules": inbound_rules
            }
        )