from flask import Blueprint
import json
from dbconfig import DBConfig
from flask import Flask, request
from flask_jwt import JWT
from werkzeug.security import safe_str_cmp
import mysql.connector as mysql
import json
from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS

from datetime import datetime
import hashlib
import bcrypt

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from datetime import datetime
now = datetime.now()

import bcrypt

dbObj = DBConfig()
db = dbObj.connect()

admin_blueprint = Blueprint('admin_blueprint', __name__, url_prefix="/admin")

@admin_blueprint.route('/update_user', methods=["POST"])
@jwt_required()
def update_user():
    print("admin/updateuser")
    username = request.json.get('username')
    # password = request.json.get('password')
    level_user = request.json.get('level_user')
    position_id = request.json.get('position_id')
    order_license = request.json.get('order_license')
    nama = request.json.get('nama')
    telepon = request.json.get('telepon')
    alamat = request.json.get('alamat')
    email = request.json.get('email')
    ktp = request.json.get('ktp')
    cursor = db.cursor(dictionary=True)
    query = "SELECT iduser,username, password FROM user WHERE username = %s"
    cursor.execute(query, (username,))
    record = cursor.fetchall()
    valid = 0

    # salt = bcrypt.gensalt()
    # hashed = bcrypt.hashpw(password.encode(), salt)

    res = dict()
    if (len(record) > 0):
        valid = 1
        hashed = record[0]['password']

        query = "REPLACE INTO user (iduser, username, password, level_user, order_license, position_id " \
                ") " \
                "VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (record[0]['iduser'], username, hashed, level_user, order_license, position_id,))
        print("4")
        query = "REPLACE INTO user_data (iduser, nama, telepon, alamat, email, ktp " \
                ") " \
                "VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (cursor.lastrowid, nama, telepon, alamat, email, ktp,))
        db.commit()
        res['username'] = username
        res['level_user'] = level_user
        res['position_id'] = position_id
        res['alamat'] = alamat
        res['nama'] = nama
        res['ktp'] = ktp
        res['telepon'] = telepon
        res['email'] = email
    else:
        valid = 2
        res['errorMessage'] = "username does not exist - create first"



    res['valid'] = valid
    cursor.close()
    return res