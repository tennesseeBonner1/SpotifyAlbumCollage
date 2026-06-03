import webbrowser
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests

CLIENT_ID = "3a836f83ac8349b6a97ad3a655f3bd6c"
CLIENT_SECRET = "cbe4c06d6ada4464a7a7e275448916c1"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-library-read"

auth_code = None

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code

        parsed = urllib.parse.urlparse(self.path)

        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return

        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            auth_code = params["code"][0]
            print("Received auth code!")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"You can close this tab now.")
        else:
            print("No code found in callback")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing code")

    def log_message(self, format, *args):
        return  # silence default logging

def get_auth_code():
    print ("Getting authorization code...")
    global auth_code

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "scope": SCOPE,
        "redirect_uri": REDIRECT_URI,
    }

    url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)

    webbrowser.open(url)

    server = HTTPServer(("localhost", 8888), Handler)

    while auth_code is None:
        server.handle_request()

    server.server_close()

    print("authorization code received.")
    return auth_code

def get_access_token():
    print ("Getting access token...")
    auth_code = get_auth_code()

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": REDIRECT_URI,
        },
        auth=(CLIENT_ID, CLIENT_SECRET),
    )

    response.raise_for_status()

    print("access token received.")
    return response.json()["access_token"]
