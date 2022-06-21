from __future__ import print_function # for compatability with Python 2.x
import sys, os.path, base64, pathlib
from fsdk import FSDK
import os
import glob
import ffmpeg

from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))
license_key = environ.get('license_key')

db_filename = "search.db"

# fps = 1 --> i frame per sec
# ffmpeg -i .\video1.mp4 -filter:v fps=fps=1 thumb%04d.jpg

print("Initializing FSDK... ", end='')
FSDK.ActivateLibrary(license_key);
FSDK.Initialize()
print("OK\nLicense info:", FSDK.GetLicenseInfo())

for path in pathlib.Path("needle-video").iterdir():
    print(path)
    if path.is_file():
        # print(path)
        with open(db_filename, 'a+') as db:
            FSDK.SetFaceDetectionParameters(True, True,384)  # HandleArbitraryRotations, DetermineFaceRotationAngle, InternalResizeWidthTrue
            FSDK.SetFaceDetectionThreshold(3)
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

FSDK.SetFaceDetectionParameters(True, True, 384)  # HandleArbitraryRotations, DetermineFaceRotationAngle, InternalResizeWidthTrue
FSDK.SetFaceDetectionThreshold(3)


top_match = 20 #find n top match
for path in pathlib.Path("haystack-video").iterdir():
    if path.is_file():
        print('\n' + str(path))
        # ffmpeg -i .\video1.mp4 -filter:v fps=fps=1 thumb%04d.jpg
        (
            ffmpeg
                .input(path)
                .filter('fps', fps=1, round='up')
                .output('videoframestemp/frame%04d.jpg')
                # .hflip()
                # .output('output.mp4')
                .run()
        )

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
            
        for path in pathlib.Path("videoframestemp").iterdir():
            if path.is_file():

                print('\n' + str(path))

                filename1 = os.path.normcase(path)
                try:
                    face_template = FSDK.Image(filename1).GetFaceTemplate()  # get template of detected face
                    src = ((n, FSDK.FaceTemplate(*base64.b64decode(ft))) for n, ft in base.items())
                    matches = sorted(((face_template.Match(ft) * 100, n) for n, ft in src), reverse=True)[:top_match]
                    print('Found similarities:', len(matches) or None)
                    for match in matches:
                        print('%i%%\t%s' % match)
                    # print(current_file.read())
                except:
                    # print('no face found')
                    pass



a_file = open(db_filename, "w")
a_file.truncate()
a_file.close()

files = glob.glob('videoframestemp/*')
# for f in files:
#     os.remove(f)