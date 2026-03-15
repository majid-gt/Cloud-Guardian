from main import run_analysis_pipeline
from analysis.remediation_engine import RemediationEngine


def run_fix():

    result = run_analysis_pipeline(return_state=True)

    if not result:
        return

    state, creds = result

    engine = RemediationEngine(creds, state)
    engine.execute()
