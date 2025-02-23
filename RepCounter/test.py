import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class Exercise:
    name: str
    threshold: float
    position_check: str
    feedback_messages: Dict[str, str]
    ideal_angles: Dict[str, Tuple[float, float]]  # min, max angles for perfect form
    common_mistakes: Dict[str, str]

class FormScoring:
    def __init__(self):
        self.rep_scores = []
        self.current_rep_deductions = []
        self.total_score = 0
        
    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360-angle
            
        return angle

    def get_joint_angles(self, landmarks, mp_pose):
        """Get relevant joint angles for exercise form analysis"""
        angles = {}
        
        # Get coordinates for key points
        landmarks_dict = {}
        for landmark in mp_pose.PoseLandmark:
            landmarks_dict[landmark.name] = [
                landmarks[landmark.value].x,
                landmarks[landmark.value].y,
                landmarks[landmark.value].visibility
            ]
        
        # Calculate right knee angle
        angles['right_knee'] = self.calculate_angle(
            landmarks_dict['RIGHT_HIP'],
            landmarks_dict['RIGHT_KNEE'],
            landmarks_dict['RIGHT_ANKLE']
        )
        
        # Calculate left knee angle
        angles['left_knee'] = self.calculate_angle(
            landmarks_dict['LEFT_HIP'],
            landmarks_dict['LEFT_KNEE'],
            landmarks_dict['LEFT_ANKLE']
        )
        
        # Calculate hip angles
        angles['right_hip'] = self.calculate_angle(
            landmarks_dict['RIGHT_SHOULDER'],
            landmarks_dict['RIGHT_HIP'],
            landmarks_dict['RIGHT_KNEE']
        )
        
        angles['left_hip'] = self.calculate_angle(
            landmarks_dict['LEFT_SHOULDER'],
            landmarks_dict['LEFT_HIP'],
            landmarks_dict['LEFT_KNEE']
        )
        
        # Calculate back angle (vertical alignment)
        # Using right side for reference
        spine_mid = [
            (landmarks_dict['RIGHT_HIP'][0] + landmarks_dict['LEFT_HIP'][0]) / 2,
            (landmarks_dict['RIGHT_HIP'][1] + landmarks_dict['LEFT_HIP'][1]) / 2,
            0
        ]
        spine_top = [
            (landmarks_dict['RIGHT_SHOULDER'][0] + landmarks_dict['LEFT_SHOULDER'][0]) / 2,
            (landmarks_dict['RIGHT_SHOULDER'][1] + landmarks_dict['LEFT_SHOULDER'][1]) / 2,
            0
        ]
        vertical_reference = [spine_mid[0], 0, 0]  # Point directly above hip
        
        angles['back'] = self.calculate_angle(spine_top, spine_mid, vertical_reference)
        
        return angles

    def evaluate_form(self, angles: dict, exercise: Exercise) -> Tuple[float, List[str]]:
        score = 10.0  # Start with perfect score
        feedback = []
    
        if exercise.name == "squats":
            # Use average of left and right angles
            knee_angle = (angles['right_knee'] + angles['left_knee']) / 2
            hip_angle = (angles['right_hip'] + angles['left_hip']) / 2
            back_angle = angles['back']
        
            # Check knee angle (should be around 90 degrees at bottom of squat)
            if knee_angle < 80 or knee_angle > 100:
                score -= 2.0
                feedback.append("Watch knee angle - aim for 90 degrees at bottom")
        
            # Check hip angle (parallel to ground)
            if hip_angle < 70 or hip_angle > 110:
                score -= 2.0
                feedback.append("Hips should be parallel at bottom")
        
            # Check back angle (should stay relatively vertical)
            if back_angle < 80 or back_angle > 100:
                score -= 2.0
                feedback.append("Keep your back straight")
        
            # Additional form checks
            if knee_angle < 60:  # Too deep
                score -= 1.0
                feedback.append("Squat depth too low")
        
            if back_angle < 70:  # Leaning too far forward
                score -= 1.0
                feedback.append("Leaning too far forward")
            
            # Add positive feedback if form is good
            if len(feedback) == 0:
                feedback.append("Great form!")
    
            # Ensure score doesn't go below 0
            score = max(0, score)
    
        return score, feedback


class RepCounter:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils
        self.count = 0
        self.current_pos = "up"
        self.in_position = False
        self.start_time = 0
        self.elapsed_time = 0
        self.form_scorer = FormScoring()
        self.workout_summary = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'exercise': '',
            'reps': [],
            'average_score': 0,
            'feedback_summary': []
        }
        
        # Text-to-speech setup
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)
        
        # Exercise configurations with form requirements
        self.exercises = {
            "squats": Exercise(
                name="squats",
                threshold=0.1,
                position_check="hip_below_knee",
                feedback_messages={"good": "Good Squat Depth", "bad": "Need Deeper Squat!"},
                ideal_angles={
                    'knee': (80, 100),  # Degrees for knee angle at bottom
                    'hip': (70, 90),    # Degrees for hip angle
                    'back': (80, 100)   # Degrees for back angle (vertical is 90)
                },
                common_mistakes={
                    'knee': "Knees going too far past toes",
                    'hip': "Not hitting parallel",
                    'back': "Leaning too far forward"
                }
            ),
            # Add configurations for other exercises here
        }

    def process_frame(self, frame, exercise_type: str):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            # Draw skeleton
            self.mp_drawing.draw_landmarks(
                frame_bgr, 
                results.pose_landmarks, 
                self.mp_pose.POSE_CONNECTIONS
            )
            
            # Get joint angles
            angles = self.form_scorer.get_joint_angles(results.pose_landmarks.landmark, self.mp_pose)
            
            # Evaluate form and get feedback
            exercise = self.exercises.get(exercise_type)
            if exercise:
                score, feedback = self.form_scorer.evaluate_form(angles, exercise)
                
                # Display real-time feedback
                self.display_feedback(frame_bgr, feedback, score)
                
                # Count reps and update scoring
                self.process_exercise(angles, exercise, score, feedback)

        # Display rep count and instructions
        self.display_stats(frame_bgr)
        
        return frame_bgr

    def process_exercise(self, angles: dict, exercise: Exercise, score: float, feedback: List[str]):
        """Process exercise movement and update scoring"""
        if exercise.name == "squats":
            # Use average of left and right knee angles
            avg_knee_angle = (angles['right_knee'] + angles['left_knee']) / 2
            
            if avg_knee_angle > 150 and self.current_pos == "up":  # Standing position
                self.current_pos = "down"
            elif avg_knee_angle < 100 and self.current_pos == "down":  # Squat position
                self.current_pos = "up"
                self.count += 1
                self.announce_rep_with_feedback(score, feedback)
                
                # Save rep data
                self.workout_summary['reps'].append({
                    'rep_number': self.count,
                    'score': score,
                    'feedback': feedback,
                    'angles': {
                        'knee_angle': avg_knee_angle,
                        'hip_angle': (angles['right_hip'] + angles['left_hip']) / 2,
                        'back_angle': angles['back']
                    }
                })
            
        elif exercise.name == "pushups":
            # Implement pushup-specific logic using shoulder and elbow angles
            pass

    def display_feedback(self, frame, feedback: List[str], score: float):
        """Display real-time feedback and score"""
        cv2.putText(frame, f"Score: {score:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        y_offset = 50
        for line in feedback:
            cv2.putText(frame, line, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            y_offset += 30

    def display_stats(self, frame):
        """Display rep count and instructions on screen"""
        cv2.putText(frame, f"Reps: {self.count}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    def announce_rep_with_feedback(self, score: float, feedback: List[str]):
        """Text-to-speech announcement of rep score"""
        self.engine.say(f"Rep {self.count} complete, score: {score:.2f}.")
        self.engine.say(" ".join(feedback))
        self.engine.runAndWait()


def main():
    cap = cv2.VideoCapture(0)  # Use webcam

    rep_counter = RepCounter()
    exercise_type = "squats"  # Change this based on the exercise you're doing

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame = rep_counter.process_frame(frame, exercise_type)
        cv2.imshow('Exercise Form Tracker', processed_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()