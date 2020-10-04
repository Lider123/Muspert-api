from bottle import Bottle, request, response, run, static_file
from bottle_log import LoggingPlugin
from dotenv import load_dotenv
from firebase_admin import auth, credentials
from firebase_admin._auth_utils import InvalidIdTokenError
import firebase_admin
import db
import models
import os
import utils

HEADER_AUTHORIZATION = "Authorization"
ENV_HOST = "HOST"
ENV_PORT = "PORT"
ENV_GOOGLE_APPLICATION_CREDENTIALS = "GOOGLE_APPLICATION_CREDENTIALS"
DIR_MEDIA = "media"
DIR_AVATARS = DIR_MEDIA + "/avatars"

load_dotenv()
app = Bottle()
app.install(LoggingPlugin(app.config))


@app.get("/api/profile")
def get_profile():
    token = request.headers.get(HEADER_AUTHORIZATION)
    if token is None:
        response.status = 401
        return "Unauthorized"
    profile = db.get_user_by_token(token)
    if profile is None:
        profile = db.create_user(token)
        response.status = 201
    return profile


@app.post("/api/profile")
def update_profile():
    data = request.json
    try:
        profile = models.User(**data)
        db.update_user(profile)
        response.status = 200
        return "Success"
    except:
        response.status = 400
        return "Invalid user data"


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


@app.post("/api/media/avatar")
def upload_avatar():
    token = request.headers.get(HEADER_AUTHORIZATION)
    if token is None:
        response.status = 401
        return "Unauthorized"

    file = request.files.get("image")
    extension = file.filename.split('.')[-1]
    if extension not in ("png", "jpg", "jpeg"):
        response.status = 400
        return "Invalid file format"

    save_path = os.path.join(os.getcwd(), DIR_AVATARS)
    file.filename = utils.generate_random_string(32) + "." + extension
    file.save(save_path)
    user = db.get_user_by_token(token)
    os.remove(os.path.join(os.getcwd(), user["avatar"][1:]))
    db.update_avatar(token, "/" + DIR_AVATARS + "/" + file.filename)
    response.status = 200
    return "Success"


@app.get("/media/avatars/<filename>")
def get_avatar(filename):
    return static_file(filename, DIR_AVATARS)


if __name__ == "__main__":
    os.makedirs(os.path.join(os.getcwd(), DIR_MEDIA), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), DIR_AVATARS), exist_ok=True)
    cred = credentials.Certificate(os.getenv(ENV_GOOGLE_APPLICATION_CREDENTIALS))
    firebase_admin.initialize_app(cred)
    run(app, host=os.getenv(ENV_HOST), port=os.getenv(ENV_PORT), debug=True)
