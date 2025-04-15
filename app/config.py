class Config:
    SECRET_KEY = "super-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///flask_security_api.db"
    SECURITY_PASSWORD_SALT = "another-super-secret"
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    JWT_SECRET_KEY = "jwt-super-secret"
