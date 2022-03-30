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

cc_blueprint = Blueprint('cc_blueprint', __name__, url_prefix="/cc")


@cc_blueprint.route('/login_user', methods=["POST"])
def login_user():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    res = authenticate_user(username, password)
    return res

def authenticate_user(username, password):
    cursor = db.cursor(dictionary=True)
    query = "SELECT iduser,username,password, level_user, position_id, position.position_name as 'position_name', department.id as 'department_id', department.department_name as 'department_name', " \
            "region.id as 'region_id', region.region_name as 'region_name' FROM user " \
            "LEFT JOIN position ON position.id = user.position_id " \
            "LEFT JOIN department ON department.id = position.department_id "\
            "LEFT JOIN region ON region.id = department.region_id "\
            "WHERE username = %s"
    cursor.execute(query, (username,))
    record = cursor.fetchall()
    cursor.close()
    level_user = ''
    position_id = ''
    position_name = ''
    region_id = ''
    region_name = ''
    department_id = ''
    department_name = ''

    valid = 0
    res = dict()
    if (len(record) > 0):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)

        if bcrypt.checkpw(password.encode(), (record[0]['password']).encode()):
            valid = 1
            token = username
            access_token = create_access_token(identity=record[0]['iduser'])
            name = record[0]['username']
            level_user = record[0]['level_user']
            position_id = record[0]['position_id']
            position_name = record[0]['position_name']
            department_id = record[0]['department_id']
            department_name = record[0]['department_name']
            region_id = record[0]['region_id']
            region_name = record[0]['region_name']
            print(record[0])
            res['valid'] = valid
            res['response'] = 'success'
            res['username'] = name
            res['level_user'] = level_user
            res['position_id'] = position_id
            res['position_name'] = position_name
            res['department_id'] = department_id
            res['department_name'] = department_name
            res['region_id'] = region_id
            res['region_name'] = region_name
            res['token'] = token

            return jsonify(token=access_token, name=name, level_user=level_user, position_id=position_id, position_name=position_name,
                           department_id=department_id, department_name=department_name, region_id=region_id,region_name=region_name, valid=valid)
        else:
            valid = 2
            res['valid'] = valid
            res['response'] = 'password does not match'
    else:
        valid = 2
        res['valid'] = valid
        res['response'] = 'username does not exist'



    return res

@cc_blueprint.route('/simpan_user', methods=["POST"])
def simpan_user():
    username = request.json.get('username')
    password = request.json.get('password')
    level_user = request.json.get('level_user')
    position_id = request.json.get('position_id')

    cursor = db.cursor(dictionary=True)
    query = "SELECT username,password FROM user WHERE username = %s"
    cursor.execute(query, (username,))
    record = cursor.fetchall()
    valid = 0

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)

    if (len(record) > 0):
        valid = 2
    else:
        valid = 1
        query = "INSERT INTO user (username, password, level_user, position_id " \
                ") " \
                "VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (username, hashed, level_user, position_id,))
        db.commit()
    res = dict()
    res['valid'] = valid
    cursor.close()
    return res

# @cc_blueprint.route('/laporan_image_upload', methods=["POST"])
# @jwt_required()
# def laporan_image_upload():
#     # response = requests.post(URL, data=img, headers=headers)



@cc_blueprint.route('/laporan_add', methods=["POST"])
@jwt_required()
def laporan_add():
    cursor = db.cursor(dictionary=True)
    user_id = get_jwt_identity()
    # user_id = '1'
    no_laporan = request.json.get('no_laporan')
    lat_pelapor = request.json.get('lat_pelapor')
    long_pelapor = request.json.get('long_pelapor')
    laporan_text = request.json.get('laporan_text')
    sub_kategori_id = request.json.get('sub_kategori_id')
    status = request.json.get('status')
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    # tgl_approved = request.json.get('tgl_approved')


    query = "INSERT INTO laporan (no_laporan, user_id, lat_pelapor, long_pelapor, sub_kategori_id, laporan_text, status, tgl_submitted) " \
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (no_laporan, user_id, lat_pelapor, long_pelapor, sub_kategori_id, laporan_text, status, formatted_date))
    record = cursor.fetchone()

    result = dict()
    try:
        db.commit()
    except mysql.connector.Error as error:
        print("Failed to update record to database rollback: {}".format(error))
        # reverting changes because of exception
        cursor.rollback()
        result['result'] = 'failed'
    finally:
        cursor.close()
        print("connection is closed")
        result['result'] = 'sucess'

    return jsonify(result)





@cc_blueprint.route('/laporan', methods=["POST"])
# @jwt_required()
def laporan():
    level_user = request.json.get('level_user')
    position_id = request.json.get('position_id')
    start = request.json.get('start')
    limit = request.json.get('limit')
    cursor = db.cursor(dictionary=True)
    res = dict()

    if (level_user == 'superadmin'):
        print("superadmin")
        query = "SELECT no_laporan,user_id, user_data.nama, user.position_id, position.position_name,sub_kategori_id,subkategori.sub_kategori, " \
                "tgl_submitted,tgl_approved,status,status_detail.keterangan,laporan.id FROM laporan " \
                "LEFT JOIN status_detail ON status_detail.idstatus = laporan.status " \
                "LEFT JOIN user ON user.iduser = laporan.user_id " \
                "LEFT JOIN user_data ON user_data.iduser = laporan.user_id " \
                "LEFT JOIN position ON position.id = user.position_id " \
                "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan.sub_kategori_id LIMIT %s, %s"
        cursor.execute(query, (start, limit,))
        record = cursor.fetchall()
        res = record
        print(res)
    # elif (level_user == 'spv'):
    #     query = "SELECT no_pengaduan,nama_pelapor,work_order.position_id,position.position_name,sub_kategori_id,subkategori.sub_kategori,tgl_kontak,tgl_close,status,status_detail.keterangan,idworkorder FROM work_order " \
    #             "LEFT JOIN position ON position.id = work_order.position_id " \
    #             "LEFT JOIN status_detail ON status_detail.idstatus = work_order.status " \
    #             "LEFT JOIN department ON department.id = position.department_id " \
    #             "LEFT JOIN region ON region.id = department.region_id " \
    #             "LEFT JOIN user ON user.iduser = work_order.user_id " \
    #             "LEFT JOIN subkategori ON subkategori.idsubkategori = work_order.sub_kategori_id " \
    #             "WHERE region.id = %s LIMIT %s, %s "
    #     cursor.execute(query, (region, start, limit, ))
    #     record = cursor.fetchall()
    #     res = record
    else:
        query = "SELECT no_laporan,user_id,user.position_id, position.position_name,sub_kategori_id,subkategori.sub_kategori, " \
                "tgl_submitted,tgl_approved,status,status_detail.keterangan,laporan.id FROM laporan " \
                "LEFT JOIN status_detail ON status_detail.idstatus = laporan.status " \
                "LEFT JOIN user ON user.iduser = laporan.user_id " \
                "LEFT JOIN position ON position.id = user.position_id " \
                "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan.sub_kategori_id " \
                "WHERE laporan.position_id = %s LIMIT %s, %s "
        cursor.execute(query, (position_id, start, limit, ))
        record = cursor.fetchall()
        res = record
    cursor.close()
    return jsonify(res)

@cc_blueprint.route('/users', methods=["POST"])
@jwt_required()
def users():
    cursor = db.cursor(dictionary=True)
    query = "SELECT iduser, username, level_user FROM user"
    cursor.execute(query)
    record = cursor.fetchall()
    valid = 0

    res = dict()
    res = record
    cursor.close()
    return jsonify(res)


@cc_blueprint.route('/user_setpass', methods=["POST"])
def user_setpass():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    ol_password = request.json.get('ol_password')

    cursor = db.cursor(dictionary=True)
    query = "SELECT iduser, username, password FROM user WHERE username = %s"
    cursor.execute(query, (username,))
    record = cursor.fetchall()
    valid = 0
    if (len(record) > 0):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)

        if bcrypt.checkpw(ol_password.encode(), (record[0]['password']).encode()):
            valid = 1

            query = "UPDATE user SET password =  %s WHERE username = %s"
            cursor.execute(query, (hashed, username,))
            db.commit()
        else:
            valid = 0

    else:
        valid = 0

    res = dict()
    res['valid'] = valid
    cursor.close()
    return res







