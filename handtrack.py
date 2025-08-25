import cv2
import mediapipe as mp
from gestureMapping import execute_function_for_gesture

# MediaPipe Hand model
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Use webcam
cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    max_num_hands=1,       # Detect only one hand for now
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
) as hands:

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Failed to read from camera.")
            break

        # Flip and convert color for MediaPipe
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Get frame dimensions
        frame_height, frame_width, _ = frame.shape

        # Process the frame
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Convert landmarks to list of [x, y] (normalized 0–1)
                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.append([lm.x, lm.y])

                # Call gesture logic
                execute_function_for_gesture(landmarks, frame_width, frame_height)

                # Draw hand landmarks
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )

                # Print landmark coordinates for debugging
                for i, lm in enumerate(hand_landmarks.landmark):
                    cx, cy = int(lm.x * frame_width), int(lm.y * frame_height)
                    cv2.putText(frame, str(i), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    # For debugging:
                    # print(f"Landmark {i}: ({cx}, {cy})")

        # Show the video feed
        cv2.imshow("Hand Tracking Debug View", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # Press ESC to exit
            break

cap.release()
cv2.destroyAllWindows()

