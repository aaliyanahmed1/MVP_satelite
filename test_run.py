"""
Quick test script to run analysis and send email.
"""
import asyncio
import sys
from pathlib import Path

# Add parent AI_Roof_Damage_Detection to path
sys.path.insert(0, str(Path(__file__).parent.parent / "AI_Roof_Damage_Detection"))
sys.path.insert(0, str(Path(__file__).parent))

from main import analyze_and_email

if __name__ == "__main__":
    # Default zipcode for testing
    zipcode = sys.argv[1] if len(sys.argv) > 1 else "75201"
    recipient = "aliyanew16@gmail.com"
    
    print("=" * 60)
    print(f"Testing MVP Satellite Roof Damage Detection")
    print(f"Zipcode: {zipcode}")
    print(f"Recipient: {recipient}")
    print("=" * 60)
    print()
    
    asyncio.run(analyze_and_email(zipcode, recipient))

