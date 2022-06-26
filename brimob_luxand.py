#!/usr/bin/env python
from __future__ import print_function # for compatability with Python 2.x
import sys, math, os.path, base64, pathlib
from luxand.fsdk import FSDK
from os import environ, path
from dotenv import load_dotenv
import mysql.connector as mysql
from os.path import exists
import PIL
from PIL import ImageDraw
import time


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))
license_key = environ.get('license_key')
FSDK.ActivateLibrary(license_key);
FSDK.Initialize()


class Brimob_Luxand:
    def test(self):
        print("tesT")
        return "test dari brimob luxand"


    def find_match_portrait(db_filename, threshold, haystacks):

        try:  # read all photo from database
            with open(db_filename) as db:
                base = dict(l.rsplit(' ', 1) for l in db if l)
        except FileNotFoundError:
            print('\nCannot open', db_filename, 'database file.\nUse "-a" option to create database.');
            exit(1)

        def draw_features(f,draw):
            def dot_center(dots):  # calc geometric center of dots
                return sum(p.x for p in dots) / len(dots), sum(p.y for p in dots) / len(dots)

            xl, yl = dot_center([f[k] for k in FSDK.FSDKP_LEFT_EYE_SET])
            xr, yr = dot_center([f[k] for k in FSDK.FSDKP_RIGHT_EYE_SET])
            w = (xr - xl) * 2.8
            h = w * 1.4
            center = (xr + xl) / 2, (yr + yl) / 2 + w * 0.05
            angle = math.atan2(yr - yl, xr - xl) * 180 / math.pi
            frame = -w / 2, -h / 2, w / 2, h / 2
            # container = graph.beginContainer()
            # graph.translateTransform(*center).rotateTransform(angle).ellipse(facePen, *frame)  # draw frame
            # graph.endContainer(container)
            draw.rectangle((xl-w/2, yl-h/2, xl+w, yr+h*0.8), fill=None, outline="red")
            # print(xl, yl, xr, yr)
            # for p in f: graph.circle(featurePen, p.x, p.y, 3)  # draw features
        output = dict()
        matches = []
        output['matches'] = []
        for haystack in haystacks:
            haystack_path = os.path.normcase(os.path.abspath(environ.get('UPLOAD_HAYSTACK') + haystack))
            ts = time.time()
            timestamp = os.path.splitext(str(ts))[0]
            if os.path.exists(haystack_path):
                img = FSDK.Image(haystack_path)
                im = PIL.Image.open(haystack_path)
                print("-")
                print(haystack_path)
                print("--")
                draw = ImageDraw.Draw(im)
                faces = img.DetectMultipleFaces()
                # print(faces)
                temp_array = []
                temp_dict = dict()
                temp_portrait = dict()
                temp_match = []
                for p in faces:
                    # print(p)
                    temp2_dict = dict()
                    template = img.GetFaceTemplate(p)
                    src = ((n, FSDK.FaceTemplate(*base64.b64decode(ft))) for n, ft in base.items())
                    for n, ft in src:
                        percent = template.Match(ft) * 100
                        if percent > threshold:
                            print(os.path.basename(n) + " -----> " + str(percent))
                            draw_features(img.DetectFacialFeatures(p), draw)
                            # temp_dict[os.path.basename(n)] = str(percent)
                            temp2_dict["portrait"] = os.path.basename(n)
                            temp2_dict["match_percentage"] = str(percent)
                            temp_match.append(temp2_dict)

                temp_dict["haystack"] = haystack
                temp_dict["match_found"] = temp_match
                matches.append(temp_dict)
                # matches[] = temp_dict
                output_path = os.path.join(environ.get('OUTPUT_FOLDER') + 'output-' + haystack + '-' + timestamp + ".jpg")
                print(output_path)
                draw_features(img.DetectFacialFeatures(p), draw)
                im.save(output_path, quality=95)

                # im.SaveToFile("./putput.jpg", quality=95)
            else:
                print("not exist")
            output['result'] = matches
            output['output_file'] = os.path.basename(output_path)
        return output


    def populate_portrait_db(db_filename, needles):
        # print("Initializing FSDK... ", end='')
        print("OK\nLicense info:", FSDK.GetLicenseInfo())
        FSDK.SetFaceDetectionParameters(True, True, 384)  # HandleArbitraryRotations, DetermineFaceRotationAngle, InternalResizeWidthTrue 384 or 512 value
        FSDK.SetFaceDetectionThreshold(3)
        with open(db_filename, 'a+') as db:
            for needle in needles:
                portrait_path = os.path.normcase(os.path.abspath(environ.get('UPLOAD_PORTRAIT') + needle))
                if os.path.exists(portrait_path):
                    face_template = FSDK.Image(portrait_path).GetFaceTemplate()  # get template of detected face
                    ft = base64.b64encode(face_template).decode('utf-8')
                    print(portrait_path, ft, file=db)
                    print(os.path.basename(portrait_path), 'is added to the database.')
                else :
                    print("not exist")
        return "image mtch result"




    def create_portrait(filepath, outpath):
        basedir = path.abspath(path.dirname(__file__))
        load_dotenv(path.join(basedir, '.env'))
        license_key = environ.get('license_key')

        print("Initializing FSDK... ", end='')
        FSDK.ActivateLibrary(license_key);
        FSDK.Initialize()
        print("OK\nLicense info:", FSDK.GetLicenseInfo())

        print("\nLoading file", filepath , "...")
        file_exists = exists(filepath)
        if file_exists:
            print("EXISTS")
        else:
            print("NO FILE")

        img = FSDK.Image(filepath)  # create image from file
        FSDK.SetFaceDetectionParameters(False, False,
                                        256)  # HandleArbitraryRotations, DetermineFaceRotationAngle, InternalResizeWidth
        FSDK.SetFaceDetectionThreshold(5)

        print("Detecting face...")
        try:
            face = img.DetectFace()  # detect face in the image
        except:
            return 0

        maxWidth, maxHeight = 337, 450
        img = img.Crop(*face.rect).Resize(max((maxWidth + 0.4) / (face.w + 1),
                                              (maxHeight + 0.4) / (face.w + 1)))  # crop and resize face image inplace
        img.SaveToFile(outpath, quality=85)  # save face image to file with given compression quality

        print("File '%s' with detected face is created." % outpath)
        return 1


    def create_portrait_test(file):
        print("inside create portrait")
        basedir = path.abspath(path.dirname(__file__))
        load_dotenv(path.join(basedir, '.env'))
        license_key = environ.get('license_key')

        if len(sys.argv) < 2:
            print("Usage: portrait.py <in_file> [out_file]")  # default out_file name is 'face.in_file'
            exit(-1)

        inputFileName, outFileName = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'face.' + sys.argv[1]

        print("Initializing FSDK... ", end='')
        FSDK.ActivateLibrary(license_key);
        FSDK.Initialize()
        print("OK\nLicense info:", FSDK.GetLicenseInfo())

        print("\nLoading file", inputFileName, "...")
        img = FSDK.Image(inputFileName)  # create image from file
        FSDK.SetFaceDetectionParameters(False, False,
                                        256)  # HandleArbitraryRotations, DetermineFaceRotationAngle, InternalResizeWidth
        FSDK.SetFaceDetectionThreshold(5)

        print("Detecting face...")
        face = img.DetectFace()  # detect face in the image

        maxWidth, maxHeight = 337, 450
        img = img.Crop(*face.rect).Resize(max((maxWidth + 0.4) / (face.w + 1),
                                              (maxHeight + 0.4) / (face.w + 1)))  # crop and resize face image inplace
        img.SaveToFile(outFileName, quality=85)  # save face image to file with given compression quality

        print("File '%s' with detected face is created." % outFileName)
        return "success"