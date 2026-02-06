from datetime import datetime, timezone

def detect_idle_ec2(instances):
    idle_instances = []

    for inst in instances:
        if inst["State"]["Name"] == "stopped":
            idle_days = (datetime.now(timezone.utc) - inst["LaunchTime"]).days

            idle_instances.append({
                "InstanceId": inst["InstanceId"],
                "State": "stopped",
                "IdleDays": idle_days,
                "MonthlyCostUSD": calculate_ec2_storage_cost()
            })

    return idle_instances


def detect_unused_ebs(volumes):
    unused_volumes = []

    for vol in volumes:
        if vol["State"] == "available":
            unused_days = (datetime.now(timezone.utc) - vol["CreateTime"]).days

            unused_volumes.append({
                "VolumeId": vol["VolumeId"],
                "Size": vol["Size"],
                "VolumeType": vol["VolumeType"],
                "UnusedDays": unused_days,
                "MonthlyCostUSD": calculate_ebs_cost(vol["Size"])
            })

    return unused_volumes



def calculate_ec2_storage_cost():
    # Assume 8 GB root volume
    return 8 * 0.10  # USD per month


def calculate_ebs_cost(size_gb):
    return size_gb * 0.10  # USD per month
