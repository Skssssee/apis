from flask import Flask, Response, request, render_template_string
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
# 360p URL: Good quality, but light enough for Pydroid
PLAYLIST_URL = "http://live12p-sgai-n-akt.cdn.hotstar.com/hls/live/2123018/inallow-icct20wc-2026/hin/1540062234/15mindvrm02c61baa8d09694903a31e4c9523f4c11e16february2026/master_ap_360_3.m3u8?random=1-inallow-icct20wc-2026&content_id=1540062234&language=hindi&resolution=640x360&hash=18bc&bandwidth=600000&media_codec=codec=h264:dr=sdr&audio_codec=aac&layer=child&playback_proto=http&playback_host=live12p-pristine-akt.cdn.hotstar.com&si_match_id=720227&routing_bucket=156"
BASE_HOST = "http://live12p-sgai-n-akt.cdn.hotstar.com"

# Your Valid Cookie (Valid until ~3:52 PM)
COOKIE_VAL = "hdntl=exp=1771237323~acl=/hls/live/2123018/inallow-icct20wc-2026/hin/1540062234/15mindvrm02c61baa8d09694903a31e4c9523f4c11e16february2026/master_ap*~data=ip=dvgYakk4pgcpRwdQH5SsXnXUfiegtNJTYUiVOdgMplVnXVkLGNVLP6p-userid=zIQJvMh3RNmr5ThaqKfu26SThrVSDC3lg8jmv9fJNoGy-did=GqsHiVNnnMOX81FeAh3iyvin8x6NhqpC7Y1bdByE4WjtOtSmH6UHZTQ-cc=in-de=1-pl=android-ap=26.01.13.2-ut=free-fpassv2-chids=A3T52V7U-ttl=1800-type=paid-raf=1771236123-rd=12781-cd=1619-ad=14400-ce=1771235523-~hmac=93c11f7dc0f5f2beac96d8cb140f4a731ed174793bb39247835b115c62cabecd"

HEADERS = {
    "User-Agent": "Hotstar;in.startv.hotstar/26.01.13.2.12194 (Android/16)",
    "Cookie": COOKIE_VAL,
    "Hs-Id": "SSAI::A_U:D_15T25:G_U:S_JH:M_NA:N_NA:P_P_AN",
    "X-HS-App-Id": "92b368a2-9fb1-4ba7-80a6-2411a9a7b6c9",
    "Connection": "keep-alive"
}

# Session makes downloads 2x faster
session = requests.Session()
session.headers.update(HEADERS)

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live 360p</title>
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
        <style>body{background:#000;margin:0;display:flex;justify-content:center;align-items:center;height:100vh;}video{width:100%;max-width:800px;border:1px solid #333;}</style>
    </head>
    <body>
        <video id="v" controls autoplay muted playsinline></video>
        <script>
            var v = document.getElementById('v');
            if(Hls.isSupported()){
                var hls = new Hls({
                    lowLatencyMode: true,
                    backBufferLength: 90
                });
                hls.loadSource('/playlist.m3u8');
                hls.attachMedia(v);
            }
        </script>
    </body>
    </html>
    """)

@app.route('/playlist.m3u8')
def playlist():
    try:
        r = session.get(PLAYLIST_URL, timeout=3)
        content = r.text.replace('/hls/live/', f'http://{request.host}/ts?path=/hls/live/')
        return Response(content, mimetype='application/vnd.apple.mpegurl')
    except Exception as e:
        return str(e), 500

@app.route('/ts')
def ts():
    path = request.args.get('path')
    def generate():
        try:
            # Increased timeout to prevent dropping chunks on slow networks
            with session.get(f"{BASE_HOST}{path}", stream=True, timeout=10) as r:
                if r.status_code == 200:
                    for chunk in r.iter_content(chunk_size=8192):
                        yield chunk
                else:
                    print(f"❌ Error: {r.status_code}")
        except Exception as e:
            print(f"Stream Error: {e}")

    return Response(generate(), mimetype='video/mp2t')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
