from flask import Blueprint
import time
from datetime import date
import os
import json
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


class Stats:
    def stats_most_active_region(region_id):
        result = dict()
        result['stat_name'] = "most active region"
        result['stat_value'] = "Aceh"
        return result

    def stats_most_active_user(region_id):
        result = dict()
        result['stat_name'] = "most active user"
        result['stat_value'] = "zenner"
        return result
