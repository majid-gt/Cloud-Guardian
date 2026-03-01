from main import run_analysis_pipeline

def run_analyze(hardware_auth=False):
    print("Running cloud analysis...\n")
    run_analysis_pipeline(hardware_auth=hardware_auth)