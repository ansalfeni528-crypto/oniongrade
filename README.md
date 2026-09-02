# OnionGrade AI 🧅
### *“Smart Vision for Better Onion Grading”*
**AI-Powered Onion Quality Assessment & Grading Platform**

---

## 🌟 Overview
**OnionGrade AI** is a modern, responsive web application engineered for real-time agricultural quality assessment:
**AI-Based Onion Quality Assessment and Grading**.

It provides an AI-powered computer vision platform that allows users to upload or capture an onion image with a live camera, analyze it using computer vision, detect visible defects, estimate quality parameters, calculate a transparent quality score, and assign an AGMARK-aligned grade.

### Core Objectives:
- ⚡ **Fast**: Under 500ms processing per bulb.
- 🎯 **Consistent**: Objective millimeter physical size calibration eliminating human estimation bias.
- 🔍 **Transparent**: Fully explainable multi-parameter scoring formula.
- 🧠 **Explainable**: Plain-English reasons explaining why every grade was awarded.
- 📉 **Less Dependent on Manual Inspection**: Aligned with APMC Mandi and NAFED procurement standards.

---

## 🧭 Core Workflow

```
OPEN APP ➔ QUICK LIVE SCAN / UPLOAD ➔ LIVE CAMERA AI DETECTION ➔ CAPTURE & ANALYZE ➔ DEFECT LOCALIZATION ➔ QUALITY SCORE (76/100) ➔ ASSIGNED GRADE B ➔ QUALITY REPORT (PDF)
```

---

## 🖥️ Screen & Feature Matrix

1. **Screen 1 — Splash / Login & Authentication**:
   - Role Selection: Farmer (Kisan), Mandi Quality Inspector, Wholesale Trader.
   - Quick 1-click Demo Login.
   - Workflow Pills (Capture, Analyze, Detect, Grade).

2. **Screen 2 — Farmer Dashboard & Home**:
   - Personalized Farmer Greeting Header.
   - Quick AI Scan Hero Card with camera button.
   - 4 Workflow Step Chips.
   - Recent Scans List with Grade Badges and **Delete Functionality**.
   - Mandi Quality KPI Summary Cards.

3. **Screen 3 — Live Camera & AI Detection**:
   - 30 FPS Real-time bounding box tracking (`● ONION DETECTED`).
   - Live millimeter diameter caliper bar (`Ø 58.4mm`).
   - Camera flip (Front/Rear) and AI overlay toggles.
   - Size Calibration Standard Selector (₹10 Coin, Agri Card, Steel Scale, Auto).
   - 4 Benchmark Demo Lots (Grade A, Grade B, Grade C, Reject).

4. **Screen 4 — Scan Result**:
   - Overall Grade Header (Grade B - Minor Defects) with animated circular score (`76 / 100`).
   - Segmented Onion Image with defect bounding boxes.
   - Quality Analysis Status Rows (Surface Damage, Shape, Color, Size).
   - 💡 Insight Callout Card.

5. **Screen 5 — Quality Report**:
   - Report ID, Date & Time, Sample Summary & Source.
   - Quality Breakdown Progress Bars (Surface Damage 25%, Shape 30%, Color 90%, Size 75%).
   - AI Summary Card.
   - **Download Report (PDF)** Action.

6. **Screen 6 — Mandi Procurement Analytics**:
   - Scanned lot metrics & grade breakdown.
   - Interactive Chart.js charts: Grade Distribution, Defect Breakdown, 7-Day Quality & Price Trends.

7. **Screen 7 — Analysis History & Audit Ledger**:
   - Searchable table with thumbnail previews, scores, and status.
   - Grade filter chips and **Delete Action**.
   - CSV Export action.

---

## 🧮 Transparent Scoring Formula

```
Final Score = Size Score (20) + Shape Score (20) + Color Score (20) + Surface Condition Score (20) - Defect Penalty (up to -20)
```

---

## 🚀 How to Run

### Method 1: Python Server (Recommended)
```bash
python server.py
```
Open in browser: **http://localhost:8000**

### Method 2: Direct Browser Launch
Double-click `index.html` or open in any modern browser (Chrome, Edge, Firefox, Safari).

---

## 📡 REST API Integration
- `GET /api/health` — Microservice health status.
- `GET /api/stats` — Aggregate Mandi grading distributions.
- `POST /api/analyze` — Accepts onion image payload and returns structured JSON analysis with bounding boxes, physical metrics, AGMARK score, and XAI explanation.

---
© 2026 OnionGrade AI • AI-Powered Onion Quality Assessment & Grading
