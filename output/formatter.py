from tabulate import tabulate

def display_idle_ec2(idle_instances):
    if not idle_instances:
        print("\n✅ No idle EC2 instances found")
        return

    table = []
    for inst in idle_instances:
        table.append([
            inst["InstanceId"],
            inst["State"],
            inst["IdleDays"],
            f"${inst['MonthlyCostUSD']:.2f}"
        ])

    print("\n⚠️ Idle EC2 Instances Detected:")
    print(tabulate(
        table,
        headers=["Instance ID", "State", "Idle Days", "Monthly Cost ($)"],
        tablefmt="grid"
    ))


def display_unused_ebs(unused_volumes):
    if not unused_volumes:
        print("\n✅ No unused EBS volumes found")
        return

    table = []
    for vol in unused_volumes:
        table.append([
            vol["VolumeId"],
            vol["Size"],
            vol["VolumeType"],
            vol["UnusedDays"],
            f"${vol['MonthlyCostUSD']:.2f}"
        ])

    print("\n⚠️ Unused EBS Volumes Detected:")
    print(tabulate(
        table,
        headers=["Volume ID", "Size (GB)", "Type", "Unused Days", "Monthly Cost ($)"],
        tablefmt="grid"
    ))

