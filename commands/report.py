import json
import os
from datetime import datetime
from main import run_analysis_pipeline
from rich.console import Console

console = Console()


def run_report(format_type="json"):
    console.print("[cyan]Generating cloud audit report...[/cyan]\n")

    cloud_state = run_analysis_pipeline(return_state=True)

    if format_type == "json":
        generate_json_report(cloud_state)
    elif format_type == "html":
        generate_html_report(cloud_state)
    else:
        console.print("[red]Unsupported format. Use json or html.[/red]")


def generate_json_report(state):
    report_data = {
        "generated_at": datetime.utcnow().isoformat(),
        "findings": state.findings,
        "total_findings": state.get_total_findings()
    }

    filename = f"cloudguardian_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, "w") as f:
        json.dump(report_data, f, indent=4, default=str)

    console.print(f"[green]JSON report generated:[/green] {filename}")


def generate_html_report(state):
    filename = f"cloudguardian_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    html_content = f"""
    <html>
    <head>
        <title>Cloud Guardian Report</title>
        <style>
            body {{ font-family: Arial; background-color: #0f172a; color: #f8fafc; }}
            h1 {{ color: #38bdf8; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #334155; padding: 8px; }}
            th {{ background-color: #1e293b; }}
        </style>
    </head>
    <body>
        <h1>Cloud Guardian Audit Report</h1>
        <p>Generated at: {datetime.utcnow().isoformat()}</p>
        <h2>Total Findings: {state.get_total_findings()}</h2>
        <table>
            <tr>
                <th>Category</th>
                <th>Service</th>
                <th>Resource</th>
                <th>Issue</th>
                <th>Severity</th>
                <th>Estimated Monthly Loss</th>
            </tr>
    """

    for category, findings in state.findings.items():
        for finding in findings:
            html_content += f"""
            <tr>
                <td>{category}</td>
                <td>{finding['service']}</td>
                <td>{finding['resource_id']}</td>
                <td>{finding['issue']}</td>
                <td>{finding['severity']}</td>
                <td>${finding.get('estimated_monthly_loss', 0)}</td>
            </tr>
            """

    html_content += """
        </table>
    </body>
    </html>
    """

    with open(filename, "w") as f:
        f.write(html_content)

    console.print(f"[green]HTML report generated:[/green] {filename}")