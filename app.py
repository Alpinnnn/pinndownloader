import os
from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp

app = Flask(__name__)

# Pastikan direktori downloads ada
if not os.path.exists('downloads'):
    os.makedirs('downloads')

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/download", methods=["POST"])
def download_video():
    video_url = request.form.get("url")
    if not video_url:
        return jsonify({"error": "URL tidak boleh kosong"}), 400

    try:
        # Konfigurasi yt-dlp
        ydl_opts = {
            'format': 'best',  # Mengambil kualitas terbaik
            'outtmpl': 'downloads/%(title)s.%(ext)s',  # Format nama file yang sesuai
            'cookiesfile': 'cookies.txt',
            'quiet': True,
            'no_warnings': True,
        }

        # Download info video terlebih dahulu
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Ekstrak informasi video
            info = ydl.extract_info(video_url, download=False)
            video_title = info['title']
            video_ext = info['ext']
            filename = f"downloads/{video_title}.{video_ext}"
            
            # Download video
            ydl.download([video_url])
            
            # Kirim file ke user dengan nama yang sesuai
            return send_file(
                filename,
                as_attachment=True,
                download_name=f"{video_title}.{video_ext}"
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)