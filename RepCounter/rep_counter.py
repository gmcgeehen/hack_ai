import cv2
import mediapipe as mp
import numpy as np
import sys
import threading
import pyttsx3
import time
import queue

#Create a queue for TTS messages
tts_queue = queue.Queue()

#Setup voice engine
engine = pyttsx3.init()
engine.setProperty("rate", 200)
engine.setProperty("volume", 0.75)
voices = engine.getProperty("voices")

#Set voice to 0 because every device should work then
if voices:
    engine.setProperty("voice", voices[0].id)

is_running = True

#TTS worker function that runs in a separate thread
def tts_worker():
    while is_running:
        message = tts_queue.get()
        if message is None:
            break
        engine.say(message)
        engine.runAndWait()
        tts_queue.task_done()

#Start TTS thread
tts_thread = threading.Thread(target=tts_worker, daemon=True)
tts_thread.start()

#Check command line arguments
if len(sys.argv) < 2:
    print("Need more than 1 command line argument! Add in what exercise you would like to record. i.e python3 rep_counter.py squats")
    sys.exit(1)

#Grab the exercise type to comapre later
exercise_type = sys.argv[1]

#Setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 20)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('workout_session.mp4', fourcc, 20.0, (640, 480))
cv2.namedWindow("Pose Detection", cv2.WINDOW_NORMAL)  # Allow resizing
cv2.resizeWindow("Pose Detection", 640, 480)  # Set initial window size
#Initialize variables
count = 0
currentpos = "up"
threshold = 0.1
in_position = False
start_time = 0
elapsed_time = 0


#Main program loop
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        landmarks = results.pose_landmarks.landmark

        #Get landmarks
        right_hip_y = landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y
        left_hip_y = landmarks[mp_pose.PoseLandmark.LEFT_HIP].y
        right_knee_y = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y
        left_knee_y = landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y
        left_shoulder_y = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y 
        left_elbow_y = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y
        right_shoulder_y = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y 
        right_elbow_y = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y
        right_ankle_y = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y
        left_ankle_y = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y
        right_ankle_x = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x
        left_ankle_x = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x
        right_hip_x = landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x
        left_hip_x = landmarks[mp_pose.PoseLandmark.LEFT_HIP].x
        right_shoulder_x = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x 
        left_shoulder_x = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x

        # Exercise detection logic
        #Squats
        if exercise_type == "squats":
            if left_hip_y + right_hip_y > left_knee_y + right_knee_y - threshold and currentpos == "up":
                currentpos = "down"
            elif left_hip_y + right_hip_y < left_knee_y + right_knee_y - threshold and currentpos == "down":
                currentpos = "up"
                count += 1
                tts_queue.put(f"Squat {count} complete!")

        #Pushups
        elif exercise_type == "pushups":
            if left_shoulder_y + right_shoulder_y > left_elbow_y + right_elbow_y - threshold and currentpos == "up":
                currentpos = "down"
            elif left_shoulder_y + right_shoulder_y < left_elbow_y + right_elbow_y - threshold and currentpos == "down":
                currentpos = "up"
                count += 1
                tts_queue.put(f"Pushup {count} complete!")

        #Pullups
        elif exercise_type == "pullups":
            if left_shoulder_y + right_shoulder_y < left_elbow_y + right_elbow_y - threshold and currentpos == "down":
                currentpos = "up"
            elif left_shoulder_y + right_shoulder_y > left_elbow_y + right_elbow_y - threshold and currentpos == "up":
                currentpos = "down"
                count += 1
                tts_queue.put(f"Pullup {count} complete!")

        #Planks
        elif exercise_type == "planks":
            if abs(left_shoulder_y - left_hip_y) < threshold and abs(left_hip_y - left_knee_y) < threshold:
                if not in_position:
                    in_position = True
                    start_time = time.time()
            else:
                if in_position:
                    in_position = False
                    elapsed_time = time.time() - start_time
                    tts_queue.put(f"You held the plank for {int(elapsed_time)} seconds!")

            if in_position:
                elapsed_time = time.time() - start_time

            cv2.putText(frame, f"Plank Time: {int(elapsed_time)} seconds", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        #Legraises
        elif exercise_type == "legraises":
            if left_shoulder_x + right_shoulder_x < right_hip_x + left_hip_x:
                if left_ankle_x + right_ankle_x < left_hip_x + right_hip_x - threshold and currentpos == "down":
                    currentpos = "up"
                elif left_ankle_x + right_ankle_x > left_hip_x + right_hip_x - threshold and currentpos == "up":
                    currentpos = "down"
                    count += 1
                    tts_queue.put(f"Legraise {count} complete!")
            else:
                if left_ankle_x + right_ankle_x > left_hip_x + right_hip_x - threshold and currentpos == "down":
                    currentpos = "up"
                elif left_ankle_x + right_ankle_x < left_hip_x + right_hip_x - threshold and currentpos == "up":
                    currentpos = "down"
                    count += 1
                    tts_queue.put(f"Legraise {count} complete!")

    cv2.putText(frame, f"Reps: {count}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)   
    out.write(frame)

    #Message telling the user how to quit the program
    cv2.putText(frame, "Once you are done recording your reps, press Q to quit", (20, 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    #Name of the frame
    cv2.imshow("Pose Detection", frame)
    if cv2.waitKey(10) & 0xFF == ord("q"):
        break

#Cleanup
tts_queue.put(None)  # Signal the TTS thread to stop
tts_thread.join()    # Wait for the TTS thread to finish
is_running = False   #Set flag to false
cap.release()
out.release()
cv2.destroyAllWindows()