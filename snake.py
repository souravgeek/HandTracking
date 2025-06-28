# Import necessary libraries and modules
import math            # Standard math functions
import random          # Module for generating random numbers
import cvzone           # Library extending OpenCV functionalities
import cv2              # OpenCV library for computer vision and image processing
import numpy as np      # Numerical operations library
from cvzone.HandTrackingModule import HandDetector  # Hand tracking module from cvzone

# Initialize video capture from the default camera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Set the width of captured frames to 1280 pixels
cap.set(4, 720)   # Set the height of captured frames to 720 pixels

# Initialize a HandDetector object for hand tracking,
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Define a class representing the Snake Game
class SnakeGameClass:
    def __init__(self, pathFood):
        # Initialize snake game parameters
        self.points = []           # All points of the snake
        self.lengths = []          # Distance between each point
        self.currentLength = 0     # Total length of the snake
        self.allowedLength = 150   # Total allowed length
        self.previousHead = 0, 0   # Previous head point

        # Load the image for the food
        self.imgFood = cv2.imread(pathFood, cv2.IMREAD_UNCHANGED)
        self.hFood, self.wFood, _ = self.imgFood.shape
        self.foodPoint = 0, 0
        self.randomFoodLocation()

        self.score = 0
        self.gameOver = False

    # Method to set random coordinates for the food
    def randomFoodLocation(self):
        self.foodPoint = random.randint(100, 1000), random.randint(100, 600)

    # Method to update the game state based on the current position of the snake's head
    def update(self, imgMain, currentHead):
        if self.gameOver:
            # Display "Game Over" message and the score
            cvzone.putTextRect(imgMain, "Game Over", [300, 400],
                               scale=7, thickness=5, offset=20)
            cvzone.putTextRect(imgMain, f'Your Score: {self.score}', [300, 550],
                               scale=7, thickness=5, offset=20)
        else:
            px, py = self.previousHead
            cx, cy = currentHead

            # Update snake's state
            self.points.append([cx, cy])
            distance = math.hypot(cx - px, cy - py)
            self.lengths.append(distance)
            self.currentLength += distance
            self.previousHead = cx, cy

            # Length Reduction
            if self.currentLength > self.allowedLength:
                for i, length in enumerate(self.lengths):
                    self.currentLength -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength < self.allowedLength:
                        break

            # Check if snake ate the Food
            rx, ry = self.foodPoint
            if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and \
                    ry - self.hFood // 2 < cy < ry + self.hFood // 2:
                self.randomFoodLocation()
                self.allowedLength += 50
                self.score += 1
                print(self.score)

            # Draw Snake
            if self.points:
                for i, point in enumerate(self.points):
                    if i != 0:
                        cv2.line(imgMain, tuple(self.points[i - 1]), tuple(self.points[i]), (0, 0, 255), 20)
                cv2.circle(imgMain, tuple(self.points[-1]), 20, (0, 255, 0), cv2.FILLED)

            # Draw Food
            imgMain = cvzone.overlayPNG(imgMain, self.imgFood,
                                        (rx - self.wFood // 2, ry - self.hFood // 2))

            # Display the score
            cvzone.putTextRect(imgMain, f'Score: {self.score}', [50, 80],
                               scale=3, thickness=3, offset=10)

            # Check for Collision
            pts = np.array(self.points[:-2], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(imgMain, [pts], False, (0, 255, 0), 3)
            minDist = cv2.pointPolygonTest(pts, (cx, cy), True)

            if -1 <= minDist <= 1:
                # Handle collision
                print("Hit")
                self.gameOver = True
                self.points = []            # All points of the snake
                self.lengths = []           # Distance between each point
                self.currentLength = 0      # Total length of the snake
                self.allowedLength = 150    # Total allowed Length
                self.previousHead = 0, 0    # Previous head point
                self.randomFoodLocation()

        return imgMain

# Create an instance of the SnakeGameClass with the path to the food image
game = SnakeGameClass("donut.png")

# Main game loop
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)

    # If hands are detected, update the game based on the position of the index finger
    if hands:
        lmList = hands[0]['lmList']
        pointIndex = lmList[8][0:2]
        img = game.update(img, pointIndex)

    # Display the current frame in a window
    cv2.imshow("Image", img)

    # Check for key presses
    key = cv2.waitKey(1)
    if key == ord('r'):
        # Restart the game if the 'r' key is pressed
        game.gameOver = False
