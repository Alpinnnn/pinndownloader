import os
from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import sys

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
        # Pastikan file cookies.txt ada
        cookies_file = os.path.join(os.path.dirname(__file__), 'cookies.txt')
        if not os.path.exists(cookies_file):
            return jsonify({"error": "File cookies.txt tidak ditemukan"}), 500

        # Konfigurasi yt-dlp dengan cookies
        ydl_opts = {
            'format': 'best',  # Mengambil kualitas terbaik
            'outtmpl': 'downloads/%(title)s.%(ext)s',  # Format nama file yang sesuai
            'cookiesfile': cookies_file,  # Menggunakan cookies.txt
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'ignoreerrors': True,
            'no_color': True,
            'verbose': True
        }

        # Download info video terlebih dahulu
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Ekstrak informasi video
            info = ydl.extract_info(video_url, download=False)
            if info is None:
                return jsonify({"error": "Tidak dapat mengekstrak informasi video"}), 500
                
            video_title = info['title']
            video_ext = info['ext']
            filename = f"downloads/{video_title}.{video_ext}"
            
            # Download video
            ydl.download([video_url])
            
            # Verifikasi file telah didownload
            if not os.path.exists(filename):
                return jsonify({"error": "File tidak berhasil didownload"}), 500
            
            try:
                # Kirim file ke user dengan nama yang sesuai
                return send_file(
                    filename,
                    as_attachment=True,
                    download_name=f"{video_title}.{video_ext}"
                )
            finally:
                # Hapus file setelah dikirim
                try:
                    os.remove(filename)
                except:
                    pass  # Abaikan error jika file tidak dapat dihapus

    except Exception as e:
        error_message = str(e)
        print(f"Error: {error_message}", file=sys.stderr)  # Log error ke stderr
        return jsonify({"error": f"Terjadi kesalahan: {error_message}"}), 500

if __name__ == "__main__":
    app.run(debug=True)