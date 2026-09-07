"""
Generate a simple PDF report for a scan result using reportlab.
Usage example:
    python generate_report.py result.json image.jpg output.pdf
"""
import sys
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


def generate(report_json, image_path, out_pdf_path):
    c = canvas.Canvas(out_pdf_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, height - 50, "OnionGrade AI — Inspection Report")

    c.setFont("Helvetica", 10)
    c.drawString(40, height - 70, f"Report ID: {report_json.get('report_id', 'RPT-0001')}")
    c.drawString(300, height - 70, f"Model: {report_json.get('model_version','unknown')}")
    c.drawString(40, height - 85, f"Date: {report_json.get('timestamp','unknown')}")

    # Image
    try:
        img = ImageReader(image_path)
        c.drawImage(img, 40, height - 300, width=220, height=220)
    except Exception:
        c.setFont("Helvetica", 9)
        c.drawString(40, height - 120, "(Image not available)")

    # Measurements
    c.setFont("Helvetica-Bold", 12)
    c.drawString(280, height - 120, "Measurements")
    c.setFont("Helvetica", 10)
    c.drawString(280, height - 140, f"Diameter (mm): {report_json.get('diameter_mm', 'N/A')}")
    c.drawString(280, height - 155, f"Quality Score: {report_json.get('quality_score', 'N/A')}")
    c.drawString(280, height - 170, f"Grade: {report_json.get('grade', 'N/A')}")

    # Defects
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 340, "Defects")
    c.setFont("Helvetica", 10)
    defects = report_json.get('defects', [])
    y = height - 360
    if not defects:
        c.drawString(40, y, "None detected")
    else:
        for d in defects:
            c.drawString(40, y, f"- {d.get('type')} | Area: {d.get('area_pct')}% | Severity: {d.get('severity')} | Conf: {d.get('confidence')}")
            y -= 14

    # Explanation
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "AI Explanation")
    y -= 16
    c.setFont("Helvetica", 10)
    explanation = report_json.get('explanation', 'See scoring breakdown attached.')
    c.drawString(40, y, explanation)

    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(40, 30, "AI-assisted assessment — not an official certification. Model version: " + report_json.get('model_version','N/A'))

    c.showPage()
    c.save()


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python generate_report.py result.json image.jpg out.pdf")
        sys.exit(1)
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    generate(data, sys.argv[2], sys.argv[3])
