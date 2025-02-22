#Create the list of imports for the project that we are going to be using.
import cv2
import mediapipe as mp
import numpy as np



mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame)

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)



    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)


    cv2.imshow("Pose Detection", frame)
    if cv2.waitKey(10) & 0xff == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()







    