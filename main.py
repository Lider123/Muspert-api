from bottle import Bottle, get, post, request, run


@get("/api/profile")
def get_profile():
    return {  # TODO: return real one
        "id": 1,
        "nickname": "johndoe",
        "first_name": "John",
        "last_name": "Doe"
    }


@post("/api/authorization")
def authorize():
    return {  # TODO: return real token
        "token": "token"
    }


if __name__ == "__main__":
    run(host="0.0.0.0", port=8080, debug=True)
