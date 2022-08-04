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

@login_blueprint.route('/password_update', methods=["POST"])
def password_update():
    username = request.form['username']
    password = request.form['password']
    # ol_password = request.json.get('ol_password')

    cursor = db.cursor(dictionary=True)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)

    query = "UPDATE user SET password =  %s WHERE username= %s"
    cursor.execute(query, (hashed,username,))
    db.commit()

    res = dict()
    res['rowcount'] = cursor.rowcount
    cursor.close()
    return res



@login_blueprint.route('/check_login', methods=["POST"])
def check_login():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    result = dict()
    username = request.form['username']
    password = request.form['password']
    valid = 0
    query = "SELECT iduser,username,password,level_user,satwil_id,satwil,polda,polda.idpolda as polda_id, user_license.status AS 'status_license' FROM user " \
            "LEFT JOIN satwil ON satwil.idsatwil = user.satwil_id LEFT JOIN polda ON polda.idpolda = user.polda_id LEFT JOIN user_license ON " \
            "user.iduser = user_license.user_id WHERE username = %s"
    cursor.execute(query, (username,))
    records = cursor.fetchall()
    if (len(records) > 0):
        # salt = bcrypt.gensalt()
        # hashed = bcrypt.hashpw(password.encode(), salt)
        try:
            if bcrypt.checkpw(password.encode(), (records[0]['password']).encode()):
                valid = 1
            else:
                valid = 0
        except:
            valid = 0
        records[0]['login_success'] = valid
    else:
        valid = 0


    result = records
    return jsonify(result)
