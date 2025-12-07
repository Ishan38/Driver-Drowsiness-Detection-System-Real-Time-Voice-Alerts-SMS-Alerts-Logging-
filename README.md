# Driver Drowsiness Detection System  
Real-Time Detection | Voice Alerts | SMS Alerts | Logging

This project is an advanced **driver drowsiness monitoring system** that uses computer vision, voice alerts, and intelligent thresholds to identify early signs of fatigue. It detects **eye closure**, **yawning**, and **unsafe head tilting**, then warns the driver using **human-like voice messages** and optionally sends an **SMS alert** using Twilio.

---

🎯 Features
Core Detection Capabilities

Eye Aspect Ratio (EAR) - Detects eye closure and blink patterns
Mouth Aspect Ratio (MAR) - Identifies yawning behavior
Head Pose Estimation - Monitors head tilt angle for drowsiness signs

Enhanced Alert System

✅ Smart Alert Management - Prevents excessive/continuous beeping
✅ State Change Detection - Alerts only on new drowsiness events
✅ Configurable Cooldown Timers - Customizable alert frequencies
✅ Voice Warnings - Natural human voice alerts using Windows SAPI/pyttsx3
✅ SMS Notifications - Sends SMS alert on first drowsiness detection
✅ Visual Indicators - Real-time on-screen warnings

Data Logging & Analysis

📊 Timestamped event logging (CSV format)
📝 Unique log file per session
📈 Records EAR, MAR, and head tilt values
🕐 Real-time date and time stamps

🎬 Demo
Detection in Action
The system monitors three key indicators:

Eyes Closed Detection

Triggers when Eye Aspect Ratio < 0.25 for 3+ consecutive frames
Voice Alert: "Eyes closed"


Yawn Detection

Triggers when Mouth Aspect Ratio > 0.79
Voice Alert: "Yawn detected"


Head Tilt Warning

Triggers when head angle exceeds 30 degrees
Voice Alert: "Please keep head straight"




