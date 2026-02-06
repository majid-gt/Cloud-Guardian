from config.credential_prompt import prompt_for_credentials, validate_credentials
from aws.ec2_scanner import scan_ec2
from analysis.rule_engine import detect_idle_ec2
from output.formatter import display_idle_ec2

from aws.ebs_scanner import scan_ebs
from analysis.rule_engine import detect_unused_ebs
from output.formatter import display_unused_ebs

# from ai.advisory import generate_advisory

def main():
    creds = prompt_for_credentials()
    is_valid, identity = validate_credentials(creds)

    if not is_valid:
        print("Invalid credentials")
        return

    print("\n✅ AWS Account Connected")

    instances = scan_ec2(creds)
    idle_instances = detect_idle_ec2(instances)
    display_idle_ec2(idle_instances)
    
    
    volumes = scan_ebs(creds)
    unused_volumes = detect_unused_ebs(volumes)
    display_unused_ebs(unused_volumes)

if __name__ == "__main__":
    main()
