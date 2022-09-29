from flask import Flask
from dotenv import load_dotenv
import os
load_dotenv()


app = Flask(__name__)
app.config["DB_USER"] = os.environ.get("DB_USER")
app.config["DB_PASSWORD"] = os.environ.get("DB_PASSWORD")
app.config["DB_HOST"] = os.environ.get("DB_HOST")


from api import routes
