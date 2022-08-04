from flask import Blueprint, g
import json
from ntmcdbconfig import DBConfig
from flask import Flask, request
from flask_jwt import JWT
# from werkzeug.security import safe_str_cmp
import mysql.connector as mysql
import json
from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS

from datetime import datetime, timedelta
import hashlib
import bcrypt

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

import bcrypt

dbObj = DBConfig()
db = dbObj.connect()
now = datetime.now()
login_blueprint = Blueprint('login_blueprint', __name__, url_prefix="/login")


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'mysql_db'):
        g.mysql_db = dbObj.connect()
    return g.mysql_db


@login_blueprint.route('/check_login', methods=["POST"])
def check_login():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    result = dict()
    username = request.form['username']
    password = request.form['password']
    query = "SELECT iduser,username,password,level_user,satwil_id,satwil,polda,polda.idpolda as polda_id, user_license.status AS 'status_license' FROM user " \
            "LEFT JOIN satwil ON satwil.idsatwil = user.satwil_id LEFT JOIN polda ON polda.idpolda = user.polda_id LEFT JOIN user_license ON " \
            "user.iduser = user_license.user_id WHERE username = %s"
    cursor.execute(query, (username,))
    records = cursor.fetchall()
    records[0]['login_success'] = 'true'
    result = records
    return jsonify(result)
