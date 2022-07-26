import random

from flask import Blueprint, g
import time
from datetime import date
import os
import json

from stats import Stats
from dbconfig import DBConfig
from dbconfig2 import DBConfig2
from flask import Flask, request
from flask_jwt import JWT
# from werkzeug.security import safe_str_cmp
import mysql.connector as mysql
import json
from flask import Flask
from flask import jsonify
from flask import request, flash, request, redirect, url_for
from flask_cors import CORS

from werkzeug.utils import secure_filename
from os.path import exists
from datetime import datetime
import hashlib
import bcrypt

import pdfkit


from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from datetime import datetime
now = datetime.now()
from flask import send_from_directory

import bcrypt

dbObj = DBConfig()
dbObj2 = DBConfig2()

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'mysql_db'):
        g.mysql_db = dbObj.connect()
    return g.mysql_db

def get_db2():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'mysql_db2'):
        g.mysql_db2 = dbObj2.connect()
    return g.mysql_db2


UPLOAD_FOLDER = './uploads/'
UPLOAD_USERPHOTO_FOLDER = './uploads/userphoto/'
UPLOAD_GIATHARIAN_FOLDER = './uploads/giatharian/'
UPLOAD_GIATINSIDENTIL_FOLDER = './uploads/giatinsidentil/'
UPLOAD_KOMANDAN_FOLDER = './uploads/komandan/'
UPLOAD_WAKIL_FOLDER = './uploads/wakil/'
UPLOAD_REGION_FOLDER = './uploads/region/'
UPLOAD_DEPARTMENT_FOLDER = './uploads/department/'

DOWNLOAD_FOLDER = './downloads/'
DOWNLOAD_LAPORAN_FOLDER = './downloads/laporan/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
cc_blueprint = Blueprint('cc_blueprint', __name__, url_prefix="/cc")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_LAPORAN_FOLDER'] = DOWNLOAD_LAPORAN_FOLDER
app.config['UPLOAD_USERPHOTO_FOLDER'] = UPLOAD_USERPHOTO_FOLDER
app.config['UPLOAD_GIATHARIAN_FOLDER'] = UPLOAD_GIATHARIAN_FOLDER
app.config['UPLOAD_GIATINSIDENTIL_FOLDER'] = UPLOAD_GIATINSIDENTIL_FOLDER

app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['UPLOAD_REGION_FOLDER'] = UPLOAD_REGION_FOLDER
app.config['UPLOAD_DEPARTMENT_FOLDER'] = UPLOAD_DEPARTMENT_FOLDER









# /?id=D59B0CA08F49&lat=-6.2410&lon=106.8189&hdop=73&altitude=47&speed=0.0

@cc_blueprint.route('/tracker', methods=["GET"])
def tracker():
    id = request.args.get("id", None)
    lat = request.args.get("lat", None)
    lon = request.args.get("lon", None)
    hdop = request.args.get("hdop", None)
    altitude = request.args.get("altitude", None)
    speed = request.args.get("speed", None)

    db2 = get_db2()
    cursor = db2.cursor(dictionary=True)

    query = "INSERT INTO tracker_loc (tracker_device_id, lat, lon, hdop, altitude,speed) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (id, lat, lon, hdop, altitude, speed))

    # print("here")
    result = dict()
    try:
        db2.commit()
    except mysql.connector.Error as error:
        print("Failed to update record to database rollback: {}".format(error))
        # reverting changes because of exception
        cursor.rollback()
        result['result'] = 'failed'
        result['valid'] = 2
    finally:

        cursor.close()
        result['result'] = 'success'
        result['valid'] = 1

    cursor.close()
    return result


@cc_blueprint.route('/get_tracker_devices', methods=["GET"])
def get_tracker_devices():
    db2 = get_db2()
    cursor = db2.cursor(dictionary=True)

    query = "select a.loc_id, a.tracker_device_id, a.lat, a.lon, a.altitude, a.speed, a.hdop, tracker_device.device_name, tracker_device.device_type, tracker_device.`status` from " \
            "(select tracker_loc.id as 'loc_id', tracker_loc.tracker_device_id, tracker_loc.lat, tracker_loc.lon, tracker_loc.altitude, tracker_loc.speed, tracker_loc.hdop " \
            "from tracker_loc where id in (select max(tracker_loc.id) as id from tracker_loc group by tracker_loc.tracker_device_id)) a " \
            "LEFT JOIN tracker_device on a.tracker_device_id = tracker_device.device_id"
    # query = "SELECT device_id, device_name, device_type, tracker_loc.id, tracker_loc.lat, tracker_loc.lon, tracker_loc.altitude, tracker_loc.hdop, tracker_loc.speed, status, tracker_video.video_url FROM tracker_device LEFT JOIN " \
    #         "tracker_video on tracker_video.tracker_device_id = tracker_device.device_id LEFT JOIN tracker_loc on tracker_loc.tracker_device_id = tracker_device.device_id ORDER BY tracker_loc.id DESC"
    cursor.execute(query)
    record = cursor.fetchall()
    result = dict()
    result = record
    dummylon = float(result[0]['lon']) + float(random.random() * 30)
    print(dummylon)
    result[0]['lon'] = dummylon
    return jsonify(result)


@cc_blueprint.route('/get_tracker_device', methods=["POST"])
def get_tracker_device():

    tracker_device_id = request.json.get("tracker_device_id", None)
    db2 = get_db2()
    cursor = db2.cursor(dictionary=True)
    query = "SELECT device_id, device_name, device_type, status, tracker_video.video_url FROM tracker_device LEFT JOIN " \
            "tracker_video on tracker_video.tracker_device_id = tracker_device.device_id WHERE device_id = %s"
    cursor.execute(query, (tracker_device_id,))
    record = cursor.fetchone()
    return record



@cc_blueprint.route('/get_tracker_loc', methods=["POST"])
def get_tracker_loc():
    tracker_device_id = request.json.get("tracker_device_id", None)
    db2 = get_db2()
    cursor = db2.cursor(dictionary=True)
    query = "SELECT id, tracker_device_id, lat, lon, altitude, hdop, speed FROM tracker_loc WHERE tracker_device_id = %s ORDER BY id DESC"
    cursor.execute(query, (tracker_device_id,))
    record = cursor.fetchone()
    return record


@cc_blueprint.route('/login_user', methods=["POST"])
def login_user():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    res = authenticate_user(username, password)
    return res

def authenticate_user(username, password):
    db = get_db()
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
            iduser = record[0]['iduser']
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
            res['iduser'] = iduser
            res['username'] = name
            res['level_user'] = level_user
            res['position_id'] = position_id
            res['position_name'] = position_name
            res['department_id'] = department_id
            res['department_name'] = department_name
            res['region_id'] = region_id
            res['region_name'] = region_name
            res['token'] = token

            return jsonify(token=access_token, iduser=iduser, name=name, level_user=level_user, position_id=position_id, position_name=position_name,
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
    nama = request.json.get('nama')
    telepon = request.json.get('telepon')
    alamat = request.json.get('alamat')
    email = request.json.get('email')
    ktp = request.json.get('ktp')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = "SELECT username,password FROM user WHERE username = %s"
    cursor.execute(query, (username,))
    record = cursor.fetchall()
    valid = 0

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    res = dict()
    if (len(record) > 0):
        valid = 2
        res['errorMessage'] = "username existed"
    else:
        valid = 1
        query = "INSERT INTO user (username, password, level_user, position_id " \
                ") " \
                "VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (username, hashed, level_user, position_id,))

        query = "INSERT INTO user_data (iduser, nama, telepon, alamat, email, ktp " \
                ") " \
                "VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (cursor.lastrowid, nama, telepon, alamat, email, ktp,))

        db.commit()

    res['valid'] = valid
    cursor.close()
    return res

@cc_blueprint.route('/get_user_info', methods=["POST"])
@jwt_required()
def get_user_info():
    db = get_db()
    user_id = get_jwt_identity()
    # user_id = "2680"
    cursor = db.cursor(dictionary=True)
    result = dict()
    print(user_id)
    query = "select iduser, username, user.position_id, position.position_name, position.department_id, department.id as 'department_id', department.department_name, region.id as 'region_id', region.region_name from user " \
            "LEFT JOIN position ON position.id = user.position_id " \
            "LEFT JOIN department ON department.id = position.department_id " \
            "LEFT JOIN region ON region.id = department.region_id " \
            "where iduser = %s"
    cursor.execute(query, (user_id,))
    record = cursor.fetchone()
    # print(record)
    # result = record
    return record


# @cc_blueprint.route('/laporan_image_upload', methods=["POST"])
# @jwt_required()
# def laporan_image_upload():
#     # response = requests.post(URL, data=img, headers=headers)

# @cc_blueprint.route('/get_laporan_no[DEPRECATED]', methods=["POST"])
# @jwt_required()
# def get_laporan_no():
#     #format laporan 2022/bulan/region(kesatuanid)/subkategori
#     db.reconnect()
#     user_id = get_jwt_identity()
#
#     cursor = db.cursor(dictionary=True)
#     result = dict()
#     sub_kategori_id = request.json.get('sub_kategori_id')
#     # print(user_id)
#     user_info = get_user_info()
#     # print(user_info['username'])
#     if user_info['region_id'] is None:
#         result['valid'] = 0
#         result['status'] = 'no region set for this user'
#         return jsonify(result)
#     # query_0 = "select iduser, username, position_id from USER where iduser = %s"
#     # cursor.execute(query_0, (user_id,))
#     # record = cursor.fetchone()
#
#
#     query_a = "SELECT idsubkategori, kategori_id, kategori.kategori, sub_kategori FROM subkategori " \
#               "LEFT JOIN kategori ON kategori.idkategori = subkategori.kategori_id " \
#               "WHERE idsubkategori = %s"
#     cursor.execute(query_a, (sub_kategori_id,))
#     record = cursor.fetchone()
#     if record is None:
#         result['valid'] = 0
#         result['status'] = 'wrong sub_kategori_id'
#         return jsonify(result)
#
#     print(record)
#     if(record['kategori_id'] == 1) :
#         print("ini yg pertama")
#         no_laporan_string = str(date.today().year) + "-" + str(date.today().month) + "-" + str(date.today().strftime("%d")) + "-" + str(sub_kategori_id) + "-" + str(user_info['region_id'])
#     elif (record['kategori_id'] == 2) :
#         print("ini yg kedua")
#         no_laporan_string = str(date.today().year) + "-" + str(date.today().month) + "-" + str(sub_kategori_id) + "-" + str(user_info['region_id'])
#     else :
#         print(record['kategori_id'])
#         no_laporan_string = str(date.today().year) + "-" + str(sub_kategori_id) + "-" + str(user_info['region_id'])
#     print(no_laporan_string)
#
#
#     query = "SELECT id, no_laporan, approved_by, date_submitted, date_approved, status FROM laporan_published WHERE no_laporan = %s"
#     cursor.execute(query, (no_laporan_string,))
#     record = cursor.fetchall()
#
#     if (len(record) > 0):
#         if record[0]['status'] == 'approved' :
#             valid = 2
#             result['no_laporan'] = ''
#             result['status'] = "laporan approved"
#         else :
#             valid = 1
#             result['status'] = 'laporan submitted'
#             result['no_laporan'] = no_laporan_string
#     else:
#         formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
#         query = "INSERT INTO laporan_published (no_laporan, laporan_subcategory_id, date_submitted, status " \
#                 ") " \
#                 "VALUES (%s, %s, %s, %s)"
#         cursor.execute(query, (no_laporan_string,sub_kategori_id, formatted_date, "submitted",))
#         db.commit()
#         valid = 1
#         result['status'] = 'new laporan submitted'
#         result['no_laporan'] = no_laporan_string
#     result['valid'] = valid
#
#     cursor.close()
#     return jsonify(result)



@cc_blueprint.route('/laporan_approve', methods=["POST"])
@jwt_required()
def laporan_approve():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    user_id = get_jwt_identity()
    no_laporan = request.json.get('no_laporan')
    approved = "approved"
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    query = "UPDATE laporan_published SET status =  %s, date_approved = %s, approved_by = %s WHERE no_laporan = %s"
    cursor.execute(query, (approved, formatted_date, user_id, no_laporan,))
    result = dict()
    try:
        db.commit()
    except mysql.connector.Error as error:
        print("Failed to update record to database rollback: {}".format(error))
        # reverting changes because of exception
        cursor.rollback()
        result['result'] = 'failed'
        result['valid'] = 2
    finally:

        cursor.close()
        result['result'] = 'success'
        result['valid'] = 1

    return jsonify(result)

@cc_blueprint.route('/laporan_published', methods=["GET"])
def laporan_published():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = "SELECT no_laporan, laporan_subcategory_id, approved_by, user.username, date_submitted, date_approved, status FROM laporan_published " \
            "LEFT JOIN user ON user.iduser = laporan_published.approved_by "
    cursor.execute(query)
    record = cursor.fetchall()
    result = dict()
    result = record
    return jsonify(result)

@cc_blueprint.route('/get_laporan_pdf', methods=["POST"])
# @jwt_required()
def get_laporan_pdf():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    # user_id = get_jwt_identity()
    no_laporan = request.json.get('no_laporan')
    sub_kategori_id = request.json.get('sub_kategori_id')
    query = "SELECT id, no_laporan, approved_by date_submitted, date_approved, status FROM laporan_published "
    cursor.execute(query)
    record = cursor.fetchone()

    result = dict()
    if (record['status'] != "approved") :
        print('jere 2')
        result['result'] = 'not yet approved'
        result['download_url'] = None
        result['valid'] = 0
    else :
        result['result'] = 'success'
        result['download_url'] = 'http://202.sekian sekian sekian'
        result['valid'] = 1

    print(result)
    return jsonify(result)


#
#
#
#
# @cc_blueprint.route('/laporan_add_DEPRECATED', methods=["POST"])
# @jwt_required()
# def laporan_add():
#     db.reconnect()
#     cursor = db.cursor(dictionary=True)
#     user_id = get_jwt_identity()
#     # user_id = '1'
#     no_laporan = request.json.get('no_laporan')
#     tgl_laporan = request.json.get('tgl_laporan')
#     lat_pelapor = request.json.get('lat_pelapor')
#     long_pelapor = request.json.get('long_pelapor')
#     laporan_text = request.json.get('laporan_text')
#     laporan_total = request.json.get('laporan_total')
#     sub_kategori_id = request.json.get('sub_kategori_id')
#     laporan_subcategory_id = request.json.get('laporan_subcategory_id')
#     status = request.json.get('status')
#     formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
#     # tgl_approved = request.json.get('tgl_approved')
#
#     query = "INSERT INTO laporan (no_laporan, tgl_laporan, user_id, lat_pelapor, long_pelapor, sub_kategori_id, " \
#             "laporan_subcategory_id, laporan_text, laporan_total, status, tgl_submitted) " \
#             "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
#     cursor.execute(query, (no_laporan, tgl_laporan, user_id, lat_pelapor, long_pelapor, sub_kategori_id,laporan_subcategory_id, laporan_text, laporan_total, status, formatted_date))
#     record = cursor.fetchone()
#
#     result = dict()
#     try:
#         db.commit()
#     except mysql.connector.Error as error:
#         print("Failed to update record to database rollback: {}".format(error))
#         # reverting changes because of exception
#         cursor.rollback()
#         result['result'] = 'failed'
#         result['valid'] = 2
#     finally:
#
#         cursor.close()
#         result['result'] = 'success'
#         result['valid'] = 1
#
#     return jsonify(result)
#

@cc_blueprint.route('/position_list', methods=["get"])
def position_list():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = "SELECT position.id as 'position_id', position.position_name, department.id as 'department_id', department.department_name,  region.id as 'region_id', region.region_name from position " \
            "LEFT JOIN department ON department.id = position.department_id " \
            "LEFT JOIN region ON region.id = department.region_id "
    cursor.execute(query,)
    record = cursor.fetchall()
    cursor.close()
    res = dict()
    res = record
    return jsonify(res)




@cc_blueprint.route('/laporan', methods=["POST"])
@jwt_required()
def laporan():
    db = get_db()
    level_user = request.json.get('level_user')
    position_id = request.json.get('position_id')
    start = request.json.get('start')
    limit = request.json.get('limit')
    cursor = db.cursor(dictionary=True)
    res = dict()

    if (level_user == 'superadmin'):
        print("superadmin")
        query = "SELECT no_laporan, user_id, user_data.nama, user.position_id, position.position_name,sub_kategori_id,subkategori.sub_kategori, laporan.laporan_subcategory_id, laporan_subcategory.name, laporan_subcategory.description, " \
                "kesatuan_region_id, tgl_submitted,tgl_approved,laporan.status,status_detail.keterangan,laporan.id, laporan.laporan_total, " \
                "laporan.laporan_text, laporan.lat_pelapor, laporan.long_pelapor FROM laporan " \
                "LEFT JOIN status_detail ON status_detail.idstatus = laporan.status " \
                "LEFT JOIN user ON user.iduser = laporan.user_id " \
                "LEFT JOIN user_data ON user_data.iduser = laporan.user_id " \
                "LEFT JOIN laporan_subcategory ON laporan_subcategory.id = laporan.laporan_subcategory_id " \
                "LEFT JOIN position ON position.id = user.position_id " \
                "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan.sub_kategori_id LIMIT %s, %s"
        cursor.execute(query, (start, limit,))
        record = cursor.fetchall()
        res = record
        print(res)

    else:
        query = "SELECT no_laporan, tgl_laporan, user_id, user_data.nama, user.position_id, position.position_name,sub_kategori_id,subkategori.sub_kategori, laporan.laporan_subcategory_id, laporan_subcategory.name, laporan_subcategory.description, " \
                "kesatuan_region_id, tgl_submitted,tgl_approved,laporan.status,status_detail.keterangan,laporan.id, laporan.laporan_total,laporan.laporan_text, laporan.lat_pelapor, laporan.long_pelapor FROM laporan " \
                "LEFT JOIN status_detail ON status_detail.idstatus = laporan.status " \
                "LEFT JOIN user ON user.iduser = laporan.user_id " \
                "LEFT JOIN user_data ON user_data.iduser = laporan.user_id " \
                "LEFT JOIN laporan_subcategory ON laporan_subcategory.id = laporan.laporan_subcategory_id " \
                "LEFT JOIN position ON position.id = user.position_id " \
                "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan.sub_kategori_id " \
                "WHERE laporan.position_id = %s LIMIT %s, %s "
        cursor.execute(query, (position_id, start, limit, ))
        record = cursor.fetchall()
        res = record
    cursor.close()
    return jsonify(res)

@cc_blueprint.route('/ebooks', methods=["GET"])
def ebooks():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = "SELECT idebook, filename, tanggal FROM ebook"

    cursor.execute(query)
    record = cursor.fetchall()
    valid = 0
    res = dict()
    res = record
    cursor.close()
    return jsonify(res)


@cc_blueprint.route('/laporan_subcategory', methods=["POST"])
# @jwt_required()
def laporan_subcategory():
    print("laporan subcat")
    group = request.json.get("group", None)
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = "SELECT id, name, description, laporan_subcategory.group FROM laporan_subcategory where laporan_subcategory.group = %s"

    cursor.execute(query,(group,))
    record = cursor.fetchall()
    valid = 0
    res = dict()
    res = record
    cursor.close()
    return jsonify(res)




@cc_blueprint.route('/users', methods=["POST"])
# @jwt_required()
def users():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = "SELECT user.iduser, username, level_user, order_license, position_id, user_data.nama, user_data.telepon, " \
            "user_data.alamat, user_data.email, user_data.ktp FROM user LEFT JOIN user_data ON user_data.iduser = user.iduser "

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
    db = get_db()
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

@cc_blueprint.route('/laporan_map', methods=["POST"])
def laporan_map():
    level_user = request.json.get('level_user')
    start = request.json.get('start')
    regions = request.json.get('regions')
    subkategoris = request.json.get('subkategoris')
    # for region in regions:
    db = get_db()
    cursor = db.cursor(dictionary=True)
    print(regions)
    # print(str(regions)[1:-1])/
    region = str(regions)[1:-1]

    subkategori = str(subkategoris)[1:-1]
    tuple_regions = tuple(regions)
    s = tuple(subkategoris)
    regs = ""
    if (len(s) == 1) :
        regs = "(" + str(s[0]) + ")"
        print(regs)
    else :
        regs = s

    # query = "SELECT data_laporan.user_id, data_laporan.lat_pelapor, data_laporan.long_pelapor, " \
    #         "region.id as 'region_id', region.region_name, department.id as 'department_id', department.department_name, user.position_id as 'position_id', position.position_name, " \
    #         "data_laporan.data_laporan_subcategory_id as 'sub_kategori_id',subkategori.sub_kategori, " \
    #         "data_laporan.tgl_laporan, data_laporan.tgl_submitted ,data_laporan.tgl_approved,data_laporan.status as 'status', status_detail.keterangan as 'status_keterangan', " \
    #         "data_laporan.id as 'laporan_id', data_laporan.laporan_text " \
    #         "FROM data_laporan " \
    #         "LEFT JOIN status_detail ON status_detail.idstatus = data_laporan.status " \
    #         "LEFT JOIN user ON user.iduser = data_laporan.user_id " \
    #         "LEFT JOIN position ON position.id = user.position_id " \
    #         "LEFT JOIN department ON department.id = position.department_id " \
    #         "LEFT JOIN region ON region.id = department.region_id " \
    #         "LEFT JOIN subkategori ON subkategori.idsubkategori = data_laporan.data_laporan_subcategory_id " \
    #         "WHERE data_laporan.data_laporan_subcategory_id IN %(ids)s" % {"ids": tuple(subkategoris)}

    query = "SELECT data_laporan.user_id, data_laporan.lat_pelapor, data_laporan.long_pelapor FROM data_laporan WHERE data_laporan.data_laporan_subcategory_id IN  %(ids)s" % {"ids": regs}
    print("sampai")
    res = dict()
    cursor.execute(query)
    record = cursor.fetchall()
    print("sampai sini")
    res = record
    return jsonify(res)


@cc_blueprint.route('/laporan_filter', methods=["POST"])
def laporan_filter():
    level_user = request.json.get('level_user')
    position_id = request.json.get('position_id')
    start = request.json.get('start')
    limit = request.json.get('limit')

    sub_kategori_id = request.json.get('sub_kategori_id')
    status = request.json.get('status')
    # tgl_submit = request.json.get('tgl_submit')
    # tgl_approve = request.json.get('tgl_approve')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    res = dict()

    query = "SELECT no_laporan,user_id,user.position_id, position.position_name,sub_kategori_id,subkategori.sub_kategori, " \
            "tgl_submitted,tgl_approved,status,status_detail.keterangan,laporan.id, laporan.text FROM laporan " \
            "LEFT JOIN status_detail ON status_detail.idstatus = laporan.status " \
            "LEFT JOIN user ON user.iduser = laporan.user_id " \
            "LEFT JOIN position ON position.id = user.position_id " \
            "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan.sub_kategori_id " \
            "WHERE laporan.position_id = %s AND laporan.sub_kategori_id = %s AND laporan.status = %s and LIMIT %s, %s "

    cursor.execute(query, (position_id, sub_kategori_id, status, start, limit,))
    record = cursor.fetchall()
    res = record
    print(res)

    cursor.close()
    return jsonify(res)


@cc_blueprint.route('/load_video_banner')
def load_video_banner():
    db = get_db()
    cursor = db.cursor()
    ## defining the Query
    query = "SELECT * FROM apps_video_banner WHERE id = '1'"
    query2 = "SELECT * FROM app_link_banner WHERE id = '1'"
    ## getting records from the table
    cursor.execute(query)

    ## fetching all records from the 'cursor' object
    # records = cursor.fetchall()
    record = cursor.fetchone()
    cursor.execute(query2)
    record_link = cursor.fetchone()
    cursor.close()
    ## Showing the data
    # for record in records:
    #     print(record)
    # print(record)
    res = dict()
    res['you_1'] = record[1]
    res['you_2'] = record[3]
    res['you_3'] = record[5]
    res['you_tit1'] = record[2]
    res['you_tit2'] = record[4]
    res['you_tit3'] = record[6]
    res['banner_twitter'] = record[7]
    res['banner_news'] = record[8]
    res['twitter_embed'] = record[9]
    res['news_embed'] = record[10]
    res['link_title'] = record_link[1]
    res['link_banner'] = record_link[2]
    res['link_reff'] = record_link[3]
    res['link_title_2'] = record_link[4]
    res['link_banner_2'] = record_link[5]
    res['link_reff_2'] = record_link[6]
    return json.dumps(res)


@cc_blueprint.route('/load_banner_news')
def load_banner_news():
    db = get_db()
    cursor = db.cursor()

    ## defining the Query
    query = "SELECT * FROM apps_video_banner WHERE id = '1'"

    ## getting records from the table
    cursor.execute(query)
    record = cursor.fetchone()
    cursor.close()

    ## Showing the data
    # for record in records:
    #     print(record)
    # print(record)
    res = dict()
    res2 = dict()
    res['id'] = record[0]
    res['youtube_1'] = record[1]
    res['title_youtube_1'] = record[2]
    res['youtube_2'] = record[3]
    res['title_youtube_2'] = record[4]
    res['youtube_3'] = record[5]
    res['title_youtube_3'] = record[6]
    res['banner_twitter'] = record[7]
    res['banner_news'] = record[8]
    res['twitter_embed'] = record[9]
    res['news_embed'] = record[10]
    res2['list'] = res
    return json.dumps(res2)



# @cc_blueprint.route('/user_get_history', methods=["POST"])
# @jwt_required()
# def user_get_history():
#     id = get_jwt_identity()
#     db.reconnect()
#     cursor = db.cursor(dictionary=True)
#
#     query = "SELECT no_laporan, sub_kategori_id, subkategori.sub_kategori, laporan_text, DATE_FORMAT(tgl_submitted, '%Y-%m-%d %T') as tgl_submitted FROM laporan " \
#             "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan.sub_kategori_id " \
#             "WHERE user_id = %s ORDER BY tgl_submitted DESC "
#     print("syaalala")
#     ## getting records from the table
#     cursor.execute(query, (id,))
#     record = cursor.fetchall()
#     cursor.close()
#
#     res = dict()
#     res['list'] = record
#     res['valid'] = 1
#
#     return res



@cc_blueprint.route('/user_get_picturesolve',methods=["POST"])
@jwt_required()
def user_get_picturesolve():
    id = request.json.get('id')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    # get the last rate & feedback - the latest ID
    query = "SELECT problem,solve FROM work_order_image WHERE work_order_id = %s ORDER BY idworkorderimage DESC"
    cursor.execute(query, (id,))
    record = cursor.fetchall()
    res = dict()
    res['list'] = record
    res['valid'] = 1
    cursor.close()
    return res



@cc_blueprint.route('/warga_get_mail', methods=["POST"])
@jwt_required()
def warga_get_mail():
    username = request.json.get('username', None)
#originalnya ada 3 query execution di satu API call ini
    cursor = db.cursor(dictionary=True)
    # query = "SELECT id_user_mobile, nama FROM user_mobile WHERE email = %s"
    # query2 = "SELECT id_user_mobile FROM work_order WHERE id_user_mobile = '5513'"
    query3 = "SELECT * from work_order WHERE id_user_mobile IN (select id_user_mobile from user_mobile where email = %s)"
    db = get_db()
    cursor.execute(query3, (username,))
    record = cursor.fetchall()

    res = dict()
    res['list'] = record
    res['valid'] = 0

    if (cursor.rowcount > 0) :
        query4 = "SELECT no_pengaduan AS 'NoPengaduan'," \
                 "idworkorder AS 'IdWorkOrder'," \
                 "nama_pelapor AS 'NamePelapor'," \
                 "telp_pelapor AS 'TelpPelapor'," \
                 "alamat_pelapor AS 'AlamatPelapor'," \
                 "lat_pelapor AS 'LatPelapor'," \
                 "long_pelapor AS 'LonPelapor'," \
                 "tgl_kontak AS 'TanggalKontak'," \
                 "tgl_received AS 'Tanggal Received'," \
                 "tgl_on_process AS 'Tanggal On Process'," \
                 "tgl_close AS 'Tanggal Selesai'," \
                 "problem AS 'Picture'," \
                 "status AS 'StatusLaporan', " \
                 "TIMESTAMPDIFF(Hour,tgl_kontak,tgl_close) AS 'Durasi (Jam)', " \
                 "TIMESTAMPDIFF(Minute,tgl_kontak,tgl_close) AS 'Durasi (Menit)', " \
                 "TIMESTAMPDIFF(Second,tgl_kontak,tgl_close) AS 'Durasi (Detik)', " \
                 "position.position_name AS 'Position', " \
                 "department.department_name AS 'Department', " \
                 "region.region_name AS 'Region', " \
                 "kategori.kategori AS 'Kategori', " \
                 "subkategori.sub_kategori AS 'SubKategori', " \
                 "user.username AS 'User Creator', " \
                 "pengaduan AS 'Pengaduan', IF(STATUS=1,'Open', IF(STATUS=2,'Received', IF(STATUS=3,'On Process', IF(STATUS=4,'Done','')))) AS STATUS " \
                 "from work_order LEFT JOIN position ON position.id = work_order.position_id  " \
                 "LEFT JOIN department ON department.id = position.department_id " \
                 "LEFT JOIN region ON region.id = department.region_id " \
                 "LEFT JOIN work_order_image ON work_order_image.work_order_id = work_order.idworkorder " \
                 "LEFT JOIN subkategori ON subkategori.idsubkategori = work_order.sub_kategori_id " \
                 "LEFT JOIN kategori ON kategori.idkategori = subkategori.kategori_id " \
                 "LEFT JOIN user ON user.iduser = work_order.user_id " \
                 "WHERE work_order.id_user_mobile = %s ORDER BY idworkorder DESC"
        cursor.execute(query4, (res['list'][0]['id_user_mobile'],))
        record = cursor.fetchall()
        res['list'] = record
        res['sitrep'] = len(record)
        res['valid'] = 1
    res['sitrep'] = len(record)
    cursor.close()
    return res

# @cc_blueprint.route('/user_get_category')
# def user_get_category():
#     cursor = db.cursor(dictionary=True)
#     query = "SELECT idsubkategori AS 'id', sub_kategori AS 'name', icon, nomor FROM subkategori WHERE kategori_id = %s ORDER BY nomor ASC"
#     cursor.execute(query, ('1',))
#     record = cursor.fetchall()
#     res = dict()
#     res['list'] = record
#     res['valid'] = 1
#     cursor.close()
#     return res

@cc_blueprint.route('/laporan_subkategori_list', methods=["get"])
def laporan_subkategori_list():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = "SELECT idsubkategori, sub_kategori, icon,  nomor, kategori_id, kategori.kategori from subkategori " \
            "LEFT JOIN kategori ON kategori.idkategori = subkategori.kategori_id "
    cursor.execute(query,)
    record = cursor.fetchall()
    cursor.close()
    res = dict()
    res = record
    return jsonify(res)


@cc_blueprint.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@cc_blueprint.route('/downloads/laporan/<kategori_id>/<name>')
def download_file_laporan(kategori_id, name):
    res = dict()
    dirName = "downloads/laporan/" + kategori_id
    try:
        # Create target Directory
        os.mkdir(dirName)
        print("Directory ", dirName, " Created ")
    except FileExistsError:
        print("Directory ", dirName, " already exists")

    path_to_file = app.config["DOWNLOAD_FOLDER"] + "laporan/" + kategori_id + '/'
    file_exists = exists(path_to_file + name)
    print("here")
    if file_exists :
        return send_from_directory(path_to_file, name)
    else :
        res['valid'] = 0
        res['error'] = "file does not exist"
        return res


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

@cc_blueprint.route('/upload_giat_foto', methods=["POST"])
# @jwt_required()
def upload_giat_foto():
    print("inside upload image")
    res = dict()
    # user_id = get_jwt_identity()
    newfilename = ''
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file part')
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        laporan_no = request.form['laporan_no']
        laporan_subkategori_id = request.form['laporan_subcategory_id']
        user_id = request.form['user_id']

        # print(request.form['laporan_no'])
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print("no selected file")
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_image_file(file.filename):
            print("inside user photo 3")
            filename = secure_filename(file.filename)
            # print(os.path.join(app.config['UPLOAD_GIATHARIAN_FOLDER']))
            ts = time.time()
            # newfilename = str(user_id) + "-" + str(laporan_subkategori_id) + "-" + str(laporan_no) + "-" + os.path.splitext(str(ts))[0] + os.path.splitext(filename)[1]
            newfilename = str(user_id) + "-" + str(laporan_subkategori_id) + "-" + str(laporan_no) + os.path.splitext(filename)[1]
            if (laporan_subkategori_id == "4") :

                file.save(os.path.join(app.config['UPLOAD_GIATHARIAN_FOLDER'] + "/" + newfilename.lower()))
            elif (laporan_subkategori_id == "5") :
                file.save(os.path.join(app.config['UPLOAD_GIATINSIDENTIL_FOLDER'] + "/" + newfilename.lower()))


            res['valid'] = '1'
            res['filename'] = newfilename.lower()
            return res
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''



@cc_blueprint.route('/upload_userphoto', methods=["POST"])
# @jwt_required()
def upload_userphoto():
    print("inside user photo")
    res = dict()
    # user_id = get_jwt_identity()
    newfilename = ''
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file part')
            flash('No file part')
            return redirect(request.url)
        print("FILE OK")
        file = request.files['file']
        # laporan_no = request.form['laporan_no']
        user_id  = request.form['user_id']
        # print(request.form['laporan_no'])
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print("no selected file")
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_image_file(file.filename):
            print("inside user photo 3")
            filename = secure_filename(file.filename)

            print(os.path.join(app.config['UPLOAD_USERPHOTO_FOLDER']))
            print("inside user photo 2")
            # ts = time.time()
            # newfilename = str(laporan_no) + "-" + str(laporan_subcategory_id) + "-" + str(user_id) + "-" + os.path.splitext(str(ts))[0] + os.path.splitext(filename)[1]
            newfilename = os.path.splitext(filename)[1]
            file.save(os.path.join(app.config['UPLOAD_USERPHOTO_FOLDER'] + "/" + user_id + ".jpeg" ))


            res['valid'] = '1'
            # res['thumb_path'] ='https://ccntmc.1500669.com/ntmc_upload/'.$uploadfile
            return res
            # return redirect(url_for('download_file', name=newfilename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@cc_blueprint.route('/get_giatharian_image', methods=["POST"])
def get_giatharian_image():
    res = dict()
    filename = request.form['filename']
    # name = user_id + ".jpeg"
    path_to_file = app.config["UPLOAD_GIATHARIAN_FOLDER"] + '/'
    file_exists = exists(path_to_file + filename)
    if file_exists :
        return send_from_directory(path_to_file, filename)
    else :
        res['valid'] = 0
        res['error'] = "file does not exist"
        return res

@cc_blueprint.route('/get_giatinsidentil_image', methods=["POST"])
def get_giatinsidentil_image():
    res = dict()
    filename = request.form['filename']
    # name = user_id + ".jpeg"
    path_to_file = app.config["UPLOAD_GIATINSIDENTIL_FOLDER"] + '/'
    file_exists = exists(path_to_file + filename)
    if file_exists :
        return send_from_directory(path_to_file, filename)
    else :
        res['valid'] = 0
        res['error'] = "file does not exist"
        return res


@cc_blueprint.route('/get_userphoto', methods=["POST"])
def get_userphoto():
    res = dict()
    print("here")
    user_id = request.form['user_id']
    name = user_id + ".jpeg"
    path_to_file = app.config["UPLOAD_USERPHOTO_FOLDER"] + '/'
    file_exists = exists(path_to_file + name)
    if file_exists :
        return send_from_directory(path_to_file, name)
    else :
        res['valid'] = 0
        res['error'] = "file does not exist"
        return res



@cc_blueprint.route('/upload_laporan', methods=["POST"])
@jwt_required()
def upload_laporan():
    res = dict()
    user_id = get_jwt_identity()
    newfilename = ''
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file part')
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # laporan_no = request.form['laporan_no']
        laporan_subcategory_id = request.form['laporan_subcategory_id']
        # print(request.form['laporan_no'])
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(os.path.join(app.config['UPLOAD_LAPORAN_FOLDER']))
            ts = time.time()
            # newfilename = str(laporan_no) + "-" + str(laporan_subcategory_id) + "-" + str(user_id) + "-" + os.path.splitext(str(ts))[0] + os.path.splitext(filename)[1]
            newfilename = os.path.splitext(filename)[1]
            file.save(os.path.join(app.config['UPLOAD_LAPORAN_FOLDER'] + laporan_subcategory_id + "/", filename ))


            res['valid'] = '1'
            # res['thumb_path'] ='https://ccntmc.1500669.com/ntmc_upload/'.$uploadfile
            return res
            # return redirect(url_for('download_file', name=newfilename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''







@cc_blueprint.route('/upload', methods=["POST"])
@jwt_required()
def upload_file():
    res = dict()
    user_id = get_jwt_identity()
    newfilename = ''
    if request.method == 'POST':
        print('post')
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file part')
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        laporan_no = request.form['laporan_no']
        laporan_subcategory_id = request.form['laporan_subcategory_id']
        # print(request.form['laporan_no'])
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(os.path.join(app.config['UPLOAD_FOLDER']))
            ts = time.time()
            newfilename = str(laporan_no) + "-" + str(laporan_subcategory_id) + "-" + str(user_id) + "-" + os.path.splitext(str(ts))[0] + os.path.splitext(filename)[1]

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], newfilename ))
            db = get_db()
            cursor = db.cursor(dictionary=True)
            # get the last rate & feedback - the latest ID
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
            query = "INSERT INTO file_uploads (file_name, file_type, laporan_no, laporan_subcategory_id, user_id, date_submitted) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (newfilename, "file", laporan_no, laporan_subcategory_id, user_id, formatted_date,))
            db.commit()
            res['valid'] = '1'
            # res['thumb_path'] ='https://ccntmc.1500669.com/ntmc_upload/'.$uploadfile
            return res
            # return redirect(url_for('download_file', name=newfilename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''








@cc_blueprint.route('/save_token',methods=["POST"])
@jwt_required()
def save_token():
    username = request.json.get('username')
    token = request.json.get('token')


    stamp2 = datetime.now()

    stamp = stamp2.strftime("%Y-%m-%d %H:%M:%S")
    db = get_db()
    cursor = db.cursor(dictionary=True)
    # get the last rate & feedback - the latest ID
    query = "INSERT INTO notif_token (username, token, stamp) VALUES (%s, %s, %s)"
    cursor.execute(query, (username, token, stamp,))
    db.commit()

    # record = cursor.fetchall()
    res = dict()
    # res['list'] = record
    res['valid'] = 1
    cursor.close()
    return res

@cc_blueprint.route('/user_idle', methods=["POST"])
@jwt_required()
def user_idle():
    username = request.json.get('username', None)
    if (username == "") :
        valid = 0
        name = ""
    else :
        db = get_db()
        cursor = db.cursor(dictionary=True)
        query = "SELECT id_user_mobile, nama FROM user_mobile WHERE email = %s"
        cursor.execute(query, (username,))
        record = cursor.fetchall()
        if (len(record) > 0) :
            valid = 1
            name = record[0]['nama']
        else :
            valid = 0
            name = ""


    res = dict()
    res['name'] = name
    res['valid'] = valid
    cursor.close()
    return res




@cc_blueprint.route('/verify', methods=["POST"])
@jwt_required()
def verify():
    email = request.json.get('email')
    passwd = request.json.get('pass')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = "SELECT id_user_mobile,password FROM user_mobile WHERE email = %s"
    cursor.execute(query, (email,))
    record = cursor.fetchall()
    cursor.close()
    valid = 0

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(passwd.encode(), salt)

    if bcrypt.checkpw(passwd.encode(), (record[0]['password']).encode()):
        print("match")
    else:
        print("does not match")
    return 'valid'



@cc_blueprint.route('/user_upload_ktp', methods=["POST"])
@jwt_required()
def warga_upload_ktp():
    email = request.json.get('email')
    passwd = request.json.get('pass')

@cc_blueprint.route('/user_upload_photo', methods=["POST"])
@jwt_required()
def warga_upload_photo():
    email = request.json.get('email')
    passwd = request.json.get('pass')

@cc_blueprint.route('/user_upload_video', methods=["POST"])
@jwt_required()
def warga_upload_video():
    email = request.json.get('email')
    passwd = request.json.get('pass')









################### LAPORAN GIAT #################################################

@cc_blueprint.route('/laporan_giat_user', methods=["POST"])
def laporan_giat_user():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = "SELECT laporan_giat.id, laporan_giat.user_id, laporan_giat.region_id, laporan_giat.department_id, laporan_giat.no_laporan, laporan_giat.tgl_laporan, " \
            "laporan_giat.laporan_text, laporan_giat.lat_pelapor, laporan_giat.long_pelapor, laporan_giat.laporan_subcategory_id, subkategori.sub_kategori,  laporan_giat.image_file FROM laporan_giat " \
            "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan_giat.laporan_subcategory_id "
            # "WHERE DATE(laporan_published.date_submitted) =  DATE('"+ date +"')  AND laporan.sub_kategori_id =  " + subkategoriid + " GROUP BY laporan.laporan_subcategory_id"
    cursor.execute(query,)
    record = cursor.fetchall()
    cursor.close()
    result = dict()
    # print(record)
    temp = dict()

    return jsonify(record)





@cc_blueprint.route('/laporan_giat_list', methods=["GET"])
def laporan_giat_list():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    # date_submitted = request.json.get('date_submitted')
    # date_approved = request.json.get('date_approved')
    # status = request.json.get('status')
    query = "SELECT laporan_giat.id, laporan_giat.user_id, laporan_giat.region_id, region.region_name, laporan_giat.department_id, department.department_name, no_laporan, " \
            "tgl_laporan, DATE_FORMAT(tgl_laporan, '%e/%m/%Y') as tgl_for_search, lat_pelapor, long_pelapor, laporan_text, laporan_subcategory_id, subkategori.sub_kategori, image_file FROM laporan_giat " \
            "LEFT JOIN region ON region.id = laporan_giat.region_id " \
            "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan_giat.laporan_subcategory_id " \
            "LEFT JOIN department ON department.id = laporan_giat.department_id "
    cursor.execute(query)
    record = cursor.fetchall()
    cursor.close()
    result = dict()
    result = record
    return jsonify(result)


@cc_blueprint.route('/laporan_giat_submit', methods=["POST"])
def laporan_giat_submit():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    # no_laporan = request.json.get('no_laporan')
    tgl_laporan = request.json.get('tgl_laporan')
    laporan_subcategory_id = request.json.get('laporan_subcategory_id')
    laporan_text = request.json.get('laporan_text')
    user_id = request.json.get('user_id')
    region_id = request.json.get('region_id')
    department_id = request.json.get('department_id')
    lat_pelapor = request.json.get('lat_pelapor')
    long_pelapor = request.json.get('long_pelapor')
    image_file = request.json.get('image_file')
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

    ts = time.time()
    no_laporan = str(user_id) + "-" + str(laporan_subcategory_id) + "-" + os.path.splitext(str(ts))[0]
    query = "INSERT INTO laporan_giat (user_id, region_id, department_id, no_laporan, tgl_laporan, laporan_text,  lat_pelapor, long_pelapor, laporan_subcategory_id, image_file, tgl_submitted) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "

    result = dict()
    print("laporan giat review")
    cursor.execute(query, (str(user_id),str(region_id),str(department_id),str(no_laporan), tgl_laporan, laporan_text,str(lat_pelapor),str(long_pelapor),str(laporan_subcategory_id),image_file,formatted_date))
    try:
        db.commit()
    except mysql.connector.Error as error:
        print("Failed to update record to database rollback: {}".format(error))
        # reverting changes because of exception
        cursor.rollback()
        result['result'] = 'failed'
        result['valid'] = 2
    finally:
        print("here success")
        cursor.close()
        result['result'] = 'success'
        result['valid'] = 1
    return jsonify(result)



################### REGION CRUD #################################################

@cc_blueprint.route('/region_image_upload', methods=["POST"])
def region_image_upload():
    res = dict()
    newfilename = ''
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file part')
            res['valid'] = '0'
        print("FILE OK")
        file = request.files['file']
        region_id = request.form['region_id']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print("no selected file")
            res['valid'] = '0'

        if file and allowed_image_file(file.filename):
            filename = secure_filename(file.filename)
            img_ext = os.path.splitext(filename)[1]
            file.save(os.path.join(app.config['UPLOAD_REGION_FOLDER'] + "/" + str(region_id) + img_ext))
            db = get_db()
            cursor = db.cursor(dictionary=True)
            newfilename = str(region_id) + img_ext
            query = "UPDATE region set image = %s where id = %s"
            cursor.execute(query, (newfilename, region_id,))
            try:
                db.commit()
            except mysql.connector.Error as error:
                print("Failed to update record to database rollback: {}".format(error))
                # reverting changes because of exception
                cursor.rollback()
                res['result'] = 'failed'
                res['valid'] = 0
            finally:
                cursor.close()
                res['result'] = 'success'
                res['valid'] = 1
            cursor.close()
    return res

@cc_blueprint.route('/region_image_download', methods=["POST"])
def region_image_download():
    image_name = request.json.get('image_name')
    return send_from_directory(app.config["UPLOAD_REGION_FOLDER"], image_name)




@cc_blueprint.route('/region_create', methods=["POST"])
def region_create():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    region_name = request.json.get('region_name')

    query = "INSERT INTO region (region_name) VALUES (%s)"
    cursor.execute(query, (region_name,))

    # print("here")
    result = dict()
    try:
        db.commit()
    except mysql.connector.Error as error:
        print("Failed to update record to database rollback: {}".format(error))
        # reverting changes because of exception
        cursor.rollback()
        result['result'] = 'failed'
        result['valid'] = 2
    finally:

        cursor.close()
        result['result'] = 'success'
        result['valid'] = 1
    cursor.close()
    return result


@cc_blueprint.route('/region_update', methods=["POST"])
def region_update():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    region_id = request.json.get('region_id')
    region_name = request.json.get('region_name')

    query = "UPDATE region set region_name = %s where id = %s"
    cursor.execute(query, (region_name, region_id,))

    # print("here")
    result = dict()
    try:
        db.commit()
    except mysql.connector.Error as error:
        print("Failed to update record to database rollback: {}".format(error))
        # reverting changes because of exception
        cursor.rollback()
        result['result'] = 'failed'
        result['valid'] = 2
    finally:

        cursor.close()
        result['result'] = 'success'
        result['valid'] = 1
    cursor.close()
    return result


@cc_blueprint.route('/region_read', methods=["GET"])
def region_read():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    region_id = request.json.get('region_id')
    query = "SELECT id, region_name, image from region WHERE id = %s"
    cursor.execute(query, (str(region_id),))
    record = cursor.fetchone()
    cursor.close()
    result = dict()
    result = record
    return jsonify(result)

@cc_blueprint.route('/region_delete', methods=["DELETE"])
def region_delete():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    region_id = request.json.get('region_id')

    query = "DELETE FROM region where id = %s"
    cursor.execute(query, (region_id,))

    # print("here")
    result = dict()
    try:
        db.commit()
        result['row_affected'] = cursor.rowcount
        result['result'] = 'success'
        result['valid'] = 1
    except mysql.connector.Error as error:
        print("Failed to update record to database rollback: {}".format(error))
        # reverting changes because of exception
        cursor.rollback()
        result['result'] = 'failed'
        result['row_affected'] = cursor.rowcount
        result['valid'] = 0
    finally:

        cursor.close()

    cursor.close()
    return result



################### DEPARTMENT CRUD #################################################

@cc_blueprint.route('/department_image_upload', methods=["POST"])
def department_image_upload():
    res = dict()
    newfilename = ''
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file part')
            res['valid'] = '0'
        file = request.files['file']
        department_id = request.form['department_id']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print("no selected file")
            res['valid'] = '0'

        if file and allowed_image_file(file.filename):
            filename = secure_filename(file.filename)
            img_ext = os.path.splitext(filename)[1]
            file.save(os.path.join(app.config['UPLOAD_DEPARTMENT_FOLDER'] + "/" + str(department_id) + img_ext))
            db = get_db()
            cursor = db.cursor(dictionary=True)
            newfilename = str(department_id) + img_ext
            query = "UPDATE department set image = %s where id = %s"
            cursor.execute(query, (newfilename, department_id,))
            try:
                db.commit()
            except mysql.connector.Error as error:
                print("Failed to update record to database rollback: {}".format(error))
                # reverting changes because of exception
                cursor.rollback()
                res['result'] = 'failed'
                res['valid'] = 0
            finally:
                cursor.close()
                res['result'] = 'success'
                res['valid'] = 1
            cursor.close()
    return res

@cc_blueprint.route('/department_image_download', methods=["POST"])
def department_image_download():
    image_name = request.json.get('image_name')
    return send_from_directory(app.config["UPLOAD_DEPARTMENT_FOLDER"], image_name)




@cc_blueprint.route('/department_create', methods=["POST"])
def department_create():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    department_name = request.json.get('department_name')
    region_id = request.json.get('region_id')
    query = "INSERT INTO department (region_id, department_name) VALUES (%s, %s)"
    cursor.execute(query, (region_id, department_name,))

    result = dict()
    try:
        db.commit()
    except mysql.connector.Error as error:
        print("Failed to update record to database rollback: {}".format(error))
        # reverting changes because of exception
        cursor.rollback()
        result['result'] = 'failed'
        result['valid'] = 0
    finally:

        cursor.close()
        result['result'] = 'success'
        result['valid'] = 1
    cursor.close()
    return result


@cc_blueprint.route('/department_update', methods=["POST"])
def department_update():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    department_id = request.json.get('department_id')
    region_id = request.json.get('region_id')
    department_name = request.json.get('department_name')
    telp = request.json.get('telp')

    query = "UPDATE department set department_name = %s, telp = %s, region_id = %s where id = %s"
    cursor.execute(query, (department_name, telp, region_id,department_id,))

    result = dict()
    try:
        db.commit()
    except mysql.connector.Error as error:
        print("Failed to update record to database rollback: {}".format(error))
        # reverting changes because of exception
        cursor.rollback()
        result['result'] = 'failed'
        result['valid'] = 0
    finally:

        cursor.close()
        result['result'] = 'success'
        result['valid'] = 1
    cursor.close()
    return result


@cc_blueprint.route('/department_read', methods=["GET"])
def department_read():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    department_id = request.json.get('department_id')
    query = "SELECT id, region_id, department_name, telp, image from department WHERE id = %s"
    cursor.execute(query, (str(department_id),))
    record = cursor.fetchone()
    cursor.close()
    result = dict()
    result = record
    return jsonify(result)

@cc_blueprint.route('/department_delete', methods=["DELETE"])
def department_delete():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    department_id = request.json.get('department_id')

    query = "DELETE FROM department where id = %s"
    cursor.execute(query, (department_id,))

    result = dict()
    result['result'] = 'failed'
    result['valid'] = 0
    try:
        db.commit()
        result['result'] = 'success'
        result['row_affected'] = cursor.rowcount
        result['valid'] = 1
    except mysql.connector.Error as error:
        print("Failed to update record to database rollback: {}".format(error))
        # reverting changes because of exception
        cursor.rollback()
        result['result'] = 'failed'
        result['row_affected'] = cursor.rowcount
        result['valid'] = 0
    finally:

        cursor.close()

    cursor.close()
    return result



################### LAPORAN SISKAMBTIBMAS #################################################

@cc_blueprint.route('/laporan_review', methods=["POST"])
def laporan_review():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    no_laporan = request.json.get('no_laporan')


    query = "SELECT data_laporan.id, data_laporan.tgl_laporan, laporan_published.no_laporan, laporan_published.status, laporan_subcategory.sub_category_id, subkategori.sub_kategori, " \
            "data_laporan.data_laporan_subcategory_id, laporan_subcategory.name, data_laporan.laporan_total, data_laporan.laporan_text, laporan_published.date_submitted FROM data_laporan " \
            "LEFT JOIN laporan_subcategory ON laporan_subcategory.id = data_laporan.data_laporan_subcategory_id " \
            "LEFT JOIN laporan_published ON DATE(laporan_published.tgl_laporan) = DATE(data_laporan.tgl_laporan) AND " \
            "laporan_published.region_id = data_laporan.region_id AND laporan_subcategory.sub_category_id = laporan_published.laporan_subcategory_id " \
            "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan_subcategory.sub_category_id " \
            "WHERE laporan_published.no_laporan = %s"
    print("laporan review")
    cursor.execute(query, (str(no_laporan),))
    record = cursor.fetchall()
    cursor.close()
    result = dict()
    result = record
    return jsonify(result)

@cc_blueprint.route('/data_laporan_review_all', methods=["POST"])
def data_laporan_review_all():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    date = request.json.get('tgl_submitted')
    subkategoriid = request.json.get('sub_kategori_id')


    query = "SELECT data_laporan.id, data_laporan.tgl_laporan, laporan_published.no_laporan, laporan_published.status, laporan_subcategory.sub_category_id, subkategori.sub_kategori, " \
            "data_laporan.data_laporan_subcategory_id, laporan_subcategory.name, data_laporan.laporan_total, data_laporan.laporan_text, laporan_published.date_submitted FROM data_laporan " \
            "LEFT JOIN laporan_subcategory ON laporan_subcategory.id = data_laporan.data_laporan_subcategory_id " \
            "LEFT JOIN laporan_published ON DATE(laporan_published.tgl_laporan) = DATE(data_laporan.tgl_laporan) AND " \
            "laporan_published.region_id = data_laporan.region_id AND laporan_subcategory.sub_category_id = laporan_published.laporan_subcategory_id " \
            "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan_subcategory.sub_category_id " \
            "WHERE DATE(data_laporan.tgl_submitted) =  DATE('" + date + "') GROUP BY data_laporan.data_laporan_subcategory_id order by data_laporan.data_laporan_subcategory_id asc"

    print("laporan review")
    cursor.execute(query)
    record = cursor.fetchall()
    cursor.close()
    result = dict()
    result = record
    return jsonify(result)

@cc_blueprint.route('/data_laporan_review_peruser', methods=["POST"])
def data_laporan_review_peruser():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    userid = request.json.get('user_id')
    date = request.json.get('tgl_submitted')
    # subkategoriid = request.json.get('sub_kategori_id')


    query = "SELECT data_laporan.id, data_laporan.tgl_laporan, laporan_published.no_laporan, laporan_published.status, laporan_subcategory.sub_category_id, subkategori.sub_kategori, " \
            "data_laporan.data_laporan_subcategory_id, laporan_subcategory.name, data_laporan.laporan_total, data_laporan.laporan_text, laporan_published.date_submitted FROM data_laporan " \
            "LEFT JOIN laporan_subcategory ON laporan_subcategory.id = data_laporan.data_laporan_subcategory_id " \
            "LEFT JOIN laporan_published ON DATE(laporan_published.tgl_laporan) = DATE(data_laporan.tgl_laporan) AND " \
            "laporan_published.region_id = data_laporan.region_id AND laporan_subcategory.sub_category_id = laporan_published.laporan_subcategory_id " \
            "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan_subcategory.sub_category_id " \
            "WHERE DATE(data_laporan.tgl_submitted) =  DATE('" + date + "') AND data_laporan.user_id = '" + str(userid) + "' GROUP BY data_laporan.data_laporan_subcategory_id order by data_laporan.data_laporan_subcategory_id asc"

    print("laporan review")
    cursor.execute(query)
    record = cursor.fetchall()
    cursor.close()
    result = dict()
    result = record
    return jsonify(result)



@cc_blueprint.route('/laporan_data_review', methods=["POST"])
def laporan_data_review():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    date = request.json.get('date')
    subkategoriid = request.json.get('sub_kategori_id')

    query = "SELECT laporan.id, laporan.no_laporan, laporan_published.status, laporan.laporan_total, laporan.sub_kategori_id, subkategori.sub_kategori, " \
            "laporan.laporan_subcategory_id, laporan_subcategory.name FROM laporan " \
            "LEFT JOIN laporan_published ON laporan_published.no_laporan = laporan.no_laporan " \
            "LEFT JOIN laporan_subcategory ON laporan_subcategory.id = laporan.laporan_subcategory_id " \
            "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan.sub_kategori_id " \
            "WHERE DATE(laporan_published.date_submitted) =  DATE('"+ date +"')  AND laporan.sub_kategori_id =  " + subkategoriid + " GROUP BY laporan.laporan_subcategory_id"
    cursor.execute(query,)
    record = cursor.fetchall()
    cursor.close()
    result = dict()
    # result = record
    temp = dict()
    # result = [];
    data_array = []
    nolaporan = ''
    subkategorinama = ''
    for x in record:
        temp = dict()
        temp['id'] = x['id']
        temp['laporan_subcategory_id'] = x['laporan_subcategory_id']
        temp['name'] = x['name']
        temp['laporan_total'] = x['laporan_total']
        nolaporan = x['no_laporan']
        subkategorinama = x['sub_kategori']
        # print(x['id'])
        data_array.append(temp)
    print(data_array)
    result['data'] = record
    result['sub_kategori_id'] = subkategoriid
    result['sub_kategori_nama'] = subkategorinama

    return jsonify(result)

@cc_blueprint.route('/create_laporan', methods=["POST"])
def create_laporan():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    tgl_laporan = request.json.get('tgl_laporan')
    subkategoriid = request.json.get('sub_kategori_id')
    region_id = request.json.get('region_id')
    department_id = request.json.get('department_id')

    result = dict()
    tgl_laporan_datetime_object = datetime.strptime(tgl_laporan, '%Y-%m-%d %H:%M:%S')

    query_a = "SELECT idsubkategori, kategori_id, kategori.kategori, sub_kategori FROM subkategori " \
              "LEFT JOIN kategori ON kategori.idkategori = subkategori.kategori_id " \
              "WHERE idsubkategori = %s"
    cursor.execute(query_a, (subkategoriid,))
    record = cursor.fetchone()
    if record is None:
        result['valid'] = 0
        result['status'] = 'wrong sub_kategori_id'
        return jsonify(result)



    if(record['kategori_id'] == 1) :
        print("ini yg pertama")
        no_laporan_string = str(date.today().year) + "-" + str(tgl_laporan_datetime_object.month) + "-" + str(tgl_laporan_datetime_object.strftime("%d")) + "-" + str(subkategoriid) + "-" + str(region_id)
    elif (record['kategori_id'] == 2) :
        print("ini yg kedua")
        no_laporan_string = str(date.today().year) + "-" + str(date.today().month) + "-" + str(subkategoriid) + "-" + str(region_id)
    else :
        print(record['kategori_id'])
        no_laporan_string = str(date.today().year) + "-" + str(subkategoriid) + "-" + str(region_id)
    print(no_laporan_string)
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    query = "INSERT IGNORE INTO laporan_published (no_laporan, tgl_laporan, region_id, department_id, laporan_subcategory_id, date_submitted) VALUES (%s,%s, %s, %s, %s, %s)"
    try:
        print("in try")
        cursor.execute(query,(no_laporan_string, tgl_laporan, region_id, department_id, subkategoriid, formatted_date,))
        db.commit()
        result = dict()
        print(tgl_laporan)
        print("here 999")
        result['result'] = 'success'
        result['valid'] = 1
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        # print("Failed to update record to database rollback: {}".format(error))
        # reverting changes because of exception
        cursor.rollback()
        result['result'] = 'failed'
        result['valid'] = 2
    finally:
        cursor.close()


    cursor.close()

    return jsonify(result)





@cc_blueprint.route('/display_stats', methods=["POST"])
def display_stats(self=None):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    result_array = []
    # userid = request.json.get('user_id')
    # laporan_subcategory_id = request.json.get('laporan_subcategory_id')
    # # status = request.json.get('status')
    # query = "SELECT laporan_giat.id, laporan_giat.user_id, laporan_giat.region_id, region.region_name, laporan_giat.department_id, department.department_name, no_laporan, tgl_laporan, lat_pelapor, long_pelapor, laporan_text, laporan_subcategory_id, subkategori.sub_kategori, image_file FROM laporan_giat " \
    #         "LEFT JOIN region ON region.id = laporan_giat.region_id " \
    #         "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan_giat.laporan_subcategory_id " \
    #         "LEFT JOIN department ON department.id = laporan_giat.department_id WHERE laporan_giat.user_id = %s AND laporan_giat.laporan_subcategory_id = %s"
    # cursor.execute(query, (userid,laporan_subcategory_id,))
    # record = cursor.fetchall()
    # cursor.close()
    # result = dict()
    # result = record

    result = getattr(Stats, "stats_most_active_region")(2)
    result2 = getattr(Stats, "stats_most_active_user")(2)
    result_array.append(result)
    result_array.append(result2)
    result_array.append(result)
    result_array.append(result2)
    return jsonify(result_array)


@cc_blueprint.route('/laporan_giat_list_peruser', methods=["POST"])
def laporan_giat_list_peruser():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    userid = request.json.get('user_id')
    laporan_subcategory_id = request.json.get('laporan_subcategory_id')
    # status = request.json.get('status')
    query = "SELECT laporan_giat.id, laporan_giat.user_id, laporan_giat.region_id, region.region_name, laporan_giat.department_id, department.department_name, no_laporan, tgl_laporan, lat_pelapor, long_pelapor, laporan_text, laporan_subcategory_id, subkategori.sub_kategori, image_file FROM laporan_giat " \
            "LEFT JOIN region ON region.id = laporan_giat.region_id " \
            "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan_giat.laporan_subcategory_id " \
            "LEFT JOIN department ON department.id = laporan_giat.department_id WHERE laporan_giat.user_id = %s AND laporan_giat.laporan_subcategory_id = %s"
    cursor.execute(query, (userid,laporan_subcategory_id,))
    record = cursor.fetchall()
    cursor.close()
    result = dict()
    result = record
    return jsonify(result)




@cc_blueprint.route('/laporan_print', methods=["POST"])
def laporan_print():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    no_laporan = request.json.get('no_laporan')
    query = "SELECT laporan.id, laporan.no_laporan, laporan_published.status, laporan.sub_kategori_id, subkategori.sub_kategori, " \
            "laporan.laporan_subcategory_id, laporan_subcategory.name, laporan.laporan_total, laporan.laporan_text, laporan_published.date_submitted, " \
            "laporan_published.date_approved FROM laporan " \
            "LEFT JOIN laporan_published ON laporan_published.no_laporan = laporan.no_laporan " \
            "LEFT JOIN laporan_subcategory ON laporan_subcategory.id = laporan.laporan_subcategory_id " \
            "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan.sub_kategori_id " \
            "WHERE laporan.no_laporan = %s"
    cursor.execute(query, (str(no_laporan),))
    record = cursor.fetchall()
    cursor.close()
    result = dict()
    result = record
    return jsonify(result)

@cc_blueprint.route('/laporan_print_filter', methods=["POST"])
def laporan_print_filter():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    date_submitted = request.json.get('date_submitted')
    date_approved = request.json.get('date_approved')
    status = request.json.get('status')

    where_query = ""
    query = "SELECT laporan.id, laporan.no_laporan, laporan_published.status, laporan.sub_kategori_id, subkategori.sub_kategori, " \
            "laporan.laporan_subcategory_id, laporan_subcategory.name, laporan_published.date_submitted, " \
            "laporan_published.date_approved FROM laporan " \
            "LEFT JOIN laporan_published ON laporan_published.no_laporan = laporan.no_laporan " \
            "LEFT JOIN laporan_subcategory ON laporan_subcategory.id = laporan.laporan_subcategory_id " \
            "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan.sub_kategori_id"

    if status != "" :
        status_exist = True
        where_query = where_query + ' WHERE laporan_published.status = "' +status +'"'
    if date_submitted != "":
        submitted_exist = True
        if (status_exist) :
            where_query = where_query + ' AND DATE(laporan_published.date_submitted) =  DATE("'+ date_submitted +'")'
        else :
            where_query = where_query + ' WHERE DATE(laporan_published.date_submitted) =  DATE("'+ date_submitted +'")'
    if date_approved != "":
        approved_exist = True
        if (status_exist or submitted_exist):
            where_query = where_query + ' AND DATE(laporan_published.date_approved) = DATE("'+ date_approved +'")'
        else :
            where_query = where_query + ' WHERE DATE(laporan_published.date_approved) = DATE("'+ date_approved +'")'

    query = query + where_query
    print (query)
    cursor.execute(query,)
    # cursor.execute(query, (str(no_laporan),))
    record = cursor.fetchall()
    cursor.close()
    result = dict()
    result = record
    return jsonify(result)


@cc_blueprint.route('/get_laporan_data_list', methods=["POST"])
def get_laporan_data_list():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    sub_category_id = request.json.get('sub_kategori_id')
    query = "SELECT id, name, type, description, laporan_subcategory.group, status FROM laporan_subcategory " \
            "WHERE sub_category_id = %s"
    cursor.execute(query,(sub_category_id,))
    record = cursor.fetchall()
    cursor.close()
    result = dict()
    result = record
    return jsonify(result)


@cc_blueprint.route('/load_laporan_data_list', methods=["POST"])
def load_laporan_data_list():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    sub_category_id = request.json.get('sub_kategori_id')
    tgl_laporan = request.json.get('tgl_laporan')
    region_id = request.json.get('region_id')

    query = "SELECT data_laporan.id, data_laporan.tgl_laporan, laporan_published.no_laporan, laporan_published.status, subkategori.sub_kategori, " \
            "data_laporan.data_laporan_subcategory_id, laporan_subcategory.name, data_laporan.laporan_total, data_laporan.laporan_text, laporan_published.date_submitted FROM data_laporan " \
            "LEFT JOIN laporan_published ON DATE(laporan_published.tgl_laporan) = DATE(data_laporan.tgl_laporan) " \
            "LEFT JOIN laporan_subcategory ON laporan_subcategory.id = data_laporan.data_laporan_subcategory_id " \
            "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan_subcategory.sub_category_id " \
            "WHERE DATE(laporan_published.tgl_laporan) = DATE(%s) AND laporan_published.laporan_subcategory_id = %s AND data_laporan.region_id = %s"


    cursor.execute(query,(tgl_laporan, sub_category_id, region_id,))
    record = cursor.fetchall()
    print("load laporan")
    cursor.close()
    result = dict()
    result = record
    return jsonify(result)


@cc_blueprint.route('/get_region_list', methods=["GET"])
def get_region_list():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    # sub_category_id = request.json.get('sub_kategori_id')
    query = "select id, region_name, image from region"
    cursor.execute(query,)
    record = cursor.fetchall()
    cursor.close()
    result = dict()
    result = record
    return jsonify(result)


# @cc_blueprint.route('/get_position_list', methods=["GET"])
# def get_position_list():
#     db.reconnect()
#     cursor = db.cursor(dictionary=True)
#     # sub_category_id = request.json.get('sub_kategori_id')
#     query = "select region_name, department_name, position_name, position.id from position LEFT JOIN department on position.department_id = department.id LEFT JOIN region on department.region_id = region.id"
#     cursor.execute(query,)
#     record = cursor.fetchall()
#     cursor.close()
#     result = dict()
#     temp = dict()
#     # result = record
#     result = [];
#     for x in record:
#         # result[x['id']] = result
#         temp['id'] = x['id']
#         temp['name'] = x['region_name'] + ":" + x['department_name'] + ":" + x['position_name']
#         result.append(temp)
#     # print(result)
#     return jsonify(result)

@cc_blueprint.route('/submit_laporan_data_list', methods=["POST"])
@jwt_required()
def submit_laporan_data_list():
    data = request.json.get('data')
    lat_pelapor = request.json.get('lat_pelapor')
    long_pelapor = request.json.get('long_pelapor')
    tgl_laporan = request.json.get('tgl_laporan')
    sub_kategori_id = request.json.get('sub_kategori_id')
    region_id = request.json.get('region_id')
    department_id = request.json.get('department_id')
    user_id = get_jwt_identity()
    print(data)
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    for x in data:
        query = "INSERT INTO data_laporan (tgl_laporan, user_id, lat_pelapor, long_pelapor, region_id, department_id, data_laporan_subcategory_id, laporan_total, laporan_text, tgl_submitted) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s) " \
                "ON DUPLICATE KEY UPDATE lat_pelapor = %s, long_pelapor = %s, laporan_total = %s, laporan_text = %s"
        cursor.execute(query, (tgl_laporan, user_id, lat_pelapor, long_pelapor, region_id, department_id, x['data_laporan_subcategory_id'],x['laporan_total'],x['laporan_text'], formatted_date, lat_pelapor, long_pelapor,x['laporan_total'],x['laporan_text']))
    result = dict()
    print(tgl_laporan)
    try:
        print("here 999")
        db.commit()
    except mysql.connector.Error as error:
        print("here error")
        print("Failed to update record to database rollback: {}".format(error))
        # reverting changes because of exception
        cursor.rollback()
        result['result'] = 'failed'
        result['valid'] = 2
    finally:
        print("here success")
        cursor.close()
        result['result'] = 'success'
        result['valid'] = 1

    cursor.close()
    return result

@cc_blueprint.route('/print_pdf', methods=["GET"])
def print_pdf():
    print("inside print pdf")
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        # 'custom-header': [
        #     ('Accept-Encoding', 'gzip')
        # ],
        # 'cookie': [
        #     ('cookie-empty-value', '""')
        #     ('cookie-name1', 'cookie-value1'),
        #     ('cookie-name2', 'cookie-value2'),
        # ],
        'no-outline': None,
        'javascript-delay': 5000
    }

    # pdfkit.from_url('https://api.brimob.id/#/report?n=2022-6-08-1-1', 'laporan_siskamtibmas_2022-6-08-1-1.pdf', verbose=True)
    pdfkit.from_url('https://api.brimob.id/#/report?n=1', 'out.pdf')
    # pdfkit.from_url('https://api.brimob.id/#/report?n=1', 'out2.pdf',options=options)
    # pdfkit.from_file('g.html', 'out.pdf')
    return "ok"