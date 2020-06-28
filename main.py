from bottle import Bottle, request, response, run
from bottle_log import LoggingPlugin
from dotenv import load_dotenv
from firebase_admin import auth, credentials
from firebase_admin._auth_utils import InvalidIdTokenError
import firebase_admin
import os

load_dotenv()
app = Bottle()
app.install(LoggingPlugin(app.config))


@app.get("/api/profile")
def get_profile():
    return {  # TODO: return real one
        "id": 1,
        "nickname": "johndoe",
        "first_name": "John",
        "last_name": "Doe"
    }


@app.post("/api/authorization")
def authorize():
    data = request.json
    try:
        decoded_token = auth.verify_id_token(data["access_token"])
        uid = decoded_token["uid"]
        return {
            "token": uid
        }
    except InvalidIdTokenError:
        response.status = 510
        return "Invalid auth token"


if __name__ == "__main__":
    cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
    firebase_admin.initialize_app(cred)
    run(app, host="0.0.0.0", port=8080, debug=True)
