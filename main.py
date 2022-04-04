import math
import os
import time
import mobile
import cc
from mrun import MRun
from dbconfig import DBConfig
from flask import send_from_directory
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
from flask import request, flash, request, redirect, url_for
from flask_cors import CORS

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from mobile import mobile_blueprint
from cc import cc_blueprint
from admin import admin_blueprint
from sqlalchemy import create_engine
from werkzeug.utils import secure_filename
from flask import Blueprint


import logging


app = Flask(__name__)
CORS(app)
app.register_blueprint(mobile_blueprint)
app.register_blueprint(cc_blueprint)
app.register_blueprint(admin_blueprint)

logging.basicConfig(filename='record.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
jwt = JWTManager(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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


@app.route('/upload', methods=['GET', 'POST'])
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
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(os.path.join(app.config['UPLOAD_FOLDER']))
            ts = time.time()
            newfilename = str(user_id) + "-" + os.path.splitext(str(ts))[0] + os.path.splitext(filename)[1]

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], newfilename))
            res['valid'] = '2'
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

@app.route('/test')
def test():
    ret = MRun.get_polda_no_cc()
    return ret





@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)








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
