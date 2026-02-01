# AI Traffic Control Simulation

A Python-based traffic simulation showcasing **Adaptive Traffic Control Logic** and **Emergency Vehicle Prioritization**. This project demonstrates object-oriented programming, real-time simulation logic, and basic reinforcement learning concepts (state-based decision making).

##  Features

*   **Adaptive Traffic Lights:** Logic that adjusts green light duration based on queue length (Sensor-based).
*   **Emergency Mode:** Automatic detection of emergency vehicles (Ambulances) triggers a system-wide override to clear the path.
*   **Queue Management:** Real-time visualization of waiting cars per lane.
*   **Modular Architecture:** Clean, type-hinted, and documented code structure suitable for further expansion.
*   **DRL integration** Deep Reinforcement Learning (DRL) The system uses DRL to optimize traffic flow. The agent monitors vehicle queues and pedestrian density in real time, dynamically adjusting signal phases to minimize delays.

## Technologies

*   **Language:** Python 3.10+
*   **Engine:** Pygame Community Edition (`pygame-ce`)
*   **Concepts:** State Machines, OOP, Event-Driven Programming.



##  Installation

1.  **Clone the repository** (or download source):
    ```bash
    git clone https://github.com/snoRIP/ai-traffic-control.git
    cd ai-traffic-control
    ```

2.  **Create a Virtual Environment (Optional but Recommended):**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

##  Usage

Run the simulation:

```bash
python main.py
```

### Controls
*   **Close Window:** Exits the simulation.
*   **Ctrl+C:** Exits if running from a terminal.

### Simulation Rules
*   **Standard Cars (Blue):** Stop at red/yellow lights.
*   **Ambulances (Red):** Ignore lights; lights automatically turn Green for them.
*   **Adaptive Logic:** Green light holds for a minimum of 5 seconds, then switches if the opposing lane has a longer queue.


