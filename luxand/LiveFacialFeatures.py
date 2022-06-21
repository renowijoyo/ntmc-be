from __future__ import print_function
import sys, fsdk, math
from fsdk import FSDK


from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))
license_key = environ.get('license_key')


if not fsdk.windows:
	print('The program is for Microsoft Windows.'); exit(1)
import win

FONT_SIZE = 30

print("Initializing FSDK... ", end='')
FSDK.ActivateLibrary(license_key); 
FSDK.Initialize()
print("OK\nLicense info:", FSDK.GetLicenseInfo())

FSDK.InitializeCapturing()
print('Looking for video cameras... ', end = '')
camList = FSDK.ListCameraNames()

if not camList: print("Please attach a camera."); 
print(camList[0].devicePath)

camera = camList[0] # choose the first camera (0)
print("using '%s'" % camera)
formatList = FSDK.ListVideoFormats(camera)
print(*formatList, sep='\n')

vfmt = formatList[0] # choose the first format: vfmt.Width, vfmt.Height, vfmt.BPP
print('Selected camera format:', vfmt)
FSDK.SetVideoFormat(camera, vfmt)

print("Trying to open '%s'... " % camera, end = '')
camera = FSDK.OpenVideoCamera(camera)
print("OK", camera.handle)

fsdkTracker = FSDK.Tracker() # creating a FSDK Tracker 
fsdkTracker.SetParameters( # set realtime face detection parameters
	RecognizeFaces=False, DetectFacialFeatures=True,
	HandleArbitraryRotations=True, DetermineFaceRotationAngle=True,
	InternalResizeWidth=256, FaceDetectionThreshold=5
)

hwnd = win.CreateWindowEx(win.WS_EX_TOOLWINDOW, win.L("LISTBOX"), win.L("LiveFacialFeatures"), *[0]*9)
win.SendMessage(hwnd, win.LB_ADDSTRING, 0, win.L("Press Esc to exit ..."))
win.SetWindowPos(hwnd, 0, 100, 50, 6+vfmt.Width, 6+32+(vfmt.Height), win.SWP_NOZORDER)
win.ShowWindow(hwnd, win.SW_SHOW)

def dot_center(dots): # calc geometric center of dots
	return sum(p.x for p in dots)/len(dots), sum(p.y for p in dots)/len(dots)

class LowPassFilter: # low pass filter to stabilize frame size
	def __init__(self, a = 0.35): self.a, self.y = a, None
	def __call__(self, x): self.y = self.a * x + (1-self.a)*(self.y or x); return self.y

class FaceLocator:
	def __init__(self):
		self.lpf = None
		self.center = self.angle = self.frame = None 
	def isIntersect(self, state):
		(x1,y1,x2,y2), (xx1,yy1,xx2,yy2) = self.frame, state.frame
		return not(x1 >= xx2 or x2 < xx1 or y1 >= yy2 or y2 < yy1)
	def isActive(self): return self.lpf is not None
	def draw_shape(self, surf):
		container = surf.beginContainer()
		surf.translateTransform(*self.center).rotateTransform(self.angle).ellipse(facePen, *self.frame) # draw frame
		surf.endContainer(container)

	def draw(self, surf, path, face_id=None):
		if face_id is not None:
			ff = fsdkTracker.GetFacialFeatures(0, face_id)
			if self.lpf is None: self.lpf = LowPassFilter()
			xl, yl = dot_center([ff[k] for k in FSDK.FSDKP_LEFT_EYE_SET])
			xr, yr = dot_center([ff[k] for k in FSDK.FSDKP_RIGHT_EYE_SET])
			w = self.lpf((xr - xl)*2.8)
			h = w*1.4
			self.center = (xr + xl)/2, (yr + yl)/2 + w*0.05
			self.angle = math.atan2(yr-yl, xr-xl)*180/math.pi
			self.frame = -w/2, -h/2, w/2, h/2

			self.draw_shape(surf)

			for p in ff: surf.circle(featurePen, p.x, p.y, 1) # draw features

		else:
			if self.lpf is not None: self.lpf, self.countdown = None, 35
			self.countdown -= 1
			if self.countdown <= 8:
				self.frame = [v * 0.95 for v in self.frame]
			else: 
				self.draw_shape(surf)

		path.ellipse(*self.frame) # frame background
		return self.lpf or self.countdown > 0

gdiplus = win.GDIPlus() # initialize GDI+
graphics = win.Graphics(hwnd=hwnd)
backsurf = win.Bitmap.FromGraphics(vfmt.Width, vfmt.Height, graphics)
surfGr = win.Graphics(bmp=backsurf).setSmoothing(True) # graphics object for back surface with antialiasing
facePen, featurePen, brush = win.Pen(0x60ffffff, 5), win.Pen(0xa060ff60, 1.8), win.Brush(0x28ffffff) 
text_color = win.Brush(0xffffffff)
trackers = {}

while 1:
	img = camera.GrabFrame()
	surfGr.resetClip().drawImage(win.Bitmap.FromHBITMAP(img.GetHBitmap())) # fill backsurface with image

	faces = frozenset(fsdkTracker.FeedFrame(0, img)) # recognize all faces in the image
	for face_id in faces.difference(trackers): trackers[face_id] = FaceLocator() # create new trackers

	missed, gpath = [], win.GraphicsPath()
	for face_id, tracker in trackers.items(): # iterate over current trackers
		if face_id in faces: tracker.draw(surfGr, gpath, face_id) #fsdkTracker.GetFacialFeatures(face_id)) # draw existing tracker
		else: missed.append(face_id)
	for mt in missed: # find and remove trackers that are not active anymore
		st = trackers[mt]
		if any(st.isIntersect(trackers[tr]) for tr in faces) or not st.draw(surfGr, gpath): del trackers[mt]

	graphics.drawImage(backsurf, 0, 16) # show backsurface

	msg = win.MSG()
	if win.PeekMessage(win.byref(msg), 0, 0, 0, win.PM_REMOVE):
		win.TranslateMessage(win.byref(msg))
		win.DispatchMessage(win.byref(msg))
		if msg.message == win.WM_KEYDOWN and msg.wParam == win.VK_ESCAPE: break

print("Please wait while freeing resources... ", end='',  flush=True)
win.ShowWindow(hwnd, win.SW_HIDE)

img.Free()
fsdkTracker.Free()
camera.Close()

FSDK.FinalizeCapturing()

FSDK.Finalize()