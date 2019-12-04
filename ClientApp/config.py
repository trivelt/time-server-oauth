class AppConfig:
    PORT = 9000
    HOST = "127.0.0.1"
    AUTH_CALLBACK = "/auth_callback"
    AUTH_CALLBACK_URL = f"http://{HOST}:{PORT}{AUTH_CALLBACK}"
    CLIENT_ID = "1234"
    CLIENT_SECRET = "qwerty" # in real app it should be e.g. in config file (not pushed into the repo)
