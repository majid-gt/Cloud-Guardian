import boto3


def collect_ec2(creds, state):
    """
    Collect EC2 instance inventory and relationships
    and store in CloudState.
    """

    ec2 = boto3.client(
        "ec2",
        aws_access_key_id=creds["aws_access_key_id"],
        aws_secret_access_key=creds["aws_secret_access_key"],
        region_name=creds["region"]
    )

    response = ec2.describe_instances()

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:

            instance_id = instance["InstanceId"]
            instance_state = instance["State"]["Name"]
            instance_type = instance["InstanceType"]

            # Collect security group IDs
            security_groups = [
                sg["GroupId"]
                for sg in instance.get("SecurityGroups", [])
            ]

            # Store EC2 inventory
            state.add_resource(
                "ec2",
                instance_id,
                {
                    "state": instance_state,
                    "instance_type": instance_type,
                    "security_groups": security_groups
                }
            )

            # Build relationships
            for sg_id in security_groups:
                state.add_relation("instance_sg", instance_id, sg_id)
                state.add_relation("sg_instance", sg_id, instance_id)