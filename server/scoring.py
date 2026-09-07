"""
Scoring utilities for OnionGrade demo.
Encapsulates the weighted formula and grade thresholds.
"""

def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))


def compute_size_score(diameter_mm):
    # Example: target size 50-70 mm maps to high score
    if diameter_mm is None:
        return 50
    if diameter_mm < 40:
        return 40
    if diameter_mm > 80:
        return 60
    # linear 40->80 maps to 60->100
    return int(clamp(60 + (diameter_mm - 40) * (40/40)))


def compute_defect_penalty(defects):
    # defects is a list of dicts with area_pct and severity
    penalty = 0.0
    for d in defects:
        area = d.get('area_pct', 0)
        severity = d.get('severity', 'minor')
        if severity == 'minor':
            penalty += area * 0.3
        elif severity == 'moderate':
            penalty += area * 0.8
        elif severity == 'severe':
            penalty += area * 2.0
    # normalize penalty into 0-40 scale (max)
    return min(penalty, 40)


def compute_quality(diameter_mm, shape_score, color_score, defects):
    # weights: size 25%, shape 25%, color 20%, defects 30%
    size_s = compute_size_score(diameter_mm)
    defect_penalty = compute_defect_penalty(defects)
    defect_score = max(0, 100 - defect_penalty)

    final = (
        size_s * 0.25 +
        shape_score * 0.25 +
        color_score * 0.2 +
        defect_score * 0.3
    )
    return int(clamp(round(final)))
