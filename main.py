import os

import mobile
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

from flask import Blueprint


import logging




app = Flask(__name__)
CORS(app)

logging.basicConfig(filename='record.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)




dbObj = DBConfig()
db = dbObj.connect()
def __init__(self):
    self.data = dict()


MRun = MRun()


@app.route('/test')
def test():
    ret = MRun.get_polda_no_cc()
    return ret

@app.route('/load_video_banner')
def load_video_banner():

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


@app.route('/load_banner_news')
def load_banner_news():

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


@app.route('/warga_get_history', methods=["POST"])
@jwt_required()
def warga_get_history():
    id = request.json.get('id', None)

    cursor = db.cursor(dictionary=True)

    query = "SELECT detail_penanganan, nama_petugas, DATE_FORMAT(tanggal, '%Y-%m-%d %T') tanggal FROM penanganan WHERE work_order_id = %s ORDER BY tanggal DESC"


    ## getting records from the table
    cursor.execute(query, (id,))
    record = cursor.fetchall()
    cursor.close()

    res = dict()
    res['list'] = record
    res['valid'] = 1

    return res

@app.route('/check_rate', methods=["POST"])
@jwt_required()
def check_rate():
    id = request.json.get('idworkorder', None)
    cursor = db.cursor(dictionary=True)
    # get the last rate & feedback - the latest ID
    query = "SELECT id, rate, feedback FROM report_rate WHERE idworkorder = %s ORDER BY id DESC"

    cursor.execute(query, (id,))
    record = cursor.fetchall()
    res = dict()
    if len(record) > 0:
        res['rate'] = record[0]['rate']
        res['feedback'] = record[0]['feedback']
    else:
        res['rate'] = 0
        res['feedback'] = ""
    cursor.close()
    return res

@app.route('/warga_get_picturesolve',methods=["POST"])
@jwt_required()
def warga_get_picturesolve():
    id = request.json.get('id')
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

@app.route('/rate_this', methods=["POST"])
@jwt_required()
def rate_this():
    idworkorder = request.json.get('idworkorder', None)
    rate = request.json.get('rate', None)
    feedback = request.json.get('feedback', None)

    cursor = db.cursor(dictionary=True)
    # get the last rate & feedback - the latest ID
    query = "INSERT INTO report_rate (idworkorder, rate, feedback) VALUES (%s, %s, %s)"
    cursor.execute(query, (idworkorder, rate, feedback,))
    db.commit()
    cursor.close()
    # record = cursor.fetchall()
    res = dict()
    # res['list'] = record
    res['valid'] = 1
    return res


@app.route('/warga_get_mail', methods=["POST"])
@jwt_required()
def warga_get_mail():
    username = request.json.get('username', None)
#originalnya ada 3 query execution di satu API call ini
    cursor = db.cursor(dictionary=True)
    # query = "SELECT id_user_mobile, nama FROM user_mobile WHERE email = %s"
    # query2 = "SELECT id_user_mobile FROM work_order WHERE id_user_mobile = '5513'"
    query3 = "SELECT * from work_order WHERE id_user_mobile IN (select id_user_mobile from user_mobile where email = %s)"

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
                 "satwil.satwil AS 'Satuan Wilayah', " \
                 "kategori.kategori AS 'Kategori', " \
                 "subkategori.sub_kategori AS 'SubKategori', " \
                 "user.username AS 'User Creator', " \
                 "pengaduan AS 'Pengaduan', IF(STATUS=1,'Open', IF(STATUS=2,'Received', IF(STATUS=3,'On Process', IF(STATUS=4,'Done','')))) AS STATUS " \
                 "from work_order LEFT JOIN satwil ON satwil.idsatwil = work_order.satwil_id " \
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

@app.route('/warga_get_category')
def warga_get_category():
    cursor = db.cursor(dictionary=True)
    query = "SELECT idsubkategori AS 'id', sub_kategori AS 'name', icon, nomor FROM subkategori WHERE kategori_id = %s ORDER BY nomor ASC"
    cursor.execute(query, ('2',))
    record = cursor.fetchall()
    res = dict()
    res['list'] = record
    res['valid'] = 1
    cursor.close()
    return res

@app.route('/save_token',methods=["POST"])
@jwt_required()
def save_token():
    username = request.json.get('username')
    token = request.json.get('token')


    stamp2 = datetime.now()

    stamp = stamp2.strftime("%Y-%m-%d %H:%M:%S")

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

@app.route('/warga_idle', methods=["POST"])
@jwt_required()
def warga_idle():
    username = request.json.get('username', None)
    if (username == "") :
        valid = 0
        name = ""
    else :
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


@app.route('/warga_save_report', methods=["POST"])
@jwt_required()
def warga_save_report():
    username = request.json.get("username", None)
    address = request.json.get("address", None)
    lat = request.json.get('lat', None)
    lon = request.json.get('lon', None)
    id_cat = request.json.get('id_cat', None)
    detail = request.json.get('detail', None)
    picture = request.json.get('picture', None)

    cursor = db.cursor(dictionary=True)
    query = "SELECT id_user_mobile, ktp, telepon, alamat, nama FROM user_mobile WHERE email = %s"
    cursor.execute(query, (username,))
    record = cursor.fetchall()
    # res = dict()
    valid = 0
    if len(record) > 0 :
        valid = 1
        status = 1
        id_creator = 561
        nama_pelapor = record[0]['nama']
        telp_pelapor = record[0]['telepon']
        id_user_mobile = record[0]['id_user_mobile']
        stamp2 = datetime.now()
        no_pengaduan = stamp2.strftime("%Y%m%d%H%M%S")
        stamp = stamp2.strftime("%Y-%m-%d %H:%M:%S")


        query = "INSERT INTO work_order (no_pengaduan, nama_pelapor, telp_pelapor, alamat_pelapor, lat_pelapor, " \
                "long_pelapor, tgl_kontak, sub_kategori_id, status, user_id, id_user_mobile, pengaduan) " \
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (no_pengaduan, nama_pelapor,telp_pelapor,address, lat, lon, stamp, id_cat,
                               status, id_creator, id_user_mobile, detail,))
        db.commit()
    # print(len(record))
    res = dict()
    res['list'] = record
    res['valid'] = valid
    cursor.close()
    return res

@app.route('/warga_setpass', methods=["POST"])
@jwt_required()
def warga_setpass():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    ol_password = request.json.get('ol_password')

    cursor = db.cursor(dictionary=True)
    query = "SELECT id_user_mobile,nama, password FROM user_mobile WHERE email = %s"
    cursor.execute(query, (username,))
    record = cursor.fetchall()
    valid = 0
    if (len(record) > 0):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)

        if bcrypt.checkpw(ol_password.encode(), (record[0]['password']).encode()):
            valid = 1

            query = "UPDATE user_mobile SET password =  %s WHERE email= %s"
            cursor.execute(query, (hashed,username,))
            db.commit()
        else:
            valid = 0

    else:
        valid = 0

    res = dict()
    res['valid'] = valid
    cursor.close()
    return res


@app.route('/warga_login', methods=["POST"])
def warga_login():
    # username = request.args.get('username')
    # password = request.args.get('password')
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    res = authenticate(username, password)
    # cursor.close()
    return res




@app.route('/verify', methods=["POST"])
@jwt_required()
def verify():
    email = request.json.get('email')
    passwd = request.json.get('pass')
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

@app.route('/login_user', methods=["POST"])
def login_user():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    res = authenticate_user(username, password)
    return res




@app.route('/simpan_user', methods=["POST"])
def simpan_user():
    username = request.json.get('username')
    password = request.json.get('password')
    level_user = request.json.get('level_user')
    satwil_id = request.json.get('satwil')
    polda_id = request.json.get('polda')

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
        query = "INSERT INTO user (username, password, level_user, satwil_id, polda_id " \
                ") " \
                "VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (username, hashed,level_user,satwil_id, polda_id,))
        db.commit()
    res = dict()
    res['valid'] = valid
    cursor.close()
    return res


@app.route('/warga_reg', methods=["POST"])
def warga_reg():
    email = request.json.get('email')
    passwd = request.json.get('pass')
    name = request.json.get('name')
    ktp = request.json.get('ktp')
    ktppic = request.json.get('ktppic')
    detail = request.json.get('detail')
    hp = request.json.get('hp')
    address = request.json.get('alamat')
    cursor = db.cursor(dictionary=True)
    query = "SELECT id_user_mobile,password FROM user_mobile WHERE email = %s"
    cursor.execute(query, (email,))
    record = cursor.fetchall()
    valid = 0

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(passwd.encode(), salt)

    if (len(record) > 0):
        valid = 2
    else:
        valid = 1
        query = "INSERT INTO user_mobile (nama, ktp, ktppic, email, password, " \
                "telepon, alamat, user_status) " \
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (name, ktp,ktppic,email, hashed, hp, address, 1,))
        db.commit()
    res = dict()
    res['valid'] = valid
    cursor.close()
    return res

def authenticate_user(username, password):
    cursor = db.cursor(dictionary=True)
    query = "SELECT iduser,username,password, level_user, satwil_id, polda_id FROM user WHERE username = %s"
    cursor.execute(query, (username,))
    record = cursor.fetchall()
    cursor.close()
    level_user = ''
    satwil = ''
    polda = ''
    valid = 0
    if (len(record) > 0):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)

        if bcrypt.checkpw(password.encode(), (record[0]['password']).encode()):
            valid = 1
            token = username
            access_token = create_access_token(identity=username)
            name = record[0]['username']
            level_user = record[0]['level_user']
            satwil = record[0]['satwil_id']
            polda = record[0]['polda_id']

            return jsonify(token=access_token, name=name, level_user=level_user, satwil=satwil, polda=polda,valid=valid)

        else:
            valid = 2
            token = ""
            name = ""
    else:
        valid = 2
        token = ""
        name = ""
    res = dict()
    res['valid'] = valid
    res['username'] = name
    res['level_user'] = level_user
    res['satwil'] = satwil
    res['polda'] = polda
    res['token'] = token

    return res

def authenticate(username, password):
    cursor = db.cursor(dictionary=True)
    query = "SELECT id_user_mobile,nama, password FROM user_mobile WHERE email = %s"
    cursor.execute(query, (username,))
    record = cursor.fetchall()
    cursor.close()
    valid = ''
    name = ''
    token = ''
    valid = 0
    if (len(record) > 0):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)

        if bcrypt.checkpw(password.encode(), (record[0]['password']).encode()):
            valid = 1
            token = username
            access_token = create_access_token(identity=username)
            name = record[0]['nama']
            return jsonify(token=access_token, name=name, valid=valid)

        else:
            valid = 2
            token = ""
            name = ""
    else:
        valid = 2
        token = ""
        name = ""
    res = dict()
    res['valid'] = valid
    res['name'] = name
    res['token'] = token

    return res




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
