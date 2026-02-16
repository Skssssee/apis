from flask import Flask, Response, request
import requests

app = Flask(__name__)

# ──────────────────────────────────────────────
#                  CONFIGURATION
# ──────────────────────────────────────────────

PLAYLIST_URL = "http://live12p-sgai-n-akt.cdn.hotstar.com/hls/live/2123018/inallow-icct20wc-2026/hin/1540062234/15mindvrm02c61baa8d09694903a31e4c9523f4c11e16february2026/master_ap_1080_6.m3u8?random=1-inallow-icct20wc-2026&content_id=1540062234&language=hindi&resolution=1920x1080&hash=18bc&bandwidth=2490400&media_codec=codec=h264:dr=sdr&audio_codec=aac&layer=child&playback_proto=http&playback_host=live12p-pristine-akt.cdn.hotstar.com&si_match_id=720227&routing_bucket=156&asn_id=tffsz"

BASE_HOST = "http://live12p-sgai-n-akt.cdn.hotstar.com"

COOKIE_VAL = "hdntl=exp=1771237323\~acl=/hls/live/2123018/inallow-icct20wc-2026/hin/1540062234/15mindvrm02c61baa8d09694903a31e4c9523f4c11e16february2026/master_ap*\~data=ip=dvgYakk4pgcpRwdQH5SsXnXUfiegtNJTYUiVOdgMplVnXVkLGNVLP6p-userid=zIQJvMh3RNmr5ThaqKfu26SThrVSDC3lg8jmv9fJNoGy-did=GqsHiVNnnMOX81FeAh3iyvin8x6NhqpC7Y1bdByE4WjtOtSmH6UHZTQ-cc=in-de=1-pl=android-ap=26.01.13.2-ut=free-fpassv2-chids=A3T52V7U-ttl=1800-type=paid-raf=1771236123-rd=12781-cd=1619-ad=14400-ce=1771235523-\~hmac=93c11f7dc0f5f2beac96d8cb140f4a731ed174793bb39247835b115c62cabecd"

HEADERS = {
    "User-Agent": "Hotstar;in.startv.hotstar/26.01.13.2.12194 (Android/16)",
    "Cookie": COOKIE_VAL,
    "Hs-Id": "SSAI::A_U:D_15T25:G_U:S_JH:M_NA:N_NA:P_P_AN",
    "X-HS-App-Id": "92b368a2-9fb1-4ba7-80a6-2411a9a7b6c9",
    "X-HS-Platform": "android",
    "X-Country-Code": "in",
    "Connection": "keep-alive"
}

session = requests.Session()
session.headers.update(HEADERS)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>1080p Stream (Vercel)</title>
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
        <style>
            body {background:#000; margin:0; display:flex; justify-content:center; align-items:center; height:100vh;}
            video {width:94%; max-width:1200px; border:1px solid #444;}
        </style>
    </head>
    <body>
        <video id="v" controls autoplay muted playsinline></video>
        <script>
            const video = document.getElementById('v');
            if (Hls.isSupported()) {
                const hls = new Hls({
                    enableWorker: true,
                    lowLatencyMode: true,
                    maxBufferLength: 30,
                    maxMaxBufferLength: 60
                });
                hls.loadSource('/api/playlist.m3u8');
                hls.attachMedia(video);
                hls.on(Hls.Events.ERROR, (event, data) => {
                    console.error("HLS Error:", data);
                });
            } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                video.src = '/api/playlist.m3u8';
            }
        </script>
    </body>
    </html>
    """

@app.route('/api/playlist.m3u8')
def playlist():
    try:
        r = session.get(PLAYLIST_URL, timeout=5)
        r.raise_for_status()
        content = r.text.replace('/hls/live/', f'/api/ts?path=/hls/live/')
        # You can also try: .replace(BASE_HOST, f"https://{request.host}")
        return Response(content, mimetype='application/vnd.apple.mpegurl')
    except Exception as e:
        return f"Error fetching master: {str(e)}", 503

@app.route('/api/ts')
def ts():
    path = request.args.get('path')
    if not path:
        return "Missing path", 400

    target_url = f"{BASE_HOST}{path}"

    def generate():
        try:
            with session.get(target_url, stream=True, timeout=12) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=32*1024):
                    yield chunk
        except Exception as e:
            print(f"Stream error {target_url}: {e}")
            yield b""  # just close gracefully

    return Response(generate(), mimetype='video/mp2t')

# Vercel needs this (WSGI callable)
application = app
