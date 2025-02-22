#Create the list of imports for the project that we are going to be using.
import cv2
import mediapipe as mp
import numpy as np
import sys

# #Importing a tts so that it can count your reps for you actively!
# import pyttsx3

#Importing a time for planks and maybe also just having an active timer for workouts!
import time
start_time = time.time()

# engine = pyttsx3.init()
# engine.setProperty("rate", 150)  #Adjust speaking speed if needed

#Check if the correct number of arguments are provided
if len(sys.argv) < 2:
    print("Need more than 1 command line argument! Add in what excercise you would like to record. i.e python3 rep_counter.py squats")
    sys.exit(1)

#Get the exercise type from command line args
exercise_type = sys.argv[1] 


#Setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

#Take webcam footage
cap = cv2.VideoCapture(0)

#Initialize the count and the current position for the rep counter to work
count = 0
currentpos = "up"
threshold = 0.1  #Small threshold to prevent errors

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
        landmarks = results.pose_landmarks.landmark
        #Get points for comparisons (we want the y coordianted because thats the plane that matters)
        right_hip_y = landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y
        left_hip_y = landmarks[mp_pose.PoseLandmark.LEFT_HIP].y
        right_knee_y = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y
        left_knee_y = landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y
        left_shoulder_y = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y 
        left_elbow_y = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y
        right_shoulder_y = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y 
        right_elbow_y = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y


        #Logic for squats
        if exercise_type == "squats":
            if left_hip_y + right_hip_y > left_knee_y + right_knee_y - threshold and currentpos == "up":
                currentpos = "down"
            elif left_hip_y +right_hip_y < left_knee_y + right_knee_y - threshold and currentpos == "down":
                currentpos = "up"
                count += 1
        
        #Logic for pushups
        elif exercise_type == "pushups":
            if left_shoulder_y + right_shoulder_y > left_elbow_y + right_elbow_y - threshold and currentpos == "up":
                currentpos = "down"
            elif left_shoulder_y + right_shoulder_y < left_elbow_y + right_elbow_y - threshold and currentpos == "down":
                currentpos = "up"
                count += 1

        #Logic for pullups
        elif exercise_type == "pullups":
             if left_shoulder_y + right_shoulder_y < left_elbow_y + right_elbow_y - threshold and currentpos == "down":
                currentpos = "up"
             elif left_shoulder_y + right_shoulder_y > left_elbow_y + right_elbow_y - threshold and currentpos == "up":
                currentpos = "down"
                count += 1

            
        #Logic for lunges
        # elif sys.argv[1] == "lunges":
        #     pass
        #Logic for planks
        # elif exercise_type == "planks":
        #     pass
        #Logic for legaises
        # elif exercise_type == "legraises":
        #     pass





     
    #Display the count and the quit message
    cv2.putText(frame, f"Reps: {count}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(frame, "Once you are done recording your reps, press Q to quit", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Pose Detection", frame)
    if cv2.waitKey(10) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()





    