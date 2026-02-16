from flask import Flask, Response, request, render_template_string
import requests

app = Flask(__name__)

# --- CONFIGURATION (Bucket: 2027118) ---
PLAYLIST_URL = "https://live12p.hotstar.com/hls/live/2027118/inallow-icct20wc-2026/hin/1540062349/15mindvrm0119d6a0268f074e458ecd56115890359b16february2026/master_ap_1080_5.m3u8"
COOKIE_VAL = "hdntl=exp=1771254060~acl=/hls/live/2027118/inallow-icct20wc-2026/hin/1540062349/15mindvrm0119d6a0268f074e458ecd56115890359b16february2026/master_ap*~data=ip=MaHZHDdAjnzVufuZhe4J2D-userid=zIQJvMh3RNmr5ThaqKfu26SThrVSDC3lg8jmv9fJNoGy-did=i8FHpjtTqfOoMzX9myZkKDQsrQKkKDSdS0O59mzHlzQa-cc=in-de=1-pl=web-ap=26.01.11.0-ut=free-fpassv2-chids=A3T52V7U-ttl=1800-type=paid-raf=1771252860-rd=11486-cd=2914-ad=14400-ce=1771252260-~hmac=464b5313c984c0ea240b79c75ccfe195d77ba9b1323f6d64adcea963b0366bb3"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 16; RMX3870 Build/BP2A.250605.015) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.7632.45 Mobile Safari/537.36",
    "Cookie": COOKIE_VAL,
    "Referer": "https://www.hotstar.com/",
    "Origin": "https://www.hotstar.com"
}

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vercel Hotstar Proxy</title>
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
                hls.loadSource('/api/playlist');
                hls.attachMedia(video);
            }
        </script>
    </body>
    </html>
    """)

@app.route('/api/playlist')
def playlist():
    try:
        r = requests.get(PLAYLIST_URL, headers=HEADERS, timeout=5)
        if r.status_code != 200:
            return "❌ Token Expired", 403
            
        # Point segments to the internal proxy route
        # Using a relative path helps Vercel handle the routing correctly
        content = r.text.replace('master_ap_', '/api/ts?path=master_ap_')
        return Response(content, mimetype='application/vnd.apple.mpegurl')
    except Exception as e:
        return str(e), 500

@app.route('/api/ts')
def ts():
    filename = request.args.get('path')
    base_folder = PLAYLIST_URL.rsplit('/', 1)[0]
    full_url = f"{base_folder}/{filename}"
    
    # We fetch the segment and return it directly. 
    # For Vercel, we don't use 'yield' as it can cause streaming issues in serverless functions.
    try:
        r = requests.get(full_url, headers=HEADERS, timeout=10)
        return Response(r.content, mimetype='video/mp2t')
    except:
        return "", 404
