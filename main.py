# Brandon Leydon   3/23/2025
# Self-Organized Criticality

import numpy as np
import matplotlib.pyplot as plt
import random
from scipy.ndimage import label
import time

# ---------------------------
# CONFIG
# ---------------------------
storage_size = 1000
max_file_size = 30
frag_threshold = 70
total_steps = 300
base_time = 1
defrag_interval = 150
defrag_percent = 0.75
fragment_penalty = 0.02
step_limit = 100  # Cap time step display to avoid graph issues

# ---------------------------
# INIT
# ---------------------------
storage = np.zeros(storage_size)
file_list, gaps = [], []
frag_data, save_time_data, load_time_data, access_time_data, frag_time_data = [], [], [], [], []
critical_points = []  # Track critical points to visualize

# ---------------------------
# HELPERS
# ---------------------------
def update_gaps():
    # Update available gaps in storage
    global gaps
    gaps = []
    labeled, num_features = label(storage == 0)
    for i in range(1, num_features + 1):
        gap_size = np.sum(labeled == i)
        if gap_size > 0:
            start_idx = np.where(labeled == i)[0][0]
            gaps.append((gap_size, start_idx))


def calc_fragmentation():
    # Return % fragmentation
    total_free = np.sum(storage == 0)
    if not gaps or total_free == 0:
        return 0.0
    largest_gap = max((gap[0] for gap in gaps), default=0)
    frag = (total_free - largest_gap) / total_free * 100
    return frag


def can_fit(file_size):
    # Check if the file can fit without fragmentation
    return any(gap_size >= file_size for gap_size, _ in gaps)


def save_file(file_size):
    # Save a file in the best available gap or fragment
    global file_list
    best_gap = min((g for g in gaps if g[0] >= file_size), default=None, key=lambda x: x[0])

    if best_gap:
        _, start_idx = best_gap
        storage[start_idx: start_idx + file_size] = 1
        file_list.append((start_idx, start_idx + file_size))
    else:
        fragment_file(file_size)
    update_gaps()


def fragment_file(file_size):
    # Fragment file across multiple gaps
    remaining = file_size
    for gap_size, start_idx in gaps:
        if remaining <= 0:
            break
        chunk_size = min(gap_size, remaining)
        storage[start_idx: start_idx + chunk_size] = 1
        file_list.append((start_idx, start_idx + chunk_size))
        remaining -= chunk_size
    update_gaps()


def delete_random_file():
    # Delete a random file if there are enough files
    if len(file_list) < 3:  # Avoid deleting too many files
        return
    start, end = random.choice(file_list)
    storage[start:end] = 0
    file_list.remove((start, end))


def calc_save_time(frag):
    # Increase save time based on fragmentation
    return base_time * (1 + frag / 100)


def calc_load_time(frag):
    # Increase load time based on fragmentation
    return base_time * (1 + frag / 50)


def calc_access_time(file_size, fragments):
    # Calculate access time based on fragments
    return base_time + fragment_penalty * fragments


def count_fragments():
    # Count the number of file fragments
    labeled, num_features = label(storage == 1)
    return num_features


def defrag_storage():
    # Partially defragment storage to consolidate files
    global file_list
    occupied_indices = np.where(storage == 1)[0]
    storage.fill(0)

    # Defrag a portion of the files to leave some fragmentation
    num_to_defrag = int(len(occupied_indices) * defrag_percent)
    if num_to_defrag > 0:
        storage[:num_to_defrag] = 1

    # Leave fixed-sized gap to maintain fragmentation behavior
    gap_start = num_to_defrag + random.randint(10, 20)
    remaining_files = len(occupied_indices) - num_to_defrag
    if remaining_files > 0:
        storage[gap_start: gap_start + remaining_files] = 1

    update_gaps()
    file_list = [(start, end) for start, end in zip(np.where(storage == 1)[0], np.where(storage == 1)[0] + 1)]


# ---------------------------
# MAIN LOOP
# ---------------------------
# Initial smaller files to prevent immediate fragmentation
for _ in range(5):
    save_file(random.randint(5, 10))

update_gaps()

file_size = 0  # Default file size

# Weighted actions (80% create, 20% delete)
for step in range(total_steps):
    if step > step_limit:
        break  # Stop processing if step exceeds step_limit

    action = random.choices(["create", "delete"], weights=[0.8, 0.2])[0]

    if action == "create":
        file_size = random.randint(5, max_file_size)
        save_file(file_size if can_fit(file_size) else file_size)
    elif action == "delete":
        delete_random_file()
        file_size = 0

    update_gaps()
    frag_start_time = time.time()
    frag = calc_fragmentation()
    frag_end_time = time.time()

    # Track fragmentation calculation time
    frag_time_data.append(frag_end_time - frag_start_time)

    frag_data.append(frag)
    save_time_data.append(calc_save_time(frag))
    load_time_data.append(calc_load_time(frag))

    # Count fragments for access time calculation
    fragments = count_fragments()
    access_time_data.append(calc_access_time(file_size, fragments))

    if frag > frag_threshold:
        print(f"⚠️ WARNING: High fragmentation at {frag:.2f}% at step {step}")
        critical_points.append(step)
        break

    # Defragment storage periodically and if fragmentation > 60%
    if step % defrag_interval == 0 and step != 0 and frag > 60:
        defrag_storage()


# ---------------------------
# FINAL PLOT
# ---------------------------
if frag_data:
    time_steps = np.arange(len(frag_data))
    plt.figure(figsize=(10, 6))
    plt.plot(time_steps, frag_data, label="Fragmentation (%)", color="red")
    plt.plot(time_steps, save_time_data, label="Save Time", color="blue")
    plt.plot(time_steps, load_time_data, label="Load Time", color="green")
    plt.plot(time_steps, access_time_data, label="Access Time", color="purple")
    plt.plot(time_steps, frag_time_data, label="Frag. Calc Time", color="orange")

    # Plot critical points within the step limit
    for point in critical_points:
        if point <= step_limit:
            plt.axvline(point, color="black", linestyle="--", label=f"Critical Point @ {point}")

    plt.xlabel("Time Step")
    plt.ylabel("Value")
    plt.title("System Metrics Over Time")
    plt.legend()
    plt.grid(True)
    plt.show()
