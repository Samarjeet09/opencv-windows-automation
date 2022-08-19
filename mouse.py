import cv2
import numpy as np
import handTrackingModule as handTM
import time
import pyautogui

cam = cv2.VideoCapture(0)
wCam = 1080
hCam = 720
cTime, pTime = 0, 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
smoothening = 6

cam.set(3, wCam)
cam.set(4, hCam)
wScreen, hScreen = pyautogui.size()
mousePadW = 150
mousePadH = 160
detector = handTM.handDetector(maxHands=1)
while True:
    # 1. Find hand Landmarks
    success, img = cam.read()
    hands, img = detector.findHands(img)
    if hands:
        lmList = hands[0]["lmList"]
        bbox = hands[0]["bbox"]

        # 2. Get the tip of the index and middle fingers
        if len(lmList) != 0:
            x1, y1 = lmList[8][:2]
            x2, y2 = lmList[12][:2]

        # 3. Check which fingers are up
            fingers = detector.fingersUp(hands[0])
            cv2.rectangle(img, (100, 150), (600, 430),
                          (255, 0, 255), 2)
            # 4. Only Index Finger : Moving Mode
            if fingers[1] == 1 and fingers[2] == 0:
                # 5. Convert Coordinates
                x3 = np.interp(x1, (100, 600), (0, wScreen))
                y3 = np.interp(
                    y1, (150, 430), (0, hScreen))
                # 6. Smoothen Values
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening

                # 7. Move Mouse
                pyautogui.moveTo(int(wScreen - clocX),
                                 int(clocY), duration=0.01)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                plocX, plocY = clocX, clocY
            # 8. Both Index and middle fingers are up : Clicking Mode
            if fingers[1] == 1 and fingers[2] == 1:
                # 9. Find distance between fingers
                length,  lineInfo, img = detector.findDistance(
                    lmList[8][0:2], lmList[12][0:2], img)

                # 10. Click mouse if distance short
                if length < 40:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]),
                               15, (0, 255, 0), cv2.FILLED)
                    pyautogui.click()

    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (420, 420, 0), 3)
    # 12. Display
    cv2.imshow("mouse", img)
    cv2.waitKey(1)
