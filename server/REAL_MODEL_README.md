## Real model integration instructions

To enable the real YOLOv8 segmentation model for inference:

1) Install dependencies (recommended in a virtualenv):

```bash
python -m venv venv
source venv/bin/activate
pip install -r server/requirements.txt
```

2) Download model weights. For a small default, download Ultralytics' yolov8n-seg weights:

```bash
# example (replace URL with your preferred weights host)
wget -O yolov8n-seg.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-seg.pt
```

3) Place the weights in the server/ directory or set YOLOR_WEIGHTS environment variable to its path.

4) Start the API in real model mode:

```bash
export USE_REAL_MODEL=1
export YOLOR_WEIGHTS=./yolov8n-seg.pt
python server/api.py
```

Notes:
- The real_model.py file assumes class 0=onion and class 1=defect. If your model has different classes, edit server/real_model.py CLASS_* mappings.
- For GPU inference, ensure torch and CUDA are installed and the ultralytics model will run on the GPU.
- The example code contains basic heuristics for shape/color/defect extraction. You should replace them with model-trained logic or calibrated algorithms for production.
