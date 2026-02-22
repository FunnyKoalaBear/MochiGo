## Software Architecture: Multitasking with Threading
**The Issue:** Launching the microphone script via `subprocess` locked the audio hardware, preventing the main script from accessing it. Standard sequential loops also caused the motors to pause while the microphone was actively recording.
**The Solution:** Implemented Python's `threading` library for concurrent execution.
* The `motors.oscillate()`, `eyes.neutral()`, and `mic.record()` functions were wrapped in infinite loops and assigned to their own background threads.
* **Crucial Detail:** Used the `daemon=True` flag when creating the threads. This ensures the background threads are tied to the main script's lifespan and do not refuse to close when the main program exits.


## Graceful Shutdown Sequence
**The Issue:** Pressing `Ctrl+C` sends a `KeyboardInterrupt` only to the Main Thread. The daemon threads continued to run for a split second, attempting to access hardware connections (`pigpio` and `sounddevice`) that the main thread had already destroyed, resulting in messy terminal crash tracebacks.
**The Solution:** Implemented a universal kill switch using `threading.Event()`.
* **How it works:** When `Ctrl+C` is pressed, the main thread flips the `kill_switch.set()`. 
* The background `while` loops check `while not kill_switch.is_set():`, allowing them to terminate their own loops peacefully.
* Wrapped the thread actions in `try/except Exception: break` to catch and silently hide any split-second teardown errors, ensuring a clean terminal exit.