import os


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'tma.db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/")

    broker_url = os.getenv("REDIS_URL", "redis://localhost:6379/")
    result_backend = os.getenv("REDIS_URL", "redis://localhost:6379/")

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "")

    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@tma.com")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")

    SECRET_KEY = os.getenv("SECRET_KEY", "")
