# Cloud Guardian  
### AI-Assisted Edge-Based AWS Audit and Optimization System

Cloud Guardian is a **modular cloud governance and optimization tool** designed to audit AWS environments for **cost inefficiencies, security misconfigurations, and operational risks**.

The system combines **automated AWS analysis**, **AI-generated advisory recommendations**, and a **hardware-backed credential vault implemented using an ESP32 microcontroller**.

The goal of Cloud Guardian is to provide a **lightweight but powerful auditing engine** that detects underutilized resources, security exposures, and cost waste in AWS accounts while ensuring **secure credential handling through edge-based hardware authentication**.

---

# Project Overview

Cloud Guardian operates as a **command-line interface (CLI) application** that performs automated cloud analysis using the following pipeline:

1. Resource inventory collection  
2. Metrics aggregation and utilization analysis  
3. Rule-based cost and security evaluation  
4. Cloud health scoring and risk classification  
5. AI-generated remediation advisory  
6. Professional report generation (HTML, JSON, PDF)

The system can also **retrieve AWS credentials securely from an ESP32-based hardware vault** instead of storing credentials locally on the host machine.

---

# Key Features

## Automated AWS Resource Audit

Cloud Guardian scans multiple AWS services and builds a contextual representation of the cloud environment.

Currently supported AWS resources:

- EC2 Instances
- EBS Volumes
- EBS Snapshots
- Elastic IP Addresses
- Security Groups
- IAM Users

The system also models relationships between resources, including:

- EC2 ↔ EBS attachments
- Security group associations
- Network exposure analysis

This allows **context-aware rule evaluation**.

---

## Cost Optimization Detection

Cloud Guardian detects common cloud cost inefficiencies such as:

- Underutilized EC2 instances
- Unattached EBS volumes
- Orphaned EBS snapshots
- Unassociated Elastic IP addresses

Each issue includes:

- Estimated monthly financial impact
- Severity classification
- Recommended remediation

---

## Security Risk Identification

Cloud Guardian performs security checks on networking and access configurations, including:

- Publicly exposed SSH ports
- Publicly exposed RDP ports
- Open security groups without active usage
- Potentially unsafe network configurations

Security findings are categorized separately from cost findings.

---

## Cloud Health Scoring

The system calculates an overall **Cloud Health Score** using:

- Total number of findings
- Severity weighting
- Estimated financial impact

This score provides a quick overview of the **overall health of the AWS account**.

---

## AI Advisory Engine

Cloud Guardian includes an **AI advisory system** that converts raw findings into structured recommendations.

The AI module provides:

- Executive summary of cloud risks
- Prioritized remediation actions
- Cost optimization suggestions
- Security improvement strategies

This helps users understand the **operational impact of detected issues**.

---

## Hardware-Backed Credential Vault

A key feature of Cloud Guardian is its **ESP32-based credential vault**.

Instead of storing AWS credentials locally, credentials are stored securely inside an **ESP32 microcontroller using AES-256 encryption**.

The CLI communicates with the vault using **serial communication** and retrieves credentials only after successful password authentication.

### Benefits

- No permanent credential storage on the host machine
- Hardware isolation of sensitive credentials
- Password-protected credential access
- Secure password rotation

---

## Automated Remediation Engine

Cloud Guardian includes an optional **automated remediation system** capable of fixing certain issues automatically.

Supported actions include:

- Releasing unused Elastic IP addresses
- Deleting unattached EBS volumes

Before performing changes, the system:

1. Generates a remediation plan  
2. Requests user confirmation  
3. Executes the approved fixes

---

## Professional Reporting

Cloud Guardian generates comprehensive audit reports in multiple formats.

### JSON Report

- Machine-readable structured output
- Suitable for integrations and automation

### HTML Report

- Interactive dashboard
- Severity distribution charts
- Service risk breakdown
- Visualizations of findings

### PDF Report

- Professional audit document
- Executive summary
- Risk visualizations
- Remediation recommendations
- Detailed findings table

---

# System Architecture

The system follows a **modular pipeline architecture**:

```
User CLI
   │
   ▼
Authentication Layer
   ├── Hardware Vault (ESP32)
   └── Manual AWS Credentials
   │
   ▼
Cloud Orchestrator
   │
   ▼
Resource Collectors
   │
   ▼
Metrics Analyzer
   │
   ▼
Rule Engine
   │
   ▼
Health Scoring
   │
   ▼
AI Advisory Engine
   │
   ▼
Report Generation
```

Each stage operates independently, allowing **easy extension and feature additions**.

---

# Repository Structure

```
cloud-guardian/
│
├── commands/              # CLI command implementations
├── core/                  # Core orchestration logic
├── collectors/            # AWS resource collection modules
├── metrics/               # CloudWatch metrics processing
├── analysis/              # Rule engine and remediation engine
├── output/                # Reporting and visualization modules
│
├── firmware/              # ESP32 credential vault firmware
│   └── esp32_vault/
│       └── esp32_vault.ino
│
├── requirements.txt
├── setup.py
├── cli.py
└── README.md
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/majid-gt/Cloud-Guardian.git
cd Cloud-Guardian
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install the CLI tool:

```bash
pip install -e .
```

---

# Usage

## Run Cloud Audit

```bash
cg analyze
```

If the **ESP32 vault is connected**, credentials will automatically be retrieved from the hardware vault.

Otherwise the CLI will prompt for AWS credentials.

---

## Generate Reports

### JSON Report

```bash
cg report --format json
```

### HTML Dashboard

```bash
cg report --format html
```

### Professional PDF Report

```bash
cg report --format pdf
```

---

## Automatic Remediation

Run automated remediation for supported issues:

```bash
cg fix
```

The tool displays a **remediation plan before executing changes**.

---

## Hardware Vault Status

Check if the ESP32 vault is connected:

```bash
cg hardware status
```

---

## Change Vault Password

```bash
cg change-password
```

This rotates the encryption password protecting credentials inside the ESP32 vault.

---

# ESP32 Credential Vault Setup

1. Open the firmware located at:

```
firmware/esp32_vault/esp32_vault.ino
```

2. Configure the following values:

```
SETUP_PASSWORD
AWS_ACCESS_KEY
AWS_SECRET_KEY
AWS_REGION
```

3. Upload the firmware to an **ESP32 DevKit V1** using **Arduino IDE**.

Once connected via USB, the CLI will automatically detect the vault.

---

# Technology Stack

Cloud Guardian is built using:

### Backend

- Python
- Boto3 (AWS SDK for Python)

### CLI Framework

- Rich CLI Framework

### Hardware Communication

- PySerial

### Reporting & Visualization

- ReportLab (PDF generation)
- Matplotlib (charts)
- Chart.js (HTML dashboards)

### Embedded Hardware

- ESP32 Microcontroller
- Arduino Framework (C++)

### Security

- AES-256 Encryption
- SHA-256 Hashing

---

# Future Improvements

Planned enhancements include:

- Multi-account AWS auditing
- Real-time monitoring mode
- Advanced IAM privilege analysis
- Additional automated remediation actions
- ML-based anomaly detection
- Kubernetes cluster auditing

---

# License

This project is intended for **educational and research purposes**.
