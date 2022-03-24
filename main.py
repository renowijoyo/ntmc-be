import os

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
from flask import request
from flask_cors import CORS

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from mobile import mobile_blueprint
from cc import cc_blueprint
from sqlalchemy import create_engine

from flask import Blueprint


import logging


app = Flask(__name__)
CORS(app)
app.register_blueprint(mobile_blueprint)
app.register_blueprint(cc_blueprint)

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









@app.route('/datatable', methods=["POST"])
@jwt_required()
def datatable():
    level_user = request.json.get('level_user')
    polda = request.json.get('polda')
    satwil = request.json.get('satwil')
    start = request.json.get('start')
    limit = request.json.get('limit')
    cursor = db.cursor(dictionary=True)
    res = dict()

    if (level_user == 'superadmin'):
        query = "SELECT no_pengaduan,nama_pelapor,work_order.satwil_id, satwil.satwil,sub_kategori_id,subkategori.sub_kategori,tgl_kontak,tgl_close,status,status_detail.keterangan,idworkorder FROM work_order " \
                "LEFT JOIN satwil ON satwil.idsatwil = work_order.satwil_id " \
                "LEFT JOIN status_detail ON status_detail.idstatus = work_order.status " \
                "LEFT JOIN user ON user.iduser = work_order.user_id " \
                "LEFT JOIN subkategori ON subkategori.idsubkategori = work_order.sub_kategori_id LIMIT %s, %s"
        cursor.execute(query, (start, limit,))
        record = cursor.fetchall()
        res = record
    elif (level_user == 'spv'):
        query = "SELECT no_pengaduan,nama_pelapor,work_order.satwil_id,satwil.satwil,sub_kategori_id,subkategori.sub_kategori,tgl_kontak,tgl_close,status,status_detail.keterangan,idworkorder FROM work_order " \
                "LEFT JOIN satwil ON satwil.idsatwil = work_order.satwil_id " \
                "LEFT JOIN status_detail ON status_detail.idstatus = work_order.status " \
                "LEFT JOIN polda ON polda.idpolda = satwil.polda_id " \
                "LEFT JOIN user ON user.iduser = work_order.user_id " \
                "LEFT JOIN subkategori ON subkategori.idsubkategori = work_order.sub_kategori_id " \
                "WHERE polda.idpolda = %s LIMIT %s, %s "
        cursor.execute(query, (polda, start, limit, ))
        record = cursor.fetchall()
        res = record
    else:
        query = "SELECT no_pengaduan,nama_pelapor,work_order.satwil_id,satwil.satwil,sub_kategori_id,subkategori.sub_kategori,tgl_kontak,tgl_close,status,status_detail.keterangan,idworkorder FROM work_order " \
                "LEFT JOIN satwil ON satwil.idsatwil = work_order.satwil_id " \
                "LEFT JOIN status_detail ON status_detail.idstatus = work_order.status " \
                "LEFT JOIN user ON user.iduser = work_order.user_id " \
                "LEFT JOIN subkategori ON subkategori.idsubkategori = work_order.sub_kategori_id " \
                "WHERE work_order.satwil_id = %s LIMIT %s, %s "
        cursor.execute(query, (satwil, start, limit, ))
        record = cursor.fetchall()
        res = record
    cursor.close()
    return jsonify(res)




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
