from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mock_model import analyze_image
import uvicorn

app = FastAPI(title="OnionGrade Inference (mock)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...),
                  reference_mm: float = Form(None)):
    """Accepts an image and optional reference_mm (for calibration). Returns a mocked analysis JSON.
    The real model hook replaces analyze_image in mock_model.py with an actual inference call.
    """
    content = await file.read()
    result = analyze_image(content, reference_mm)
    return JSONResponse(content=result)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
