"""Web server."""

import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
# from flask_bcrypt import Bcrypt
# from flask_jwt_extended import JWTManager
from routes import routes_api
# from routes import *

app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv("APP_SECRET_KEY")
app.config["CORS_HEADERS"] = "Content-Type"

corsOriginsStr = os.getenv("ALLOWED_ORIGINS", "*")
corsOrigin = []
if corsOriginsStr == "*":
    corsOrigin.append("*")
else:
    for aOrigin in corsOriginsStr.split(","):
        corsOrigin.append(aOrigin.rstrip().lstrip())
CORS(app, origins=corsOrigin, supports_credentials=True)

# bcrypt = Bcrypt(app)
# jwt = JWTManager(app)

app.register_blueprint(routes_api, url_prefix="/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT", 5000), debug=True)
