import models
import os
import pymysql

ENV_DB_HOST = "DB_HOST"
ENV_DB_USER = "DB_USER"
ENV_DB_PASS = "DB_PASS"
ENV_DB_NAME = "DB_NAME"


def create_connection():
    return pymysql.connect(host=os.getenv(ENV_DB_HOST),
                           user=os.getenv(ENV_DB_USER),
                           password=os.getenv(ENV_DB_PASS),
                           db=os.getenv(ENV_DB_NAME),
                           charset="utf8mb4",
                           cursorclass=pymysql.cursors.DictCursor)


def get_user_by_token(token: str):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            query = f"""
                SELECT id, nickname, first_name, last_name
                FROM users
                WHERE firebase_token = '{token}'
            """
            cursor.execute(query)
            result = cursor.fetchone()
            return result
    finally:
        connection.close()


def create_user(token: str):
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
    return get_user_by_token(token)


def update_user(user: models.User):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            query = f"""
                UPDATE users
                SET
                    first_name = '{user.first_name}',
                    last_name = '{user.last_name}',
                    nickname = '{user.nickname}'
                WHERE id = {user.id}
            """
            cursor.execute(query)
        connection.commit()
    finally:
        connection.close()
        return