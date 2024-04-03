# LHandC
 Translate hand gestures and position to a cursor

# Hand Gesture Control with Python

This Python script utilizes the MediaPipe library to detect hand gestures from a webcam feed and control the cursor movement on the screen accordingly. It allows users to perform pinch gestures to simulate mouse clicks.

## Requirements
- Python 3.x
- OpenCV (cv2)
- MediaPipe
- NumPy
- Pillow
- Tkinter
- win32api
- ttkthemes
- screeninfo

## Installation
1. Make sure you have Python installed on your system.
2. Install the required Python packages using pip:
pip install opencv-python mediapipe numpy pillow tk ttkthemes
3. Additionally, if you are on a Windows system, install the `pywin32` package:
pip install pywin32
## Usage
1. Run the `hand_gesture_control.py` script using Python.
2. Adjust the detection confidence, tracking confidence, and cursor sensitivity sliders to fine-tune the hand detection and cursor movement.
3. Click the "START" button to initiate hand gesture control.
4. Perform pinch gestures (bringing thumb and index finger close together) to simulate mouse clicks.
5. Click the "START" button again to stop hand gesture control.

## Features
- Real-time hand gesture detection and cursor control.
- Adjustable parameters for detection confidence, tracking confidence, and cursor sensitivity.
- Pinch gesture recognition for mouse clicks.

## Credits
This project utilizes the MediaPipe library for hand tracking and gesture recognition.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author
Ihab ELbani ALIAS Eurekios

