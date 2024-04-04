import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import ttk
from screeninfo import get_monitors
import threading
import win32api
from PIL import Image, ImageTk
import time
import ttkthemes as ThemedTk
import pyautogui

class HandDetector:
    def __init__(self):
        self.detect_hand = False # Flag to control hand detection

        # Default parameters for hand detection
        self.detection_confidence = 0.5
        self.tracking_confidence = 0.5
        self.cursor_sensitivity = 1.0
        self.pinch_threshold = 0.03  # Threshold for pinch detection
        
        # Pinch state variables
        self.pinch_detected = False
        self.prev_pinch_distance = None
        self.prev_pinch_state = False

        # Create main window
        self.root = ThemedTk.ThemedTk()
        self.root.get_themes()
        self.root.set_theme("equilux")  # Choose a modern theme
        
        self.root.title("Hand Gesture Control")
        self.root.geometry("800x600")

        # Main frame for GUI elements
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Canvas for displaying video feed
        self.canvas = tk.Canvas(self.main_frame, width=640, height=480, bg='black', highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=20, pady=20)

        # Frame for parameters
        self.params_frame = ttk.Frame(self.main_frame)
        self.params_frame.pack(side=tk.RIGHT, padx=20, pady=20, fill='y')

        # Labels and sliders for parameters
        self.detection_confidence_label = ttk.Label(self.params_frame, text="Detection Confidence")
        self.detection_confidence_label.grid(row=0, column=0, padx=10, pady=5)
        self.detection_confidence_slider = ttk.Scale(self.params_frame, from_=0, to=1, length=200, orient=tk.HORIZONTAL, command=self.update_detection_confidence)
        self.detection_confidence_slider.set(self.detection_confidence)
        self.detection_confidence_slider.grid(row=0, column=1, padx=10, pady=5)

        self.tracking_confidence_label = ttk.Label(self.params_frame, text="Tracking Confidence")
        self.tracking_confidence_label.grid(row=1, column=0, padx=10, pady=5)
        self.tracking_confidence_slider = ttk.Scale(self.params_frame, from_=0, to=1, length=200, orient=tk.HORIZONTAL, command=self.update_tracking_confidence)
        self.tracking_confidence_slider.set(self.tracking_confidence)
        self.tracking_confidence_slider.grid(row=1, column=1, padx=10, pady=5)

        self.cursor_sensitivity_label = ttk.Label(self.params_frame, text="Cursor Sensitivity")
        self.cursor_sensitivity_label.grid(row=2, column=0, padx=10, pady=5)
        self.cursor_sensitivity_slider = ttk.Scale(self.params_frame, from_=0.5, to=2, length=200, orient=tk.HORIZONTAL, command=self.update_cursor_sensitivity)
        self.cursor_sensitivity_slider.set(self.cursor_sensitivity)
        self.cursor_sensitivity_slider.grid(row=2, column=1, padx=10, pady=5)

        # Start/Stop button for hand detection
        self.start_stop_button = ttk.Button(self.params_frame, text="START", command=self.toggle_detection)
        self.start_stop_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Create threading lock
        self.lock = threading.Lock()

    def toggle_detection(self):
        self.detect_hand = not self.detect_hand
        if self.detect_hand:
            # Start a new thread for hand detection
            threading.Thread(target=self.detect_hand_landmarks, daemon=True).start()

    def stop_detection(self):
        # Stop hand detection
        self.detect_hand = False
        print("Hand detection stopped.")

    def detect_hand_landmarks(self):
        # Detect hand landmarks using MediaPipe
        cap = cv2.VideoCapture(0)
        mp_hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=self.detection_confidence, min_tracking_confidence=self.tracking_confidence)
        
        last_cursor_pos = win32api.GetCursorPos()
        last_time = time.time()
        
        while self.detect_hand:
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = mp_hands.process(frame_rgb)
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        center_x, center_y = self.calculate_hand_center(hand_landmarks.landmark, frame.shape)
                        screen_x, screen_y = self.map_to_screen_coordinates(center_x, center_y, frame.shape[1], frame.shape[0])
                        
                        current_time = time.time()
                        time_diff = current_time - last_time
                        if time_diff > 0:
                            cursor_speed_x = (screen_x - last_cursor_pos[0]) / time_diff
                            cursor_speed_y = (screen_y - last_cursor_pos[1]) / time_diff
                            cursor_pos_x = last_cursor_pos[0] + cursor_speed_x * 0.006 * self.cursor_sensitivity # Adjust cursor sensitivity
                            cursor_pos_y = last_cursor_pos[1] + cursor_speed_y * 0.006 * self.cursor_sensitivity # Adjust cursor sensitivity
                            win32api.SetCursorPos((int(cursor_pos_x), int(cursor_pos_y)))
                            last_cursor_pos = (int(cursor_pos_x), int(cursor_pos_y))
                            last_time = current_time
                        
                        self.draw_landmarks(frame, hand_landmarks.landmark)
                        
                        # Detect pinch gesture
                        thumb_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
                        index_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
                        thumb_index_distance = np.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
                        
                        # Check if pinch is detected
                        pinch_detected = thumb_index_distance < self.pinch_threshold
                        
                        if pinch_detected and not self.prev_pinch_state:
                            print("Pinch started!")
                            pyautogui.mouseDown()  # Simulate mouse click down
                        elif not pinch_detected and self.prev_pinch_state:  # Release mouse click when pinch ends
                            print("Pinch ended!")
                            pyautogui.mouseUp()  # Simulate mouse click up
                        # Update previous pinch state
                        self.prev_pinch_state = pinch_detected
                self.display_frame(frame)

    def display_frame(self, frame):
        # Display frame with detected landmarks
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img_tk = ImageTk.PhotoImage(image=img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        self.root.img = img_tk

    def calculate_hand_center(self, landmarks, frame_shape):
        # Calculate the center of the hand
        landmarks_x = [lm.x * frame_shape[1] for lm in landmarks]
        landmarks_y = [lm.y * frame_shape[0] for lm in landmarks]
        center_x = int(np.mean(landmarks_x))
        center_y = int(np.mean(landmarks_y))
        return center_x, center_y

    def map_to_screen_coordinates(self, camera_x, camera_y, camera_width, camera_height):
        # Map camera coordinates to screen coordinates
        screen_widths = [monitor.width for monitor in get_monitors()]
        screen_height = self.root.winfo_screenheight()
        
        total_screen_width = sum(screen_widths)
        screen_boundaries = np.cumsum(screen_widths)
        screen_index = 0
        while screen_index < len(screen_boundaries) and camera_x > screen_boundaries[screen_index]:
            screen_index += 1
        relative_x = camera_x - sum(screen_widths[:screen_index])
        relative_y = camera_y
        screen_x = int(np.interp(relative_x, [0, camera_width], [0, screen_widths[screen_index]]))
        screen_y = int(np.interp(relative_y, [0, camera_height], [0, screen_height]))
        return screen_x, screen_y

    def draw_landmarks(self, frame, landmarks):
        # Draw landmarks on the frame
        for landmark in landmarks:
            cx, cy = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
            cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

    def update_detection_confidence(self, value):
        # Update the detection confidence
        self.detection_confidence = float(value)

    def update_tracking_confidence(self, value):
        # Update the tracking confidence
        self.tracking_confidence = float(value)

    def update_cursor_sensitivity(self, value):
        # Update the cursor sensitivity
        self.cursor_sensitivity = float(value)

    def on_close(self):
        # Stop hand detection when closing the application
        self.stop_detection()
        self.root.destroy()

if __name__ == "__main__":
    hand_detector = HandDetector()
    hand_detector.root.protocol("WM_DELETE_WINDOW", hand_detector.on_close)
    hand_detector.root.mainloop()