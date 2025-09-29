# 🚗 Gesture Control for Smart Car Kit using Raspberry Pi

This project uses your phone as a live video source and detects hand gestures using MediaPipe. The recognized gestures are sent serially from the Raspberry Pi to an Arduino, which controls the movement of a Smart Car Kit.

## 📽️ Demo Video

👉 *[[Demo video link here](https://youtu.be/gDPhRZBRRIo)]*

---

## 📌 Project Overview

This project implements a gesture-controlled smart car system on a Raspberry Pi. The mobile phone acts as an IP camera using the IP Webcam app, and the video stream is processed in real-time on the Raspberry Pi.

Using MediaPipe, hand gestures are detected and classified into directional commands (e.g., forward, left, right, stop). These commands are then sent via serial communication to the Arduino, which drives the motors of the Smart Car Kit accordingly.
---

## ⚙️ Features

- 📱 Live video streaming from mobile phone to Raspberry Pi via IP Webcam
- ✋ Real-time gesture detection using MediaPipe
- 🚗 Gesture-based control of a Smart Car Kit via Arduino
- 💻 Lightweight solution, optimized for Raspberry Pi’s resources

---

## 🧰 Technologies & Libraries

- **Python 3**
- **OpenCV** (for image processing and face detection)
- **IP Webcam App** (for turning mobile into an IP camera)
- **MediaPipe** (for hand gesture detection)
- **PySerial** (for communication with Arduino)

---

## 🛠️ Hardware Components

| Component                    | Quantity |
|-----------------------------|----------|
| Raspberry Pi                | 1        |
| Android Uno                 | 1        |
| Smart Car Kit               | 1        |



---

## 🧪 Working Principle

1. The mobile phone camera streams live video over Wi-Fi using the IP Webcam app.
2. The Raspberry Pi connects to the video stream using the provided URL.
3. Each frame is processed using OpenCV and analyzed with MediaPipe to detect hand gestures.
4. The detected gesture is classified into commands like forward, backward, left, right, or stop.
5. The command is sent serially to the Arduino, which drives the Smart Car Kit’s motors accordingly.


---

## 👨‍💻 Authors

Developed by:

- **Anshul Dewangan**
- **Pratyaksh Lodhi**
- **Aaron David Don**
- **Joshua Benchamin**

---

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).

---

