# OnionGrade — E2E Real Inference branch

This branch provides a minimal end-to-end skeleton to demo the Camera → Inference → Measurement → Score → Grade → Report flow.

How to run the mock inference server (local):

1. Create a Python virtual environment and install requirements:

```bash
python -m venv venv
source venv/bin/activate
pip install -r server/requirements.txt
```

2. Start the API:

```bash
python server/api.py
```

3. Open the frontend page (any static page that includes src/camera_integration.js) and use the camera capture button to post to /api/analyze.

Notes:
- The current implementation uses a mocked inference (server/mock_model.py). Replace analyze_image with a real model inference hook when ready.
- A PDF generator is included at server/generate_report.py which uses reportlab to create a simple report from a result JSON and an image.
