from tabulate import tabulate


def display_findings(state):
    findings = state.get_all_findings()

    if state.get_total_findings() == 0:
        print("\n✅ No issues detected. Cloud looks healthy.\n")
        return

    print("\n========== CLOUD FINDINGS ==========\n")

    # Severity weights for priority calculation
    severity_weight = {
        "CRITICAL": 5,
        "HIGH": 4,
        "MEDIUM": 3,
        "LOW": 2,
        "INFO": 1
    }

    for category, items in findings.items():

        if not items:
            continue

        print(f"\n🔎 Category: {category.upper()}")

        # Sort findings by priority (severity × cost impact)
        sorted_items = sorted(
            items,
            key=lambda x: severity_weight.get(
                x["severity"].upper(), 1
            ) * x.get("estimated_monthly_loss", 0),
            reverse=True
        )

        table = []

        for f in sorted_items:
            table.append([
                f["service"],
                f["resource_id"],
                f["issue"],
                f["severity"],
                f.get("estimated_monthly_loss", 0)
            ])

        print(tabulate(
            table,
            headers=["Service", "Resource", "Issue", "Severity", "Est. Monthly Loss ($)"],
            tablefmt="grid"
        ))

    print("\n====================================\n")
