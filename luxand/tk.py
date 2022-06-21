import tkinter
from tkinter import ttk
from PIL import Image, ImageTk
from collections import namedtuple

Style = namedtuple('Style', ['color', 'width', 'fill'], defaults=('black', 1, ''))

class MainWindow(tkinter.Frame):

    __defaultStyle = Style(color='black', width=1, fill='')

    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent)
        self.pack()
        self.canvas = tkinter.Canvas(self, width=parent.winfo_screenwidth(), height=parent.winfo_screenheight())
        self.canvas.pack(side='top', fill='both', expand='yes')
        self.canvas.focus_set()
        self.bind('<Configure>', self.configure)
        self.image = None

    def configure(self, event):
        self.canvas.config(width=event.width, height=event.height)

    def drawImage(self, image):
        if not self.image:
            self.deleteObject(self.image)

        self.__image = ImageTk.PhotoImage(image)
        self.image = self.canvas.create_image(0, 0, image=self.__image, anchor=tkinter.NW)

        return self.image

    def drawOval(self, center, x0, y0, x1, y1, style=__defaultStyle):
        x, y = center
        return self.canvas.create_oval(x + x0, y + y0, x + x1, y + y1, outline=style.color, width=style.width, fill=style.fill)

    def drawCircle(self, center, radius, style=__defaultStyle):
        x, y = center
        return self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline=style.color, width=style.width, fill=style.fill)

    def drawText(self, position, text, style=__defaultStyle):
        return self.canvas.create_text(*position, text=text, fill=style.color, font='Tahoma')

    def deleteObject(self, obj):
        if obj is not None:
            self.canvas.delete(obj)

    def getScaleFor(self, width, height):
        canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        if canvas_width == 1 and canvas_height == 1:
            return 1
        return min(self.canvas.winfo_width() / width, self.canvas.winfo_height() / height)
