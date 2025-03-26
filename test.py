import pyautogui
import cv2
from mss import mss
import numpy as np
from PIL import Image

def showAround(x,y,w=0,h=0, sh=True) :
    options = {'left': max(0, x-100), 'top': max(0, y-100), 'width': 200, 'height': 200}
    if w != 0 or h != 0 :
        options = {'left': x, 'top': y, 'width': w, 'height': h}
    with mss() as sct:
        screenShot = sct.grab(options)
        img = Image.frombytes(
            'RGB',
            (screenShot.width, screenShot.height),
            screenShot.rgb,
        )
        if sh :
            show(img)
        return np.array(img)
    
def show(img) :
    cv2.imshow("oui", np.array(img))
    cv2.waitKey(0)

for number in range(1, 13) :
    tup = pyautogui.locateOnScreen("phorreur"+str(number)+".png", confidence=0.7)
    if tup is not None :
        x, y, w, h = tup
        print("Found")
        showAround(x,y,w,h)
        break