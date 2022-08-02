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


@dashboard_blueprint.route('/get_petugas', methods=["POST"])
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


@dashboard_blueprint.route('/get_work_order', methods=["POST"])
def get_work_order():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM work_order WHERE status = '1'"
    cursor.execute(query)
    record = cursor.fetchall()
    tahun = now.strftime('%Y')
    month = now.strftime('%m')
    query2 = "SELECT wo.sub_kategori_id, sk.sub_kategori, sk.icon, wo.idworkorder, wo.lat_pelapor, wo.long_pelapor," \
            "wo.alamat_pelapor FROM work_order AS wo INNER JOIN subkategori AS sk ON wo.sub_kategori_id = sk.idsubkategori " \
            "WHERE MONTH(`tgl_kontak`) = %s AND YEAR(`tgl_kontak`) = %s AND `lat_pelapor` != ''"

    cursor.execute(query2,(month, tahun,))
    record2 = cursor.fetchall()
    result = dict()
    result['open'] = record
    result['list'] = record2
    return jsonify(result)


