import os
import requests
from flask import Flask, request
from flask_cors import CORS
import urllib3

# SSL 경고 비활성화 (개발 환경에서만 사용할 것)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Enable CORS support
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# Load env variables
SERVER_PORT = os.environ.get("SERVER_PORT",3001)
# SERVER_PORT
# OPENVIDU_URL = os.environ.get("OPENVIDU_URL")
# OPENVIDU_SECRET = os.environ.get("OPENVIDU_SECRET")
OPENVIDU_URL="https://13.125.231.212:4443/"
OPENVIDU_SECRET="VidU_3xS7_kEy9-Z1"
SESSION_TIMEOUT_MINUTES=60
OPENVIDU_VERIFY_SSL=False

@app.route("/api/sessions", methods=['POST'])
def initializeSession():
    try:
        body = request.json if request.data else {}
        response = requests.post(
            OPENVIDU_URL + "openvidu/api/sessions",
            verify=False,
            auth=("OPENVIDUAPP", OPENVIDU_SECRET),
            headers={'Content-type': 'application/json'},
            json=body
        )
        response.raise_for_status()
        return response.json()["sessionId"]
    except requests.exceptions.HTTPError as err:
        if (err.response.status_code == 409):
            # Session already exists in OpenVidu
            return request.json["customSessionId"]
        else:
            return err


@app.route("/api/sessions/<sessionId>/connections", methods=['POST'])
def createConnection(sessionId):
    body = request.json if request.data else {}
    return requests.post(
        OPENVIDU_URL + "openvidu/api/sessions/" + sessionId + "/connection",
        verify=False,
        auth=("OPENVIDUAPP", OPENVIDU_SECRET),
        headers={'Content-type': 'application/json'},
        json=body
    ).json()["token"]


if __name__ == "__main__":
    import ssl
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    # crt,key 파일 경로 설정
    ssl_context.load_cert_chain(certfile='./openvidu-selfsigned.crt', keyfile='./openvidu-selfsigned.key')
    app.run(debug=True, host="0.0.0.0", port=3001, ssl_context = ssl_context)
