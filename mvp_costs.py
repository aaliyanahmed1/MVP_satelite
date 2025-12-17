"""
Mock cost calculation for roof damage repairs.
Calculates labor and material costs based on damage area and type.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from src.output.json_generator import AnalysisResult
from src.detection.damage_detector import DamageType, DamageSeverity, DamageDetection


@dataclass
class RepairCosts:
    """Repair cost breakdown."""
    total_cost: float
    labor_cost: float
    material_cost: float
    damage_area_sqft: float
    cost_per_sqft: float
    breakdown_by_type: Dict[str, float]


# Base cost per square foot by damage type (mock data)
BASE_COSTS_PER_SQFT = {
    "hail_damage": 8.50,
    "missing_shingles": 6.00,
    "cracks": 7.50,
    "blisters": 9.00,
    "ponding": 12.00,
    "warping": 10.00,
    "flashing_damage": 15.00,
    "soft_spots": 18.00,
    "membrane_damage": 14.00,
    "unknown": 8.00
}

# Severity multipliers
SEVERITY_MULTIPLIERS = {
    "low": 1.0,
    "medium": 1.2,
    "high": 1.5,
    "critical": 2.0
}

# Labor percentage of total cost by damage type
LABOR_PERCENTAGES = {
    "hail_damage": 0.50,
    "missing_shingles": 0.45,
    "cracks": 0.50,
    "blisters": 0.55,
    "ponding": 0.60,
    "warping": 0.55,
    "flashing_damage": 0.65,
    "soft_spots": 0.70,
    "membrane_damage": 0.60,
    "unknown": 0.50
}

# Pixel to square feet conversion (approximate for zoom level 21)
# At zoom 21: ~0.075m per pixel = ~0.25 feet per pixel
# So 1 pixel² ≈ 0.0625 sqft
PIXEL_TO_SQFT = 0.0625


def calculate_repair_costs(result: AnalysisResult, damages: Optional[List[DamageDetection]] = None) -> RepairCosts:
    """
    Calculate repair costs from analysis result.
    
    Args:
        result: Analysis result with roofs and damages
        damages: Optional list of specific damages to calculate costs for.
                 If None, uses all damages from result.
        
    Returns:
        RepairCosts object with cost breakdown
    """
    # Use provided damages or all damages from result
    damages_to_calculate = damages if damages is not None else result.damages
    
    if not damages_to_calculate:
        return RepairCosts(
            total_cost=0.0,
            labor_cost=0.0,
            material_cost=0.0,
            damage_area_sqft=0.0,
            cost_per_sqft=0.0,
            breakdown_by_type={}
        )
    
    # Calculate total damage pixels from provided damages
    total_damage_pixels = sum(d.area_pixels for d in damages_to_calculate)
    total_damage_sqft = total_damage_pixels * PIXEL_TO_SQFT
    
    # Calculate costs by damage type
    breakdown_by_type = {}
    total_cost = 0.0
    
    for damage in damages_to_calculate:
        damage_type = damage.damage_type.value
        severity = damage.severity.value
        damage_area_pixels = damage.area_pixels
        damage_area_sqft = damage_area_pixels * PIXEL_TO_SQFT
        
        # Get base cost
        base_cost_per_sqft = BASE_COSTS_PER_SQFT.get(damage_type, 8.0)
        
        # Apply severity multiplier
        severity_mult = SEVERITY_MULTIPLIERS.get(severity, 1.0)
        adjusted_cost_per_sqft = base_cost_per_sqft * severity_mult
        
        # Calculate cost for this damage
        damage_cost = adjusted_cost_per_sqft * damage_area_sqft
        
        # Add to breakdown
        if damage_type not in breakdown_by_type:
            breakdown_by_type[damage_type] = 0.0
        breakdown_by_type[damage_type] += damage_cost
        
        total_cost += damage_cost
    
    # Apply minimum cost threshold
    if total_cost < 500.0:
        total_cost = 500.0
    
    # Calculate labor and material costs
    # Use average labor percentage across all damage types
    avg_labor_pct = sum(LABOR_PERCENTAGES.values()) / len(LABOR_PERCENTAGES)
    labor_cost = total_cost * avg_labor_pct
    material_cost = total_cost * (1 - avg_labor_pct)
    
    # Calculate average cost per sqft
    cost_per_sqft = total_cost / total_damage_sqft if total_damage_sqft > 0 else 0.0
    
    return RepairCosts(
        total_cost=round(total_cost, 2),
        labor_cost=round(labor_cost, 2),
        material_cost=round(material_cost, 2),
        damage_area_sqft=round(total_damage_sqft, 2),
        cost_per_sqft=round(cost_per_sqft, 2),
        breakdown_by_type={k: round(v, 2) for k, v in breakdown_by_type.items()}
    )

