from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('video_url')
    if not url:
        return "URL tidak valid!", 400

    try:
        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(info)
            ydl.download([url])

        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Terjadi kesalahan: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)