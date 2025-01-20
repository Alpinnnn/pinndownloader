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
    video_url = request.form.get("url")
    if not video_url:
        return "URL tidak boleh kosong", 400

    cookies_path = "cookies.txt"
    output_path = "downloads/video.mp4"  # Path dasar untuk file output

    try:
        # Jalankan yt-dlp
        result = subprocess.run(
            [
                "yt-dlp",
                "--cookies", cookies_path,
                "-o", output_path,
                video_url
            ],
            check=True,
            capture_output=True,
            text=True
        )

        # Cek nama file output dari hasil yt-dlp
        output_file = f"{output_path}.webm"
        if not os.path.exists(output_file):
            return "File tidak ditemukan setelah pengunduhan.", 500

        # Kirim file ke user
        return send_file(output_file, as_attachment=True)

    except subprocess.CalledProcessError as e:
        return f"Terjadi kesalahan saat mengunduh video: {e.stderr or str(e)}", 500

    except Exception as e:
        return f"Kesalahan tak terduga: {str(e)}", 500


if __name__ == "__main__":
    app.run(debug=True)