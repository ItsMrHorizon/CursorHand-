Hand-Controlled Mouse using MediaPipe
=====================================

Project Overview
----------------
This is a gesture-based mouse control application that uses your webcam and MediaPipe Hand Landmarker to:
- Move the cursor with your index finger tip
- Perform left-clicks via a pinch gesture (thumb + index finger)

It is designed for Windows (tested on Windows 10/11) and runs in real-time with visual wireframe feedback.

Current Features
----------------
- Smooth cursor movement following index finger tip
- Pinch-to-click (thumb tip + index tip close together)
- Full hand wireframe visualization (green points + white connections)
- Exponential smoothing for trackpad-like cursor feel
- Detection persistence to reduce flickering
- FPS display and status messages
- Low-resolution camera input for better performance

Requirements
------------
- Windows 10 or 11 (recommended)
- Python 3.9 – 3.12
- Webcam (built-in or external)
- Administrator privileges (required for mouse control via PyAutoGUI)

Installation Instructions
-------------------------

1. Install Python
   - Download and install Python 3.10 or 3.11 from https://www.python.org
   - Make sure to check "Add Python to PATH" during installation

2. Open Command Prompt as Administrator
   - Press Win + S → type "cmd" → right-click → Run as administrator

3. Navigate to your project folder
   cd C:\Users\YourUsername\Downloads\hand-mouse-project
   (replace with your actual folder path)

4. Create a virtual environment (recommended)
   python -m venv venv
   venv\Scripts\activate

5. Install required packages
   pip install mediapipe opencv-python pyautogui

   Note: If you previously installed a newer MediaPipe version, downgrade to a stable one:
   pip uninstall mediapipe -y
   pip install mediapipe==0.10.14

6. Save the script
   - Save the main script as hand_mouse.py in your project folder

7. Run the program
   python hand_mouse.py

   → A window should open showing your camera feed with hand wireframe
   → Move index finger to control cursor
   → Pinch thumb + index finger to left-click

Usage Guide
-----------
Controls:
- Index finger tip → moves the cursor
- Pinch (thumb tip close to index tip) → left click
- Press 'q' on keyboard → quit the application

Tips for best performance:
- Sit 50–70 cm from the camera
- Use even, bright lighting (avoid strong backlighting)
- Plain background helps detection
- Palm facing camera, fingers clearly visible
- Run Command Prompt as Administrator

Troubleshooting
---------------
- Cursor doesn't move → Run as Administrator
- Very low FPS (under 8) → Increase FRAME_SKIP to 4 or 5 in the script
- Grey lines / tearing in camera window → Normal at low FPS; try higher FRAME_SKIP or lower resolution
- Hand not detected reliably → Improve lighting or lower confidence thresholds in script

Planned Optimizations & Future Updates
--------------------------------------
Short-term (next 1–3 versions):
- Dynamic calibration routine (point to screen corners)
- Right-click and double-click gestures
- Scroll support (two-finger vertical movement)
- Adjustable click threshold via on-screen slider or config file
- Better flicker reduction with longer persistence + prediction

Medium-term:
- Kalman filter or low-pass filter for even smoother cursor
- Optional GPU acceleration (requires custom MediaPipe build with CUDA)
- Background subtraction to improve detection in complex environments
- Multi-monitor support

Long-term (if interest continues):
- Voice command fallback/integration
- Multiple hand modes (left/right hand selection)
- Gesture customization interface
- Packaging as standalone .exe (using PyInstaller)

Feedback & Contributions
------------------------
If you find bugs, have performance issues, or want specific features,
feel free to report them. This project is open for improvement.

Enjoy gesture control!

Last updated: February 2026
