# Recon Rover V1 — dual-processor reconnaissance rover

**A modular rover that keeps high-level reasoning on a Raspberry Pi and real-time hardware control on an ESP32.**

> **Provenance.** This public repository is a restored snapshot of the upstream [HariTheja21/ReconRover](https://github.com/HariTheja21/ReconRover) project. Its git history is authored by HariTheja21 (`bhthari21@gmail.com`) and the visible release commit is *"Release v1.0.0: Software platform freeze before hardware integration"* (2026-07-16). The design and code are that author's work, **not original work by this account**. This snapshot also contains later V2 phase design documents. The upstream README states the MIT license; **no `LICENSE` file is present here**, so consult upstream for authoritative terms.

## Overview

Recon Rover V1 uses a strict dual-processor split, connected only by a JSON-over-USB-serial bridge.

- **Cognitive layer — Raspberry Pi 3B+ (Python 3):** USB webcam vision with OpenCV/TFLite, voice-command processing (VAD and speech-to-text), spatial mapping and obstacle-avoidance logic, and a WebSocket server that streams telemetry to a web dashboard. It does not touch GPIO pins.
- **Reactive layer — ESP32-S3 N16R8 (C++ on FreeRTOS):** polls HC-SR04 ultrasonic, VL53L0X ToF, MPU6050 IMU and MQ-2 gas sensors; drives four DC motors through an L298N and SG90 pan/tilt servos; renders expressions on two SSD1306 OLED displays and WS2812B LEDs. A hardware watchdog shuts motors down on fault or Pi disconnect. It executes commands and reports telemetry; it does not make decisions.

The separation is documented as a deliberate design rule: perception and planning live on the Pi, while timing-critical actuation and safety stay on the microcontroller.

## 🔐 Web UI session secret

The ground-station Web UI signs session tokens with HMAC-SHA256. Set
`RECON_ROVER_JWT_SECRET` to a long random value in the environment before
starting it. If unset, a random per-process secret is generated, so sessions
expire on restart — safe for development, but not suitable for a persistent
deployment.

## Hardware

- Raspberry Pi 3B+ and ESP32-S3 N16R8
- L298N motor driver with 4 DC gear motors; PCA9548A I²C multiplexer
- Sensors: 4× HC-SR04, 2× VL53L0X, MPU6050, MQ-2
- Displays: 2× 0.96″ SSD1306 OLED, 2× WS2812B LED strips
- USB webcam and microphone; 2S Li-Po battery and two 5 V buck converters isolating logic from motors

See [HARDWARE_COMPONENTS.md](Docs/Hardware/HARDWARE_COMPONENTS.md) for the bill of materials.

## Getting started

Prerequisites: ESP-IDF v5.x for the firmware, Python 3.10+ for the Pi runtime, and USB serial access (on Linux, add the user to the `dialout` group).

```bash
git clone https://github.com/anya12forger12-max/ReconRover.git
cd ReconRover
cd "MAIN CODE/RASPBERRY_PI"
python3 -m venv rover_env
source rover_env/bin/activate
pip install -r requirements.txt
python main.py
```

The upstream setup guide spells this directory with a space; in this snapshot the path is `MAIN CODE/RASPBERRY_PI`. The standalone ESP-IDF firmware project is in `ESP32_ROVER/`, shared protocol schemas in `MAIN CODE/SHARED/`, and the browser dashboard in `WEB_UI/`.

For firmware commands (`idf.py set-target esp32s3`, `build`, `flash monitor`) and the full Pi setup, follow [SETUP_GUIDE.md](Docs/SETUP_GUIDE.md).

## Documentation

- [Documentation index](Docs/README.md)
- [System architecture](Docs/Architecture/SYSTEM_ARCHITECTURE.md)
- [Software architecture](Docs/Architecture/SOFTWARE_ARCHITECTURE.md)
- [Firmware architecture](Docs/Architecture/FIRMWARE_ARCHITECTURE.md)
- [Communication protocol](Docs/Protocol/COMMUNICATION_PROTOCOL.md)
- [Testing procedures](Docs/Tests/TESTING_PROCEDURES.md)

## Responsible use

This is a reconnaissance robotics platform. Use it only where you have permission to operate and collect data, respect privacy and local rules about cameras and audio recording, and keep the hardware safety interlocks and watchdog enabled during testing.

## License and credits

Original project by **HariTheja21** at [github.com/HariTheja21/ReconRover](https://github.com/HariTheja21/ReconRover). The upstream README describes the project as MIT-licensed; this restored snapshot preserves that attribution but contains no license file of its own. No original authorship is claimed here.
