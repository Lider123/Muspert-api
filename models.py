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
    "createdAt"
])

Genre = namedtuple("Genre", [
    "id",
    "title",
    "image"
])
