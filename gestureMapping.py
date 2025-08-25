import csv
import controller
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Gesture definition structure
class Gesture:
    def __init__(self, name, condition, action, priority):
        self.name = name
        self.condition = condition
        self.action = action
        self.priority = int(priority)

# Load gesture config from CSV and sort by priority
def load_gestures(csv_path):
    gestures = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            gestures.append(Gesture(
                row["GestureName"],
                row["Condition"],
                row["Action"],
                row["Priority"]
            ))
    gestures.sort(key=lambda g: g.priority)
    return gestures

# Helper function for gesture conditions
def distance(i, j, landmarks):
    xi, yi = landmarks[i]
    xj, yj = landmarks[j]
    return ((xi - xj) ** 2 + (yi - yj) ** 2) ** 0.5

# Evaluate condition string using current landmark coordinates
def evaluate_condition(condition_str, landmarks):
    local_scope = {
        "distance": lambda i, j: distance(i, j, landmarks),
        "landmarks": landmarks
    }
    try:
        return eval(condition_str, {}, local_scope)
    except Exception as e:
        print(f"[Eval Error] {e}")
        return False

# Initialize gesture list once
GESTURES = load_gestures("gestures.csv")

 #Main callable function
def execute_function_for_gesture(landmarks, frame_width, frame_height):


    # Convert normalized landmarks to absolute handPos
    handPos = [
        [lm[0] * frame_width, lm[1] * frame_height] for lm in landmarks
    ]
    print("Checking Gesture:")
    for gesture in GESTURES:
        
        if evaluate_condition(gesture.condition, landmarks):
            print("Condition " + gesture.condition + " fulfilled")
            if hasattr(controller, gesture.action):
                print(f"[Gesture] Triggered: {gesture.name}")
                getattr(controller, gesture.action)(handPos, frame_width, frame_height)
                break

