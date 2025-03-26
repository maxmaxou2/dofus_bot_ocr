import numpy as np
import cv2
from mss import mss
from PIL import Image

import pyautogui
import pytesseract

import time
from clues import *
from windowsData import *

from move import move
from move import action_types
from move import routes
from proxy import Proxy

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

constants = {"launchtime":3, "retries": 2, "width" : 1295, "height" : 1038, "start": 210, "span": 45, "overstep": 5, "overstep2": 10, "titleHeight": 24, "turning_ratio":1.24738732, "downUI": 90}
dir = {"G": 0, "H": 1, "D": 2, "B": 3}

"""
    [TODO] --- [TODO]
    - \ Utilisation du havre sac et choix du zaap auquel se TP
    - \ Gestion de route avec le module de déplacement
    - \ Ajout de cas particuliers de clics sur image (screenshots) aux feuilles de routes
    - \ Intéractions avec PNJ (chasse au trésor, voir si ouvrir à d'autres)
    - Choix de la chasse au trésor en fonction de si elle est judicieuse ou pas
    - Liste exhaustive des maps à escaliers
    - Ajouter les cas particuliers des maps qui se déplacent pas droites
    - \ Reconnaissance visuelle d'un phorreur
    - \ Combat automatique du coffre
    [TODO] --- [TODO]
"""
logging = True
forceLog = True
def log(*args) :
    if logging :
        for s in args :
            print("[LOG] "+str(s))

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

def isSame(img1, img2) :
    return np.all(img1 == img2)

class DynamicImage() :
    def __init__(self, file) :
        self.img = Image.open(file)

    def locateCenter(self, dw, confidence=0, region=None) :
        return pyautogui.center(self.locate(dw, confidence, region))

    def locate(self, dw, confidence=0, region=None, retry=True, delay=0) :
        if confidence == 0 :
            confidence = dw.confidence1
        if region is None :
            region = [dw.eff_x, dw.eff_y, dw.eff_w, dw.eff_h]
        tup, i = pyautogui.locateOnScreen(self.resize(dw), confidence=confidence, region=region), 0
        while tup is None and i < constants['retries'] and retry :
            log("Didn't find, retrying... ["+str(i+1)+"/"+str(constants['retries'])+"]")
            time.sleep(delay)
            tup = pyautogui.locateOnScreen(self.resize(dw), confidence=confidence, region=region)
            i += 1
        return tup
    
    def locateAll(self, dw, confidence=0, region=None, retry=True, delay=0) :
        if confidence == 0 :
            confidence = dw.confidence1
        if region is None :
            region = [dw.eff_x, dw.eff_y, dw.eff_w, dw.eff_h]
        tup, i = pyautogui.locateAllOnScreen(self.resize(dw), confidence=confidence, region=region), 0
        while tup is None and i < constants['retries'] and retry :
            log("Didn't find, retrying... ["+str(i+1)+"/"+str(constants['retries'])+"]")
            time.sleep(delay)
            tup = pyautogui.locateAllOnScreen(self.resize(dw), confidence=confidence, region=region)
            i += 1
        return tup
    
    def getArray(self) :
        return np.array(self.img)

    def getImage(self) :
        return self.img
    
    def resize(self, dw) :
        return self.img
        if dw.ratio > constants['turning_ratio'] :
            return self.resizeAlongHeight(dw)
        return self.resizeAlongWidth(dw)

    def resizeAlongWidth(self, dw) :
        w,h = self.img.size
        ratio = dw.w/constants['width']
        return self.img.resize((int(w*ratio), int(h*ratio)))

    def resizeAlongHeight(self, dw) :
        w,h = self.img.size
        ratio = dw.h/constants['height']
        return self.img.resize((int(w*ratio), int(h*ratio)))

#Route similar to "G-H-H-D-pnj:photo_du_png.png-out:photo_sortie.png-keypress:shift+h"
class Route() :
    def __init__(self, route) :
        self.str_route = route
        self.unpack(self.str_route)

    def unpack(self, str_route) :
        self.route = []
        tab = str_route.split("-")
        print(tab)
        for el in tab :
            el = el.split(":")
            if el[0] in action_types['move'] :
                self.route.append(('move', el[0]))
            elif el[0] in action_types['click'] :
                self.route.append(('click', el[0], el[1]))
            elif el[0] == 'keypress' :
                self.route.append(('keypress', el[1]))
            elif el[0] == 'wait' :
                self.route.append(('wait', float(el[1])))

class DofusWindow() :
    def __init__(self) :

        windowData = getDataOfWindow("Dofus 2.")
        self.title = windowData[0]
        hwnd = win32gui.FindWindow(None, self.title)
        win32gui.MoveWindow(hwnd, -8, 0, 946, 1027, True)

        self.x = 0
        self.y = 3
        self.w = 930
        self.h = 1027
        self.ratio = self.w/(self.h-constants['titleHeight'])
        self.proxy = Proxy()
        time.sleep(1)
        
        """self.x = (0 if windowData[1]+2*constants['overstep'] < 0 else windowData[1]+2*constants['overstep'])
        self.y = (0 if windowData[2] < 0 else windowData[2])
        self.w = windowData[3]+min(0,windowData[1])-4*constants['overstep']
        self.h = windowData[4]+min(0,windowData[2])
        self.ratio = self.w/self.h"""

        self.computeEffectiveCoords()

        self.pos = None
        self.interface = {}
        self.direction=0
        self.visible = True
        self.last_pos_str = self.capturePosition()
        self.last_pos_img = self.getMapImage()
        self.confidence1 = 0.8
        self.confidence2 = 0.9

        #Setup moves click location
        self.setupMovesClickLocations()

    def computeEffectiveCoords(self, sh=False) :
        if self.ratio < constants["turning_ratio"] :
            self.eff_x = self.x
            self.eff_w = self.w

            self.eff_h = int(self.w/constants['turning_ratio'])
            self.eff_y = int(self.y+constants['titleHeight']+(self.h-constants['titleHeight']-self.eff_h)/2)
        else :
            self.eff_y = self.y+constants['titleHeight']
            self.eff_h = self.h-constants['titleHeight']

            self.eff_w = int(self.h*constants['turning_ratio'])
            self.eff_x = int(self.x+(self.w-self.eff_w)/2)
        
        if sh :
            print(self.eff_x, self.eff_y, self.eff_w, self.eff_h)
            showAround(self.eff_x, self.eff_y, self.eff_w, self.eff_h)
            
    def updateTHInterface(self, sh=False) :
        s_tab = []
        x,y,w,h = DynamicImage("images/THTitleFixed.png").locate(self, confidence=self.confidence2)
        for lettre in ['H', 'B', 'G', 'D']:
            t_tab = DynamicImage('images/fleche'+lettre+'.png').locateAll(self, region=[x-20, y, w, 600])
            for t in t_tab:
                if t is not None:
                    s_tab.append((t[0], t[1], t[2], t[3], dir[lettre]))
        #showAround(x-20, y, w, 400)
        f_left, f_top, f_width, f_height, f_dire = s_tab[0]
        for left, top, width, height, dire in s_tab:
            if top + height > f_top+f_height:
                f_left, f_top, f_width, f_height, f_dire = left, top, width, height, dire
        
        self.interface['x'] = f_left+f_width
        self.interface['y'] = f_top-constants['overstep']
        self.interface['w'] = w-3*f_width
        self.interface['h'] = f_height+2*constants['overstep']
        self.interface['completeX'] = f_left
        self.interface['completeY'] = y
        self.interface['completeW'] = w
        self.interface['completeH'] = h
        self.interface['x_flag'] = f_left+w-f_width+constants['overstep']
        self.interface['y_flag'] = int(f_top+f_height/2)
        self.direction = f_dire

        #showAround(self.interface['x'],self.interface['y'], self.interface['w'], self.interface['h'])

        self.updateHint(sh)

        if sh :
            showAround(self.interface['x'], self.interface['y'], self.interface['w'], self.interface['h'], sh=True)

    def updateTarget(self) :
        if "Phorreur" in self.hint :
            self.t_pos = forward(self.pos[0], self.pos[1], self.direction, 10)
        else :
            self.t_pos = findClue(self.pos[0], self.pos[1], self.direction, self.hint)

    def getRealDirection(self) :
        if self.direction%2 == 0 :
            return (2 if self.pos[0] < self.t_pos[0] else 0)
        else :
            return (3 if self.pos[1] < self.t_pos[1] else 1)

    def updateHint(self, sh=False) :
        x,y,w,h = self.interface['x'],self.interface['y'],self.interface['w'],self.interface['h']
        img = self.formatForOCR(cv2.bitwise_not(showAround(x,y,w,h,sh=False)), fx=3, fy=3, start=100, span=150)
        self.hint = getClosestHint(pytesseract.image_to_string(img, lang='fra'))
        if sh or forceLog :
            log(self.hint+" : "+str(self.direction))

    def clickCenter(self, tup) :
        x,y = pyautogui.center(tup)
        self.click(x,y)

    def click(self, x, y, back=True) :
        a,b = pyautogui.position()
        pyautogui.leftClick(x,y)
        #pyautogui.moveTo(int(self.eff_x+self.eff_w/2), int(self.y))
        if back :
            pyautogui.moveTo(a,b)
        if forceLog :
            log("Click : ("+str(x)+","+str(y)+")")

    def validateFlag(self) :
        self.click(self.interface['x_flag'], self.interface['y_flag'])
    
    def getEndStageButton(self) :
        return DynamicImage("images/buttonFixed.png").locate(self, region=[self.interface['completeX'],self.interface['y'],self.interface['completeW'], int(self.interface['h']+32)])

    def formatForOCR(self, img, fx=1, fy=1, start=constants['start'], span=constants['span']) :
        mask = cv2.inRange(img, (start, start, start), (start+span, start+span, start+span))
        filtered = cv2.bitwise_and(img, img, mask=mask)
        gray_image = cv2.cvtColor(filtered, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(gray_image, start, start+span, cv2.THRESH_BINARY)
        return cv2.resize(binary_image, (0, 0), fx=fx, fy=fy)

    def capturePosition(self, sh = False) :
        with mss() as sct:
            screenShot = sct.grab(
                {'left': self.x, 'top': self.eff_y, 'width': int(self.eff_w/6), 'height': int(self.eff_h/8)})
            img = Image.frombytes(
                'RGB',
                (screenShot.width, screenShot.height),
                screenShot.rgb,
            )
            str = pytesseract.image_to_string(self.formatForOCR(np.array(img), fx=1, fy=1))
            if sh :
                show(self.formatForOCR(np.array(img), fx=1, fy=1))
                print(str)
            return str
        
    def updateFirstPosition(self) :
        x,y,w,h = DynamicImage("images/locate.png").locate(self)
        img = self.formatForOCR(cv2.bitwise_not(showAround(x+w,y,self.interface['w'],h,sh=False)), fx=1.5, fy=1.5, start=100, span=150)
        str = pytesseract.image_to_string(img, lang='fra')
        print(str)
        coords = str.split("[")[1].split("]")[0].split(",")
        self.pos = (int(coords[0]), int(coords[1]))

    def updatePosition(self, sh=False) :
        """if self.pos is None :
            self.updateFirstPosition()
            return"""
        self.last_pos_str = self.capturePosition()
        self.last_pos_img = self.getMapImage()
        tab = self.last_pos_str.split("\n")
        line = tab[1]
        coords = line.split(",")
        try :
            self.pos = (int(coords[0]), int(coords[1]))
        except ValueError :
            if self.pos is None :
                self.updateFirstPosition()
            else :
                pos_x, pos_y = self.pos
                self.pos = forward(pos_x, pos_y, self.direction, 1)
        if sh or forceLog :
            log("Current position :"+str(self.pos))

    def oldSetupMovesClickLocations(self) :
        _,y_u,_,_ = DynamicImage("images/gear.png").locate(self, confidence=self.confidence2)
        x_r,y_d = DynamicImage("images/eye.png").locateCenter(self, confidence=self.confidence2)
        x_l,_,_,_ = DynamicImage("images/plus.png").locate(self, confidence=self.confidence2)

        self.moves = [[(x_l, int(self.h/4)),(x_l, int(self.h*3/4))], [(int(self.w/3), y_u),(int(self.w*2/3), y_u)],
                      [(x_r, int(self.h/4)),(x_r, int(self.h*3/4))], [(int(self.w/3), y_d),(int(self.w*2/3), y_d)]]

    def setupMovesClickLocations(self) :
        self.moves = [[(self.eff_x+constants['overstep2'], int(self.eff_y+self.eff_h/3)), (self.eff_x+constants['overstep2'], int(self.eff_y+self.eff_h*2/3))],
                      [(int(self.eff_x+self.eff_w/3), self.eff_y+constants['overstep2']), (int(self.eff_x+self.eff_w*2/3), self.eff_y+constants['overstep2'])],
                      [(self.eff_x+self.eff_w-constants['overstep2'], int(self.eff_y+self.eff_h/3)), (self.eff_x+self.eff_w-constants['overstep2'], int(self.eff_y+self.eff_h*2/3))],
                      [(int(self.eff_x+self.eff_w/3), self.eff_y+self.eff_h-constants['overstep2']-constants['downUI']), (int(self.eff_x+self.eff_w*2/3), self.eff_y+self.eff_h-constants['overstep2']-constants['downUI'])]]

    def getMapImage(self, sh=False) :
        return showAround(int(self.eff_x+self.eff_w*9/10),self.eff_y+self.eff_h-constants['downUI'], int(self.eff_w/20), constants['downUI'], sh=sh)

    def waitForCoordsChange(self, delay=1, timeout=8) :
        cnt = 0
        while cnt < timeout :
            time.sleep(delay)
            if self.last_pos_str != self.capturePosition() and not isSame(self.last_pos_img, self.getMapImage()) :
                log("Change detected !")
                return True
            cnt += delay
        log("No change detected !")
        return False
    
    def waitForCoordsChangeWithTxt(self, delay=0.5, timeout=8) :
        cnt = 0
        while cnt < timeout :
            time.sleep(delay)
            if self.last_pos_str != self.capturePosition() :
                log("Change detected !")
                return True
            cnt += delay
        log("No change detected !")
        return False
        
    def tryMove(self, direction, first=True) :
        x,y = self.moves[direction][0 if first else 1]
        self.click(x,y)

    def moveWithConfirmation(self, direction, forceMove=False) :
        self.last_pos_str = self.capturePosition()
        self.last_pos_img = self.getMapImage()
        self.tryMove(direction)
        if not self.waitForCoordsChange() :
            self.tryMove(direction, False)
            if not self.waitForCoordsChange() :
                log("Had to stop cause didn't move for a while !")
                #Handle stairs
                return False
        if not forceMove :
            self.pos = forward(self.pos[0], self.pos[1], direction)
        time.sleep(1)
        log("Finished the movement...")
        return True
    
    def followRoute(self, route_str) :
        route = Route(route_str)
        print(route.route)
        self.focus()
        for step in route.route :
            if step[0] == 'move' :
                self.moveWithConfirmation(dir[step[1]], forceMove = True)
            elif step[0] == 'click' :
                if step[1] == 'pnj' :
                    self.clickCenter(DynamicImage(step[2]).locate(self, confidence=0.8))
                elif step[1] == 'out' :
                    self.clickCenter(DynamicImage(step[2]).locate(self, confidence=0.7))
            elif step[0] == 'keypress' :
                pyautogui.hotkey(*step[1].split("+"))
            elif step[0] == 'wait' :
                time.sleep(step[1])

    def getNewTH(self) :
        self.followRoute("-".join([routes['THzaap'], routes['THmoveIn'], routes['THget'], routes['THmoveOut']]))
    
    def cancelTH(self) :
        if not self.visible :
            log("Interface not visible !")
            return
        self.updateTHInterface()
        for path,reg in [('images/cancel.png', [self.interface['completeX'], self.interface['completeY'], self.interface['completeW'], self.interface['completeH']*5]), ('images/confirm.png', None)] :
            x,y = DynamicImage(path).locateCenter(self, region = reg)
            self.click(x,y)
            time.sleep(2)

    def toggleInterface(self) :
        self.click(self.interface['completeX']+self.interface['completeW'], int(self.interface['completeY']+self.interface['completeH']/2))
        self.visible = not self.visible

    def isPhorreurHere(self) :
        for number in range(1, 13) :
            tup = pyautogui.locateOnScreen("images/phorreur"+str(number)+".png", confidence=0.85)
            if tup is not None :
                log("Phorreur found at ("+str(self.pos[0])+","+str(self.pos[1])+")")
                return True
        return False
    
    def moveToPhorreur(self) :
        log("Looking for Phorreur...")
        cnt = 0
        while cnt < 11 :
            if not self.moveWithConfirmation(self.direction) :
                log("Problem along path...")
                return False
            cnt += 1
            if self.isPhorreurHere() :
                return True
            else :
                log("No Phorreur here...")
        log("Didn't find any Phorreur...")
        return False
    
    def moveToHint(self) :
        log("Target found ! Moving until ("+str(self.t_pos[0])+","+str(self.t_pos[1])+")")
        cnt = 0
        dist = abs(self.pos[0] - self.t_pos[0]) + abs(self.pos[1] - self.t_pos[1])
        while (cnt < dist):
            if not self.moveWithConfirmation(self.direction) :
                log("Problem along path...")
                return False
            cnt += 1
            log(cnt)
        if cnt >= 11 :
            log("Problem along path...")
            return False
        return True
    
    def inFight(self) :
        self.focus()
        tup = DynamicImage('images/victory.png').locate(self, confidence=0.7)
        i = 0
        while tup is None or i < 6:
            for i in range(1,7) :
                tup = DynamicImage('images/treasure'+str(i)+'.png').locate(self, confidence=0.9)
                if tup is not None :
                    pyautogui.hotkey('a')
                    time.sleep(0.5)
                    #pyautogui.moveTo(pyautogui.center(tup))
                    self.click(int(tup[0]+tup[2]/2),tup[1]+30)
                    time.sleep(1)
                    pyautogui.press("f1")
                    time.sleep(5)
                    continue
            tup = DynamicImage('images/victory.png').locate(self, confidence=0.7)
            i += 1
        log("Fight finished !")

    def focus(self) :
        self.click(int(self.x+self.w/2), int(self.y+constants['titleHeight']/2), back=True)
        
    def runTH(self) :
        keep = True
        self.updateTHInterface()
        self.updatePosition()
        while keep :
            log("Begin loop !")
            tup = DynamicImage('images/fight_buttonFixed.png').locate(self)
            if tup is not None :
                log("Fight available !")
                self.clickCenter(tup)
                time.sleep(5)
                self.clickCenter(DynamicImage('images/ready.png').locate(self))
                time.sleep(10)
                self.inFight()
                self.clickCenter(DynamicImage('images/close_fight.png').locate(self))
                self.getNewTH()
                return
            
            self.updateTHInterface()
            self.updateTarget()
            if self.t_pos[0] is None or self.pos[0] is None :
                log("Target or source not found !")
                return
            
            if "Phorreur" in self.hint :
                self.toggleInterface()
                if not self.moveToPhorreur() :
                    return
                self.toggleInterface()
            else :
                if not self.moveToHint() :
                    return

            self.validateFlag()
            self.focus()
            endStageButton = self.getEndStageButton()
            if endStageButton is None :
                log("Next flag reached !")
                self.updateTHInterface()
                continue
            
            self.clickCenter(endStageButton)
            log("Stage finished !")

def treasure_hunt() :
    #Launch
    log("Launching the hunt... ", "You have "+str(constants['launchtime'])+" seconds to put Dofus in full screen")
    time.sleep(constants['launchtime'])

    #Get the data of Dofus window
    DW = DofusWindow()

    #DW.getMapImage(True)
    DW.runTH()
    #DW.inFight()
    #DW.followRoute(routes['THzaap'])
    #DW.cancelTH()

treasure_hunt()