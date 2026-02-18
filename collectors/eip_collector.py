import boto3


def collect_eip(creds, state):
    """
    Collect Elastic IP inventory and store in CloudState.
    """

    ec2 = boto3.client(
        "ec2",
        aws_access_key_id=creds["aws_access_key_id"],
        aws_secret_access_key=creds["aws_secret_access_key"],
        region_name=creds["region"]
    )

    response = ec2.describe_addresses()

    for address in response["Addresses"]:
        allocation_id = address.get("AllocationId")
        public_ip = address.get("PublicIp")
        instance_id = address.get("InstanceId")  # may be None

        resource_id = allocation_id if allocation_id else public_ip

        # Store inventory
        state.add_resource(
            "eip",
            resource_id,
            {
                "public_ip": public_ip,
                "attached_to": instance_id
            }
        )

        # Build relation if attached
        if instance_id:
            state.add_relation("instance_eip", instance_id, resource_id)