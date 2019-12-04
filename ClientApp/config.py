class AppConfig:
    PORT = 9000
    HOST = "127.0.0.1"
    AUTH_CALLBACK = "/auth_callback"
    AUTH_CALLBACK_URL = f"http://{HOST}:{PORT}{AUTH_CALLBACK}"
