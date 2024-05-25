import os

import dotenv

dotenv.load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
DATABASE_NAME = os.environ.get("DATABASE_NAME")
SECRET = os.environ.get("SECRET")
SUPER_USER_TOKEN = os.environ.get("SUPER_USER_TOKEN")
