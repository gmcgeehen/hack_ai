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

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame)

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)



    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        #Get points for comparisons
        landmarks = results.pose_landmarks.landmark
        hip_y = landmarks[mp_pose.PoseLandmark.LEFT_HIP].y
        knee_y = landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y

        # 🔽🔽 **Squat Detection Logic Goes Here** 🔽🔽
        if hip_y > knee_y and currentpos == "up":  # Squatting down
            currentpos = "down"
        elif hip_y < knee_y and currentpos == "down":  # Standing up
            currentpos = "up"
            count += 1  # Count rep

    # Display the count
    cv2.putText(frame, f"Reps: {count}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Pose Detection", frame)
    if cv2.waitKey(10) & 0xff == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()





#Now we need to find the coordinates of knees hips etc, so we can track their movement
#We will use the following code to do this

    