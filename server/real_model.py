"""
Real model integration for OnionGrade using Ultralytics YOLOv8 segmentation model.

This file expects a weights file (e.g., yolov8n-seg.pt or custom trained weights) to be available locally.
Set the environment variable YOLOR_WEIGHTS to point to the weights path, or the code will attempt to use 'yolov8n-seg.pt'.

Usage:
- pip install -r server/requirements.txt
- Download weights (see README_e2e.md)
- Set USE_REAL_MODEL=1 and optionally YOLOR_WEIGHTS=/path/to/weights
- Start server: python server/api.py

Note: This integration assumes the model outputs segmentation masks and class ids corresponding to:
  0: onion
  1: defect
If your model uses different classes, adapt the mapping below.
"""

import os
import io
import numpy as np
import cv2
from PIL import Image
import base64

MODEL = None
MODEL_WEIGHTS = os.getenv('YOLOR_WEIGHTS', 'yolov8n-seg.pt')

# Class mapping - adapt to your model
CLASS_ONION = 0
CLASS_DEFECT = 1


def load_model():
    global MODEL
    if MODEL is not None:
        return MODEL
    try:
        from ultralytics import YOLO
    except Exception as e:
        raise RuntimeError('ultralytics not installed: ' + str(e))
    print('Loading model weights:', MODEL_WEIGHTS)
    MODEL = YOLO(MODEL_WEIGHTS)
    return MODEL


def _px_to_mm(d_px, reference_mm, px_ref=None):
    # if reference_mm and px_ref provided, compute px_per_mm
    if reference_mm and px_ref:
        px_per_mm = px_ref / reference_mm
        return round(d_px / px_per_mm, 1)
    # fallback assumption
    px_per_mm = 8.0
    return round(d_px / px_per_mm, 1)


def analyze_image(image_bytes, reference_mm=None):
    """Run real model on image bytes. Returns structured JSON similar to mock_model.analyze_image.
    """
    # lazy load model
    model = load_model()

    # decode image bytes to numpy BGR
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return {"onion_detected": False, "confidence": 0.0, "error": "invalid image"}

    # Run inference (Ultralytics returns a Results object)
    results = model(img, imgsz=640, device=0) if False else model(img)
    # pick first result
    r = results[0]

    # extract boxes, masks, scores, classes
    boxes = []
    masks = []
    classes = []
    scores = []

    # Boxes and scores
    if hasattr(r, 'boxes') and r.boxes is not None:
        try:
            xyxy = r.boxes.xyxy.cpu().numpy()
            confs = r.boxes.conf.cpu().numpy()
            clses = r.boxes.cls.cpu().numpy()
            for b, c, cl in zip(xyxy, confs, clses):
                boxes.append(list(map(float, b.tolist())))
                scores.append(float(c))
                classes.append(int(cl))
        except Exception:
            pass

    # Masks - ultralytics stores masks in r.masks
    mask_images = []
    try:
        if hasattr(r, 'masks') and r.masks is not None:
            # r.masks.xy, r.masks.data, r.masks.segments depending on version
            # Try to get boolean masks array
            masks_data = r.masks.data.cpu().numpy()  # (N, H, W)
            for m in masks_data:
                mask_images.append((m > 0.5).astype('uint8'))
    except Exception:
        # fallback: no masks
        pass

    # determine onion detection: choose largest detection with class == onion
    onion_idx = None
    for i, cl in enumerate(classes):
        if cl == CLASS_ONION:
            onion_idx = i
            break
    if onion_idx is None:
        # try any detection as onion
        if len(classes) > 0:
            onion_idx = 0

    if onion_idx is None:
        return {"onion_detected": False, "confidence": 0.0}

    confidence = scores[onion_idx] if onion_idx < len(scores) else 0.0
    # compute diameter in pixels from box width
    box = boxes[onion_idx]
    x1, y1, x2, y2 = box
    diameter_px = float(max(x2 - x1, y2 - y1))

    # If we have a reference marker detection (not implemented), allow passing px_ref via reference_mm; here assume px_ref=200 for demo
    px_ref = 200.0
    diameter_mm = _px_to_mm(diameter_px, reference_mm, px_ref)

    # compute shape and color scores using simple heuristics
    # shape: use contour circularity on mask if available
    shape_score = 75
    if len(mask_images) > 0 and onion_idx < len(mask_images):
        mask = mask_images[onion_idx]
        # find contours
        contours, _ = cv2.findContours(mask.astype('uint8'), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            cnt = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(cnt)
            perimeter = cv2.arcLength(cnt, True)
            if perimeter > 0:
                circularity = 4 * np.pi * (area / (perimeter * perimeter))
                shape_score = int(max(0, min(100, circularity * 100)))

    # color: compute color uniformity in HSV
    color_score = 80
    try:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h = hsv[:,:,0]
        # compute dominant hue variance inside onion mask if available
        if len(mask_images) > 0 and onion_idx < len(mask_images):
            mask = mask_images[onion_idx].astype(bool)
            hues = h[mask]
            if hues.size > 0:
                var = float(np.var(hues))
                color_score = int(max(0, min(100, 100 - var)))
    except Exception:
        pass

    # defects: analyze mask areas of class==defect if model provides separate detections or by using segmentation class ids
    defects = []
    # if model provides class==defect detections
    for i, cl in enumerate(classes):
        if cl == CLASS_DEFECT:
            # compute area from mask if available
            area_pct = None
            if i < len(mask_images):
                mask = mask_images[i]
                area = np.sum(mask)
                total = mask.size
                area_pct = round((area / total) * 100, 2)
            defects.append({
                'type': 'defect',
                'area_pct': area_pct if area_pct is not None else 1.0,
                'severity': 'minor' if (area_pct is None or area_pct < 3) else ('moderate' if area_pct < 8 else 'severe'),
                'confidence': scores[i] if i < len(scores) else 0.8
            })

    # as a fallback, if no defect detections, attempt to find dark regions on onion mask (simple heuristic)
    if not defects and len(mask_images) > 0 and onion_idx < len(mask_images):
        mask = mask_images[onion_idx].astype(bool)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        onion_pixels = gray[mask]
        if onion_pixels.size > 0:
            # find very dark pixels as potential rot
            thresh = int(np.percentile(onion_pixels, 5))
            dark = (onion_pixels < thresh).sum()
            area_pct_est = round((dark / onion_pixels.size) * 100, 2)
            if area_pct_est > 0.5:
                defects.append({
                    'type': 'surface_damage',
                    'area_pct': area_pct_est,
                    'severity': 'minor' if area_pct_est < 3 else ('moderate' if area_pct_est < 8 else 'severe'),
                    'confidence': 0.7
                })

    # compute quality using scoring module
    try:
        from scoring import compute_quality
        quality_score = compute_quality(diameter_mm, shape_score, color_score, defects)
    except Exception:
        quality_score = 60

    # determine grade with override for severe rot
    if any(d.get('type') == 'rot' and d.get('severity') == 'severe' for d in defects):
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
        'onion_detected': True,
        'confidence': round(float(confidence), 2),
        'diameter_mm': diameter_mm,
        'shape_score': int(shape_score),
        'color_score': int(color_score),
        'defects': defects,
        'quality_score': int(quality_score),
        'grade': grade,
        'model_version': os.path.basename(MODEL_WEIGHTS)
    }

    return result
