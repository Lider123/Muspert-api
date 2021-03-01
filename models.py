from collections import namedtuple

User = namedtuple("User", [
    "id",
    "first_name",
    "last_name",
    "nickname",
    "avatar"
])

Album = namedtuple("Album", [
    "id",
    "title",
    "cover",
    "artistName",
    "createdAt"
])

Genre = namedtuple("Genre", [
    "id",
    "title",
    "image"
])

Track = namedtuple("Track", [
    "id",
    "title",
    "link",
    "albumId",
    "cover",
    "albumTitle",
    "artistName",
    "position"
])
