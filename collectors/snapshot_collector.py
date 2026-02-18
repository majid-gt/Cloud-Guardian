import boto3


def collect_snapshots(creds, state):
    """
    Collect EBS snapshot inventory.
    """

    ec2 = boto3.client(
        "ec2",
        aws_access_key_id=creds["aws_access_key_id"],
        aws_secret_access_key=creds["aws_secret_access_key"],
        region_name=creds["region"]
    )

    response = ec2.describe_snapshots(OwnerIds=["self"])

    for snapshot in response["Snapshots"]:

        snapshot_id = snapshot["SnapshotId"]
        volume_id = snapshot.get("VolumeId")
        size = snapshot["VolumeSize"]
        start_time = snapshot["StartTime"]

        state.add_resource(
            "snapshots",
            snapshot_id,
            {
                "volume_id": volume_id,
                "size": size,
                "start_time": start_time
            }
        )