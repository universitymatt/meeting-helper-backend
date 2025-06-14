"""Config taken from .env file"""

import os
from dotenv import load_dotenv

if os.getenv("ENVIRONMENT") != "production":
    load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("JWT_EXPIRATION_SECONDS", "3600"))
