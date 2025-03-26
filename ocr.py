import numpy as np
import cv2
from mss import mss
from PIL import Image

import pyautogui
import pytesseract

import time
from move import move
from clues import *
import pyperclip
from windowsData import *


"""[TODO] """
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

confidence = 0.8
mon = {'left': 1100, 'top': 145, 'width': 240, 'height': 400}
moves = {"H": "up", "B": "down", "G": "left", "D": "right"}
direction = {"H": 1, "B": 3, "G": 0, "D": 2}
direct = ["left", "up", "right", "down"]

def locateHuntInterface() :
    return

def getInterfaceData():
    s_tab = []
    """with mss() as sct:
        screenShot = sct.grab({"left":mon['left']-20, "top":mon['top'], "width":mon['width'], "height":mon['height']})
        img = Image.frombytes(
            'RGB',
            (screenShot.width, screenShot.height),
            screenShot.rgb,
        )
        cv2.imshow("oui", np.array(img))
        cv2.waitKey(0)"""
    for lettre in ['H', 'B', 'G', 'D']:
        t_tab = pyautogui.locateAllOnScreen('images/fleche'+lettre+'.png', region=[
                                            mon['left']-20, mon['top'], mon['width'], mon['height']], confidence=confidence)
        for t in t_tab:
            if t is not None:
                s_tab.append((t[0], t[1], t[2], t[3], lettre))
    print("Nous sommes à l'indice ", len(s_tab))
    f_left, f_top, f_width, f_height, f_lettre = s_tab[0]
    for left, top, width, height, lettre in s_tab:
        if top + height > f_top+f_height:
            f_left, f_top, f_width, f_height, f_lettre = left, top, width, height, lettre
    """with mss() as sct:
        screenShot = sct.grab(
            {'left': f_left, 'top': 0, 'width': f_width, 'height': int(f_top+f_height)})
        img = Image.frombytes(
            'RGB',
            (screenShot.width, screenShot.height),
            screenShot.rgb,
        )
        cv2.imshow("oui", np.array(img))
        cv2.waitKey(0)"""
    return (f_left, f_top, f_width, f_height, f_lettre)


start, span = 210, 45
def oldGetPosition(a,b,c) :
    x_sun, y_sun = pyautogui.locateCenterOnScreen("images/sun.png", confidence=confidence)
    x_map, y_map = pyautogui.locateCenterOnScreen("images/map.png", confidence=confidence)

    pyautogui.rightClick(x=x_sun, y=y_map)
    time.sleep(0.05)
    x,y = pyautogui.locateCenterOnScreen("images/getposition.png", confidence=confidence)
    pyautogui.leftClick(x=x,y=y)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "c")
    pyautogui.hotkey("del")
    str = pyperclip.paste()[1:-2]
    tab = str.split(",")
    return (int(tab[0]), int(tab[1]))

def getPosition(x,y,direction):
    img = capturePositionText()
    """cv2.imshow("oui", np.array(img))
    cv2.waitKey(0)"""
    mask = cv2.inRange(img, (start, start, start),
                           (start+span, start+span, start+span))
    filtered = cv2.bitwise_and(img, img, mask=mask)

    gray_image = cv2.cvtColor(filtered, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(
        gray_image, start, start+span, cv2.THRESH_BINARY)
    binary_image = cv2.resize(binary_image, (0, 0), fx=3, fy=3)
    str = pytesseract.image_to_string(binary_image, lang='fra')
    tab = str.split("\n")
    # print("str", str)
    """print("Tableau", tab)
    cv2.imshow("oui", np.array(binary_image))
    cv2.waitKey(0)"""
    line = tab[1]
    # print(line)
    coords = line.split(",")
    ans = None
    try :
        ans = (int(coords[0]), int(coords[1]))
    except ValueError :
        ans = forward(x, y, direction, 1)
    return ans


def getLastUsefulElem(tab, inteligible=False):
    for i in range(1, len(tab)+1):
        if tab[-i] is not None and tab[-i] != "" and (not inteligible or (("a" in tab[-i] or "e" in tab[-i] or "o" in tab[-i]) and tab[-i][0].isupper())):
            return tab[-i]


def getLastIndice(mon, top, height):
    start = 100
    span = 250-start
    with mss() as sct:
        screenShot = sct.grab({'left': mon['left']+20, 'top': mon['top'],
                              'width': mon['width'], 'height': int(top+height-mon['top'])})
        img = Image.frombytes(
            'RGB',
            (screenShot.width, screenShot.height),
            screenShot.rgb,
        )
        img = cv2.bitwise_not(np.array(img))
        mask = cv2.inRange(img, (start, start, start),
                           (start+span, start+span, start+span))
        filtered = cv2.bitwise_and(img, img, mask=mask)

        gray_image = cv2.cvtColor(filtered, cv2.COLOR_BGR2GRAY)
        _, img = cv2.threshold(
            gray_image, start, start+span, cv2.THRESH_BINARY)
        img = cv2.resize(img, (0, 0), fx=3, fy=3)
        """cv2.imshow("oui", img)
        cv2.waitKey(0)"""
        str = pytesseract.image_to_string(img, lang='fra')
        print(str)
        """cv2.imshow("oui", np.array(img))
        cv2.waitKey(0)"""
        return getLastUsefulElem(str.split("\n"), True)

def capturePositionText() :
    with mss() as sct:
        screenShot = sct.grab(
            {'left': 5, 'top': 50, 'width': 120, 'height': 65})
        img = Image.frombytes(
            'RGB',
            (screenShot.width, screenShot.height),
            screenShot.rgb,
        )
        """cv2.imshow("oui", np.array(img))
        cv2.waitKey(0)"""
        return np.array(img)
    
def comparator_in_time(last_str, delay=0.5, timeout=8) :
    cnt = 0
    while cnt < timeout :
        time.sleep(delay)
        str = pytesseract.image_to_string(capturePositionText(), lang='fra')
        if last_str != str :
            print("After :", str)
            return True
        cnt += delay

def waitForMapChange(x, y, x_f, y_f, direction, delay=0.5, timeout=8) :
    print("Wait for map to change...")
    last_str = pytesseract.image_to_string(capturePositionText(), lang='fra')
    if direction == 1 and y < y_f :
        move("down")
    elif direction == 3 and y > y_f :
        move("up")
    elif direction == 2 and x < x_f :
        move("right")
    elif direction == 0 and x > x_f :
        move("left")
    else :
        move(direct[direction])
    print("Before :", last_str)
    ans = comparator_in_time(last_str, delay, timeout)
    if ans :
        return True
    #Several possibilities : stairs or split map not clicking at the right position
    tweaks = [-250, 250]
    for tweak in tweaks :
        move(direct[direction], tweak=tweak)
        ans = comparator_in_time(last_str, delay, timeout)
    return ans

def full_stage():
    keep = True
    x, y = getPosition(0,0,0)
    while keep :
        # Get coordinates of the treasure hunt interface
        left, top, width, height, lettre = getInterfaceData()
        print("Coords : ", x, y, "Lettre :", lettre)
        x_f, y_f = findClue(x, y, direction[lettre], getLastIndice(mon, top, height))
        if x_f is None or y_f is None:
            print("Target not found !")
            return
        print("Target : ", x_f, y_f)

        # Move till next flagged map
        counter = 0
        while (x != x_f or y != y_f) and counter < 12:
            change = waitForMapChange(x,y,x_f,y_f,direction[lettre])
            time.sleep(2)
            if not change :
                #Problem here, the map has a stair or sthg like that
                print("Didn't move for a long time, map must have stairs")
                return
            x, y = forward(x, y, direction[lettre])
            print("Now at :", x, y, " aiming for ", x_f, y_f)
            counter += 1
        print("Arrived at next flag")

        # Check if there wasn't an error
        if counter == 12:
            print("Erreur, déplacement de 11 cases impossible")
            return

        # Click on the flag
        x_flag,y_flag = pyautogui.center(pyautogui.locateOnScreen('images/flag.png', region=(mon['left']+20, mon['top'], mon['width']+45, int(top+height-mon['top'])+10), confidence=0.7))
        pyautogui.leftClick(x=x_flag, y=y_flag)
        time.sleep(0.1)
        pyautogui.moveTo(x=int(mon['left']+mon['width']/2), y=int(mon['top']+mon['height']/2))

        # Check if stage is finished
        tup = pyautogui.locateOnScreen('images/button.png', region=(mon['left'], mon['top'], mon['width']+45, int(top+height-mon['top'])+50), confidence=0.7)
        if tup is not None :
            print("Stage process begining")
            """with mss() as sct:
                screenShot = sct.grab(
                    {'left': mon['left'], 'top': mon['top'], 'width': mon['width']+45, 'height':  int(top+height-mon['top'])+50})
                img = Image.frombytes(
                    'RGB',
                    (screenShot.width, screenShot.height),
                    screenShot.rgb,
                )
                cv2.imshow("oui", np.array(img))
                cv2.waitKey(0)"""
            button_x, button_y = pyautogui.center(tup)
            time.sleep(0.3)
            pyautogui.leftClick(button_x, button_y)
            time.sleep(0.3)
            print('Stage finished !')
            tup = pyautogui.locateOnScreen('images/fight_button.png', confidence=0.7)
            if tup is not None :
                print("Fight is available !")
                return
            #keep = False
            


full_stage()