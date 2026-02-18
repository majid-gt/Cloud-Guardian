# ======================================================
# SECURITY RULE — OPEN PORT DETECTION
# ======================================================

def detect_open_security_groups(state):
    """
    Smart security group exposure detection (no duplicates).
    """

    for sg_id, data in state.inventory["security_groups"].items():

        inbound_rules = data.get("inbound_rules", [])

        attached_instances = state.relations.get("sg_instance", {}).get(sg_id, [])
        is_attached = len(attached_instances) > 0

        exposure_types = set()

        for rule in inbound_rules:

            ip_ranges = rule.get("IpRanges", [])
            from_port = rule.get("FromPort")

            for ip_range in ip_ranges:
                cidr = ip_range.get("CidrIp")

                if cidr != "0.0.0.0/0":
                    continue

                if from_port is None:
                    exposure_types.add("all_ports")
                elif from_port == 22:
                    exposure_types.add("ssh")
                elif from_port == 3389:
                    exposure_types.add("rdp")
                else:
                    exposure_types.add("other")

        # If nothing exposed, skip
        if not exposure_types:
            continue

        # Determine highest severity
        if not is_attached:
            severity = "low"
            issue = "Open Port (Unused Security Group)"
        elif "all_ports" in exposure_types:
            severity = "critical"
            issue = "All Ports Open to Internet"
        elif "ssh" in exposure_types:
            severity = "high"
            issue = "SSH Port Open to Internet"
        elif "rdp" in exposure_types:
            severity = "high"
            issue = "RDP Port Open to Internet"
        else:
            severity = "medium"
            issue = "Public Port Exposure"

        finding = {
            "category": "security",
            "service": "Security Group",
            "resource_id": sg_id,
            "issue": issue,
            "severity": severity,
            "reason": "Inbound access from 0.0.0.0/0 detected",
            "recommendation": "Validate necessity of public exposure and restrict to trusted IP ranges if not required.",
            "estimated_monthly_loss": 0,
            "confidence": 0.8
        }

        state.add_finding("security", finding)


from datetime import datetime, timezone


# ======================================================
# IAM UNUSED ACCESS KEY DETECTION
# ======================================================

def detect_unused_iam_keys(state):
    """
    Detect IAM access keys unused for 90+ days.
    """

    now = datetime.now(timezone.utc)

    for username, data in state.inventory["iam_users"].items():

        access_keys = data.get("access_keys", [])

        # Case 1: Two active keys
        active_keys = [k for k in access_keys if k["status"] == "Active"]

        if len(active_keys) >= 2:
            finding = {
                "category": "security",
                "service": "IAM",
                "resource_id": username,
                "issue": "Multiple Active Access Keys",
                "severity": "medium",
                "reason": "User has multiple active access keys",
                "recommendation": "Disable unused keys to follow least privilege principle",
                "estimated_monthly_loss": 0,
                "confidence": 1.0
            }

            state.add_finding("security", finding)

        # Case 2: Key unused for 90+ days
        for key in access_keys:
            last_used = key.get("last_used")

            if not last_used:
                continue

            days_unused = (now - last_used).days

            if days_unused > 90:
                finding = {
                    "category": "security",
                    "service": "IAM",
                    "resource_id": username,
                    "issue": "Unused Access Key",
                    "severity": "medium",
                    "reason": f"Access key unused for {days_unused} days",
                    "recommendation": "Rotate or delete unused access key",
                    "estimated_monthly_loss": 0,
                    "confidence": 0.9
                }

                state.add_finding("security", finding)