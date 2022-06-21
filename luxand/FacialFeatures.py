from __future__ import print_function # for compatability with Python 2.x
import sys, fsdk, math
from fsdk import FSDK
if not fsdk.windows:
	print('This program requiers to be run under Microsoft Windows.'); exit(1)
import win


from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))
license_key = environ.get('license_key')


if len(sys.argv) < 2:
	print("Usage: facial-features.py <in_file> [out_file]") # default out_file name is 'features.in_file.jpeg'
	exit(0)

inputFileName, outFileName = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'features.'+sys.argv[1]

print("Initializing FSDK... ", end='')
FSDK.ActivateLibrary(license_key); 
FSDK.Initialize()
print("OK\nLicense info:", FSDK.GetLicenseInfo())

print("\nLoading file", inputFileName, "...")
img = FSDK.Image(inputFileName) # create image from file
FSDK.SetFaceDetectionParameters(True, True, 2000) # HandleArbitraryRotations, DetermineFaceRotationAngle, InternalResizeWidthTrue
FSDK.SetFaceDetectionThreshold(5)

print("Detecting faces...")
faces = img.DetectMultipleFaces() # detect all faces in the image
if faces:
	print(len(faces), "face(s) found")
	for face in faces:
		print(face)
else:
	print("No faces found")
	exit(1)

gdiplus = win.GDIPlus() # initialize GDI+
bmp = win.Bitmap.FromHBITMAP(img.GetHBitmap())
graphics = win.Graphics(bmp=bmp).setSmoothing(True)
facePen, featurePen = win.Pen(0xffb0b0b0, 5), win.Pen(0xffffff00, 1.8)

def draw_features(graph, f):
	def dot_center(dots): # calc geometric center of dots
		return sum(p.x for p in dots)/len(dots), sum(p.y for p in dots)/len(dots)
	xl, yl = dot_center([f[k] for k in FSDK.FSDKP_LEFT_EYE_SET])
	xr, yr = dot_center([f[k] for k in FSDK.FSDKP_RIGHT_EYE_SET])
	w = (xr - xl)*2.8
	h = w*1.4
	center = (xr + xl)/2, (yr + yl)/2 + w*0.05
	angle = math.atan2(yr-yl, xr-xl)*180/math.pi
	frame = -w/2, -h/2, w/2, h/2
	container = graph.beginContainer()
	graph.translateTransform(*center).rotateTransform(angle).ellipse(facePen, *frame) # draw frame
	graph.endContainer(container)
	for p in f: graph.circle(featurePen, p.x, p.y, 3) # draw features

for p in faces:
	template = img.GetFaceTemplate(p)
	draw_features(graphics, img.DetectFacialFeatures(p))
del graphics

img = FSDK.Image(bmp.GetHBITMAP())
img.SaveToFile(outFileName, quality = 85) # save face image to file with given compression quality

print("File '%s' with detected facial features is created." % outFileName)
