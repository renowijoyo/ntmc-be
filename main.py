import math
import os
import time
import mobile
import cc
from mrun import MRun
from dbconfig import DBConfig

from flask import Flask, request
from flask_jwt import JWT
from werkzeug.security import safe_str_cmp
import mysql.connector as mysql
import json
from datetime import datetime
import hashlib
import bcrypt

from flask import Flask
from flask import jsonify
from flask import request, flash, request, redirect, url_for
from flask_cors import CORS

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from mobile import mobile_blueprint
from cc import cc_blueprint
from admin import admin_blueprint
from sqlalchemy import create_engine
from werkzeug.utils import secure_filename
from flask import Blueprint


import logging


app = Flask(__name__)
CORS(app)
app.register_blueprint(mobile_blueprint)
app.register_blueprint(cc_blueprint)
app.register_blueprint(admin_blueprint)

logging.basicConfig(filename='record.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')



# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!

jwt = JWTManager(app)


dbObj = DBConfig()
db = dbObj.connect()
def __init__(self):
    self.data = dict()


MRun = MRun()


# engine = create_engine('mysql://root:dhe123!@#@202.67.10.238/ntmc_ccntmc')
# connection = engine.connect()
# metadata = db.MetaData()
# apps_video_banner = db.Table('apps_video_banner', metadata, autoload=True, autoload_with=engine)
# app_link_banner = db.Table('app_linkS_banner', metadata, autoload=True, autoload_with=engine)




@app.route('/test')
def test():
    ret = MRun.get_polda_no_cc()
    return ret










# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


if __name__ == "__main__":
    app.run(ssl_context='adhoc', debug=True)

# if __name__ == "__main__":
#     app.run(ssl_context=('cert.pem', 'key.pem'))
