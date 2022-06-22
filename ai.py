import os
import os.path
from flask import Blueprint
from dbconfig import DBConfig
# from werkzeug.security import safe_str_cmp
import mysql.connector as mysql
from flask import Flask
from flask import jsonify
from werkzeug.utils import secure_filename
import time

from datetime import datetime


from flask import send_from_directory
from flask import flash, request, redirect
from os import environ, path
from dotenv import load_dotenv


# sys.path.insert(0, '/luxand')
from brimob_luxand import Brimob_Luxand

ALLOWED_VIDEO_EXTENSIONS = {'mp4'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}



app = Flask(__name__)

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))
license_key = environ.get('license_key')


app.config['UPLOAD_PORTRAIT'] = environ.get('UPLOAD_PORTRAIT')
app.config['UPLOAD_ORIGINALPORTRAIT'] = environ.get('UPLOAD_ORIGINALPORTRAIT')
app.config['UPLOAD_HAYSTACK'] = environ.get('UPLOAD_HAYSTACK')




dbObj = DBConfig()
db = dbObj.connect()

ai_blueprint = Blueprint('ai_blueprint', __name__, url_prefix="/ai")

def allowed_video_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

def allowed_image_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

@ai_blueprint.route('/test', methods=["POST"])
# @jwt_required()
def test(self=None):
    res = dict()
    res = Brimob_Luxand.test(self)
    return res


@ai_blueprint.route('/list_portrait', methods=["GET"])
def list_portrait():
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    query = "SELECT id, original_filename, portrait_filename, ai_portrait_uploads.group,  tags, created_at, modified_at from ai_portrait_uploads"
    cursor.execute(query,)
    record = cursor.fetchall()
    cursor.close()
    res = dict()
    res = record
    return jsonify(res)


@ai_blueprint.route('/download_portrait/<name>')
def download_portrait(name):
    return send_from_directory(app.config["UPLOAD_PORTRAIT"], name)


@ai_blueprint.route('/upload_portrait', methods=["POST"])
def upload_portrait():
    print ("uplaod portrait")
    res = dict()
    if request.method == 'POST':
        # check if the post request has the uuuuu part
        if 'file' not in request.files:
            print('no file part')
            return redirect(request.url)

        file = request.files['file']
        # Brimob_Luxand.create_portrait(file)
        # print(request.form['laporan_no'])
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print("no selected file")
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_image_file(file.filename):
            print("here")
            filename = secure_filename(file.filename)
            # print(os.path.join(app.config['UPLOAD_GIATHARIAN_FOLDER']))
            ts = time.time()
            # newfilename = str(user_id) + "-" + str(laporan_subkategori_id) + "-" + str(laporan_no) + "-" + os.path.splitext(str(ts))[0] + os.path.splitext(filename)[1]
            originalfilename = os.path.splitext(str(ts))[0]
            newfilename = "portrait-" + os.path.splitext(str(ts))[0]
            extension = os.path.splitext(filename)[1]
            original_name = "original-" + originalfilename.lower() + extension.lower()
            newfilename_ext = newfilename.lower() + extension.lower()
            # print(app.config['UPLOAD_PORTRAIT'])

            file.save(os.path.join(app.config['UPLOAD_ORIGINALPORTRAIT']  + original_name))
            file.close()

            create_portrait_result = Brimob_Luxand.create_portrait(os.path.join(app.config['UPLOAD_ORIGINALPORTRAIT']  + original_name), os.path.join(app.config['UPLOAD_PORTRAIT']  + newfilename_ext))


            # portrait_file.save(os.path.join(app.config['UPLOAD_PORTRAIT'] + "/" + newfilename_ext))
            # file.close()
            # portrait_file.close()
            print(newfilename_ext)
            result = dict()
            if create_portrait_result:
                db.reconnect()
                cursor = db.cursor(dictionary=True)
                group = ""
                tags = ""
                now = datetime.now()
                formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
                query = "INSERT INTO ai_portrait_uploads (original_filename, portrait_filename, ai_portrait_uploads.group, tags, created_at) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (original_name, newfilename_ext, group, tags, formatted_date))


                try:
                    db.commit()
                    result['result'] = 'success'
                    result['valid'] = 1
                except mysql.connector.Error as error:
                    print("Failed to update record to database rollback: {}".format(error))
                    # reverting changes because of exception
                    cursor.rollback()
                    result['result'] = 'failed'
                    result['valid'] = 2
                finally:
                    cursor.close()

            else:
                result['result'] = 'face detect failed'
                result['valid'] = 2
                os.remove(os.path.join(app.config['UPLOAD_ORIGINALPORTRAIT']  + original_name))
            return result

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@ai_blueprint.route('/find_match_portrait', methods=["POST"])
def find_match_portrait():
    portraits = request.json.get("portraits", None)
    haystacks = request.json.get("haystacks", None)

    for haystack in haystacks:
        print(haystack)

    print(portraits)
    print(haystacks)

    return ""

@ai_blueprint.route('/list_haystack', methods=["GET"])
def list_haystack():
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    query = "SELECT id, filename, ai_haystack_uploads.group,  tags, created_at, modified_at from ai_haystack_uploads"
    cursor.execute(query,)
    record = cursor.fetchall()
    cursor.close()
    res = dict()
    res = record
    return jsonify(res)

@ai_blueprint.route('/remove_haystack', methods=["GET", "POST"])
def remove_haystack():
    res = dict()
    filenames = request.json.get('filenames')
    db.reconnect()
    cursor = db.cursor(dictionary=True)

    for filename in filenames:
        print(filename)
        query = 'DELETE FROM ai_haystack_uploads WHERE filename = %s'
        cursor.execute(query, (filename,))
        db.commit()
        os.remove(app.config['UPLOAD_HAYSTACK'] + "/" + filename)

    cursor.close()
    res['result'] = 'success'
    res['valid'] = 1
    return res

@ai_blueprint.route('/remove_portrait', methods=["GET", "POST"])
def remove_portrait():
    res = dict()
    filenames = request.json.get('filenames')
    db.reconnect()
    cursor = db.cursor(dictionary=True)

    for filename in filenames:
        print(filename)
        query = 'DELETE FROM ai_portrait_uploads WHERE portrait_filename = %s'
        cursor.execute(query, (filename,))
        db.commit()
        os.remove(app.config['UPLOAD_PORTRAIT'] + "/" + filename)
    cursor.close()
    res['result'] = 'success'
    res['valid'] = 1
    return res


@ai_blueprint.route('/remove_original_portrait', methods=["GET", "POST"])
def remove_original_portrait():
    res = dict()
    filenames = request.json.get('filenames')
    db.reconnect()
    cursor = db.cursor(dictionary=True)

    for filename in filenames:
        print(filename)
        query = 'DELETE FROM ai_portrait_uploads WHERE original_filename = %s'
        cursor.execute(query, (filename,))
        db.commit()
        os.remove(app.config['UPLOAD_PORTRAITORIGINAL'] + "/" + filename)
    cursor.close()
    res['result'] = 'success'
    res['valid'] = 1
    return res




@ai_blueprint.route('/download_haystack/<name>')
def download_haystack(name):
    return send_from_directory(app.config["UPLOAD_HAYSTACK"], name)

@ai_blueprint.route('/upload_haystack', methods=["POST"])
def upload_haystack():
    res = dict()
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file part haystack')
            return redirect(request.url)

        file = request.files['file']
        # Brimob_Luxand.create_portrait(file)
        # print(request.form['laporan_no'])
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print("no selected file")
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_image_file(file.filename):

            filename = secure_filename(file.filename)
            # print(os.path.join(app.config['UPLOAD_GIATHARIAN_FOLDER']))
            ts = time.time()
            # newfilename = str(user_id) + "-" + str(laporan_subkategori_id) + "-" + str(laporan_no) + "-" + os.path.splitext(str(ts))[0] + os.path.splitext(filename)[1]
            newfilename = "haystack-" + os.path.splitext(str(ts))[0]
            extension = os.path.splitext(filename)[1]
            newfilename_ext = newfilename.lower() + extension.lower()
            file.save(os.path.join(app.config['UPLOAD_HAYSTACK'] + "/" + newfilename_ext))
            print(newfilename_ext)

            db.reconnect()
            cursor = db.cursor(dictionary=True)
            group = ""
            tags = ""
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
            query = "INSERT INTO ai_haystack_uploads (filename, ai_haystack_uploads.group, tags, created_at) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (newfilename_ext, group, tags, formatted_date))

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

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''



