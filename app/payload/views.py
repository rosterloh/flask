from flask import Blueprint, render_template, request, redirect, url_for, jsonify
# http://pymotw.com/2/hmac/
import hmac
import hashlib
# http://techarena51.com/index.php/how-to-install-python-3-and-flask-on-linux/
import subprocess
import os

payload = Blueprint('payload', __name__)

def verify_hmac_hash(data, signature):
    github_secret = bytes(os.environ['GITHUB_SECRET'], 'UTF-8')
    mac = hmac.new(github_secret, msg=data, digestmod=hashlib.sha1)
    return hmac.compare_digest('sha1=' + mac.hexdigest(), signature)

@payload.route("/", methods=['POST'])
def github_payload():
    signature = request.headers.get('X-Hub-Signature')
    data = request.data
    if verify_hmac_hash(data, signature):
        if request.headers.get('X-GitHub-Event') == "ping":
            return jsonify({'msg': 'Ok'})
        if request.headers.get('X-GitHub-Event') == "push":
            payload = request.get_json()
            if payload['commits'][0]['distinct'] == True:
                try:
                    cmd_output = subprocess.check_output(
                        ['git', 'pull', 'origin', 'master'],)
                    return jsonify({'msg': str(cmd_output)})
                except subprocess.CalledProcessError as error:
                    return jsonify({'msg': str(error.output)})
    else:
        return jsonify({'msg': 'invalid hash'})
