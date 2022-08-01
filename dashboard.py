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
dashboard_blueprint = Blueprint('dashboard_blueprint', __name__, url_prefix="/dashboard")


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'mysql_db'):
        g.mysql_db = dbObj.connect()
    return g.mysql_db


@dashboard_blueprint.route('/get_petugas', methods=["GET"])
def get_petugas():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    sekarang = datetime.now()
    besok = sekarang + timedelta(hours=24)
    today = sekarang.strftime('%Y-%m-%d')
    tomorrow = besok.strftime('%Y-%m-%d')
    query = "select pp.iduser,pp.lat,pp.lon,pp.address,pp.stamp,u.username from posisi_petugas AS pp " \
            "INNER JOIN user AS u ON pp.iduser = u.iduser " \
            "WHERE pp.stamp < %s AND pp.stamp >= %s"
    cursor.execute(query, (tomorrow, today,))
    record = cursor.fetchall()
    result = dict()
    result['list'] = record
    result['cp'] = cursor.rowcount
    return jsonify(result)


