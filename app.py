from flask import Flask, request, jsonify
import subprocess
import requests
import os
import tempfile

app = Flask(__name__)

@app.route('/merge', methods=['POST'])
def merge():
    data = request.json
    video_url = data.get('video_url')
    audio_url = data.get('audio_url')
    
    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, 'video.mp4')
        audio_path = os.path.join(tmpdir, 'audio.mp3')
        output_path = os.path.join(tmpdir, 'output.mp4')
        
        # Download files
        with open(video_path, 'wb') as f:
            f.write(requests.get(video_url).content)
        with open(audio_path, 'wb') as f:
            f.write(requests.get(audio_url).content)
        
        # Merge with FFmpeg
        cmd = [
            'ffmpeg', '-stream_loop', '-1',
            '-i', video_path,
            '-i', audio_path,
            '-shortest', '-c:v', 'libx264',
            '-c:a', 'aac', '-y', output_path
        ]
        subprocess.run(cmd, check=True)
        
        with open(output_path, 'rb') as f:
            video_data = f.read()
    
    import base64
    return jsonify({'video_base64': base64.b64encode(video_data).decode()})

@app.route('/')
def health():
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
