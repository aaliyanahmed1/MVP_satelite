"""
Email service for sending damage reports.
Uses SMTP with email login credentials.
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Optional
import os
from loguru import logger

from src.output.json_generator import AnalysisResult
from mvp_costs import RepairCosts


def send_damage_report_email(
    recipient_email: str,
    zipcode: str,
    result: AnalysisResult,
    costs: RepairCosts,
    annotated_image_path: Optional[str] = None,
    heatmap_path: Optional[str] = None,
    roof_info: str = "",
    json_file_path: Optional[str] = None
) -> bool:
    """
    Send damage report email with costs and images.
    
    Args:
        recipient_email: Email address to send to
        zipcode: Zipcode analyzed
        result: Analysis result
        costs: Repair costs
        annotated_image_path: Path to annotated image
        heatmap_path: Path to heatmap
        
    Returns:
        True if email sent successfully, False otherwise
    """
    # Email credentials (hardcoded for testing)
    # NOTE: Gmail requires App Password, not regular password
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    email_user = "aaliyanahmedrajput@gmail.com"
    # Gmail App Password (16 characters, spaces removed)
    email_password = "kdqwrsjwquvqlkjw"
    
    # Default recipient
    if not recipient_email:
        recipient_email = "aliyannew16@gmail.com"
    
    try:
        # Create message
        msg = MIMEMultipart('related')
        msg['From'] = email_user
        msg['To'] = recipient_email
        msg['Subject'] = f"🏠 Roof Damage Report - Zipcode {zipcode}"
        
        # Load email template
        template_path = Path(__file__).parent / "email_template.html"
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                html_template = f.read()
        else:
            logger.warning("Template not found, using fallback")
            html_template = "<html><body><h1>Report</h1></body></html>"
        
        # Prepare data for template
        total_damages = len(result.damages)
        damage_area_sqft = f"{costs.damage_area_sqft:.2f}"
        
        # Build damage breakdown rows
        damage_breakdown_rows = ""
        if costs.breakdown_by_type:
            for damage_type, cost in costs.breakdown_by_type.items():
                damage_name = damage_type.replace('_', ' ').title()
                damage_breakdown_rows += f"""
                <tr>
                    <td><strong>{damage_name}</strong></td>
                    <td style="color: #667eea; font-weight: 600;">${cost:,.2f}</td>
                </tr>
                """
        else:
            damage_breakdown_rows = "<tr><td colspan='2' style='text-align: center; color: #999;'>No damage breakdown available</td></tr>"
        
        # Build severity cards
        severity_cards = ""
        severity_classes = {
            'critical': 'severity-critical',
            'high': 'severity-high',
            'medium': 'severity-medium',
            'low': 'severity-low'
        }
        
        for severity, count in result.damage_summary.items():
            if count > 0:
                severity_class = severity_classes.get(severity, 'severity-low')
                severity_cards += f"""
                <div class="stat-card">
                    <div class="stat-value">{count}</div>
                    <div class="stat-label">
                        <span class="severity-badge {severity_class}">{severity}</span>
                    </div>
                </div>
                """
        
        if not severity_cards:
            severity_cards = '<div class="stat-card"><div class="stat-value">0</div><div class="stat-label">No Damage Detected</div></div>'
        
        # Build roof info section
        roof_info_section = ""
        if roof_info and result.roofs:
            first_roof = result.roofs[0]
            roof_info_section = f"""
                <div class="divider"></div>
                <div class="section">
                    <h2 class="section-title">🏛️ First Roof Detection Details</h2>
                    <div class="roof-info-card">
                        <h4>Roof #{first_roof.id}</h4>
                        <div class="roof-info-grid">
                            <div class="info-item">
                                <div class="info-label">Confidence</div>
                                <div class="info-value">{first_roof.confidence:.1%}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Area (Pixels)</div>
                                <div class="info-value">{first_roof.area_pixels:,}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Center X</div>
                                <div class="info-value">{first_roof.center[0]:.1f}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Center Y</div>
                                <div class="info-value">{first_roof.center[1]:.1f}</div>
                            </div>
                        </div>
                    </div>
                </div>
            """
        
        # Replace template placeholders
        html_body = html_template.replace('{zipcode}', str(zipcode))
        html_body = html_body.replace('{total_roofs}', str(result.total_roofs))
        html_body = html_body.replace('{roofs_with_damage}', str(result.roofs_with_damage))
        html_body = html_body.replace('{total_damages}', str(total_damages))
        html_body = html_body.replace('{damage_area_sqft}', damage_area_sqft)
        html_body = html_body.replace('{total_cost}', f"{costs.total_cost:,.2f}")
        html_body = html_body.replace('{labor_cost}', f"{costs.labor_cost:,.2f}")
        html_body = html_body.replace('{material_cost}', f"{costs.material_cost:,.2f}")
        html_body = html_body.replace('{cost_per_sqft}', f"{costs.cost_per_sqft:.2f}")
        html_body = html_body.replace('{damage_breakdown_rows}', damage_breakdown_rows)
        html_body = html_body.replace('{severity_cards}', severity_cards)
        html_body = html_body.replace('{roof_info_section}', roof_info_section)
        
        # Attach HTML body
        msg.attach(MIMEText(html_body, 'html'))
        
        # Attach images if available
        if annotated_image_path and Path(annotated_image_path).exists():
            with open(annotated_image_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-Disposition', 'attachment', filename='annotated_detection.png')
                msg.attach(img)
        
        if heatmap_path and Path(heatmap_path).exists():
            with open(heatmap_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-Disposition', 'attachment', filename='damage_heatmap.png')
                msg.attach(img)
        
        # Attach JSON file if available
        if json_file_path and Path(json_file_path).exists():
            with open(json_file_path, 'rb') as f:
                part = MIMEBase('application', 'json')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename=Path(json_file_path).name)
                msg.attach(part)
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

