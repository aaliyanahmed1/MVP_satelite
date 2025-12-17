"""
Area calculation utilities.
Converts pixel areas to square feet and provides area-related functions.
"""
from typing import List, Tuple
import math

# Pixel to square feet conversion for zoom level 21
# At zoom 21: ~0.075m per pixel = ~0.25 feet per pixel
# So 1 pixel² ≈ 0.0625 sqft
PIXEL_TO_SQFT = 0.0625

# Square feet to square meters
SQFT_TO_SQM = 0.092903


def pixels_to_sqft(pixels: int) -> float:
    """
    Convert pixel area to square feet.
    
    Args:
        pixels: Area in pixels
        
    Returns:
        Area in square feet
    """
    return pixels * PIXEL_TO_SQFT


def sqft_to_sqm(sqft: float) -> float:
    """
    Convert square feet to square meters.
    
    Args:
        sqft: Area in square feet
        
    Returns:
        Area in square meters
    """
    return sqft * SQFT_TO_SQM


def calculate_polygon_area(polygon: List[Tuple[float, float]]) -> float:
    """
    Calculate area of polygon using shoelace formula.
    
    Args:
        polygon: List of (x, y) coordinates
        
    Returns:
        Area in square units
    """
    if len(polygon) < 3:
        return 0.0
    
    area = 0.0
    n = len(polygon)
    
    for i in range(n):
        j = (i + 1) % n
        area += polygon[i][0] * polygon[j][1]
        area -= polygon[j][0] * polygon[i][1]
    
    return abs(area) / 2.0


def calculate_roof_area_sqft(roof_area_pixels: int) -> float:
    """
    Calculate roof area in square feet from pixel area.
    
    Args:
        roof_area_pixels: Roof area in pixels
        
    Returns:
        Roof area in square feet
    """
    return pixels_to_sqft(roof_area_pixels)


def calculate_damage_percentage(damage_area_pixels: int, roof_area_pixels: int) -> float:
    """
    Calculate damage percentage of roof.
    
    Args:
        damage_area_pixels: Damage area in pixels
        roof_area_pixels: Roof area in pixels
        
    Returns:
        Damage percentage (0-100)
    """
    if roof_area_pixels == 0:
        return 0.0
    
    return (damage_area_pixels / roof_area_pixels) * 100.0


def format_area(area_sqft: float) -> str:
    """
    Format area for display.
    
    Args:
        area_sqft: Area in square feet
        
    Returns:
        Formatted string (e.g., "1,234.56 sq ft")
    """
    return f"{area_sqft:,.2f} sq ft"

