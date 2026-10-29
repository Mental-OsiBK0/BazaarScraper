# farenin konumunu gösteriyor, market alanının köşelerini bulmak için
# çıkmak için ctrl+c

import time

import pyautogui

try:
    while True:
        x, y = pyautogui.position()
        print(f"İmlecin konumu: x={x}, y={y}    ", end="\r")
        time.sleep(0.05)
except KeyboardInterrupt:
    print()
