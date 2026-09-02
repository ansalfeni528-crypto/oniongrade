"""
=============================================================================
ONIONGRADE AI - FASTAPI / PYTHON BACKEND SERVER
AI-Based Onion Quality Assessment & Grading
=============================================================================

This server provides the REST API endpoints for:
- POST /api/analyze (Accepts onion image, performs vision segmentation & scoring)
- GET /api/stats (Returns procurement aggregate grading distributions)
- Static file hosting for the frontend prototype

Run with:
    python server.py
"""

import os
import sys
import json
import time
import base64
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class OnionGradeAPIHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Enable CORS for API integration
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                "status": "online",
                "service": "OnionGrade AI Vision Core v2.4",
                "timestamp": time.time()
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return

        elif parsed.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            stats = {
                "total_analyzed": 142,
                "grade_a_count": 68,
                "grade_b_count": 45,
                "grade_c_count": 17,
                "reject_count": 12,
                "average_score": 79.4,
                "model": "YOLOv8-Seg + ResNet50 Classifier"
            }
            self.wfile.write(json.dumps(stats).encode('utf-8'))
            return

        # Serve static files (HTML, CSS, JS, Assets)
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/analyze':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                payload = json.loads(post_data.decode('utf-8')) if post_data else {}
            except Exception:
                payload = {}

            # Perform Simulated Computer Vision / YOLO Inference
            result = {
                "status": "success",
                "sample_id": f"OGAI-{time.strftime('%Y')}-SMP-{int(time.time() % 10000)}",
                "score": 87,
                "grade": "Grade A",
                "confidence": 0.942,
                "metrics": {
                    "size_mm": 58.4,
                    "size_category": "Medium",
                    "sphericity_index": 0.92,
                    "color_uniformity": 0.94,
                    "surface_condition_score": 78
                },
                "defects": [
                    {
                        "type": "Minor Surface Abrasion",
                        "confidence": 0.91,
                        "severity": "Low",
                        "bounding_box": [140, 210, 48, 36]
                    }
                ],
                "explanation": "The onion received Grade A because overall size and color are acceptable with minimal surface damage penalty.",
                "scoring_breakdown": {
                    "size_score": 20,
                    "shape_score": 17,
                    "color_score": 19,
                    "surface_score": 15,
                    "defect_penalty": -4,
                    "final_score": 87
                },
                "commercial_recommendation": "Direct Supermarket Retail & Export Batch"
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()

def run(port=PORT):
    # Ensure UTF-8 output on Windows consoles
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    server_address = ('', port)
    httpd = HTTPServer(server_address, OnionGradeAPIHandler)
    print("=================================================================")
    print(f"[*] OnionGrade AI Server is running at http://localhost:{port}")
    print(f"[*] API Health Check: http://localhost:{port}/api/health")
    print(f"[*] API Stats: http://localhost:{port}/api/stats")
    print(f"[*] AI Inference API: POST http://localhost:{port}/api/analyze")
    print("=================================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run(port)
