from bottle import Bottle, request, response, run
from bottle_log import LoggingPlugin
from dotenv import load_dotenv
from firebase_admin import auth, credentials
from firebase_admin._auth_utils import InvalidIdTokenError
import firebase_admin
import os
import pymysql

load_dotenv()
app = Bottle()
app.install(LoggingPlugin(app.config))


@app.get("/api/profile")
def get_profile():
    token = request.headers.get("Authorization")
    if token is None:
        response.status = 401
        return "Unauthorized"
    profile = get_profile_from_db(token)
    if profile is None:
        profile = create_user(token)
        response.status = 201
    return profile


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


def get_profile_from_db(token):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            query = f"""
            SELECT user_id, nickname, first_name, last_name
            FROM users
            WHERE firebase_token = '{token}'
            """
            cursor.execute(query)
            result = cursor.fetchone()
            return result
    finally:
        connection.close()


def create_user(token):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            query = f"""
            INSERT INTO users (firebase_token) VALUES ('{token}')
            """
            cursor.execute(query)
        connection.commit()
    finally:
        connection.close()
    return get_profile_from_db(token)


def create_connection():
    return pymysql.connect(host="localhost",
                           user="admin",
                           password="admin",
                           db="muspert",
                           charset="utf8mb4",
                           cursorclass=pymysql.cursors.DictCursor)


if __name__ == "__main__":
    cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
    firebase_admin.initialize_app(cred)
    run(app, host="0.0.0.0", port=8080, debug=True)
