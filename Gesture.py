#!/usr/bin/env python3

import argparse
import time
from collections import deque, Counter

import cv2
import mediapipe as mp
import numpy as np
import serial

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def fingers_from_landmarks(lm):
    """
    lm : list of normalized landmarks
    returns [thumb, index, middle, ring, pinky] booleans
    """
    tips = [4, 8, 12, 16, 20]
    fingers = []
    # index..pinky: compare tip.y with pip.y  (y grows downward)
    for i in range(1, 5):
        try:
            tip_y = lm[tips[i]].y
            pip_y = lm[tips[i] - 2].y
            fingers.append(tip_y < pip_y)
        except Exception:
            fingers.append(False)
    # thumb simple heuristic (may be noisy depending on orientation)
    try:
        thumb_up = lm[4].x > lm[3].x
    except Exception:
        thumb_up = False
    return [thumb_up] + fingers

def classify_three(fingers):
    thumb, idx, mid, ring, pinky = fingers
    if idx and mid and ring and pinky:
        return 'forward'
    if idx and mid and not ring and not pinky:
        return 'backward'
    return 'stop'

class GestureSerialGUI:
    def _init_(self, stream_url, serial_port=None, baud=115200,
                 smoothing_buffer=7, stable_frames=4, show_debug=True, resize_w=None):
        self.stream_url = stream_url
        self.serial_port = serial_port
        self.baud = baud
        self.smoothing_buffer = smoothing_buffer
        self.stable_frames = stable_frames
        self.show_debug = show_debug
        self.resize_w = resize_w  

        self.ser = None
        if serial_port:
            try:
                self.ser = serial.Serial(serial_port, baudrate=baud, timeout=1)
                print(f"[SERIAL] Opened {serial_port} @ {baud}")
                time.sleep(2.0)  
            except Exception as e:
                print(f"[SERIAL] Could not open serial {serial_port}: {e}")
                self.ser = None

        self.cap = None
        self.open_capture()

        # mediapipe hands
        self.hands = mp_hands.Hands(static_image_mode=False,
                                    max_num_hands=1,
                                    model_complexity=0,
                                    min_detection_confidence=0.5,
                                    min_tracking_confidence=0.5)

        # smoothing
        self.buffer = deque(maxlen=self.smoothing_buffer)
        self.last_sent = None
        self.same_count = 0

        # mapping
        self.map_cmd = {'forward': b'1', 'backward': b'2', 'stop': b'3'}

        # For FPS measurement
        self._last_time = time.time()
        self._fps = 0.0

        if self.show_debug:
            cv2.namedWindow('Gesture', cv2.WINDOW_NORMAL)

    def open_capture(self):
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
        print(f"[VIDEO] Opening stream: {self.stream_url}")
        self.cap = cv2.VideoCapture(self.stream_url)
        time.sleep(0.5)
        if not (self.cap and self.cap.isOpened()):
            print("[VIDEO] Warning: cannot open stream right now. Will retry in loop.")
            self.cap = None

    def send_serial(self, gesture):
        if self.ser is None:
            print(f"[SERIAL] (dry-run) -> {gesture} -> {self.map_cmd.get(gesture)}")
            return
        cmd = self.map_cmd.get(gesture)
        if cmd is None:
            return
        try:
            self.ser.write(cmd)
            self.ser.flush()
            print(f"[SERIAL] Sent {cmd} for gesture {gesture}")
        except Exception as e:
            print(f"[SERIAL] Serial write failed: {e}")

    def _update_fps(self):
        now = time.time()
        dt = now - self._last_time
        if dt > 0:
            self._fps = 0.9 * self._fps + 0.1 * (1.0 / dt) if self._fps else (1.0 / dt)
        self._last_time = now

    def run(self):
        print("[RUN] Starting main loop. Press Ctrl+C or 'q' in window to quit.")
        try:
            while True:
                if not self.cap or not self.cap.isOpened():
                    self.open_capture()
                    time.sleep(0.5)
                    continue

                ret, frame = self.cap.read()
                if not ret or frame is None:
                  
                    self.cap.release()
                    self.cap = None
                    time.sleep(0.2)
                    continue

                if self.resize_w:
                    h, w = frame.shape[:2]
                    new_h = int(h * (self.resize_w / w))
                    frame = cv2.resize(frame, (self.resize_w, new_h))

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(rgb)

                gesture = 'stop'

                if results.multi_hand_landmarks and len(results.multi_hand_landmarks) > 0:
                    hand_lm = results.multi_hand_landmarks[0].landmark
                    fingers = fingers_from_landmarks(hand_lm)
                    gesture = classify_three(fingers)

                    
                    mp_drawing.draw_landmarks(frame, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)

                # smoothing + stability
                self.buffer.append(gesture)
                most_common, count = Counter(self.buffer).most_common(1)[0]

                if most_common == self.last_sent:
                    self.same_count += 1
                else:
                    self.same_count = 1

                if self.same_count >= self.stable_frames and most_common != self.last_sent:
                    self.send_serial(most_common)
                    self.last_sent = most_common

                
                self._update_fps()
                cv2.putText(frame, f'Gesture: {gesture}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                cv2.putText(frame, f'FPS: {self._fps:.1f}', (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)

                if self.show_debug:
                    cv2.imshow('Gesture', frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        print("[RUN] Quit pressed")
                        break

        except KeyboardInterrupt:
            print("\n[RUN] Interrupted by user")
        finally:
            try:
                if self.cap:
                    self.cap.release()
            except Exception:
                pass
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass
            try:
                if self.hands:
                    self.hands.close()
            except Exception:
                pass
            try:
                if self.ser:
                    self.ser.close()
            except Exception:
                pass
            print("[RUN] Clean exit")


if _name_ == '_main_':
    from collections import Counter
    parser = argparse.ArgumentParser(description="Gesture -> Serial (IP cam -> Mediapipe -> Arduino) with GUI")
    parser.add_argument('--url', '-u', required=True, help='IP camera video URL (e.g. http://192.168.1.5:8080/video)')
    parser.add_argument('--serial', '-s', default=None, help='Serial port for Arduino (e.g. /dev/ttyACM0). Omit for dry-run/logging.')
    parser.add_argument('--baud', '-b', type=int, default=115200, help='Serial baud rate')
    parser.add_argument('--buffer', type=int, default=7, help='Smoothing buffer length (frames)')
    parser.add_argument('--stable', type=int, default=4, help='Frames of stability required to send command')
    parser.add_argument('--no-gui', action='store_true', help='Disable debug window (headless)')
    parser.add_argument('--resize', type=int, default=640, help='Resize width for processing (set smaller for speed)')
    args = parser.parse_args()

    gs = GestureSerialGUI(stream_url=args.url,
                          serial_port=args.serial,
                          baud=args.baud,
                          smoothing_buffer=args.buffer,
                          stable_frames=args.stable,
                          show_debug=not args.no_gui,
                          resize_w=args.resize if args.resize > 0 else None)
    gs.run()
