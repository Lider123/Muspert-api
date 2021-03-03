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
                SELECT id, nickname, first_name, last_name, avatar
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
                    nickname = '{user.nickname}',
                    avatar = '{user.avatar}'
                WHERE id = {user.id}
            """
            cursor.execute(query)
        connection.commit()
    finally:
        connection.close()
        return


def update_avatar(token, path):
    user = get_user_by_token(token)
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            query = f"""
                UPDATE users
                SET
                    avatar = '{path}'
                WHERE id = {user['id']}
            """
            cursor.execute(query)
        connection.commit()
    finally:
        connection.close()
        return


def get_albums(limit, offset):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            query = f"""
                SELECT
                    albums.id,
                    albums.title,
                    albums.cover,
                    artists.name AS artistName,
                    cast(albums.createdAt as unsigned) AS createdAt
                FROM albums LEFT JOIN artists ON albums.artistId = artists.id
                ORDER BY createdAt DESC
                LIMIT {limit}
                OFFSET {offset}
            """
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    finally:
        connection.close()


def get_genres(limit, offset):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            query = f"""
                SELECT id, title, image
                FROM genres
                LIMIT {limit}
                OFFSET {offset}
            """
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    finally:
        connection.close()


def get_tracks_by_album_id(album_id, user_id):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            query = f"""
                    SELECT
                        tracks.id AS id,
                        tracks.title AS title,
                        tracks.link AS link,
                        tracks.albumId AS albumId,
                        tracks.position AS position,
                        albums.cover AS cover,
                        albums.title AS albumTitle,
                        artists.name AS artistName,
                        IF(favorites.userId IS NOT NULL, 'true', 'false') AS isFavorite
                    FROM tracks
                        LEFT JOIN albums ON tracks.albumId = albums.id
                        LEFT JOIN artists ON albums.artistId = artists.id
                        LEFT JOIN favorites ON favorites.trackId = tracks.id AND favorites.userId = {user_id}
                    WHERE tracks.albumId = {album_id}
                    ORDER BY tracks.position
                """
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    finally:
        connection.close()


def create_favorite(user_id, track_id):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            query = f"""
                    INSERT INTO favorites (userId, trackId)
                    VALUES ('{user_id}', '{track_id}')
                """
            cursor.execute(query)
        connection.commit()
    finally:
        connection.close()


def delete_favorite(user_id, track_id):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            query = f"""
                DELETE FROM favorites
                WHERE userId = {user_id} AND trackId = {track_id}
            """
            cursor.execute(query)
        connection.commit()
    finally:
        connection.close()


def get_favorite_tracks(user_id, limit, offset):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            query = f"""
                SELECT
                    tracks.id AS id,
                    tracks.title AS title,
                    tracks.link AS link,
                    tracks.albumId AS albumId,
                    tracks.position AS position,
                    albums.cover AS cover,
                    albums.title AS albumTitle,
                    artists.name AS artistName,
                    IF(favorites.userId IS NOT NULL, 'true', 'false') AS isFavorite
                FROM tracks
                    LEFT JOIN albums ON tracks.albumId = albums.id
                    LEFT JOIN artists ON albums.artistId = artists.id
                    LEFT JOIN favorites ON favorites.trackId = tracks.id AND favorites.userId = {user_id}
                WHERE favorites.userId IS NOT NULL
                ORDER BY favorites.createdAt DESC
            """
            if limit is not None:
                query += f" LIMIT {limit}"
            if offset is not None:
                query += f" OFFSET {offset}"
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    finally:
        connection.close()


def get_search_results(query, limit, offset):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            query = f"""
                SELECT
                    albums.id,
                    albums.title,
                    albums.cover,
                    artists.name AS artistName,
                    cast(albums.createdAt as unsigned) AS createdAt
                FROM albums LEFT JOIN artists ON albums.artistId = artists.id
                WHERE albums.title LIKE '%{query}%'
                ORDER BY createdAt DESC
                LIMIT {limit}
                OFFSET {offset}
            """
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    finally:
        connection.close()
