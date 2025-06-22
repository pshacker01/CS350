# Thermostat Controller

## Project Summary  
This project implements a smart thermostat on a Raspberry Pi. It reads room temperature via an AHT20 I²C sensor, lets the user cycle between Off, Heat, and Cool modes, adjusts a Fahrenheit set-point with buttons, and indicates heating or cooling status by fading or solid LEDs. A 16×2 LCD displays the current date/time and alternates between current temperature and “MODE SETPOINT°F,” while a serial port streams a comma-delimited status update every 30 seconds.

## What Went Well  
- **Design up front:** I sketched the finite-state machine (Off → Heat → Cool → Off) in draw.io before writing code, which eliminated transition errors.  
- **Incremental testing:** I developed and tested each hardware interface (LED fade, temperature read, button interrupt) in isolation, ensuring reliable building blocks.  
- **Clear thread separation:** Display updates and serial output run in background threads, keeping the main loop responsive to button presses and safe shutdown.

## Areas for Improvement  
- **Error handling:** I could add retries or fallback logic for I²C sensor timeouts and serial-port failures.  
- **Debounce logic:** Although `Button.when_pressed` works, hardware or software debouncing could be hardened for noisy switches.  
- **Configuration flexibility:** Hard-coded GPIO pins and set-point could be moved into a JSON/YAML config file for easier customization.

## Tools & Resources Added to My Support Network  
- **Draw.io (diagrams.net):** For rapid FSM and architecture sketches.  
- **GPIO Zero & Adafruit CircuitPython docs:** I now reference their guides first for any Raspberry Pi peripheral work.  
- **PyPI libraries:** `statemachine`, `PWMLED`, `Adafruit_AHTx0`, and `pySerial` for robust, well-maintained building blocks.  
- **Community forums:** Raspberry Pi Stack Exchange and Stack Overflow for quick answers to wiring and timing questions.

## Transferable Skills  
- **State-machine design:** Modeling complex workflows as FSMs applies to any event-driven embedded project.  
- **Threaded I/O patterns:** Running UI updates and communications in separate threads is critical for responsive systems.  
- **Modular hardware abstraction:** Encapsulating display, sensor, and LED logic in classes makes future reuse easy.  
- **Incremental development & Git usage:** Committing small, testable changes supports rapid iteration and safe rollbacks.

## Maintainability, Readability & Adaptability  
- **Well-documented FSM transitions** in draw.io and inline comments match code to design.  
- **Helper methods** (`updateLights()`, `setupSerialOutput()`, `manageMyDisplay()`) isolate responsibilities.  
- **Consistent naming conventions** and a clear directory structure make it easy for new developers to onboard.  
- **Thread-based tasks** for display and serial I/O mean adding new features (e.g. cloud upload) won’t block core logic.
