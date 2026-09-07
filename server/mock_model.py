"""
Simple mocked model for OnionGrade demo. Replace analyze_image with real inference hook.
Produces a deterministic realistic JSON response from an input image.
"""
import io
import random
from PIL import Image
import base64
import math

MODEL_VERSION = "mock-yolov8seg-v0"

def _fake_diameter_px(img):
    # Use image size heuristics to produce a diameter in px
    w, h = img.size
    return int(min(w, h) * 0.4)


def _px_to_mm(d_px, reference_mm):
    # If reference provided, assume reference width in mm corresponds to 200 px for demo
    if reference_mm:
        px_per_mm = 200.0 / reference_mm
        return round(d_px / px_per_mm, 1)
    # fallback assumption
    px_per_mm = 8.0
    return round(d_px / px_per_mm, 1)


def analyze_image(image_bytes, reference_mm=None):
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    except Exception:
        # return a failure structure
        return {
            "onion_detected": False,
            "confidence": 0.0,
            "model_version": MODEL_VERSION,
            "error": "invalid image"
        }

    # Deterministic random seed based on image size to produce consistent demo results
    seed = img.size[0] * 31 + img.size[1]
    rng = random.Random(seed)

    onion_detected = True
    confidence = round(0.85 + rng.random() * 0.14, 2)  # 0.85 - 0.99

    diameter_px = _fake_diameter_px(img)
    diameter_mm = _px_to_mm(diameter_px, reference_mm)

    # shape/color scores
    shape_score = int(75 + rng.randint(0, 20))
    color_score = int(80 + rng.randint(0, 15))

    # defects: 0-2 defects
    num_defects = rng.choice([0,0,1,1,2])
    defects = []
    for i in range(num_defects):
        d_type = rng.choice(["surface_damage", "rot", "sprouting", "cut"])
        area_pct = round(rng.uniform(0.5, 9.0), 2)
        confidence_d = round(0.7 + rng.random() * 0.28, 2)
        severity = "minor"
        if area_pct > 8:
            severity = "severe"
        elif area_pct > 3:
            severity = "moderate"
        defects.append({
            "type": d_type,
            "area_pct": area_pct,
            "severity": severity,
            "confidence": confidence_d
        })

    # compute quality score using a simple weighted formula
    from scoring import compute_quality
    quality_score = compute_quality(diameter_mm, shape_score, color_score, defects)

    # decide grade
    if any(d['type'] == 'rot' and d['severity']=='severe' for d in defects):
        grade = 'Reject'
    else:
        if quality_score >= 85:
            grade = 'A'
        elif quality_score >= 70:
            grade = 'B'
        elif quality_score >= 50:
            grade = 'C'
        else:
            grade = 'Reject'

    result = {
        "onion_detected": onion_detected,
        "confidence": confidence,
        "diameter_mm": diameter_mm,
        "shape_score": shape_score,
        "color_score": color_score,
        "defects": defects,
        "quality_score": quality_score,
        "grade": grade,
        "model_version": MODEL_VERSION
    }

    return result
