import os
import json
from datetime import datetime
from main import run_analysis_pipeline
from rich.console import Console

console = Console()

REPORT_DIR = r"D:\CloudGuardianReports"
os.makedirs(REPORT_DIR, exist_ok=True)


def run_report(format_type="json"):
    console.print("[cyan]Generating cloud audit report...[/cyan]\n")

    cloud_state, _ = run_analysis_pipeline(return_state=True)

    if format_type == "json":
        generate_json_report(cloud_state)
    elif format_type == "html":
        generate_html_report(cloud_state)
    elif format_type == "pdf":
        generate_pdf_report(cloud_state)    
    else:
        console.print("[red]Unsupported format. Use json or html.[/red]")


def generate_json_report(state):
    report_data = {
        "generated_at": datetime.utcnow().isoformat(),
        "findings": state.findings,
        "total_findings": state.get_total_findings()
    }

    filename = os.path.join(
        REPORT_DIR,
        f"cloudguardian_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(filename, "w") as f:
        json.dump(report_data, f, indent=4, default=str)

    console.print(f"[green]JSON report generated:[/green] {filename}")


def generate_html_report(state):

    filename = os.path.join(
        REPORT_DIR,
        f"cloudguardian_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    )
    total_findings = state.get_total_findings()

    severity_counts = {"CRITICAL":0,"HIGH":0,"MEDIUM":0,"LOW":0}
    total_cost = 0
    service_counts = {}

    for category, findings in state.findings.items():
        for f in findings:

            sev = f["severity"].upper()
            if sev in severity_counts:
                severity_counts[sev] += 1

            cost = f.get("estimated_monthly_loss",0)
            total_cost += cost

            service = f["service"]
            service_counts[service] = service_counts.get(service,0) + 1


    service_labels = list(service_counts.keys())
    service_values = list(service_counts.values())


    html_content = """
<html>
<head>
<title>Cloud Guardian Report</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

body {
font-family: Arial;
background:#0f172a;
color:white;
margin:0;
padding:20px;
}

h1 {
color:#38bdf8;
}

.dashboard {
display:grid;
grid-template-columns: repeat(3, 1fr);
gap:20px;
margin-bottom:30px;
}

.card {
background:#1e293b;
padding:20px;
border-radius:10px;
text-align:center;
}

.metric {
font-size:32px;
font-weight:bold;
}

.chart-container {
width:100%;
max-width:900px;
margin:30px auto;
}

.small-chart {
max-width:400px;
margin:auto;
}

table {
width:100%;
border-collapse:collapse;
margin-top:20px;
}

th,td {
border:1px solid #334155;
padding:8px;
text-align:left;
}

th {
background:#1e293b;
}

</style>

</head>

<body>

<h1>Cloud Guardian Security & Cost Audit</h1>

<p>Generated: """ + datetime.utcnow().isoformat() + """</p>

<div class="dashboard">

<div class="card">
<div>Total Findings</div>
<div class="metric">""" + str(total_findings) + """</div>
</div>

<div class="card">
<div>Estimated Monthly Waste</div>
<div class="metric">$""" + str(total_cost) + """</div>
</div>

<div class="card">
<div>Critical Issues</div>
<div class="metric">""" + str(severity_counts["CRITICAL"]) + """</div>
</div>

</div>

<div class="chart-container">
<h2>Findings by Severity</h2>
<canvas id="severityChart"></canvas>
</div>

<div class="chart-container small-chart">
<h2>Findings by Service</h2>
<canvas id="serviceChart"></canvas>
</div>

<h2>Detailed Findings</h2>

<table>

<tr>
<th>Category</th>
<th>Service</th>
<th>Resource</th>
<th>Issue</th>
<th>Severity</th>
<th>Monthly Loss</th>
</tr>
"""


    for category, findings in state.findings.items():
        for f in findings:

            html_content += f"""
<tr>
<td>{category}</td>
<td>{f["service"]}</td>
<td>{f["resource_id"]}</td>
<td>{f["issue"]}</td>
<td>{f["severity"]}</td>
<td>${f.get("estimated_monthly_loss",0)}</td>
</tr>
"""


    html_content += """

</table>

<script>

const severityChart = new Chart(
document.getElementById('severityChart'),
{
type:'bar',
data:{
labels:['Critical','High','Medium','Low'],
datasets:[{
label:'Findings',
data:[""" + str(severity_counts["CRITICAL"]) + "," + str(severity_counts["HIGH"]) + "," + str(severity_counts["MEDIUM"]) + "," + str(severity_counts["LOW"]) + """],
backgroundColor:['#ef4444','#f97316','#eab308','#22c55e']
}]
},
options:{
plugins:{
legend:{
labels:{ color:"white" }
}
},
scales:{
x:{
ticks:{ color:"white" },
grid:{ color:"#334155" }
},
y:{
ticks:{ color:"white" },
grid:{ color:"#334155" }
}
}
}
});


const serviceChart = new Chart(
document.getElementById('serviceChart'),
{
type:'pie',
data:{
labels:""" + str(service_labels) + """,
datasets:[{
data:""" + str(service_values) + """,
backgroundColor:['#38bdf8','#22c55e','#f97316','#eab308','#ef4444']
}]
},
options:{
plugins:{
legend:{
labels:{ color:"white" }
}
}
}
});

</script>

</body>
</html>
"""

    with open(filename,"w") as f:
        f.write(html_content)

    console.print(f"[green]HTML dashboard report generated:[/green] {filename}")

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors
import matplotlib.pyplot as plt



def generate_pdf_report(state):

    filename = os.path.join(
        REPORT_DIR,
        f"cloudguardian_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )
    styles = getSampleStyleSheet()

    elements = []

    # ---------- SUMMARY DATA ----------

    total_findings = state.get_total_findings()

    total_cost = 0
    severity_counts = {"CRITICAL":0,"HIGH":0,"MEDIUM":0,"LOW":0}
    service_counts = {}

    remediation_items = []

    for category, findings in state.findings.items():
        for f in findings:

            total_cost += f.get("estimated_monthly_loss",0)

            sev = f["severity"].upper()
            if sev in severity_counts:
                severity_counts[sev]+=1

            service = f["service"]
            service_counts[service] = service_counts.get(service,0)+1

            issue = f["issue"].lower()

            if "volume" in issue and "unattached" in issue:
                remediation_items.append("Delete unattached EBS volumes")

            if "elastic ip" in issue and "unassociated" in issue:
                remediation_items.append("Release unused Elastic IPs")

            if "security group" in issue and "unused" in issue:
                remediation_items.append("Remove unused security groups")

            if "underutilized" in issue:
                remediation_items.append("Resize or terminate underutilized EC2 instances")

    remediation_items = list(set(remediation_items))

    # ---------- CREATE CHARTS ----------

    severity_chart = os.path.join(REPORT_DIR, "severity_chart.png")
    service_chart = os.path.join(REPORT_DIR, "service_chart.png")
    # Severity chart
    plt.figure(figsize=(4,3))
    plt.bar(severity_counts.keys(), severity_counts.values(), color=["red","orange","gold","green"])
    plt.title("Findings by Severity")
    plt.tight_layout()
    plt.savefig(severity_chart)
    plt.close()

    # Service chart
    plt.figure(figsize=(4,3))
    plt.pie(service_counts.values(), labels=service_counts.keys(), autopct='%1.0f%%')
    plt.title("Findings by Service")
    plt.tight_layout()
    plt.savefig(service_chart)
    plt.close()

    # ---------- HEADER ----------

    elements.append(Paragraph("<b>Cloud Guardian</b>", styles["Title"]))
    elements.append(Paragraph("AWS Security & Cost Audit Report", styles["Heading2"]))
    elements.append(Spacer(1,20))

    elements.append(Paragraph(f"Generated at: {datetime.utcnow().isoformat()}", styles["Normal"]))
    elements.append(Spacer(1,20))

    # ---------- SUMMARY TABLE ----------

    summary_data = [
        ["Total Findings", total_findings],
        ["Estimated Monthly Waste ($)", round(total_cost,2)]
    ]

    summary_table = Table(summary_data, colWidths=[8*cm,5*cm])

    summary_table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),1,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey)
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1,25))

    # ---------- VISUALIZATIONS ----------

    elements.append(Paragraph("<b>Findings Visualization</b>", styles["Heading3"]))
    elements.append(Spacer(1,10))

    elements.append(Image(severity_chart, width=8*cm, height=6*cm))
    elements.append(Spacer(1,15))

    elements.append(Image(service_chart, width=8*cm, height=6*cm))
    elements.append(Spacer(1,25))

    # ---------- REMEDIATION SECTION ----------

    elements.append(Paragraph("<b>Recommended Remediation Actions</b>", styles["Heading3"]))
    elements.append(Spacer(1,10))

    for item in remediation_items:
        elements.append(Paragraph(f"• {item}", styles["Normal"]))

    elements.append(Spacer(1,25))

    # ---------- FINDINGS TABLE ----------

    elements.append(Paragraph("<b>Detailed Findings</b>", styles["Heading3"]))
    elements.append(Spacer(1,10))

    table_data = [["Category","Service","Resource","Issue","Severity","Monthly Loss"]]

    for category, findings in state.findings.items():
        for f in findings:
            table_data.append([
                category,
                f["service"],
                f["resource_id"],
                f["issue"],
                f["severity"],
                f"${f.get('estimated_monthly_loss',0)}"
            ])

    findings_table = Table(table_data)

    findings_table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("ALIGN",(5,1),(-1,-1),"RIGHT")
    ]))

    elements.append(findings_table)

    # ---------- PAGE BORDER ----------

    def draw_border(canvas, doc):
        canvas.setStrokeColor(colors.grey)
        canvas.rect(20,20,A4[0]-40,A4[1]-40)

    pdf = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    pdf.build(elements, onFirstPage=draw_border, onLaterPages=draw_border)

    console.print(f"[green]PDF report generated:[/green] {filename}")
