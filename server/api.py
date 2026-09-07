from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

USE_REAL = os.getenv('USE_REAL_MODEL', '0') in ['1', 'true', 'True']

if USE_REAL:
    try:
        from real_model import analyze_image as real_analyze
    except Exception as e:
        real_analyze = None
        print('Failed to import real_model:', e)

from mock_model import analyze_image as mock_analyze
import uvicorn

app = FastAPI(title="OnionGrade Inference")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {"status": "ok", "use_real_model": USE_REAL}

@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...),
                  reference_mm: float = Form(None)):
    """Accepts an image and optional reference_mm (for calibration). Returns analysis JSON.
    If USE_REAL_MODEL is enabled and real_model is available, uses that; otherwise falls back to mocked inference.
    """
    content = await file.read()
    if USE_REAL and real_analyze is not None:
        try:
            result = real_analyze(content, reference_mm)
            return JSONResponse(content=result)
        except Exception as e:
            # on failure, log and fallback
            print('Real model inference failed:', e)
    # fallback to mock
    result = mock_analyze(content, reference_mm)
    return JSONResponse(content=result)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
