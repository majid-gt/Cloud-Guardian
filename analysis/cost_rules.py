# ======================================================
# PASS 1 — EC2 Classification + Cost Calculation
# ======================================================

def classify_ec2_instances(state):
    """
    Classify EC2 instances and calculate waste cost for idle ones.
    """

    # Approximate hourly pricing (Linux on-demand)
    EC2_PRICING = {
        "t2.micro": 0.0116,
        "t3.micro": 0.0104,
        "t3.small": 0.0208,
        "t3.medium": 0.0416,
        "t2.medium": 0.0464,
        "m5.large": 0.096
    }

    for instance_id, data in state.inventory["ec2"].items():

        instance_state = data.get("state")
        instance_type = data.get("instance_type", "unknown")

        # If stopped, no cost
        if instance_state != "running":
            state.set_compute_status("ec2", instance_id, "stopped")
            continue

        cpu = state.metrics["ec2_cpu"].get(instance_id, 0.0)

        # Idle detection threshold
        if cpu < 5.0:

            state.set_compute_status("ec2", instance_id, "idle")

            hourly_price = EC2_PRICING.get(instance_type, 0.05)
            monthly_cost = round(hourly_price * 24 * 30, 2)

            finding = {
                "category": "cost",
                "service": "EC2",
                "resource_id": instance_id,
                "issue": "Underutilized EC2 Instance",
                "severity": "medium",
                "reason": f"{instance_type} running with low CPU ({cpu:.2f}%)",
                "recommendation": "Stop, resize, or terminate unused instance",
                "estimated_monthly_loss": monthly_cost,
                "confidence": 0.9
            }

            state.add_finding("cost", finding)

        else:
            state.set_compute_status("ec2", instance_id, "active")
            

# ======================================================
# PASS 2 — EBS Waste Detection (Real Cost Calculation)
# ======================================================

def detect_ebs_waste(state):
    """
    Detect unattached EBS volumes and calculate real monthly cost.
    """

    # Approximate EBS pricing per GB per month
    EBS_PRICING = {
        "gp2": 0.10,
        "gp3": 0.08,
        "io1": 0.125,
        "io2": 0.125,
        "st1": 0.045,
        "sc1": 0.025
    }

    for volume_id, data in state.inventory["ebs"].items():

        attached_instance = data.get("attached_to")
        size_gb = data.get("size", 0)
        volume_type = data.get("volume_type", "gp2")

        # If unattached
        if not attached_instance:

            price_per_gb = EBS_PRICING.get(volume_type, 0.10)
            monthly_cost = round(size_gb * price_per_gb, 2)

            finding = {
                "category": "cost",
                "service": "EBS",
                "resource_id": volume_id,
                "issue": "Unattached Volume",
                "severity": "high",
                "reason": f"{size_gb}GB {volume_type} volume not attached to any instance",
                "recommendation": "Delete unused volume to reduce storage cost",
                "estimated_monthly_loss": monthly_cost,
                "confidence": 1.0
            }

            state.add_finding("cost", finding)
            
# ======================================================
# PASS 2 — Elastic IP Waste Detection
# ======================================================

def detect_eip_waste(state):
    """
    Detect unused or wasteful Elastic IP addresses.
    """

    for eip_id, data in state.inventory["eip"].items():

        attached_instance = data.get("attached_to")

        # Case 1: Unattached EIP
        if not attached_instance:
            finding = {
                "category": "cost",
                "service": "Elastic IP",
                "resource_id": eip_id,
                "issue": "Unassociated Elastic IP",
                "severity": "high",
                "reason": "Elastic IP is not associated with any EC2 instance",
                "recommendation": "Release unused Elastic IP to avoid charges",
                "estimated_monthly_loss": 3.5,  # approximate monthly cost
                "confidence": 1.0
            }

            state.add_finding("cost", finding)
            continue

        # Case 2: Attached to idle EC2
        instance_status = state.compute_status["ec2"].get(attached_instance)

        if instance_status == "idle":
            finding = {
                "category": "cost",
                "service": "Elastic IP",
                "resource_id": eip_id,
                "issue": "Elastic IP Attached to Idle Instance",
                "severity": "medium",
                "reason": f"Associated EC2 instance {attached_instance} is underutilized",
                "recommendation": "Stop instance or release Elastic IP if not required",
                "estimated_monthly_loss": 3.5,
                "confidence": 0.9
            }

            state.add_finding("cost", finding)
            
            
from datetime import datetime, timezone


# ======================================================
# SNAPSHOT WASTE DETECTION
# ======================================================

def detect_snapshot_waste(state):
    """
    Detect old or orphaned EBS snapshots.
    """

    SNAPSHOT_PRICE_PER_GB = 0.05
    now = datetime.now(timezone.utc)

    for snapshot_id, data in state.inventory["snapshots"].items():

        volume_id = data.get("volume_id")
        size = data.get("size", 0)
        start_time = data.get("start_time")

        age_days = (now - start_time).days

        volume_exists = volume_id in state.inventory["ebs"]

        # Rule 1 — Snapshot of deleted volume
        if not volume_exists:

            monthly_cost = round(size * SNAPSHOT_PRICE_PER_GB, 2)

            finding = {
                "category": "cost",
                "service": "EBS Snapshot",
                "resource_id": snapshot_id,
                "issue": "Snapshot of Deleted Volume",
                "severity": "medium",
                "reason": f"Snapshot references missing volume {volume_id}",
                "recommendation": "Review and delete unused snapshots",
                "estimated_monthly_loss": monthly_cost,
                "confidence": 0.9
            }

            state.add_finding("cost", finding)

        # Rule 2 — Snapshot older than 30 days
        elif age_days > 30:

            monthly_cost = round(size * SNAPSHOT_PRICE_PER_GB, 2)

            finding = {
                "category": "cost",
                "service": "EBS Snapshot",
                "resource_id": snapshot_id,
                "issue": "Old Snapshot",
                "severity": "low",
                "reason": f"Snapshot is {age_days} days old",
                "recommendation": "Review retention policy for old snapshots",
                "estimated_monthly_loss": monthly_cost,
                "confidence": 0.8
            }

            state.add_finding("cost", finding)