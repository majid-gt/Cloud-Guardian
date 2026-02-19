import os
import json

def run_init():
    config_dir = ".cg"
    config_file = os.path.join(config_dir, "config.json")

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    default_config = {
        "region": "us-east-1",
        "ai_enabled": True
    }

    with open(config_file, "w") as f:
        json.dump(default_config, f, indent=4)

    print("Cloud Guardian initialized.")
    print(f"Config created at {config_file}")