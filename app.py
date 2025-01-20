import os
import subprocess
from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/download", methods=["POST"])
def download_video():
    video_url = request.form["url"]
    cookies_path = "cookies.txt"  # Path ke file cookies
    output_path = "downloads/video.mp4"

    try:
        # Jalankan perintah yt-dlp
        subprocess.run(
            [
                "yt-dlp",
                "--cookies", cookies_path,
                "-o", output_path,
                video_url
            ],
            check=True
        )

        # Kirim file sebagai response
        return send_file(output_path, as_attachment=True)

    except subprocess.CalledProcessError as e:
        return f"Terjadi kesalahan: {e}"

if __name__ == "__main__":
    app.run(debug=True)