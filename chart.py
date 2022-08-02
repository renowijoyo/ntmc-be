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
chart_blueprint = Blueprint('chart_blueprint', __name__, url_prefix="/chart")


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'mysql_db'):
        g.mysql_db = dbObj.connect()
    return g.mysql_db


@chart_blueprint.route('/filtered', methods=["GET"])
def filtered():
    db = get_db()
    cursor = db.cursor(dictionary=True)


    idpolda = request.args.get('idpolda')
    tahun = request.args.get('tahun')
    bulan = request.args.get('bulan')

    if(idpolda is not None):
        show_polda = " AND polda_id=" + idpolda
    else :
        show_polda = ""
    if(bulan is not None):
        show_bulan = " AND MONTH(tgl_kontak)=" + bulan
    else :
        show_bulan = ""
    if(tahun is not None):
        show_tahun = " AND YEAR(tgl_kontak)=" + tahun
    else :
        show_tahun = ""

    query = "select status, COUNT(idworkorder) AS itung_received FROM work_order LEFT JOIN satwil ON satwil.idsatwil = work_order.satwil_id " \
            "LEFT JOIN polda ON polda.idpolda = satwil.polda_id " \
            "LEFT JOIN subkategori ON subkategori.idsubkategori = work_order.sub_kategori_id " \
            "LEFT JOIN kategori ON kategori.idkategori = subkategori.kategori_id " \
            "where kategori_id = 2 " + show_polda + show_bulan + show_tahun + " group by status"

    query2 = "SELECT polda_id,satwil_id,kategori_id,sub_kategori, COUNT(*) AS itungan FROM work_order " \
             "LEFT JOIN subkategori ON subkategori.idsubkategori = work_order.sub_kategori_id " \
             "LEFT JOIN satwil ON satwil.idsatwil = work_order.satwil_id " \
             "WHERE sub_kategori_id IS NOT NULL " + show_polda + show_bulan + show_tahun + " GROUP BY sub_kategori_id"


    cursor.execute(query)
    records = cursor.fetchall()
    result = dict()

    result['kasus_open'] = []
    result['kasus_receieved'] = []
    result['kasus_on_process'] = []
    result['kasus_done'] = []

    flag_1 = 0
    flag_2 = 0
    flag_3 = 0
    flag_4 = 0

    # result['list'] = records

    for record in records:
        if (record['status'] == 1):
            flag_1 = 1
            result['kasus_open'].append({'itung_open' : record['itung_received']})
        if (record['status'] == 2):
            flag_2 = 1
            result['kasus_receieved'].append({'itung_received' : record['itung_received']})
        if (record['status'] == 3):
            flag_3 = 1
            result['kasus_on_process'].append({'itung_on_process' : record['itung_received']})
        if (record['status'] == 4):
            flag_4 = 1
            result['kasus_done'].append({'itung_done' : record['itung_received']})

    if flag_1 == 0:
        result['kasus_open'].append({'itung_open': 0})
    if flag_2 == 0:
        result['kasus_receieved'].append({'itung_received': 0})
    if flag_3 == 0:
        result['kasus_on_process'].append({'itung_on_process': 0})
    if flag_4 == 0:
        result['kasus_done'].append({'itung_done': 0})
    # for record in records:
    #     if (record['status'] == 1):
    #         result['kasus_open'].append(record['itung_received'])
    #     if (record['status'] == 2):
    #         result['kasus_receieved'] = record['itung_received']
    #     if (record['status'] == 3):
    #         result['kasus_on_process'] = record['itung_received']
    #     if (record['status'] == 4):
    #         result['kasus_done'] = record['itung_received']


    cursor.execute(query2)
    records2 = cursor.fetchall()

    tahun = now.strftime('%Y')

    query3 = "SELECT DATE_FORMAT(tgl_kontak,'%b') as 'bulan', COUNT(*) AS itungan FROM work_order LEFT JOIN subkategori ON subkategori.idsubkategori = work_order.sub_kategori_id WHERE YEAR(tgl_kontak) = " + tahun+" GROUP BY MONTH(tgl_kontak)"

    cursor.execute(query3)
    records3 = cursor.fetchall()

    query4 = "SELECT subkategori.sub_kategori,COUNT(*) AS itungan FROM work_order LEFT JOIN subkategori ON subkategori.idsubkategori = work_order.sub_kategori_id WHERE YEAR(tgl_kontak) = " + tahun+" AND sub_kategori IS NOT NULL GROUP BY subkategori.idsubkategori ORDER BY itungan DESC LIMIT 5"

    cursor.execute(query4)
    records4 = cursor.fetchall()

    query5 = "SELECT polda from polda where idpolda = %s"
    cursor.execute(query5, (idpolda,))
    records5 = cursor.fetchall()
    if (cursor.rowcount > 0):
        result['wilayah'] = records5[0]['polda']



    result['report_kategori_global'] = records2
    result['report_kategori_perbulan'] = records3
    result['report_kategori_perkategori'] = records4


    return jsonify(result)


