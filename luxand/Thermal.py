from __future__ import print_function # for compatability with Python 2.x
import sys
from fsdk import FSDK

license_key = "GQhpyOPlWh/TE2tYXrlNYc3gDXNlvp9jpQMtdLCoDsDfSk0bIGeM2EK7f6pllPxKbMvgF7npGj3lHBSw0Ik/9PzNK1XT+NH2uNYCW4qoiexEeCryVCqNGpUFhBWxCDqWwrUVBX+u9iuExcIRZUAUyblQ9WiOTY9a6yhSg/nxlSw="

if len(sys.argv) < 2:
	print("Usage: portrait.py <in_file> [out_file]") # default out_file name is 'face.in_file'
	exit(-1)

inputFileName, outFileName = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'face.' + sys.argv[1]

print("Initializing FSDK... ", end='')
FSDK.ActivateLibrary(license_key); 
FSDK.Initialize()
print("OK\nLicense info:", FSDK.GetLicenseInfo())

print("\nLoading file", inputFileName, "...")
img = FSDK.Image(inputFileName) # create image from file
FSDK.SetFaceDetectionParameters(True, True, 256) # HandleArbitraryRotations, DetermineFaceRotationAngle, InternalResizeWidthTrue
FSDK.SetFaceDetectionThreshold(5)
FSDK.SetParameters(FaceDetectionModel='thermal.bin', TrimOutOfScreenFaces=False, TrimFacesWithUncertainFacialFeatures=False) # load weights for thermal detection and disable face trimming

print("Detecting face...")
face = img.DetectFace() # detect face in the image

maxWidth, maxHeight = 337, 450
img = img.Crop(*face.rect).Resize(max((maxWidth+0.4)/(face.w+1), (maxHeight+0.4)/(face.w+1))) # crop and resize face image inplace
img.SaveToFile(outFileName, quality = 85) # save face image to file with given compression quality

print("File '%s' with detected face is created." % outFileName)
