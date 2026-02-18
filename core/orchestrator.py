from core.cloud_state import CloudState

class CloudOrchestrator:
    def __init__(self, creds):
        self.creds = creds
        self.state = CloudState()

    # ======================================================
    # MAIN EXECUTION PIPELINE
    # ======================================================

    def run(self):
        print("\n🚀 Starting Cloud Guardian Analysis...\n")

        self.collect_inventory()
        self.collect_metrics()
        self.run_analysis()

        return self.state

    # ======================================================
    # STAGE 1 — INVENTORY COLLECTION
    # ======================================================

    def collect_inventory(self):
        print("🔍 Collecting resource inventory...")

        from collectors.ec2_collector import collect_ec2
        from collectors.ebs_collector import collect_ebs
        from collectors.eip_collector import collect_eip
        from collectors.security_group_collector import collect_security_groups
        from collectors.iam_collector import collect_iam_users
        from collectors.snapshot_collector import collect_snapshots


        collect_ec2(self.creds, self.state)
        collect_ebs(self.creds, self.state)
        collect_eip(self.creds, self.state)
        collect_security_groups(self.creds, self.state)
        collect_iam_users(self.creds, self.state)
        collect_snapshots(self.creds, self.state)

        print(f"   EC2 instances found: {len(self.state.inventory['ec2'])}")
        print(f"   EBS volumes found: {len(self.state.inventory['ebs'])}")
        print(f"   Elastic IPs found: {len(self.state.inventory['eip'])}")
        print(f"   Security Groups found: {len(self.state.inventory['security_groups'])}")
        print(f"   IAM Users found: {len(self.state.inventory['iam_users'])}")
        print(f"   Snapshots found: {len(self.state.inventory['snapshots'])}")

        print("✅ Inventory collection completed.\n")

    # ======================================================
    # STAGE 2 — METRICS COLLECTION
    # ======================================================

    def collect_metrics(self):
        print("📊 Collecting utilization metrics...")

        from metrics.ec2_metrics import collect_ec2_metrics

        collect_ec2_metrics(self.creds, self.state)

        print(f"   EC2 CPU metrics collected: {len(self.state.metrics['ec2_cpu'])}")

        print("✅ Metrics collection completed.\n")

    # ======================================================
    # STAGE 3 — RULE ANALYSIS
    # ======================================================

    def run_analysis(self):
        print("🧠 Running rule engine...")
        
        from analysis.security_rules import detect_open_security_groups
        from analysis.security_rules import detect_unused_iam_keys
        from analysis.cost_rules import detect_snapshot_waste
        from analysis.cost_rules import (
            classify_ec2_instances,
            detect_ebs_waste,
            detect_eip_waste
        )

        # PASS 1
        classify_ec2_instances(self.state)

        # PASS 2
        detect_ebs_waste(self.state)
        detect_eip_waste(self.state)
        detect_open_security_groups(self.state)
        detect_unused_iam_keys(self.state)
        detect_snapshot_waste(self.state)

        print("   EC2 classification completed.")
        print("   Findings generated:", self.state.get_total_findings())

        print("✅ Analysis completed.\n")