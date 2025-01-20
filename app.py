import os
import subprocess
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/get-video-info", methods=["POST"])
def get_video_info():
    video_url = request.form.get("url")
    if not video_url:
        return jsonify({"error": "URL tidak boleh kosong"}), 400

    try:
        # Dapatkan informasi video menggunakan yt-dlp
        command = [
            "yt-dlp",
            "--cookies", "cookies.txt",
            "-J",  # Output dalam format JSON
            video_url
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500

        # Parse output JSON dan ambil informasi yang diperlukan
        import json
        video_info = json.loads(result.stdout)
        
        # Filter dan format informasi yang diperlukan
        formats = []
        for f in video_info.get('formats', []):
            # Skip format yang tidak memiliki URL
            if not f.get('url'):
                continue
                
            format_info = {
                'format_id': f.get('format_id'),
                'ext': f.get('ext'),
                'quality': f.get('quality', ''),
                'resolution': f.get('resolution', 'N/A'),
                'filesize': f.get('filesize', 0),
                'url': f.get('url'),
                'format_note': f.get('format_note', ''),
                'vcodec': 'video only' if f.get('vcodec') != 'none' and f.get('acodec') == 'none' else \
                         'audio only' if f.get('vcodec') == 'none' and f.get('acodec') != 'none' else \
                         'video+audio'
            }
            formats.append(format_info)
        
        # Filter format yang memiliki video+audio saja untuk kemudahan user
        formats = [f for f in formats if f['vcodec'] == 'video+audio']
        
        response = {
            'title': video_info.get('title', ''),
            'thumbnail': video_info.get('thumbnail', ''),
            'duration': video_info.get('duration', 0),
            'formats': formats
        }
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)