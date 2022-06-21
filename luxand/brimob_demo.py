from __future__ import print_function # for compatability with Python 2.x
import sys, math, os.path, base64, pathlib
from fsdk import FSDK
import PIL
from PIL import ImageDraw
# import win

from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))
license_key = environ.get('license_key')

# license_key = "fVrFCzYC5wOtEVspKM/zfLWVcSIZA4RNqx74s+QngdvRiCC7z7MHlSf2w3+OUyAZkTFeD4kSpfVPcRVIqAKWUZzJG975b/P4HNNzpl11edXGIyGrTO/DImoZksDSRs6wktvgr8lnNCB5IukIPV5j/jBKlgL5aqiwSfyCR8UdC9s="
db_filename = "search.db"

print("Initializing FSDK... ", end='')
FSDK.ActivateLibrary(license_key);
FSDK.Initialize()
print("OK\nLicense info:", FSDK.GetLicenseInfo())

FSDK.SetFaceDetectionParameters(True, True, 384)  # HandleArbitraryRotations, DetermineFaceRotationAngle, InternalResizeWidthTrue 384 or 512 value
FSDK.SetFaceDetectionThreshold(3)

for path in pathlib.Path("needle").iterdir():
    # print(path)
    if path.is_file():
        with open(db_filename, 'a+') as db:

            needlepath = os.path.normcase(os.path.abspath(path))
            face_template = FSDK.Image(needlepath).GetFaceTemplate()  # get template of detected face
            ft = base64.b64encode(face_template).decode('utf-8')
            print(needlepath, ft, file=db)
            print(os.path.basename(needlepath), 'is added to the database.')
        # exit(0)

try: # read all photo from database
    with open(db_filename) as db: base = dict(l.rsplit(' ', 1) for l in db if l)
except FileNotFoundError:
    print('\nCannot open', db_filename, 'database file.\nUse "-a" option to create database.'); exit(1)

option = len(sys.argv)==3 and sys.argv[2] or ''
if option not in ('','-a','-r'): print('Unrecognized option:', option); exit(-1)

# FSDK.SetFaceDetectionParameters(True, False, 500)  # HandleArbitraryRotations, DetermineFaceRotationAngle, InternalResizeWidthTrue
# FSDK.SetFaceDetectionThreshold(3)
# 2 baris dibawah originalnya untuk buka file untuk di match
# filename = os.path.normcase(os.path.abspath(sys.argv[1]))
# face_template = FSDK.Image(filename).GetFaceTemplate() # get template of detected face
# gdiplus = win.GDIPlus() # initialize GDI+
top_match = 20 #find n top match

if (os.path.isfile('/output/output.jpeg')):
    print('is file')
    os.remove('./output/output.jpeg')
else:
    print("no-file")


for path in pathlib.Path("haystack").iterdir():
    if path.is_file() and (os.path.basename(path)!= ".gitignore"):
        # current_file = open(path, "r")
        print('\n' + str(path))
        print(os.path.basename(path))
        # current_file.close()
        filename1 = os.path.normcase(path)
        img = FSDK.Image(filename1)
        im = PIL.Image.open(filename1)
        draw = ImageDraw.Draw(im)
        faces = img.DetectMultipleFaces()
        # bmp = win.Bitmap.FromHBITMAP(img.GetHBitmap())
        # graphics = win.Graphics(bmp=bmp).setSmoothing(True)
        # facePen, featurePen = win.Pen(0xffb0b0b0, 5), win.Pen(0xffffff00, 1.8)
        # im.save('output/output.jpeg', quality=95)

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
            print(xl, yl, xr, yr)
            # for p in f: graph.circle(featurePen, p.x, p.y, 3)  # draw features


        for p in faces:
            template = img.GetFaceTemplate(p)
            src = ((n, FSDK.FaceTemplate(*base64.b64decode(ft))) for n, ft in base.items())
            for n, ft in src:
                percent = template.Match(ft) * 100
                if percent > 95 :
                    print(n + " : " + str(percent))
                    draw_features(img.DetectFacialFeatures(p), draw)


        im.save('./output/output.jpeg', quality=95)
        # img.SaveToFile('output/output.jpeg', quality=85)  # save face image to file with given compression quality
        face_template = FSDK.Image(filename1).GetFaceTemplate()  # get template of detected face


a_file = open(db_filename, "w")
a_file.truncate()
a_file.close()