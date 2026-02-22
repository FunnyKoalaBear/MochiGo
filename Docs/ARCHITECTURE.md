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