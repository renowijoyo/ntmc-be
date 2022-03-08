#!/usr/bin/env python
from dbconfig import DBConfig
import json
from flask import Flask
from flask import jsonify

dbObj = DBConfig()
db = dbObj.connect()

class MRun:

    def get_polda_no_cc(self):
        cursor = db.cursor(dictionary=True)
        # get the last rate & feedback - the latest ID
        query = "SELECT id, rate, feedback FROM report_rate ORDER BY id DESC"

        cursor.execute(query)
        record = cursor.fetchall()
        res = dict()
        res['list'] = record
        # $query = "SELECT idpolda,polda FROM polda WHERE polda LIKE 'POLDA%' OR polda LIKE 'KORLANTAS POLRI' ORDER BY polda ASC";
        # $result = $this->db->query($query);
        # return $result->result_array();
        cursor.close()
        return res

    def get_satwil(self):
        return
    def get_detail_mobile(self):
        return
    def get_work_order_detail(self):
        return
    def get_penanganan_byId(self):
        return
