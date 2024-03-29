from bottle import Bottle, request, response, run, static_file
from bottle_log import LoggingPlugin
from dotenv import load_dotenv
from firebase_admin import auth, credentials
from firebase_admin._auth_utils import InvalidIdTokenError
import firebase_admin
import db
import json
import models
import os
import utils

HEADER_AUTHORIZATION = "Authorization"
ENV_HOST = "HOST"
ENV_PORT = "PORT"
ENV_GOOGLE_APPLICATION_CREDENTIALS = "GOOGLE_APPLICATION_CREDENTIALS"
DIR_MEDIA = "media"
DIR_AVATARS = DIR_MEDIA + "/avatars"
DIR_COVERS = DIR_MEDIA + "/covers"
DIR_GENRES = DIR_MEDIA + "/genres"
DIR_MUSIC = DIR_MEDIA + "/music"

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
    old_avatar_path = os.path.join(os.getcwd(), user["avatar"][1:])
    db.update_avatar(token, "/" + DIR_AVATARS + "/" + file.filename)
    if os.path.exists(old_avatar_path):
        os.remove(old_avatar_path)
    response.status = 200
    return "Success"


@app.get("/media/avatars/<filename>")
def get_avatar(filename):
    return static_file(filename, DIR_AVATARS)


@app.get("/media/covers/<filename>")
def get_cover(filename):
    return static_file(filename, DIR_COVERS)


@app.get("/media/genres/<filename>")
def get_cover(filename):
    return static_file(filename, DIR_GENRES)


@app.get("/media/music/<filename>")
def get_track(filename):
    return static_file(filename, DIR_MUSIC)


@app.get("/api/catalog/albums")
def get_albums():
    token = request.headers.get(HEADER_AUTHORIZATION)
    if token is None:
        response.status = 401
        return "Unauthorized"

    offset = request.query.offset or '0'
    limit = request.query.limit or "20"
    albums = db.get_albums(limit, offset)
    return json.dumps(albums, ensure_ascii=False)


@app.get("/api/catalog/genres")
def get_genres():
    token = request.headers.get(HEADER_AUTHORIZATION)
    if token is None:
        response.status = 401
        return "Unauthorized"

    offset = request.query.offset or '0'
    limit = request.query.limit or "20"
    genres = db.get_genres(limit, offset)
    return json.dumps(genres, ensure_ascii=False)


@app.get("/api/catalog/tracks/<track_id>")
def get_track(track_id):
    token = request.headers.get(HEADER_AUTHORIZATION)
    if token is None:
        response.status = 401
        return "Unauthorized"

    if track_id is None:
        response.status = 400
        return "Bad request"

    user = db.get_user_by_token(token)
    track = db.get_track(track_id, user["id"])
    if track is None:
        response.status = 404
        return "Not found"

    return json.dumps(track, ensure_ascii=False)


@app.get("/api/catalog/tracks")
def get_tracks():
    token = request.headers.get(HEADER_AUTHORIZATION)
    if token is None:
        response.status = 401
        return "Unauthorized"

    album_id = request.query.albumId or None
    if album_id is None:
        response.status = 400
        return "Bad request"

    user = db.get_user_by_token(token)
    tracks = db.get_tracks_by_album_id(album_id, user["id"])
    return json.dumps(tracks, ensure_ascii=False)


@app.get("/api/catalog/tracks/info")
def get_track_infos():
    token = request.headers.get(HEADER_AUTHORIZATION)
    if token is None:
        response.status = 401
        return "Unauthorized"

    album_id = request.query.albumId or None
    if album_id is None:
        response.status = 400
        return "Bad request"

    track_infos = db.get_track_infos_by_album_id(album_id)
    return json.dumps(track_infos, ensure_ascii=False)


@app.post("/api/favorites")
def add_to_favorites():
    data = request.json
    token = request.headers.get(HEADER_AUTHORIZATION)
    try:
        favorites_request = models.AddToFavoritesRequest(**data)
        user = db.get_user_by_token(token)
        db.create_favorite(user["id"], favorites_request.trackId)
        response.status = 200
        return "Success"
    except:
        response.status = 500
        return "Internal server error"


@app.delete("/api/favorites/<track_id>")
def remove_from_favorites(track_id):
    token = request.headers.get(HEADER_AUTHORIZATION)
    try:
        user = db.get_user_by_token(token)
        db.delete_favorite(user["id"], track_id)
        response.status = 200
        return "Success"
    except:
        response.status = 500
        return "Internal server error"


@app.get("/api/catalog/favorites")
def get_favorite_tracks():
    token = request.headers.get(HEADER_AUTHORIZATION)
    if token is None:
        response.status = 401
        return "Unauthorized"

    offset = request.query.offset or None
    limit = request.query.limit or None
    user = db.get_user_by_token(token)
    tracks = db.get_favorite_tracks(user["id"], limit, offset)
    return json.dumps(tracks, ensure_ascii=False)


@app.get("/api/catalog/favorites/info")
def get_favorite_track_infos():
    token = request.headers.get(HEADER_AUTHORIZATION)
    if token is None:
        response.status = 401
        return "Unauthorized"

    user = db.get_user_by_token(token)
    tracks = db.get_favorite_track_infos(user["id"])
    return json.dumps(tracks, ensure_ascii=False)


@app.get("/api/search")
def search():
    token = request.headers.get(HEADER_AUTHORIZATION)
    if token is None:
        response.status = 401
        return "Unauthorized"

    query = request.query.query or None
    if query is None or len(str(query)) < 1:
        response.status = 400
        return "Bad request"

    offset = request.query.offset or '0'
    limit = request.query.limit or "20"
    albums = db.get_search_results(query, limit, offset)
    return json.dumps(albums, ensure_ascii=False)


if __name__ == "__main__":
    os.makedirs(os.path.join(os.getcwd(), DIR_MEDIA), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), DIR_AVATARS), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), DIR_COVERS), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), DIR_GENRES), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), DIR_MUSIC), exist_ok=True)
    cred = credentials.Certificate(os.getenv(ENV_GOOGLE_APPLICATION_CREDENTIALS))
    firebase_admin.initialize_app(cred)
    run(app, host=os.getenv(ENV_HOST), port=os.getenv(ENV_PORT), debug=True)
