from flask import Flask, Response, redirect, request, render_template_string
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
PLAYLIST_URL = "http://live-sgai-n-cf-mum-child.cdn.hotstar.com/hls/live/2123018/inallow-icct20wc-2026/hin/1540062231/15mindvrm01a6e7bbda1dae497c99f40c96defdc14616february2026/master_ap_1080_6.m3u8?random=1-inallow-icct20wc-2026&content_id=1540062231&language=hindi&resolution=1920x1080&hash=18bc&bandwidth=2490400&media_codec=codec=h264:dr=sdr&audio_codec=aac&layer=child&playback_proto=http&playback_host=live12p-pristine-akt.cdn.hotstar.com&si_match_id=720226&routing_bucket=156&asn_id=tffsz"
BASE_HOST = "http://live12p-sgai-n-akt.cdn.hotstar.com"
HEADERS = {
    "User-Agent": "Hotstar;in.startv.hotstar/26.01.13.2.12194 (Android/16)",
    "Cookie": "hdntl=exp=1771233993~acl=/hls/live/2123018/inallow-icct20wc-2026/hin/1540062231/15mindvrm01a6e7bbda1dae497c99f40c96defdc14616february2026/master_ap*~data=ip=MaHZHDdAjnzVufuZhe4J2D-userid=zIQJvMh3RNmr5ThaqKfu26SThrVSDC3lg8jmv9fJNoGy-did=GqsHiVNnnMOX81FeAh3iyvin8x6NhqpC7Y1bdByE4WjtOtSmH6UHZTQ-cc=in-de=1-pl=android-ap=26.01.13.2-ut=free-fpassv2-chids=A3T52V7U-ttl=1800-type=paid-raf=1771232793-rd=12813-cd=1587-ad=14400-ce=1771232193-~hmac=fc079f5f96cc1c30b2273c2f871af984cc04cfef7921a783724d98c5e5a23520"
}

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>LIVE T20 World Cup</title>
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
        <style>
            body { background: #000; margin: 0; display: flex; align-items: center; justify-content: center; height: 100vh; }
            video { width: 100%; max-width: 900px; border: 1px solid #333; }
        </style>
    </head>
    <body>
        <video id="video" controls autoplay></video>
        <script>
            var video = document.getElementById('video');
            if (Hls.isSupported()) {
                var hls = new Hls({ xhrSetup: function(xhr, url) { xhr.withCredentials = false; } });
                hls.loadSource('/playlist.m3u8');
                hls.attachMedia(video);
            }
        </script>
    </body>
    </html>
    """)

@app.route('/playlist.m3u8')
def proxy_m3u8():
    r = requests.get(PLAYLIST_URL, headers=HEADERS)
    host = request.host_url.rstrip('/')
    # Fix the paths to point to our local redirector
    content = r.text.replace('/hls/live/', f'{host}/ts?path=/hls/live/')
    resp = Response(content, mimetype='application/vnd.apple.mpegurl')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/ts')
def redirect_ts():
    ts_path = request.args.get('path')
    # 302 Redirect tells the browser to go to Hotstar directly.
    # This bypasses Vercel's 10MB limit and loading lag!
    return redirect(f"{BASE_HOST}{ts_path}", code=302)
