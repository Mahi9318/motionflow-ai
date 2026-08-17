# MotionFlow AI — Kling Motion Control style clone

This project provides a mobile-friendly web UI for transferring motion from a reference
video to a character image using the fal.ai Kling V3 Motion Control API.

## 1. Get an API key
Create a fal.ai account and obtain a server-side `FAL_KEY`.

## 2. Local run
```bash
pip install -r requirements.txt
# Linux/macOS:
export FAL_KEY="YOUR_KEY"
# Windows PowerShell:
$env:FAL_KEY="YOUR_KEY"

python app.py
```
Open http://localhost:5000

## 3. Vercel
Upload the project to GitHub, import it into Vercel, and add:
`FAL_KEY` = your fal.ai API key

Do NOT put the key in HTML/JavaScript.

## Important
Vercel serverless functions have execution limits. This project uses the model queue and
polling architecture, but for heavy production traffic a dedicated backend/worker is
recommended.

The V3 Standard endpoint is `fal-ai/kling-video/v3/standard/motion-control`.
The Pro endpoint is `fal-ai/kling-video/v3/pro/motion-control`.

The upstream API currently documents up to 30 seconds for `character_orientation=video`
and up to 10 seconds for `character_orientation=image`.
