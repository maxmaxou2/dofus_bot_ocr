import win32gui

def getDataOfWindow(regex):
    ans = []
    def callback(hwnd, extra):
        rect = win32gui.GetWindowRect(hwnd)
        x = rect[0]
        y = rect[1]
        w = rect[2] - x
        h = rect[3] - y
        title = win32gui.GetWindowText(hwnd)
        if regex in title :
            ans.append((title, x, y, w, h))
    win32gui.EnumWindows(callback, None)
    return ans[-1]

print(getDataOfWindow("Dofus 2."))