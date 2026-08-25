# Portal

An AI-powered computer vision project that creates an interactive **fire portal controlled by hand gestures** using a webcam.

The system detects hand movements in real time and uses them to open and close an animated portal. It combines computer vision, hand tracking, gesture recognition, and real-time graphics.

## 🖼️ Project Preview

![AI Hand Controlled Portal](assets/portal.png)

> Add your portal screenshot inside the `assets` folder and name it `portal.png`.

---

## ✨ Features

* 🖐️ Real-time hand tracking
* 🤲 Two-hand gesture detection
* 🔥 Animated fire portal
* 🌀 Circular hand movement detection
* ✋ Open-palm gesture to open the portal
* ✊ Both-fists gesture to close the portal
* 🎥 Real-time webcam processing
* ✨ Fire glow, sparks and rotating portal rings
* 🎯 Smooth portal movement and animation
* 🧠 AI-based computer vision interaction

---

## 🛠️ Technologies & Libraries

### 1. OpenCV

**Library:** `opencv-python`

OpenCV handles the webcam feed and real-time image processing. It is also used to draw the portal, rings, glow, animations, masks and other visual effects.

### 2. MediaPipe

**Library:** `mediapipe`

MediaPipe is used for **real-time hand tracking and hand landmark detection**. The project can track up to two hands and use their positions for gesture detection.

### 3. NumPy

**Library:** `numpy`

NumPy is used for fast numerical operations and image/matrix processing. It is also used for creating masks, manipulating frames and generating parts of the portal effects.

### 4. Math

**Library:** Python built-in `math`

The `math` module is used for calculations involving angles, circular movement, coordinates and portal animation.

### 5. Collections

**Library:** Python built-in `collections`

`deque` is used to maintain recent hand movement history, which helps detect circular hand movements.

---

## 📦 Installation

Make sure Python is installed on your system.

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

Activate it on Windows CMD:

```cmd
venv\Scripts\activate
```

Install the required libraries:

```bash
pip install opencv-python mediapipe numpy
```

---

## ▶️ Run the Project

Run the main Python file:

```bash
python main_final_v2.py
```

The project will automatically access your webcam.

---

## 🎮 Controls

### Keyboard Controls

| Key | Action                   |
| --- | ------------------------ |
| `B` | Capture clean background |
| `C` | Test / Open portal       |
| `X` | Close portal             |
| `Q` | Exit                     |

### Hand Gestures

| Gesture                   | Action       |
| ------------------------- | ------------ |
| ✋ Open palms              | Open portal  |
| ✊ Both fists              | Close portal |
| 🌀 Circular hand movement | Open portal  |

The project also displays the current portal state such as **PORTAL READY**, **PORTAL OPENING**, **PORTAL ACTIVE** and **PORTAL CLOSING**.

---

## ⚙️ How It Works

1. The webcam captures the user's video.
2. OpenCV processes the camera frames.
3. MediaPipe detects the user's hands and hand landmarks.
4. The system calculates hand positions and distance.
5. Gesture logic identifies open palms, fists and circular movement.
6. When the correct gesture is detected, the portal animation starts.
7. OpenCV renders the animated portal, fire effects, glow and rotating rings in real time.
8. The portal can then be closed using the required gesture.

---

## 🔥 Portal Effects

The project includes several real-time visual effects:

* Main portal ring
* Inner and outer rings
* Rotating arcs
* Fire glow
* Fire sparks
* Background masking
* Smooth opening animation
* Smooth closing animation

---

## 📁 Project Structure

```text
portal/
│
├── main_final_v2.py
├── portal_fire_sparks.py
├── assets/
│   └── portal.png
│
├── .gitignore
└── README.md
```

> `venv/` should not be uploaded to GitHub. The project uses `.gitignore` to exclude the virtual environment.

---

## 📋 Requirements

```text
Python 3.11
OpenCV
MediaPipe
NumPy
```

Install all main dependencies with:

```bash
pip install opencv-python mediapipe numpy
```

---

## 🚀 Future Improvements

* Voice-controlled portal
* More hand gestures
* Multiple portal types
* 3D portal effects
* Background replacement
* Gesture-based application control
* AR/VR integration
* Better particle and fire effects

---

## 👨‍💻 Author

**Prashant Singh**

GitHub:
https://github.com/prashant-singh-78

---

## ⭐ Support

If you like this project, consider giving the repository a ⭐ on GitHub.
