#Create the list of imports for the project that we are going to be using.
import cv2
import mediapipe as mp
import numpy as np


#Setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

#Initialize the count and the current position for the rep counter to work
count = 0
currentpos = "up"
threshold = 0.1  # Small threshold to prevent errors

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame)

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)


    #Squat functionality need to add command line arguments for it to pass within this function
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        #Get points for comparisons (we want the y coordianted because thats the plane that matters)
        right_hip_y = landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y
        left_hip_y = landmarks[mp_pose.PoseLandmark.LEFT_HIP].y
        right_knee_y = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y
        left_knee_y = landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y
        





    #Push Up Functionality
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        #Get joint points
        landmarks = results.pose_landmarks.landmark
        left_shoulder_y = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y 
        left_elbow_y = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y
        right_shoulder_y = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y 
        right_elbow_y = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y

        if left_shoulder_y > left_elbow_y - threshold and currentpos == "up":
            currentpos = "down"
        elif left_shoulder_y < left_elbow_y - threshold and currentpos == "down":
            currentpos = "up"
            count += 1

    #Display the count
    cv2.putText(frame, f"Reps: {count}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Pose Detection", frame)
    if cv2.waitKey(10) & 0xff == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()





    