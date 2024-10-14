import imufusion
import matplotlib.pyplot as plt
import numpy as np
import sys
from pyplink import Plink
import time


def setup_plink():
    plink = Plink()
    plink.connect()

    return plink


def main():
    plink = setup_plink()

    time.sleep(5)  # Use time.sleep instead of delay

    # Preallocate arrays
    MAX_SAMPLES = 3000

    euler = np.zeros((MAX_SAMPLES, 3), dtype=np.float32)  # Initialize with zeros

    plink.calibrate_imu()  # Calibrate the IMU

    start_time = time.perf_counter()  # Use perf_counter for higher resolution

    # Start collecting data
    # Collect data for 30 seconds, at 100 Hz
    for i in range(MAX_SAMPLES):
        # Calculate the time when this sample should be taken
        next_sample_time = start_time + i * (
            1 / 100
        )  # Each sample is 0.01 seconds apart

        # Update progress bar every 100 samples
        if i % 100 == 0 or i == MAX_SAMPLES - 1:
            progress = (i + 1) / MAX_SAMPLES
            bar_length = 40  # Length of the progress bar
            filled_length = int(bar_length * progress)
            bar = "█" * filled_length + "-" * (bar_length - filled_length)
            print(f"\rProgress: |{bar}| {progress*100:.1f}%", end="")

        # Wait until the next sample time
        now = time.perf_counter()
        time_to_wait = next_sample_time - now
        if time_to_wait > 0:
            time.sleep(time_to_wait)

        # Read data from the Imu
        gravity_vector = np.array(plink.imu.gravity_vector)

        euler_angles = gravity_vector

        timestamp[i] = time.perf_counter()

    # After the loop, print a newline to move to the next line
    print()

    # Plot sensor data
    _, axes = plt.subplots(nrows=1, sharex=True)

    axes[2].plot(timestamp - timestamp[0], euler[:, 0], "tab:red", label="Roll")
    axes[2].plot(timestamp - timestamp[0], euler[:, 1], "tab:green", label="Pitch")
    axes[2].plot(timestamp - timestamp[0], euler[:, 2], "tab:blue", label="Yaw")
    axes[2].set_title("Euler angles")
    axes[2].set_xlabel("Seconds")
    axes[2].set_ylabel("Degrees")
    axes[2].grid()
    axes[2].legend()

    # plt.show(block="no_block" not in sys.argv)  # don't block when script run by CI
    plt.savefig("sensor_data_onboard_fusion.png")


if __name__ == "__main__":
    main()
