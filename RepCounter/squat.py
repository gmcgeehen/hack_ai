        landmarks = results.pose_landmarks.landmark
        right_hip_y = landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y
        left_hip_y = landmarks[mp_pose.PoseLandmark.LEFT_HIP].y
        right_knee_y = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y
        left_knee_y = landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y

        # Detect which leg is squatting (based on the knee position)
        right_knee_angle = right_hip_y - right_knee_y  # Helps to identify if right leg is bent
        left_knee_angle = left_hip_y - left_knee_y  # Helps to identify if left leg is bent

        threshold = 0.1  # Set a threshold for squat motion

        # Two-Legged Squat Detection Logic
        if right_knee_angle > left_knee_angle:
            # Right leg is more bent
            if right_hip_y > right_knee_y + threshold and currentpos == "up":  # Squatting down (right leg)
                currentpos = "down"
            elif right_hip_y < right_knee_y - threshold and currentpos == "down":  # Standing up (right leg)
                currentpos = "up"
                count += 1  # Increment rep
        else:
            # Left leg is more bent
            if left_hip_y > left_knee_y + threshold and currentpos == "up":  # Squatting down (left leg)
                currentpos = "down"
            elif left_hip_y < left_knee_y - threshold and currentpos == "down":  # Standing up (left leg)
                currentpos = "up"
                count += 1  # Increment rep

        # Additional check for ensuring both legs are squatting:
        # Optional logic to make sure both knees bend to perform a full squat (for two-legged squats)
        if right_knee_angle > threshold and left_knee_angle > threshold:  # Both knees are bent
            # Active two-legged squat motion
            if currentpos == "up":
                currentpos = "down"  # Continue detecting as squatting down
            elif currentpos == "down":
                count += 1  # Increment rep when both legs stand up after squatting
                currentpos = "up"  # Change state to standing up