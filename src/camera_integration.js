// Minimal camera capture + analyze example for demo integration
// Usage: include this script in a page that has a <video id="cam"> and <button id="capture">

async function startCamera(videoEl) {
  const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false });
  videoEl.srcObject = stream;
  await videoEl.play();
}

function captureFrameToBlob(videoEl, mime = 'image/jpeg', quality = 0.8) {
  const canvas = document.createElement('canvas');
  canvas.width = videoEl.videoWidth;
  canvas.height = videoEl.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
  return new Promise(resolve => canvas.toBlob(resolve, mime, quality));
}

async function sendForAnalysis(blob, reference_mm) {
  const fd = new FormData();
  fd.append('file', blob, 'capture.jpg');
  if (reference_mm) fd.append('reference_mm', reference_mm);
  const resp = await fetch('/api/analyze', { method: 'POST', body: fd });
  return resp.json();
}

// Example wiring
document.addEventListener('DOMContentLoaded', () => {
  const video = document.getElementById('cam');
  const captureBtn = document.getElementById('capture');
  const output = document.getElementById('result');
  const refInput = document.getElementById('reference_mm');

  startCamera(video).catch(e => {
    console.error('Camera start failed', e);
    output.textContent = 'Camera not available';
  });

  captureBtn.addEventListener('click', async () => {
    output.textContent = 'Capturing...';
    const blob = await captureFrameToBlob(video);
    output.textContent = 'Sending for analysis...';
    const res = await sendForAnalysis(blob, refInput ? refInput.value : undefined);
    output.textContent = JSON.stringify(res, null, 2);
  });
});
