import cv2
import numpy as np
import pyautogui
from mss import mss
from PIL import Image
import time

offleft, offtop, offx = 100, 100, 2
width, height = 1200, 800
z_x, z_y, scind = 30, 15, 2
dx, dy = width//z_x, height//z_y
start, span = 80, 120
limit = 1

def reduceZones(results) :
    x = 0
    while x < len(results[0]) :
        cnt = 0
        first, last = len(results), 0
        y = 0
        while y < len(results) :
            if results[y][x] == 255 :
                cnt += 1
                if y < first :
                    first = y
                if y > last :
                    last = y
            elif cnt > 0 :
                nb = last-first+1
                results[first: last+1, x] = 0
                results[int(first+1/4*nb): int(first+3/4*nb)+1, x] = 255
                cnt = 0
                first, last = len(results), 0
                break
            y += 1
        x+=1
    return results
        

def getHighlightedZones(width, height, offleft, offtop, z_x, z_y, dx, dy, start, span) :
    mon = {'left': offleft, 'top': offtop, 'width': width, 'height': height}
    pyautogui.leftClick(x=offleft, y=5)
    with mss() as sct:
        screenShot = sct.grab(mon)
        image1 = np.array(Image.frombytes(
                        'RGB', 
                        (screenShot.width, screenShot.height), 
                        screenShot.rgb, 
                    ))#cv2.imread("after.png")
        pyautogui.keyDown('y')
        screenShot = sct.grab(mon)
        image2 = np.array(Image.frombytes(
                        'RGB', 
                        (screenShot.width, screenShot.height), 
                        screenShot.rgb, 
                    ))#cv2.imread("before.png")
        time.sleep(0.1)
        pyautogui.keyUp('y')
        image3 = image1 - image2

        mask = cv2.inRange(image3, (start, start, start), (start+span, start+span, start+span))
        filtered = cv2.bitwise_and(image3, image3, mask = mask)

        gray_image = cv2.cvtColor(filtered, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(gray_image, start, start+span, cv2.THRESH_BINARY)
        #Decrease resolution
        """ratio = 0.2
        binary_image = cv2.resize(binary_image, (0,0), fx=ratio, fy=ratio)
        binary_image = cv2.resize(binary_image, (0,0), fx=1/ratio, fy=1/ratio)"""
        height,width = binary_image.shape
        result = np.zeros((z_y,z_x))
        for y in range(binary_image.shape[0]) :
            for x in range(binary_image.shape[1]) :
            #for val in binary_image[y] :
                if binary_image[y,x] > 0 :
                    val_x, val_y = x//dx, y//dy
                    result[val_y,val_x] = 255
        print("Before", result)
        result = reduceZones(result)
        print("After", result)
        ans = []
        for y in range(result.shape[0]) :
            for x in range(result.shape[1]) :
                if result[y,x] == 255 :
                    ans.append((x,y))
        return ans

"""def showHighlightedZones() :
    result = getHighlightedZones(
            width, height, offleft, offtop, z_x, z_y, dx, dy, offx, start, span)
    cv2.imshow('test', cv2.resize(result, (0,0), fx=width/z_x, fy=height/z_y))
    cv2.waitKey(0)"""