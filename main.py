import os
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# Variables
width, height = 1920, 1080
folderPath = "Presentation"

# Camera setup with DirectShow
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, width)
cap.set(4, height)

# Get the list of presentation images
pathImages = sorted(os.listdir(folderPath), key=len)

# Variable to keep track of the current image number
imgNumber = 0  # Start from 0 to avoid index errors
hs, ws = int(120 * 1), int(213 * 1)  # Webcam image size
gestureThreshold = 300
buttonPressed = False
buttonCounter = 0
buttonDelay = 30  # Corrected variable name from buttonDealy
annotations = [[]]
annotationsNumber = -1
annotationStart = False

# Hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    # Importing images from the camera
    success, img = cap.read()
    img = cv2.flip(img, 1)

    if not success:
        print("Failed to capture image")
        break

    # Get the current slide image
    if imgNumber < len(pathImages):
        pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
        imgCurrent = cv2.imread(pathFullImage)

        # Hand detection
        hands, img = detector.findHands(img, flipType=False)
        cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)

        if hands and not buttonPressed:
            hand = hands[0]

            # Check if required keys are present
            if 'lmlist' in hand and 'center' in hand:
                fingers = detector.fingersUp(hand)
                cx, cy = hand['center']
                lmlist = hand['lmlist']

                # Constraints for easier drawing
                xVal = int(np.interp(lmlist[8][0], [width // 2, width], [0, width]))
                yVal = int(np.interp(lmlist[8][1], [150, height - 150], [0, height]))
                indexFinger = (xVal, yVal)

                if cy <= gestureThreshold:  # If hand is at the height of the face
                    # Gesture 1-Left
                    if fingers == [1, 0, 0, 0, 0]:
                        print("Left")
                        buttonPressed = True
                        if imgNumber > 0:  # Ensure imgNumber doesn't go below 0
                            imgNumber -= 1

                    # Gesture 2-Right
                    if fingers == [0, 0, 0, 0, 1]:
                        print("Right")
                        buttonPressed = True
                        if imgNumber < len(pathImages) - 1:
                            imgNumber += 1

                # Gesture 3: show pointer
                if fingers == [0, 1, 1, 0, 0]:
                    cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)

                # Gesture 4: show pointer
                if fingers == [0, 1, 0, 0, 0]:
                    if not annotationStart:
                        annotationStart = True
                        annotationsNumber += 1
                        annotations.append([])
                    cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
                    annotations[annotationsNumber].append(indexFinger)
                else:
                    annotationStart = False



                  # Gesture 5 - Erase
                if fingers ==[0,1,1,1,0]:
                    if annotations:
                        annotations.pop(-1)
                        annotationsNumber -= 1
                        buttonPressed = True

                    else:
                        annotationStart = False

        # Button pressed iterations
        if buttonPressed:
            buttonCounter += 1
            if buttonCounter > buttonDelay:
                buttonCounter = 0
                buttonPressed = False

                for i in range(len(annotations)):
                    for j in range(len(annotations[i])):
                        if j != 0:  # Added missing colon
                            cv2.line(imgCurrent, annotations[i][j - 1], annotations[i][j], (0, 0, 200), 12)

        if imgCurrent is None:
            print(f"Failed to load image: {pathFullImage}")
            imgNumber = (imgNumber + 1) % len(pathImages)  # Skip to next image
            continue

        # Resize the webcam image correctly
        imgSmall = cv2.resize(img, (ws, hs))

        # Ensure we don't exceed the slide image dimensions
        h, w, _ = imgCurrent.shape
        if hs <= h and ws <= w:
            imgCurrent[0:hs, 0:ws] = imgSmall

        # Show the current slide and webcam feed
        cv2.imshow("Webcam Feed", img)
        cv2.imshow("Slides", imgCurrent)

    key = cv2.waitKey(1)
    if key == ord("q"):
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
