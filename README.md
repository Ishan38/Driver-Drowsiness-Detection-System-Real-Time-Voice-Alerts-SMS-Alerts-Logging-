# Driver Drowsiness Detection System  
Real-Time Detection | Voice Alerts | SMS Alerts | Logging

This project is an advanced **driver drowsiness monitoring system** that uses computer vision, voice alerts, and intelligent thresholds to identify early signs of fatigue. It detects **eye closure**, **yawning**, and **unsafe head tilting**, then warns the driver using **human-like voice messages** and optionally sends an **SMS alert** using Twilio.

---

## 🚗 Features

### 🔹 Real-Time Eye Closure Detection (EAR)
Identifies prolonged eye closure using the Eye Aspect Ratio. Alerts the driver when sleepiness is detected.

### 🔹 Yawn Detection (MAR)
Monitors mouth opening behavior and detects yawns, a major sign of fatigue.

### 🔹 3D Head Pose Detection
Uses 6 facial landmarks to compute head tilt angle. Warns the user when looking down or away from the road.

### 🔹 Human-Like Voice Alerts
Uses Windows SAPI or pyttsx3 to speak:
- **"Eyes closed"**  
- **"Yawn detected"**  
- **"Please keep head straight"**

### 🔹 SMS Alert System (Twilio)
Automatically sends an SMS on the first detected drowsiness event. Useful for:
- Fleet management  
- Parental monitoring  
- Safety supervisors  

### 🔹 Per-Run Logging System
Each run creates a timestamped CSV log file containing:
- Event type  
- Timestamp  
- EAR / MAR / Tilt values  

### 🔹 Cooldown + State Change Logic
Prevents repetitive alerts while maintaining fast, accurate responses.

---

## 🛠 Technologies Used
- **Python 3.6**
- **OpenCV**
- **Dlib (68-point landmark model)**
- **NumPy**
- **Twilio API**
- **pyttsx3 / win32com (TTS)**
- **Threading**

---

## 📦 Installation

### 1. Clone the Repository
```sh
git clone https://github.com/your-username/Driver-Drowsiness-Detection.git
cd Driver-Drowsiness-Detection
