from flask import Flask, request, jsonify
import urllib.request
import urllib.parse
import ssl
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

_ssl = ssl.create_default_context()
_ssl.check_hostname = False
_ssl.verify_mode = ssl.CERT_NONE

BASE = "https://danger-guild-management-web.vercel.app"
JOIN_ENDPOINTS = [f"{BASE}/join"]
LEAVE_ENDPOINTS = [
    f"{BASE}/leave",
    f"{BASE}/guild/leave",
    f"{BASE}/quit",
    f"{BASE}/guild/quit",
    f"{BASE}/exit",
]
# تم التحديث إلى إصدار OB55 الحالي
UA = "Mozilla/5.0 (Linux; Android 10) GREAT_JOHIR/5.5"

def _get(url, timeout=20):
    req = urllib.request.Request(url, method="GET", headers={
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Connection": "close",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ssl) as r:
            return True, r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try: body = e.read().decode("utf-8", "replace")
        except: body = ""
        return False, e.code, body
    except Exception as e:
        return False, 0, str(e)

def _call(endpoints, guild_id, uid, pwd):
    last = (False, 0, "")
    for ep in endpoints:
        q = urllib.parse.urlencode({"guild_id": guild_id, "uid": uid, "password": pwd})
        ok, code, body = _get(f"{ep}?{q}")
        if ok: return True, code, body
        last = (False, code, body)
    return last

@app.route('/join', methods=['GET'])
def api_join():
    uid = request.args.get('uid')
    pw = request.args.get('pw') or request.args.get('password')
    uid_clan = request.args.get('uid_clan') or request.args.get('guild_id')

    if not uid or not pw or not uid_clan:
        return jsonify({"status": "error", "message": "Missing required parameters (uid, pw, uid_clan)"}), 400

    ok, code, body = _call(JOIN_ENDPOINTS, uid_clan, uid, pw)
    
    return jsonify({
        "status": "success" if ok else "failed",
        "http_code": code,
        "action": "join",
        "version": "OB55",
        "uid": uid,
        "uid_clan": uid_clan,
        "response": body
    }), code if code != 0 else 500

@app.route('/leave', methods=['GET'])
def api_leave():
    uid = request.args.get('uid')
    pw = request.args.get('pw') or request.args.get('password')
    uid_clan = request.args.get('uid_clan') or request.args.get('guild_id')

    if not uid or not pw or not uid_clan:
        return jsonify({"status": "error", "message": "Missing required parameters (uid, pw, uid_clan)"}), 400

    ok, code, body = _call(LEAVE_ENDPOINTS, uid_clan, uid, pw)
    
    return jsonify({
        "status": "success" if ok else "failed",
        "http_code": code,
        "action": "leave",
        "version": "OB55",
        "uid": uid,
        "uid_clan": uid_clan,
        "response": body
    }), code if code != 0 else 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "active", "engine": "GREAT JOHIR OB55 API", "routes": ["/join?uid=&pw=&uid_clan=", "/leave?uid=&pw=&uid_clan="]})

# ملاحظة: لا تستخدم app.run هنا لأن Vercel يديره تلقائياً عبر ملف الـ json
