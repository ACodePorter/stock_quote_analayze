import sys
import os
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend_core.data_collectors.main import generate_annual_data, generate_hk_annual_data

if __name__ == "__main__":
    print("Starting verification of annual data generation...")
    
    print("1. Testing A-share annual data generation...")
    try:
        generate_annual_data()
        print("A-share annual data generation triggered successfully.")
    except Exception as e:
        print(f"FAILED: A-share annual data generation failed: {e}")

    print("\n2. Testing HK stock annual data generation...")
    try:
        generate_hk_annual_data()
        print("HK stock annual data generation triggered successfully.")
    except Exception as e:
        print(f"FAILED: HK stock annual data generation failed: {e}")
        
    print("\nVerification complete. Please check logs for details.")
