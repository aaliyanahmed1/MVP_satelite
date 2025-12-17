# MVP Satellite Roof Damage Detection

Simplified MVP version: Image Fetching → Detection → Email with Costs

## Features

- ✅ Satellite image fetching from MapTiler
- ✅ Roof detection using YOLOv8
- ✅ Damage detection using YOLOv8
- ✅ Cost calculation (labor + materials)
- ✅ Email reports with images

## Setup

### 1. Environment Variables

Create `.env` file in `AI_Roof_Damage_Detection` directory:

```bash
# Required: MapTiler API
MAPTILER_API_KEY=your_maptiler_api_key
```

**Note:** Email credentials are already configured in code:
- Sender: aaliyanahmedrajput@gmail.com
- Recipient: aliyanew16@gmail.com (default)

### 2. Run

**From parent directory (E:\Upwork_pro_Yolo):**

```powershell
cd MVP_satelite
python main.py 75201
```

**Or use the PowerShell script:**
```powershell
cd MVP_satelite
.\run_test.ps1 75201
```

**Example:**
```bash
# Default recipient (aliyanew16@gmail.com)
python main.py 75201

# Custom recipient
python main.py 75201 custom@email.com
```

## Output

- Analyzes zipcode
- Detects roofs and damage
- Calculates repair costs
- Sends email report with:
  - Damage summary
  - Cost breakdown (labor + materials)
  - Annotated images
  - Heatmap

## Cost Calculation

Mock costs based on:
- Damage type (hail, missing shingles, cracks, etc.)
- Damage severity (low, medium, high, critical)
- Damage area (pixels → square feet)
- Labor percentage (varies by damage type)

## Files

- `main.py` - Main entry point
- `mvp_costs.py` - Cost calculation
- `mvp_email.py` - Email sending
- `areas.py` - Area conversion utilities

