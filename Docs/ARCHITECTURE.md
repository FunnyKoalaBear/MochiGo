# MochiGo System Architecture (Prototype Phase)

## High-Level Overview
The MochiGo architecture utilizes an Orchestrator Pattern divided into two main nodes communicating over a local Wi-Fi network. 
1. **The Client (Raspberry Pi / MochiGo Robot):** Acts as a lightweight I/O terminal responsible only for hardware interaction (microphone and speaker).
2. **The Server (Local Laptop):** Acts as the heavy-computation engine, processing the entire conversational pipeline (Speech-to-Text, LLM generation, Text-to-Speech).

---

## Client-Side Architecture (MochiGo Robot)
The client-side scripts manage the physical interactions with the user and handle the network requests to the server.

* **`main.py` (Client Orchestrator):** The central hub for the robot. It triggers the listening process, transmits the captured audio file to the server, waits for the processed audio response, and triggers the playback.
* **`voiceIn.py`:** Handles the input logic. It utilizes Voice Activity Detection (VAD) or a Wake Word engine to detect when the user is speaking, triggers the microphone recording script (`mic.py`), and saves the user's speech as an audio file.
* **`voiceOut.py`:** Handles the output logic. It receives the final generated audio file from the server and interfaces with the robot's hardware speaker to play the audio back to the user.

---

## Server-Side Architecture (Local Laptop)
The server-side operates as a sequential pipeline, passing data through various modules to generate a response. 

* **`main.py` (Server Orchestrator):** Hosts the network API to receive data from the robot. Once user audio is received, it pushes the data through the following pipeline:
  1. **Receive:** Accepts the incoming speech audio file from the robot.
  2. **STT (Speech-to-Text):** Passes the audio to the STT module and receives a transcribed text string.
  3. **LLM (Language Model):** Passes the transcribed text as a prompt to the local LLM and receives a generated text response.
  4. **TTS (Text-to-Speech):** Passes the LLM's text response to the TTS module to generate a new audio file.
  5. **Send:** Transmits the final TTS audio file back to the robot.

*(Note: In this prototype phase, the pipeline runs sequentially without chunked streaming. The server processes the entire audio response before sending it back to the client.)*

# Hardware Configuration: I2S Microphone & Pigpio Clock Conflict

## The Issue
The `pigpio` daemon and the I2S microphone (INMP441) both attempt to use the Raspberry Pi’s internal **PCM clock** by default. This hardware conflict causes `pigpio` to silently fail, which results in the motors freezing while the microphone is active.

## The Solution
Force `pigpio` to use the **PWM clock** instead of the PCM clock.

## Permanent Fix

1. Edit the daemon service file:
   ```bash
   sudo nano /lib/systemd/system/pigpiod.service
   ```

2. Update the execution line to include the `-t 0` flag:
   ```bash
   ExecStart=/usr/bin/pigpiod -l -t 0
   ```

3. Reload and restart the daemon:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart pigpiod
   ```

---

# Audio System Architecture: INMP441 Omnidirectional Microphone

## Overview
Mochigo’s hearing is powered by an **INMP441 I2S omnidirectional microphone**.  
Unlike standard USB microphones, this module communicates directly with the Raspberry Pi’s GPIO pins using the **I2S (Inter-IC Sound)** serial bus protocol.

Because I2S requires precise timing via the Pi’s internal PCM clock, the hardware interface must be enabled at the boot level before any Python scripts can access the microphone.

---

## OS-Level Hardware Configuration

### Boot Configuration (`/boot/firmware/config.txt`)

The following lines enable the I2S bus and map it to a generic soundcard overlay:

```ini
dtparam=i2s=on
dtoverlay=googlevoicehat-soundcard
```

---

# Rapid Audio Testing via Local Web Server

To quickly test the audio output of `micRecording.wav` without needing to securely copy (SCP) or SSH the file to a host computer, Mochigo uses Python’s built-in HTTP server module. This temporarily turns the Raspberry Pi into a local web server.

## Command

```bash
python -m http.server 8000
```

You can then access the file from another device on the same network:

```
http://<raspberry-pi-ip>:8000/micRecording.wav
```

---

## Notes
- Ensure both devices are connected to the same local network.
- Stop the server with `Ctrl + C` when finished.


# Speaker Architecture

## Overview
This document outlines the hardware architecture for the two-way digital audio subsystem of the MochiGo AI robot. The system utilizes the $I^2S$ (Inter-IC Sound) protocol to interface both a digital microphone and a speaker amplifier directly with the core processing unit, bypassing analog conversion to ensure crisp speech recognition and playback.

## Hardware Interface & Wiring
The audio subsystem utilizes a shared $I^2S$ bus architecture. The Raspberry Pi acts as the Master device, generating the necessary clock signals, while the microphone and amplifier act as Slave devices.

To conserve GPIO pins and simplify routing, the timing signals (Clock and Word Select) are physically spliced to feed both audio devices simultaneously. The data lines remain strictly isolated to prevent input/output collision.

## Software Configuration (Raspberry Pi OS)
To activate the hardware $I^2S$ pins and load the appropriate device tree overlays for simultaneous input/output, the core system configuration must be modified.

**Target File:** `/boot/firmware/config.txt`

**Required Modifications:**
1.  Disable default onboard audio routing.
2.  Enable the $I^2S$ hardware module.
3.  Apply specific overlays for the amplifier and memory mapping (to ensure microphone recording stability).

```ini
# Disable default audio
#dtparam=audio=on

# Enable I2S interface
dtparam=i2s=on

# Audio Hardware Overlays
dtoverlay=max98357a
dtoverlay=i2s-mmap