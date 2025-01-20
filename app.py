import os
from flask import Flask, render_template, request, Response, stream_with_context
from yt_dlp import YoutubeDL

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/download", methods=["POST"])
def download_video():
    video_url = request.form.get("url")
    if not video_url:
        return "URL tidak boleh kosong", 400

    cookies_path = "cookies.txt"
    output_path = "downloads/%(title)s.%(ext)s"  # Format nama file mengikuti YouTube

    def generate():
        ydl_opts = {
            "outtmpl": output_path,
            "format": "bestvideo+bestaudio/best",
            "cookies": cookies_path,
            "progress_hooks": [progress_hook],
        }

        with YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([video_url])
            except Exception as e:
                yield f"data: Kesalahan saat mengunduh video: {str(e)}\n\n"

    def progress_hook(d):
        if d["status"] == "downloading":
            yield f"data: Sedang mengunduh {d['_percent_str']} pada {d['_speed_str']}\n\n"
        elif d["status"] == "finished":
            yield "data: Unduhan selesai! Menyiapkan file...\n\n"

    # Menggunakan stream untuk progres download
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

if __name__ == "__main__":
    # Pastikan folder 'downloads' tersedia
    os.makedirs("downloads", exist_ok=True)
    app.run(debug=True)
