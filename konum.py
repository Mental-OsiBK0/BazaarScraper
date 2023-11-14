import pyautogui


while True:
    x, y = pyautogui.position()
    print(f"İmlecin konumu: x={x}, y={y}", end="\r")
