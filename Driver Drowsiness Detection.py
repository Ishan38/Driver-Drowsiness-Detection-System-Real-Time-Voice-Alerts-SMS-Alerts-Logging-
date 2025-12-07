from scipy.spatial import distance as dist
from imutils import face_utils
import imutils
import time
import dlib
import math
import cv2
import numpy as np
from EAR import eye_aspect_ratio
from MAR import mouth_aspect_ratio
from HeadPose import getHeadTiltAndCoords

import csv
from datetime import datetime
import os
import winsound
import threading

TTS_AVAILABLE = False
USE_WIN32_SPEECH = False

try:
    import win32com.client
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    USE_WIN32_SPEECH = True
    TTS_AVAILABLE = True
    print("[INFO] Text-to-Speech enabled successfully (Windows SAPI)!")
except Exception as e:
    print(f"[WARNING] Windows SAPI error: {e}")
    
    try:
        import pyttsx3
        tts_engine = pyttsx3.init()
        tts_engine.setProperty('rate', 150)
        tts_engine.setProperty('volume', 1.0)
        TTS_AVAILABLE = True
        print("[INFO] Text-to-Speech enabled successfully (pyttsx3)!")
    except Exception as e2:
        print(f"[WARNING] pyttsx3 error: {e2}")
        print("          Using beep sounds instead.")
        tts_engine = None


ENABLE_SMS_ALERT = True  
PHONE_NUMBER = "+917409222430" 
TWILIO_ACCOUNT_SID = "AC0d99ef1d8f02c90454102e266b52a79d"  
TWILIO_AUTH_TOKEN = "3e361df08d905597d9387017db3d050a"    
TWILIO_PHONE_NUMBER = "+16365004592"           

EYE_COOLDOWN = 5        
YAWN_COOLDOWN = 8       
HEAD_TILT_COOLDOWN = 4  

USE_STATE_CHANGE_DETECTION = True

USE_VOICE_WARNINGS = True and TTS_AVAILABLE


log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)

timestamp_label = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file = os.path.join(log_folder, f"events_{timestamp_label}.csv")

with open(log_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Event", "Value"])

def log_event(event, value):
    """Log events using real laptop time into a unique file per run."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, event, value])

log_event("Program Started", "-")



SMS_SENT = False  
def send_sms_alert(warning_type):
    """Send SMS alert on first drowsiness detection"""
    global SMS_SENT
    
    if not ENABLE_SMS_ALERT or SMS_SENT:
        return
    
    try:
        from twilio.rest import Client
        
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_body = f"⚠️ DROWSINESS ALERT ⚠️\n\nType: {warning_type}\nTime: {timestamp}\n\nDriver drowsiness detected by monitoring system. Please take a break!"
        
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=PHONE_NUMBER
        )
        
        SMS_SENT = True
        log_event("SMS Alert Sent", warning_type)
        print(f"[SMS] Alert sent successfully! SID: {message.sid}")
        
    except ImportError:
        print("[SMS ERROR] Twilio not installed. Install with: pip install twilio")
        SMS_SENT = True  
    except Exception as e:
        print(f"[SMS ERROR] Failed to send SMS: {e}")
        SMS_SENT = True  



class AlertManager:
    """Manages cooldown timers and state changes for alerts"""
    
    def __init__(self):
        
        self.last_eye_alert = 0
        self.last_yawn_alert = 0
        self.last_tilt_alert = 0
        
        self.prev_eye_closed = False
        self.prev_yawning = False
        self.prev_head_tilted = False
    
    def should_alert_eyes(self, is_closed, current_time):
        """Check if eye closure alert should be triggered"""
        if not is_closed:
            self.prev_eye_closed = False
            return False
        
        cooldown_passed = (current_time - self.last_eye_alert) >= EYE_COOLDOWN
        
        state_changed = not self.prev_eye_closed
        
        if USE_STATE_CHANGE_DETECTION:
            should_alert = state_changed
        else:
            should_alert = cooldown_passed
        
        if should_alert:
            self.last_eye_alert = current_time
            self.prev_eye_closed = True
            return True
        
        return False
    
    def should_alert_yawn(self, is_yawning, current_time):
        """Check if yawn alert should be triggered"""
        if not is_yawning:
            self.prev_yawning = False
            return False
        
        cooldown_passed = (current_time - self.last_yawn_alert) >= YAWN_COOLDOWN
        state_changed = not self.prev_yawning
        
        if USE_STATE_CHANGE_DETECTION:
            should_alert = state_changed
        else:
            should_alert = cooldown_passed
        
        if should_alert:
            self.last_yawn_alert = current_time
            self.prev_yawning = True
            return True
        
        return False
    
    def should_alert_tilt(self, is_tilted, current_time):
        """Check if head tilt alert should be triggered"""
        if not is_tilted:
            self.prev_head_tilted = False
            return False
        
        cooldown_passed = (current_time - self.last_tilt_alert) >= HEAD_TILT_COOLDOWN
        state_changed = not self.prev_head_tilted
        
        if USE_STATE_CHANGE_DETECTION:
            should_alert = state_changed
        else:
            should_alert = cooldown_passed
        
        if should_alert:
            self.last_tilt_alert = current_time
            self.prev_head_tilted = True
            return True
        
        return False



def play_beep(freq, duration):
    """Runs winsound.Beep in a separate background thread."""
    try:
        winsound.Beep(freq, duration)
    except:
        pass  

def speak_warning(message):
    """Speak warning message using TTS in a separate thread"""
    def _speak():
        try:
            if USE_WIN32_SPEECH:
                
                import win32com.client
                spk = win32com.client.Dispatch("SAPI.SpVoice")
                spk.Speak(message)
            else:
                # pyttsx3 fallback
                tts_engine.say(message)
                tts_engine.runAndWait()
        except Exception as e:
            print(f"[TTS ERROR] {e}")
    threading.Thread(target=_speak, daemon=True).start()

def alarm_eyes_closed():
    """Alert for eyes closed - Voice: 'Eyes closed' or Beep"""
    if USE_VOICE_WARNINGS:
        speak_warning("Eyes closed")
    else:
        threading.Thread(target=play_beep, args=(1000, 500), daemon=True).start()

def alarm_yawn():
    """Alert for yawning - Voice: 'Yawn detected' or Beep"""
    if USE_VOICE_WARNINGS:
        speak_warning("Yawn detected")
    else:
        threading.Thread(target=play_beep, args=(800, 700), daemon=True).start()

def alarm_head_tilt():
    """Alert for head tilt - Voice: 'Please keep head straight' or Beep"""
    if USE_VOICE_WARNINGS:
        speak_warning("Please keep head straight")
    else:
        threading.Thread(target=play_beep, args=(1200, 400), daemon=True).start()



print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(
    './dlib_shape_predictor/shape_predictor_68_face_landmarks.dat')

print("[INFO] initializing camera...")
vs = cv2.VideoCapture(0)
time.sleep(2.0)

if not vs.isOpened():
    print("[ERROR] Could not open webcam.")
    exit()

print(f"[INFO] Alert Mode: {'State Change Detection' if USE_STATE_CHANGE_DETECTION else 'Cooldown Timers'}")
print(f"[INFO] Voice Warnings: {'Enabled' if USE_VOICE_WARNINGS else 'Disabled (Beeps)'}")
if not USE_STATE_CHANGE_DETECTION:
    print(f"[INFO] Cooldowns - Eyes: {EYE_COOLDOWN}s, Yawn: {YAWN_COOLDOWN}s, Tilt: {HEAD_TILT_COOLDOWN}s")

screen_width = 1920
screen_height = 1080

frame_width = 1024
frame_height = 576

cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

image_points = np.array([
    (359, 391),
    (399, 561),
    (337, 297),
    (513, 301),
    (345, 465),
    (453, 469)
], dtype="double")

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(mStart, mEnd) = (49, 68)

EYE_AR_THRESH = 0.25
MOUTH_AR_THRESH = 0.79
EYE_AR_CONSEC_FRAMES = 3
COUNTER = 0

alert_manager = AlertManager()


while True:

    ret, frame = vs.read()
    if not ret:
        continue

    frame = cv2.resize(frame, (frame_width, frame_height))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    size = gray.shape

    current_time = time.time() 

    rects = detector(gray, 0)

    if len(rects) > 0:
        cv2.putText(frame, "{} face(s) found".format(len(rects)), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    for rect in rects:

        (bX, bY, bW, bH) = face_utils.rect_to_bb(rect)
        cv2.rectangle(frame, (bX, bY), (bX + bW, bY + bH), (0, 255, 0), 1)

        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        ear = (eye_aspect_ratio(leftEye) + eye_aspect_ratio(rightEye)) / 2.0

        cv2.drawContours(frame, [cv2.convexHull(leftEye)], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [cv2.convexHull(rightEye)], -1, (0, 255, 0), 1)

        is_eyes_closed = False
        if ear < EYE_AR_THRESH:
            COUNTER += 1
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                is_eyes_closed = True
                cv2.putText(frame, "Eyes Closed!", (500, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                if alert_manager.should_alert_eyes(is_eyes_closed, current_time):
                    log_event("Eyes Closed", round(ear, 3))
                    alarm_eyes_closed()
                    send_sms_alert("Eyes Closed")  
        else:
            COUNTER = 0
            alert_manager.should_alert_eyes(False, current_time)  

        mouth = shape[mStart:mEnd]
        mar = mouth_aspect_ratio(mouth)

        cv2.drawContours(frame, [cv2.convexHull(mouth)], -1, (0, 255, 0), 1)
        cv2.putText(frame, "MAR: {:.2f}".format(mar), (650, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        is_yawning = mar > MOUTH_AR_THRESH
        if is_yawning:
            cv2.putText(frame, "Yawning!", (800, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            if alert_manager.should_alert_yawn(is_yawning, current_time):
                log_event("Yawning", round(mar, 3))
                alarm_yawn()
                send_sms_alert("Yawning") 
        else:
            alert_manager.should_alert_yawn(False, current_time)  

        key_indices = [33, 8, 36, 45, 48, 54]
        for idx, landmark in enumerate(key_indices):
            x, y = shape[landmark]
            image_points[idx] = np.array([x, y], dtype="double")
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        head_tilt_degree, start_point, end_point, end_point_alt = \
            getHeadTiltAndCoords(size, image_points, frame_height)

        cv2.line(frame, start_point, end_point, (255, 0, 0), 2)
        cv2.line(frame, start_point, end_point_alt, (0, 0, 255), 2)

        cv2.putText(frame, 'Head Tilt Degree: ' + str(head_tilt_degree[0]),
                    (170, 20), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 2)

        is_tilted = head_tilt_degree[0] > 30
        if is_tilted:
            cv2.putText(frame, "Head Tilt Warning!", (170, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            if alert_manager.should_alert_tilt(is_tilted, current_time):
                log_event("Head Tilt", round(head_tilt_degree[0], 2))
                alarm_head_tilt()
                send_sms_alert("Head Tilt") 
        else:
            alert_manager.should_alert_tilt(False, current_time)  

    fullscreen_frame = cv2.resize(frame, (screen_width, screen_height))
    cv2.imshow("Frame", fullscreen_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
vs.release()