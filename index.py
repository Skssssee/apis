from flask import Flask, Response, request, render_template_string, session
import requests
import os

app = Flask(__name__)
app.secret_key = "hotstar_secret" # Required for saving the cookie in your session

# --- CONFIGURATION ---
# The Match ID from your log
DEFAULT_URL = "https://live12p.hotstar.com/hls/live/2027118/inallow-icct20wc-2026/hin/1540062349/15mindvrm0119d6a0268f074e458ecd56115890359b16february2026/master_ap_1080_5.m3u8"

def get_headers(cookie):
    return {
        "User-Agent": "Mozilla/5.0 (Linux; Android 16; RMX3870 Build/BP2A.250605.015) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.7632.45 Mobile Safari/537.36",
        "Cookie": cookie,
        "Referer": "https://www.hotstar.com/",
        "Origin": "https://www.hotstar.com"
    }

@app.route('/')
def index():
    if 'cookie' not in session:
        return render_template_string("""
        <body style='background:#000;color:#fff;font-family:sans-serif;text-align:center;padding:20px;'>
            <h2 style='color:#fbc02d;'>🏏 AUS vs SL Player</h2>
            <p style='color:#ff5252;'>Your previous cookie expired at 8:31 PM.</p>
            <form method='POST' action='/set_cookie'>
                <p><b>Paste NEW hdntl Cookie:</b></p>
                <textarea name='cookie' style='width:100%;height:120px;background:#222;color:#0f0;border:1px solid #555;' placeholder='hdntl=exp=...'></textarea>
                <br><br>
                <button style='padding:15px;width:100%;background:#e50914;color:white;font-weight:bold;border:none;border-radius:5px;'>UPDATE & WATCH</button>
            </form>
        </body>
        """)
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vercel Proxy</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
        <style>body{background:#000;margin:0;display:flex;justify-content:center;align-items:center;height:100vh;}video{width:100%;max-width:1000px;}</style>
    </head>
    <body>
        <video id="v" controls autoplay muted playsinline></video>
        <script>
            var video = document.getElementById('v');
            if(Hls.isSupported()){
                var hls = new Hls({ lowLatencyMode: true });
                hls.loadSource('/playlist.m3u8');
                hls.attachMedia(video);
            }
        </script>
        <a href="/logout" style="position:absolute;top:10px;right:10px;color:white;text-decoration:none;border:1px solid #444;padding:5px;font-size:10px;">Update Cookie</a>
    </body>
    </html>
    """)

@app.route('/set_cookie', methods=['POST'])
def set_cookie():
    session['cookie'] = request.form.get('cookie').strip()
    return "✅ Cookie Updated! <a href='/'>Go to Player</a>"

@app.route('/logout')
def logout():
    session.pop('cookie', None)
    return "Session Cleared! <a href='/'>Click to update cookie</a>"

@app.route('/playlist.m3u8')
def playlist():
    cookie = session.get('cookie')
    if not cookie: return "No Cookie", 401
    try:
        r = requests.get(DEFAULT_URL, headers=get_headers(cookie), timeout=5)
        if r.status_code != 200: return f"Error {r.status_code}", 403
        content = r.text.replace('master_ap_', f'http://{request.host}/ts?path=master_ap_')
        return Response(content, mimetype='application/vnd.apple.mpegurl')
    except: return "Server Error", 500

@app.route('/ts')
def ts():
    cookie = session.get('cookie')
    filename = request.args.get('path')
    base_folder = DEFAULT_URL.rsplit('/', 1)[0]
    full_url = f"{base_folder}/{filename}"
    try:
        r = requests.get(full_url, headers=get_headers(cookie), timeout=10)
        return Response(r.content, mimetype='video/mp2t')
    except: return "", 404
