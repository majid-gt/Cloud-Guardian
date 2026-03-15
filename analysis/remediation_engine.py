import boto3


class RemediationEngine:

    def __init__(self, creds, cloud_state):
        self.creds = creds
        self.state = cloud_state

        self.ec2 = boto3.client(
            "ec2",
            aws_access_key_id=creds["aws_access_key_id"],
            aws_secret_access_key=creds["aws_secret_access_key"],
            region_name=creds["region"]
        )


    def execute(self):

        findings = self.state.get_all_findings()

        fixes = []

        for category, items in findings.items():
            for f in items:

                issue = f["issue"].lower()

                # Unattached EBS Volume
                if "unattached" in issue and "volume" in issue:
                    fixes.append(("delete_volume", f["resource_id"]))

                # Unassociated Elastic IP
                elif "elastic ip" in issue and "unassociated" in issue:
                    fixes.append(("release_eip", f["resource_id"]))

                # Elastic IP attached to stopped instance
                elif "elastic ip" in issue and "stopped" in issue:
                    fixes.append(("detach_eip", f["resource_id"]))



        if not fixes:
            print("No auto-fixable issues found.")
            return

        print("\nFix Plan:\n")

        for action, resource in fixes:
            print(f"{action} → {resource}")

        confirm = input("\nProceed with remediation? (y/n): ")

        if confirm.lower() != "y":
            print("Aborted.")
            return

        for action, resource in fixes:

            if action == "delete_volume":
                self.ec2.delete_volume(VolumeId=resource)

            elif action == "release_eip":
                self.ec2.release_address(AllocationId=resource)

            elif action == "detach_eip":
                self.ec2.disassociate_address(AssociationId=resource)


        print("\nRemediation complete.")
