def calculate_health_score(state):
    severity_weights = {
        "low": 2,
        "medium": 5,
        "high": 10,
        "critical": 20
    }

    total_impact = 0
    total_monthly_loss = 0

    for category, findings in state.findings.items():
        for f in findings:
            weight = severity_weights.get(f["severity"], 0)
            confidence = f.get("confidence", 1.0)

            total_impact += weight * confidence
            total_monthly_loss += f.get("estimated_monthly_loss", 0)

    health_score = max(0, 100 - total_impact)

    return round(health_score, 2), round(total_monthly_loss, 2)


def classify_health(score):
    if score >= 90:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Moderate"
    elif score >= 30:
        return "Poor"
    else:
        return "Critical"