import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Free models (change if needed)
MODEL_PRIMARY = "arcee-ai/trinity-large-preview:free"
MODEL_FALLBACK = "google/gemma-3n-4b"


# ======================================================
# INTERNAL MODEL CALL
# ======================================================

def _call_model(model, prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://cloud-guardian.local",
        "X-Title": "Cloud Guardian"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 400,
        "top_p": 0.9,
        "frequency_penalty": 0.3,
        "presence_penalty": 0.2
    }

    response = requests.post(url, headers=headers, json=data, timeout=25)
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]


# ======================================================
# PER-ISSUE ADVISORY
# ======================================================

def generate_advisory(issue_type, details):
    """
    AI explanation for a single issue.
    Falls back if API fails.
    """

    if not OPENROUTER_API_KEY:
        return fallback_advisory(issue_type, details)

    prompt = f"""
You are a cloud optimization assistant.

Explain clearly in simple beginner-friendly language:

Issue Type: {issue_type}
Details: {details}

Provide:
1. What the issue is
2. Why it matters
3. Recommended action

Keep it under 120 words.
"""

    try:
        return _call_model(MODEL_PRIMARY, prompt)
    except Exception:
        try:
            return _call_model(MODEL_FALLBACK, prompt)
        except Exception:
            return fallback_advisory(issue_type, details)


def fallback_advisory(issue_type, details):
    return f"""
[AI unavailable — basic guidance]

Issue: {issue_type}
Details: {details}

Recommendation:
Review this resource and remove or optimize it if not required to reduce unnecessary cloud cost.
"""


# ======================================================
# FULL CLOUD SUMMARY ADVISORY (NEW ARCHITECTURE)
# ======================================================

def generate_summary_advisory(state, health_score, monthly_loss):
    """
    AI-generated executive cloud summary.
    Uses structured findings from CloudState.
    """

    if not OPENROUTER_API_KEY:
        return fallback_summary(state, health_score, monthly_loss)

    findings = state.get_all_findings()

    # Build structured summary
    summary_text = f"""
Cloud Health Score: {health_score}%
Estimated Monthly Waste: ${monthly_loss}

Findings Summary:
"""

    for category, items in findings.items():
        summary_text += f"\nCategory: {category}\n"
        for f in items:
            summary_text += f"- {f['service']} | {f['issue']} | Severity: {f['severity']}\n"

    prompt = f"""
You are a professional cloud cost optimization and security advisor.

Based on this cloud audit report:

{summary_text}

Provide:

1. Executive summary (short paragraph)
2. Top 3 priority actions
3. Cost optimization recommendations
4. Risk observations

Use clear, professional, beginner-friendly language.
Keep it concise.
"""

    try:
        return _call_model(MODEL_PRIMARY, prompt)
    except Exception:
        try:
            return _call_model(MODEL_FALLBACK, prompt)
        except Exception:
            return fallback_summary(state, health_score, monthly_loss)


def fallback_summary(state, health_score, monthly_loss):
    total_findings = state.get_total_findings()

    return f"""
[AI Summary Unavailable — Basic Report]

Cloud Health Score: {health_score}%
Estimated Monthly Waste: ${monthly_loss}
Total Issues Detected: {total_findings}

Recommended Actions:
• Remove unused storage resources
• Stop or resize underutilized compute
• Review exposed network configurations
• Regularly monitor cloud usage
"""