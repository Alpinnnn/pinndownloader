import os
import subprocess
from flask import Flask, render_template, request, send_file, jsonify
import glob

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
        # Bersihkan folder downloads terlebih dahulu
        files = glob.glob('downloads/*')
        for f in files:
            try:
                os.remove(f)
            except:
                pass

        # Jalankan yt-dlp untuk mendapatkan info video terlebih dahulu
        info_command = [
            "yt-dlp",
            "--cookies", "cookies.txt",
            "--print", "%(title)s.%(ext)s",
            "--no-download",
            video_url
        ]
        
        result = subprocess.run(info_command, capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({"error": f"Error getting video info: {result.stderr}"}), 500
            
        expected_filename = result.stdout.strip()
        
        # Jalankan yt-dlp untuk download
        download_command = [
            "yt-dlp",
            "--cookies", "cookies.txt",
            "-f", "best",
            "-o", f"downloads/%(title)s.%(ext)s",
            video_url
        ]
        
        result = subprocess.run(download_command, capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({"error": f"Error downloading: {result.stderr}"}), 500

        # Cari file yang baru didownload
        downloaded_files = glob.glob('downloads/*')
        if not downloaded_files:
            return jsonify({"error": "File tidak ditemukan setelah download"}), 500
            
        downloaded_file = downloaded_files[0]  # Ambil file pertama yang ditemukan
        
        try:
            # Kirim file ke user
            return send_file(
                downloaded_file,
                as_attachment=True,
                download_name=os.path.basename(downloaded_file)
            )
        finally:
            # Hapus file setelah dikirim
            try:
                os.remove(downloaded_file)
            except:
                pass

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)