import pyautogui
from mss import mss
from PIL import Image
import pytesseract
from patternReck import getHighlightedZones
import time
import cv2
import numpy as np
import random as rd
import math

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


class Window:

    def __init__(self, offleft, offtop, width, height, zx, zy, dx, dy):
        self.offleft = offleft
        self.offtop = offtop
        self.width = width
        self.heigh = height
        self.z_x = zx
        self.z_y = zy
        self.dx = dx
        self.dy = dy

    def getPosition(self, i, j):
        return (self.offtop+(i+1/2)*self.dy, self.offleft+(j+1/2)*self.dx)


offleft, offtop = 100, 100
width, height = 1200, 800
z_x, z_y, x_scind, y_scind = 26, 12, 1, 1
dx, dy = width//z_x, height//z_y
start, span = 40, 120
limit, change_map = 10000, 2

win = Window(offleft, offtop, width, height, z_x, z_y, dx, dy)

nb_sorties = 4
def getExits() :
    exits = []
    for i in range(1,nb_sorties+1) :
        located = pyautogui.locateAllOnScreen('out'+str(i)+'.png', confidence=0.6, region=[offleft, offtop, width, height])
        if located is not None :
            for s in located :
                exits.append((int(s.left+s.width/2), int(s.top+s.height/2)))
    
    final_exits = []
    max_distance = 5
    for x,y in exits :
        to_keep = True
        for a,b in exits :
            if a!=x and b!=y and math.sqrt((a-x)**2+(b-y)**2) < max_distance :
                to_keep = False
        if to_keep :
            final_exits.append((x,y))

    return final_exits

def getBoundaries(i, j):
    return (dy*i+offtop, dx*j+offleft, dy*(i+1)+offtop, dx*(j+1)+offleft)

def getPositions(i, j, x_scind, y_scind):
    x0, y0, x1, y1 = getBoundaries(i, j)
    fx, fy = (x1-x0)//x_scind, (y1-y0)//y_scind
    coords = [0 for i in range(x_scind*y_scind)]
    for a in range(y_scind):
        for b in range(x_scind):
            vx, vy = x0+fx*(b+1/2), y0+fy*(a+1/2)
            index = (a*x_scind+b-(x_scind*y_scind)//2) % len(coords)
            coords[index] = (vx, vy)
    return coords

def main() :
    current = 0
    keep = 0
    while current <= limit:
        exits = getExits()
        print("Nb de sortie :", len(exits))
        if keep >= change_map :
            keep = 0
            if len(exits) > 0 :
                rand = rd.randint(0, len(exits)-1)
                print("Len :", len(exits), " Rand :", rand)
                x,y = exits[rand]
                pyautogui.leftClick(x=x, y=y)
                time.sleep(3)
                continue

        result = getHighlightedZones(
            width, height, offleft, offtop, z_x, z_y, dx, dy, start, span)

        for x,y in result :
            positions = getPositions(y, x, x_scind, y_scind)
            for y_c, x_c in positions:
                click_x, click_y = x_c+rd.randrange(-7,7), y_c+rd.randrange(-7,7)
                pyautogui.moveTo(x=click_x, y=click_y)
                mon = {'left': int(x_c), 'top': int(max(0,y_c-offtop)), 'width': int(2.5*offleft), 'height': int(2*offtop)}
                with mss() as sct:
                    screenShot = sct.grab(mon)
                    img = Image.frombytes(
                        'RGB',
                        (screenShot.width, screenShot.height),
                        screenShot.rgb,
                    )
                    """cv2.imshow('test', np.array(img))
                    cv2.waitKey(0)"""
                    str = pytesseract.image_to_string(img, lang='fra')
                    print(str)
                    if "Collecter" in str or "Faucher" in str:
                        pyautogui.leftClick(x=click_x, y=click_y)
                        keep = -1

        current += 1
        keep += 1

main()