from __future__ import print_function # for compatability with Python 2.x
import sys
from fsdk import FSDK

from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))
license_key = environ.get('license_key')

if len(sys.argv) < 2:
	print("Usage: portrait.py <in_file> [out_file]") # default out_file name is 'face.in_file'
	exit(-1)

inputFileName, outFileName = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'face.'+sys.argv[1]

print("Initializing FSDK... ", end='')
FSDK.ActivateLibrary(license_key); 
FSDK.Initialize()
print("OK\nLicense info:", FSDK.GetLicenseInfo())

print("\nLoading file", inputFileName, "...")
img = FSDK.Image(inputFileName) # create image from file
FSDK.SetFaceDetectionParameters(False, False, 256) # HandleArbitraryRotations, DetermineFaceRotationAngle, InternalResizeWidth
FSDK.SetFaceDetectionThreshold(5)

print("Detecting face...")
face = img.DetectFace() # detect face in the image

maxWidth, maxHeight = 337, 450
img = img.Crop(*face.rect).Resize(max((maxWidth+0.4)/(face.w+1), (maxHeight+0.4)/(face.w+1))) # crop and resize face image inplace
img.SaveToFile(outFileName, quality = 85) # save face image to file with given compression quality

print("File '%s' with detected face is created." % outFileName)

