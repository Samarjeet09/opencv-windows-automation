import cv2
import pycaw
import time
import mediapipe
import handTrackingModule as handTM
import numpy as np
import screen_brightness_control as sbc

# pycaw setup
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# opencv
cam = cv2.VideoCapture(0)
cam.set(3, 1080)
cam.set(4, 720)
# our module setup
detector = handTM.handDetector(detectionConfi=0.7, trackingConfi=0.6)

# variables
currentTime = 0
prevTime = 0
lmListR = []
boundaryBoxR = []
displayPercentage = 0
displayBar = 420
area = 0
colorVolume = (420, 420, 69)

while True:
    success, img = cam.read()
    hands, img = detector.findHands(img)

    command = "No command"
    if hands:
        visibleHand = hands[0]
        if len(hands) == 1:
            if(visibleHand["type"] == "Left"):
                leftHand = hands[0]
                lmListL = leftHand["lmList"]
                boundaryBoxL = leftHand["bbox"]
                fingersL = detector.fingersUp(leftHand)
                fingersUpLeft = fingersL.count(1)
                # for now using count later can be extended for other gestures
                if fingersUpLeft == 0:
                    command = "Virtual Mouse"
                elif fingersUpLeft == 1:
                    command = "Volume Control"
                elif fingersUpLeft == 2:
                    command = "Brightness Control"
                elif fingersUpLeft == 3:
                    command = "comand 3"
                elif fingersUpLeft == 4:
                    command = "comand 4"
                elif fingersUpLeft == 5:
                    command = "comand 5"
            elif(visibleHand["type"] == "Right"):
                lmListR = visibleHand["lmList"]
                boundaryBoxR = visibleHand["bbox"]
                command = "Virtual Mouse"
                # space for virtual mouse code
        elif len(hands) == 2:
            if(hands[0]["type"] == "Right"):
                rightHand = hands[0]
                lmListR = hands[0]["lmList"]
                boundaryBoxR = hands[0]["bbox"]

                leftHand = hands[1]
                lmListL = hands[1]["lmList"]
                boundaryBoxL = hands[1]["bbox"]
                command = "Virtual Mouse"
            else:
                rightHand = hands[1]
                lmListR = hands[1]["lmList"]
                boundaryBoxR = hands[1]["bbox"]

                leftHand = hands[0]
                lmListL = hands[0]["lmList"]
                boundaryBoxL = hands[0]["bbox"]
            # now we will have R and L hands ki values respective variables mei
            fingersL = detector.fingersUp(leftHand)
            fingersUpLeft = fingersL.count(1)
            # for now using count later can be extended for other gestures
            if fingersUpLeft == 0:
                command = "Virtual Mouse"
            elif fingersUpLeft == 1:
                command = "Volume Control"
                if(len(lmListR) != 0):
                    area = boundaryBoxR[2] * boundaryBoxR[3] // 100
                    if 100 < area < 1000:
                        if 100 < area < 250:
                            maxLength = 100
                            minLenght = 10
                        else:
                            maxLength = 200
                            minLenght = 40
                    # Find distance  between index and thumb
                    length, lineInfo, img = detector.findDistance(
                        lmListR[4][0:2], lmListR[8][0:2], img)
                    # convert length to volume
                    displayBar = np.interp(
                        length, [minLenght, maxLength], [420, 69])
                    displayPercentage = np.interp(
                        length, [minLenght, maxLength], [0, 100])
                    incrementSteps = 5
                    displayPercentage = incrementSteps * \
                        round(displayPercentage / incrementSteps)
                    fingersR = detector.fingersUp(rightHand)
                    if fingersR[4]:
                        volume.SetMasterVolumeLevelScalar(
                            displayPercentage/100, None)
                        cv2.circle(img, (lineInfo[4], lineInfo[5]),
                                   6, (0, 255, 89), cv2.FILLED)  # indication ki vol set karidya
                        cv2.putText(img, f'setting mode', (100, 69),
                                    cv2.FONT_HERSHEY_PLAIN, 2, (69, 420, 69), 2)
                        colorVolume = (420, 69, 420)
                    else:
                        colorVolume = (420, 420, 69)
                    if length < 50:
                        cv2.circle(img, (lineInfo[4], lineInfo[5]),
                                   6, (420, 69, 69), cv2.FILLED)
                # drawings
                cv2.rectangle(img, (50, 69), (75, 420), (69, 69, 69), 3)
                cv2.rectangle(img, (50, int(displayBar)), (75, 420),
                              (69, 420, 420), cv2.FILLED)
                currentBrightness = int(
                    volume.GetMasterVolumeLevelScalar()*100)
                cv2.putText(img, f'Set Volume:{int(currentBrightness)}%', (400, 69),
                            cv2.FONT_HERSHEY_PLAIN, 2, colorVolume, 2)
                cv2.putText(img, f'{int(displayPercentage)}%', (30, 450),
                            cv2.FONT_HERSHEY_PLAIN, 2, (69, 420, 69), 2)
############################################################################################################################
            elif fingersUpLeft == 2:
                command = "Brightness Control"
                if(len(lmListR) != 0):
                    area = boundaryBoxR[2] * boundaryBoxR[3] // 100
                    if 100 < area < 1000:
                        if 100 < area < 250:
                            maxLength = 100
                            minLenght = 10
                        else:
                            maxLength = 200
                            minLenght = 40
                    # Find distance  between index and thumb
                    length, lineInfo, img = detector.findDistance(
                        lmListR[4][0:2], lmListR[8][0:2], img)
                    # convert length to volume
                    displayBar = np.interp(
                        length, [minLenght, maxLength], [420, 69])
                    displayPercentage = np.interp(
                        length, [minLenght, maxLength], [0, 100])
                    incrementSteps = 10
                    displayPercentage = incrementSteps * \
                        round(displayPercentage / incrementSteps)
                    fingersR = detector.fingersUp(rightHand)
                    if fingersR[4]:
                        sbc.set_brightness(displayPercentage, display=0)
                        cv2.circle(img, (lineInfo[4], lineInfo[5]),
                                   6, (0, 255, 89), cv2.FILLED)  # indication ki Brightness set karidya
                        cv2.putText(img, f'setting mode', (100, 69),
                                    cv2.FONT_HERSHEY_PLAIN, 2, (69, 420, 69), 2)
                        colorVolume = (420, 69, 420)
                    else:
                        colorVolume = (420, 420, 69)
                    if length < 50:
                        cv2.circle(img, (lineInfo[4], lineInfo[5]),
                                   6, (420, 69, 69), cv2.FILLED)
                # drawings
                cv2.rectangle(img, (50, 69), (75, 420), (69, 69, 69), 3)
                cv2.rectangle(img, (50, int(displayBar)), (75, 420),
                              (69, 420, 420), cv2.FILLED)
                currentBrightness = sbc.get_brightness()
                print(currentBrightness)
                cv2.putText(img, f'Set Brightness:{int(currentBrightness[0])}%', (400, 69),
                            cv2.FONT_HERSHEY_PLAIN, 2, colorVolume, 2)
                cv2.putText(img, f'{int(displayPercentage)}%', (30, 450),
                            cv2.FONT_HERSHEY_PLAIN, 2, (69, 420, 69), 2)
            elif fingersUpLeft == 3:
                command = "comand 3"
            elif fingersUpLeft == 4:
                command = "comand 4"
            elif fingersUpLeft == 5:
                command = "comand 5"

    # frame rate
    currentTime = time.time()
    fps = 1 / (currentTime - prevTime)
    prevTime = currentTime
    cv2.putText(img, f'FPS: {int(fps)}', (10, 50),
                cv2.FONT_HERSHEY_PLAIN, 2, (69, 420, 69), 2)

    cv2.putText(img, str(command), (60, 100),
                cv2.FONT_HERSHEY_TRIPLEX, 1, (420, 0, 0), 2)
    cv2.imshow("TEST HAI LOL", img)
    cv2.waitKey(1)