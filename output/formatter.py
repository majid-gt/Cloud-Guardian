from tabulate import tabulate


def display_findings(state):
    findings = state.get_all_findings()

    if state.get_total_findings() == 0:
        print("\n✅ No issues detected. Cloud looks healthy.\n")
        return

    print("\n========== CLOUD FINDINGS ==========\n")

    for category, items in findings.items():

        if not items:
            continue

        print(f"\n🔎 Category: {category.upper()}")

        table = []

        for f in items:
            table.append([
                f["service"],
                f["resource_id"],
                f["issue"],
                f["severity"],
                f["estimated_monthly_loss"]
            ])

        print(tabulate(
            table,
            headers=["Service", "Resource", "Issue", "Severity", "Est. Monthly Loss ($)"],
            tablefmt="grid"
        ))

    print("\n====================================\n")