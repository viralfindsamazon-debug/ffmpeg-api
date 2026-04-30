from flask import Flask, request, jsonify
import subprocess
import requests
import os
import tempfile
import base64

app = Flask(__name__)

OPENAI_KEY = os.environ.get('OPENAI_KEY', '')

@app.route('/merge', methods=['POST'])
def merge():
    data = request.json
    video_url = data.get('video_url')
    script = data.get('script')
    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, 'video.mp4')
        audio_path = os.path.join(tmpdir, 'audio.mp3')
        output_path = os.path.join(tmpdir, 'output.mp4')
        with open(video_path, 'wb') as f:
            f.write(requests.get(video_url, timeout=60).content)
        tts_response = requests.post(
            'https://api.openai.com/v1/audio/speech',
            headers={'Authorization': f'Bearer {OPENAI_KEY}', 'Content-Type': 'application/json'},
            json={'model': 'tts-1', 'input': script[:4096], 'voice': 'onyx', 'response_format': 'mp3'},
            timeout=120
        )
        with open(audio_path, 'wb') as f:
            f.write(tts_response.content)
        cmd = ['ffmpeg', '-stream_loop', '-1', '-i', video_path, '-i', audio_path, '-shortest', '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28', '-c:a', 'aac', '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2', '-y', output_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({'error': result.stderr}), 500
        with open(output_path, 'rb') as f:
            video_data = f.read()
    return jsonify({'video_base64': base64.b64encode(video_data).decode()})

@app.route('/')
def health():
    return 'OK'
