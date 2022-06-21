from __future__ import print_function # for compatability with Python 2.x
import sys, os.path, base64
from fsdk import FSDK

from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))
license_key = environ.get('license_key')

db_filename = "faces.db"

if len(sys.argv) not in (2, 3):
	print('\nUsage: lookalikes.py <image_file> [option]')
	print('Options:')
	print('\t-a\tadd photo to database')
	print('\t-r\tremove photo from database')
	exit(-1)

filename = os.path.normcase(os.path.abspath(sys.argv[1]))
option = len(sys.argv)==3 and sys.argv[2] or ''
if option not in ('','-a','-r'): print('Unrecognized option:', option); exit(-1)

print("Initializing FSDK... ", end='')
FSDK.ActivateLibrary(license_key); 
FSDK.Initialize()
print("OK\nLicense info:", FSDK.GetLicenseInfo())

FSDK.SetFaceDetectionParameters(True, True, 384)  # HandleArbitraryRotations, DetermineFaceRotationAngle, InternalResizeWidthTrue
FSDK.SetFaceDetectionThreshold(3)
face_template = FSDK.Image(filename).GetFaceTemplate() # get template of detected face

if option=='-a': # add photo to database
	with open(db_filename, 'a+') as db:
		ft = base64.b64encode(face_template).decode('utf-8')
		print(filename, ft, file=db)
		print(os.path.basename(filename), 'is added to the database.')
	exit(0)

try: # read all photo from database
	with open(db_filename) as db: base = dict(l.rsplit(' ', 1) for l in db if l)
except FileNotFoundError:
	print('\nCannot open', db_filename, 'database file.\nUse "-a" option to create database.'); exit(1)

if option == '-r': # remove photo from database
	if filename in base:
		del base[filename]
		with open(db_filename, 'w') as db:
			for n in base: print(n, base[n], file=db)
		print(filename, 'is removed from database.')
	else: print(filename, 'is not found in database.')
	exit(0)
