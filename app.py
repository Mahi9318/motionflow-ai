import os
import tempfile
from flask import Flask, render_template, request, jsonify
import fal_client

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024

MODEL_STANDARD = "fal-ai/kling-video/v3/standard/motion-control"
MODEL_PRO = "fal-ai/kling-video/v3/pro/motion-control"

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/api/generate")
def generate():
    if not os.getenv("FAL_KEY"):
        return jsonify({"error": "FAL_KEY is not configured on the server."}), 500

    image = request.files.get("image")
    video = request.files.get("video")
    prompt = request.form.get("prompt", "").strip()
    orientation = request.form.get("orientation", "video")
    quality = request.form.get("quality", "standard")

    if not image or not video:
        return jsonify({"error": "Please upload both a character image and a motion video."}), 400

    if orientation not in ("video", "image"):
        orientation = "video"

    # Kling V3 supports up to 30s for video orientation and up to 10s for image orientation.
    model = MODEL_PRO if quality == "pro" else MODEL_STANDARD

    try:
        with tempfile.TemporaryDirectory() as td:
            image_path = os.path.join(td, image.filename or "character.png")
            video_path = os.path.join(td, video.filename or "motion.mp4")
            image.save(image_path)
            video.save(video_path)

            image_url = fal_client.upload_file(image_path)
            video_url = fal_client.upload_file(video_path)

        args = {
            "image_url": image_url,
            "video_url": video_url,
            "character_orientation": orientation,
            "keep_original_sound": True,
        }
        if prompt:
            args["prompt"] = prompt

        handler = fal_client.submit(model, arguments=args)
        return jsonify({
            "request_id": handler.request_id,
            "model": model,
            "message": "Generation queued."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/api/status/<request_id>")
def status(request_id):
    if not os.getenv("FAL_KEY"):
        return jsonify({"error": "FAL_KEY is not configured on the server."}), 500

    model = request.args.get("model", MODEL_STANDARD)
    if model not in (MODEL_STANDARD, MODEL_PRO):
        model = MODEL_STANDARD

    try:
        s = fal_client.status(model, request_id, with_logs=False)
        status_name = getattr(s, "status", None) or s.__class__.__name__
        if status_name == "Completed" or s.__class__.__name__ == "Completed":
            result = fal_client.result(model, request_id)
            video_url = result.get("video", {}).get("url")
            return jsonify({"status": "COMPLETED", "video_url": video_url, "result": result})
        if s.__class__.__name__ == "InProgress":
            return jsonify({"status": "IN_PROGRESS"})
        return jsonify({"status": "IN_QUEUE"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/health")
def health():
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
