from flask import Flask, Response, redirect, request
import requests

app = Flask(__name__)

# CONFIGURATION
PLAYLIST_URL = "http://live-sgai-n-cf-mum-child.cdn.hotstar.com/hls/live/2123018/inallow-icct20wc-2026/hin/1540062231/15mindvrm01a6e7bbda1dae497c99f40c96defdc14616february2026/master_ap_1080_6.m3u8?random=1-inallow-icct20wc-2026&content_id=1540062231&language=hindi&resolution=1920x1080&hash=18bc&bandwidth=2490400&media_codec=codec=h264:dr=sdr&audio_codec=aac&layer=child&playback_proto=http&playback_host=live12p-pristine-akt.cdn.hotstar.com&si_match_id=720226&routing_bucket=156&asn_id=tffsz"
BASE_HOST = "http://live12p-sgai-n-akt.cdn.hotstar.com"
HEADERS = {
    "User-Agent": "Hotstar;in.startv.hotstar/26.01.13.2.12194 (Android/16)",
    "Cookie": "hdntl=exp=1771233993~acl=/hls/live/2123018/inallow-icct20wc-2026/hin/1540062231/15mindvrm01a6e7bbda1dae497c99f40c96defdc14616february2026/master_ap*~data=ip=MaHZHDdAjnzVufuZhe4J2D-userid=zIQJvMh3RNmr5ThaqKfu26SThrVSDC3lg8jmv9fJNoGy-did=GqsHiVNnnMOX81FeAh3iyvin8x6NhqpC7Y1bdByE4WjtOtSmH6UHZTQ-cc=in-de=1-pl=android-ap=26.01.13.2-ut=free-fpassv2-chids=A3T52V7U-ttl=1800-type=paid-raf=1771232793-rd=12813-cd=1587-ad=14400-ce=1771232193-~hmac=fc079f5f96cc1c30b2273c2f871af984cc04cfef7921a783724d98c5e5a23520"
}

@app.route('/')
def home():
    return "Stream is Live. Use /playlist.m3u8 in your player."

@app.route('/playlist.m3u8')
def proxy_m3u8():
    r = requests.get(PLAYLIST_URL, headers=HEADERS)
    # Get the base URL of your current Vercel deployment
    host = request.host_url.rstrip('/')
    # Rewrite segments to point to our redirector
    content = r.text.replace('/hls/live/', f'{host}/ts?path=/hls/live/')
    
    resp = Response(content, mimetype='application/vnd.apple.mpegurl')
    resp.headers['Access-Control-Allow-Origin'] = '*' # Critical for web players
    return resp

@app.route('/ts')
def redirect_ts():
    ts_path = request.args.get('path')
    # Instead of fetching the video, we tell the browser: "Go find it here"
    # Note: This only works if Hotstar's CDN doesn't block the browser's User-Agent.
    return redirect(f"{BASE_HOST}{ts_path}", code=302)

# Vercel needs this
def handler(event, context):
    return app(event, context)
