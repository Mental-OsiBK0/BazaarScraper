"""
Fare imlecinin ekran koordinatlarını canlı olarak gösterir.

Market alanının sol üst ve sağ alt köşesini bulmak için kullanılır;
"""

import time

import pyautogui


def main() -> None:
    print("Fareyi market alanının köşelerine götürün. Çıkmak için Ctrl+C.\n")
    try:
        while True:
            x, y = pyautogui.position()
            print(f"İmlecin konumu: x={x:<5} y={y:<5}", end="\r", flush=True)
            time.sleep(0.05)  
    except KeyboardInterrupt:
        print("\nÇıkıldı.")


if __name__ == "__main__":
    main()
