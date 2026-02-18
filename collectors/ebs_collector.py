import boto3


def collect_ebs(creds, state):
    """
    Collect EBS volume inventory and relationships
    and store them in CloudState.
    """

    ec2 = boto3.client(
        "ec2",
        aws_access_key_id=creds["aws_access_key_id"],
        aws_secret_access_key=creds["aws_secret_access_key"],
        region_name=creds["region"]
    )

    response = ec2.describe_volumes()

    for volume in response["Volumes"]:

        volume_id = volume["VolumeId"]
        size = volume["Size"]
        volume_type = volume["VolumeType"]

        attachments = volume.get("Attachments", [])

        if attachments:
            instance_id = attachments[0]["InstanceId"]
        else:
            instance_id = None

        # Store volume inventory
        state.add_resource(
            "ebs",
            volume_id,
            {
                "size": size,
                "volume_type": volume_type,
                "attached_to": instance_id
            }
        )

        # Build relationships
        if instance_id:
            state.add_relation("instance_volumes", instance_id, volume_id)
            state.add_relation("volume_instance", volume_id, instance_id)