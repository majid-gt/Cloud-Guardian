import boto3
from datetime import datetime, timedelta, timezone


def collect_ec2_metrics(creds, state):
    """
    Collect average CPU utilization for EC2 instances (last 24h).
    """

    if not state.inventory["ec2"]:
        return

    cloudwatch = boto3.client(
        "cloudwatch",
        aws_access_key_id=creds["aws_access_key_id"],
        aws_secret_access_key=creds["aws_secret_access_key"],
        region_name=creds["region"]
    )

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=24)

    for instance_id in state.inventory["ec2"]:

        response = cloudwatch.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=["Average"]
        )

        datapoints = response.get("Datapoints", [])

        if not datapoints:
            avg_cpu = 0.0
        else:
            avg_cpu = sum(d["Average"] for d in datapoints) / len(datapoints)

        state.add_metric("ec2_cpu", instance_id, round(avg_cpu, 2))