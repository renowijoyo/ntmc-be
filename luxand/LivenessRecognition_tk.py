from __future__ import print_function

import sys
import math
import ctypes
import random
from PIL import Image, ImageOps

import tkinter
from fsdk import FSDK
from tk import MainWindow, Style

drawFeatures = False
license_key = ""


trackerMemoryFile = "tracker70.dat"

HOR_CONF_LEVEL = (2, 17)
UP_CONF_LEVEL = (2, 7)
DOWN_CONF_LEVEL = (-2, -8)

SMILE_CONF_LEVEL = (0.3, 0.6)

FONT_SIZE = 20

commands = {
	'L': 'Turn left',
	'R': 'Turn right',
	'F': 'Look straight',
	'U': 'Look up',
	'D': 'Look down',
	'S': 'Make a smile'
}

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
# # print(*formatList[0:5], sep='\n')
# # if len(formatList)>5: print('...', len(formatList)-5, 'more formats (skipped)...')

vfmt = formatList[0] # choose the first format: vfmt.Width, vfmt.Height, vfmt.BPP
print('Selected camera format:', vfmt)
FSDK.SetVideoFormat(camera, vfmt)

print("Trying to open '%s'... " % camera, end = '')
camera = FSDK.OpenVideoCamera(camera)
print("OK", camera.handle)

try:
	fsdkTracker = FSDK.Tracker.FromFile(trackerMemoryFile)
except:
	fsdkTracker = FSDK.Tracker()  # creating a FSDK Tracker 

fsdkTracker.SetParameters( # set realtime face detection parameters
	RecognizeFaces=True, DetectFacialFeatures=True,
	HandleArbitraryRotations=True, DetermineFaceRotationAngle=True,
	InternalResizeWidth=256, FaceDetectionThreshold=5,
	DetectGender=True, DetectAge=True, DetectExpression=True, DetectAngles=True
)

need_to_exit = False

def onDestroy():
	global need_to_exit
	need_to_exit = True

root = tkinter.Tk()
root.title('Liveness Recognition')
root.protocol("WM_DELETE_WINDOW", onDestroy)

window = MainWindow(root)

activeStyle = Style(color='#00FF00', width=2, fill='')
captureStyle = Style(color='#FF0000', width=3, fill='')
faceStyle = Style(color='#FFFFFF', width=5, fill='')
featureStyle = Style(color='#FFFF60', width=2, fill='#FFFF60')
textColor = Style(color='#FFFFFF')
textGreen = Style(color='#00FF00')
textRed = Style(color='#FF0000')
textShadow = Style(color='#808080')

def dot_center(dots): # calc geometric center of dots
	return sum(p.x for p in dots)/len(dots), sum(p.y for p in dots)/len(dots)

class LowPassFilter: # low pass filter to stabilize frame size

	def __init__(self, a=0.35):
		self.a, self.y = a, None

	def __call__(self, x):
		self.y = self.a * x + (1 - self.a) * (self.y or x)
		return self.y

class FaceLocator:

	def __init__(self, fid):
		self.lpf = None
		self.center = self.angle = self.frame = None 
		self.fid = fid
		self.state = {'F'}
		self.commands = []
		self.command_id = 0
		self.live = False
		self.pan = LowPassFilter()
		self.tilt = LowPassFilter()
		self.faceOval = self.activeOval = self.capturedOval = None
		self.features = []
		self.name = None
		self.countdown = 0

	def isIntersect(self, state):
		(x1, y1, x2, y2), (xx1, yy1, xx2, yy2) = self.frame, state.frame
		return not (x1 >= xx2 or x2 < xx1 or y1 >= yy2 or y2 < yy1)

	def isActive(self):
		return self.lpf is not None

	def isInside(self, x, y):
		x -= self.center[0]
		y -= self.center[1]
		a = self.angle * math.pi / 180
		x, y = x * math.cos(a) + y * math.sin(a), x * math.sin(a) - y * math.cos(a)
		return (x / self.frame[0]) ** 2 + (y / self.frame[1]) ** 2 <= 1

	def setActive(self):
		self.live = False
		self.command_id = 0
		cmds = list(commands)
		self.commands = ['F']

		while len(self.commands) < 6:
			cmd = random.choice(cmds)
			if self.commands[-1] != cmd:
				self.commands.append(cmd)

		if 'S' not in self.commands:
			self.commands[random.randint(1, len(self.commands)-1)] = 'S'

	def drawShape(self):
		window.deleteObject(self.faceOval)
		window.deleteObject(self.activeOval)
		window.deleteObject(self.capturedOval)

		self.faceOval = window.drawOval(self.center, *self.frame, style=faceStyle)

		if activeFace == self.fid:
			self.activeOval = window.drawOval(self.center, *self.frame, style=activeStyle)

		if capturedFace == self.fid:
			self.capturedOval = window.drawOval(self.center, *self.frame, style=captureStyle)

	def faceState(self):
		expression = fsdkTracker.GetTrackerFacialAttribute(0, self.fid, "Expression")
		pairs = (a.split('=') for a in expression.split(';'))
		expression = { p[0].strip(): float(p[1]) for p in pairs }
		smile = expression['Smile']

		angles = fsdkTracker.GetTrackerFacialAttribute(0, self.fid, "Angles")
		pairs = ( a.split('=') for a in angles.split(';') )
		angles = { p[0].strip(): float(p[1]) for p in pairs }		
		pan, tilt = self.pan(angles['Pan']), self.tilt(angles['Tilt'])

		st = ''
		if abs(pan) < HOR_CONF_LEVEL[0]:
			st = 'F'
		elif abs(pan) > HOR_CONF_LEVEL[1]:
			st = 'R' if pan > 0 else 'L'

		if st:
			self.state.difference_update({'L', 'R'})
			self.state.add(st)

		st = ''
		if tilt > UP_CONF_LEVEL[1]:
			st = 'U'
		elif tilt < DOWN_CONF_LEVEL[1]:
			st = 'D'
		elif tilt > DOWN_CONF_LEVEL[0] and tilt < UP_CONF_LEVEL[0]:
			st = 'F'

		if st:
			self.state.difference_update({'U', 'D'})
			self.state.add(st)

		if self.state & {'L', 'R', 'U', 'D'}:
			self.state.discard('F')

		if smile < SMILE_CONF_LEVEL[0]:
			self.state.discard('S')
		elif smile > SMILE_CONF_LEVEL[1]:
			self.state.add('S')

		def cmdApproved(cmd):
			if cmd not in self.state:
				return False

			if cmd == 'S':
				return True

			return 'S' not in self.state

		if self.fid == capturedFace and not self.live:
			cmd = self.commands[self.command_id]
			if cmdApproved(cmd):
				self.command_id += 1
				if self.command_id >= len(self.commands):
					self.live = True

		if self.state:
			print(self.state, end = ' ')
		print("Pan =", pan, "Tilt =", tilt)

	def draw(self):
		try:
			ff = fsdkTracker.GetFacialFeatures(0, self.fid)

			if self.lpf is None:
				self.lpf = LowPassFilter()

			xl, yl = dot_center([ff[k] for k in FSDK.FSDKP_LEFT_EYE_SET])
			xr, yr = dot_center([ff[k] for k in FSDK.FSDKP_RIGHT_EYE_SET])
			w = self.lpf((xr - xl) * 2.8)
			h = w * 1.4
			self.center = (xr + xl) / 2, (yr + yl) / 2 + w * 0.05
			self.angle = math.atan2(yr - yl, xr - xl) * 180 / math.pi
			self.frame = -w / 2, -h / 2, w / 2, h / 2

			self.drawShape()

			if drawFeatures:
				for i in self.features:
					window.deleteObject(i)

				self.features = [window.drawCircle((p.x, p.y), 1, style=featureStyle) for p in ff]

			name = 'LIVE!' if self.live else ''
			style = textGreen if name else textColor

			if self.fid == activeFace:
				name = 'Press to check liveness'

			if self.fid == capturedFace:
				if self.command_id >= len(self.commands):
					name = 'LIVE!'
				else:
					name = '%s (%s of %s)' % (commands[self.commands[self.command_id]], self.command_id + 1, len(self.commands))

			if name:
				if self.name is not None and self.name[0] != name:
					window.deleteObject(self.name[1])
					window.deleteObject(self.name[2])
				self.name = (
					name,
					window.drawText((self.center[0] - w // 2 + 2, self.center[1] - h // 2 + 2), name, style=textShadow),
					window.drawText((self.center[0] - w // 2, self.center[1] - h // 2), name, style=style)
				)
			else:
				if self.name is not None:
					window.deleteObject(self.name[1])
					window.deleteObject(self.name[2])
				self.name = None

			self.faceState()
			self.countdown = 35
		except FSDK.Exception:
			self.countdown -= 1

			if self.countdown <= 8:
				self.frame = [v * 0.95 for v in self.frame]

			self.drawShape()
			
		return self.countdown > 0

trackers = {}
activeFace = capturedFace = None

def updateActiveFace(event):
	global activeFace
	x, y = event.x, event.y
	for fid, tr in trackers.items():
		if tr.isInside(x, y):
			if fid != activeFace and fid != capturedFace:
				tr.setActive()
			activeFace = fid
			break
	else:
		activeFace = None

def onMousePress(event):
	global capturedFace
	print(42, activeFace, capturedFace)
	if activeFace and capturedFace != activeFace:
		capturedFace = activeFace
	else:
		capturedFace = None

window.canvas.bind('<Button-1>', onMousePress)
window.canvas.bind('<Motion>', updateActiveFace)

while not need_to_exit:
	img = camera.GrabFrame()
	img.Resize(window.getScaleFor(img.width, img.height))	
	window.drawImage(Image.frombytes('RGB', (img.width, img.height), img.ToBuffer(1)))

	faces = frozenset(fsdkTracker.FeedFrame(0, img)) # recognize all faces in the image
	for face_id in faces.difference(trackers): # create new trackers
		trackers[face_id] = FaceLocator(face_id)

	img.Free()

	missed = []
	for face_id, tracker in trackers.items(): # iterate over current trackers
		if face_id in faces:
			tracker.draw() #fsdkTracker.GetFacialFeatures(face_id)) # draw existing tracker
		else:
			missed.append(face_id)

	for mt in missed: # find and remove trackers that are not active anymore
		st = trackers[mt]
		if any(st.isIntersect(trackers[tr]) for tr in faces) or not st.draw():
			del trackers[mt]

	window.update_idletasks()
	window.update()

	if capturedFace not in trackers:
		capturedFace = None

print("Please wait while freeing resources... ",  flush=True)
fsdkTracker.SaveToFile(trackerMemoryFile)

root.destroy()

fsdkTracker.Free()
camera.Close()

FSDK.FinalizeCapturing()

FSDK.Finalize()
