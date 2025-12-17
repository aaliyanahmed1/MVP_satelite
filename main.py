"""
MVP Satellite Roof Damage Detection System
Simplified version: Image Fetching → Detection → Email with Costs
Sends separate emails for each property with damage.
"""
import asyncio
import sys
import os
import random
from pathlib import Path
from typing import List, Dict
from collections import defaultdict

# Add parent AI_Roof_Damage_Detection to path for imports
parent_dir = Path(__file__).parent.parent / "AI_Roof_Damage_Detection"
parent_dir = parent_dir.resolve()  # Resolve to absolute path

# Add parent directory to Python path FIRST (before any imports)
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Also add current directory for MVP modules
current_dir = Path(__file__).parent.resolve()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Change working directory to parent for relative imports
os.chdir(str(parent_dir))

# Load .env from production project BEFORE importing settings
from dotenv import load_dotenv
env_path = parent_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded .env from: {env_path}")
else:
    print(f"⚠ Warning: .env not found at {env_path}")

from src.pipeline import RoofDamagePipeline, PipelineConfig
from src.utils.logger import setup_logger
from config.settings import get_settings
from src.output.json_generator import AnalysisResult
from mvp_email import send_damage_report_email
from mvp_costs import calculate_repair_costs


def create_roof_specific_result(
    full_result: AnalysisResult,
    roof_id: int,
    roof_damages: List
) -> AnalysisResult:
    """
    Create a filtered AnalysisResult for a specific roof and its damages.
    
    Args:
        full_result: Complete analysis result
        roof_id: ID of the roof to filter for
        roof_damages: List of damages for this roof
        
    Returns:
        Filtered AnalysisResult with only this roof and its damages
    """
    # Find the roof
    roof = next((r for r in full_result.roofs if r.id == roof_id), None)
    if not roof:
        raise ValueError(f"Roof {roof_id} not found in results")
    
    # Create filtered result
    filtered_result = AnalysisResult(
        zipcode=full_result.zipcode,
        timestamp=full_result.timestamp,
        processing_time_sec=full_result.processing_time_sec,
        center_lat=full_result.center_lat,
        center_lng=full_result.center_lng,
        bounding_box=full_result.bounding_box,
        image_width=full_result.image_width,
        image_height=full_result.image_height,
        tiles_processed=full_result.tiles_processed,
        roofs=[roof],  # Only this roof
        damages=roof_damages,  # Only damages for this roof
        total_roofs=1,
        roofs_with_damage=1 if roof_damages else 0,
        total_damage_area_pixels=sum(d.area_pixels for d in roof_damages),
        performance=full_result.performance
    )
    
    return filtered_result


async def analyze_and_email_per_property(
    zipcode: str,
    email_list: List[str]
):
    """
    Analyze zipcode and send separate email reports for each property with damage.
    
    Args:
        zipcode: US zipcode (5 digits)
        email_list: List of email addresses to randomly assign to properties
    """
    setup_logger()
    
    settings = get_settings()
    
    if not settings.has_maptiler_api_key:
        print("ERROR: MAPTILER_API_KEY not set in .env file")
        return
    
    # Create pipeline config (output to parent project's output directory)
    output_dir = str(parent_dir / "output")
    
    # Use models from production project
    roof_model = str(parent_dir / "models" / "roof_detector.pt")
    damage_model = str(parent_dir / "models" / "damage_detector.pt")
    
    # Check if models exist, fallback to defaults
    if not Path(roof_model).exists():
        roof_model = settings.roof_model_path
    if not Path(damage_model).exists():
        damage_model = settings.damage_model_path
    
    config = PipelineConfig(
        tile_size=256,
        zoom_level=21,
        roof_confidence=0.2,
        damage_confidence=0.25,
        output_dir=output_dir,
        save_visualization=True,
        save_heatmap=True,
        save_json=True,
        roof_model_path=roof_model,
        damage_model_path=damage_model
    )
    
    print(f"Analyzing zipcode: {zipcode}")
    print("Fetching satellite images...")
    
    # Run analysis
    pipeline = RoofDamagePipeline(
        api_key=settings.maptiler_api_key.get_secret_value(),
        config=config
    )
    
    try:
        result = await pipeline.analyze_zipcode(zipcode)
        
        print(f"\nAnalysis Complete!")
        print(f"  - Total roofs: {result.total_roofs}")
        print(f"  - Roofs with damage: {result.roofs_with_damage}")
        print(f"  - Total damage area: {result.total_damage_area_pixels} pixels")
        
        # Group damages by roof_id - ONLY roofs with damage
        damages_by_roof: Dict[int, List] = defaultdict(list)
        for damage in result.damages:
            if damage.roof_id is not None:
                damages_by_roof[damage.roof_id].append(damage)
        
        if not damages_by_roof:
            print("\n⚠️  No damages detected on any roofs. No emails to send.")
            return
        
        # Filter: Only process roofs that have damage
        roofs_with_damage = [roof_id for roof_id in damages_by_roof.keys() if len(damages_by_roof[roof_id]) > 0]
        
        if not roofs_with_damage:
            print("\n⚠️  No roofs with damage found. No emails to send.")
            return
        
        print(f"\n📧 Found {len(roofs_with_damage)} roof(s) with damage")
        print(f"📧 Will send separate emails ONLY for damaged roofs")
        
        # Find output files (use most recent from AI_Roof_Damage_Detection/output)
        output_base = parent_dir / "output"
        annotated_file = None
        heatmap_file = None
        json_file = None
        
        # Get most recent files for this zipcode
        annotated_files = sorted(output_base.glob(f"{zipcode}_*_annotated.png"), key=lambda p: p.stat().st_mtime, reverse=True)
        if annotated_files:
            annotated_file = str(annotated_files[0])
        
        heatmap_files = sorted(output_base.glob(f"{zipcode}_*_heatmap.png"), key=lambda p: p.stat().st_mtime, reverse=True)
        if heatmap_files:
            heatmap_file = str(heatmap_files[0])
        
        json_files = sorted(output_base.glob(f"{zipcode}_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if json_files:
            json_file = str(json_files[0])
        
        # Send separate email for each roof with damage ONLY
        emails_sent = 0
        emails_failed = 0
        
        for roof_id in roofs_with_damage:
            roof_damages = damages_by_roof[roof_id]
            
            # Double check: Skip if no damages (shouldn't happen, but safety check)
            if not roof_damages or len(roof_damages) == 0:
                print(f"⚠️  Roof {roof_id} has no damages, skipping...")
                continue
            # Find the roof
            roof = next((r for r in result.roofs if r.id == roof_id), None)
            if not roof:
                print(f"⚠️  Roof {roof_id} not found, skipping...")
                continue
            
            # Create filtered result for this roof only
            roof_result = create_roof_specific_result(
                full_result=result,
                roof_id=roof_id,
                roof_damages=roof_damages
            )
            
            # Calculate costs for this roof's damages only
            roof_costs = calculate_repair_costs(result, damages=roof_damages)
            
            # Randomly pick an email from the list
            if not email_list:
                recipient_email = "aliyannew16@gmail.com"  # Default fallback
            else:
                recipient_email = random.choice(email_list)
            
            print(f"\n📧 Sending email for Roof #{roof_id} to: {recipient_email}")
            print(f"   - {len(roof_damages)} damage(s) detected")
            print(f"   - Total damage area: {roof_result.total_damage_area_pixels} pixels")
            print(f"   - Estimated cost: ${roof_costs.total_cost:,.2f}")
            
            # Send email for this specific roof
            success = send_damage_report_email(
                recipient_email=recipient_email,
                zipcode=zipcode,
                result=roof_result,
                costs=roof_costs,
                annotated_image_path=annotated_file,
                heatmap_path=heatmap_file,
                roof_info="",  # Will be generated in email template
                json_file_path=json_file
            )
            
            if success:
                print(f"   ✅ Email sent successfully!")
                emails_sent += 1
            else:
                print(f"   ❌ Failed to send email")
                emails_failed += 1
        
        print(f"\n📊 Email Summary:")
        print(f"   ✅ Successfully sent: {emails_sent}")
        print(f"   ❌ Failed: {emails_failed}")
        print(f"   📧 Total properties notified: {emails_sent}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await pipeline.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <zipcode> [email1] [email2] [email3] ...")
        print("Example: python main.py 75201 owner1@example.com owner2@example.com")
        print("Example: python main.py 75201  # Uses default email")
        print("\nNote: Emails are randomly assigned to properties with damage.")
        print("      If no emails provided, uses default: aliyannew16@gmail.com")
        sys.exit(1)
    
    zipcode = sys.argv[1]
    
    # Get email list from command line arguments
    email_list = []
    if len(sys.argv) > 2:
        email_list = sys.argv[2:]
        print(f"📧 Provided {len(email_list)} email address(es)")
        for i, email in enumerate(email_list, 1):
            print(f"   {i}. {email}")
    else:
        print("⚠️  No emails provided, will use default: aliyannew16@gmail.com")
        email_list = ["aliyannew16@gmail.com"]
    
    asyncio.run(analyze_and_email_per_property(zipcode, email_list))

