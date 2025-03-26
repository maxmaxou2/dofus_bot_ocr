import pyautogui

offleft, offtop = 100, 100
width, height = 1200, 800
z_x, z_y, x_scind, y_scind = 26, 12, 1, 1
dx, dy = width//z_x, height//z_y
start, span = 40, 120
limit, change_map = 10000, 2

direct = ["left", "up", "right", "down"]
def move(direction, click) :
    x,y = click[direction]
    pyautogui.leftClick(x,y)
        
    """if pyautogui.locateOnScreen(direction+"G.png", region=[offleft, offtop, width, height], confidence=0.5) is not None or pyautogui.locateOnScreen(direction+"B.png", region=[offleft, offtop, width, height], confidence=0.5) is not None :
        print("click")
        pyautogui.leftClick(x,y)
        return True
    else :
        #CANNOT MOVE
        return False"""
    
action_types = {"move": ["G", "H", "D", "B"], "click":["pnj", "out"], "keypress":["h"], "wait": [0.4]}
routes = {"THzaap":"keypress:h-wait:3-pnj:zaap.png-wait:2-pnj:champsCania.png-wait:1-pnj:teleport.png-wait:4",
          "THmoveIn":"D-D-out:door1.png-wait:5-out:outTH1.png-wait:5",
          "THget":"pnj:treasurePNJ.png-wait:2-pnj:treasurePNJ2.png-wait:6",
          "THmoveOut":"out:outTH2.png-wait:6-out:door2.png-wait:6"}