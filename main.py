from config.credential_prompt import prompt_for_credentials, validate_credentials
from core.orchestrator import CloudOrchestrator
from output.formatter import display_findings
from output.summary import calculate_health_score, classify_health
from ai.advisory import generate_summary_advisory


def run_analysis_pipeline(hardware_auth=False, return_state=False):
    """
    Executes full Cloud Guardian analysis pipeline.
    Used by CLI command: cg analyze
    """

    from core.hardware.vault_client import VaultClient

    if hardware_auth:
        try:
            vault = VaultClient()
            creds = vault.unlock()
        except Exception as e:
            print(f"[Hardware Auth Error] {str(e)}")
            return
    else:
        creds = prompt_for_credentials()
        is_valid, identity = validate_credentials(creds)
        if not is_valid:
            print("Invalid AWS credentials.")
            return

    print("\n✅ AWS Account Connected")
    
    if hardware_auth:
        print("🔐 Using ESP32 Hardware Vault Authentication\n")

    orchestrator = CloudOrchestrator(creds)
    cloud_state = orchestrator.run()

    # ---- Display Findings ----
    display_findings(cloud_state)

    # ---- Health Score ----
    score, monthly_loss = calculate_health_score(cloud_state)
    level = classify_health(score)

    print("\n========== CLOUD HEALTH SUMMARY ==========")
    print(f"Overall Health Score : {score}%")
    print(f"Health Status        : {level}")
    print(f"Estimated Monthly Waste : ${monthly_loss}")
    print("==========================================\n")

    # ---- AI Summary ----
    ai_text = generate_summary_advisory(
        cloud_state,
        score,
        monthly_loss
    )

    print("\n========== AI CLOUD ADVISORY ==========\n")
    print(ai_text)
    print("\n=======================================\n")
    
    if return_state:
        return cloud_state