# Benchmark – Project 5 – Self-Organized Criticality

## Project Overview
This project simulates a file system that models **self-organized criticality** by simulating file creation, deletion, and fragmentation over time. As fragmentation increases, the system slows down, and once it exceeds a critical threshold, performance is severely impacted. The simulation generates a graph to visualize these metrics.

## How to Run
1. Clone the Repository:
git clone https://github.com/OneLunarSkye/Self-Organized-Criticality.git



2. Navigate to the Project Directory:
cd Self-Organized-Criticality



3. Install Required Packages:
pip install numpy matplotlib scipy

4. Run the Simulation:
python main.py

## Output
The program generates a graph showing:
- Fragmentation percentage over time.
- Save, load, and access times.
- Critical points when fragmentation exceeds the threshold.

