from flask import Flask, jsonify, send_file, request, abort
import subprocess, os, secrets

app = Flask(__name__)

# Shared secret between CTFd and this API
API_KEY = "djfshgdsfsdhfdhsvbchdfsgybreugfhberyfucgbeybvcyuerbhfbcyuehjfbjashureufrbheyufghbdeyugyerbfhrbg"
OVPN_DIR = "/root"  # where openvpn-install puts the .ovpn files

def require_api_key(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.headers.get("X-API-Key") != API_KEY:
            abort(403)
        return f(*args, **kwargs)
    return decorated

@app.route("/generate/<username>", methods=["POST"])
@require_api_key
def generate(username):
    # Sanitize username — only allow alphanumeric + underscore/dash
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return jsonify({"error": "Invalid username"}), 400

    ovpn_path = f"{OVPN_DIR}/{username}.ovpn"

    # Don't regenerate if already exists
    if not os.path.exists(ovpn_path):
        result = subprocess.run(
            ["/opt/vpn-api/add_client.sh", username],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500

    return send_file(ovpn_path, as_attachment=True,
                     download_name=f"{username}.ovpn")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

