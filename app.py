import os
import subprocess
import json
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/get-formats", methods=["POST"])
def get_formats():
    video_url = request.form.get("url")
    if not video_url:
        return jsonify({"error": "URL tidak boleh kosong"}), 400

    try:
        # Gunakan yt-dlp untuk mendapatkan info video
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'cookies': 'cookies.txt'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Filter format yang memiliki video+audio
            formats = []
            for f in info['formats']:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    resolution = f.get('resolution', 'N/A')
                    # Hanya ambil format dengan resolusi standar
                    if resolution in ['144p', '240p', '360p', '480p', '720p', '1080p']:
                        formats.append({
                            'format_id': f['format_id'],
                            'resolution': resolution,
                            'filesize': f.get('filesize', 0),
                            'ext': f['ext']
                        })

            # Sort formats berdasarkan resolusi
            resolution_order = ['144p', '240p', '360p', '480p', '720p', '1080p']
            formats.sort(key=lambda x: resolution_order.index(x['resolution']) if x['resolution'] in resolution_order else -1)

            response = {
                'title': info['title'],
                'thumbnail': info['thumbnail'],
                'duration': info['duration'],
                'formats': formats
            }
            
            return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/download", methods=["POST"])
def download_video():
    try:
        video_url = request.form.get("url")
        format_id = request.form.get("format_id")
        
        if not video_url or not format_id:
            return jsonify({"error": "URL dan format harus diisi"}), 400

        # Download video dengan format yang dipilih
        command = [
            "yt-dlp",
            "--cookies", "cookies.txt",
            "-f", format_id,
            "-o", "downloads/%(title)s.%(ext)s",
            video_url
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500

        # Cari file yang baru didownload
        downloaded_file = None
        for file in os.listdir('downloads'):
            downloaded_file = os.path.join('downloads', file)
            break
            
        if not downloaded_file:
            return jsonify({"error": "File tidak ditemukan"}), 500

        return send_file(
            downloaded_file,
            as_attachment=True,
            download_name=os.path.basename(downloaded_file)
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)